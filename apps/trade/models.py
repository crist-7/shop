from django.db import models
from django.contrib.auth import get_user_model
from goods.models import Product

# 获取我们在 settings 中配置的自定义 User 模型
User = get_user_model()

class ShoppingCart(models.Model):
    """购物车"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    goods = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    nums = models.IntegerField(default=0, verbose_name="购买数量")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = verbose_name
        # 联合唯一：同一个用户同一件商品只能有一条记录
        unique_together = ("user", "goods")

    def __str__(self):
        return f"{self.goods.name} ({self.nums})"

class OrderInfo(models.Model):
    """订单主信息"""
    ORDER_STATUS = (
        ("TRADE_SUCCESS", "成功"),
        ("TRADE_CLOSED", "超时关闭"),
        ("WAIT_BUYER_PAY", "交易创建"),
        ("TRADE_FINISHED", "交易结束"),
        ("PAYING", "待支付"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name="订单号")
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="第三方支付交易号")
    pay_status = models.CharField(choices=ORDER_STATUS, default="PAYING", max_length=30, verbose_name="订单状态")
    post_script = models.CharField(max_length=200, null=True, blank=True, verbose_name="订单留言")
    order_mount = models.FloatField(default=0.0, verbose_name="订单总金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    # 订单快照信息：防止用户未来修改了个人资料，导致历史订单的收货信息跟着变
    address = models.CharField(max_length=100, default="", verbose_name="收货详细地址")
    signer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)

class OrderGoods(models.Model):
    """订单商品详情（子订单）"""
    # related_name="goods" 方便后续通过订单反向查询包含的所有商品
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name="订单信息", related_name="goods")
    goods = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    goods_num = models.IntegerField(default=0, verbose_name="商品数量")
    price = models.FloatField(default=0.0, verbose_name="成交价格")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单商品详情"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order.order_sn)