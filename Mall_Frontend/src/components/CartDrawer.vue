<template>
  <el-drawer
    v-model="cartStore.drawerVisible"
    title="我的购物车"
    direction="rtl"
    size="400px"
  >
    <div class="cart-content">
      <div v-if="cartStore.cartList.length > 0">
        <div
          v-for="item in cartStore.cartList"
          :key="item.id"
          class="cart-item"
        >
          <img
            :src="item.goods.goods_front_image || 'https://via.placeholder.com/80'"
            class="item-img"
          />
          <div class="item-info">
            <div class="item-title">{{ item.goods.name }}</div>
            <div class="item-price">¥ {{ item.goods.shop_price }}</div>
            <div class="item-actions">
              <el-input-number
                v-model="item.nums"
                :min="1"
                size="small"
                @change="(val: number) => handleUpdate(item.id, val)"
              />
              <el-button type="danger" link size="small" @click="handleDelete(item.id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="购物车还是空的"></el-empty>
    </div>

    <template #footer>
      <div class="cart-footer">
        <div class="total">
          合计: <span class="price">¥ {{ cartStore.totalPrice }}</span>
        </div>
        <el-button
          type="primary"
          size="large"
          @click="openCheckout"
          :disabled="cartStore.cartList.length === 0"
        >去结算</el-button>
      </div>
    </template>
  </el-drawer>

  <el-dialog
    v-model="dialogVisible"
    title="填写收货信息"
    width="500px"
    append-to-body
  >
    <el-form :model="orderForm" label-width="80px">
      <el-form-item label="收货人">
        <el-input v-model="orderForm.signer_name" placeholder="请输入收货人姓名"></el-input>
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="orderForm.signer_mobile" placeholder="请输入联系电话"></el-input>
      </el-form-item>
      <el-form-item label="收货地址">
        <el-input v-model="orderForm.address" type="textarea" placeholder="请输入详细地址"></el-input>
      </el-form-item>
      <el-form-item label="留言">
        <el-input v-model="orderForm.post_script" placeholder="选填：给商家的留言"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder" :loading="loading">
          确认下单
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useCartStore } from '../store/cart';
import { createOrder } from '../api/trade';
import { ElMessageBox, ElMessage } from 'element-plus';

const cartStore = useCartStore();
const dialogVisible = ref(false);
const loading = ref(false);

// 订单表单数据
const orderForm = reactive({
  signer_name: '',
  signer_mobile: '',
  address: '',
  post_script: ''
});

// 修改数量
const handleUpdate = (id: number, nums: number) => {
  cartStore.updateCartAction(id, nums);
};

// 删除商品
const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这件商品吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    cartStore.deleteCartAction(id);
  });
};

// 打开结算弹窗
const openCheckout = () => {
  dialogVisible.value = true;
};

// 提交订单
const submitOrder = async () => {
  // 简单校验
  if (!orderForm.signer_name || !orderForm.signer_mobile || !orderForm.address) {
    ElMessage.warning('请填写完整的收货信息');
    return;
  }

  loading.value = true;
  try {
    // 1. 调用后端接口创建订单
    await createOrder(orderForm);

    // 2. 成功后提示
    ElMessage.success('下单成功！');

    // 3. 关闭弹窗和抽屉
    dialogVisible.value = false;
    cartStore.toggleDrawer(false);

    // 4. 刷新购物车（此时后端已经清空了购物车，刷新后前端也会变空）
    await cartStore.fetchCartList();

    // 5. 清空表单
    orderForm.signer_name = '';
    orderForm.signer_mobile = '';
    orderForm.address = '';
    orderForm.post_script = '';

  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.cart-content {
  height: calc(100vh - 150px);
  overflow-y: auto;
}
.cart-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 15px;
}
.item-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}
.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.item-title {
  font-size: 14px;
  color: #333;
}
.item-price {
  color: #f56c6c;
  font-weight: bold;
}
.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 5px;
}
.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.total .price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}
</style>