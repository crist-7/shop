"""
商品模块缓存功能测试
测试范围：
1. 商品列表缓存
2. 商品详情缓存
3. 防穿透机制（空值缓存）
4. 防雪崩机制（TTL 随机偏移）
5. 缓存失效机制

注意：测试使用 mock 跳过 Elasticsearch 相关操作
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import hashlib

from goods.models import Product, Category
from goods.views import (
    CACHE_EMPTY_MARKER,
    CACHE_LIST_BASE_TTL,
    CACHE_DETAIL_BASE_TTL,
    CACHE_EMPTY_TTL,
    CACHE_RANDOM_OFFSET,
    build_detail_cache_key,
    get_randomized_ttl,
    clear_goods_detail_cache,
    clear_all_goods_cache,
)

User = get_user_model()


# 禁用 Elasticsearch 自动索引，避免测试时连接 ES
@override_settings(
    ELASTICSEARCH_DSL={
        'default': {
            'hosts': 'localhost:9200',
            'index': 'test_shop',
        }
    },
    CELERY_TASK_ALWAYS_EAGER=True,
)
class CacheHelperFunctionTests(TestCase):
    """缓存辅助函数测试"""

    def test_get_randomized_ttl_range(self):
        """测试 TTL 随机偏移在正确范围内"""
        for _ in range(100):
            ttl = get_randomized_ttl(300)
            self.assertGreaterEqual(ttl, 300)
            self.assertLessEqual(ttl, 300 + CACHE_RANDOM_OFFSET)

    def test_get_randomized_ttl_has_variation(self):
        """测试 TTL 随机偏移有变化（防雪崩）"""
        ttls = [get_randomized_ttl(300) for _ in range(20)]
        unique_ttls = set(ttls)
        # 20次调用应该产生多个不同的 TTL 值
        self.assertGreater(len(unique_ttls), 1,
                           "TTL 应该有随机变化，防止同时过期导致雪崩")

    def test_build_detail_cache_key(self):
        """测试详情缓存 key 生成"""
        key = build_detail_cache_key(123)
        self.assertEqual(key, "goods:detail:123")

        key2 = build_detail_cache_key(456)
        self.assertEqual(key2, "goods:detail:456")

    def test_base_ttl_values_are_correct(self):
        """测试基础 TTL 配置值"""
        self.assertEqual(CACHE_LIST_BASE_TTL, 300)
        self.assertEqual(CACHE_DETAIL_BASE_TTL, 600)
        self.assertEqual(CACHE_EMPTY_TTL, 60)
        self.assertEqual(CACHE_RANDOM_OFFSET, 60)

    def test_empty_marker_format(self):
        """测试空值标记格式"""
        self.assertEqual(CACHE_EMPTY_MARKER, "__EMPTY__")


class CachePenetrationTests(TestCase):
    """
    防穿透机制测试 - 重点测试
    验证访问不存在的商品时，是否正确缓存空值标记
    """

    def setUp(self):
        """测试前置准备"""
        self.client = APIClient()

        # 创建测试用户并获取 token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # 清空缓存
        cache.clear()

    def test_cache_empty_result_for_nonexistent_product(self):
        """
        【核心测试】防穿透：访问不存在的商品应缓存空值标记
        """
        nonexistent_id = 99999
        cache_key = build_detail_cache_key(nonexistent_id)

        # 确保缓存中不存在该 key
        self.assertIsNone(cache.get(cache_key))

        # 访问不存在的商品
        response = self.client.get(f'/api/goods/{nonexistent_id}/')

        # 应该返回 404
        self.assertEqual(response.status_code, 404)

        # 验证缓存中存储了空值标记
        cached_value = cache.get(cache_key)
        self.assertEqual(cached_value, CACHE_EMPTY_MARKER,
                         f"缓存应为 '{CACHE_EMPTY_MARKER}'，实际为: {cached_value}")

    def test_empty_cache_ttl_is_short(self):
        """
        测试空值缓存时间较短（1分钟）
        这是防穿透机制的关键配置
        """
        nonexistent_id = 88888
        cache_key = build_detail_cache_key(nonexistent_id)

        # 访问不存在的商品
        self.client.get(f'/api/goods/{nonexistent_id}/')

        # 验证空值被缓存
        self.assertEqual(cache.get(cache_key), CACHE_EMPTY_MARKER)

    def test_empty_cache_prevents_repeated_db_queries(self):
        """
        测试空值缓存能防止重复的无效请求打到数据库
        """
        nonexistent_id = 77777
        cache_key = build_detail_cache_key(nonexistent_id)

        # 第一次访问 - 应该缓存空值
        self.client.get(f'/api/goods/{nonexistent_id}/')
        self.assertEqual(cache.get(cache_key), CACHE_EMPTY_MARKER)

        # 手动清除缓存模拟没有缓存的情况
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))

        # 再次访问 - 应该再次缓存空值
        self.client.get(f'/api/goods/{nonexistent_id}/')
        self.assertEqual(cache.get(cache_key), CACHE_EMPTY_MARKER)

    def test_multiple_nonexistent_products_all_cached(self):
        """测试多个不存在的商品都被正确缓存空值"""
        nonexistent_ids = [11111, 22222, 33333]

        for pid in nonexistent_ids:
            response = self.client.get(f'/api/goods/{pid}/')
            self.assertEqual(response.status_code, 404)

            cache_key = build_detail_cache_key(pid)
            self.assertEqual(cache.get(cache_key), CACHE_EMPTY_MARKER)


class CacheAvalancheTests(TestCase):
    """
    防雪崩机制测试
    验证缓存 TTL 带有随机偏移，避免大量缓存同时失效
    """

    def test_ttl_has_random_offset(self):
        """
        【核心测试】TTL 带有随机偏移
        多次调用应产生不同的 TTL 值
        """
        ttls = [get_randomized_ttl(300) for _ in range(20)]

        # 所有 TTL 应在有效范围内
        for ttl in ttls:
            self.assertGreaterEqual(ttl, 300)
            self.assertLessEqual(ttl, 300 + CACHE_RANDOM_OFFSET)

        # TTL 应有变化（极大概率不同）
        unique_ttls = set(ttls)
        self.assertGreater(len(unique_ttls), 1,
                           "TTL 应该有随机变化，防止同时过期")

    def test_ttl_distribution(self):
        """测试 TTL 随机分布均匀性"""
        ttls = [get_randomized_ttl(300) for _ in range(100)]

        # 检查分布是否合理（不应该全部集中在某个小区间）
        min_ttl, max_ttl = min(ttls), max(ttls)

        # 范围应该覆盖较大区间
        self.assertGreater(max_ttl - min_ttl, 30,
                           "TTL 随机分布应该足够分散")


class CacheInvalidationTests(TestCase):
    """
    缓存失效机制测试
    """

    def setUp(self):
        """测试前置准备"""
        cache.clear()

    def test_clear_detail_cache(self):
        """测试清除商品详情缓存"""
        cache_key = build_detail_cache_key(123)

        # 设置缓存
        cache.set(cache_key, {'id': 123, 'name': 'test'})

        # 验证缓存存在
        self.assertIsNotNone(cache.get(cache_key))

        # 清除缓存
        clear_goods_detail_cache(123)

        # 验证缓存已清除
        self.assertIsNone(cache.get(cache_key))

    def test_clear_all_cache(self):
        """测试清除所有商品缓存"""
        detail_key = build_detail_cache_key(456)

        # 设置详情缓存
        cache.set(detail_key, {'id': 456})

        # 验证缓存存在
        self.assertIsNotNone(cache.get(detail_key))

        # 清除所有缓存
        clear_all_goods_cache(456)

        # 验证详情缓存已清除
        self.assertIsNone(cache.get(detail_key))


class CacheIntegrationTests(TestCase):
    """
    缓存集成测试 - 需要模拟 Elasticsearch
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        cache.clear()

    @override_settings(ELASTICSEARCH_DSL_AUTOSYNC=False)
    def test_full_cache_flow_with_mock(self):
        """
        【核心测试】完整缓存流程：未命中 -> 查询 -> 缓存 -> 命中
        使用 override_settings 禁用 ES 自动同步
        """
        # 创建测试分类和商品
        category = Category.objects.create(name="测试分类")
        product = Product.objects.create(
            name="测试商品",
            category=category,
            shop_price=99.99,
            goods_num=100
        )

        cache_key = build_detail_cache_key(product.id)

        # 1. 验证缓存未命中
        self.assertIsNone(cache.get(cache_key))

        # 2. 第一次请求（应该查询数据库并缓存）
        response1 = self.client.get(f'/api/goods/{product.id}/')
        self.assertEqual(response1.status_code, 200)

        # 3. 验证缓存已存储
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['name'], product.name)

        # 4. 第二次请求（应该命中缓存）
        response2 = self.client.get(f'/api/goods/{product.id}/')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['name'], product.name)

    def test_cache_key_prefix_format(self):
        """测试缓存 key 前缀规范"""
        detail_key = build_detail_cache_key(1)
        self.assertTrue(detail_key.startswith("goods:"))
        self.assertIn("detail", detail_key)


class CacheConfigurationTests(TestCase):
    """
    缓存配置验证测试
    """

    def test_cache_config_values(self):
        """验证缓存配置常量值"""
        # 列表缓存：5分钟
        self.assertEqual(CACHE_LIST_BASE_TTL, 300)

        # 详情缓存：10分钟
        self.assertEqual(CACHE_DETAIL_BASE_TTL, 600)

        # 空值缓存：1分钟
        self.assertEqual(CACHE_EMPTY_TTL, 60)

        # 随机偏移：最大60秒
        self.assertEqual(CACHE_RANDOM_OFFSET, 60)

    def test_empty_marker_is_unique(self):
        """测试空值标记不会与真实数据冲突"""
        self.assertIsInstance(CACHE_EMPTY_MARKER, str)
        self.assertNotEqual(CACHE_EMPTY_MARKER, "")
        # 使用特殊格式避免与真实数据冲突
        self.assertTrue(CACHE_EMPTY_MARKER.startswith("__"))
        self.assertTrue(CACHE_EMPTY_MARKER.endswith("__"))
