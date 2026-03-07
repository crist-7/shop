import request from '../utils/request';

// 获取所有订单列表
export const getOrderList = (params?: any) => {
  return request({
    url: '/orders/',
    method: 'get',
    params: params
  });
};