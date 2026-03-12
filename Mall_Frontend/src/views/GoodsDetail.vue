<template>
  <div class="goods-detail-layout">
    <header class="simple-header">
      <div class="inner">
        <router-link to="/" class="logo">🛍️ 星辰商城</router-link>
        <span class="divider">/</span>
        <span>商品详情</span>
      </div>
    </header>

    <div class="goods-detail-container" v-if="goodsInfo">
      <el-row :gutter="[40, 40]" class="detail-row">
        <el-col :xs="24" :md="12" class="gallery-col">
          <div class="gallery">
            <img :src="goodsInfo.goods_front_image" class="main-img" />
          </div>
        </el-col>
        <el-col :xs="24" :md="12" class="info-col">
          <div class="info-box">
            <h1 class="title">{{ goodsInfo.name }}</h1>
            <p class="desc">{{ goodsInfo.goods_brief }}</p>

            <div class="price-row">
              <span class="symbol">¥</span>
              <span class="num">{{ goodsInfo.shop_price }}</span>
              <span class="market-price">原价 ¥{{ goodsInfo.market_price }}</span>
            </div>

            <div class="meta-row">
              <span class="label">销量</span>
              <span class="value">{{ goodsInfo.sold_num }} 件</span>
              <span class="label">库存</span>
              <span class="value">{{ goodsInfo.goods_num }} 件</span>
            </div>

            <div class="sku-selector">
              <span class="label">规格</span>
              <el-radio-group v-model="selectedSku" size="large">
                <el-radio-button label="标准版" />
                <el-radio-button label="套装版" />
              </el-radio-group>
            </div>

            <div class="quantity-selector">
              <span class="label">数量</span>
              <el-input-number v-model="buyCount" :min="1" :max="goodsInfo.goods_num" />
            </div>

            <div class="actions">
              <el-button type="primary" size="large" class="buy-btn" @click="handleAddToCart">
                加入购物车
              </el-button>
              <el-button type="danger" size="large" plain @click="handleBuyNow">
                立即购买
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // 引入路由钩子
import { getGoodsDetail } from '../api/goods';
import { useCartStore } from '../store/cart';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();

const goodsInfo = ref<any>(null);
const buyCount = ref(1);
const selectedSku = ref('标准版');

// 获取详情
const loadData = async () => {
  const id = Number(route.params.id); // 从 URL 获取商品 ID
  if (!id) return;
  try {
    const res = await getGoodsDetail(id);
    goodsInfo.value = res;
  } catch (error) {
    console.error(error);
  }
};

// 加入购物车
const handleAddToCart = async () => {
  if (!goodsInfo.value) return;
  await cartStore.addToCartAction({
    goods: goodsInfo.value.id,
    nums: buyCount.value
  });
  // 成功后不跳转，留在当前页继续逛
};

// 立即购买
const handleBuyNow = async () => {
  await handleAddToCart();
  // 立即打开购物车抽屉进行结算
  cartStore.toggleDrawer(true);
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.goods-detail-layout {
  background: var(--bg-primary);
  min-height: 100vh;
}

.simple-header {
  border-bottom: 1px solid var(--bg-tertiary);
  height: 60px;
  display: flex;
  align-items: center;
  background: var(--bg-primary);
}

.simple-header .inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  display: flex;
  align-items: center;
  font-size: 18px;
  padding: 0 var(--space-xl);
  width: 100%;
}

.logo {
  font-weight: bold;
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.logo:hover {
  color: var(--primary-light);
}

.divider {
  margin: 0 var(--space-sm);
  color: var(--text-tertiary);
}

.goods-detail-container {
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: var(--space-3xl) var(--space-xl);
}

.detail-row {
  align-items: stretch;
}

.gallery-col,
.info-col {
  display: flex;
  flex-direction: column;
}

.gallery {
  width: 100%;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--bg-tertiary);
  box-shadow: var(--shadow-md);
  transition: box-shadow var(--transition-base);
}

.gallery:hover {
  box-shadow: var(--shadow-hover);
}

.main-img {
  width: 100%;
  height: auto;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  display: block;
}

.info-box {
  /* 玻璃拟态效果 */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: var(--radius-xl);
  padding: var(--space-3xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-lg),
              0 8px 32px rgba(139, 92, 246, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.6);
  height: 100%;
  position: relative;
  overflow: hidden;
}

/* 玻璃拟态背景叠加层 - 增强视觉效果 */
.info-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(59, 130, 246, 0.05));
  border-radius: var(--radius-xl);
  z-index: -1;
}

.title {
  font-size: 32px;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  line-height: 1.3;
  font-weight: 700;
}

.desc {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: var(--space-2xl);
  line-height: 1.6;
}

.price-row {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2xl);
  border: 1px solid var(--bg-hover);
}

.symbol {
  color: var(--danger);
  font-size: 18px;
  font-weight: bold;
  margin-right: var(--space-xs);
}

.num {
  color: var(--danger);
  font-size: 36px;
  font-weight: bold;
  margin-right: var(--space-md);
}

.market-price {
  color: var(--text-tertiary);
  text-decoration: line-through;
  font-size: 18px;
}

.meta-row, .sku-selector, .quantity-selector {
  margin-bottom: var(--space-2xl);
  display: flex;
  align-items: center;
}

.meta-row {
  background: var(--bg-secondary);
  padding: var(--space-lg);
  border-radius: var(--radius-md);
}

.label {
  min-width: 60px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-right: var(--space-sm);
}

.value {
  color: var(--text-primary);
  font-weight: 600;
}

.actions {
  margin-top: var(--space-3xl);
  display: flex;
  gap: var(--space-xl);
  flex-wrap: wrap;
}

.buy-btn {
  min-width: 180px;
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  background: var(--gradient-primary);
  border: none;
  color: white;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

/* 按钮发光效果 */
.buy-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--gradient-macaroon);
  opacity: 0;
  transition: opacity var(--transition-base);
  z-index: -1;
}

.buy-btn:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-primary-glow);
}

.buy-btn:hover::before {
  opacity: 1;
}

/* 立即购买按钮样式 - 使用渐变背景 */
.actions .el-button--danger {
  background: var(--gradient-candy);
  border: none;
  color: white;
  min-width: 180px;
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.actions .el-button--danger:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-primary-glow);
  color: white;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .goods-detail-container {
    padding: var(--space-lg);
  }

  .info-box {
    padding: var(--space-2xl);
  }

  .title {
    font-size: 24px;
  }

  .num {
    font-size: 30px;
  }

  .actions {
    flex-direction: column;
    gap: var(--space-md);
  }

  .buy-btn {
    width: 100%;
  }

  .simple-header .inner {
    padding: 0 var(--space-lg);
  }
}

/* 深色模式下的玻璃拟态调整 */
@media (prefers-color-scheme: dark) {
  .info-box {
    background: rgba(30, 27, 75, 0.7); /* 深紫色半透明背景 */
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: var(--shadow-lg),
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }

  .info-box::before {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
  }
}

@media (max-width: 480px) {
  .goods-detail-container {
    padding: var(--space-md);
  }

  .info-box {
    padding: var(--space-xl);
  }

  .price-row {
    padding: var(--space-lg);
  }

  .meta-row, .sku-selector, .quantity-selector {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }

  .label {
    min-width: auto;
    margin-right: 0;
    margin-bottom: var(--space-xs);
  }
}
</style>