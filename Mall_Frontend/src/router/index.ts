import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../components/Home.vue') // 首页：商品列表
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../views/Register.vue')
    }, // <--- 【修复点1】这里加了逗号
    // 【新增】商品详情页 (动态路由 :id)
    {
        path: '/goods/:id',
        name: 'GoodsDetail',
        component: () => import('../views/GoodsDetail.vue')
    }, // <--- 【修复点2】这里也建议加上逗号，方便以后继续加路由
    // 【新增】订单列表页 (需要登录)
    {
        path: '/orders',
        name: 'OrderList',
        component: () => import('../views/OrderList.vue'),
        meta: { requiresAuth: true } // 标记需要登录
    }
];

const router = createRouter({
    // 如果你的项目在根目录下运行，这样写最稳
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior() {
        // 每次切换页面，自动滚动到顶部
        return { top: 0 };
    }
});

// 【新增】简单的路由守卫 (Navigation Guard)
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    if (to.meta.requiresAuth && !token) {
        // 如果去需要登录的页面但没token，跳转登录页
        next('/login');
    } else {
        next();
    }
});

export default router;