#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
import json
import time
import os
import sys
import traceback
from pathlib import Path
from logger import logger

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from api_client import APIClient
from transcriber import WhisperXTranscriber

class QueueConsumer:
    """队列消费者 - 处理文本转写任务"""
    
    def __init__(self):
        """初始化队列消费者"""
        self.config = Config()
        self.api_client = APIClient()
        self.transcriber = None
        self.connection = None
        self.channel = None
        
        # 创建工作目录
        os.makedirs(self.config.WORK_DIR, exist_ok=True)
        os.makedirs(self.config.TEMP_DIR, exist_ok=True)
        os.makedirs('./logs', exist_ok=True)
        os.makedirs(self.config.MODEL_CACHE_DIR, exist_ok=True)
        
        logger.info(f"队列消费者初始化完成: {self.config.QUEUE_NAME}")
        logger.info(f"工作目录: {self.config.WORK_DIR}")
        logger.info(f"临时目录: {self.config.TEMP_DIR}")
    
    def _init_transcriber(self):
        """延迟初始化转写器"""
        if self.transcriber is None:
            logger.info("正在初始化WhisperX转写器...")
            self.transcriber = WhisperXTranscriber()
            logger.info("WhisperX转写器初始化完成")
    
    def connect_rabbitmq(self):
        """连接RabbitMQ"""
        try:
            logger.info(f"正在连接RabbitMQ服务器: {self.config.RABBITMQ_HOST}:{self.config.RABBITMQ_PORT}")
            
            credentials = pika.PlainCredentials(
                self.config.RABBITMQ_USERNAME,
                self.config.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.RABBITMQ_HOST,
                port=self.config.RABBITMQ_PORT,
                virtual_host=self.config.RABBITMQ_VIRTUAL_HOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # 声明队列（与后端保持一致的参数）
            queue_arguments = {
                'x-message-ttl': self.config.QUEUE_TTL,  # 消息TTL
                'x-max-priority': 10,                    # 支持优先级
                'x-dead-letter-exchange': 'task_dlx',    # 死信交换机
                'x-dead-letter-routing-key': 'dead_letter'  # 死信路由键
            }
            
            self.channel.queue_declare(
                queue=self.config.QUEUE_NAME,
                durable=self.config.QUEUE_DURABLE,
                arguments=queue_arguments
            )
            
            # 设置QoS
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"RabbitMQ连接成功: 队列={self.config.QUEUE_NAME}")
            
        except Exception as e:
            logger.error(f"RabbitMQ连接失败: {e}")
            raise
    
    def disconnect_rabbitmq(self):
        """断开RabbitMQ连接"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("RabbitMQ连接已断开")
        except Exception as e:
            logger.error(f"断开RabbitMQ连接时出错: {e}")
    
    def process_message(self, channel, method, properties, body):
        """处理消息"""
        task_id = None
        start_time = time.time()
        
        try:
            # 解析消息
            message = json.loads(body.decode())
            logger.info(f"收到队列消息: {message}")
            
            # 获取task_info数据（新格式）
            task_info = message.get('task_info', {})
            
            if not task_info or not isinstance(task_info, dict):
                raise ValueError("消息格式错误：缺少task_info字段或格式不正确")
            
            # 从task_info中获取数据
            task_id = task_info.get('id')
            if not task_id:
                raise ValueError("task_info中缺少id字段")
            
            # translate_node使用clear_url（降噪后的音频URL）
            voice_url = task_info.get('clear_url')
            if not voice_url:
                raise ValueError("task_info中缺少clear_url字段，请先完成音频降噪")
            
            logger.info(f"收到转写任务: task_id={task_id}, clear_url={voice_url}")
            logger.info(f"任务详情: 文件名={task_info.get('filename', 'N/A')}, "
                       f"是否已降噪={task_info.get('is_clear', 0)}")
            
            # 发送处理中回调
            self.api_client.send_processing_callback(task_id)
            
            # 初始化转写器（延迟初始化）
            self._init_transcriber()
            
            # 下载音频文件
            audio_file_path = self._download_audio(voice_url, task_id)
            
            try:
                # 执行音频转写
                logger.info(f"开始转写任务: {task_id}")
                transcribe_result = self.transcriber.transcribe_audio(
                    audio_file_path,
                    timeout=self.config.PROCESSING_TIMEOUT
                )
                
                # 发送成功回调
                self.api_client.send_success_callback(task_id, transcribe_result)
                
                # 记录处理成功
                process_time = time.time() - start_time
                logger.info(f"任务 {task_id} 转写成功，总耗时: {process_time:.1f}秒")
                
                # 确认消息
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
            finally:
                # 清理临时文件
                self._cleanup_files(audio_file_path)
            
        except Exception as e:
            error_message = f"任务处理失败: {str(e)}"
            logger.error(f"任务 {task_id} 处理失败: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 发送失败回调
            if task_id:
                self.api_client.send_failed_callback(task_id, error_message)
            
            # 确认消息（避免重复处理）
            channel.basic_ack(delivery_tag=method.delivery_tag)
    
    def _download_audio(self, voice_url: str, task_id: int) -> str:
        """下载音频文件"""
        try:
            # 生成本地文件路径
            file_extension = self._get_file_extension(voice_url)
            local_filename = f"task_{task_id}_audio{file_extension}"
            local_path = os.path.join(self.config.TEMP_DIR, local_filename)
            
            logger.info(f"正在下载音频文件: {voice_url} -> {local_path}")
            
            # 下载文件
            success = self.api_client.download_file(voice_url, local_path)
            if not success:
                raise Exception("音频文件下载失败")
            
            # 验证文件存在且大小合理
            if not os.path.exists(local_path):
                raise Exception("下载的音频文件不存在")
            
            file_size = os.path.getsize(local_path)
            if file_size == 0:
                raise Exception("下载的音频文件为空")
            
            logger.info(f"音频文件下载成功: {local_path}, 大小: {self.api_client.get_file_size_str(file_size)}")
            return local_path
            
        except Exception as e:
            logger.error(f"音频文件下载失败: {e}")
            raise
    
    def _get_file_extension(self, url: str) -> str:
        """从URL中提取文件扩展名"""
        try:
            # 从URL中提取文件名
            path = url.split('?')[0]  # 去除查询参数
            filename = os.path.basename(path)
            
            if '.' in filename:
                return os.path.splitext(filename)[1]
            else:
                return '.wav'  # 默认扩展名
                
        except:
            return '.wav'  # 默认扩展名
    
    def _cleanup_files(self, *file_paths):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"已清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理文件失败: {file_path}, 错误: {e}")
    
    def start_consuming(self):
        """开始消费消息"""
        try:
            # 连接RabbitMQ
            self.connect_rabbitmq()
            
            # 设置消费者
            self.channel.basic_consume(
                queue=self.config.QUEUE_NAME,
                on_message_callback=self.process_message
            )
            
            logger.info(f"开始监听队列: {self.config.QUEUE_NAME}")
            logger.info("等待消息中... 按 CTRL+C 退出")
            
            # 开始消费
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在停止消费者...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"消费者运行异常: {e}")
            raise
    
    def stop_consuming(self):
        """停止消费消息"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            self.disconnect_rabbitmq()
            logger.info("消费者已停止")
        except Exception as e:
            logger.error(f"停止消费者时出错: {e}")
    
    def get_status(self) -> dict:
        """获取消费者状态"""
        return {
            'queue_name': self.config.QUEUE_NAME,
            'rabbitmq_host': self.config.RABBITMQ_HOST,
            'rabbitmq_port': self.config.RABBITMQ_PORT,
            'work_dir': self.config.WORK_DIR,
            'temp_dir': self.config.TEMP_DIR,
            'connection_status': 'connected' if (self.connection and not self.connection.is_closed) else 'disconnected',
            'transcriber_status': 'initialized' if self.transcriber else 'not_initialized',
            'transcriber_model': self.transcriber.get_model_info() if self.transcriber else None
        }

def main():
    """主函数"""
    try:
        # 显示配置信息
        config = Config()
        logger.info("Translate Node 启动")
        logger.info(str(config))
        
        # 创建消费者
        consumer = QueueConsumer()
        
        # 显示状态
        status = consumer.get_status()
        logger.info(f"消费者状态: {status}")
        
        # 开始消费
        consumer.start_consuming()
        
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 