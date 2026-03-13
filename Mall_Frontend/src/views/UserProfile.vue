<template>
  <div class="user-profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
          <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
        </div>
      </template>
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        <el-form-item label="姓氏" prop="first_name">
          <el-input v-model="form.first_name" />
        </el-form-item>
        <el-form-item label="名字" prop="last_name">
          <el-input v-model="form.last_name" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="生日" prop="birthday">
          <el-date-picker v-model="form.birthday" type="date" placeholder="选择生日" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="form.mobile" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getUserInfo, updateUserInfo } from '../api/users'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const saving = ref(false)
const userId = ref<number | null>(null)

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  gender: '',
  birthday: '',
  mobile: ''
})

const rules: FormRules = {
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ]
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const res = await getUserInfo()
    // 注意：返回的是数组，取第一个元素
    if (Array.isArray(res) && res.length > 0) {
      const user = res[0]
      userId.value = user.id
      form.value.username = user.username || ''
      form.value.email = user.email || ''
      form.value.first_name = user.first_name || ''
      form.value.last_name = user.last_name || ''
      form.value.gender = user.gender || ''
      form.value.birthday = user.birthday || ''
      form.value.mobile = user.mobile || ''
    } else if (typeof res === 'object' && res.id) {
      // 如果返回的是单个对象（比如通过 /users/me/ 端点）
      const user = res
      userId.value = user.id
      form.value.username = user.username || ''
      form.value.email = user.email || ''
      form.value.first_name = user.first_name || ''
      form.value.last_name = user.last_name || ''
      form.value.gender = user.gender || ''
      form.value.birthday = user.birthday || ''
      form.value.mobile = user.mobile || ''
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 保存修改
const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    if (!userId.value) {
      ElMessage.warning('无法获取用户ID')
      return
    }
    saving.value = true
    await updateUserInfo(userId.value, form.value)
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error('更新失败', error)
    ElMessage.error('更新失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.user-profile-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}
.profile-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>