# Clear Node - 音频清理节点

音频清理节点，基于ClearVoice进行音频降噪和增强处理。

## 功能特性

- 🎵 **音频降噪**: 使用先进的深度学习模型去除音频中的噪声
- 🔊 **语音增强**: 提升语音质量和清晰度
- 🚀 **多模型支持**: 支持FRCRN、MossFormer2等多种模型
- 📦 **队列处理**: 基于RabbitMQ的异步任务处理
- 🐳 **容器化部署**: 支持Docker和Docker Compose部署
- 📊 **实时监控**: 完整的日志记录和状态回调

## 支持的模型

- **FRCRN_SE_16K**: 快速卷积循环网络，适用于16kHz音频
- **MossFormer2_SE_48K**: MossFormer2语音增强模型，适用于48kHz音频
- **MossFormer2_SR_48K**: MossFormer2超分辨率模型
- **MossFormerGAN_SE_16K**: 基于GAN的语音增强模型

## 目录结构

```
clear_node/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日志管理
│   ├── audio_cleaner.py   # 音频清理器
│   ├── api_client.py      # API客户端
│   └── queue_consumer.py  # 队列消费者
├── ClearerVoice-Studio/   # ClearVoice项目
├── work/                  # 工作目录
├── temp/                  # 临时文件目录
├── logs/                  # 日志目录
├── .env.example          # 环境配置示例
├── requirements.txt      # Python依赖
├── Dockerfile           # Docker配置
├── docker-compose.yml   # Docker Compose配置
├── start.sh            # Linux启动脚本
├── start.bat           # Windows启动脚本
├── test.py             # 测试脚本
└── README.md           # 说明文档
```

## 快速开始

### 1. 环境准备

#### 系统要求
- Python 3.9+
- FFmpeg
- 至少4GB内存
- CUDA支持（可选，用于GPU加速）

#### 安装依赖
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg libsndfile1 libsox-fmt-all sox

# CentOS/RHEL
sudo yum install ffmpeg libsndfile sox

# macOS
brew install ffmpeg libsndfile sox

# Windows
# 请从官网下载并安装FFmpeg
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

主要配置项：
```bash
# RabbitMQ配置
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest

# 队列名称
QUEUE_NAME=voice_clear_queue

# 后端API配置
API_BASE_URL=http://localhost:8787

# 音频清理配置
CLEAR_MODEL=FRCRN_SE_16K
CLEAR_TASK=speech_enhancement
OUTPUT_FORMAT=wav
```

### 3. 启动服务

#### 方式一：直接启动
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

#### 方式二：手动启动
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/main.py
```

#### 方式三：Docker启动
```bash
# 构建镜像
docker build -t clear_node .

# 启动服务
docker-compose up -d
```

### 4. 测试服务

```bash
# 运行测试脚本
python test.py
```

## 使用说明

### 任务消息格式

队列接收的消息格式：
```json
{
    "task_number": "000001202412250001",
    "file_url": "http://example.com/audio.wav",
    "file_name": "input_audio.wav",
    "priority": 5,
    "options": {
        "model": "FRCRN_SE_16K",
        "task": "speech_enhancement",
        "output_format": "wav"
    }
}
```

### 处理流程

1. **接收任务**: 从RabbitMQ队列接收音频清理任务
2. **下载文件**: 从指定URL下载原始音频文件
3. **音频清理**: 使用ClearVoice模型进行降噪和增强
4. **上传结果**: 将处理后的音频上传到后端
5. **状态回调**: 发送处理状态和结果到后端API

### 状态回调

处理过程中会发送以下状态回调：

- `processing`: 开始处理
- `completed`: 处理完成
- `failed`: 处理失败

回调数据格式：
```json
{
    "task_number": "000001202412250001",
    "node_type": "clear_node",
    "status": "completed",
    "message": "音频清理处理完成",
    "file_url": "http://example.com/cleaned_audio.wav",
    "timestamp": "2024-12-25T10:30:00",
    "processing_time": 15.5,
    "input_size": 1024000,
    "output_size": 1048576,
    "model_used": "FRCRN_SE_16K"
}
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `RABBITMQ_HOST` | localhost | RabbitMQ主机地址 |
| `RABBITMQ_PORT` | 5672 | RabbitMQ端口 |
| `RABBITMQ_USERNAME` | guest | RabbitMQ用户名 |
| `RABBITMQ_PASSWORD` | guest | RabbitMQ密码 |
| `QUEUE_NAME` | voice_clear_queue | 队列名称 |
| `API_BASE_URL` | http://localhost:8787 | 后端API地址 |
| `CLEAR_MODEL` | FRCRN_SE_16K | 清理模型 |
| `CLEAR_TASK` | speech_enhancement | 清理任务类型 |
| `OUTPUT_FORMAT` | wav | 输出格式 |
| `WORK_DIR` | ./work | 工作目录 |
| `TEMP_DIR` | ./temp | 临时目录 |
| `LOG_LEVEL` | INFO | 日志级别 |

### 模型配置

不同模型的特点和适用场景：

- **FRCRN_SE_16K**: 
  - 采样率: 16kHz
  - 特点: 快速处理，资源占用少
  - 适用: 实时处理，资源受限环境

- **MossFormer2_SE_48K**:
  - 采样率: 48kHz
  - 特点: 高质量增强，效果好
  - 适用: 高质量音频处理

- **MossFormer2_SR_48K**:
  - 采样率: 48kHz
  - 特点: 超分辨率，提升音频质量
  - 适用: 低质量音频升级

## 监控和日志

### 日志级别
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 日志格式
```
2024-12-25 10:30:00 - clear_node - INFO - 收到音频清理任务: 000001202412250001
```

### 性能监控

系统会记录以下性能指标：
- 处理时间
- 文件大小变化
- 内存使用情况
- 模型加载时间

## 故障排除

### 常见问题

1. **ClearVoice导入失败**
   ```
   错误: ModuleNotFoundError: No module named 'clearvoice'
   解决: 确保ClearerVoice-Studio目录存在且路径正确
   ```

2. **模型加载失败**
   ```
   错误: 模型文件不存在
   解决: 检查模型文件是否下载完整
   ```

3. **RabbitMQ连接失败**
   ```
   错误: 连接RabbitMQ失败
   解决: 检查RabbitMQ服务状态和配置
   ```

4. **内存不足**
   ```
   错误: CUDA out of memory
   解决: 降低批处理大小或使用CPU模式
   ```

### 调试模式

启用调试模式：
```bash
export LOG_LEVEL=DEBUG
python src/main.py
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8787/health

# 检查队列状态
rabbitmqctl list_queues
```

## 开发指南

### 添加新模型

1. 在`config.py`中添加模型配置
2. 在`audio_cleaner.py`中添加模型初始化逻辑
3. 更新文档和测试

### 自定义处理逻辑

继承`AudioCleaner`类并重写相关方法：

```python
class CustomAudioCleaner(AudioCleaner):
    def clean_audio(self, input_path, output_path=None):
        # 自定义处理逻辑
        pass
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请联系开发团队。