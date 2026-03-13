import request from '../utils/request';

// 获取商品列表
export const getGoodsList = (params?: any) => {
  return request({
    url: '/goods/',
    method: 'get',
    params
  });
};

// 获取分类列表
export const getCategoryList = () => {
  return request({
    url: '/category/',
    method: 'get',
    params: {
      page_size: 100 // 一次拉取所有分类
    }
  });
};

// 获取轮播图列表
export const getBannerList = () => {
  return request({
    url: '/banners/',
    method: 'get'
  });
};

// 获取商品详情
export const getGoodsDetail = (id: number | string) => {
  return request({
    url: `/goods/${id}/`,
    method: 'get'
  });
};