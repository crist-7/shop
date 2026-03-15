<template>
  <!--
    GoodsDetail.vue - 星辰商城商品详情页

    功能特性：
    1. 左侧图片画廊（主图 + 缩略图 hover 切换）
    2. 右侧商品信息（名称、价格、描述）
    3. 数量选择器 + 购物车操作
    4. 玻璃拟态卡片效果
  -->
  <div class="goods-detail-page">
    <!-- ============================================================ -->
    <!-- 简洁头部导航 -->
    <!-- ============================================================ -->
    <header class="detail-header">
      <div class="header-inner">
        <router-link to="/" class="logo-link">
          <span class="logo-icon">🛍️</span>
          <span class="logo-text">星辰商城</span>
        </router-link>
        <el-icon class="breadcrumb-sep"><ArrowRight /></el-icon>
        <span class="current-page">商品详情</span>

        <!-- 右侧快捷操作 -->
        <div class="header-actions">
          <el-button
            v-if="userStore.isLoggedIn"
            class="cart-btn"
            @click="cartStore.toggleDrawer(true)"
          >
            <el-icon><ShoppingCart /></el-icon>
            <el-badge :value="cartStore.cartCount" :hidden="cartStore.cartCount === 0" class="cart-badge" />
          </el-button>
        </div>
      </div>
    </header>

    <!-- ============================================================ -->
    <!-- 主内容区 -->
    <!-- ============================================================ -->
    <main class="detail-main">
      <div class="detail-container" v-if="goodsInfo">
        <!-- ==================== 左侧图片画廊 ==================== -->
        <section class="gallery-section">
          <!-- 主图展示区 -->
          <div class="main-image-wrapper">
            <div class="main-image-container">
              <img
                :src="currentMainImage"
                :alt="goodsInfo.name"
                class="main-image"
                @mouseenter="isZooming = true"
                @mouseleave="isZooming = false"
                :class="{ 'zooming': isZooming }"
              />
              <!-- 图片放大镜提示 -->
              <div class="zoom-hint" v-if="!isZooming">
                <el-icon><ZoomIn /></el-icon>
                <span>悬停放大</span>
              </div>
            </div>
          </div>

          <!-- 缩略图列表 -->
          <div class="thumbnail-list">
            <div
              v-for="(img, index) in galleryImages"
              :key="index"
              class="thumbnail-item"
              :class="{ active: currentImageIndex === index }"
              @mouseenter="currentImageIndex = index"
              @click="currentImageIndex = index"
            >
              <img :src="img" :alt="`缩略图${index + 1}`" class="thumbnail-img" />
            </div>
          </div>
        </section>

        <!-- ==================== 右侧商品信息 ==================== -->
        <section class="info-section">
          <div class="info-card">
            <!-- 商品标题 -->
            <div class="title-area">
              <h1 class="goods-title">{{ goodsInfo.name }}</h1>
            </div>

            <!-- 商品简介 -->
            <p class="goods-brief">{{ goodsInfo.goods_brief || '精选好物，品质保证，让您购物无忧。' }}</p>

            <!-- 价格展示区 -->
            <div class="price-area">
              <div class="price-main">
                <span class="price-symbol">¥</span>
                <span class="price-value">{{ formatPrice(goodsInfo.shop_price) }}</span>
              </div>
            </div>

            <!-- 销量与库存 -->
            <div class="stats-area">
              <div class="stat-item">
                <span class="stat-label">销量</span>
                <span class="stat-value">{{ goodsInfo.sold_num || 0 }}件</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-label">库存</span>
                <span class="stat-value">{{ goodsInfo.goods_num || 0 }}件</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-label">好评率</span>
                <span class="stat-value highlight">98%</span>
              </div>
            </div>

            <!-- ==================== 数量选择器 ==================== -->
            <div class="quantity-area">
              <span class="quantity-label">数量</span>
              <div class="quantity-control">
                <el-input-number
                  v-model="buyCount"
                  :min="1"
                  :max="goodsInfo.goods_num || 99"
                  size="large"
                  class="quantity-input"
                />
                <span class="stock-hint">
                  库存 <em>{{ goodsInfo.goods_num || 0 }}</em> 件
                </span>
              </div>
            </div>

            <!-- ==================== 操作按钮区 ==================== -->
            <div class="action-area">
              <el-button
                type="primary"
                size="large"
                class="btn-cart"
                :loading="isAddingToCart"
                @click="handleAddToCart"
              >
                <el-icon><ShoppingCart /></el-icon>
                <span>加入购物车</span>
              </el-button>
              <el-button
                type="danger"
                size="large"
                class="btn-buy"
                @click="handleBuyNow"
              >
                <el-icon><Lightning /></el-icon>
                <span>立即购买</span>
              </el-button>
            </div>

            <!-- 服务承诺 -->
            <div class="service-area">
              <div class="service-item">
                <el-icon><CircleCheck /></el-icon>
                <span>正品保证</span>
              </div>
              <div class="service-item">
                <el-icon><Van /></el-icon>
                <span>极速发货</span>
              </div>
              <div class="service-item">
                <el-icon><RefreshLeft /></el-icon>
                <span>7天无理由退换</span>
              </div>
              <div class="service-item">
                <el-icon><Service /></el-icon>
                <span>专属客服</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 加载状态骨架屏 -->
      <div class="loading-skeleton" v-else>
        <div class="skeleton-gallery">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="image" style="width: 100%; height: 500px;" />
            </template>
          </el-skeleton>
        </div>
        <div class="skeleton-info">
          <el-skeleton animated :rows="8" />
        </div>
      </div>
    </main>

    <!-- 购物车抽屉 -->
    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
/**
 * GoodsDetail.vue - 商品详情页
 *
 * 功能：
 * 1. 图片画廊（主图 + 缩略图 hover 切换）
 * 2. 数量选择器
 * 3. 加入购物车 / 立即购买
 */

import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  ArrowRight,
  ShoppingCart,
  ZoomIn,
  Lightning,
  CircleCheck,
  Van,
  RefreshLeft,
  Service,
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { getGoodsDetail } from '../api/goods';
import { useUserStore } from '../store/user';
import { useCartStore } from '../store/cart';
import CartDrawer from '../components/CartDrawer.vue';

// ============================================================
// 路由和 Store
// ============================================================

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const cartStore = useCartStore();

// ============================================================
// 商品数据状态
// ============================================================

/** 商品详情数据 */
const goodsInfo = ref<any>(null);

/** 当前显示的主图索引 */
const currentImageIndex = ref(0);

/** 是否正在放大查看 */
const isZooming = ref(false);

/** 购买数量 */
const buyCount = ref(1);

/** 是否正在添加到购物车 */
const isAddingToCart = ref(false);

// ============================================================
// 计算属性
// ============================================================

/**
 * 图片画廊 - 主图 + 多角度展示
 * 如果商品只有一张图，则用主图填充画廊
 */
const galleryImages = computed(() => {
  if (!goodsInfo.value) return [];
  const mainImage = goodsInfo.value.goods_front_image;
  if (!mainImage) return [];

  // 模拟多角度图片（实际项目中应从后端获取）
  return [
    mainImage,
    // 如果有更多图片 URL，可以在这里添加
    // goodsInfo.value.image_2,
    // goodsInfo.value.image_3,
  ].filter(Boolean);
});

/**
 * 当前显示的主图 URL
 */
const currentMainImage = computed(() => {
  return galleryImages.value[currentImageIndex.value] || '';
});

// ============================================================
// 工具函数
// ============================================================

/**
 * 格式化价格（确保显示两位小数）
 */
const formatPrice = (price: number | undefined | null): string => {
  if (price === undefined || price === null || isNaN(price)) {
    return '0.00';
  }
  return price.toFixed(2);
};

// ============================================================
// 数据获取
// ============================================================

/**
 * 加载商品详情
 */
const loadGoodsDetail = async () => {
  const id = Number(route.params.id);
  if (!id) {
    ElMessage.error('商品ID无效');
    router.push('/');
    return;
  }

  try {
    const res = await getGoodsDetail(id);
    goodsInfo.value = res;
    // 重置图片索引
    currentImageIndex.value = 0;
  } catch (error) {
    console.error('获取商品详情失败:', error);
    ElMessage.error('商品不存在或已下架');
    router.push('/');
  }
};

// ============================================================
// 用户操作
// ============================================================

/**
 * 加入购物车
 */
const handleAddToCart = async () => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }

  // 检查商品数据
  if (!goodsInfo.value) return;

  isAddingToCart.value = true;
  try {
    await cartStore.addToCartAction({
      goods: goodsInfo.value.id,
      nums: buyCount.value,
    });
    ElMessage.success({
      message: `已添加 ${buyCount.value} 件商品到购物车`,
      duration: 2000,
    });
  } catch (error) {
    console.error('添加购物车失败:', error);
  } finally {
    isAddingToCart.value = false;
  }
};

/**
 * 立即购买
 */
const handleBuyNow = async () => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }

  // 先加入购物车
  await handleAddToCart();
  // 打开购物车抽屉进行结算
  cartStore.toggleDrawer(true);
};

// ============================================================
// 生命周期
// ============================================================

onMounted(() => {
  loadGoodsDetail();
});
</script>

<style scoped>
/* ============================================================ */
/* 页面整体布局 */
/* ============================================================ */

.goods-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
}

/* ============================================================ */
/* 头部导航 */
/* ============================================================ */

.detail-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--bg-tertiary);
  box-shadow: var(--shadow-sm);
}

.header-inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  height: 64px;
  padding: 0 var(--space-xl);
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  text-decoration: none;
  color: var(--primary-color);
  font-weight: 700;
  font-size: 20px;
  transition: all var(--transition-fast);
}

.logo-link:hover {
  transform: scale(1.02);
}

.logo-icon {
  font-size: 24px;
}

.breadcrumb-sep {
  margin: 0 var(--space-md);
  color: var(--text-tertiary);
  font-size: 12px;
}

.current-page {
  color: var(--text-secondary);
  font-size: 14px;
}

.header-actions {
  margin-left: auto;
}

.cart-btn {
  position: relative;
  padding: var(--space-sm) var(--space-md);
}

.cart-badge {
  position: absolute;
  top: 0;
  right: 0;
}

/* ============================================================ */
/* 主内容区 */
/* ============================================================ */

.detail-main {
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: var(--space-3xl) var(--space-xl);
}

.detail-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4xl);
  align-items: start;
}

@media (max-width: 1024px) {
  .detail-container {
    grid-template-columns: 1fr;
    gap: var(--space-2xl);
  }
}

/* ============================================================ */
/* 左侧图片画廊 */
/* ============================================================ */

.gallery-section {
  position: sticky;
  top: 96px;
}

/* 主图容器 */
.main-image-wrapper {
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  margin-bottom: var(--space-lg);
}

.main-image-container {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  cursor: zoom-in;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: var(--space-2xl);
  transition: transform var(--transition-slow);
}

.main-image.zooming {
  transform: scale(1.5);
  cursor: move;
}

/* 放大提示 */
.zoom-hint {
  position: absolute;
  bottom: var(--space-lg);
  right: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: var(--radius-full);
  font-size: 12px;
  pointer-events: none;
  opacity: 0.8;
}

/* 缩略图列表 */
.thumbnail-list {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  padding: var(--space-sm) 0;
}

.thumbnail-item {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  background: var(--bg-primary);
  transition: all var(--transition-fast);
}

.thumbnail-item:hover {
  border-color: var(--primary-light);
}

.thumbnail-item.active {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-primary-glow);
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ============================================================ */
/* 右侧商品信息 */
/* ============================================================ */

.info-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--radius-2xl);
  padding: var(--space-3xl);
  box-shadow: var(--shadow-lg),
              0 8px 32px rgba(139, 92, 246, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .info-card {
    background: rgba(30, 27, 75, 0.8);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* 标题区域 */
.title-area {
  margin-bottom: var(--space-lg);
}

.goods-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  margin: 0;
}

/* 商品简介 */
.goods-brief {
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: var(--space-2xl);
}

/* ============================================================ */
/* 价格展示区 */
/* ============================================================ */

.price-area {
  display: flex;
  align-items: flex-end;
  gap: var(--space-lg);
  padding: var(--space-xl);
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-2xl);
}

@media (prefers-color-scheme: dark) {
  .price-area {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.2) 100%);
  }
}

.price-main {
  display: flex;
  align-items: baseline;
}

.price-symbol {
  font-size: 20px;
  font-weight: 600;
  color: var(--danger);
  margin-right: 2px;
}

.price-value {
  font-size: 42px;
  font-weight: 700;
  color: var(--danger);
  line-height: 1;
}

/* ============================================================ */
/* 销量与库存 */
/* ============================================================ */

.stats-area {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2xl);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.highlight {
  color: var(--primary-color);
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--bg-tertiary);
}

/* ============================================================ */
/* 数量选择器 */
/* ============================================================ */

.quantity-area {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-3xl);
}

.quantity-label {
  flex-shrink: 0;
  width: 60px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.quantity-input {
  width: 160px;
}

.quantity-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-lg);
}

.stock-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}

.stock-hint em {
  font-style: normal;
  color: var(--primary-color);
  font-weight: 600;
}

/* ============================================================ */
/* 操作按钮区 */
/* ============================================================ */

.action-area {
  display: flex;
  gap: var(--space-lg);
  margin-bottom: var(--space-2xl);
}

.btn-cart,
.btn-buy {
  flex: 1;
  height: 56px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  transition: all var(--transition-base);
}

/* 加入购物车按钮 */
.btn-cart {
  background: var(--gradient-primary);
  border: none;
  color: white;
}

.btn-cart:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-primary-glow);
}

/* 立即购买按钮 */
.btn-buy {
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  border: none;
  color: white;
}

.btn-buy:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -3px rgba(239, 68, 68, 0.4);
}

/* ============================================================ */
/* 服务承诺 */
/* ============================================================ */

.service-area {
  display: flex;
  justify-content: space-around;
  padding: var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
}

.service-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-secondary);
  font-size: 12px;
}

.service-item .el-icon {
  font-size: 20px;
  color: var(--primary-color);
}

/* ============================================================ */
/* 加载骨架屏 */
/* ============================================================ */

.loading-skeleton {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4xl);
}

@media (max-width: 1024px) {
  .loading-skeleton {
    grid-template-columns: 1fr;
  }
}

.skeleton-gallery {
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.skeleton-info {
  padding: var(--space-2xl);
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
}

/* ============================================================ */
/* 响应式调整 */
/* ============================================================ */

@media (max-width: 768px) {
  .detail-main {
    padding: var(--space-lg);
  }

  .info-card {
    padding: var(--space-xl);
  }

  .goods-title {
    font-size: 22px;
  }

  .price-value {
    font-size: 32px;
  }

  .stats-area {
    flex-wrap: wrap;
    justify-content: center;
  }

  .action-area {
    flex-direction: column;
  }

  .btn-cart,
  .btn-buy {
    width: 100%;
  }

  .service-area {
    flex-wrap: wrap;
    gap: var(--space-lg);
  }

  .service-item {
    flex: 0 0 calc(50% - var(--space-md));
  }
}

@media (max-width: 480px) {
  .quantity-area {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}
</style>
