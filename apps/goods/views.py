from rest_framework import mixins, viewsets, filters, permissions, status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from .models import Product, Category, Banner
from .serializers import ProductSerializer, CategorySerializer, BannerSerializer
from .filters import ProductFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid

class GoodsPagination(PageNumberPagination):
    """自定义分页配置"""
    page_size = 10  # 默认每页显示 10 条
    page_size_query_param = 'page_size'  # 允许前端通过 url 参数指定每页几条
    page_query_param = "page"  # 第几页的参数名
    max_page_size = 100  # 限制每页最大数量


class ProductViewSet(viewsets.ModelViewSet):
    """
    商品列表页, 分页, 搜索, 过滤, 排序
    使用 select_related 优化分类外键查询，解决 N+1 问题
    """
    # 优化点：一次性预加载 category 信息，避免序列化时重复查询数据库
    queryset = Product.objects.filter(is_delete=False).select_related('category').order_by('id')
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

    def destroy(self, request, *args, **kwargs):
        """重写删除方法实现逻辑删除"""
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    商品分类管理 (增删改查)
    使用 select_related 优化父级分类查询，解决 N+1 问题
    """
    # 优化点：预加载父级分类，避免在显示分类层级时产生 N+1 查询
    queryset = Category.objects.filter(is_delete=False).select_related('parent_category').order_by('id')
    serializer_class = CategorySerializer
    # 【安全升级】：替换 AllowAny
    permission_classes = (IsAdminUserOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        # 可选：同步逻辑删除该分类下的所有商品
        Product.objects.filter(category=instance).update(is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @method_decorator(cache_page(60 * 60))  # 缓存1小时
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # 缓存1小时
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class BannerViewSet(viewsets.ModelViewSet):
    """
    获取首页轮播图
    使用 select_related 优化商品信息查询
    """
    # 优化点：预加载关联的商品信息，避免在显示轮播图时产生额外查询
    queryset = Banner.objects.select_related('goods').order_by('index')
    serializer_class = BannerSerializer
    permission_classes = (IsAdminUserOrReadOnly,) # 游客只能看，管理员能改

    @method_decorator(cache_page(60 * 60))  # 缓存1小时
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # 缓存1小时
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
# 【新增】独立的文件上传接口
class ImageUploadView(APIView):
    # 允许解析 multipart/form-data 格式（文件上传标准格式）
    parser_classes = (MultiPartParser,)
    # 文件上传需要认证
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file') # 获取前端传来的 file 字段
        if not file_obj:
            return Response({'error': '请选择文件'}, status=400)

        # 安全检查：验证文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in allowed_extensions:
            return Response({'error': '只支持以下图片格式：jpg, jpeg, png, gif, webp'}, status=400)

        # 安全检查：验证文件大小（限制为 5MB）
        max_size = 5 * 1024 * 1024  # 5MB
        if file_obj.size > max_size:
            return Response({'error': '文件大小不能超过 5MB'}, status=400)

        # 安全检查：验证文件内容
        allowed_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file_obj.content_type not in allowed_mime_types:
            return Response({'error': '不支持的文件类型'}, status=400)

        # 1. 生成随机文件名，防止重名覆盖
        file_name = f"uploads/{uuid.uuid4()}{ext}"

        # 2. 保存文件到 MEDIA_ROOT
        path = default_storage.save(file_name, ContentFile(file_obj.read()))

        # 3. 拼接完整的访问链接 (http://localhost:8000/media/uploads/xxxx.jpg)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + path)

        return Response({
            'url': file_url,
            'name': file_obj.name
        })
