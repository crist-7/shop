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
             <el-button type="warning" size="small" @click="showAddressDialog(order)">修改地址</el-button>
             <el-button type="danger" size="small" @click="handleCancel(order)">取消订单</el-button>
          </div>
        </div>
      </el-card>

      <el-empty v-if="orderList.length === 0" description="您还没有下过单哦"></el-empty>
    </div>

    <!-- 地址修改对话框 -->
    <el-dialog v-model="addressDialogVisible" title="修改收货地址" width="500px">
      <el-form :model="addressForm" label-width="80px">
        <el-form-item label="收货人">
          <el-input v-model="addressForm.signer_name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="addressForm.signer_mobile" placeholder="请输入11位手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="addressForm.address" type="textarea" placeholder="请输入详细收货地址" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addressDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateAddress">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getOrders, payOrder, updateOrderAddress, cancelOrder } from '../api/trade';
import { ElMessage, ElMessageBox } from 'element-plus';

const orderList = ref<any[]>([]);
const addressDialogVisible = ref(false);
const currentOrderId = ref<number | null>(null);
const addressForm = ref({
  signer_name: '',
  signer_mobile: '',
  address: ''
});

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

// 支付订单
const handlePay = async (order: any) => {
  try {
    await ElMessageBox.confirm(
      `确认支付订单 ${order.order_sn}，金额 ¥${order.order_mount}？`,
      '确认支付',
      { type: 'warning' }
    );

    const res = await payOrder(order.id);
    ElMessage.success(res.message || '支付成功');
    fetchOrders(); // 刷新订单列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '支付失败');
    }
  }
};

// 显示地址修改对话框
const showAddressDialog = (order: any) => {
  currentOrderId.value = order.id;
  addressForm.value = {
    signer_name: order.signer_name || '',
    signer_mobile: order.signer_mobile || '',
    address: order.address || ''
  };
  addressDialogVisible.value = true;
};

// 更新地址
const updateAddress = async () => {
  try {
    if (!currentOrderId.value) return;

    // 过滤空值字段
    const data: any = {};
    if (addressForm.value.signer_name.trim()) data.signer_name = addressForm.value.signer_name;
    if (addressForm.value.signer_mobile.trim()) data.signer_mobile = addressForm.value.signer_mobile;
    if (addressForm.value.address.trim()) data.address = addressForm.value.address;

    if (Object.keys(data).length === 0) {
      ElMessage.warning('请至少修改一个地址字段');
      return;
    }

    const res = await updateOrderAddress(currentOrderId.value, data);
    ElMessage.success(res.message || '地址修改成功');
    addressDialogVisible.value = false;
    fetchOrders(); // 刷新订单列表
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '地址修改失败');
  }
};

// 取消订单
const handleCancel = async (order: any) => {
  try {
    await ElMessageBox.confirm(
      `确认取消订单 ${order.order_sn}？`,
      '确认取消',
      { type: 'warning' }
    );

    const res = await cancelOrder(order.id);
    ElMessage.success(res.message || '订单已取消');
    fetchOrders(); // 刷新订单列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '取消失败');
    }
  }
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