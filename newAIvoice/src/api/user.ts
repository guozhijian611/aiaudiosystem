import request from '../utils/request';
// 退出
export const loginoutFn = () => {
    return request({
        url: '/user/logout',
        method: 'post',
    });
};
// 登录
export const loginFn = (username, password) => {
    return request({
        url: '/user/login',
        method: 'post',
        data: {
            username: username,
            password: password
        }
    });
};
// 创建用户/注册
export const createuserFn = (username, password) => {
    return request({
        url: '/user/register',
        method: 'post',
        data: {
            username: username,
            password: password
        }
    });
};
// 修改密码
export const changePassword = (oldPassword, newPassword) => {
    return request({
        url: '/user/updatepassword',
        method: 'post',
        data: {
            oldPassword: oldPassword,
            newPassword: newPassword
        }
    });
};
// 更新用户昵称
export const changeNickname = (nickname) => {
    return request({
        url: '/user/updateuserinfo',
        method: 'post',
        data: {
            nickname: nickname
        }
    });
};
// 获取用户信息
export const getuserInfo = () => {
    return request({
        url: '/user/getuserinfo',
        method: 'post'
    });
};