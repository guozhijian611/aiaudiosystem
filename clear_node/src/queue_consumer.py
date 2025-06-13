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
import urllib.parse

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
        task_id = None
        
        try:
            # 解析消息
            message = body.decode('utf-8')
            task_data = json.loads(message)
            
            # 获取task_info数据
            task_info = task_data.get('task_info', {})
            
            if not task_info or not isinstance(task_info, dict):
                raise ValueError("消息格式错误：缺少task_info字段或格式不正确")
            
            # 从task_info中获取数据
            task_id = task_info.get('id')
            if not task_id:
                raise ValueError("task_info中缺少id字段")
            
            task_number = f"task_{task_id}"
            
            # clear_node使用voice_url（提取后的音频URL）
            file_url = task_info.get('voice_url')
            if not file_url:
                raise ValueError("task_info中缺少voice_url字段")
            
            # 根据voice_url确定正确的文件名和扩展名
            parsed_url = urllib.parse.urlparse(file_url)
            url_filename = os.path.basename(parsed_url.path)
            
            # 如果URL中有文件名，使用URL中的文件名；否则生成一个
            if url_filename and '.' in url_filename:
                file_name = url_filename
            else:
                # 从voice_url推断文件扩展名，默认为mp3
                file_extension = '.mp3'  # 音频提取后通常是mp3格式
                file_name = f"audio_{task_id}{file_extension}"
            
            logger.info(f"任务 {task_id}: 收到音频降噪任务")
            logger.info(f"任务 {task_id}: 音频URL: {file_url}")
            logger.info(f"任务 {task_id}: 使用文件名: {file_name}")
            logger.info(f"任务 {task_id}: 原始文件信息 - 原始名称: {task_info.get('filename', 'N/A')}, "
                       f"文件大小: {task_info.get('size', 'N/A')}, "
                       f"是否已提取: {task_info.get('is_extract', 0)}, "
                       f"是否已降噪: {task_info.get('is_clear', 0)}")
            
            # 发送开始处理通知
            self.api_client.send_callback(
                task_id=task_id,
                task_type=2,  # 音频降噪任务类型
                status='processing',
                message='开始音频降噪处理'
            )
            
            # 处理任务
            result = self._process_audio_task({
                'task_id': task_id,
                'task_number': task_number,
                'file_url': file_url,
                'file_name': file_name,
                'task_info': task_info  # 传递完整的task_info用于回调
            })
            
            # 发送完成通知
            callback_data = {
                'clear_url': result.get('output_url', ''),
                'file_size': result.get('output_size', 0),
                'file_name': result.get('output_filename', ''),
                'duration': result.get('output_duration', 0),
                'processing_time': result.get('processing_time', 0),
                'model_used': self.config.CLEAR_MODEL,
                'input_size': result.get('input_size', 0),
                'quality_improvement': result.get('quality_improvement', 'N/A')
            }
            
            self.api_client.send_callback(
                task_id=task_id,
                task_type=2,  # 音频降噪任务类型
                status='success',
                message='音频降噪处理完成',
                data=callback_data
            )
            
            # 确认消息
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"任务 {task_id}: 处理完成")
            
        except json.JSONDecodeError as e:
            logger.error(f"消息格式错误: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"任务 {task_id}: 处理失败 - {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 发送失败通知
            if task_id:
                try:
                    success = self.api_client.send_callback(
                        task_id=task_id,
                        task_type=2,  # 音频降噪任务类型
                        status='failed',
                        message=f'音频降噪处理失败: {str(e)}'
                    )
                    if not success:
                        logger.error("失败回调发送失败")
                except Exception as callback_error:
                    logger.error(f"发送失败通知时出错: {callback_error}")
            
            # 拒绝消息，不重新入队
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _process_audio_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理音频降噪任务
        
        Args:
            task_data (Dict[str, Any]): 任务数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        
        try:
            task_id = task_data['task_id']
            task_number = task_data['task_number']
            file_url = task_data['file_url']
            file_name = task_data['file_name']
            task_info = task_data.get('task_info', {})
            
            logger.info(f"任务 {task_id}: 开始音频降噪处理")
            logger.info(f"任务 {task_id}: 输入文件URL: {file_url}")
            logger.info(f"任务 {task_id}: 输入文件名: {file_name}")
            
            # 创建工作目录
            work_dir = os.path.join(self.config.WORK_DIR, task_number)
            temp_dir = os.path.join(self.config.TEMP_DIR, task_number)
            os.makedirs(work_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)
            
            # 下载输入文件
            input_path = os.path.join(temp_dir, file_name)
            logger.info(f"任务 {task_id}: 下载输入文件: {file_url} -> {input_path}")
            
            if not self.api_client.download_file(file_url, input_path):
                raise Exception("音频文件下载失败")
            
            # 验证下载的文件
            if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
                raise Exception("下载的音频文件无效或为空")
            
            # 获取输入文件信息
            input_info = self.audio_cleaner.get_audio_info(input_path)
            logger.info(f"任务 {task_id}: 输入文件信息: 时长={input_info.get('duration', 0):.2f}秒, "
                       f"大小={input_info.get('file_size', 0)} bytes")
            
            # 生成输出文件路径
            base_name = os.path.splitext(file_name)[0]
            output_filename = f"{base_name}_cleared.{self.config.OUTPUT_FORMAT}"
            output_path = os.path.join(work_dir, output_filename)
            
            # 检查音频时长限制
            audio_duration = input_info.get('duration', 0)
            if audio_duration > self.config.MAX_AUDIO_DURATION:
                logger.warning(f"任务 {task_id}: 音频时长 {audio_duration:.2f}秒 超过限制 {self.config.MAX_AUDIO_DURATION}秒")
                logger.info(f"任务 {task_id}: 将使用分块处理模式")
            
            # 执行音频降噪
            logger.info(f"任务 {task_id}: 开始音频降噪处理: {input_path} -> {output_path}")
            logger.info(f"任务 {task_id}: 使用模型: {self.config.CLEAR_MODEL}")
            logger.info(f"任务 {task_id}: 处理超时设置: {self.config.PROCESSING_TIMEOUT}秒")
            
            cleaned_path = self.audio_cleaner.clean_audio(
                input_path, 
                output_path, 
                timeout=self.config.PROCESSING_TIMEOUT
            )
            
            # 验证输出文件
            if not os.path.exists(cleaned_path) or os.path.getsize(cleaned_path) == 0:
                raise Exception("音频降噪处理失败，输出文件无效")
            
            # 获取输出文件信息
            output_info = self.audio_cleaner.get_audio_info(cleaned_path)
            logger.info(f"任务 {task_id}: 输出文件信息: 时长={output_info.get('duration', 0):.2f}秒, "
                       f"大小={output_info.get('file_size', 0)} bytes")
            
            # 上传处理结果
            logger.info(f"任务 {task_id}: 上传降噪后的音频文件: {cleaned_path}")
            upload_result = self.api_client.upload_file(
                file_path=cleaned_path,
                task_type=2  # 音频降噪任务类型
            )
            
            if not upload_result or not upload_result.get('data', {}).get('file_info', {}).get('url'):
                raise Exception("降噪音频文件上传失败")
            
            # 计算处理时间和质量改进指标
            processing_time = time.time() - start_time
            
            # 简单的质量改进评估（基于文件大小变化）
            input_size = input_info.get('file_size', 0)
            output_size = output_info.get('file_size', 0)
            size_change_percent = ((output_size - input_size) / input_size * 100) if input_size > 0 else 0
            
            # 清理临时文件
            self._cleanup_temp_files(temp_dir)
            
            file_info = upload_result.get('data', {}).get('file_info', {})
            result = {
                'output_url': file_info.get('url', ''),
                'output_filename': output_filename,
                'processing_time': round(processing_time, 2),
                'input_size': input_size,
                'output_size': output_size,
                'input_duration': input_info.get('duration', 0),
                'output_duration': output_info.get('duration', 0),
                'model_used': self.config.CLEAR_MODEL,
                'task_type': self.config.CLEAR_TASK,
                'quality_improvement': f"文件大小变化: {size_change_percent:+.1f}%",
                'upload_info': {
                    'file_name': file_info.get('origin_name', ''),
                    'file_size': file_info.get('size_byte', 0),
                    'upload_time': file_info.get('create_time', '')
                }
            }
            
            logger.info(f"任务 {task_id}: 音频降噪处理完成")
            logger.info(f"任务 {task_id}: 处理时间: {result['processing_time']}秒")
            logger.info(f"任务 {task_id}: 输出URL: {result['output_url']}")
            
            return result
            
        except Exception as e:
            logger.error(f"任务 {task_id}: 音频降噪处理失败 - {e}")
            logger.error(traceback.format_exc())
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