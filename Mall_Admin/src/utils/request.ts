import axios from 'axios';
import { ElMessage } from 'element-plus';

// 1. 创建 axios 实例，指向你的 Django 后端地址
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 5000,
});

// 2. 请求拦截器：如果以后后台也做了真实登录，这里用来自动带上 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    // 如果不是假 token，就带上真实的
    if (token && token !== 'fake-admin-token') {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 3. 响应拦截器：统一剥离外层数据并处理报错
service.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    ElMessage.error(error.response?.data?.detail || '请求后端失败，请检查 Django 是否启动');
    return Promise.reject(error);
  }
);

export default service;