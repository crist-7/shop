from django.db import models

class Category(models.Model):
    """商品类别：支持无限级分类"""
    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")
    is_delete = models.BooleanField(default=False, verbose_name="是否逻辑删除")
    parent_category = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, verbose_name="父类目", related_name="sub_cat")
    is_tab = models.BooleanField(default=False, verbose_name="是否导航", help_text="是否显示在顶部导航")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")


    class Meta:
        verbose_name = "商品类别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Product(models.Model):
    """商品信息"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="商品类目")
    name = models.CharField(max_length=100, verbose_name="商品名")
    is_delete = models.BooleanField(default=False, verbose_name="是否逻辑删除")
    goods_sn = models.CharField(max_length=50, default="", verbose_name="商品唯一货号")
    sold_num = models.IntegerField(default=0, verbose_name="商品销售量")
    goods_num = models.IntegerField(default=0, verbose_name="库存数")
    market_price = models.FloatField(default=0, verbose_name="市场价格")
    shop_price = models.FloatField(default=0, verbose_name="本店价格")
    goods_brief = models.TextField(max_length=500, verbose_name="商品简短描述")
    # 【修改】：改用 CharField 以支持长 URL，长度设为 1000 足够存任何链接
    goods_front_image = models.CharField(max_length=1000, null=True, blank=True, verbose_name="封面图链接")
    is_new = models.BooleanField(default=False, verbose_name="是否新品")
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
class Banner(models.Model):
    """
    首页轮播图
    """
    # 关联到具体商品，点击轮播图可以直接跳转到该商品详情页
    goods = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    # 同样使用 CharField 存长链接，防止爆表
    image = models.CharField(max_length=1000, verbose_name="轮播图片链接")
    index = models.IntegerField(default=0, verbose_name="轮播顺序")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name