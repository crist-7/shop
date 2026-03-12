<template>
  <div class="goods-container">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="商品名称">
          <el-input v-model="searchForm.name" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>商品列表</span>
          <el-button type="success" @click="handleAdd">+ 新增商品</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <el-table-column label="商品图片" width="100" align="center">
          <template #default="scope">
            <el-image
              style="width: 50px; height: 50px; border-radius: 4px; border: 1px solid #f0f0f0;"
              :src="scope.row.goods_front_image"
              fit="cover"
              :preview-src-list="[scope.row.goods_front_image]"
              preview-teleported
            >
              <template #error>
                <div class="image-slot-error">无图</div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="shop_price" label="售价" width="120">
          <template #default="scope">¥ {{ scope.row.shop_price }}</template>
        </el-table-column>
        <el-table-column prop="goods_num" label="库存" width="100" align="center" />
        <el-table-column prop="sold_num" label="销量" width="100" align="center" />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      :title="dialogType === 'add' ? '新增商品' : '编辑商品'"
      v-model="dialogVisible"
      width="550px"
      destroy-on-close
    >
      <el-form :model="goodsForm" label-width="100px" style="padding-right: 20px;">
        <el-form-item label="商品名称" required>
          <el-input v-model="goodsForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品图片" required>
          <div class="image-edit-wrapper">
            <el-upload
              class="avatar-uploader"
              action=""
              :http-request="handleUpload"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
            >
              <img v-if="goodsForm.goods_front_image" :src="goodsForm.goods_front_image" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>

            <el-input
              v-model="goodsForm.goods_front_image"
              placeholder="或者直接粘贴图片链接"
              size="small"
              style="margin-top: 10px;"
            />
          </div>
        </el-form-item>

        <el-form-item label="分类ID" required>
          <el-input-number v-model="goodsForm.category" :min="1" />
          <span style="margin-left: 10px; color: #999; font-size: 12px;">(测试请填1)</span>
        </el-form-item>
        <el-form-item label="商品货号">
          <el-input v-model="goodsForm.goods_sn" placeholder="如: SN123456" />
        </el-form-item>
        <el-form-item label="商品售价">
          <el-input-number v-model="goodsForm.shop_price" :min="0" :precision="2" :step="10" />
        </el-form-item>
        <el-form-item label="商品库存">
          <el-input-number v-model="goodsForm.goods_num" :min="0" />
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
import { ref, reactive, onMounted } from 'vue'; // <--- 改回 'vue'
import { getGoodsList, createGoods, updateGoods, deleteGoods } from '../../api/goods';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { uploadImage } from '../../api/goods';
import type { UploadRequestOptions, UploadProps } from 'element-plus';

const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const tableData = ref<any[]>([]);

const searchForm = reactive({ name: '' });

// 弹窗相关状态
const dialogVisible = ref(false);
const dialogType = ref('add');
const submitLoading = ref(false);

// 初始化表单数据，包含图片字段
const initFormData = () => ({
  id: null,
  name: '',
  goods_front_image: '', // 【关键】确保有这个字段
  category: 1,
  goods_sn: '',
  shop_price: 0,
  goods_num: 100
});

const goodsForm = reactive(initFormData());

// 拉取列表数据
const fetchGoodsData = async () => {
  loading.value = true;
  try {
    const params = { page: currentPage.value, name: searchForm.name };
    const res: any = await getGoodsList(params);
    if (res.results) {
      tableData.value = res.results;
      total.value = res.count;
    } else {
      tableData.value = res || [];
      total.value = res.length || 0;
    }
  } catch (error) {
    console.error('获取商品失败', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => { currentPage.value = 1; fetchGoodsData(); };
const resetSearch = () => { searchForm.name = ''; handleSearch(); };
const handlePageChange = (val: number) => { currentPage.value = val; fetchGoodsData(); };

const handleAdd = () => {
  dialogType.value = 'add';
  // 清空表单并清空图片路径
  Object.assign(goodsForm, initFormData(), { goods_sn: `SN${Date.now()}` });
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = 'edit';
  // 将包括图片路径在内的数据回显
  Object.assign(goodsForm, {
    id: row.id,
    name: row.name,
    goods_front_image: row.goods_front_image, // 【关键】回显图片
    category: row.category,
    goods_sn: row.goods_sn,
    shop_price: row.shop_price,
    goods_num: row.goods_num
  });
  dialogVisible.value = true;
};

const submitForm = async () => {
  if (!goodsForm.name || !goodsForm.goods_front_image) {
    ElMessage.warning('请填写商品名称和图片链接');
    return;
  }
  submitLoading.value = true;
  try {
    if (dialogType.value === 'add') {
      await createGoods(goodsForm);
      ElMessage.success('新增商品成功！');
    } else {
      await updateGoods(goodsForm.id as unknown as number, goodsForm);
      ElMessage.success('修改商品成功！');
    }
    dialogVisible.value = false;
    fetchGoodsData();
  } catch (error) {
    console.error(error);
  } finally {
    submitLoading.value = false;
  }
};

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要永久删除商品【${row.name}】吗？`, '高危操作提示', {
    confirmButtonText: '狠心删除',
    cancelButtonText: '取消',
    type: 'error',
  }).then(async () => {
    try {
      await deleteGoods(row.id);
      ElMessage.success('删除成功');
      fetchGoodsData();
    } catch (error) {
      console.error(error);
    }
  }).catch(() => {});
};

// 自定义上传行为
const handleUpload = async (options: UploadRequestOptions) => {
  try {
    const res: any = await uploadImage(options.file);
    // 后端返回了完整的 url，直接赋值给表单
    goodsForm.goods_front_image = res.url;
    ElMessage.success('上传成功');
  } catch (error) {
    ElMessage.error('上传失败');
  }
};

// 上传前校验 (限制格式和大小)
const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('图片必须是 JPG 或 PNG 格式!');
    return false;
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过 2MB!');
    return false;
  }
  return true;
};

onMounted(() => {
  fetchGoodsData();
});
</script>

<style scoped>
.goods-container {
  padding: var(--space-xl);
  background-color: var(--bg-secondary);
  min-height: 100vh;
}

.search-card {
  margin-bottom: var(--space-xl);
  background-color: var(--bg-primary);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--bg-tertiary);
}

.table-card {
  background-color: var(--bg-primary);
  border: none;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--bg-tertiary);
  overflow: hidden;
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

.pagination {
  margin-top: var(--space-xl);
  display: flex;
  justify-content: flex-end;
  padding: var(--space-lg) var(--space-xl);
  background: var(--bg-secondary);
  border-top: 1px solid var(--bg-tertiary);
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

/* 图片单元格样式 */
:deep(.el-table .cell) {
  padding: var(--space-sm) var(--space-md);
}

/* 表格内图片占位样式 */
.image-slot-error {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 50px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

/* 【核心样式】：弹窗内图片编辑区域 */
.image-edit-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  width: 100%;
}
.image-url-input {
  width: 100%;
}
.form-image-preview {
  width: 120px;
  height: 120px;
  border: 1px dashed var(--text-tertiary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: var(--bg-tertiary);
  transition: border-color var(--transition-base);
}
.form-image-preview:hover {
  border-color: var(--primary-color);
}
.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.image-placeholder-slot, .image-error-slot {
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
  padding: var(--space-sm);
  line-height: 1.4;
}
.image-error-slot {
  color: var(--danger);
}
.image-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: -5px;
}
.avatar-uploader .el-upload {
  border: 1px dashed var(--text-tertiary);
  border-radius: var(--radius-md);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color var(--transition-base);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--primary-color);
}
.avatar-uploader-icon {
  font-size: 28px;
  color: var(--text-tertiary);
  width: 120px;
  height: 120px;
  text-align: center;
  line-height: 120px; /* 垂直居中 */
  display: flex;       /* 或者使用 flex 布局 */
  justify-content: center;
  align-items: center;
}
.avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
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