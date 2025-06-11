# Cut Node - 音频提取节点

Cut Node 是一个专门用于从视频文件中提取音频的微服务节点，基于 Python 和 Docker，使用 FFmpeg 进行音频提取，通过 RabbitMQ 与后端队列系统通信。

## 功能特性

- 🎵 **音频提取**: 使用 FFmpeg 从视频文件中提取高质量音频
- 🚀 **队列处理**: 监听 RabbitMQ 队列，自动处理音频提取任务
- 🔄 **自动重连**: 支持 RabbitMQ 连接断开后自动重连
- 📤 **文件上传**: 自动上传提取的音频文件到后端
- 📊 **状态回调**: 实时向后端报告任务处理状态
- 🐳 **Docker 部署**: 完整的 Docker 和 Docker Compose 支持
- 📝 **详细日志**: 完整的日志记录和错误追踪

## 项目结构

```
cut_node/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日志管理
│   ├── audio_extractor.py # 音频提取器
│   ├── api_client.py      # API客户端
│   └── queue_consumer.py  # 队列消费者
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker Compose配置
├── .env.example         # 环境变量示例
└── README.md           # 项目说明
```

## 快速开始

### 1. 环境准备

#### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository>
cd cut_node

# 2. 复制环境配置
cp .env.example .env

# 3. 修改配置文件
vim .env  # 修改后端API地址等配置

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f cut_node
```

#### 方式二：本地开发

```bash
# 1. 安装 FFmpeg
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# 2. 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 运行程序
cd src
python main.py
```

### 2. 配置说明

主要配置项（.env文件）：

```bash
# RabbitMQ配置
RABBITMQ_HOST=localhost         # RabbitMQ主机地址
RABBITMQ_PORT=5672             # RabbitMQ端口
RABBITMQ_USERNAME=guest        # RabbitMQ用户名
RABBITMQ_PASSWORD=guest        # RabbitMQ密码

# 后端API配置
API_BASE_URL=http://localhost:8787    # 后端API基础URL
API_UPLOAD_ENDPOINT=/queue/upload     # 文件上传接口
API_CALLBACK_ENDPOINT=/queue/callback # 状态回调接口

# FFmpeg配置
AUDIO_FORMAT=mp3              # 输出音频格式
AUDIO_BITRATE=128k           # 音频比特率
AUDIO_SAMPLE_RATE=44100      # 采样率
FFMPEG_THREADS=4             # FFmpeg线程数
```

## 工作流程

1. **监听队列**: 程序启动后监听 `voice_extract_queue` 队列
2. **接收任务**: 接收包含视频文件URL的任务消息
3. **下载文件**: 从后端下载视频文件到本地临时目录
4. **提取音频**: 使用 FFmpeg 从视频中提取音频
5. **上传音频**: 将提取的音频文件上传到后端
6. **发送回调**: 向后端发送任务完成状态
7. **清理文件**: 清理本地临时文件

## API 对接

### 队列消息格式

接收的队列消息：
```json
{
    "task_id": 123,
    "video_url": "http://domain/storage/video.mp4",
    "url": "http://domain/storage/video.mp4"  // 备用字段
}
```

### 回调接口

成功回调：
```json
{
    "task_id": 123,
    "task_type": 1,
    "status": "success",
    "data": {
        "voice_url": "http://domain/storage/audio.mp3",
        "file_size": 1048576,
        "file_name": "audio.mp3",
        "duration": 180.5
    }
}
```

失败回调：
```json
{
    "task_id": 123,
    "task_type": 1,
    "status": "failed",
    "message": "音频提取失败: 文件格式不支持"
}
```

## 监控和调试

### 查看日志

```bash
# Docker 部署
docker-compose logs -f cut_node

# 本地运行
tail -f /app/logs/cut_node_20241220.log
```

### 健康检查

```bash
# 检查容器状态
docker-compose ps

# 检查后端连接
docker exec cut_node python -c "
import sys; sys.path.append('/app/src')
from api_client import APIClient
print('健康检查:', '正常' if APIClient().health_check() else '异常')
"
```

### RabbitMQ 管理

访问 RabbitMQ 管理界面：http://localhost:15672
- 用户名: guest
- 密码: guest

## 故障排除

### 常见问题

1. **FFmpeg 未找到**
   ```bash
   # 确保 FFmpeg 已安装
   ffmpeg -version
   
   # Docker 中应该自动安装
   docker exec cut_node ffmpeg -version
   ```

2. **RabbitMQ 连接失败**
   ```bash
   # 检查 RabbitMQ 服务状态
   docker-compose logs rabbitmq
   
   # 检查网络连接
   docker exec cut_node ping rabbitmq
   ```

3. **后端API连接失败**
   ```bash
   # 检查后端服务是否运行
   curl http://localhost:8787
   
   # 检查Docker网络配置
   docker network ls
   ```

4. **文件上传失败**
   - 检查后端存储配置
   - 确认文件大小限制
   - 验证网络连接稳定性

### 调试模式

启用详细日志：
```bash
# 修改 .env 文件
LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart cut_node
```

## 性能优化

### 调整 FFmpeg 参数

```bash
# 增加线程数（多核CPU）
FFMPEG_THREADS=8

# 调整音频质量
AUDIO_BITRATE=192k  # 更高质量
AUDIO_SAMPLE_RATE=48000
```

### 扩展部署

```bash
# 启动多个实例
docker-compose up -d --scale cut_node=3
```

## 开发

### 添加新功能

1. 修改源代码
2. 重新构建Docker镜像
3. 测试功能
4. 更新文档

### 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License 