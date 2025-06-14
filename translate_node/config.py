"""
Translate Node 配置管理模块
负责加载和管理文本转写节点的所有配置项
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # RabbitMQ配置
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_VIRTUAL_HOST = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
    
    # 队列名称
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'transcribe_queue')
    
    # 后端API配置
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8787')
    API_UPLOAD_ENDPOINT = os.getenv('API_UPLOAD_ENDPOINT', '/queue/upload')
    API_CALLBACK_ENDPOINT = os.getenv('API_CALLBACK_ENDPOINT', '/queue/callback')
    
    # 工作目录配置
    default_work_dir = './work' if not os.path.exists('/app') else '/app/work'
    default_temp_dir = './temp' if not os.path.exists('/app') else '/app/temp'
    WORK_DIR = os.getenv('WORK_DIR', default_work_dir)
    TEMP_DIR = os.getenv('TEMP_DIR', default_temp_dir)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # WhisperX转写配置
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'large-v3')  # 默认使用large-v3模型
    WHISPER_LANGUAGE = os.getenv('WHISPER_LANGUAGE', 'auto')  # 自动检测语言
    WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'auto')  # 自动选择设备
    WHISPER_BATCH_SIZE = int(os.getenv('WHISPER_BATCH_SIZE', 16))  # 批处理大小
    WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'auto')  # 计算精度，auto为自动选择
    
    # 说话人分离配置
    ENABLE_DIARIZATION = os.getenv('ENABLE_DIARIZATION', 'true').lower() == 'true'
    DIARIZATION_MODEL = os.getenv('DIARIZATION_MODEL', 'pyannote/speaker-diarization-3.1')
    HF_TOKEN = os.getenv('HF_TOKEN', '')  # Hugging Face Token，用于说话人分离
    MIN_SPEAKERS = int(os.getenv('MIN_SPEAKERS', 1))
    MAX_SPEAKERS = int(os.getenv('MAX_SPEAKERS', 10))
    
    # 语言对齐配置
    ENABLE_ALIGNMENT = os.getenv('ENABLE_ALIGNMENT', 'true').lower() == 'true'
    ALIGNMENT_MODEL = os.getenv('ALIGNMENT_MODEL', 'WAV2VEC2_ASR_LARGE_LV60K_960H')
    
    # 处理限制配置
    MAX_AUDIO_DURATION = int(os.getenv('MAX_AUDIO_DURATION', 3600))  # 最大音频时长（秒），默认1小时
    PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', 7200))  # 处理超时（秒），默认2小时
    CHUNK_DURATION = int(os.getenv('CHUNK_DURATION', 600))  # 分块处理时长（秒），默认10分钟
    
    # 输出格式配置
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'json')  # 输出格式: json, srt, vtt, txt
    INCLUDE_TIMESTAMPS = os.getenv('INCLUDE_TIMESTAMPS', 'true').lower() == 'true'
    INCLUDE_CONFIDENCE = os.getenv('INCLUDE_CONFIDENCE', 'true').lower() == 'true'
    
    # 模型缓存配置
    MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', './models')
    DISABLE_UPDATE = os.getenv('DISABLE_UPDATE', 'true').lower() == 'true'
    
    # 队列配置
    QUEUE_TTL = int(os.getenv('QUEUE_TTL', 3600000))  # 消息TTL（毫秒）
    QUEUE_DURABLE = os.getenv('QUEUE_DURABLE', 'true').lower() == 'true'
    
    # 其他配置
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 1))  # 最大并发数
    DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', 300))  # 下载超时
    
    # WhisperX路径配置
    WHISPERX_PATH = os.getenv('WHISPERX_PATH', './whisperX')
    
    @property
    def upload_url(self):
        """获取上传接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_UPLOAD_ENDPOINT}"
    
    @property
    def callback_url(self):
        """获取回调接口完整URL"""
        return f"{self.API_BASE_URL}{self.API_CALLBACK_ENDPOINT}"
    
    @property
    def API_CALLBACK_URL(self):
        """兼容性属性，供API客户端使用"""
        return self.callback_url
    
    def __str__(self):
        """配置信息字符串表示"""
        return f"""Translate Node 配置信息:
        RabbitMQ: {self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}
        队列名称: {self.QUEUE_NAME}
        API地址: {self.API_BASE_URL}
        工作目录: {self.WORK_DIR}
        临时目录: {self.TEMP_DIR}
        Whisper模型: {self.WHISPER_MODEL}
        语言检测: {self.WHISPER_LANGUAGE}
        设备: {self.WHISPER_DEVICE}
        说话人分离: {self.ENABLE_DIARIZATION}
        语言对齐: {self.ENABLE_ALIGNMENT}
        输出格式: {self.OUTPUT_FORMAT}
        """ 