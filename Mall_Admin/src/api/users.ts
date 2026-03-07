import request from '../utils/request';

// 获取用户列表
export const getUserList = (params?: any) => {
  return request({ url: '/users/', method: 'get', params });
};

// 删除用户
export const deleteUser = (id: number) => {
  return request({ url: `/users/${id}/`, method: 'delete' });
};