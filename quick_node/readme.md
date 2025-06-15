# Quick Node - 快速识别节点

基于 FunASR 的语音活动检测（VAD）服务，用于快速分析音频文件的有效语音时长。

## 功能特性

- 🎯 **快速VAD分析**: 使用FunASR的FSMN-VAD模型进行语音活动检测
- 📊 **详细统计**: 提供音频总时长、有效语音时长、静音时长、语音占比等统计信息
- 🔄 **队列处理**: 基于RabbitMQ的异步任务处理
- 📡 **API回调**: 自动向后端API发送处理结果
- 🧹 **自动清理**: 处理完成后自动清理临时文件
- 📝 **详细日志**: 完整的处理日志记录

## 系统架构

```
音频降噪完成 → 推送到快速识别队列 → quick_node处理 → VAD分析 → 更新数据库
```

## 安装部署

### 1. 环境要求

- Python 3.8+
- CUDA支持（推荐，用于GPU加速）
- 足够的磁盘空间用于模型下载

### 2. 安装依赖

#### 方式1: 使用Conda环境（推荐）

```bash
# 创建并激活conda环境
conda env create -f environment.yml
conda activate funasr

# 安装本地FunASR（开发模式）
cd FunASR
pip install -e .
cd ..

# 安装Quick Node特有依赖
pip install -r requirements.txt
```

#### 方式2: 使用纯pip环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装完整依赖
pip install -r requirements-full.txt

# 安装本地FunASR（开发模式）
cd FunASR
pip install -e .
cd ..
```

### 3. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑配置文件
vim .env
```

### 4. 启动服务

```bash
# 直接启动
python run.py

# 或者使用src目录启动
cd src && python queue_consumer.py
```

## 依赖文件说明

| 文件名 | 用途 | 说明 |
|--------|------|------|
| `environment.yml` | Conda环境配置 | 包含FunASR核心依赖，不包含funasr主包 |
| `requirements.txt` | Quick Node特有依赖 | 仅包含队列、API等特有功能的依赖 |
| `requirements-full.txt` | 完整依赖列表 | 适用于非conda环境，不包含funasr主包 |
| `FunASR/` | 本地FunASR源码 | 使用 `pip install -e .` 安装开发版本 |

## 配置说明

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `RABBITMQ_HOST` | 10.0.0.130 | RabbitMQ服务器地址 |
| `RABBITMQ_PORT` | 5672 | RabbitMQ端口 |
| `API_BASE_URL` | http://10.0.0.130:8787 | 后端API地址 |
| `VAD_MODEL` | fsmn-vad | VAD模型名称 |
| `VAD_MODEL_REVISION` | v2.0.4 | 模型版本 |
| `MAX_WORKERS` | 2 | 最大并发处理数 |

### VAD模型参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `VAD_MAX_END_SILENCE_TIME` | 800ms | 最大结束静音时间 |
| `VAD_MAX_START_SILENCE_TIME` | 3000ms | 最大开始静音时间 |
| `VAD_MIN_SPEECH_DURATION` | 250ms | 最小语音持续时间 |

## 工作流程

### 1. 队列消息格式

```json
{
  "task_info": {
    "id": 53,
    "clear_url": "http://10.0.0.130:8787/storage/queue/20250612/xxx.wav",
    "filename": "original_file.mp4",
    "size": "1.73 MB",
    // ... 其他TaskInfo字段
  },
  "processing_type": "fast_recognition"
}
```

### 2. 处理步骤

1. **接收任务**: 从 `fast_process_queue` 队列接收任务
2. **发送处理中回调**: 通知后端开始处理
3. **下载音频**: 从 `clear_url` 下载降噪后的音频文件
4. **VAD分析**: 使用FunASR进行语音活动检测
5. **发送结果回调**: 将分析结果发送给后端API
6. **清理文件**: 删除临时下载的文件

### 3. 回调数据格式

#### 成功回调
```json
{
  "task_id": 53,
  "task_type": 3,
  "status": "success",
  "data": {
    "total_voice": 15.86,           // 音频总时长(秒)
    "effective_voice": 12.34,       // 有效语音时长(秒)
    "speech_ratio": 0.7782,         // 语音占比
    "speech_segments_count": 8,     // 语音段落数
    "analysis_details": {
      "silence_duration": 3.52,     // 静音时长(秒)
      "file_info": {...},           // 文件信息
      "speech_segments": [...]      // 语音段落详情
    }
  }
}
```

#### 失败回调
```json
{
  "task_id": 53,
  "task_type": 3,
  "status": "failed",
  "data": {
    "error_message": "错误详情"
  }
}
```

## 数据库更新

处理成功后，后端会更新以下字段：

- `effective_voice`: 有效语音时长
- `total_voice`: 音频总时长
- `fast_status`: 快速识别状态 (1=完成, 2=未完成)
- `step`: 任务步骤 (6=快速识别完成)

## 测试验证

### 1. VAD功能测试

```bash
# 准备测试音频文件
cp your_audio_file.wav test_audio.wav

# 运行测试
python test_vad.py
```

### 2. 队列消息测试

```bash
# 发送测试消息到队列
python -c "
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.130'))
channel = connection.channel()

test_message = {
    'task_info': {
        'id': 999,
        'clear_url': 'http://10.0.0.130:8787/storage/queue/test.wav'
    }
}

channel.basic_publish(
    exchange='',
    routing_key='fast_process_queue',
    body=json.dumps(test_message)
)
connection.close()
"
```

## 监控和日志

### 日志文件位置
- 默认位置: `./logs/quick_node.log`
- 日志轮转: 10MB自动轮转，保留7天

### 关键日志信息
- 任务接收和处理状态
- VAD分析结果统计
- 回调发送状态
- 错误和异常信息

### 服务状态检查

```python
from src.queue_consumer import QueueConsumer
consumer = QueueConsumer()
status = consumer.get_status()
print(status)
```

## 故障排除

### 常见问题

1. **模型下载失败**
   - 检查网络连接
   - 确认ModelScope访问正常
   - 手动下载模型到缓存目录

2. **RabbitMQ连接失败**
   - 检查RabbitMQ服务状态
   - 验证连接参数
   - 确认队列权限

3. **音频文件下载失败**
   - 检查文件URL可访问性
   - 验证网络连接
   - 确认磁盘空间充足

4. **VAD分析失败**
   - 检查音频文件格式
   - 验证文件完整性
   - 查看详细错误日志

### 性能优化

1. **GPU加速**: 安装CUDA版本的PyTorch
2. **并发处理**: 调整 `MAX_WORKERS` 参数
3. **内存优化**: 及时清理临时文件
4. **网络优化**: 使用本地文件存储减少下载时间

## 开发说明

### 项目结构

```
quick_node/
├── src/
│   ├── __init__.py
│   ├── queue_consumer.py    # 队列消费者主程序
│   ├── vad_analyzer.py      # VAD分析器
│   └── api_client.py        # API客户端
├── config.py                # 配置文件
├── environment.yml          # Conda环境配置
├── requirements.txt         # Quick Node特有依赖
├── requirements-full.txt    # 完整依赖（非conda环境）
├── run.py                  # 启动脚本
├── start.sh                # 自动化启动脚本
├── test_vad.py             # VAD测试脚本
├── .env.example            # 环境变量示例
└── README.md               # 说明文档
```

### 扩展开发

1. **添加新的分析功能**: 在 `VADAnalyzer` 类中扩展
2. **支持更多音频格式**: 修改 `SUPPORTED_AUDIO_FORMATS` 配置
3. **自定义回调格式**: 修改 `APIClient.send_success_callback` 方法
4. **添加监控指标**: 集成Prometheus或其他监控系统

## 版本历史

- v1.0.0: 初始版本，基础VAD功能
- 计划中: 实时语音识别支持、多语言检测、说话人分离