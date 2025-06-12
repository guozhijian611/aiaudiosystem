#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class APIClient:
    """API客户端 - 处理与后端API的通信"""
    
    def __init__(self):
        """初始化API客户端"""
        self.config = Config()
        self.session = requests.Session()
        self.session.timeout = 30
    
    def send_callback(self, task_id: int, task_type: int, status: str, data: dict = None) -> dict:
        """
        发送任务回调通知
        
        Args:
            task_id (int): 任务ID
            task_type (int): 任务类型 (3=快速识别)
            status (str): 任务状态 ('processing', 'success', 'failed')
            data (dict): 回调数据
            
        Returns:
            dict: API响应结果
        """
        try:
            callback_data = {
                'task_id': task_id,
                'task_type': task_type,
                'status': status,
                'data': data or {}
            }
            
            logger.info(f"发送回调通知: 任务ID={task_id}, 类型={task_type}, 状态={status}")
            
            response = self.session.post(
                self.config.API_CALLBACK_URL,
                json=callback_data,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"回调通知发送成功: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"发送回调通知失败: {e}")
            raise
        except Exception as e:
            logger.error(f"回调处理异常: {e}")
            raise
    
    def send_processing_callback(self, task_id: int) -> dict:
        """发送处理中回调"""
        return self.send_callback(task_id, 3, 'processing')
    
    def send_success_callback(self, task_id: int, analysis_result: dict) -> dict:
        """
        发送成功回调
        
        Args:
            task_id (int): 任务ID
            analysis_result (dict): VAD分析结果
        """
        # 准备回调数据
        callback_data = {
            'total_voice': analysis_result.get('total_duration', 0),      # 音频总时长
            'effective_voice': analysis_result.get('effective_duration', 0),  # 有效语音时长
            'speech_ratio': analysis_result.get('speech_ratio', 0),       # 语音占比
            'speech_segments_count': analysis_result.get('speech_segments_count', 0),  # 语音段落数
            'analysis_details': {
                'silence_duration': analysis_result.get('silence_duration', 0),
                'file_info': analysis_result.get('file_info', {}),
                'speech_segments': analysis_result.get('speech_segments', [])
            }
        }
        
        return self.send_callback(task_id, 3, 'success', callback_data)
    
    def send_failed_callback(self, task_id: int, error_message: str) -> dict:
        """发送失败回调"""
        callback_data = {
            'error_message': error_message
        }
        return self.send_callback(task_id, 3, 'failed', callback_data)
    
    def download_file(self, url: str, local_path: str) -> bool:
        """
        下载文件
        
        Args:
            url (str): 文件URL
            local_path (str): 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            logger.info(f"开始下载文件: {url} -> {local_path}")
            
            response = self.session.get(url, stream=True, timeout=self.config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            # 确保目录存在
            import os
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 写入文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            file_size = os.path.getsize(local_path)
            logger.info(f"文件下载成功: {local_path}, 大小: {file_size} bytes")
            
            return True
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return False
    
    def get_file_size_str(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB" 