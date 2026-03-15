<template>
  <div class="app-layout">
    <!-- 全局头部导航 -->
    <GlobalHeader v-if="showHeader" />

    <!-- 主内容区域 -->
    <main class="main-content" :class="{ 'with-header': showHeader }">
      <router-view></router-view>
    </main>

    <!-- 购物车抽屉 -->
    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import GlobalHeader from './components/GlobalHeader.vue';
import CartDrawer from './components/CartDrawer.vue';
import { useCartStore } from './store/cart';

const route = useRoute();
const cartStore = useCartStore();

/**
 * 是否显示全局头部
 * 登录、注册页面不显示
 */
const showHeader = computed(() => {
  const hiddenRoutes = ['/login', '/register'];
  return !hiddenRoutes.includes(route.path);
});

onMounted(() => {
  cartStore.initCart();
});
</script>

<style>
/* 确保全屏高度，防止页面塌陷 */
#app {
  width: 100%;
  min-height: 100vh;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 64px; /* 为固定的头部留出空间 */
}

.main-content.with-header {
  padding-top: 64px;
}
</style>