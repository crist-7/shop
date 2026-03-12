<template>
  <div class="category-container">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="success" @click="handleAdd">+ 新增分类</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="分类ID" width="100" align="center" />
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="is_tab" label="是否导航显示" width="150" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_tab ? 'success' : 'info'">
              {{ scope.row.is_tab ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="添加时间" min-width="180">
          <template #default="scope">
            {{ new Date(scope.row.add_time).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="dialogType === 'add' ? '新增分类' : '编辑分类'" v-model="dialogVisible" width="400px">
      <el-form :model="categoryForm" label-width="100px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="导航显示">
          <el-switch v-model="categoryForm.is_tab" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '../../api/category';
import { ElMessage, ElMessageBox } from 'element-plus';

const loading = ref(false);
const tableData = ref<any[]>([]);
const dialogVisible = ref(false);
const dialogType = ref('add');

const categoryForm = reactive({
  id: null as number | null,
  name: '',
  is_tab: false,
});

const fetchCategories = async () => {
  loading.value = true;
  try {
    const res: any = await getCategoryList();
    tableData.value = res.results ? res.results : res;
  } catch (error) {
    console.error('获取分类失败', error);
  } finally {
    loading.value = false;
  }
};

const handleAdd = () => {
  dialogType.value = 'add';
  Object.assign(categoryForm, { id: null, name: '', is_tab: false });
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = 'edit';
  Object.assign(categoryForm, { id: row.id, name: row.name, is_tab: row.is_tab });
  dialogVisible.value = true;
};

const submitForm = async () => {
  if (!categoryForm.name) return ElMessage.warning('请输入分类名称');
  try {
    if (dialogType.value === 'add') {
      await createCategory(categoryForm);
      ElMessage.success('新增成功');
    } else {
      await updateCategory(categoryForm.id!, categoryForm);
      ElMessage.success('修改成功');
    }
    dialogVisible.value = false;
    fetchCategories();
  } catch (error) {
    console.error(error);
  }
};

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除分类【${row.name}】吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteCategory(row.id);
    ElMessage.success('删除成功');
    fetchCategories();
  }).catch(() => {});
};

onMounted(() => fetchCategories());
</script>

<style scoped>
.category-container {
  padding: var(--space-xl);
  background-color: var(--bg-secondary);
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--bg-tertiary);
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

/* 表格样式增强 */
:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--bg-tertiary);
}

:deep(.el-table__header) {
  background: var(--bg-tertiary);
}

:deep(.el-table th) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 600;
  border-bottom: 1px solid var(--bg-hover);
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--bg-tertiary);
  color: var(--text-secondary);
}

:deep(.el-table__row:hover) {
  background-color: var(--bg-hover);
}

:deep(.el-table__row:hover td) {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

/* 按钮微动效 */
.el-button {
  transition: all var(--transition-fast) !important;
}

.el-button:active {
  transform: scale(0.98);
}

.el-button--primary:hover {
  box-shadow: 0 4px 12px rgba(var(--primary-color-rgb, 59, 130, 246), 0.3);
}

/* 弹窗样式增强 */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--bg-tertiary);
}

:deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--bg-hover);
}

:deep(.el-dialog__body) {
  padding: var(--space-xl);
}

:deep(.el-form-item) {
  margin-bottom: var(--space-lg);
}
</style>