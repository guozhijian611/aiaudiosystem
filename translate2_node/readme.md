# Translate2 Node - Whisper-Diarization 转写节点

Translate2 Node 是一个基于 Whisper-Diarization 的音频转文本服务，在 WhisperX 基础上进一步集成 VAD + TitaNet 嵌入 + diarization，提供一体化的说话人分离和音频转写功能。

## 🚀 主要特性

- **增强的说话人分离**: 集成 VAD + TitaNet 嵌入 + diarization
- **一体化标注**: 一句一句的说话人标注，支持中文
- **优雅的流程**: 流程更优雅，处理更精确
- **兼容性**: 与原始 translate_node 使用同一个队列
- **回退机制**: 如果 Whisper-Diarization 不可用，自动回退到基础 Whisper

## 📋 功能对比

| 功能 | translate_node | translate2_node |
|------|----------------|-----------------|
| 基础转写 | ✅ WhisperX | ✅ Whisper-Diarization |
| 说话人分离 | ✅ 基础分离 | ✅ 增强分离 (VAD + TitaNet) |
| VAD | ❌ | ✅ 语音活动检测 |
| TitaNet嵌入 | ❌ | ✅ 说话人嵌入 |
| 中文支持 | ✅ | ✅ 优化支持 |
| 流程优化 | 基础 | 优雅一体化 |

## 🏗️ 项目结构

```
translate2_node/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日志管理
│   ├── transcriber.py     # Whisper-Diarization 转写器
│   ├── api_client.py      # API客户端
│   └── queue_consumer.py  # 队列消费者
├── whisper-diarization/   # Whisper-Diarization 模块
├── requirements.txt       # Python依赖
├── environment.yml        # Conda环境配置
├── .env.example          # 环境变量示例
├── logs/                 # 日志目录
├── temp/                 # 临时文件目录
├── work/                 # 工作目录
├── models/               # 模型缓存目录
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

#### 方式一：Conda 环境（推荐）

```bash
# 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate whisper-diarization

# 安装 Whisper-Diarization
git clone https://github.com/guillaumekln/whisper-diarization.git
cd whisper-diarization
pip install -e .
```

#### 方式二：Docker 部署

```bash
# 构建镜像
docker build -t translate2-node .

# 运行容器
docker run -d --name translate2-node translate2-node
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑配置文件
vim .env
```

**重要配置项：**

```bash
# 必需：Hugging Face Token（用于说话人分离）
HF_TOKEN=your_huggingface_token_here

# RabbitMQ 配置（与原始 translate_node 相同）
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin

# 队列名称（与原始 translate_node 使用同一个队列）
QUEUE_NAME=transcribe_queue
```

### 3. 启动服务

```bash
# 直接运行
python main.py

# 或者使用 conda
conda activate whisper-diarization
python main.py
```

## ⚙️ 配置说明

### 核心配置

- **WHISPER_MODEL**: Whisper 模型大小 (tiny, base, small, medium, large, large-v3)
- **ENABLE_DIARIZATION**: 是否启用说话人分离
- **ENABLE_VAD**: 是否启用语音活动检测
- **ENABLE_TITANET**: 是否启用 TitaNet 嵌入

### VAD 配置

- **VAD_THRESHOLD**: VAD 阈值 (0.0-1.0)
- **VAD_MIN_SPEECH_DURATION**: 最小语音时长（秒）
- **VAD_MAX_SPEECH_DURATION**: 最大语音时长（秒）

### 说话人分离配置

- **MIN_SPEAKERS**: 最小说话人数
- **MAX_SPEAKERS**: 最大说话人数
- **HF_TOKEN**: Hugging Face Token（必需）

## 🔧 高级功能

### 1. 说话人分离增强

```python
# 配置示例
ENABLE_DIARIZATION=true
ENABLE_VAD=true
ENABLE_TITANET=true
HF_TOKEN=your_token_here
```

### 2. 自定义 VAD 参数

```python
# 调整 VAD 敏感度
VAD_THRESHOLD=0.3          # 更敏感
VAD_MIN_SPEECH_DURATION=0.3  # 更短的语音片段
VAD_MAX_SPEECH_DURATION=20.0  # 更长的语音片段
```

### 3. 模型选择

```python
# 不同大小的模型
WHISPER_MODEL=tiny      # 最快，精度较低
WHISPER_MODEL=base      # 平衡
WHISPER_MODEL=large-v3  # 最精确，较慢
```

## 📊 输出格式

### JSON 格式示例

```json
{
  "text": "完整的转写文本",
  "language": "zh",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "你好，世界",
      "speaker": "SPEAKER_00",
      "confidence": 0.95
    }
  ],
  "speakers": {
    "SPEAKER_00": "SPEAKER_00",
    "SPEAKER_01": "SPEAKER_01"
  },
  "summary": {
    "total_duration": 120.5,
    "total_segments": 45,
    "total_speakers": 2
  },
  "metadata": {
    "processing_time": 45.2,
    "model": "large-v3",
    "device": "cuda",
    "diarization_enabled": true,
    "vad_enabled": true,
    "titanet_enabled": true
  }
}
```

## 🔍 监控和调试

### 查看日志

```bash
# 实时日志
tail -f logs/translate2_node_20241220.log

# 错误日志
grep "ERROR" logs/translate2_node_20241220.log
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8787/health

# 检查队列连接
python -c "
from src.queue_consumer import QueueConsumer
consumer = QueueConsumer()
print('状态:', consumer.get_status())
"
```

## 🐛 故障排除

### 常见问题

1. **HF_TOKEN 未配置**
   ```
   错误: 未配置 HF_TOKEN，说话人分离功能将被禁用
   解决: 在 .env 文件中设置有效的 HF_TOKEN
   ```

2. **Whisper-Diarization 模块未找到**
   ```
   警告: Whisper-Diarization 模块未找到，将使用基础 Whisper 实现
   解决: 安装 Whisper-Diarization 模块
   ```

3. **CUDA 内存不足**
   ```
   错误: CUDA out of memory
   解决: 减小 WHISPER_BATCH_SIZE 或使用较小的模型
   ```

### 性能优化

1. **GPU 优化**
   ```bash
   WHISPER_DEVICE=cuda
   WHISPER_BATCH_SIZE=32  # 根据GPU内存调整
   ```

2. **内存优化**
   ```bash
   WHISPER_MODEL=medium   # 使用中等大小模型
   CHUNK_DURATION=300     # 分块处理
   ```

3. **VAD 优化**
   ```bash
   VAD_THRESHOLD=0.5      # 调整敏感度
   VAD_MIN_SPEECH_DURATION=0.5
   ```

## 🔄 与原始 translate_node 的兼容性

- **队列兼容**: 使用同一个 `transcribe_queue` 队列
- **API兼容**: 相同的回调接口和格式
- **配置兼容**: 大部分配置项相同
- **输出兼容**: 相同的 JSON 输出格式

## 📈 性能对比

| 指标 | translate_node | translate2_node |
|------|----------------|-----------------|
| 转写精度 | 高 | 更高 |
| 说话人分离精度 | 中等 | 高 |
| 处理速度 | 快 | 中等 |
| 内存使用 | 中等 | 较高 |
| 中文支持 | 好 | 更好 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## �� 许可证

MIT License 