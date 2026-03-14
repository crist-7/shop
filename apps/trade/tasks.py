from celery import shared_task
from django.db import transaction, DatabaseError
from django.db.models import F
from django.core.cache import cache
from django_redis.exceptions import RedisError
from .models import OrderInfo, OrderGoods
from goods.models import Product
import logging
import time

logger = logging.getLogger(__name__)

# ============================================================
# 幂等性控制：基于 Redis 的任务去重锁
# ============================================================
def acquire_idempotency_lock(order_id, task_id, ttl=300):
    """
    获取幂等性锁，防止同一订单的关闭任务被重复执行
    Args:
        order_id: 订单ID
        task_id: 当前任务ID
        ttl: 锁过期时间（秒），默认5分钟
    Returns:
        bool: True 表示获取锁成功，可以执行任务；False 表示已有其他任务在执行
    """
    lock_key = f"order:close:lock:{order_id}"
    try:
        # 使用 setnx 实现分布式锁
        acquired = cache.set(lock_key, task_id, nx=True, timeout=ttl)
        if acquired:
            logger.info(f"[幂等锁获取成功] 订单ID: {order_id}, 任务ID: {task_id}")
            return True
        else:
            # 检查是否是同一个任务的重试（允许重试）
            existing_task = cache.get(lock_key)
            if existing_task == task_id:
                logger.info(f"[幂等锁重入] 订单ID: {order_id}, 同一任务重试: {task_id}")
                return True
            logger.warning(f"[幂等锁获取失败] 订单ID: {order_id}, 已被任务: {existing_task} 占用")
            return False
    except (RedisError, Exception) as e:
        # Redis 异常时不阻塞任务执行，降级为仅依赖数据库锁
        logger.warning(f"[幂等锁异常] 订单ID: {order_id}, 降级继续执行: {e}")
        return True


def release_idempotency_lock(order_id):
    """释放幂等性锁"""
    lock_key = f"order:close:lock:{order_id}"
    try:
        cache.delete(lock_key)
        logger.debug(f"[幂等锁释放] 订单ID: {order_id}")
    except Exception as e:
        logger.warning(f"[幂等锁释放异常] 订单ID: {order_id}: {e}")


# ============================================================
# 核心任务：超时未支付自动关闭订单
# ============================================================
@shared_task(
    bind=True,
    max_retries=5,              # 最大重试次数
    default_retry_delay=30,     # 默认重试间隔
    acks_late=True,             # 任务执行成功后才确认，防止中途丢失
    reject_on_worker_lost=True, # worker 崩溃时拒绝任务，触发重试
    autoretry_for=(DatabaseError, ConnectionError, TimeoutError, RedisError),
    retry_backoff=True,         # 启用指数退避
    retry_backoff_max=600,      # 最大退避时间 10 分钟
    retry_jitter=True,          # 添加随机抖动，避免重试风暴
)
def close_order_task(self, order_id):
    """
    异步任务：超时未支付自动关闭订单

    可靠性保障：
    1. acks_late + reject_on_worker_lost：确保任务不丢失
    2. 幂等性锁：防止同一订单被多次处理
    3. select_for_update：数据库行锁防止并发修改
    4. F 表达式：原子化库存/销量更新，防止竞态条件
    5. 指数退避重试：失败后自动重试，最多 5 次
    6. 库存+销量双向回滚：保证数据一致性

    重试策略：
    - 第1次重试：30秒后
    - 第2次重试：60秒后
    - 第3次重试：120秒后
    - 第4次重试：240秒后
    - 第5次重试：480秒后
    """
    task_id = self.request.id
    task_start_time = time.time()
    logger.info(f"[订单超时任务开始] 订单ID: {order_id}, 任务ID: {task_id}, 重试次数: {self.request.retries}")

    # 幂等性检查：获取分布式锁
    if not acquire_idempotency_lock(order_id, task_id):
        logger.info(f"[任务跳过] 订单ID: {order_id}, 已有其他任务在处理")
        return

    try:
        # 使用原子操作和行锁机制关闭订单
        with transaction.atomic():
            # 使用 select_for_update 锁定订单行，防止并发修改
            order = OrderInfo.objects.select_for_update().filter(id=order_id).first()

            if not order:
                logger.warning(f"[订单不存在] 订单ID: {order_id}, 任务ID: {task_id}")
                release_idempotency_lock(order_id)
                return

            # 幂等性检查：只有待支付状态才进行处理
            if order.pay_status != "PAYING":
                logger.info(f"[订单状态无需关闭] 订单ID: {order_id}, "
                           f"当前状态: {order.pay_status}, 任务ID: {task_id}")
                release_idempotency_lock(order_id)
                return

            # 记录原始状态用于日志
            old_status = order.pay_status

            # 更新订单状态为已关闭
            order.pay_status = "TRADE_CLOSED"
            order.save()

            logger.info(f"[订单状态已更新] 订单ID: {order_id}, "
                       f"状态变更: {old_status} -> TRADE_CLOSED, 任务ID: {task_id}")

            # 释放库存并回滚销量：遍历订单中的商品
            order_goods_list = OrderGoods.objects.filter(order=order).select_related('goods')
            stock_updated_count = 0
            sold_rollback_count = 0

            for order_goods in order_goods_list:
                if order_goods.goods:
                    # 原子操作：库存加回 + 销量减少，使用 F 表达式避免竞态条件
                    updated = Product.objects.filter(
                        id=order_goods.goods.id
                    ).update(
                        goods_num=F('goods_num') + order_goods.goods_num,  # 库存加回
                        sold_num=F('sold_num') - order_goods.goods_num     # 销量回滚
                    )

                    if updated:
                        stock_updated_count += 1
                        sold_rollback_count += 1
                        logger.debug(f"[库存&销量已回滚] 商品ID: {order_goods.goods.id}, "
                                   f"商品名称: {order_goods.goods.name}, "
                                   f"库存+{order_goods.goods_num}, 销量-{order_goods.goods_num}")
                    else:
                        logger.warning(f"[库存回滚失败] 商品ID: {order_goods.goods.id} 可能已被删除")

            logger.info(f"[库存释放完成] 订单ID: {order_id}, "
                       f"库存回滚: {stock_updated_count}/{len(order_goods_list)}, "
                       f"销量回滚: {sold_rollback_count}/{len(order_goods_list)}")

        # 任务成功完成，释放幂等锁
        release_idempotency_lock(order_id)

        # 计算任务执行时间
        execution_time = time.time() - task_start_time
        logger.info(f"[订单超时任务完成] 订单ID: {order_id}, "
                   f"任务ID: {task_id}, 执行时间: {execution_time:.2f}秒")

    except Exception as exc:
        logger.error(f"[订单超时任务异常] 订单ID: {order_id}, "
                    f"任务ID: {task_id}, 重试次数: {self.request.retries}, "
                    f"异常信息: {str(exc)}", exc_info=True)

        # 判断是否还能重试
        if self.request.retries < self.max_retries:
            logger.warning(f"[任务将重试] 订单ID: {order_id}, "
                          f"任务ID: {task_id}, 下次重试倒计时: {60 * (2 ** self.request.retries)}秒")
            # 抛出异常触发 Celery 自动重试（使用指数退避）
            raise self.retry(exc=exc)
        else:
            # 达到最大重试次数，记录严重错误
            logger.critical(f"[任务最终失败] 订单ID: {order_id}, "
                           f"任务ID: {task_id}, 已达最大重试次数，需人工介入！")
            # 释放锁，允许后续手动处理
            release_idempotency_lock(order_id)
            raise