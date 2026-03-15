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

// ================= 新增接口 =================

// 获取当前登录用户信息
export const getUserInfo = () => {
  return request({ url: '/users/info/', method: 'get' });
};

// 修改密码
export const changePassword = (data: { old_password: string; new_password: string; confirm_password: string }) => {
  return request({ url: '/users/change_password/', method: 'post', data });
};