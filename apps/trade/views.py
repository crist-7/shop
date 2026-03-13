from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ShoppingCart
from .serializers import ShoppingCartSerializer, ShoppingCartDetailSerializer
import time
from rest_framework import mixins
from .models import OrderInfo, OrderGoods
from .serializers import OrderSerializer, OrderDetailSerializer
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import OrderInfo, ShoppingCart
from .serializers import OrderSerializer, OrderDetailSerializer, ShoppingCartDetailSerializer
from .tasks import close_order_task  # 导入异步任务

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
        from django.db.models import Prefetch
        from .models import OrderGoods

        return OrderInfo.objects.filter(user=self.request.user)\
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