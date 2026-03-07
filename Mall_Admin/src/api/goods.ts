import request from '../utils/request';

// 1. 获取商品列表
export const getGoodsList = (params?: any) => {
  return request({ url: '/goods/', method: 'get', params });
};

// 2. 新增商品
export const createGoods = (data: any) => {
  return request({ url: '/goods/', method: 'post', data });
};

// 3. 修改商品
export const updateGoods = (id: number, data: any) => {
  return request({ url: `/goods/${id}/`, method: 'put', data });
};

// 4. 删除商品
export const deleteGoods = (id: number) => {
  return request({ url: `/goods/${id}/`, method: 'delete' });
};
// --- 轮播图管理相关接口 ---
export const getBannerList = (params?: any) => {
  return request({ url: '/banners/', method: 'get', params });
};

export const createBanner = (data: any) => {
  return request({ url: '/banners/', method: 'post', data });
};

export const updateBanner = (id: number, data: any) => {
  return request({ url: `/banners/${id}/`, method: 'put', data });
};

export const deleteBanner = (id: number) => {
  return request({ url: `/banners/${id}/`, method: 'delete' });
};
// 上传图片接口
export const uploadImage = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return request({
    url: '/upload/', // 对应刚才后端写的接口
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};