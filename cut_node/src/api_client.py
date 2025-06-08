"""
API客户端模块
负责与后端队列系统通信
"""

import requests
import os
from typing import Dict, Any
from config import Config
from logger import logger

class APIClient:
    """API客户端，用于与后端通信"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        # 设置请求超时
        self.session.timeout = 300  # 5分钟
        
    def upload_file(self, file_path: str, task_type: int = 1) -> Dict[str, Any]:
        """
        上传文件到后端
        
        Args:
            file_path (str): 文件路径
            task_type (int): 任务类型 (1: 音频提取)
            
        Returns:
            Dict[str, Any]: 上传结果
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 准备文件上传
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                data = {'task_type': task_type}
                
                logger.info(f"开始上传文件: {file_path} 到 {self.config.upload_url}")
                
                response = self.session.post(
                    self.config.upload_url,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                # 检查响应状态
                if response.status_code != 200:
                    raise Exception(f"HTTP错误: {response.status_code}, {response.text}")
                
                # 解析响应
                result = response.json()
                if result.get('code') != 200:
                    raise Exception(f"上传失败: {result.get('msg', 'Unknown error')}")
                
                logger.info(f"文件上传成功: {result.get('data', {}).get('file_info', {}).get('url', 'N/A')}")
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            raise Exception(f"网络请求失败: {e}")
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def callback_success(self, task_id: int, task_type: int, data: Dict[str, Any]) -> bool:
        """
        发送成功回调
        
        Args:
            task_id (int): 任务ID
            task_type (int): 任务类型
            data (Dict[str, Any]): 结果数据
            
        Returns:
            bool: 是否成功
        """
        payload = {
            'task_id': task_id,
            'task_type': task_type,
            'status': 'success',
            'data': data
        }
        
        return self._send_callback(payload)
    
    def callback_failed(self, task_id: int, task_type: int, message: str) -> bool:
        """
        发送失败回调
        
        Args:
            task_id (int): 任务ID
            task_type (int): 任务类型
            message (str): 错误信息
            
        Returns:
            bool: 是否成功
        """
        payload = {
            'task_id': task_id,
            'task_type': task_type,
            'status': 'failed',
            'message': message
        }
        
        return self._send_callback(payload)
    
    def _send_callback(self, payload: Dict[str, Any]) -> bool:
        """
        发送回调请求
        
        Args:
            payload (Dict[str, Any]): 回调数据
            
        Returns:
            bool: 是否成功
        """
        try:
            logger.info(f"发送回调: {payload}")
            
            response = self.session.post(
                self.config.callback_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"回调HTTP错误: {response.status_code}, {response.text}")
                return False
            
            # 解析响应
            result = response.json()
            if result.get('code') != 200:
                logger.error(f"回调业务错误: {result.get('msg', 'Unknown error')}")
                return False
            
            logger.info("回调发送成功")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"回调网络请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"回调发送失败: {e}")
            return False
    
    def download_file(self, url: str, local_path: str) -> bool:
        """
        下载文件到本地
        
        Args:
            url (str): 文件URL
            local_path (str): 本地保存路径
            
        Returns:
            bool: 是否成功
        """
        try:
            logger.info(f"开始下载文件: {url} -> {local_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            response = self.session.get(url, timeout=300, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件下载是否完整
            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                raise Exception("下载的文件为空或不存在")
            
            logger.info(f"文件下载成功: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            # 清理可能存在的不完整文件
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except:
                    pass
            return False
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 后端是否可用
        """
        try:
            # 简单的健康检查，可以ping后端基础URL
            response = self.session.get(
                self.config.API_BASE_URL,
                timeout=10
            )
            return response.status_code < 500
        except:
            return False 