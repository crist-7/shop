<template>
  <router-view></router-view>

  <CartDrawer />
</template>

<script setup lang="ts">
import CartDrawer from './components/CartDrawer.vue';
</script>

<style>
/* 确保全屏高度，防止页面塌陷 */
#app {
  width: 100%;
  min-height: 100vh;
}
</style>