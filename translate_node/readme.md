# Translate Node - 音频转文本服务

基于 WhisperX 的高性能音频转文本微服务，支持多语言转写、说话人分离和语言对齐功能。

## 功能特性

- **多语言转写**: 基于 Whisper large-v3 模型，支持多种语言自动识别和转写
- **说话人分离**: 使用 pyannote-audio 进行说话人识别和分离
- **语言对齐**: 提供精确的词级时间戳对齐
- **GPU 加速**: 支持 CUDA 和 Apple Silicon MPS 加速
- **队列处理**: 基于 RabbitMQ 的异步任务处理
- **API 回调**: 支持处理状态和结果的实时回调
- **跨平台**: 支持 Windows、macOS 和 Linux

## 架构设计

```
translate_node/
├── src/
│   ├── api_client.py       # API客户端，处理文件上传下载和回调
│   ├── transcriber.py      # WhisperX转写器核心模块
│   ├── queue_consumer.py   # RabbitMQ队列消费者
│   └── logger.py          # 日志配置
├── config.py              # 配置管理
├── main.py               # 主入口
├── requirements.txt      # Python依赖
├── environment.yml       # Conda环境配置
├── .env                 # 环境变量配置
├── Dockerfile           # Docker构建文件
├── docker-compose.yml   # Docker编排配置
├── install.sh          # 环境安装脚本
└── run.sh             # 运行脚本
```

## 环境要求

### 系统要求
- Python 3.9-3.12
- CUDA 12.1+ (GPU 加速，可选)
- 8GB+ RAM (16GB+ 推荐)
- 5GB+ 存储空间

### 依赖软件
- Anaconda/Miniconda
- RabbitMQ 服务器
- FFmpeg (音频处理)

## 安装配置

### 1. 使用安装脚本（推荐）

```bash
# 克隆代码
git clone <repository>
cd translate_node

# 运行安装脚本
./install.sh
```

### 2. 手动安装

```bash
# 创建conda环境
conda env create -f environment.yml

# 激活环境
conda activate whisperx

# 安装额外依赖
pip install -r requirements.txt

# 创建工作目录
mkdir -p work temp logs models
```

### 3. 配置环境变量

复制并编辑环境变量文件：

```bash
# 复制模板文件
cp .env.example .env

# 编辑配置
nano .env  # 或使用其他编辑器
```

编辑 `.env` 文件：

```bash
# RabbitMQ配置
RABBITMQ_HOST=10.0.0.130
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin

# API配置
API_BASE_URL=http://10.0.0.130:8787
QUEUE_NAME=transcribe_queue

# WhisperX配置
WHISPER_MODEL=large-v3          # 模型大小: tiny, base, small, medium, large-v3
WHISPER_LANGUAGE=auto           # 语言: auto, zh, en, ja, 等
WHISPER_DEVICE=auto             # 设备: auto, cuda, cpu, mps

# 功能开关
ENABLE_DIARIZATION=true         # 说话人分离
ENABLE_ALIGNMENT=true           # 语言对齐
HF_TOKEN=your_huggingface_token # Hugging Face Token (说话人分离需要)
```

## 使用方法

### 本地运行

```bash
# 使用运行脚本
./run.sh

# 或者手动运行
conda activate whisperx
python main.py
```

### Docker 运行

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f translate_node

# 停止服务
docker-compose down
```

## GPU 支持配置

### NVIDIA GPU

```bash
# 检查CUDA可用性
nvidia-smi

# 在environment.yml中确保使用CUDA版本的PyTorch
# 已在配置文件中设置为nightly版本以支持RTX 50系列
```

### Apple Silicon

```bash
# MPS会自动检测和使用
# 设置环境变量
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

## 监控和调试

### 日志查看

```bash
# 实时查看日志
tail -f logs/translate_node.log

# 查看特定级别日志
grep "ERROR" logs/translate_node.log
```

### 状态监控

程序启动时会显示：
- 设备检测信息（GPU/CPU）
- 模型加载状态
- 队列连接状态
- 配置参数摘要

### 性能调优

1. **GPU 内存优化**:
   ```bash
   # 调整批处理大小
   WHISPER_BATCH_SIZE=8  # 默认16，可根据GPU内存调整
   ```

2. **CPU 处理优化**:
   ```bash
   # 限制线程数
   export OMP_NUM_THREADS=4
   ```

3. **处理超时配置**:
   ```bash
   PROCESSING_TIMEOUT=7200  # 2小时超时
   MAX_AUDIO_DURATION=3600  # 最大1小时音频
   ```

## API 集成

### 队列消息格式

发送到 `transcribe_queue` 的消息格式：

```json
{
    "task_id": 123,
    "voice_url": "http://example.com/audio.wav"
}
```

### 回调数据格式

成功回调 (task_type=4, status='success'):

```json
{
    "task_id": 123,
    "task_type": 4,
    "status": "success",
    "data": {
        "text_info": "转写的文本内容",
        "effective_voice": 1234.5,
        "total_voice": 1500.0,
        "language": "zh",
        "transcribe_details": {
            "segments_count": 45,
            "confidence_avg": 0.92,
            "word_count": 200,
            "speakers": ["SPEAKER_00", "SPEAKER_01"],
            "segments": [...]
        }
    }
}
```

## 故障排除

### 常见问题

1. **模型下载失败**:
   ```bash
   # 手动下载模型
   python -c "import whisperx; whisperx.load_model('large-v3')"
   ```

2. **GPU 内存不足**:
   ```bash
   # 减少批处理大小
   WHISPER_BATCH_SIZE=4
   # 或使用较小模型
   WHISPER_MODEL=medium
   ```

3. **说话人分离失败**:
   ```bash
   # 需要Hugging Face Token
   # 在 https://huggingface.co/settings/tokens 获取
   HF_TOKEN=your_token_here
   ```

4. **音频格式不支持**:
   ```bash
   # 确保安装了FFmpeg
   sudo apt install ffmpeg  # Ubuntu
   brew install ffmpeg      # macOS
   ```

### 日志级别

```bash
LOG_LEVEL=DEBUG    # 详细调试信息
LOG_LEVEL=INFO     # 一般信息 (默认)
LOG_LEVEL=WARNING  # 警告信息
LOG_LEVEL=ERROR    # 仅错误信息
```

## 开发说明

### 代码结构

- `transcriber.py`: 核心转写逻辑，处理 WhisperX 模型调用
- `queue_consumer.py`: 队列消费逻辑，处理任务分发
- `api_client.py`: HTTP 客户端，处理文件和回调
- `config.py`: 配置管理，统一环境变量处理

### 扩展功能

1. **添加新的输出格式**:
   - 在 `transcriber.py` 中扩展输出格式支持
   - 支持 SRT、VTT、TXT 等格式

2. **优化处理性能**:
   - 实现音频分块处理
   - 添加并行处理支持

3. **增强监控**:
   - 添加 Prometheus 指标
   - 集成健康检查端点

## 许可证

本项目遵循项目根目录的许可证。

## 支持

如有问题，请查看：
1. 日志文件 `logs/translate_node.log`
2. 项目文档和 issue
3. WhisperX 官方文档
