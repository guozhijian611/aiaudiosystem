import request from '../utils/request';
// 创建任务
export const createTask = (name) => {
    return request({
        url: '/task/createTask',
        method: 'post',
        data: {
            name: name
        }
    });
};
// 获取任务列表
export const getTaskList = (page: number, limit: number, options?: {
    search?: string;
    status?: string;
    sort?: string;
    order?: string;
    start_time?: string;
    end_time?: string;
}) => {
    return request({
        url: '/task/tasklist',
        method: 'post',
        data: {
            page,
            limit,
            search: options?.search || null,
            status: options?.status || null,
            sort: options?.sort || null,
            order: options?.order || null,
            start_time: options?.start_time || null,
            end_time: options?.end_time || null,
        }
    });
}
// 删除任务
export const deleteTask = (id) => {
    return request({
        url: '/task/deletetask',
        method: 'post',
        data: {
            id: id 
        }
    });
}
// 更新任务
export const updateTask = (id,[name,status]) => {
    return request({
        url: '/task/updatetask',
        method: 'post',
        data: {
            id: id,
            name: name || null,
            status: status || null
        }
    });
}
// 任务操作上传文件
export const uploadTask = (task_id: number, files?: { [key: string]: File }) => {
    const formData = new FormData();
    formData.append('task_id', task_id.toString());
    
    if (files) {
        Object.entries(files).forEach(([key, file]) => {
            formData.append(key, file);
        });
    }

    return request({
        url: '/task/upload',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
}
// 获取任务详情
export const getTaskDetail = (task_id: string, page: number, limit: number, options?: {
    search?: string;
    sort?: string;
    order?: string;
}) => {
    return request({
        url: '/taskinfo/getTaskInfo',
        method: 'post',
        data: {
            task_id,
            page,
            limit,
            search: options?.search || null,
            sort: options?.sort || null,
            order: options?.order || null
        }
    });
}
// 执行工作流
export const workflow = (task_id, action, taskinfo_id?) => {
    return request({
        url: '/queue/queueAction',
        method: 'post',
        data: {
            task_id: task_id,
            action: action,
            taskinfo_id: taskinfo_id || null
        }
    });
};
// 检测进度
export const getFileProgress = (task_id,) => {
    return request({
        url: '/task/getFileProgress',
        method: 'post',
        data: {
            task_id: task_id,
        }
    });
};
// 转写进度
export const getFileTranscriptionProgress = (task_id,) => {
    return request({
        url: '/task/getFileTranscriptionProgress',
        method: 'post',
        data: {
            task_id: task_id,
        }
    });
};
// 任务详情统计
export const getTaskStatistics = (task_id,) => {
    return request({
        url: '/task/getTaskStatistics',
        method: 'post',
        data: {
            task_id: task_id,
        }
    });
};
// 获取子文件任务详情
export const getTaskFileDetail = (task_info_id,) => {
    return request({
        url: '/task/getTaskFileDetail',
        method: 'post',
        data: {
            task_info_id: task_info_id,
        }
    });
};