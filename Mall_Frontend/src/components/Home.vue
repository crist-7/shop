<template>
  <!--
    Home.vue - 星辰商城首页（顶级电商 UI 标准）

    功能特性：
    1. 吸顶导航（毛玻璃效果）
    2. 左侧分类菜单 + 右侧沉浸式轮播图
    3. 商品卡片高级动画效果
    4. CSS Grid 响应式布局
  -->
  <div class="mall-layout">
    <!-- ============================================================ -->
    <!-- 吸顶头部导航 -->
    <!-- ============================================================ -->
    <header class="mall-header" :class="{ 'is-sticky': isHeaderSticky }">
      <div class="header-inner">
        <!-- Logo 区域 -->
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">🛍️</span>
          <span class="logo-text">星辰商城</span>
        </div>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索手机、电脑、家电..."
            class="search-input"
            size="large"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #append>
              <el-button type="primary" class="search-btn" @click="handleSearch">
                <el-icon><Search /></el-icon> 搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 用户操作区 -->
        <div class="user-actions">
          <template v-if="userStore.isLoggedIn">
            <!-- 购物车徽标 -->
            <el-badge
              :value="cartStore.cartCount"
              class="cart-badge"
              :hidden="cartStore.cartCount === 0"
            >
              <el-button class="cart-btn" plain @click="cartStore.toggleDrawer(true)">
                <el-icon><ShoppingCart /></el-icon>
                <span class="cart-text">购物车</span>
              </el-button>
            </el-badge>
            <!-- 用户欢迎语 -->
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="user-greeting">{{ userStore.username }}</span>
            </div>
            <el-button link class="logout-btn" @click="handleLogout">退出</el-button>
          </template>
          <template v-else>
            <router-link to="/login">
              <el-button type="primary" plain class="login-btn">登录</el-button>
            </router-link>
            <router-link to="/register">
              <el-button class="register-btn">注册</el-button>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <!-- ============================================================ -->
    <!-- 分类导航栏 -->
    <!-- ============================================================ -->
    <nav class="category-nav" :class="{ 'is-sticky': isNavSticky }">
      <div class="nav-inner">
        <div
          class="nav-item"
          :class="{ active: activeCategoryId === null }"
          @click="handleCategoryClick(null)"
        >
          <el-icon><HomeFilled /></el-icon>
          <span>首页推荐</span>
        </div>
        <div
          v-for="item in categoryList"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeCategoryId === item.id }"
          @click="handleCategoryClick(item.id)"
        >
          {{ item.name }}
        </div>
      </div>
    </nav>

    <!-- ============================================================ -->
    <!-- 主内容区 -->
    <!-- ============================================================ -->
    <main class="main-content">
      <!-- ============================================================ -->
      <!-- 沉浸式轮播图区域：左侧分类菜单 + 右侧轮播图 -->
      <!-- ============================================================ -->
      <section class="hero-section">
        <!-- 左侧分类菜单 -->
        <aside class="category-menu">
          <div class="menu-header">
            <el-icon><Menu /></el-icon>
            <span>全部分类</span>
          </div>
          <div class="menu-list">
            <div
              v-for="item in categoryList"
              :key="item.id"
              class="menu-item"
              @click="handleCategoryClick(item.id)"
            >
              <span class="menu-item-text">{{ item.name }}</span>
              <el-icon class="menu-item-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </aside>

        <!-- 右侧轮播图 -->
        <div class="banner-wrapper">
          <el-carousel
            v-if="bannerList.length > 0"
            height="420px"
            :interval="5000"
            indicator-position="outside"
            arrow="hover"
            class="banner-carousel"
          >
            <el-carousel-item v-for="item in bannerList" :key="item.id">
              <div class="banner-content" @click="router.push(`/goods/${item.goods}`)">
                <img v-lazy="item.image" class="banner-image" />
                <div class="banner-overlay">
                  <div class="banner-tag">热门推荐</div>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>

          <!-- 无轮播图时的占位 -->
          <div v-else class="banner-placeholder">
            <div class="placeholder-content">
              <el-icon :size="80"><Picture /></el-icon>
              <h3>星辰商城 · 品质生活</h3>
              <p>暂无轮播图，请去后台添加</p>
            </div>
          </div>
        </div>

        <!-- 右侧快捷入口 -->
        <aside class="quick-entry">
          <div class="entry-item" @click="router.push('/orders')">
            <el-icon :size="28"><Document /></el-icon>
            <span>我的订单</span>
          </div>
          <div class="entry-item" @click="cartStore.toggleDrawer(true)">
            <el-icon :size="28"><ShoppingCart /></el-icon>
            <span>购物车</span>
          </div>
        </aside>
      </section>

      <!-- ============================================================ -->
      <!-- 热卖推荐商品区域 -->
      <!-- ============================================================ -->
      <section class="goods-section">
        <div class="section-header">
          <div class="section-title-wrapper">
            <span class="section-icon">✨</span>
            <h2 class="section-title">热卖推荐</h2>
            <span class="section-subtitle">精选好物，品质保障</span>
          </div>
          <el-button
            v-if="activeCategoryId !== null || searchKeyword"
            text
            type="primary"
            @click="resetFilters"
          >
            <el-icon><RefreshRight /></el-icon>
            清除筛选
          </el-button>
        </div>

        <!-- 商品网格列表 -->
        <div class="goods-grid">
          <!-- 加载骨架屏 -->
          <template v-if="loading">
            <div v-for="i in 8" :key="i" class="goods-card-skeleton">
              <div class="skeleton-image"></div>
              <div class="skeleton-content">
                <div class="skeleton-title"></div>
                <div class="skeleton-price"></div>
              </div>
            </div>
          </template>

          <!-- 商品卡片 -->
          <article
            v-for="item in goodsList"
            :key="item.id"
            class="goods-card"
            @click="router.push(`/goods/${item.id}`)"
          >
            <!-- 商品图片容器 -->
            <div class="goods-image-wrapper">
              <img
                v-if="item.goods_front_image"
                v-lazy="item.goods_front_image"
                class="goods-image"
              />
              <div v-else class="goods-image-placeholder">
                <el-icon :size="48"><Picture /></el-icon>
                <span>暂无图片</span>
              </div>

              <!-- 悬浮购物车按钮 -->
              <div class="cart-action" @click.stop="addToCart(item)">
                <el-icon :size="20"><ShoppingCart /></el-icon>
              </div>

              <!-- 热卖标签 -->
              <div class="hot-tag">HOT</div>
            </div>

            <!-- 商品信息 -->
            <div class="goods-info">
              <h3 class="goods-name">{{ item.name }}</h3>
              <p class="goods-desc" v-if="item.goods_desc">{{ item.goods_desc }}</p>

              <div class="goods-footer">
                <div class="price-wrapper">
                  <span class="price-symbol">¥</span>
                  <span class="price-value">{{ item.shop_price.toFixed(2) }}</span>
                </div>
                <span class="sales-count">已售 {{ Math.floor(Math.random() * 1000) }}+</span>
              </div>
            </div>
          </article>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && goodsList.length === 0" class="empty-state">
          <el-empty description="暂无相关商品">
            <el-button type="primary" @click="resetFilters">查看全部商品</el-button>
          </el-empty>
        </div>
      </section>
    </main>

    <!-- 购物车抽屉 -->
    <CartDrawer />

    <!-- 回到顶部按钮 -->
    <el-backtop :bottom="100" :right="40">
      <div class="backtop-btn">
        <el-icon :size="20"><Top /></el-icon>
      </div>
    </el-backtop>
  </div>
</template>

<script setup lang="ts">
/**
 * Home.vue - 星辰商城首页
 *
 * 技术栈：Vue 3 + TypeScript + Element Plus
 * 特性：Composables 逻辑抽离、响应式布局、高级动画
 */

import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  Search,
  ShoppingCart,
  HomeFilled,
  Menu,
  ArrowRight,
  Picture,
  Document,
  RefreshRight,
  Top,
} from '@element-plus/icons-vue';
import { useUserStore } from '../store/user';
import { useCartStore } from '../store/cart';
import { useHomeData, type GoodsItem } from '../hooks/useHomeData';
import CartDrawer from './CartDrawer.vue';

// ============================================================
// 路由和 Store
// ============================================================

const router = useRouter();
const userStore = useUserStore();
const cartStore = useCartStore();

// ============================================================
// 使用 Composable 抽离的数据逻辑
// ============================================================

const {
  loading,
  categoryList,
  bannerList,
  goodsList,
  searchKeyword,
  activeCategoryId,
  fetchAllData,
  fetchGoods,
  handleSearch,
  handleCategoryClick,
  resetFilters,
} = useHomeData();

// ============================================================
// 吸顶导航状态
// ============================================================

/** 头部是否吸顶 */
const isHeaderSticky = ref(false);

/** 导航栏是否吸顶 */
const isNavSticky = ref(false);

/**
 * 滚动监听 - 控制吸顶效果
 */
const handleScroll = () => {
  const scrollY = window.scrollY;
  // 滚动超过 80px 时头部吸顶
  isHeaderSticky.value = scrollY > 80;
  // 滚动超过 160px 时导航栏吸顶
  isNavSticky.value = scrollY > 160;
};

// ============================================================
// 用户交互方法
// ============================================================

/**
 * 退出登录
 */
const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

/**
 * 添加商品到购物车
 */
const addToCart = async (item: GoodsItem) => {
  if (!userStore.isLoggedIn) {
    router.push('/login');
    return;
  }
  await cartStore.addToCartAction({ goods: item.id, nums: 1 });
};

// ============================================================
// 生命周期
// ============================================================

onMounted(() => {
  // 加载首页数据
  fetchAllData();

  // 如果已登录，获取购物车数据
  if (userStore.isLoggedIn) {
    cartStore.fetchCartList();
  }

  // 添加滚动监听
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  // 移除滚动监听
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* ============================================================ */
/* 全局布局 */
/* ============================================================ */

.mall-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
}

/* ============================================================ */
/* 吸顶头部导航 */
/* ============================================================ */

.mall-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-primary);
  border-bottom: 2px solid var(--primary-color);
  padding: 0 var(--space-xl);
  transition: all var(--transition-base);
}

/* 吸顶状态 - 毛玻璃效果 */
.mall-header.is-sticky {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: var(--shadow-lg);
}

.header-inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xl);
}

/* Logo 样式 */
.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 24px;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 搜索栏 */
.search-bar {
  flex: 1;
  max-width: 560px;
}

.search-input {
  border-radius: var(--radius-full) !important;
  overflow: hidden;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-full) 0 0 var(--radius-full) !important;
  padding-left: 20px;
  box-shadow: 0 2px 12px rgba(139, 92, 246, 0.1);
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

.search-input :deep(.el-input__wrapper:focus-within) {
  border-color: var(--primary-color);
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

.search-btn {
  border-radius: 0 var(--radius-full) var(--radius-full) 0 !important;
  padding: 0 24px;
}

/* 用户操作区 */
.user-actions {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.cart-badge :deep(.el-badge__content) {
  background: var(--danger);
}

.cart-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  border-radius: var(--radius-full) !important;
}

.cart-text {
  display: none;
}

@media (min-width: 768px) {
  .cart-text {
    display: inline;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.user-avatar {
  background: var(--gradient-primary);
  color: white;
  font-weight: 600;
}

.user-greeting {
  font-weight: 500;
  color: var(--text-primary);
}

.login-btn,
.register-btn {
  border-radius: var(--radius-full) !important;
  padding: 8px 24px;
}

/* ============================================================ */
/* 分类导航栏 */
/* ============================================================ */

.category-nav {
  position: sticky;
  top: 80px;
  z-index: 99;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--bg-tertiary);
  transition: all var(--transition-base);
}

.category-nav.is-sticky {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: var(--shadow-sm);
}

.nav-inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  display: flex;
  gap: var(--space-xs);
  padding: 0 var(--space-xl);
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-inner::-webkit-scrollbar {
  display: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-md) var(--space-lg);
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  color: var(--primary-color);
  background: var(--bg-tertiary);
}

.nav-item.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  background: linear-gradient(180deg, var(--bg-tertiary) 0%, transparent 100%);
}

/* ============================================================ */
/* 主内容区 */
/* ============================================================ */

.main-content {
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
}

/* ============================================================ */
/* 沉浸式轮播图区域 */
/* ============================================================ */

.hero-section {
  display: grid;
  grid-template-columns: 220px 1fr 180px;
  gap: var(--space-md);
  margin-bottom: var(--space-4xl);
  height: 420px;
}

@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 200px 1fr;
  }

  .quick-entry {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
    height: auto;
  }

  .category-menu {
    display: none;
  }
}

/* 左侧分类菜单 */
.category-menu {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.menu-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
  font-weight: 600;
  color: white;
  background: var(--gradient-primary);
}

.menu-list {
  max-height: 360px;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: var(--bg-tertiary);
  border-left-color: var(--primary-color);
}

.menu-item:hover .menu-item-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.menu-item-text {
  font-size: 14px;
  color: var(--text-secondary);
}

.menu-item:hover .menu-item-text {
  color: var(--primary-color);
}

.menu-item-arrow {
  opacity: 0;
  font-size: 12px;
  color: var(--primary-color);
  transition: all var(--transition-fast);
}

/* 轮播图容器 */
.banner-wrapper {
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.banner-carousel :deep(.el-carousel__indicators) {
  padding: 12px 0;
}

.banner-carousel :deep(.el-carousel__indicator--horizontal .el-carousel__button) {
  width: 24px;
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--text-tertiary);
  transition: all var(--transition-fast);
}

.banner-carousel :deep(.el-carousel__indicator--horizontal.is-active .el-carousel__button) {
  width: 36px;
  background: var(--primary-color);
}

.banner-content {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.banner-content:hover .banner-image {
  transform: scale(1.03);
}

.banner-overlay {
  position: absolute;
  top: var(--space-lg);
  left: var(--space-lg);
}

.banner-tag {
  padding: var(--space-xs) var(--space-md);
  font-size: 12px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, var(--danger) 0%, var(--warning) 100%);
  border-radius: var(--radius-full);
}

.banner-placeholder {
  width: 100%;
  height: 100%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  color: white;
}

.placeholder-content h3 {
  margin-top: var(--space-lg);
  font-size: 24px;
}

.placeholder-content p {
  opacity: 0.8;
  margin-top: var(--space-sm);
}

/* 右侧快捷入口 */
.quick-entry {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.entry-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.entry-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  color: var(--primary-color);
}

.entry-item span {
  font-size: 13px;
  font-weight: 500;
}

.entry-highlight {
  background: var(--gradient-sunset);
  color: white;
}

.entry-highlight:hover {
  color: white;
  transform: translateY(-4px) scale(1.02);
}

/* ============================================================ */
/* 商品区域 */
/* ============================================================ */

.goods-section {
  margin-bottom: var(--space-5xl);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2xl);
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.section-icon {
  font-size: 28px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.section-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
  padding-left: var(--space-md);
  border-left: 2px solid var(--bg-tertiary);
}

/* ============================================================ */
/* 商品网格布局 */
/* ============================================================ */

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-xl);
}

/* ============================================================ */
/* 商品卡片 */
/* ============================================================ */

.goods-card {
  position: relative;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

/* 卡片悬浮效果 - 上浮 + 阴影 */
.goods-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-multi-glow);
}

/* 商品图片容器 */
.goods-image-wrapper {
  position: relative;
  width: 100%;
  height: 260px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.goods-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: var(--space-lg);
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 图片悬浮放大效果 */
.goods-card:hover .goods-image {
  transform: scale(1.08);
}

.goods-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  color: var(--text-tertiary);
}

/* 悬浮购物车按钮 */
.cart-action {
  position: absolute;
  bottom: var(--space-md);
  right: var(--space-md);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  opacity: 0;
  transform: translateY(20px) scale(0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.goods-card:hover .cart-action {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.cart-action:hover {
  transform: translateY(0) scale(1.1);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
}

/* 热卖标签 */
.hot-tag {
  position: absolute;
  top: var(--space-md);
  left: var(--space-md);
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  border-radius: var(--radius-sm);
  letter-spacing: 0.5px;
}

/* 商品信息 */
.goods-info {
  padding: var(--space-lg);
}

.goods-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0 0 var(--space-sm) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color var(--transition-fast);
}

.goods-card:hover .goods-name {
  color: var(--primary-color);
}

.goods-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0 0 var(--space-md) 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goods-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.price-wrapper {
  display: flex;
  align-items: baseline;
}

.price-symbol {
  font-size: 16px;
  font-weight: 600;
  color: var(--danger);
}

.price-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--danger);
  line-height: 1;
}

.sales-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ============================================================ */
/* 骨架屏样式 */
/* ============================================================ */

.goods-card-skeleton {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-image {
  height: 260px;
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-hover) 50%, var(--bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

.skeleton-content {
  padding: var(--space-lg);
}

.skeleton-title {
  height: 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-md);
}

.skeleton-price {
  height: 28px;
  width: 80px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ============================================================ */
/* 空状态 */
/* ============================================================ */

.empty-state {
  padding: var(--space-5xl) 0;
}

/* ============================================================ */
/* 回到顶部按钮 */
/* ============================================================ */

.backtop-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  box-shadow: var(--shadow-primary-glow);
  transition: all var(--transition-fast);
}

.backtop-btn:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-multi-glow);
}

/* ============================================================ */
/* 响应式调整 */
/* ============================================================ */

@media (max-width: 640px) {
  .header-inner {
    height: 64px;
    padding: 0 var(--space-md);
  }

  .logo-text {
    display: none;
  }

  .search-bar {
    max-width: 100%;
  }

  .goods-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }

  .goods-image-wrapper {
    height: 180px;
  }

  .price-value {
    font-size: 18px;
  }

  .section-title {
    font-size: 22px;
  }
}
</style>
