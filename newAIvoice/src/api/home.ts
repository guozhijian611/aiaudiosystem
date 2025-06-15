import request from '../utils/request';

// 获取任务状态详情
export const obtainDetails = () => {
    return request({
        url: '/index/taskStatusCount',
        method: 'post'
    });
}; 