from rest_framework import serializers
from .models import Product, Category, Banner


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # 【核心修复1】：覆盖默认的 ImageField 校验，允许前端直接传 URL 字符串
    goods_front_image = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)

    # 【核心修复2】：将商品简介设为非必填，防止前端没传导致 400 报错
    goods_brief = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    # 【电商营销优化】：动态计算原价，增强价格对比效果
    original_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'is_delete', 'goods_sn', 'sold_num', 'goods_num',
            'market_price', 'shop_price', 'goods_brief', 'goods_front_image',
            'is_new', 'is_hot', 'add_time', 'original_price'
        ]

    def get_original_price(self, obj):
        """
        动态计算商品原价，用于前端价格展示
        规则：如果数据库中的市场价(market_price)为0，则根据当前售价(shop_price)的120%计算
        这种处理方式在电商营销心理学中能创造价格对比，提升用户购买意愿
        """
        if obj.market_price and obj.market_price > 0:
            # 如果数据库中有有效的市场价，直接返回
            return round(float(obj.market_price), 2)
        else:
            # 如果市场价为0或不存在，基于当前售价计算120%作为原价
            calculated_price = float(obj.shop_price) * 1.2
            return round(calculated_price, 2)

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"