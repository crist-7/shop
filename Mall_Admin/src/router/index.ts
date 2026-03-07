import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router' // 【修复点】：专门引入类型

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '控制台' }
      },
      // 【新增】注册商品管理路由
      {
        path: 'goods',
        name: 'GoodsList',
        component: () => import('../views/goods/index.vue'),
        meta: { title: '商品列表' }
      },
        // 【新增】订单管理路由
      {
        path: 'orders',
        name: 'OrderList',
        component: () => import('../views/orders/index.vue'),
        meta: { title: '订单列表' }
      },
      // 【新增】用户管理路由
      {
        path: 'users',
        name: 'UserList',
        component: () => import('../views/users/index.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'category',
        name: 'CategoryList',
        component: () => import('../views/category/index.vue'),
        meta: { title: '分类管理' }
      },
      // 【新增】：轮播图管理路由
      {
        path: 'banner',
        name: 'BannerList',
        component: () => import('../views/banner/index.vue'),
        meta: { title: '轮播图管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 简单的路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.path !== '/login' && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router