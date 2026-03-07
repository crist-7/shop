<template>
  <div class="banner-container">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>轮播图管理</span>
          <el-button type="success" @click="handleAdd">+ 新增轮播图</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <el-table-column label="轮播图片" width="200" align="center">
          <template #default="scope">
            <el-image
              style="width: 150px; height: 60px; border-radius: 4px;"
              :src="scope.row.image"
              fit="cover"
              :preview-src-list="[scope.row.image]"
              preview-teleported
            />
          </template>
        </el-table-column>

        <el-table-column prop="goods" label="关联商品ID" width="120" align="center" />
        <el-table-column prop="index" label="展示顺序(从小到大)" width="150" align="center" />
        <el-table-column prop="add_time" label="添加时间" min-width="180" align="center">
          <template #default="scope">
            {{ new Date(scope.row.add_time).toLocaleString() }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 增改弹窗 -->
    <el-dialog
      :title="dialogType === 'add' ? '新增轮播图' : '编辑轮播图'"
      v-model="dialogVisible"
      width="500px"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" style="padding-right: 20px;">
        <el-form-item label="关联商品ID" required>
          <el-input-number v-model="form.goods" :min="1" style="width: 100%;" />
          <div class="tip-text">用户点击图片后将跳转到该商品详情页</div>
        </el-form-item>

        <el-form-item label="轮播图片" required>
          <div class="image-edit-wrapper">
            <el-input
              v-model="form.image"
              placeholder="粘贴图片网络链接 (URL)"
              clearable
            />
            <el-image
              v-if="form.image"
              :src="form.image"
              fit="cover"
              class="preview-img"
            >
              <template #error>
                <div class="image-error-slot">无效链接</div>
              </template>
            </el-image>
          </div>
        </el-form-item>

        <el-form-item label="展示顺序">
          <el-input-number v-model="form.index" :min="0" style="width: 100%;" />
          <div class="tip-text">数字越小越靠前</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { getBannerList, createBanner, updateBanner, deleteBanner } from '../../api/goods'; // 确保路径正确
import { ElMessage, ElMessageBox } from 'element-plus';

const loading = ref(false);
const tableData = ref<any[]>([]);

// 弹窗状态
const dialogVisible = ref(false);
const dialogType = ref('add');
const submitLoading = ref(false);

const initFormData = () => ({
  id: null,
  goods: 1, // 默认关联商品ID 1
  image: '',
  index: 0
});
const form = reactive(initFormData());

const fetchData = async () => {
  loading.value = true;
  try {
    const res: any = await getBannerList();
    tableData.value = res.results ? res.results : res;
  } catch (error) {
    console.error('获取轮播图失败', error);
  } finally {
    loading.value = false;
  }
};

const handleAdd = () => {
  dialogType.value = 'add';
  Object.assign(form, initFormData());
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = 'edit';
  Object.assign(form, { ...row });
  dialogVisible.value = true;
};

const submitForm = async () => {
  if (!form.goods || !form.image) {
    ElMessage.warning('请填写完整的关联商品和图片链接');
    return;
  }
  submitLoading.value = true;
  try {
    if (dialogType.value === 'add') {
      await createBanner(form);
      ElMessage.success('新增成功');
    } else {
      await updateBanner(form.id as unknown as number, form);
      ElMessage.success('修改成功');
    }
    dialogVisible.value = false;
    fetchData();
  } catch (error) {
    console.error(error);
  } finally {
    submitLoading.value = false;
  }
};

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除这张轮播图吗？', '提示', {
    type: 'warning',
  }).then(async () => {
    try {
      await deleteBanner(row.id);
      ElMessage.success('删除成功');
      fetchData();
    } catch (error) {
      console.error(error);
    }
  }).catch(() => {});
};

onMounted(() => fetchData());
</script>

<style scoped>
.banner-container { padding: 20px; }
.table-card { background-color: #fff; border: none; border-radius: 8px;}
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold;}

.image-edit-wrapper { width: 100%; display: flex; flex-direction: column; gap: 10px; }
.preview-img { width: 100%; height: 120px; border-radius: 6px; border: 1px dashed #d9d9d9; }
.image-error-slot { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; background: #f5f7fa; color: #f56c6c; font-size: 12px; }
.tip-text { font-size: 12px; color: #909399; margin-top: 4px; line-height: 1.2;}
</style>