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

      <div class="goods-list" v-loading="loading">
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
      </div>
    </main>

    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Search, ArrowDown } from '@element-plus/icons-vue';
import { useUserStore } from '../store/user';
import { useCartStore } from '../store/cart';
import { getGoodsList, getCategoryList, getBannerList } from '../api/goods'; // 确保路径正确
import CartDrawer from './CartDrawer.vue';

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
  if (searchKeyword.value) params.name = searchKeyword.value;
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
.mall-layout { background-color: #f4f4f4; min-height: 100vh; }
.mall-header { background: #fff; border-bottom: 2px solid #409EFF; padding: 0 20px; }
.header-inner { max-width: 1200px; margin: 0 auto; height: 80px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 24px; font-weight: bold; color: #409EFF; display: flex; align-items: center; gap: 10px; }
.search-bar { flex: 1; max-width: 500px; margin: 0 40px; }
.category-nav { background: #fff; border-bottom: 1px solid #ddd; }
.nav-inner { max-width: 1200px; margin: 0 auto; display: flex; gap: 30px; }
.nav-item { line-height: 50px; cursor: pointer; padding: 0 10px; font-size: 16px; }
.nav-item.active { color: #409EFF; border-bottom: 3px solid #409EFF; font-weight: bold; }
.banner-section { max-width: 1200px; margin: 20px auto; }
.banner-content { height: 100%; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }
.main-content { max-width: 1200px; margin: 0 auto; padding-bottom: 40px; }
.goods-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }
.goods-card { overflow: hidden; }
.image-wrapper { height: 220px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.image { width: 100%; height: 100%; object-fit: contain; }
.card-content { padding: 10px; }
.bottom-action { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.price-num { color: #f56c6c; font-size: 18px; font-weight: bold; }
.footer-links { display: flex; justify-content: space-around; padding: 40px 0; background: #333; color: #999; }
.footer-copyright { text-align: center; padding: 20px; background: #333; color: #666; border-top: 1px solid #444; }
</style>