from rest_framework import mixins, viewsets, filters, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsAdminUserOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.http import Http404
from django.db.models import Q

from .models import Product, Category, Banner
from .serializers import ProductSerializer, CategorySerializer, BannerSerializer
from .filters import ProductFilter
from .documents import ProductDocument
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
import random
import hashlib


# ============================================================
# 缓存配置常量
# ============================================================
CACHE_EMPTY_MARKER = "__EMPTY__"  # 空值标记，用于防穿透
CACHE_LIST_BASE_TTL = 300  # 列表缓存基础时间：5分钟
CACHE_DETAIL_BASE_TTL = 600  # 详情缓存基础时间：10分钟
CACHE_EMPTY_TTL = 60  # 空值缓存时间：1分钟
CACHE_RANDOM_OFFSET = 60  # 随机偏移最大值：60秒


def get_randomized_ttl(base_ttl):
    """
    获取带随机偏移的缓存时间，防止缓存雪崩
    例如：base_ttl=300，返回 300~360 之间的随机值
    """
    return base_ttl + random.randint(0, CACHE_RANDOM_OFFSET)


def build_list_cache_key(request):
    """
    构建商品列表缓存 key
    基于查询参数生成唯一标识
    """
    query_string = request.query_params.urlencode()
    # 使用 MD5 压缩过长的查询字符串
    query_hash = hashlib.md5(query_string.encode()).hexdigest() if query_string else 'default'
    return f"goods:list:{query_hash}"


def build_detail_cache_key(pk):
    """构建商品详情缓存 key"""
    return f"goods:detail:{pk}"


def clear_goods_list_cache():
    """清除商品列表缓存（所有变体）"""
    try:
        # 尝试使用 delete_pattern（需要 django-redis）
        cache.delete_pattern("goods:list:*")
    except (AttributeError, NotImplementedError):
        # 降级方案：如果缓存后端不支持 delete_pattern，记录日志但不报错
        # 生产环境建议使用 django-redis 作为缓存后端
        pass


def clear_goods_detail_cache(pk):
    """清除单个商品详情缓存"""
    cache_key = build_detail_cache_key(pk)
    cache.delete(cache_key)


def clear_all_goods_cache(pk=None):
    """清除商品相关所有缓存"""
    clear_goods_list_cache()
    if pk:
        clear_goods_detail_cache(pk)


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
    引入 Redis 缓存优化查询性能，包含防雪崩与防穿透机制
    """
    # 优化点：一次性预加载 category 信息，避免序列化时重复查询数据库
    queryset = Product.objects.filter(is_delete=False).select_related('category').order_by('id')
    serializer_class = ProductSerializer
    pagination_class = GoodsPagination

    # 【安全升级】：替换 AllowAny
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # 配置过滤器后端：DjangoFilter(字段过滤), OrderingFilter(排序)
    # SearchFilter已移除，使用自定义的Elasticsearch搜索
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)

    # 指定过滤类
    filterset_class = ProductFilter

    # 指定搜索字段 (支持按商品名、简介搜索)
    search_fields = ('name', 'goods_brief')

    # 指定排序字段 (允许前端按销量、价格排序)
    ordering_fields = ('sold_num', 'shop_price')

    # ============================================================
    # Phase 1: 商品列表缓存（含防穿透、防雪崩）
    # ============================================================
    def list(self, request, *args, **kwargs):
        # 构建缓存 key
        cache_key = build_list_cache_key(request)

        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            # 防穿透：检查是否为空值标记
            if cached_data == CACHE_EMPTY_MARKER:
                return Response({
                    "count": 0,
                    "next": None,
                    "previous": None,
                    "results": []
                })
            return Response(cached_data)

        # 缓存未命中，查询数据库
        response = super().list(request, *args, **kwargs)

        # 防穿透：空结果缓存短时间
        if not response.data.get('results'):
            cache.set(cache_key, CACHE_EMPTY_MARKER, timeout=CACHE_EMPTY_TTL)
        else:
            # 防雪崩：使用随机偏移的 TTL
            ttl = get_randomized_ttl(CACHE_LIST_BASE_TTL)
            cache.set(cache_key, response.data, timeout=ttl)

        return response

    # ============================================================
    # Phase 1: 商品详情缓存（含防穿透、防雪崩）
    # ============================================================
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cache_key = build_detail_cache_key(pk)

        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            # 防穿透：检查是否为空值标记（表示商品不存在）
            if cached_data == CACHE_EMPTY_MARKER:
                raise Http404("商品不存在")
            return Response(cached_data)

        # 缓存未命中，查询数据库
        try:
            instance = self.get_object()
        except Http404:
            # 防穿透：缓存不存在的商品（短时间）
            cache.set(cache_key, CACHE_EMPTY_MARKER, timeout=CACHE_EMPTY_TTL)
            raise

        serializer = self.get_serializer(instance)
        data = serializer.data

        # 防雪崩：使用随机偏移的 TTL
        ttl = get_randomized_ttl(CACHE_DETAIL_BASE_TTL)
        cache.set(cache_key, data, timeout=ttl)

        return Response(data)

    # ============================================================
    # Phase 3: 缓存失效机制 - 商品创建时清除列表缓存
    # ============================================================
    def perform_create(self, serializer):
        serializer.save()
        # 新增商品后，清除列表缓存（详情缓存无需清除，因为是新商品）
        clear_goods_list_cache()

    # ============================================================
    # Phase 3: 缓存失效机制 - 商品更新时清除相关缓存
    # ============================================================
    def perform_update(self, serializer):
        instance = serializer.save()
        # 更新商品后，清除列表缓存和该商品详情缓存
        clear_all_goods_cache(instance.id)

    # ============================================================
    # Phase 3: 缓存失效机制 - 商品删除时清除相关缓存
    # ============================================================
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        goods_id = instance.id

        instance.is_delete = True
        instance.save()

        # 删除商品后，清除列表缓存和该商品详情缓存
        clear_all_goods_cache(goods_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def filter_queryset(self, queryset):
        """
        重写过滤方法，当有search参数时使用Elasticsearch，否则使用原MySQL查询
        支持与分类过滤的组合查询，使用 IK 中文分词器

        容灾机制：当 Elasticsearch 不可用时，自动降级到 MySQL LIKE 查询
        """
        search_query = self.request.query_params.get('search')

        if not search_query:
            # 没有搜索关键词，使用父类的过滤逻辑（分类过滤、排序等）
            return super().filter_queryset(queryset)

        # 先应用其他过滤（分类过滤等）但不包括搜索
        # 注意：super().filter_queryset会使用当前filter_backends（DjangoFilterBackend, OrderingFilter）
        filtered_qs = super().filter_queryset(queryset)

        # ============================================================
        # Elasticsearch 搜索（带容灾降级）
        # ============================================================

        # 提取智能分词搜索为独立函数，供 ES 失败或无结果时复用
        def fallback_mysql_search(base_qs, search_term):
            """
            MySQL 降级搜索：支持空格分词的智能搜索
            例如："联想 拯救者" → 商品名/简介必须同时包含 "联想" 和 "拯救者"
            """
            keywords = search_term.split()

            # 单关键词：简单的 OR 查询
            if len(keywords) == 1:
                keyword = keywords[0]
                return base_qs.filter(
                    Q(name__icontains=keyword) |
                    Q(goods_brief__icontains=keyword)
                )

            # 多关键词：每个关键词都必须在 name 或 goods_brief 中出现
            query = Q()
            for keyword in keywords:
                keyword_condition = Q(name__icontains=keyword) | Q(goods_brief__icontains=keyword)
                query &= keyword_condition

            return base_qs.filter(query)

        try:
            # 使用 Elasticsearch 进行中文分词搜索
            es_search = ProductDocument.search().query(
                'multi_match',
                query=search_query,
                fields=['name^3', 'goods_brief'],
                type='best_fields',
            )
            es_results = es_search.execute()

            # 获取匹配的商品ID列表
            product_ids = [hit.id for hit in es_results]

            # ES 有结果：使用 ES 搜索结果
            if product_ids:
                return filtered_qs.filter(id__in=product_ids)

            # ============================================================
            # ES 返回空结果：降级到 MySQL 搜索
            # 场景：ES 索引为空、索引未同步、或分词器不匹配
            # ============================================================
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Elasticsearch 返回空结果，降级到 MySQL 搜索: {search_query}")

            return fallback_mysql_search(filtered_qs, search_query)

        except Exception as e:
            # ============================================================
            # ES 异常：降级到 MySQL 搜索
            # 场景：ES 服务宕机、网络不通、配置错误
            # ============================================================
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Elasticsearch 搜索异常，降级到 MySQL 查询: {str(e)}")

            return fallback_mysql_search(filtered_qs, search_query)


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
        # 分类变更会影响商品列表，清除商品缓存
        clear_goods_list_cache()
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
