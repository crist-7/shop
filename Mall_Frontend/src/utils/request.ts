import axios from 'axios';
import { ElMessage } from 'element-plus';
import 'element-plus/theme-chalk/el-message.css'; // 引入消息提示样式

// 1. 创建 axios 实例
const service = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', // 指向你的 Django 后端 API 地址
    timeout: 5000, // 请求超时时间
});

// 2. 请求拦截器 (在发送请求前自动携带 Token)
service.interceptors.request.use(
    (config) => {
        // 从浏览器本地存储中获取 JWT Token
        const token = localStorage.getItem('token');
        if (token) {
            // 如果有 token，按规范添加到请求头中
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 3. 响应拦截器 (统一处理后端的报错信息)
service.interceptors.response.use(
    (response) => {
        return response.data; // 直接返回数据部分，剥离 axios 的外层包装
    },
    (error) => {
        const { response } = error;
        if (response) {
            switch (response.status) {
                case 401:
                    ElMessage.error('登录状态已过期或未提供身份认证信息，请登录');
                    localStorage.removeItem('token');
                    // 实际项目中这里可以加代码跳转到登录页
                    break;
                case 403:
                    ElMessage.error('您没有权限进行此操作');
                    break;
                case 404:
                    ElMessage.error('请求的资源不存在');
                    break;
                case 500:
                    ElMessage.error('服务器内部错误，请联系管理员');
                    break;
                default:
                    ElMessage.error(response.data.detail || '网络请求错误');
            }
        } else {
            ElMessage.error('网络连接异常，请检查后端服务是否启动');
        }
        return Promise.reject(error);
    }
);

export default service;