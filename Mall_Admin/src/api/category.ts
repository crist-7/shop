import request from '../utils/request';

export const getCategoryList = (params?: any) => request({ url: '/category/', method: 'get', params });
export const createCategory = (data: any) => request({ url: '/category/', method: 'post', data });
export const updateCategory = (id: number, data: any) => request({ url: `/category/${id}/`, method: 'put', data });
export const deleteCategory = (id: number) => request({ url: `/category/${id}/`, method: 'delete' });