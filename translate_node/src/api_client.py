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
        # 数据验证和安全处理
        def safe_get_array(data, key, default=None):
            """安全获取数组，确保不为空"""
            value = data.get(key, default or [])
            if not isinstance(value, list):
                return []
            return value if value else []
        
        def safe_get_number(data, key, default=0):
            """安全获取数字，确保有效"""
            value = data.get(key, default)
            if value is None or (isinstance(value, (int, float)) and value <= 0):
                return default
            return value
        
        def safe_get_string(data, key, default=""):
            """安全获取字符串"""
            value = data.get(key, default)
            return str(value) if value is not None else default
        
        def clean_segments(segments):
            """清理segments数据，确保格式正确"""
            if not isinstance(segments, list):
                return []
            
            cleaned_segments = []
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                
                # 确保必要字段存在
                cleaned_segment = {
                    'text': safe_get_string(segment, 'text', ''),
                    'start': safe_get_number(segment, 'start', 0.0),
                    'end': safe_get_number(segment, 'end', 0.0)
                }
                
                # 处理words字段
                words = segment.get('words', [])
                if isinstance(words, list) and words:
                    cleaned_words = []
                    for word in words:
                        if isinstance(word, dict):
                            cleaned_word = {
                                'word': safe_get_string(word, 'word', ''),
                                'start': safe_get_number(word, 'start', 0.0),
                                'end': safe_get_number(word, 'end', 0.0),
                                'score': safe_get_number(word, 'score', 0.0)
                            }
                            cleaned_words.append(cleaned_word)
                    if cleaned_words:
                        cleaned_segment['words'] = cleaned_words
                
                # 处理speaker字段
                if 'speaker' in segment and segment['speaker']:
                    cleaned_segment['speaker'] = safe_get_string(segment, 'speaker', '')
                
                cleaned_segments.append(cleaned_segment)
            
            return cleaned_segments
        
        # 安全获取和处理数据
        text = safe_get_string(transcribe_result, 'text', '')
        segments = clean_segments(transcribe_result.get('segments', []))
        speakers = safe_get_array(transcribe_result, 'speakers', [])
        
        # 如果speakers为空，添加默认值避免PHP访问空数组
        if not speakers:
            speakers = ['UNKNOWN']
        
        # 计算有效的confidence_avg
        confidence_avg = safe_get_number(transcribe_result, 'confidence_avg', 0.0)
        if confidence_avg <= 0:
            # 从segments中重新计算
            confidences = []
            for segment in segments:
                if 'words' in segment:
                    for word in segment['words']:
                        score = word.get('score', 0)
                        if score > 0:
                            confidences.append(score)
            confidence_avg = sum(confidences) / len(confidences) if confidences else 0.85
        
        # 构建完整的转写详情
        transcribe_details = {
            'text': text,
            'segments_count': len(segments),
            'confidence_avg': round(confidence_avg, 3),
            'word_count': len(text.split()) if text else 0,
            'speakers': speakers,
            'segments': segments,
            'processing_time': safe_get_number(transcribe_result, 'processing_time', 0.0),
            'file_info': transcribe_result.get('file_info', {}),
            'model_info': {
                'whisper_model': safe_get_string(transcribe_result, 'whisper_model', 'unknown'),
                'language_detected': safe_get_string(transcribe_result, 'language', 'unknown'),
                'compute_device': safe_get_string(transcribe_result, 'compute_device', 'unknown'),
                'alignment_enabled': bool(transcribe_result.get('alignment_enabled', False)),
                'diarization_enabled': bool(transcribe_result.get('diarization_enabled', False))
            }
        }
        
        # 准备回调数据
        callback_data = {
            'text_info': transcribe_details,
            'effective_voice': safe_get_number(transcribe_result, 'effective_voice', 0.0),
            'total_voice': safe_get_number(transcribe_result, 'total_voice', 0.0),
            'language': safe_get_string(transcribe_result, 'language', 'unknown'),
            'transcribe_details': transcribe_details
        }
        
        # 记录回调数据大小
        callback_json = json.dumps(callback_data, ensure_ascii=False)
        data_size = len(callback_json.encode('utf-8'))
        logger.info(f"回调数据大小: {data_size} bytes ({data_size/1024:.1f} KB)")
        
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