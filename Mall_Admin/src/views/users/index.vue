<template>
  <div class="users-container">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>注册用户列表</span>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="用户ID" width="80" align="center" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="mobile" label="手机号码" width="150">
          <template #default="scope">
            {{ scope.row.mobile || '未绑定' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="账号状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" min-width="180">
          <template #default="scope">
            {{ new Date(scope.row.date_joined).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="scope">
            <el-button
              v-if="scope.row.username !== 'admin'"
              link
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
            <span v-else style="color: #999; font-size: 12px;">超级管理员</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getUserList, deleteUser } from '../../api/users';
import { ElMessage, ElMessageBox } from 'element-plus';

const loading = ref(false);
const tableData = ref<any[]>([]);

const fetchUsers = async () => {
  loading.value = true;
  try {
    const res: any = await getUserList();
    tableData.value = res.results ? res.results : res;
  } catch (error) {
    console.error('获取用户失败', error);
  } finally {
    loading.value = false;
  }
};

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要永久删除用户【${row.username}】吗？`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteUser(row.id);
      ElMessage.success('用户已删除');
      fetchUsers();
    } catch (error) {
      console.error(error);
    }
  }).catch(() => {});
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.users-container { padding: 20px; }
.card-header { font-weight: bold; }
</style>