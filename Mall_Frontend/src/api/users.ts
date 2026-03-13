import request from '../utils/request';

// 登录接口 (获取 JWT Token)
export const login = (data: any) => {
    return request({
        url: '/login/', // 对应后端 urls.py 中的 api/login/
        method: 'post',
        data: data
    });
};

// 注册接口
export const register = (data: any) => {
    return request({
        url: '/users/', // 对应后端 UserViewSet
        method: 'post',
        data: data
    });
};

// 获取当前用户信息
export const getUserInfo = () => {
    return request({
        url: '/users/',
        method: 'get'
    });
};

// 更新当前用户信息
export const updateUserInfo = (id: number, data: any) => {
    return request({
        url: `/users/${id}/`,
        method: 'patch',
        data: data
    });
};