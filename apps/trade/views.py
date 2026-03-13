from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.models import Product
from .serializers import ShoppingCartSerializer, ShoppingCartDetailSerializer, OrderSerializer, OrderDetailSerializer, OrderAddressSerializer
from .tasks import close_order_task  # 导入异步任务
import time

# 高并发控制可选方案：Redis分布式锁
# 如果需要跨进程/跨服务器并发控制，可以取消以下注释并安装redis和redis-lock库
# import redis
# from django_redis import get_redis_connection
# import redis_lock

class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能
    list: 获取当前用户的购物车列表
    create: 加入购物车
    update: 修改购物车商品数量
    delete: 删除购物车记录
    """
    # 强制要求必须登录才能访问购物车！
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    pagination_class = None

    def get_queryset(self):
        # 优化点：预加载关联的 goods 及 goods 的 category，解决购物车列表展示时的 N+1 问题
        # 过滤逻辑删除的商品：只显示未被逻辑删除的商品
        return ShoppingCart.objects.filter(user=self.request.user, goods__is_delete=False).select_related('goods__category').order_by('-add_time')

    def get_serializer_class(self):
        """
        动态选择序列化器：
        如果是获取列表，就返回带商品详细信息的 Serializer；
        如果是添加/修改，就返回只需要传 ID 的基本 Serializer。
        """
        if self.action == 'list':
            return ShoppingCartDetailSerializer
        return ShoppingCartSerializer


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    订单管理：使用 prefetch_related 优化订单商品详情查询
    list: 获取个人订单列表
    create: 新增订单 (结算购物车)
    delete: 删除订单
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        # 优化点：使用 Prefetch 对象进行更细粒度的预加载控制
        # 预加载关联的 OrderGoods，以及 OrderGoods 中关联的 Product（包括 Product 的 category）
        # 同时使用 select_related 预加载订单关联的 User，避免序列化时的 N+1 查询
        # 过滤逻辑删除的订单：只显示未被逻辑删除的订单
        from django.db.models import Prefetch
        from .models import OrderGoods

        return OrderInfo.objects.filter(user=self.request.user, is_delete=False)\
            .select_related('user')\
            .prefetch_related(
                Prefetch('goods', queryset=OrderGoods.objects.select_related('goods__category'))
            )

    def get_serializer_class(self):
        # 动态选择序列化器
        if self.action == "retrieve" or self.action == "list":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """
        重写创建方法：实现购物车数据的迁移和总价计算
        """
        user = self.request.user

        # 1. 生成订单号 (时间戳 + 用户ID + 随机数)
        import random
        order_sn = f"{time.strftime('%Y%m%d%H%M%S')}{user.id}{random.randint(10, 99)}"

        # 2. 先保存订单初步信息 (前端传过来的地址等)
        order = serializer.save(order_sn=order_sn)

        # 3. 获取该用户的购物车数据（优化：使用 select_related 预加载商品信息）
        # 过滤掉已逻辑删除的商品
        shop_carts = ShoppingCart.objects.filter(user=user, goods__is_delete=False).select_related('goods')
        order_mount = 0.0

        # 4. 遍历购物车，把商品转移到订单商品表中
        for cart in shop_carts:
            # 再次检查商品是否已被逻辑删除（防止并发问题）
            if cart.goods.is_delete:
                continue

            OrderGoods.objects.create(
                order=order,
                goods=cart.goods,
                goods_num=cart.nums,
                price=cart.goods.shop_price
            )
            # 累加总金额
            order_mount += cart.nums * cart.goods.shop_price

        # 5. 更新订单的总金额
        order.order_mount = order_mount
        order.save()

        # 6. 【重中之重】清空购物车！
        shop_carts.delete()

        # 7. 【异步任务应用】：下单后开启一个 30 分钟后执行的延时任务，检查支付状态
        # 如果 30 分钟后未支付，close_order_task 将自动关闭该订单
        close_order_task.apply_async(args=[order.id], countdown=30 * 60)

    def destroy(self, request, *args, **kwargs):
        """软删除订单：将 is_delete 标记为 True，而非物理删除"""
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付订单：模拟支付接口，更新状态并扣减库存
        高并发控制方案：
        1. Redis分布式锁：防止跨进程/跨服务器并发（可选，需安装redis-lock）
        2. 数据库事务+行级锁：保证数据库操作原子性
        3. 双重检查：防止状态在检查后发生变化
        """
        order = self.get_object()

        # 检查订单状态
        if order.pay_status != "PAYING":
            return Response(
                {"error": f"订单状态为{order.pay_status}，无法支付"},
                status=400
            )

        # ========== 高并发控制：Redis分布式锁（可选）==========
        # 在生产环境中，如果需要跨进程/跨服务器的并发控制，可以启用以下代码
        # 需要安装：pip install redis redis-lock
        # try:
        #     redis_conn = get_redis_connection("default")
        #     lock_key = f"order_pay_lock:{order.id}"
        #     # 获取分布式锁，超时时间10秒，防止死锁
        #     with redis_lock.Lock(redis_conn, lock_key, expire=10, auto_renewal=True):
        #         return self._process_payment_with_lock(order)
        # except redis_lock.NotAcquired:
        #     return Response(
        #         {"error": "订单正在处理中，请稍后再试"},
        #         status=409  # 409 Conflict
        #     )
        # except ImportError:
        #     # Redis锁不可用，降级为数据库锁
        #     pass

        # 使用数据库事务保证原子性（单服务器场景）
        try:
            with transaction.atomic():
                # 使用select_for_update锁定订单行，防止并发修改
                order = OrderInfo.objects.select_for_update().get(id=order.id)

                # 双重检查订单状态（防止状态在检查后发生变化）
                if order.pay_status != "PAYING":
                    return Response(
                        {"error": f"订单状态已变更为{order.pay_status}"},
                        status=400
                    )

                # 扣减库存（原子操作）
                order_goods = order.goods.all()
                for item in order_goods:
                    # 使用F表达式原子扣减库存，同时增加销量
                    # 条件：库存充足才更新
                    updated = Product.objects.filter(
                        id=item.goods.id,
                        goods_num__gte=item.goods_num  # 确保库存充足
                    ).update(
                        goods_num=F('goods_num') - item.goods_num,
                        sold_num=F('sold_num') + item.goods_num
                    )

                    if not updated:
                        raise ValidationError(f"商品{item.goods.name}库存不足")

                # 更新订单状态
                order.pay_status = "TRADE_SUCCESS"
                order.pay_time = timezone.now()
                order.save()

                return Response({
                    "message": "支付成功",
                    "order_sn": order.order_sn,
                    "pay_status": order.pay_status,
                    "pay_time": order.pay_time
                })

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "支付处理失败"}, status=500)

    @action(detail=True, methods=['patch'])
    def update_address(self, request, pk=None):
        """修改收货地址（仅限未支付订单）"""
        order = self.get_object()

        # 检查订单状态
        if order.pay_status != "PAYING":
            return Response(
                {"error": "只有未支付的订单才能修改地址"},
                status=400
            )

        # 使用序列化器验证地址数据
        serializer = OrderAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 更新地址信息
        validated_data = serializer.validated_data
        if 'address' in validated_data:
            order.address = validated_data['address']
        if 'signer_name' in validated_data:
            order.signer_name = validated_data['signer_name']
        if 'signer_mobile' in validated_data:
            order.signer_mobile = validated_data['signer_mobile']

        order.save()

        return Response({
            "message": "地址修改成功",
            "order_sn": order.order_sn,
            "address": order.address,
            "signer_name": order.signer_name,
            "signer_mobile": order.signer_mobile
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单（释放库存）"""
        order = self.get_object()

        # 检查订单状态
        if order.pay_status not in ["PAYING", "WAIT_BUYER_PAY"]:
            return Response(
                {"error": "只有未支付的订单才能取消"},
                status=400
            )

        try:
            with transaction.atomic():
                # 锁定订单行
                order = OrderInfo.objects.select_for_update().get(id=order.id)

                # 再次检查状态
                if order.pay_status not in ["PAYING", "WAIT_BUYER_PAY"]:
                    return Response(
                        {"error": "订单状态已变更，无法取消"},
                        status=400
                    )

                # 释放库存
                order_goods = order.goods.all()
                for item in order_goods:
                    # 使用F表达式原子增加库存（订单未支付，销量未增加，所以只释放库存）
                    Product.objects.filter(id=item.goods.id).update(
                        goods_num=F('goods_num') + item.goods_num
                    )

                # 更新订单状态
                order.pay_status = "TRADE_CLOSED"
                order.save()

                return Response({
                    "message": "订单已取消",
                    "order_sn": order.order_sn,
                    "pay_status": order.pay_status
                })

        except Exception as e:
            return Response({"error": "订单取消失败"}, status=500)