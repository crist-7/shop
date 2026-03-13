<template>
  <div class="login-wrapper">
    <div class="login-box">
      <h2 class="title">商城后台管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" size="large">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入管理员账号">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
          立即登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { login } from '../api/users'; // 引入登录 API 函数

const router = useRouter();
const loginFormRef = ref();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: ''
});

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleLogin = () => {
  loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true;
      try {
        // 调用真实的登录接口
        const res = await login(loginForm.username, loginForm.password);
        // JWT 返回 access 和 refresh 字段
        const accessToken = res.access;
        const refreshToken = res.refresh;

        if (accessToken) {
          // 存入 access token 和 refresh token
          localStorage.setItem('token', accessToken);
          localStorage.setItem('refreshToken', refreshToken);
          ElMessage.success('登录成功');
          router.push('/');
        } else {
          ElMessage.error('未获取到有效 Token');
        }
      } catch (error: any) {
        console.error('登录失败', error);
        // 如果报错，拦截器会自动提示，这里不做额外处理
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #2d3a4b;
}
.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}
.login-btn {
  width: 100%;
}
</style>