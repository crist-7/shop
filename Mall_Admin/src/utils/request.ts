import axios from 'axios';
import { ElMessage } from 'element-plus';
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// 1. 创建 axios 实例，指向你的 Django 后端地址
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 5000,
});

// 2. 请求拦截器：自动带上 JWT Token
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 access token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    // 确保 Content-Type 为 application/json（可根据需要调整）
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 3. 响应拦截器：统一错误处理与 Token 过期自动处理
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 统一剥离外层数据，直接返回业务数据
    return response.data;
  },
  (error) => {
    const { response } = error;

    // 处理 HTTP 401 未授权错误（Token过期或无效）
    if (response?.status === 401) {
      // 清除本地存储的 token 信息
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');

      // 显示友好提示
      ElMessage.error('登录已过期，请重新登录');

      // 重定向到登录页面（避免在当前页面停留）
      setTimeout(() => {
        // 使用 window.location 确保完全跳转，避免路由守卫循环
        window.location.href = '/login';
      }, 1500);

      // 返回一个 resolved Promise 避免后续错误处理
      return Promise.resolve({});
    }

    // 处理 HTTP 403 禁止访问错误（CSRF 校验失败等）
    if (response?.status === 403) {
      const errorMsg = response.data?.detail || '权限不足，禁止访问';
      ElMessage.error(errorMsg);
      // 如果是 CSRF 失败，可以提示用户刷新页面
      if (errorMsg.includes('CSRF')) {
        console.warn('CSRF 校验失败，建议检查 token 或刷新页面');
      }
    }

    // 其他错误统一处理
    const errorMsg = response?.data?.detail || error.message || '请求失败，请检查网络或后端服务';
    ElMessage.error(errorMsg);

    // 返回 reject 让调用方可以继续处理
    return Promise.reject(error);
  }
);

export default service;