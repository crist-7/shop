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

    class Meta:
        model = Product
        fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"