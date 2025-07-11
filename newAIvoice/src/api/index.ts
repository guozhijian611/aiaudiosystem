import request from '../utils/request';

export const fetchData = () => {
    return request({
        url: './mock/table.json',
        method: 'get'
    });
};


export const fetchUserData = () => {
    return request({
        url: './mock/user.json',
        method: 'get'
    });
};

export const fetchTaskData = () => {
    return request({
        url: './mock/task.json',
        method: 'get'
    });
};
export const fetchFileData = () => {
    return request({
        url: './mock/file.json',
        method: 'get'
    });
};
export const fetchRoleData = () => {
    return request({
        url: './mock/role.json',
        method: 'get'
    });
};

