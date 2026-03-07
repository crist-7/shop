import { defineStore } from 'pinia';
import { login } from '../api/users';

export const useUserStore = defineStore('user', {
    state: () => ({
        token: localStorage.getItem('token') || '', // 初始化时优先从本地取
        username: localStorage.getItem('username') || '',
    }),
    getters: {
        isLoggedIn: (state) => !!state.token, // 判断是否有 token
    },
    actions: {
        // 登录动作
        async loginAction(loginForm: any) {
            try {
                const res: any = await login(loginForm);
                // 后端返回的数据结构通常是 { access: '...', refresh: '...' }
                if (res.access) {
                    this.token = res.access;
                    this.username = loginForm.username;

                    // 【关键】持久化存储到浏览器，刷新不丢失
                    localStorage.setItem('token', res.access);
                    localStorage.setItem('refresh', res.refresh);
                    localStorage.setItem('username', loginForm.username);
                    return true;
                }
                return false;
            } catch (error) {
                console.error("Login failed:", error);
                throw error;
            }
        },
        // 退出登录
        logout() {
            this.token = '';
            this.username = '';
            localStorage.removeItem('token');
            localStorage.removeItem('refresh');
            localStorage.removeItem('username');
        }
    }
});