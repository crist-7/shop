from rest_framework import mixins, viewsets, filters
from .permissions import IsAdminUserOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Product, Category, Banner
from .serializers import ProductSerializer, CategorySerializer, BannerSerializer
from .filters import ProductFilter
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from rest_framework import mixins, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Banner
from .serializers import ProductSerializer, CategorySerializer, BannerSerializer
from .filters import ProductFilter
from .permissions import IsAdminUserOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    """
    商品列表页：使用 select_related 优化分类外键查询
    """
    # 优化点：一次性预加载 category 信息，避免序列化时重复查询数据库
    queryset = Product.objects.filter(is_delete=False).select_related('category').order_by('id')
    serializer_class = ProductSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ('name', 'goods_brief')
    ordering_fields = ('sold_num', 'shop_price')

    def destroy(self, request, *args, **kwargs):
        """重写删除方法实现逻辑删除"""
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoodsPagination(PageNumberPagination):
    """自定义分页配置"""
    page_size = 10  # 默认每页显示 10 条
    page_size_query_param = 'page_size'  # 允许前端通过 url 参数指定每页几条
    page_query_param = "page"  # 第几页的参数名
    max_page_size = 100  # 限制每页最大数量


class ProductViewSet(viewsets.ModelViewSet):
    """
    商品列表页, 分页, 搜索, 过滤, 排序
    """
    queryset = Product.objects.all().order_by('id')  # 默认排序
    serializer_class = ProductSerializer
    pagination_class = GoodsPagination

    # 【安全升级】：替换 AllowAny
    permission_classes = (IsAdminUserOrReadOnly,)

    # 配置三大过滤器后端：DjangoFilter(字段过滤), SearchFilter(关键词搜索), OrderingFilter(排序)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

    # 指定过滤类
    filterset_class = ProductFilter

    # 指定搜索字段 (支持按商品名、简介搜索)
    search_fields = ('name', 'goods_brief')

    # 指定排序字段 (允许前端按销量、价格排序)
    ordering_fields = ('sold_num', 'shop_price')
class CategoryViewSet(viewsets.ModelViewSet):
    """
    商品分类管理 (增删改查)
    """
    queryset = Category.objects.filter(is_delete=False).order_by('id')
    serializer_class = CategorySerializer
    # 【安全升级】：替换 AllowAny
    permission_classes = (IsAdminUserOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        """重写删除方法实现逻辑删除"""
        instance = self.get_object()
        # 进阶建议：删除分类时，也可以逻辑删除该分类下的所有商品
        # Product.objects.filter(category=instance).update(is_delete=True)
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BannerViewSet(viewsets.ModelViewSet):
    """
    获取首页轮播图
    """
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializer
    permission_classes = (IsAdminUserOrReadOnly,) # 游客只能看，管理员能改
# 【新增】独立的文件上传接口
class ImageUploadView(APIView):
    # 允许解析 multipart/form-data 格式（文件上传标准格式）
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file') # 获取前端传来的 file 字段
        if not file_obj:
            return Response({'error': '请选择文件'}, status=400)

        # 1. 生成随机文件名，防止重名覆盖
        ext = os.path.splitext(file_obj.name)[1]
        file_name = f"uploads/{uuid.uuid4()}{ext}"

        # 2. 保存文件到 MEDIA_ROOT
        path = default_storage.save(file_name, ContentFile(file_obj.read()))

        # 3. 拼接完整的访问链接 (http://localhost:8000/media/uploads/xxxx.jpg)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + path)

        return Response({
            'url': file_url,
            'name': file_obj.name
        })
