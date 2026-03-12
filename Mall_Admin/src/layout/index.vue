<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon color="#409EFF" size="24"><Shop /></el-icon>
        <span v-show="!isCollapse" class="logo-text">星辰商城后台</span>
      </div>

      <el-menu
        active-text-color="#409EFF"
        background-color="#304156"
        text-color="#bfcbd9"
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        class="el-menu-vertical"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>

        <!-- 商品管理菜单 (里面包含3个子菜单) -->
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>商品管理</span>
          </template>
          <el-menu-item index="/goods">商品列表</el-menu-item>
          <el-menu-item index="/category">分类管理</el-menu-item>
          <el-menu-item index="/banner">轮播图管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="2">
          <template #title>
            <el-icon><List /></el-icon>
            <span>订单管理</span>
          </template>
          <el-menu-item index="/orders">订单列表</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title || '控制台' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="30" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span style="margin-left: 8px">Admin</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';

const isCollapse = ref(false);
const router = useRouter();
// const route = useRoute(); // 供面包屑使用

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    // 这里清除 token
    localStorage.removeItem('token');
    ElMessage.success('已退出登录');
    router.push('/login');
  });
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: var(--primary-darker);
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: bold;
  background-color: var(--primary-dark);
  white-space: nowrap;
  padding: 0 var(--space-lg);
}

.logo-text {
  margin-left: var(--space-sm);
  font-size: 16px;
}

.el-menu-vertical {
  border-right: none;
  background-color: transparent;
}

:deep(.el-menu) {
  background-color: transparent !important;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: var(--text-primary) !important;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--primary-color) !important;
  color: white !important;
}

.header {
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--primary-color);
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-primary);
  transition: color var(--transition-fast);
}

.user-info:hover {
  color: var(--primary-color);
}

.main {
  background-color: var(--bg-secondary);
  padding: var(--space-xl);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .aside {
    width: 64px !important;
  }

  .logo-text {
    display: none;
  }

  .header {
    padding: 0 var(--space-lg);
  }
}
</style>