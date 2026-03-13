import request from '../utils/request';

// 获取购物车列表
export const getShopCarts = () => {
    return request({
        url: '/shopcarts/',
        method: 'get'
    });
};

// 添加商品到购物车
export const addShopCart = (data: { goods: number, nums: number }) => {
    return request({
        url: '/shopcarts/',
        method: 'post',
        data: data
    });
};

// 修改购物车商品数量 (id是购物车记录的ID，不是商品ID)
export const updateShopCart = (id: number, params: { nums: number }) => {
    return request({
        url: `/shopcarts/${id}/`,
        method: 'patch',
        data: params
    });
};

// 删除购物车商品
export const deleteShopCart = (id: number) => {
    return request({
        url: `/shopcarts/${id}/`,
        method: 'delete'
    });
};
// 创建订单 (结算)
export const createOrder = (data: any) => {
    return request({
        url: '/orders/',
        method: 'post',
        data: data
    });
};

// 获取订单列表 (为后续做准备)
export const getOrders = () => {
    return request({
        url: '/orders/',
        method: 'get'
    });
};

// 支付订单
export const payOrder = (orderId: number) => {
    return request({
        url: `/orders/${orderId}/pay/`,
        method: 'post'
    });
};

// 修改订单地址
export const updateOrderAddress = (orderId: number, data: { address?: string, signer_name?: string, signer_mobile?: string }) => {
    return request({
        url: `/orders/${orderId}/update_address/`,
        method: 'patch',
        data: data
    });
};

// 取消订单
export const cancelOrder = (orderId: number) => {
    return request({
        url: `/orders/${orderId}/cancel/`,
        method: 'post'
    });
};