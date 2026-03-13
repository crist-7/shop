<template>
  <div class="mall-layout">
    <header class="mall-header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon">🛍️</span>
          <span class="logo-text">星辰商城</span>
        </div>

        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索手机、电脑、家电..."
            class="search-input"
            size="large"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #append>
              <el-button type="primary" class="search-btn" @click="handleSearch">
                <el-icon><Search /></el-icon> 搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <div class="user-actions">
          <template v-if="userStore.isLoggedIn">
            <el-badge :value="cartStore.cartCount" class="cart-badge" :hidden="cartStore.cartCount === 0">
              <el-button class="cart-btn" plain @click="cartStore.toggleDrawer(true)">
                🛒 我的购物车
              </el-button>
            </el-badge>
            <span class="user-greeting">欢迎, {{ userStore.username }}</span>
            <el-button link @click="handleLogout">退出</el-button>
          </template>
          <template v-else>
            <router-link to="/login"><el-button type="primary" plain>登录</el-button></router-link>
            <el-button style="margin-left: 10px">注册</el-button>
          </template>
        </div>
      </div>
    </header>

    <nav class="category-nav">
      <div class="nav-inner">
        <span
          class="nav-item"
          :class="{ active: activeCategoryId === null }"
          @click="handleCategoryClick(null)"
        >
          首页
        </span>
        <span
          v-for="item in categoryList"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeCategoryId === item.id }"
          @click="handleCategoryClick(item.id)"
        >
          {{ item.name }}
        </span>
      </div>
    </nav>

    <div class="banner-section">
      <el-carousel height="380px" trigger="click" v-if="bannerList.length > 0">
        <el-carousel-item v-for="item in bannerList" :key="item.id">
          <div
            class="banner-content"
            style="padding: 0; cursor: pointer;"
            @click="router.push(`/goods/${item.goods}`)"
          >
            <img :src="item.image" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />
          </div>
        </el-carousel-item>
      </el-carousel>

      <el-carousel height="380px" v-else>
        <el-carousel-item>
          <div class="banner-content" style="background: linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%);">
            <div class="banner-text">
              <h2>星辰商城 · 毕业季大促</h2>
              <p>暂无轮播图，请去后台添加</p>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <main class="main-content">
      <div class="section-header">
        <h2 class="section-title">✨ 热卖推荐</h2>
      </div>

      <div class="goods-list">
        <template v-if="loading">
          <Skeleton
            v-for="i in 8"
            :key="i"
            type="product"
            :showImage="true"
            :lines="2"
            class="goods-card-skeleton"
          />
        </template>
        <template v-else>
          <el-card
            v-for="item in goodsList"
            :key="item.id"
            class="goods-card"
            shadow="hover"
            :body-style="{ padding: '0px' }"
            @click="router.push(`/goods/${item.id}`)"
            style="cursor: pointer"
          >
            <div class="image-wrapper">
              <img v-if="item.goods_front_image" :src="item.goods_front_image" class="image"/>
              <div v-else class="image-placeholder">暂无图片</div>
            </div>
            <div class="card-content">
              <h3 class="goods-name">{{ item.name }}</h3>
              <div class="bottom-action">
                <span class="price-num">¥ {{ item.shop_price }}</span>
                <el-button type="primary" size="small" @click.stop="addToCart(item)">加入购物车</el-button>
              </div>
            </div>
          </el-card>
        </template>
      </div>
    </main>

    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Search } from '@element-plus/icons-vue';
import { useUserStore } from '../store/user';
import { useCartStore } from '../store/cart';
import { getGoodsList, getCategoryList, getBannerList } from '../api/goods'; // 确保路径正确
import CartDrawer from './CartDrawer.vue';
import Skeleton from './Skeleton.vue';

const router = useRouter();
const userStore = useUserStore();
const cartStore = useCartStore();

const loading = ref(false);
const goodsList = ref<any[]>([]);
const categoryList = ref<any[]>([]);
const bannerList = ref<any[]>([]);
const searchKeyword = ref('');
const activeCategoryId = ref<number | null>(null);

// 拉取所有数据
const fetchAllData = async () => {
  loading.value = true;
  try {
    // 1. 获取分类
    const catRes: any = await getCategoryList();
    categoryList.value = catRes.results ? catRes.results : catRes;

    // 2. 获取轮播图
    const bannerRes: any = await getBannerList();
    bannerList.value = bannerRes.results ? bannerRes.results : bannerRes;

    // 3. 获取商品
    await fetchGoods();
  } catch (error) {
    console.error('数据加载失败', error);
  } finally {
    loading.value = false;
  }
};

const fetchGoods = async () => {
  const params: any = {};
  if (searchKeyword.value) params.search = searchKeyword.value;
  if (activeCategoryId.value) params.category = activeCategoryId.value;

  const res: any = await getGoodsList(params);
  goodsList.value = res.results ? res.results : (res || []);
};

const handleSearch = () => {
  activeCategoryId.value = null;
  fetchGoods();
};

const handleCategoryClick = (id: number | null) => {
  activeCategoryId.value = id;
  searchKeyword.value = '';
  fetchGoods();
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

const addToCart = async (item: any) => {
  if (!userStore.isLoggedIn) return router.push('/login');
  await cartStore.addToCartAction({ goods: item.id, nums: 1 });
};

onMounted(() => {
  fetchAllData();
  if (userStore.isLoggedIn) cartStore.fetchCartList();
});
</script>

<style scoped>
/* 简化的核心样式，防止布局错乱 */
.mall-layout { background-color: var(--bg-secondary); min-height: 100vh; }
.mall-header { background: var(--bg-primary); border-bottom: 2px solid var(--primary-color); padding: 0 var(--space-xl); box-shadow: var(--shadow-sm); }
.header-inner { max-width: var(--container-xl); margin: 0 auto; height: 80px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 24px; font-weight: bold; color: var(--primary-color); display: flex; align-items: center; gap: var(--space-sm); transition: color var(--transition-fast); }
.logo:hover { color: var(--primary-light); }
.search-bar { flex: 1; max-width: 500px; margin: 0 var(--space-4xl); }
.category-nav { background: var(--bg-primary); border-bottom: 1px solid var(--bg-tertiary); box-shadow: var(--shadow-xs); }
.nav-inner { max-width: var(--container-xl); margin: 0 auto; display: flex; gap: var(--space-2xl); padding: 0 var(--space-xl); }
.nav-item { line-height: 50px; cursor: pointer; padding: 0 var(--space-md); font-size: 16px; color: var(--text-secondary); transition: all var(--transition-fast); }
.nav-item:hover { color: var(--primary-color); }
.nav-item.active { color: var(--primary-color); border-bottom: 3px solid var(--primary-color); font-weight: bold; background: var(--bg-hover); border-radius: var(--radius-sm) var(--radius-sm) 0 0; }
.banner-section { max-width: var(--container-xl); margin: var(--space-2xl) auto; }
.banner-content {
  height: 100%;
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg), var(--glow-soft);
  transition: all var(--transition-base);
  position: relative;
}
.banner-content:hover {
  box-shadow: var(--shadow-xl), var(--glow-primary);
  transform: translateY(-4px);
}
.main-content { max-width: var(--container-xl); margin: 0 auto; padding-bottom: var(--space-5xl); padding-top: var(--space-2xl); }
.goods-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-2xl); margin-top: var(--space-2xl); }
.goods-card {
  overflow: hidden;
  border-radius: var(--radius-lg); /* 12px 大圆角 */
  background: var(--bg-primary);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid transparent; /* 透明边框保留布局空间 */
  background-clip: padding-box; /* 确保背景不延伸到边框区域 */
}

.goods-card:hover {
  box-shadow: var(--shadow-multi-glow); /* 彩色弥散阴影 */
  transform: translateY(-12px) scale(1.02); /* 更明显的浮起效果 */
  border-color: transparent; /* 移除边框 */
}

.image-wrapper {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--bg-secondary);
  position: relative;
}

.image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform var(--transition-base);
  padding: var(--space-md);
}

.goods-card:hover .image {
  transform: scale(1.05);
}

.card-content {
  padding: var(--space-xl);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.goods-name {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  line-height: 1.4;
  font-weight: 600;
  flex-grow: 1;
}

.bottom-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-lg);
}

.price-num {
  color: var(--danger);
  font-size: 20px;
  font-weight: bold;
}

.price-num::before {
  content: '¥ ';
  font-size: 16px;
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
.footer-links { display: flex; justify-content: space-around; padding: var(--space-4xl) 0; background: var(--bg-tertiary); color: var(--text-secondary); }
.footer-copyright { text-align: center; padding: var(--space-xl); background: var(--bg-tertiary); color: var(--text-tertiary); border-top: 1px solid var(--bg-hover); }

.goods-card-skeleton {
  height: 340px;
  border-radius: var(--radius-xl);
  overflow: hidden;
}
</style>