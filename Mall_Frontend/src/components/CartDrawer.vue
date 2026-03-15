<template>
  <el-drawer
    v-model="cartStore.drawerVisible"
    title="我的购物车"
    direction="rtl"
    size="420px"
  >
    <div class="cart-content">
      <!-- 购物车有商品 -->
      <div v-if="cartStore.cartList.length > 0">
        <!-- 全选栏 -->
        <div class="select-all-bar">
          <el-checkbox
            :model-value="cartStore.isAllSelected"
            :indeterminate="cartStore.selectedCount > 0 && cartStore.selectedCount < cartStore.cartList.length"
            @change="cartStore.toggleSelectAll"
          >
            全选
          </el-checkbox>
          <span class="selected-count">已选 {{ cartStore.selectedCount }} 件</span>
        </div>

        <!-- 商品列表 -->
        <div
          v-for="item in cartStore.cartList"
          :key="item.id"
          class="cart-item"
          :class="{ 'is-selected': cartStore.selectedIds.includes(item.id) }"
        >
          <!-- 选择框 -->
          <el-checkbox
            :model-value="cartStore.selectedIds.includes(item.id)"
            @change="cartStore.toggleSelect(item.id)"
            class="item-checkbox"
          />

          <!-- 商品图片 -->
          <div class="item-img-wrapper">
            <img
              v-if="item.goods.goods_front_image"
              :src="item.goods.goods_front_image"
              class="item-img"
            />
            <div v-else class="item-img-placeholder">
              <el-icon :size="32"><Picture /></el-icon>
            </div>
          </div>

          <!-- 商品信息 -->
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

      <!-- 空购物车 -->
      <div v-else class="empty-cart">
        <el-empty description="购物车空空如也">
          <template #image>
            <el-icon :size="80" color="#c0c4cc"><ShoppingCart /></el-icon>
          </template>
          <p style="color: #999; margin-top: 8px;">快去挑选心仪的商品吧~</p>
          <el-button type="primary" size="small" @click="cartStore.toggleDrawer(false)" style="margin-top: 16px;">
            去逛逛
          </el-button>
        </el-empty>
      </div>
    </div>

    <template #footer>
      <div class="cart-footer">
        <div class="total">
          合计: <span class="price">¥ {{ cartStore.selectedTotalPrice }}</span>
        </div>
        <el-button
          type="primary"
          size="large"
          @click="handleCheckout"
          :disabled="cartStore.cartList.length === 0"
        >去结算</el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 收货信息弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    title="填写收货信息"
    width="500px"
    append-to-body
  >
    <el-form :model="orderForm" label-width="80px">
      <el-form-item label="收货人" required>
        <el-input v-model="orderForm.signer_name" placeholder="请输入收货人姓名"></el-input>
      </el-form-item>
      <el-form-item label="手机号" required>
        <el-input v-model="orderForm.signer_mobile" placeholder="请输入联系电话"></el-input>
      </el-form-item>
      <el-form-item label="收货地址" required>
        <el-input v-model="orderForm.address" type="textarea" :rows="2" placeholder="请输入详细地址"></el-input>
      </el-form-item>
      <el-form-item label="留言">
        <el-input v-model="orderForm.post_script" placeholder="选填：给商家的留言"></el-input>
      </el-form-item>
    </el-form>

    <!-- 订单金额确认 -->
    <div class="order-summary">
      <span>订单金额：</span>
      <span class="summary-price">¥ {{ cartStore.selectedTotalPrice }}</span>
    </div>

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
/**
 * CartDrawer.vue - 购物车抽屉组件
 *
 * 功能：
 * 1. 显示购物车商品列表
 * 2. 商品选择（单选/全选）
 * 3. 修改数量、删除商品
 * 4. 结算流程（校验 → 填写收货信息 → 提交订单 → 跳转订单列表）
 */

import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '../store/cart';
import { createOrder } from '../api/trade';
import { ElMessageBox, ElMessage } from 'element-plus';
import { ShoppingCart, Picture } from '@element-plus/icons-vue';

// ============================================================
// Store & Router
// ============================================================

const cartStore = useCartStore();
const router = useRouter();

// ============================================================
// 响应式状态
// ============================================================

/** 收货信息弹窗可见性 */
const dialogVisible = ref(false);

/** 提交中状态 */
const loading = ref(false);

/** 订单表单数据 */
const orderForm = reactive({
  signer_name: '',
  signer_mobile: '',
  address: '',
  post_script: ''
});

// ============================================================
// 购物车操作
// ============================================================

/**
 * 修改商品数量
 */
const handleUpdate = (id: number, nums: number) => {
  cartStore.updateCartAction(id, nums);
};

/**
 * 删除商品
 */
const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这件商品吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    cartStore.deleteCartAction(id);
  });
};

// ============================================================
// 结算流程
// ============================================================

/**
 * 点击"去结算"按钮
 * 1. 检查是否勾选了商品
 * 2. 弹出二次确认框
 * 3. 确认后打开收货信息弹窗
 */
const handleCheckout = () => {
  // 1. 检查是否勾选了商品
  if (cartStore.selectedCount === 0) {
    ElMessage.warning('请先勾选要结算的商品');
    return;
  }

  // 2. 弹出二次确认框
  ElMessageBox.confirm(
    `确认使用模拟支付提交订单吗？\n总价: ¥${cartStore.selectedTotalPrice}`,
    '订单确认',
    {
      confirmButtonText: '确认下单',
      cancelButtonText: '取消',
      type: 'info',
    }
  ).then(() => {
    // 3. 确认后打开收货信息弹窗
    dialogVisible.value = true;
  }).catch(() => {
    // 用户取消
  });
};

/**
 * 提交订单
 * 1. 校验收货信息
 * 2. 调用 createOrder API
 * 3. 成功后关闭弹窗、刷新购物车、跳转订单列表
 */
const submitOrder = async () => {
  // 1. 校验收货信息
  if (!orderForm.signer_name.trim()) {
    ElMessage.warning('请填写收货人姓名');
    return;
  }
  if (!orderForm.signer_mobile.trim()) {
    ElMessage.warning('请填写联系电话');
    return;
  }
  if (!orderForm.address.trim()) {
    ElMessage.warning('请填写收货地址');
    return;
  }

  loading.value = true;

  try {
    // 2. 调用后端接口创建订单（后端会自动清空已下单的购物车项）
    await createOrder({
      signer_name: orderForm.signer_name,
      signer_mobile: orderForm.signer_mobile,
      address: orderForm.address,
      post_script: orderForm.post_script,
    });

    // 3. 成功提示
    ElMessage.success('下单成功！正在跳转到订单列表...');

    // 4. 关闭弹窗和抽屉
    dialogVisible.value = false;
    cartStore.toggleDrawer(false);

    // 5. 刷新购物车（后端已清空已下单的商品）
    await cartStore.fetchCartList();

    // 6. 清空选中状态和表单
    cartStore.selectedIds = [];
    resetOrderForm();

    // 7. 跳转到订单列表页面
    router.push('/orders');

  } catch (error: any) {
    console.error('下单失败:', error);
    ElMessage.error(error?.response?.data?.message || '下单失败，请重试');
  } finally {
    loading.value = false;
  }
};

/**
 * 重置订单表单
 */
const resetOrderForm = () => {
  orderForm.signer_name = '';
  orderForm.signer_mobile = '';
  orderForm.address = '';
  orderForm.post_script = '';
};
</script>

<style scoped>
/* ============================================================ */
/* 购物车内容区 */
/* ============================================================ */

.cart-content {
  height: calc(100vh - 180px);
  overflow-y: auto;
}

/* ============================================================ */
/* 全选栏 */
/* ============================================================ */

.select-all-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.selected-count {
  font-size: 13px;
  color: #909399;
}

/* ============================================================ */
/* 商品项 */
/* ============================================================ */

.cart-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s;
}

.cart-item:hover {
  background-color: #fafafa;
  margin: 0 -12px;
  padding: 12px;
  border-radius: 8px;
}

.cart-item.is-selected {
  background-color: rgba(139, 92, 246, 0.05);
}

.item-checkbox {
  margin-top: 24px;
}

.item-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.item-img-wrapper {
  flex-shrink: 0;
}

.item-img-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  color: #303133;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 15px;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ============================================================ */
/* 底部结算栏 */
/* ============================================================ */

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
}

.total {
  font-size: 14px;
  color: #606266;
}

.total .price {
  color: #f56c6c;
  font-size: 22px;
  font-weight: 700;
  margin-left: 4px;
}

/* ============================================================ */
/* 订单确认弹窗 */
/* ============================================================ */

.order-summary {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

.summary-price {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
  margin-left: 8px;
}

/* ============================================================ */
/* 空购物车 */
/* ============================================================ */

.empty-cart {
  padding: 40px 0;
}
</style>
