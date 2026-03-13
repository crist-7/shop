import { createRouter, createWebHistory } from 'vue-router'
import { defineAsyncComponent } from 'vue'
import type { RouteRecordRaw } from 'vue-router' // 【修复点】：专门引入类型

// 异步组件加载配置
const asyncComponentOptions = {
  // 加载中显示的组件（可选）
  // loadingComponent: () => import('@/components/Loading.vue'),
  // 加载失败时显示的组件（可选）
  // errorComponent: () => import('@/components/Error.vue'),
  // 延迟显示加载组件的时间（毫秒）
  delay: 200,
  // 超时时间（毫秒）
  timeout: 10000,
  // 是否允许挂起（suspensible）
  suspensible: false
};

// 创建配置好的异步组件
const createAsyncComponent = (loader: () => Promise<any>) => {
  return defineAsyncComponent({
    loader,
    ...asyncComponentOptions
  });
};

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: createAsyncComponent(() => import('../views/Login.vue'))
  },
  {
    path: '/',
    name: 'Layout',
    component: createAsyncComponent(() => import('../layout/index.vue')),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: createAsyncComponent(() => import('../views/Dashboard.vue')),
        meta: { title: '控制台' }
      },
      // 【新增】注册商品管理路由
      {
        path: 'goods',
        name: 'GoodsList',
        component: createAsyncComponent(() => import('../views/goods/index.vue')),
        meta: { title: '商品列表' }
      },
        // 【新增】订单管理路由
      {
        path: 'orders',
        name: 'OrderList',
        component: createAsyncComponent(() => import('../views/orders/index.vue')),
        meta: { title: '订单列表' }
      },
      // 【新增】用户管理路由
      {
        path: 'users',
        name: 'UserList',
        component: createAsyncComponent(() => import('../views/users/index.vue')),
        meta: { title: '用户管理' }
      },
      {
        path: 'category',
        name: 'CategoryList',
        component: createAsyncComponent(() => import('../views/category/index.vue')),
        meta: { title: '分类管理' }
      },
      // 【新增】：轮播图管理路由
      {
        path: 'banner',
        name: 'BannerList',
        component: createAsyncComponent(() => import('../views/banner/index.vue')),
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