<template>
  <!--
    GoodsDetail.vue - 星辰商城商品详情页

    功能特性：
    1. 左侧图片画廊（主图 + 缩略图 hover 切换）
    2. 右侧商品信息（名称、价格、描述）
    3. SKU 选择器（前端模拟颜色/版本）
    4. 数量选择器 + 购物车操作
    5. 玻璃拟态卡片效果
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
            <!-- 商品标题与标签 -->
            <div class="title-area">
              <h1 class="goods-title">{{ goodsInfo.name }}</h1>
              <div class="goods-tags">
                <el-tag type="danger" size="small" effect="dark" class="tag-item">
                  <el-icon><TrendCharts /></el-icon>
                  热卖
                </el-tag>
                <el-tag type="warning" size="small" effect="dark" class="tag-item">
                  <el-icon><Present /></el-icon>
                  限时优惠
                </el-tag>
              </div>
            </div>

            <!-- 商品简介 -->
            <p class="goods-brief">{{ goodsInfo.goods_brief || '精选好物，品质保证，让您购物无忧。' }}</p>

            <!-- 价格展示区 -->
            <div class="price-area">
              <div class="price-main">
                <span class="price-symbol">¥</span>
                <span class="price-integer">{{ priceParts.integer }}</span>
                <span class="price-decimal">.{{ priceParts.decimal }}</span>
              </div>
              <div class="price-original" v-if="goodsInfo.original_price">
                <span>原价</span>
                <span class="original-value">¥{{ (goodsInfo.original_price / 100).toFixed(2) }}</span>
              </div>
              <div class="price-discount" v-if="discountPercent > 0">
                <span class="discount-tag">{{ discountPercent }}% OFF</span>
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

            <!-- ==================== SKU 选择器（前端模拟） ==================== -->
            <div class="sku-area">
              <!-- 颜色选择 -->
              <div class="sku-row">
                <span class="sku-label">颜色</span>
                <div class="sku-options">
                  <div
                    v-for="color in mockSkuOptions.colors"
                    :key="color.value"
                    class="sku-option color-option"
                    :class="{ active: selectedColor === color.value, disabled: color.disabled }"
                    @click="!color.disabled && (selectedColor = color.value)"
                  >
                    <span
                      class="color-dot"
                      :style="{ backgroundColor: color.color }"
                    ></span>
                    <span class="option-name">{{ color.label }}</span>
                  </div>
                </div>
              </div>

              <!-- 版本选择 -->
              <div class="sku-row">
                <span class="sku-label">版本</span>
                <div class="sku-options">
                  <div
                    v-for="version in mockSkuOptions.versions"
                    :key="version.value"
                    class="sku-option version-option"
                    :class="{ active: selectedVersion === version.value, disabled: version.disabled }"
                    @click="!version.disabled && (selectedVersion = version.value)"
                  >
                    <span class="option-name">{{ version.label }}</span>
                    <span class="option-price" v-if="version.priceDiff">
                      {{ version.priceDiff > 0 ? '+' : '' }}¥{{ Math.abs(version.priceDiff) }}
                    </span>
                  </div>
                </div>
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
 * 2. SKU 选择器（前端模拟）
 * 3. 数量选择器
 * 4. 加入购物车 / 立即购买
 */

import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  ArrowRight,
  ShoppingCart,
  ZoomIn,
  TrendCharts,
  Present,
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
// SKU 选择状态（前端模拟）
// ============================================================

/** 选中的颜色 */
const selectedColor = ref('black');

/** 选中的版本 */
const selectedVersion = ref('128g');

/** 模拟的 SKU 选项数据 */
const mockSkuOptions = {
  colors: [
    { label: '星空黑', value: 'black', color: '#1a1a2e', disabled: false },
    { label: '远峰蓝', value: 'blue', color: '#4a90d9', disabled: false },
    { label: '月光银', value: 'silver', color: '#c0c0c0', disabled: false },
    { label: '玫瑰金', value: 'gold', color: '#e8b4b8', disabled: true }, // 缺货
  ],
  versions: [
    { label: '128GB', value: '128g', priceDiff: 0, disabled: false },
    { label: '256GB', value: '256g', priceDiff: 300, disabled: false },
    { label: '512GB', value: '512g', priceDiff: 800, disabled: false },
    { label: '1TB', value: '1t', priceDiff: 1500, disabled: true }, // 缺货
  ],
};

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

/**
 * 价格拆分（整数部分和小数部分）
 */
const priceParts = computed(() => {
  if (!goodsInfo.value) return { integer: '0', decimal: '00' };
  const price = goodsInfo.value.shop_price / 100; // 假设价格以分为单位
  const [integer, decimal = '00'] = price.toFixed(2).split('.');
  return { integer, decimal };
});

/**
 * 折扣百分比
 */
const discountPercent = computed(() => {
  if (!goodsInfo.value?.original_price || !goodsInfo.value?.shop_price) return 0;
  const original = goodsInfo.value.original_price;
  const current = goodsInfo.value.shop_price;
  if (original <= current) return 0;
  return Math.round((1 - current / original) * 100);
});

/**
 * 计算最终价格（考虑 SKU 差价）
 */
const finalPrice = computed(() => {
  if (!goodsInfo.value) return 0;
  let price = goodsInfo.value.shop_price;
  const version = mockSkuOptions.versions.find(v => v.value === selectedVersion.value);
  if (version?.priceDiff) {
    price += version.priceDiff * 100; // 差价以分为单位
  }
  return price;
});

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
  margin-bottom: var(--space-md);
}

.goods-tags {
  display: flex;
  gap: var(--space-sm);
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 4px;
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

.price-integer {
  font-size: 42px;
  font-weight: 700;
  color: var(--danger);
  line-height: 1;
}

.price-decimal {
  font-size: 18px;
  font-weight: 600;
  color: var(--danger);
}

.price-original {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.price-original span:first-child {
  font-size: 12px;
  color: var(--text-tertiary);
}

.original-value {
  font-size: 16px;
  color: var(--text-tertiary);
  text-decoration: line-through;
}

.discount-tag {
  display: inline-flex;
  padding: 4px 12px;
  background: var(--danger);
  color: white;
  font-size: 12px;
  font-weight: 700;
  border-radius: var(--radius-full);
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
/* SKU 选择器 */
/* ============================================================ */

.sku-area {
  margin-bottom: var(--space-2xl);
}

.sku-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: var(--space-xl);
}

.sku-row:last-child {
  margin-bottom: 0;
}

.sku-label {
  flex-shrink: 0;
  width: 60px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  padding-top: 10px;
}

.sku-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.sku-option {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-lg);
  border: 2px solid var(--bg-tertiary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--bg-primary);
}

.sku-option:hover:not(.disabled) {
  border-color: var(--primary-light);
  background: rgba(139, 92, 246, 0.05);
}

.sku-option.active {
  border-color: var(--primary-color);
  background: rgba(139, 92, 246, 0.1);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.sku-option.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  position: relative;
}

.sku-option.disabled::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--text-tertiary);
  transform: rotate(-10deg);
}

/* 颜色选项 */
.color-option .color-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.1);
}

.option-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.option-price {
  font-size: 12px;
  color: var(--danger);
  margin-left: var(--space-xs);
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

  .price-integer {
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
  .sku-row {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .sku-label {
    width: auto;
    padding-top: 0;
  }

  .quantity-area {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}
</style>
