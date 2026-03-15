import { defineStore } from 'pinia';
import { addShopCart, getShopCarts, updateShopCart, deleteShopCart } from '../api/trade';
import { ElMessage } from 'element-plus';
import { useUserStore } from './user';

export const useCartStore = defineStore('cart', {
    state: () => ({
        cartList: [] as any[], // 购物车数据
        drawerVisible: false,  // 控制购物车抽屉的开关
        selectedIds: [] as number[], // 选中的购物车项ID
    }),
    getters: {
        // 购物车总数量
        cartCount: (state) => state.cartList.length,
        // 购物车总金额（所有商品）
        totalPrice: (state) => {
            let sum = 0;
            state.cartList.forEach((item) => {
                if (item.goods && item.goods.shop_price) {
                    sum += item.nums * parseFloat(item.goods.shop_price);
                }
            });
            return sum.toFixed(2);
        },
        // 选中的商品列表
        selectedItems: (state) => {
            return state.cartList.filter(item => state.selectedIds.includes(item.id));
        },
        // 选中的商品数量
        selectedCount: (state) => state.selectedIds.length,
        // 选中商品的总金额
        selectedTotalPrice: (state) => {
            let sum = 0;
            state.cartList.forEach((item) => {
                if (state.selectedIds.includes(item.id) && item.goods && item.goods.shop_price) {
                    sum += item.nums * parseFloat(item.goods.shop_price);
                }
            });
            return sum.toFixed(2);
        },
        // 是否全选
        isAllSelected: (state) => {
            return state.cartList.length > 0 && state.selectedIds.length === state.cartList.length;
        }
    },
    actions: {
        // 打开/关闭抽屉
        toggleDrawer(visible: boolean) {
            this.drawerVisible = visible;
        },

        // 获取列表
        async fetchCartList() {
            const userStore = useUserStore();
            if (!userStore.isLoggedIn) return;
            try {
                const res: any = await getShopCarts();
                this.cartList = res;
            } catch (error) {
                console.error("获取购物车失败", error);
            }
        },

        // 添加商品
        async addToCartAction(params: { goods: number, nums: number }) {
            const userStore = useUserStore();
            if (!userStore.isLoggedIn) {
                ElMessage.warning('请先登录');
                return false;
            }
            try {
                await addShopCart(params);
                ElMessage.success('加入成功');
                await this.fetchCartList();
                this.drawerVisible = true; // 加购成功后自动打开抽屉
                return true;
            } catch (error) {
                console.error("添加失败", error);
                return false;
            }
        },

        // 【新增】修改数量
        async updateCartAction(id: number, nums: number) {
            try {
                await updateShopCart(id, { nums });
                // 这里不需要重新拉整个列表，直接本地更新以提升性能，或者也可以重新拉取
                await this.fetchCartList();
                ElMessage.success('购物车更新成功');
            } catch (error) {
                console.error("更新失败", error);
                ElMessage.error('更新失败');
            }
        },

        // 【新增】删除商品
        async deleteCartAction(id: number) {
            try {
                await deleteShopCart(id);
                ElMessage.success('已删除');
                await this.fetchCartList();
            } catch (error) {
                console.error("删除失败", error);
            }
        },

        // 清空购物车（用户登出时调用）
        clearCart() {
            this.cartList = [];
            this.selectedIds = [];
        },

        // 切换选中状态
        toggleSelect(id: number) {
            const index = this.selectedIds.indexOf(id);
            if (index > -1) {
                this.selectedIds.splice(index, 1);
            } else {
                this.selectedIds.push(id);
            }
        },

        // 全选/取消全选
        toggleSelectAll() {
            if (this.isAllSelected) {
                this.selectedIds = [];
            } else {
                this.selectedIds = this.cartList.map(item => item.id);
            }
        },

        // 获取选中的购物车项（用于提交订单）
        getSelectedCartItems() {
            return this.cartList.filter(item => this.selectedIds.includes(item.id));
        },

        // 初始化购物车（应用启动或用户登录时调用）
        async initCart() {
            const userStore = useUserStore();
            if (userStore.isLoggedIn) {
                await this.fetchCartList();
            } else {
                this.clearCart();
            }
        }
    }
});