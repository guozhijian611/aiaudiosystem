#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """快速识别节点配置类"""
    
    # ==================== RabbitMQ配置 ====================
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', '10.0.0.130')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    
    # 队列名称和配置
    QUEUE_FAST_PROCESS = os.getenv('QUEUE_FAST_PROCESS', 'fast_process_queue')
    QUEUE_TTL = int(os.getenv('QUEUE_TTL', 3600000))  # 队列消息TTL (毫秒)
    QUEUE_DURABLE = os.getenv('QUEUE_DURABLE', 'true').lower() == 'true'
    
    # ==================== API配置 ====================
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://10.0.0.130:8787')
    API_CALLBACK_URL = f"{API_BASE_URL}/queue/handleTaskCallback"
    
    # ==================== VAD模型配置 ====================
    # 使用FunASR的VAD模型
    VAD_MODEL = os.getenv('VAD_MODEL', 'fsmn-vad')
    VAD_MODEL_REVISION = os.getenv('VAD_MODEL_REVISION', 'v2.0.4')
    
    # 模型参数
    VAD_MAX_END_SILENCE_TIME = int(os.getenv('VAD_MAX_END_SILENCE_TIME', 800))  # 最大结束静音时间(ms)
    VAD_MAX_START_SILENCE_TIME = int(os.getenv('VAD_MAX_START_SILENCE_TIME', 3000))  # 最大开始静音时间(ms)
    VAD_MIN_SPEECH_DURATION = int(os.getenv('VAD_MIN_SPEECH_DURATION', 250))  # 最小语音持续时间(ms)
    
    # 模型缓存配置
    MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', './models')
    DISABLE_UPDATE = os.getenv('DISABLE_UPDATE', 'true').lower() == 'true'
    
    # ==================== 文件处理配置 ====================
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    WORK_DIR = os.getenv('WORK_DIR', './work')
    
    # 支持的音频格式
    SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
    
    # ==================== 日志配置 ====================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/quick_node.log')
    
    # ==================== 其他配置 ====================
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))  # 最大并发处理数
    DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', 300))  # 下载超时时间(秒)
    PROCESS_TIMEOUT = int(os.getenv('PROCESS_TIMEOUT', 600))  # 处理超时时间(秒)
    
    @classmethod
    def validate_config(cls):
        """验证配置有效性"""
        required_dirs = [cls.TEMP_DIR, cls.WORK_DIR, cls.MODEL_CACHE_DIR, os.path.dirname(cls.LOG_FILE)]
        for dir_path in required_dirs:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        
        return True 