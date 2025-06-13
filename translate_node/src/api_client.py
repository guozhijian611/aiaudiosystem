#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import sys
from pathlib import Path
from logger import logger

# 添加项目路径
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
            task_type (int): 任务类型 (4=文本转写)
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
                'data': data or {},
                'node_type': 'translate_node'
            }
            
            logger.info(f"发送回调通知: 任务ID={task_id}, 类型={task_type}, 状态={status}")
            
            response = self.session.post(
                self.config.API_CALLBACK_URL,
                json=callback_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 检查业务层面的响应状态
            if result.get('code') == 401:
                logger.warning(f"回调认证失败，但继续处理: {result}")
                return result  # 不抛出异常，认证问题不影响业务流程
            elif result.get('code') != 200 and result.get('code') is not None:
                logger.warning(f"回调业务错误: {result}")
                return result  # 记录但不中断处理
            
            logger.info(f"回调通知发送成功: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"发送回调通知失败: {e}")
            # 回调失败不应该中断任务处理
            return {'code': 500, 'msg': f'回调网络错误: {str(e)}'}
        except Exception as e:
            logger.error(f"回调处理异常: {e}")
            return {'code': 500, 'msg': f'回调处理异常: {str(e)}'}
    
    def send_processing_callback(self, task_id: int) -> dict:
        """发送处理中回调"""
        return self.send_callback(task_id, 4, 'processing')
    
    def send_success_callback(self, task_id: int, transcribe_result: dict) -> dict:
        """
        发送成功回调
        
        Args:
            task_id (int): 任务ID
            transcribe_result (dict): 转写结果
        """
        # 准备回调数据
        callback_data = {
            'text_info': transcribe_result.get('text', ''),                    # 转写文本
            'effective_voice': transcribe_result.get('effective_voice', 0),    # 有效语音时长
            'total_voice': transcribe_result.get('total_voice', 0),            # 音频总时长
            'language': transcribe_result.get('language', 'unknown'),          # 识别的语言
            'transcribe_details': {
                'segments_count': transcribe_result.get('segments_count', 0),
                'confidence_avg': transcribe_result.get('confidence_avg', 0),
                'word_count': transcribe_result.get('word_count', 0),
                'speakers': transcribe_result.get('speakers', []),
                'segments': transcribe_result.get('segments', [])
            }
        }
        
        return self.send_callback(task_id, 4, 'success', callback_data)
    
    def send_failed_callback(self, task_id: int, error_message: str) -> dict:
        """发送失败回调"""
        callback_data = {
            'error_message': error_message
        }
        return self.send_callback(task_id, 4, 'failed', callback_data)
    
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
    
    def upload_file(self, file_path: str, task_type: int = 4) -> dict:
        """
        上传文件到服务器
        
        Args:
            file_path (str): 本地文件路径
            task_type (int): 任务类型，默认4（文本转写）
            
        Returns:
            dict: 上传结果
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            logger.info(f"开始上传文件: {file_path}")
            
            # 准备文件和数据
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
                data = {'task_type': task_type}
                
                response = self.session.post(
                    self.config.upload_url,
                    files=files,
                    data=data,
                    timeout=300  # 上传超时5分钟
                )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                logger.info(f"文件上传成功: {result}")
                return result
            else:
                logger.error(f"文件上传失败: {result}")
                return result
                
        except Exception as e:
            logger.error(f"文件上传异常: {e}")
            return {'code': 500, 'msg': f'上传失败: {str(e)}'}
    
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