<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon :color="'var(--primary-color)'" size="24"><Shop /></el-icon>
        <span v-show="!isCollapse" class="logo-text">星辰商城后台</span>
      </div>

      <el-menu
        active-text-color="var(--primary-color)"
        background-color="var(--bg-sidebar)"
        text-color="var(--text-primary)"
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
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <!-- 使用本地 Icon 替代外部 CDN 头像，避免网络延迟 -->
              <el-avatar :size="30" class="avatar-icon">
                <el-icon :size="18"><User /></el-icon>
              </el-avatar>
              <span style="margin-left: 8px">Admin</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
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
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';
import { User, Setting, SwitchButton } from '@element-plus/icons-vue';

const isCollapse = ref(false);
const router = useRouter();

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中');
      break;
    case 'settings':
      ElMessage.info('系统设置功能开发中');
      break;
    case 'logout':
      handleLogout();
      break;
  }
};

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
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
  background-color: var(--bg-sidebar);
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  border-right: 1px solid var(--bg-tertiary);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: bold;
  background-color: var(--bg-sidebar);
  white-space: nowrap;
  padding: 0 var(--space-lg);
  border-bottom: 1px solid var(--bg-tertiary);
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
  border-radius: var(--radius-md);
  margin: var(--space-xs) var(--space-sm);
  transition: all var(--transition-fast);
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: var(--bg-sidebar-hover) !important;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--bg-sidebar-active) !important;
  color: var(--primary-color) !important;
  font-weight: 600;
  border-radius: var(--radius-md);
  margin: var(--space-xs) var(--space-sm);
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

.avatar-icon {
  background: linear-gradient(135deg, var(--primary-color), #6a8eff);
  color: white;
}

.main {
  background-color: var(--bg-secondary);
  padding: var(--space-2xl);
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