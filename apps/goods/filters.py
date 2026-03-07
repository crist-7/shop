# @Version  :1.0
# @Author   :crist
# @File     :filters.py.py
import django_filters
from .models import Product

class ProductFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    # 价格区间过滤：name对应模型字段，lookup_expr对应比较操作
    min_price = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte', help_text="最低价格")
    max_price = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte', help_text="最高价格")
    # 模糊查询：name包含什么
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'is_hot', 'is_new', 'category']