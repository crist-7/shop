<template>
  <div class="order-list-layout">
    <header class="simple-header">
      <div class="inner">
        <router-link to="/" class="logo">🛍️ 星辰商城</router-link>
        <span class="divider">/</span>
        <span>我的订单</span>
      </div>
    </header>

    <div class="main-container">
      <el-card class="order-card" v-for="order in orderList" :key="order.id">
        <template #header>
          <div class="card-header">
            <span class="order-sn">订单号：{{ order.order_sn }}</span>
            <span class="order-time">{{ formatDate(order.add_time) }}</span>
            <el-tag :type="order.pay_status === 'TRADE_SUCCESS' ? 'success' : 'warning'">
              {{ order.pay_status === 'TRADE_SUCCESS' ? '已支付' : '待支付' }}
            </el-tag>
          </div>
        </template>

        <div class="order-goods" v-for="item in order.goods" :key="item.id">
          <img :src="item.goods.goods_front_image" class="goods-img" />
          <div class="goods-info">
            <div class="name">{{ item.goods.name }}</div>
            <div class="price">¥ {{ item.goods.shop_price }} x {{ item.goods_num }}</div>
          </div>
        </div>

        <div class="card-footer">
          <div class="total">
            实付金额：<span class="money">¥ {{ order.order_mount }}</span>
          </div>
          <div class="btns" v-if="order.pay_status !== 'TRADE_SUCCESS'">
             <el-button type="primary" size="small" @click="handlePay(order)">去支付</el-button>
          </div>
        </div>
      </el-card>

      <el-empty v-if="orderList.length === 0" description="您还没有下过单哦"></el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getOrders } from '../api/trade';
import { ElMessage } from 'element-plus';

const orderList = ref<any[]>([]);

const fetchOrders = async () => {
  try {
    const res: any = await getOrders();
    // 后端返回的可能是分页格式 { count:.., results: [..] } 或直接数组
    // 根据之前的逻辑，如果没关分页，数据在 results 里
    orderList.value = res.results ? res.results : res;
  } catch (error) {
    console.error(error);
  }
};

// 简单的日期格式化
const formatDate = (isoString: string) => {
  return new Date(isoString).toLocaleString();
};

// 模拟支付功能（毕设常用技巧）
const handlePay = (order: any) => {
  // 真实支付需要跳转支付宝，这里我们直接弹窗提示演示
  ElMessage.success(`正在前往支付宝支付订单 ${order.order_sn}...`);
  // 在真实项目中，这里会调用后端接口获取支付宝 URL
};

onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
.order-list-layout { background: #f5f7fa; min-height: 100vh; }
.simple-header { background: #fff; height: 60px; border-bottom: 1px solid #eee; display: flex; align-items: center; margin-bottom: 20px;}
.simple-header .inner { width: 1200px; margin: 0 auto; font-size: 18px; }
.logo { text-decoration: none; color: #409EFF; font-weight: bold; }
.divider { margin: 0 10px; color: #ccc; }

.main-container { width: 1200px; margin: 0 auto; padding-bottom: 50px; }

.order-card { margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #666; }
.order-sn { font-weight: bold; color: #333; }

.order-goods { display: flex; gap: 15px; padding: 15px 0; border-bottom: 1px solid #f9f9f9; }
.goods-img { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
.goods-info { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.name { font-size: 14px; }
.price { font-size: 13px; color: #999; }

.card-footer { padding-top: 15px; display: flex; justify-content: flex-end; align-items: center; gap: 20px; }
.total { font-size: 14px; }
.money { font-size: 18px; color: #e1251b; font-weight: bold; }
</style>