"""
队列消费者模块
监听RabbitMQ队列，处理音频提取任务
"""

import json
import os
import time
import pika
import traceback
from typing import Dict, Any
from config import Config
from logger import logger
from audio_extractor import AudioExtractor
from api_client import APIClient

class QueueConsumer:
    """队列消费者"""
    
    def __init__(self):
        self.config = Config()
        self.audio_extractor = AudioExtractor()
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
    
    def start_consuming(self):
        """开始消费队列"""
        try:
            logger.info(f"开始监听队列: {self.config.QUEUE_NAME}")
            
            # 设置消费回调
            self.channel.basic_consume(
                queue=self.config.QUEUE_NAME,
                on_message_callback=self._on_message,
                auto_ack=False  # 手动确认消息
            )
            
            # 开始消费
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("接收到停止信号，正在停止消费...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"消费队列时出错: {e}")
        finally:
            self.disconnect()
    
    def _on_message(self, channel, method, properties, body):
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
            message = json.loads(body.decode('utf-8'))
            logger.info(f"接收到任务: {message}")
            
            # 验证消息格式
            task_id = message.get('task_id')
            if not task_id:
                raise ValueError("消息中缺少task_id")
            
            # 处理任务
            success = self._process_task(message)
            
            if success:
                # 确认消息
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"任务 {task_id} 处理成功")
            else:
                # 拒绝消息并重新排队（可以根据需要决定是否重新排队）
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    multiple=False,
                    requeue=False  # 不重新排队，避免无限重试
                )
                logger.error(f"任务 {task_id} 处理失败")
                
        except json.JSONDecodeError as e:
            logger.error(f"消息格式错误: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            logger.error(traceback.format_exc())
            
            # 发送失败回调
            if task_id:
                try:
                    self.api_client.callback_failed(
                        task_id=task_id,
                        task_type=1,  # 音频提取任务类型
                        message=str(e)
                    )
                except:
                    pass
            
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _process_task(self, message: Dict[str, Any]) -> bool:
        """
        处理单个任务
        
        Args:
            message (Dict[str, Any]): 任务消息
            
        Returns:
            bool: 处理是否成功
        """
        task_id = message.get('task_id')
        video_url = message.get('video_url') or message.get('url') or message.get('task_url')
        
        if not video_url:
            logger.error("消息中缺少video_url、url或task_url字段")
            self.api_client.callback_failed(
                task_id=task_id,
                task_type=1,
                message="消息中缺少视频文件URL"
            )
            return False
        
        local_video_path = None
        extracted_audio_path = None
        
        try:
            # 1. 下载视频文件
            logger.info(f"开始下载视频文件: {video_url}")
            local_video_path = os.path.join(
                self.config.TEMP_DIR,
                f"task_{task_id}_video_{int(time.time())}.mp4"
            )
            
            if not self.api_client.download_file(video_url, local_video_path):
                raise Exception("视频文件下载失败")
            
            # 2. 验证视频文件
            if not self.audio_extractor.validate_video_file(local_video_path):
                raise Exception("视频文件格式无效或不包含音频")
            
            # 3. 提取音频
            logger.info(f"开始提取音频: 任务ID {task_id}")
            extracted_audio_path = self.audio_extractor.extract_audio_with_fallback(local_video_path)
            
            # 4. 上传提取的音频文件
            logger.info(f"开始上传音频文件: {extracted_audio_path}")
            upload_result = self.api_client.upload_file(extracted_audio_path, task_type=1)
            
            # 5. 发送成功回调
            file_info = upload_result.get('data', {}).get('file_info', {})
            callback_data = {
                'voice_url': file_info.get('url', ''),
                'file_size': file_info.get('size_byte', 0),
                'file_name': file_info.get('origin_name', ''),
                'duration': self._get_audio_duration(extracted_audio_path)
            }
            
            success = self.api_client.callback_success(
                task_id=task_id,
                task_type=1,
                data=callback_data
            )
            
            if not success:
                logger.error("回调发送失败，但音频提取已完成")
                # 这里可以考虑重试机制
            
            return True
            
        except Exception as e:
            logger.error(f"任务处理失败: {e}")
            logger.error(traceback.format_exc())
            
            # 发送失败回调
            self.api_client.callback_failed(
                task_id=task_id,
                task_type=1,
                message=str(e)
            )
            
            return False
            
        finally:
            # 清理临时文件
            self._cleanup_files([local_video_path, extracted_audio_path])
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频时长
        
        Args:
            audio_path (str): 音频文件路径
            
        Returns:
            float: 音频时长（秒）
        """
        try:
            info = self.audio_extractor.get_video_info(audio_path)
            return info.get('duration', 0)
        except:
            return 0
    
    def _cleanup_files(self, file_paths: list):
        """
        清理临时文件
        
        Args:
            file_paths (list): 文件路径列表
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"已清理临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"清理文件失败: {file_path}, 错误: {e}")
    
    def run_with_retry(self, max_retries: int = 5, retry_interval: int = 10):
        """
        运行消费者，支持重连机制
        
        Args:
            max_retries (int): 最大重试次数
            retry_interval (int): 重试间隔（秒）
        """
        retries = 0
        
        while retries < max_retries:
            try:
                # 确保工作目录存在
                self.config.ensure_directories()
                
                # 尝试连接
                if self.connect():
                    # 重置重试计数
                    retries = 0
                    
                    # 开始消费
                    self.start_consuming()
                else:
                    raise Exception("无法连接到RabbitMQ")
                    
            except KeyboardInterrupt:
                logger.info("接收到停止信号，退出程序")
                break
            except Exception as e:
                retries += 1
                logger.error(f"消费者运行失败 (重试 {retries}/{max_retries}): {e}")
                
                if retries < max_retries:
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error("达到最大重试次数，退出程序")
                    break
                    
            finally:
                self.disconnect() 