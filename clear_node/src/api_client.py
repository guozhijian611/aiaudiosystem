"""
API客户端模块
负责与后端API进行通信
"""

import requests
import json
import os
from typing import Dict, Any, Optional
from config import Config
from logger import logger

class APIClient:
    """API客户端"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        # 设置请求超时
        self.timeout = 30
        
    def upload_file(self, file_path: str, task_type: int = 2) -> Dict[str, Any]:
        """
        上传文件到后端
        
        Args:
            file_path (str): 文件路径
            task_type (int): 任务类型（2=音频降噪）
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 准备文件
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'audio/wav')
                }
                
                # 准备数据
                data = {
                    'task_type': task_type,
                    'node_type': 'clear_node'
                }
                
                logger.info(f"开始上传文件: {file_path} -> {self.config.upload_url}")
                
                # 发送请求
                response = self.session.post(
                    self.config.upload_url,
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                # 检查响应
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"文件上传成功: {result}")
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"上传文件网络错误: {e}")
            raise
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            raise
    
    def send_callback(self, task_id: str = None, task_type: int = 2, status: str = '', 
                     message: str = '', data: Dict = None, 
                     # 兼容旧参数
                     task_number: str = None, file_url: str = '', extra_data: Dict = None) -> Dict[str, Any]:
        """
        发送回调通知 - 支持新旧两种格式
        
        新格式参数:
            task_id (str): 任务ID
            task_type (int): 任务类型（2=音频降噪）
            status (str): 任务状态 (processing/success/failed)
            message (str): 状态消息
            data (Dict): 回调数据
            
        旧格式参数（兼容性）:
            task_number (str): 任务编号
            file_url (str): 处理后的文件URL
            extra_data (Dict): 额外数据
            
        Returns:
            Dict[str, Any]: 回调结果
        """
        try:
            # 优先使用新格式
            if task_id and task_type:
                # 新格式回调
                callback_data = {
                    'task_id': task_id,
                    'task_type': task_type,
                    'status': status,
                    'message': message,
                    'data': data or {},
                    'timestamp': self._get_timestamp(),
                    'node_type': 'clear_node'
                }
                
                logger.info(f"发送新格式回调通知: 任务ID={task_id}, 类型={task_type}, 状态={status}")
                
            else:
                # 旧格式回调（兼容性）
                callback_data = {
                    'task_number': task_number,
                    'node_type': 'clear_node',
                    'status': status,
                    'message': message,
                    'file_url': file_url,
                    'timestamp': self._get_timestamp()
                }
                
                # 添加额外数据
                if extra_data:
                    callback_data.update(extra_data)
                
                logger.info(f"发送旧格式回调通知: 任务编号={task_number}, 状态={status}")
            
            # 发送请求
            response = self.session.post(
                self.config.callback_url,
                json=callback_data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            # 检查响应
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"回调通知发送成功: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"发送回调网络错误: {e}")
            raise
        except Exception as e:
            logger.error(f"发送回调失败: {e}")
            raise
    
    def download_file(self, file_url: str, local_path: str) -> bool:
        """
        下载文件
        
        Args:
            file_url (str): 文件URL
            local_path (str): 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            logger.info(f"开始下载文件: {file_url} -> {local_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 下载文件
            response = self.session.get(file_url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 保存文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件
            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                raise Exception("下载的文件为空或不存在")
            
            file_size = os.path.getsize(local_path)
            logger.info(f"文件下载成功: {local_path}, 大小: {file_size} bytes")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载文件网络错误: {e}")
            return False
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return False
    
    def get_task_info(self, task_number: str) -> Dict[str, Any]:
        """
        获取任务信息
        
        Args:
            task_number (str): 任务编号
            
        Returns:
            Dict[str, Any]: 任务信息
        """
        try:
            url = f"{self.config.API_BASE_URL}/task/getTaskInfo"
            data = {'task_number': task_number}
            
            logger.info(f"获取任务信息: {task_number}")
            
            response = self.session.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"任务信息获取成功: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取任务信息网络错误: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务信息失败: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否正常
        """
        try:
            url = f"{self.config.API_BASE_URL}/health"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳
        
        Returns:
            str: ISO格式时间戳
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """
        关闭会话
        """
        if self.session:
            self.session.close()
            logger.info("API客户端会话已关闭")