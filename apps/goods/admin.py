from django.contrib import admin
from .models import Category, Product, Banner  # 记得引入 Banner

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ["name", "parent_category", "is_tab", "add_time"]
    # 增加右侧过滤栏
    list_filter = ["is_tab", "parent_category"]
    # 增加顶部搜索框
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "goods_sn", "shop_price", "goods_num", "is_new", "is_hot"]
    list_filter = ["category", "is_new", "is_hot"]
    search_fields = ["name", "goods_sn"]

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["goods", "image", "index"]
