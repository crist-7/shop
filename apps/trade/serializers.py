from rest_framework import serializers
from .models import ShoppingCart
from goods.models import Product
from goods.serializers import ProductSerializer
from .models import OrderInfo, OrderGoods


class ShoppingCartSerializer(serializers.ModelSerializer):
    # 隐藏字段：自动获取当前登录的用户，不需要前端传过来，防止安全漏洞
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, min_value=1, error_messages={
        "min_value": "商品数量不能小于1",
        "required": "请选择购买数量"
    })

    # goods 字段是外键，DRF 默认会接收商品 ID

    class Meta:
        model = ShoppingCart
        fields = ("user", "goods", "nums", "id")
        validators = []

    def create(self, validated_data):
        """
        重写 create 方法：实现购物车中已有商品则数量累加，没有则新建
        """
        user = self.context["request"].user  # 获取当前请求的用户
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        # 检查商品是否已被逻辑删除
        if goods.is_delete:
            raise serializers.ValidationError("该商品已下架，无法加入购物车")

        # 去数据库里找找看，这个用户是不是已经加过这个商品了
        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums  # 如果存在，数量加上新的 nums
            existed.save()
        else:
            # 如果不存在，正常创建一条新记录
            existed = ShoppingCart.objects.create(**validated_data)

        return existed


class ShoppingCartDetailSerializer(serializers.ModelSerializer):
    """
    购物车列表详情的序列化器
    因为前端查看购物车时，需要看到商品的名字、图片、价格，而不仅仅是一个商品 ID
    """
    # 嵌套序列化器：把 goods 字段从 ID 变成完整的商品信息对象
    goods = ProductSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums", "id")
class OrderGoodsSerializer(serializers.ModelSerializer):
    """
    订单中的商品详情序列化器
    """
    goods = ProductSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"

class OrderDetailSerializer(serializers.ModelSerializer):
    """
    订单详情序列化器 (包含订单里面的商品列表)
    """
    # 这里的 goods 是模型中 related_name="goods" 定义的
    goods = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    """
    创建订单的序列化器
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 这些字段在创建时不需要前端传，设为只读
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    order_mount = serializers.FloatField(read_only=True)

    class Meta:
        model = OrderInfo
        # 前端创建订单时，只需要传收货人信息和留言即可
        fields = ("user", "order_sn", "trade_no", "pay_status", "pay_time",
                  "post_script", "order_mount", "signer_name", "signer_mobile", "address")


class OrderAddressSerializer(serializers.Serializer):
    """修改收货地址的序列化器"""
    address = serializers.CharField(max_length=100, required=False)
    signer_name = serializers.CharField(max_length=20, required=False)
    signer_mobile = serializers.CharField(max_length=11, required=False)

    def validate(self, attrs):
        # 至少提供一个字段
        if not any(attrs.values()):
            raise serializers.ValidationError("至少需要提供一个地址字段（address, signer_name, signer_mobile）")

        # 手机号格式验证
        if attrs.get('signer_mobile'):
            if not attrs['signer_mobile'].isdigit() or len(attrs['signer_mobile']) != 11:
                raise serializers.ValidationError("手机号格式不正确，应为11位数字")

        return attrs