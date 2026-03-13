from celery import shared_task
from django.db import transaction, DatabaseError
from django.db.models import F
from .models import OrderInfo, OrderGoods
from goods.models import Product
import logging
import time

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def close_order_task(self, order_id):
    """
    异步任务：超时未支付自动关闭订单
    优化点：
    1. 增加任务重试机制，确保分布式环境下任务可靠性
    2. 完善日志记录，便于问题排查和监控
    3. 原子化库存释放逻辑，防止超卖和数据不一致
    4. 使用数据库事务保证数据一致性
    """
    task_start_time = time.time()
    logger.info(f"[订单超时任务开始] 订单ID: {order_id}, 任务ID: {self.request.id}")

    try:
        # 使用原子操作和乐观锁机制关闭订单
        with transaction.atomic():
            # 使用select_for_update锁定订单行，防止并发修改
            order = OrderInfo.objects.select_for_update().filter(id=order_id).first()

            if not order:
                logger.error(f"[订单不存在] 订单ID: {order_id}")
                return

            # 检查订单状态，只有待支付状态才进行处理
            if order.pay_status != "PAYING":
                logger.info(f"[订单状态无需关闭] 订单ID: {order_id}, 当前状态: {order.pay_status}")
                return

            # 记录原始状态用于日志
            old_status = order.pay_status

            # 更新订单状态为已关闭
            order.pay_status = "TRADE_CLOSED"
            order.save()

            logger.info(f"[订单状态已更新] 订单ID: {order_id}, 状态变更: {old_status} -> TRADE_CLOSED")

            # 释放库存：遍历订单中的商品，将库存加回
            order_goods_list = OrderGoods.objects.filter(order=order).select_related('goods')
            stock_updated_count = 0

            for order_goods in order_goods_list:
                if order_goods.goods:
                    # 原子操作增加商品库存，使用F表达式避免竞态条件
                    updated = Product.objects.filter(
                        id=order_goods.goods.id
                    ).update(
                        goods_num=F('goods_num') + order_goods.goods_num
                    )

                    if updated:
                        stock_updated_count += 1
                        logger.debug(f"[库存已释放] 商品ID: {order_goods.goods.id}, "
                                   f"商品名称: {order_goods.goods.name}, "
                                   f"释放数量: {order_goods.goods_num}")
                    else:
                        logger.warning(f"[库存释放失败] 商品ID: {order_goods.goods.id} 可能已被删除")

            logger.info(f"[库存释放完成] 订单ID: {order_id}, 释放商品数量: {stock_updated_count}/{len(order_goods_list)}")

        # 计算任务执行时间
        execution_time = time.time() - task_start_time
        logger.info(f"[订单超时任务完成] 订单ID: {order_id}, 执行时间: {execution_time:.2f}秒")

    except Exception as exc:
        logger.error(f"[订单超时任务异常] 订单ID: {order_id}, 异常信息: {str(exc)}", exc_info=True)

        # 根据异常类型决定是否重试
        retryable_errors = (ConnectionError, TimeoutError, DatabaseError)
        if isinstance(exc, retryable_errors):
            logger.warning(f"[任务重试] 订单ID: {order_id}, 重试次数: {self.request.retries}")
            # 指数退避重试
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"[任务失败] 订单ID: {order_id}, 非重试性异常，任务终止")
            raise