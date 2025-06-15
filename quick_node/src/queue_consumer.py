#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import pika
import shutil
from pathlib import Path
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import sys

# 添加本地FunASR路径
current_dir = os.path.dirname(__file__)
funasr_path = os.path.join(os.path.dirname(current_dir), 'FunASR')
if os.path.exists(funasr_path):
    sys.path.insert(0, funasr_path)

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from vad_analyzer import VADAnalyzer
from api_client import APIClient

class QueueConsumer:
    """快速识别队列消费者"""
    
    def __init__(self):
        """初始化队列消费者"""
        self.config = Config()
        self.vad_analyzer = VADAnalyzer()
        self.api_client = APIClient()
        self.connection = None
        self.channel = None
        
        # 验证配置
        self.config.validate_config()
        
        # 初始化日志
        self._setup_logging()
        
        # 连接RabbitMQ
        self._connect_rabbitmq()
    
    def _setup_logging(self):
        """设置日志配置"""
        # 创建logs目录
        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            os.path.join(log_dir, "quick_node.log"),
            rotation="10 MB",
            retention="7 days",
            level=self.config.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss,SSS} - quick_node - {level} - {message}"
        )
        
        logger.info("=" * 50)
        logger.info("快速识别节点启动")
        logger.info(f"VAD模型: {self.config.VAD_MODEL}")
        logger.info(f"队列名称: {self.config.QUEUE_NAME}")
        logger.info(f"API回调地址: {self.config.API_CALLBACK_URL}")
    
    def _connect_rabbitmq(self):
        """连接RabbitMQ"""
        try:
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
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # 声明队列（与其他节点保持一致的配置）
            queue_arguments = {
                'x-message-ttl': self.config.QUEUE_TTL,  # 消息TTL
                'x-max-priority': 10,      # 支持优先级
                'x-dead-letter-exchange': 'task_dlx',
                'x-dead-letter-routing-key': 'dead_letter'
            }
            
            self.channel.queue_declare(
                queue=self.config.QUEUE_NAME, 
                durable=self.config.QUEUE_DURABLE,
                arguments=queue_arguments
            )
            
            # 设置预取数量（一次只处理一个任务）
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"成功连接到RabbitMQ: {self.config.RABBITMQ_HOST}:{self.config.RABBITMQ_PORT}")
            
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            raise
    
    def start_consuming(self):
        """开始消费队列消息"""
        try:
            logger.info("开始消费队列消息...")
            
            # 设置消费者
            self.channel.basic_consume(
                queue=self.config.QUEUE_NAME,
                on_message_callback=self.process_message,
                auto_ack=False
            )
            
            logger.info(f"开始监听队列: {self.config.QUEUE_NAME}")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"消费队列异常: {e}")
            raise
    
    def stop_consuming(self):
        """停止消费队列"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        logger.info("队列消费已停止")
    
    def process_message(self, ch, method, properties, body):
        """处理队列消息"""
        try:
            # 解析消息
            message_data = json.loads(body.decode('utf-8'))
            logger.info(f"收到快速识别任务: {message_data}")
            
            # 提取任务信息
            task_info = message_data.get('task_info', {})
            task_id = task_info.get('id')
            
            if not task_id:
                logger.error("消息中缺少任务ID")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # 处理任务
            result = self._process_vad_task(task_info)
            
            if result['success']:
                logger.info(f"任务 {task_id}: 快速识别完成")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.error(f"任务 {task_id}: 快速识别失败 - {result['error']}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except json.JSONDecodeError as e:
            logger.error(f"消息格式错误: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"处理消息异常: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def _process_vad_task(self, task_info: dict) -> dict:
        """
        处理VAD分析任务
        
        Args:
            task_info (dict): 任务信息
            
        Returns:
            dict: 处理结果 {'success': bool, 'data': dict, 'error': str}
        """
        task_id = task_info.get('id')
        start_time = time.time()
        
        try:
            logger.info(f"任务 {task_id}: 开始快速识别处理")
            
            # 发送处理中回调
            self.api_client.send_processing_callback(task_id)
            
            # quick_node使用clear_url（降噪后的音频URL）
            file_url = task_info.get('voice_url')
            if not file_url:
                raise ValueError("task_info中缺少voice_url字段")
            
            # 生成本地文件路径
            file_name = os.path.basename(file_url.split('?')[0])  # 去除URL参数
            if not file_name or '.' not in file_name:
                file_name = f"audio_{task_id}.wav"
            
            temp_dir = os.path.join(self.config.TEMP_DIR, f"task_{task_id}")
            input_path = os.path.join(temp_dir, file_name)
            
            logger.info(f"任务 {task_id}: 音频URL: {file_url}")
            logger.info(f"任务 {task_id}: 本地路径: {input_path}")
            
            # 下载音频文件
            if not self.api_client.download_file(file_url, input_path):
                raise Exception("音频文件下载失败")
            
            # 获取文件信息
            file_size = os.path.getsize(input_path)
            logger.info(f"任务 {task_id}: 文件下载完成，大小: {self.api_client.get_file_size_str(file_size)}")
            
            # 进行VAD分析
            logger.info(f"任务 {task_id}: 开始VAD分析")
            analysis_result = self.vad_analyzer.analyze_audio(input_path)
            
            # 发送成功回调
            self.api_client.send_success_callback(task_id, analysis_result)
            
            # 清理临时文件
            self._cleanup_temp_files(temp_dir)
            
            # 计算处理时间
            process_time = time.time() - start_time
            logger.info(f"任务 {task_id}: 快速识别完成，处理时间: {process_time:.2f}秒")
            
            return {
                'success': True,
                'data': analysis_result,
                'process_time': process_time
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"任务 {task_id}: 快速识别失败 - {error_msg}")
            
            try:
                # 发送失败回调
                self.api_client.send_failed_callback(task_id, error_msg)
            except Exception as callback_error:
                logger.error(f"发送失败回调异常: {callback_error}")
            
            # 清理临时文件
            temp_dir = os.path.join(self.config.TEMP_DIR, f"task_{task_id}")
            self._cleanup_temp_files(temp_dir)
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _cleanup_temp_files(self, temp_dir: str):
        """清理临时文件"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"已清理临时目录: {temp_dir}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
    
    def get_status(self) -> dict:
        """获取服务状态"""
        return {
            'service': 'quick_node',
            'status': 'running',
            'vad_model': self.vad_analyzer.get_model_info(),
            'queue': self.config.QUEUE_NAME,
            'rabbitmq_host': self.config.RABBITMQ_HOST,
            'api_callback_url': self.config.API_CALLBACK_URL
        }

def main():
    """主函数"""
    try:
        consumer = QueueConsumer()
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

if __name__ == "__main__":
    main() 