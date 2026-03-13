<template>
  <router-view></router-view>

  <CartDrawer />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import CartDrawer from './components/CartDrawer.vue';
import { useCartStore } from './store/cart';

const cartStore = useCartStore();

onMounted(() => {
  // 初始化购物车状态（如果用户已登录）
  cartStore.initCart();
});
</script>

<style>
/* 确保全屏高度，防止页面塌陷 */
#app {
  width: 100%;
  min-height: 100vh;
}
</style>