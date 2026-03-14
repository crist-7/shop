from rest_framework import serializers
from .models import Product, Category, Banner


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """
    商品完整序列化器（用于详情页）
    """
    # 覆盖默认的 ImageField 校验，允许前端直接传 URL 字符串
    goods_front_image = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)

    # 将商品简介设为非必填
    goods_brief = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    # 动态计算原价
    original_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'is_delete', 'goods_sn', 'sold_num', 'goods_num',
            'market_price', 'shop_price', 'goods_brief', 'goods_front_image',
            'is_new', 'is_hot', 'add_time', 'original_price'
        ]

    def get_original_price(self, obj):
        """动态计算商品原价"""
        if obj.market_price and obj.market_price > 0:
            return round(float(obj.market_price), 2)
        else:
            calculated_price = float(obj.shop_price) * 1.2
            return round(calculated_price, 2)


class ProductListSerializer(serializers.ModelSerializer):
    """
    【性能优化】商品列表精简序列化器
    只返回列表页需要的字段，减少数据传输量
    用于商品列表接口，不包含详情页才需要的字段
    """
    # 覆盖默认的 ImageField 校验
    goods_front_image = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)

    # 动态计算原价（列表页也需要)
    original_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'shop_price', 'market_price',
            'goods_front_image', 'sold_num', 'is_new', 'is_hot',
            'original_price'
        ]
        # 【性能优化】减少字段数量，不包含：
        # - category: 列表页通常不需要分类详情
        # - goods_sn: 商品编号，内部使用
        # - goods_num: 库存数，详情页才需要
        # - goods_brief: 商品简介，详情页才需要
        # - is_delete: 逻辑删除标记，内部使用
        # - add_time: 添加时间，内部使用

    def get_original_price(self, obj):
        """动态计算商品原价"""
        if obj.market_price and obj.market_price > 0:
            return round(float(obj.market_price), 2)
        else:
            calculated_price = float(obj.shop_price) * 1.2
            return round(calculated_price, 2)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"