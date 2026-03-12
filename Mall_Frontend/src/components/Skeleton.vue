<template>
  <div class="skeleton" :class="type" :style="{ width, height }">
    <div class="skeleton-image" v-if="showImage"></div>
    <div
      class="skeleton-line"
      v-for="i in lines"
      :key="i"
      :style="{ width: i === lines && lastLineWidth ? lastLineWidth : '100%' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type?: 'text' | 'card' | 'product'
  showImage?: boolean
  lines?: number
  width?: string
  height?: string
  lastLineWidth?: string
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  showImage: false,
  lines: 3,
  width: '100%',
  height: 'auto',
  lastLineWidth: '60%'
})
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-secondary) 25%,
    var(--bg-hover) 50%,
    var(--bg-secondary) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.skeleton.card {
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
}

.skeleton.product {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 25%,
    var(--bg-hover) 50%,
    var(--bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 25%,
    var(--bg-hover) 50%,
    var(--bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-sm);
}

.skeleton-line:last-child {
  margin-bottom: 0;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>