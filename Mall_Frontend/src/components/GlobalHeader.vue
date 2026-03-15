<template>
  <header class="global-header">
    <div class="header-container">
      <!-- ==================== 左侧 Logo 区域 ==================== -->
      <div class="header-left">
        <router-link to="/" class="logo-link">
          <span class="logo-icon">🛍️</span>
          <span class="logo-text">StartMall</span>
        </router-link>
        <router-link to="/" class="home-link">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </router-link>
      </div>

      <!-- ==================== 中间搜索框 ==================== -->
      <div class="header-center">
        <div class="search-wrapper">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索商品..."
            size="large"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
            @clear="handleClearSearch"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" class="search-btn" @click="handleSearch">
            <el-icon class="search-icon"><Search /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- ==================== 右侧用户操作区 ==================== -->
      <div class="header-right">
        <!-- 已登录状态 -->
        <template v-if="userStore.isLoggedIn">
          <!-- 购物车 -->
          <el-badge
            :value="cartStore.cartCount"
            :hidden="cartStore.cartCount === 0"
            class="cart-badge"
          >
            <el-button class="cart-btn" @click="cartStore.toggleDrawer(true)">
              <el-icon :size="20"><ShoppingCart /></el-icon>
            </el-button>
          </el-badge>

          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-dropdown-trigger">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="orders">
                  <el-icon><Document /></el-icon>
                  我的订单
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <!-- 未登录状态 -->
        <template v-else>
          <router-link to="/login">
            <el-button type="primary" plain class="auth-btn">登录</el-button>
          </router-link>
          <router-link to="/register">
            <el-button class="auth-btn">注册</el-button>
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
/**
 * GlobalHeader.vue - 全局顶部导航栏
 *
 * 职责：
 * 1. 提供全局搜索入口，搜索时跳转到首页并带上 keyword 参数
 * 2. 显示用户登录状态和购物车数量
 * 3. 提供用户下拉菜单（个人中心、订单、退出）
 */

import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  Search,
  ShoppingCart,
  HomeFilled,
  User,
  Document,
  SwitchButton,
  ArrowDown,
} from '@element-plus/icons-vue';
import { useUserStore } from '../store/user';
import { useCartStore } from '../store/cart';

// ============================================================
// Store & Router
// ============================================================

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const cartStore = useCartStore();

// ============================================================
// 响应式状态
// ============================================================

/** 搜索关键词 */
const searchKeyword = ref('');

// ============================================================
// 监听路由变化，同步搜索框内容
// ============================================================

watch(
  () => route.query.keyword,
  (newKeyword) => {
    // 当 URL 中的 keyword 变化时，同步到搜索框
    searchKeyword.value = (newKeyword as string) || '';
  },
  { immediate: true }
);

// ============================================================
// 搜索逻辑
// ============================================================

/**
 * 执行搜索
 * 跳转到首页并带上 keyword 参数
 */
const handleSearch = () => {
  const keyword = searchKeyword.value.trim();

  if (keyword) {
    // 有搜索词：跳转到首页带参数
    router.push({
      path: '/',
      query: { keyword },
    });
  } else {
    // 无搜索词：跳转到首页清空参数
    router.push('/');
  }
};

/**
 * 清空搜索
 */
const handleClearSearch = () => {
  // 如果当前在首页且有搜索参数，清空参数
  if (route.path === '/' && route.query.keyword) {
    router.push('/');
  }
};

// ============================================================
// 用户操作
// ============================================================

/**
 * 处理用户下拉菜单命令
 */
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile');
      break;
    case 'orders':
      router.push('/orders');
      break;
    case 'logout':
      handleLogout();
      break;
  }
};

/**
 * 退出登录
 */
const handleLogout = () => {
  userStore.logout();
  cartStore.clearCart();
  router.push('/login');
};
</script>

<style scoped>
/* ============================================================ */
/* 全局头部容器 */
/* ============================================================ */

.global-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

/* ============================================================ */
/* 左侧 Logo 区域 */
/* ============================================================ */

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: transform 0.2s;
}

.logo-link:hover {
  transform: scale(1.02);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.home-link {
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  color: #6b7280;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.home-link:hover {
  background: #f3f4f6;
  color: #8b5cf6;
}

/* ============================================================ */
/* 中间搜索框 */
/* ============================================================ */

.header-center {
  flex: 1;
  max-width: 600px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding-left: 16px;
  box-shadow: 0 0 0 1px #e5e7eb;
  transition: all 0.2s;
}

.search-input :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3);
}

.search-icon {
  color: #9ca3af;
}

.search-btn {
  border-radius: 24px;
  padding: 0 20px;
}

/* ============================================================ */
/* 右侧用户操作区 */
/* ============================================================ */

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.cart-badge :deep(.el-badge__content) {
  background: #f56c6c;
}

.cart-btn {
  padding: 8px;
  border-radius: 50%;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  transition: all 0.2s;
}

.cart-btn:hover {
  background: #e4e7ed;
  border-color: #dcdfe6;
}

.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.user-dropdown-trigger:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  color: white;
  font-weight: 600;
}

.username {
  font-size: 14px;
  color: #303133;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 12px;
  color: #909399;
}

.auth-btn {
  border-radius: 20px;
  padding: 8px 20px;
}

/* ============================================================ */
/* 己色模式适配 */
/* ============================================================ */

@media (prefers-color-scheme: dark) {
  .global-header {
    background: #1f2937;
    border-bottom-color: #374151;
  }

  .logo-text {
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .home-link {
    color: #e5e7eb;
  }

  .home-link:hover {
    background: #374151;
    color: #a78bfa;
  }

  .search-input :deep(.el-input__wrapper) {
    background: #374151;
    box-shadow: 0 0 0 1px #4b5563;
  }

  .username {
    color: #f3f4f6;
  }

  .user-dropdown-trigger:hover {
    background: #374151;
  }
}
</style>
