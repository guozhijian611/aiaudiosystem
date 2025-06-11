"""
队列消费者模块
监听RabbitMQ队列，处理音频清理任务
"""

import json
import os
import time
import pika
import traceback
from typing import Dict, Any
from config import Config
from logger import logger
from audio_cleaner import AudioCleaner
from api_client import APIClient

class QueueConsumer:
    """队列消费者"""
    
    def __init__(self):
        self.config = Config()
        self.audio_cleaner = AudioCleaner()
        self.api_client = APIClient()
        self.connection = None
        self.channel = None
        
    def connect(self) -> bool:
        """
        连接到RabbitMQ
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 建立连接
            credentials = pika.PlainCredentials(
                self.config.RABBITMQ_USERNAME,
                self.config.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.RABBITMQ_HOST,
                port=self.config.RABBITMQ_PORT,
                virtual_host=self.config.RABBITMQ_VIRTUAL_HOST,
                credentials=credentials,
                heartbeat=600,  # 10分钟心跳
                blocked_connection_timeout=300  # 5分钟阻塞超时
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # 声明队列（与后端保持一致的参数）
            queue_arguments = {
                'x-message-ttl': 3600000,  # 消息TTL: 1小时
                'x-max-priority': 10,      # 支持优先级
                'x-dead-letter-exchange': 'task_dlx',
                'x-dead-letter-routing-key': 'dead_letter'
            }
            
            self.channel.queue_declare(
                queue=self.config.QUEUE_NAME, 
                durable=True,
                arguments=queue_arguments
            )
            
            # 设置预取数量（一次只处理一个任务）
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"成功连接到RabbitMQ: {self.config.RABBITMQ_HOST}:{self.config.RABBITMQ_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("已断开RabbitMQ连接")
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
    
    def process_message(self, channel, method, properties, body):
        """
        处理队列消息
        
        Args:
            channel: 通道对象
            method: 方法对象
            properties: 属性对象
            body: 消息体
        """
        task_data = None
        task_number = None
        
        try:
            # 解析消息
            message = body.decode('utf-8')
            task_data = json.loads(message)
            task_number = task_data.get('task_number')
            
            logger.info(f"收到音频清理任务: {task_number}")
            logger.info(f"任务数据: {task_data}")
            
            # 验证必要字段
            required_fields = ['task_number', 'file_url', 'file_name']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 发送开始处理通知
            self.api_client.send_callback(
                task_number=task_number,
                status='processing',
                message='开始音频清理处理'
            )
            
            # 处理任务
            result = self._process_audio_task(task_data)
            
            # 发送完成通知
            self.api_client.send_callback(
                task_number=task_number,
                status='completed',
                message='音频清理处理完成',
                file_url=result.get('output_url', ''),
                extra_data={
                    'processing_time': result.get('processing_time', 0),
                    'input_size': result.get('input_size', 0),
                    'output_size': result.get('output_size', 0),
                    'model_used': self.config.CLEAR_MODEL
                }
            )
            
            # 确认消息
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"任务处理完成: {task_number}")
            
        except json.JSONDecodeError as e:
            logger.error(f"消息格式错误: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"处理任务失败: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 发送失败通知
            if task_number:
                try:
                    self.api_client.send_callback(
                        task_number=task_number,
                        status='failed',
                        message=f'音频清理处理失败: {str(e)}'
                    )
                except:
                    logger.error("发送失败通知时出错")
            
            # 拒绝消息，不重新入队
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _process_audio_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理音频清理任务
        
        Args:
            task_data (Dict[str, Any]): 任务数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        
        try:
            task_number = task_data['task_number']
            file_url = task_data['file_url']
            file_name = task_data['file_name']
            
            # 创建工作目录
            work_dir = os.path.join(self.config.WORK_DIR, task_number)
            temp_dir = os.path.join(self.config.TEMP_DIR, task_number)
            os.makedirs(work_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)
            
            # 下载输入文件
            input_path = os.path.join(temp_dir, file_name)
            logger.info(f"下载输入文件: {file_url} -> {input_path}")
            self.api_client.download_file(file_url, input_path)
            
            # 获取输入文件信息
            input_info = self.audio_cleaner.get_audio_info(input_path)
            logger.info(f"输入文件信息: {input_info}")
            
            # 生成输出文件路径
            output_filename = f"{os.path.splitext(file_name)[0]}_cleaned.{self.config.OUTPUT_FORMAT}"
            output_path = os.path.join(work_dir, output_filename)
            
            # 执行音频清理
            logger.info(f"开始音频清理处理: {input_path}")
            cleaned_path = self.audio_cleaner.clean_audio(input_path, output_path)
            
            # 获取输出文件信息
            output_info = self.audio_cleaner.get_audio_info(cleaned_path)
            logger.info(f"输出文件信息: {output_info}")
            
            # 上传处理结果
            logger.info(f"上传处理结果: {cleaned_path}")
            upload_result = self.api_client.upload_file(
                file_path=cleaned_path,
                task_number=task_number,
                file_type='cleaned_audio'
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 清理临时文件
            self._cleanup_temp_files(temp_dir)
            
            return {
                'output_url': upload_result.get('file_url', ''),
                'processing_time': round(processing_time, 2),
                'input_size': input_info.get('file_size', 0),
                'output_size': output_info.get('file_size', 0),
                'input_duration': input_info.get('duration', 0),
                'output_duration': output_info.get('duration', 0),
                'model_used': self.config.CLEAR_MODEL,
                'task_type': self.config.CLEAR_TASK
            }
            
        except Exception as e:
            logger.error(f"音频清理任务处理失败: {e}")
            raise
    
    def _cleanup_temp_files(self, temp_dir: str):
        """
        清理临时文件
        
        Args:
            temp_dir (str): 临时目录路径
        """
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"已清理临时目录: {temp_dir}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
    
    def start_consuming(self):
        """
        开始消费消息
        """
        try:
            logger.info(f"开始监听队列: {self.config.QUEUE_NAME}")
            
            # 设置消息处理回调
            self.channel.basic_consume(
                queue=self.config.QUEUE_NAME,
                on_message_callback=self.process_message
            )
            
            # 开始消费
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止消费")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"消费消息时出错: {e}")
            raise
    
    def run_with_retry(self, max_retries: int = 10, retry_interval: int = 15):
        """
        带重试机制的运行
        
        Args:
            max_retries (int): 最大重试次数
            retry_interval (int): 重试间隔（秒）
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 尝试连接
                if self.connect():
                    logger.info("开始消费队列消息...")
                    self.start_consuming()
                    break
                else:
                    raise Exception("连接失败")
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"运行失败 (第{retry_count}次): {e}")
                
                if retry_count < max_retries:
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error(f"达到最大重试次数 ({max_retries})，程序退出")
                    raise
                
            finally:
                # 清理连接
                self.disconnect()
                self.api_client.close()
        
        logger.info("队列消费者已停止")