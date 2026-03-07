<template>
  <div class="orders-container">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>全部订单列表</span>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="order_sn" label="订单号" min-width="180" />
        <el-table-column prop="signer_name" label="收货人" width="120" />
        <el-table-column prop="signer_mobile" label="联系电话" width="150" />
        <el-table-column prop="order_mount" label="订单金额" width="120">
          <template #default="scope">
            <span style="color: #e1251b; font-weight: bold;">¥ {{ scope.row.order_mount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pay_status" label="支付状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.pay_status === 'TRADE_SUCCESS' ? 'success' : 'warning'">
              {{ scope.row.pay_status === 'TRADE_SUCCESS' ? '已支付' : '待支付' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="收货地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="下单时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.add_time).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getOrderList } from '../../api/orders';

const loading = ref(false);
const tableData = ref<any[]>([]);

const fetchOrders = async () => {
  loading.value = true;
  try {
    const res: any = await getOrderList();
    // 兼容分页和不分页的数据结构
    tableData.value = res.results ? res.results : res;
  } catch (error) {
    console.error('获取订单失败', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
.orders-container { padding: 20px; }
.card-header { font-weight: bold; }
</style>