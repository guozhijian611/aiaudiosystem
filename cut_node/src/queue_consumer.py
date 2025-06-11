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
            
            # 支持新旧两种消息格式获取task_id
            task_info = message.get('task_info', {})
            task_id = task_info.get('id') if task_info else message.get('task_id')
            
            if not task_id:
                raise ValueError("消息中缺少task_id或task_info.id")
            
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
        # 支持新旧两种消息格式
        task_info = message.get('task_info', {})
        task_id = task_info.get('id') if task_info else message.get('task_id')
        
        if not task_id:
            logger.error("消息中缺少task_id或task_info.id")
            return False
        
        # 智能识别URL字段 - 根据文件类型和处理阶段选择合适的URL
        video_url = None
        
        if task_info:
            # 新格式：从task_info中获取URL
            # cut_node处理原始文件，优先使用url字段
            video_url = task_info.get('url')  # 原始文件URL
            
            # 如果没有url字段，尝试其他字段（兼容性处理）
            if not video_url:
                video_url = task_info.get('voice_url') or task_info.get('task_url')
                
            logger.info(f"任务 {task_id}: 使用新格式消息，文件URL: {video_url}")
            logger.info(f"任务 {task_id}: 文件信息 - 原始名称: {task_info.get('origin_name', 'N/A')}, "
                       f"文件大小: {task_info.get('size_byte', 'N/A')} bytes, "
                       f"是否已提取: {task_info.get('is_extract', 0)}")
        else:
            # 旧格式：兼容处理
            video_url = message.get('video_url') or message.get('url') or message.get('task_url')
            logger.info(f"任务 {task_id}: 使用旧格式消息，文件URL: {video_url}")
        
        if not video_url:
            error_msg = "消息中缺少文件URL字段"
            logger.error(f"任务 {task_id}: {error_msg}")
            self.api_client.callback_failed(
                task_id=task_id,
                task_type=1,
                message=error_msg
            )
            return False
        
        # 根据文件扩展名判断是否需要音频提取
        file_extension = os.path.splitext(video_url.lower())[1]
        is_audio_file = file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        is_video_file = file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        
        logger.info(f"任务 {task_id}: 文件类型检测 - 扩展名: {file_extension}, "
                   f"音频文件: {is_audio_file}, 视频文件: {is_video_file}")
        
        local_file_path = None
        extracted_audio_path = None
        
        try:
            # 1. 下载文件
            logger.info(f"任务 {task_id}: 开始下载文件: {video_url}")
            
            # 根据文件类型设置本地文件名
            if is_audio_file:
                local_file_path = os.path.join(
                    self.config.TEMP_DIR,
                    f"task_{task_id}_audio_{int(time.time())}{file_extension}"
                )
            else:
                local_file_path = os.path.join(
                    self.config.TEMP_DIR,
                    f"task_{task_id}_video_{int(time.time())}{file_extension or '.mp4'}"
                )
            
            if not self.api_client.download_file(video_url, local_file_path):
                raise Exception("文件下载失败")
            
            # 2. 根据文件类型进行处理
            if is_audio_file:
                # 音频文件：直接上传，无需提取
                logger.info(f"任务 {task_id}: 检测到音频文件，直接上传")
                extracted_audio_path = local_file_path
                
                # 验证音频文件
                if not self.audio_extractor.validate_audio_file(extracted_audio_path):
                    raise Exception("音频文件格式无效")
                    
            elif is_video_file:
                # 视频文件：需要提取音频
                logger.info(f"任务 {task_id}: 检测到视频文件，开始提取音频")
                
                # 验证视频文件
                if not self.audio_extractor.validate_video_file(local_file_path):
                    raise Exception("视频文件格式无效或不包含音频")
                
                # 提取音频
                extracted_audio_path = self.audio_extractor.extract_audio_with_fallback(local_file_path)
                
            else:
                # 未知文件类型：尝试作为视频处理
                logger.warning(f"任务 {task_id}: 未知文件类型 {file_extension}，尝试作为视频文件处理")
                
                if not self.audio_extractor.validate_video_file(local_file_path):
                    raise Exception(f"不支持的文件格式: {file_extension}")
                
                extracted_audio_path = self.audio_extractor.extract_audio_with_fallback(local_file_path)
            
            # 3. 上传处理后的音频文件
            logger.info(f"任务 {task_id}: 开始上传音频文件: {extracted_audio_path}")
            upload_result = self.api_client.upload_file(extracted_audio_path, task_type=1)
            
            # 4. 发送成功回调
            file_info = upload_result.get('data', {}).get('file_info', {})
            callback_data = {
                'voice_url': file_info.get('url', ''),
                'file_size': file_info.get('size_byte', 0),
                'file_name': file_info.get('origin_name', ''),
                'duration': self._get_audio_duration(extracted_audio_path),
                'original_file_type': 'audio' if is_audio_file else 'video',
                'extracted': not is_audio_file  # 是否进行了音频提取
            }
            
            success = self.api_client.callback_success(
                task_id=task_id,
                task_type=1,
                data=callback_data
            )
            
            if not success:
                logger.error(f"任务 {task_id}: 回调发送失败，但音频处理已完成")
                # 这里可以考虑重试机制
            
            logger.info(f"任务 {task_id}: 处理完成 - 原始文件类型: {'音频' if is_audio_file else '视频'}, "
                       f"是否提取: {not is_audio_file}, 音频URL: {callback_data['voice_url']}")
            
            return True
            
        except Exception as e:
            logger.error(f"任务 {task_id}: 处理失败 - {e}")
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
            files_to_cleanup = [local_file_path]
            if extracted_audio_path != local_file_path:
                files_to_cleanup.append(extracted_audio_path)
            self._cleanup_files(files_to_cleanup)
    
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