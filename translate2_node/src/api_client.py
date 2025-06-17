#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API客户端模块
负责与后端API进行通信，包括文件上传、回调通知等
"""

import os
import json
import requests
import time
from pathlib import Path
from logger import logger

# 添加项目路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class APIClient:
    """API客户端类"""
    
    def __init__(self):
        """初始化API客户端"""
        self.config = Config()
        self.session = requests.Session()
        
        # 设置请求超时
        self.session.timeout = 60
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Translate2Node/1.0.0',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"API客户端初始化完成: {self.config.API_BASE_URL}")
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.session.get(
                self.config.API_BASE_URL,
                timeout=10
            )
            return response.status_code < 500
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
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
            
            response = self.session.get(url, timeout=self.config.DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件下载是否完整
            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                raise Exception("下载的文件为空或不存在")
            
            file_size = os.path.getsize(local_path)
            logger.info(f"文件下载成功: {local_path} (大小: {self._format_size(file_size)})")
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
    
    def upload_file(self, file_path: str, task_id: int) -> bool:
        """
        上传文件到后端
        
        Args:
            file_path (str): 本地文件路径
            task_id (int): 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            logger.info(f"开始上传文件: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'task_id': task_id}
                
                response = self.session.post(
                    self.config.upload_url,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('code') == 200:
                    logger.info(f"文件上传成功: {file_path}")
                    return True
                else:
                    logger.error(f"文件上传失败: {result.get('msg', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return False
    
    def send_processing_callback(self, task_id: int) -> bool:
        """
        发送处理中回调
        
        Args:
            task_id (int): 任务ID
            
        Returns:
            bool: 是否成功
        """
        return self._send_callback({
            'task_id': task_id,
            'task_type': 2,  # 转写任务类型
            'status': 'processing',
            'message': '音频转写处理中...'
        })
    
    def send_success_callback(self, task_id: int, result: dict) -> bool:
        """
        发送成功回调
        
        Args:
            task_id (int): 任务ID
            result (dict): 转写结果
            
        Returns:
            bool: 是否成功
        """
        return self._send_callback({
            'task_id': task_id,
            'task_type': 2,  # 转写任务类型
            'status': 'success',
            'message': '音频转写完成',
            'data': result
        })
    
    def send_failed_callback(self, task_id: int, error_message: str) -> bool:
        """
        发送失败回调
        
        Args:
            task_id (int): 任务ID
            error_message (str): 错误信息
            
        Returns:
            bool: 是否成功
        """
        return self._send_callback({
            'task_id': task_id,
            'task_type': 2,  # 转写任务类型
            'status': 'failed',
            'message': error_message
        })
    
    def _send_callback(self, payload: dict) -> bool:
        """
        发送回调请求
        
        Args:
            payload (dict): 回调数据
            
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
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}" 