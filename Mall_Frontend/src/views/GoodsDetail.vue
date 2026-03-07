<template>
  <div class="goods-detail-layout">
    <header class="simple-header">
      <div class="inner">
        <router-link to="/" class="logo">🛍️ 星辰商城</router-link>
        <span class="divider">/</span>
        <span>商品详情</span>
      </div>
    </header>

    <div class="detail-container" v-if="goodsInfo">
      <div class="gallery">
        <img :src="goodsInfo.goods_front_image" class="main-img" />
      </div>

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
          <span class="label" style="margin-left: 20px;">库存</span>
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
.goods-detail-layout { background: #fff; min-height: 100vh; }
.simple-header { border-bottom: 1px solid #eee; height: 60px; display: flex; align-items: center; }
.simple-header .inner { width: 1200px; margin: 0 auto; display: flex; align-items: center; font-size: 18px; }
.logo { font-weight: bold; color: #409EFF; text-decoration: none; }
.divider { margin: 0 10px; color: #ccc; }

.detail-container { width: 1200px; margin: 40px auto; display: flex; gap: 50px; }

.gallery { width: 500px; }
.main-img { width: 100%; border-radius: 8px; border: 1px solid #f0f0f0; }

.info-box { flex: 1; }
.title { font-size: 28px; color: #333; margin-bottom: 10px; }
.desc { color: #999; font-size: 14px; margin-bottom: 20px; }

.price-row { background: #fdf5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
.symbol { color: #e1251b; font-size: 16px; font-weight: bold; }
.num { color: #e1251b; font-size: 32px; font-weight: bold; }
.market-price { color: #999; text-decoration: line-through; margin-left: 15px; }

.meta-row, .sku-selector, .quantity-selector { margin-bottom: 25px; display: flex; align-items: center; }
.label { width: 60px; color: #666; }
.value { color: #333; }

.actions { margin-top: 40px; display: flex; gap: 20px; }
.buy-btn { width: 180px; height: 50px; font-size: 18px; }
</style>