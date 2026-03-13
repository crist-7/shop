import request from '../utils/request';

// 用户登录
export const login = (username: string, password: string) => {
  return request.post('/login/', { username, password });
};

// 获取用户列表
export const getUserList = (params?: any) => {
  return request({ url: '/users/', method: 'get', params });
};

// 删除用户
export const deleteUser = (id: number) => {
  return request({ url: `/users/${id}/`, method: 'delete' });
};