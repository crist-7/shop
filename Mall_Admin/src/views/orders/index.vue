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
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
              :disabled="scope.row.pay_status !== 'PAYING'"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handleSetPaid(scope.row)"
              :disabled="scope.row.pay_status === 'TRADE_SUCCESS' || scope.row.pay_status === 'TRADE_CLOSED'"
            >
              标记支付
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑订单对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑订单信息"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="收货人" prop="signer_name">
          <el-input v-model="editForm.signer_name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="signer_mobile">
          <el-input v-model="editForm.signer_mobile" placeholder="请输入11位手机号码" maxlength="11" />
        </el-form-item>
        <el-form-item label="收货地址" prop="address">
          <el-input
            v-model="editForm.address"
            type="textarea"
            :rows="3"
            placeholder="请输入详细收货地址"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="订单备注" prop="post_script">
          <el-input
            v-model="editForm.post_script"
            type="textarea"
            :rows="2"
            placeholder="请输入订单备注信息"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit" :loading="editSubmitting">
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { getOrderList, updateOrder, deleteOrder, setOrderPaid } from '../../api/orders';

const loading = ref(false);
const tableData = ref<any[]>([]);

// 编辑对话框相关
const editDialogVisible = ref(false);
const editSubmitting = ref(false);
const editFormRef = ref<FormInstance>();
const editForm = reactive({
  id: 0,
  signer_name: '',
  signer_mobile: '',
  address: '',
  post_script: ''
});

const editRules: FormRules = {
  signer_name: [
    { required: false, message: '请输入收货人姓名', trigger: 'blur' }
  ],
  signer_mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  address: [
    { required: false, message: '请输入收货地址', trigger: 'blur' }
  ],
  post_script: [
    { required: false, message: '请输入订单备注', trigger: 'blur' }
  ]
};

const fetchOrders = async () => {
  loading.value = true;
  try {
    const res: any = await getOrderList();
    // 兼容分页和不分页的数据结构
    tableData.value = res.results ? res.results : res;
  } catch (error) {
    console.error('获取订单失败', error);
    ElMessage.error('获取订单列表失败');
  } finally {
    loading.value = false;
  }
};

// 编辑订单
const handleEdit = (row: any) => {
  editForm.id = row.id;
  editForm.signer_name = row.signer_name || '';
  editForm.signer_mobile = row.signer_mobile || '';
  editForm.address = row.address || '';
  editForm.post_script = row.post_script || '';
  editDialogVisible.value = true;
};

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormRef.value) return;

  try {
    await editFormRef.value.validate();
  } catch (error) {
    return;
  }

  editSubmitting.value = true;
  try {
    // 过滤掉空值
    const submitData: any = {};
    if (editForm.signer_name.trim()) submitData.signer_name = editForm.signer_name.trim();
    if (editForm.signer_mobile.trim()) submitData.signer_mobile = editForm.signer_mobile.trim();
    if (editForm.address.trim()) submitData.address = editForm.address.trim();
    if (editForm.post_script.trim()) submitData.post_script = editForm.post_script.trim();

    if (Object.keys(submitData).length === 0) {
      ElMessage.warning('未修改任何信息');
      return;
    }

    await updateOrder(editForm.id, submitData);
    ElMessage.success('订单信息更新成功');
    editDialogVisible.value = false;
    fetchOrders(); // 刷新列表
  } catch (error: any) {
    const errorMsg = error.response?.data?.error || error.message || '更新失败';
    ElMessage.error(`更新失败: ${errorMsg}`);
  } finally {
    editSubmitting.value = false;
  }
};

// 标记为已支付
const handleSetPaid = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认将订单 ${row.order_sn} 标记为已支付？此操作将扣减商品库存。`,
      '确认标记支付',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    loading.value = true;
    await setOrderPaid(row.id);
    ElMessage.success('订单标记为已支付成功');
    fetchOrders();
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || error.message || '操作失败';
      ElMessage.error(`标记支付失败: ${errorMsg}`);
    }
  } finally {
    loading.value = false;
  }
};

// 删除订单
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认删除订单 ${row.order_sn}？此操作将软删除订单，可在数据库中恢复。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    loading.value = true;
    await deleteOrder(row.id);
    ElMessage.success('订单删除成功');
    fetchOrders();
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || error.message || '删除失败';
      ElMessage.error(`删除失败: ${errorMsg}`);
    }
  } finally {
    loading.value = false;
  }
};

// 对话框关闭时重置表单
const handleDialogClose = () => {
  if (editFormRef.value) {
    editFormRef.value.resetFields();
  }
};

onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
.orders-container { padding: 20px; }
.card-header { font-weight: bold; }

/* 操作按钮间距 */
.el-button + .el-button {
  margin-left: 8px;
}

/* 对话框表单样式 */
.el-form-item {
  margin-bottom: 20px;
}
</style>