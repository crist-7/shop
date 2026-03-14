import request from '../utils/request';

// 获取所有订单列表
export const getOrderList = (params?: any) => {
  return request({
    url: '/orders/',
    method: 'get',
    params: params
  });
};

// 获取单个订单详情
export const getOrderDetail = (id: number) => {
  return request({
    url: `/orders/${id}/`,
    method: 'get'
  });
};

// 部分更新订单信息（地址、备注等）
export const updateOrder = (id: number, data: any) => {
  return request({
    url: `/orders/${id}/`,
    method: 'patch',
    data
  });
};

// 删除订单（软删除）
export const deleteOrder = (id: number) => {
  return request({
    url: `/orders/${id}/`,
    method: 'delete'
  });
};

// 标记订单为已支付
export const setOrderPaid = (id: number) => {
  return request({
    url: `/orders/${id}/set_paid/`,
    method: 'post'
  });
};

// 取消订单
export const cancelOrder = (id: number) => {
  return request({
    url: `/orders/${id}/cancel/`,
    method: 'post'
  });
};

// 修改订单地址（专用接口）
export const updateOrderAddress = (id: number, data: any) => {
  return request({
    url: `/orders/${id}/update_address/`,
    method: 'patch',
    data
  });
};

// 获取最近订单（仪表盘用）
export const getRecentOrders = () => {
  return request({
    url: '/dashboard/recent_orders/',
    method: 'get'
  });
};