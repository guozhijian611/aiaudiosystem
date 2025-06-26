import axios, { AxiosInstance, AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import router from '../router';

const service: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8787',
  timeout: 60000,
});

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('请求拦截:', config.url);
    return config;
  },
  (error: AxiosError) => {
    console.error('请求错误:', error);
    return Promise.reject(error); // ❗建议传出 error，便于外层 catch 获取详情
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 处理业务层面的状态码
    if (response.data.code === 401) {
      // 清除本地存储的 token
      localStorage.removeItem('token');
      // 跳转到登录页
      router.push('/login');
      return Promise.reject(new Error('未授权，请重新登录'));
    }
    
    if (response.status === 200) {
      return response;
    } else {
      // ❗你原来的代码中 Promise.reject() 缺失 return，会导致无效
      return Promise.reject(new Error(`HTTP 状态码异常: ${response.status}`));
    }
  },
  (error: AxiosError) => {
    // ❗可加错误状态码处理逻辑
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 清除本地存储的 token
          localStorage.removeItem('token');
          // 跳转到登录页
          router.push('/login');
          return Promise.reject(new Error('未授权，请重新登录'));
        case 403:
          console.warn('无权限访问');
          break;
        case 500:
          console.warn('服务器错误');
          break;
      }
    }

    console.error('响应错误:', error);
    return Promise.reject(error);
  }
);

export default service;
