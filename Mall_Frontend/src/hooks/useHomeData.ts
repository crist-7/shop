/**
 * useHomeData.ts
 * 首页数据管理 Hook - 逻辑抽离与性能优化
 *
 * 功能：
 * 1. 获取分类列表、轮播图、商品列表
 * 2. 使用 Promise.all 实现并行请求优化
 * 3. 统一的 loading 状态管理
 * 4. 搜索和分类筛选功能
 */

import { ref, reactive, computed } from 'vue';
import { getCategoryList, getBannerList, getGoodsList } from '../api/goods';

// ============================================================
// 类型定义
// ============================================================

/** 商品数据结构 */
export interface GoodsItem {
  id: number;
  name: string;
  shop_price: number;
  goods_front_image?: string;
  category?: number;
  goods_desc?: string;
}

/** 分类数据结构 */
export interface CategoryItem {
  id: number;
  name: string;
  parent?: number;
}

/** 轮播图数据结构 */
export interface BannerItem {
  id: number;
  image: string;
  goods: number;
  index?: number;
}

/** 商品列表查询参数 */
export interface GoodsQueryParams {
  search?: string;
  category?: number | null;
  page?: number;
  page_size?: number;
}

/** Hook 返回值类型 */
export interface UseHomeDataReturn {
  // 状态
  loading: ReturnType<typeof ref<boolean>>;
  categoryList: ReturnType<typeof ref<CategoryItem[]>>;
  bannerList: ReturnType<typeof ref<BannerItem[]>>;
  goodsList: ReturnType<typeof ref<GoodsItem[]>>;
  searchKeyword: ReturnType<typeof ref<string>>;
  activeCategoryId: ReturnType<typeof ref<number | null>>;

  // 计算属性
  filteredGoods: ReturnType<typeof computed<GoodsItem[]>>;
  hasMore: ReturnType<typeof computed<boolean>>;

  // 方法
  fetchAllData: () => Promise<void>;
  fetchGoods: (params?: GoodsQueryParams) => Promise<void>;
  handleSearch: () => void;
  handleCategoryClick: (id: number | null) => void;
  resetFilters: () => void;
}

// ============================================================
// 主 Hook 实现
// ============================================================

/**
 * 首页数据管理 Hook
 *
 * @example
 * ```vue
 * <script setup>
 * import { useHomeData } from '../hooks/useHomeData';
 *
 * const {
 *   loading,
 *   categoryList,
 *   bannerList,
 *   goodsList,
 *   fetchAllData,
 *   handleSearch,
 *   handleCategoryClick
 * } = useHomeData();
 *
 * onMounted(() => fetchAllData());
 * </script>
 * ```
 */
export function useHomeData(): UseHomeDataReturn {
  // ============================================================
  // 响应式状态
  // ============================================================

  /** 全局加载状态 */
  const loading = ref(false);

  /** 商品列表加载状态（用于局部刷新） */
  const goodsLoading = ref(false);

  /** 分类列表 */
  const categoryList = ref<CategoryItem[]>([]);

  /** 轮播图列表 */
  const bannerList = ref<BannerItem[]>([]);

  /** 商品列表 */
  const goodsList = ref<GoodsItem[]>([]);

  /** 搜索关键词 */
  const searchKeyword = ref('');

  /** 当前选中的分类 ID */
  const activeCategoryId = ref<number | null>(null);

  /** 分页信息 */
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    total: 0,
  });

  // ============================================================
  // 计算属性
  // ============================================================

  /** 根据 search 和 category 过滤的商品列表 */
  const filteredGoods = computed(() => {
    let result = goodsList.value;

    // 按关键词过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase();
      result = result.filter(
        (item) =>
          item.name.toLowerCase().includes(keyword) ||
          item.goods_desc?.toLowerCase().includes(keyword)
      );
    }

    // 按分类过滤
    if (activeCategoryId.value) {
      result = result.filter((item) => item.category === activeCategoryId.value);
    }

    return result;
  });

  /** 是否还有更多数据 */
  const hasMore = computed(() => {
    return goodsList.value.length < pagination.total;
  });

  // ============================================================
  // 数据获取方法
  // ============================================================

  /**
   * 【性能优化】完全并行请求所有首页 API
   *
   * 优化原理：
   * - 原问题：多个 API 串行请求，总耗时 = t1 + t2 + t3
   * - 优化后：Promise.all 并行请求，总耗时 = max(t1, t2, t3)
   *
   * @returns Promise<void>
   */
  const fetchAllData = async (): Promise<void> => {
    loading.value = true;

    try {
      // 【核心优化】三个无依赖关系的 API 完全并行请求
      // 使用 Promise.all 确保所有请求完成后才更新状态
      const [catRes, bannerRes, goodsRes] = await Promise.all([
        getCategoryList().catch((err) => {
          console.error('分类接口失败:', err);
          return null;
        }),
        getBannerList().catch((err) => {
          console.error('轮播图接口失败:', err);
          return null;
        }),
        getGoodsList({ page_size: pagination.pageSize }).catch((err) => {
          console.error('商品接口失败:', err);
          return null;
        }),
      ]);

      // 各自处理数据，互不阻塞
      if (catRes) {
        // 兼容 DRF 分页格式和普通数组格式
        let categories = (catRes as any).results
          ? (catRes as any).results
          : (catRes as CategoryItem[]);
        // 过滤掉测试分类
        categoryList.value = categories.filter(
          (item: CategoryItem) => item.name !== '并发测试分类'
        );
      }

      if (bannerRes) {
        bannerList.value = (bannerRes as any).results
          ? (bannerRes as any).results
          : (bannerRes as BannerItem[]);
        // 按 index 排序
        bannerList.value.sort((a, b) => (a.index || 0) - (b.index || 0));
      }

      if (goodsRes) {
        const data = (goodsRes as any).results
          ? (goodsRes as any).results
          : (goodsRes as GoodsItem[]);
        goodsList.value = Array.isArray(data) ? data : [];
        // 更新总数（如果有分页信息）
        if ((goodsRes as any).count) {
          pagination.total = (goodsRes as any).count;
        }
      }
    } catch (error) {
      console.error('首页数据加载失败:', error);
    } finally {
      loading.value = false;
    }
  };

  /**
   * 单独获取商品列表（用于搜索和分类筛选）
   *
   * @param params - 查询参数
   */
  const fetchGoods = async (params?: GoodsQueryParams): Promise<void> => {
    goodsLoading.value = true;

    try {
      const queryParams: Record<string, any> = {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...params,
      };

      // 添加搜索关键词
      if (searchKeyword.value) {
        queryParams.search = searchKeyword.value;
      }

      // 添加分类筛选
      if (activeCategoryId.value) {
        queryParams.category = activeCategoryId.value;
      }

      const res = await getGoodsList(queryParams);
      const data = (res as any).results ? (res as any).results : (res as GoodsItem[]);
      goodsList.value = Array.isArray(data) ? data : [];

      // 更新分页信息
      if ((res as any).count) {
        pagination.total = (res as any).count;
      }
    } catch (error) {
      console.error('商品列表加载失败:', error);
    } finally {
      goodsLoading.value = false;
    }
  };

  // ============================================================
  // 交互方法
  // ============================================================

  /**
   * 处理搜索操作
   * 清除分类筛选，按关键词搜索商品
   */
  const handleSearch = (): void => {
    activeCategoryId.value = null;
    pagination.page = 1;
    fetchGoods();
  };

  /**
   * 处理分类点击
   * 清除搜索关键词，按分类筛选商品
   *
   * @param id - 分类 ID，null 表示显示全部
   */
  const handleCategoryClick = (id: number | null): void => {
    activeCategoryId.value = id;
    searchKeyword.value = '';
    pagination.page = 1;
    fetchGoods();
  };

  /**
   * 重置所有筛选条件
   */
  const resetFilters = (): void => {
    searchKeyword.value = '';
    activeCategoryId.value = null;
    pagination.page = 1;
    fetchGoods();
  };

  // ============================================================
  // 返回所有状态和方法
  // ============================================================

  return {
    // 状态
    loading,
    categoryList,
    bannerList,
    goodsList,
    searchKeyword,
    activeCategoryId,

    // 计算属性
    filteredGoods,
    hasMore,

    // 方法
    fetchAllData,
    fetchGoods,
    handleSearch,
    handleCategoryClick,
    resetFilters,
  };
}

// 默认导出
export default useHomeData;
