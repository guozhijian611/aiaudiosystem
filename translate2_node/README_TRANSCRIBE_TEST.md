# Translate2 Node 转写测试指南

本文档介绍如何使用 Translate2 Node 的转写测试功能。

## 测试脚本说明

### 1. test_local_transcribe.py - 主要测试脚本

这是主要的转写测试脚本，支持命令行参数和详细输出。

**功能特性：**
- 支持多种音频格式（wav, mp3, m4a, flac 等）
- 自动检测说话人分离功能
- 生成 JSON 和 SRT 格式的输出
- 详细的转写结果展示
- 支持超时设置

**使用方法：**
```bash
# 基本用法
python test_local_transcribe.py audio_file.wav

# 指定输出文件
python test_local_transcribe.py audio_file.wav -o output/result.json

# 设置超时时间（秒）
python test_local_transcribe.py audio_file.wav -t 1800

# 详细输出
python test_local_transcribe.py audio_file.wav -v

# 完整参数示例
python test_local_transcribe.py audio_file.wav -o output/result.json -t 3600 -v
```

### 2. example_transcribe.py - 简单示例脚本

这是一个简单的转写示例，适合快速测试。

**使用方法：**
1. 将音频文件重命名为 `example_audio.wav` 或修改脚本中的文件名
2. 运行脚本：
```bash
python example_transcribe.py
```

### 3. test_transcribe.bat - Windows 批处理脚本

Windows 平台下的便捷测试脚本。

**使用方法：**
```cmd
# 基本用法
test_transcribe.bat audio_file.wav

# 带路径的文件
test_transcribe.bat "C:\audio\test.mp3"
```

### 4. test_transcribe.sh - Linux/Mac Shell 脚本

Linux/Mac 平台下的便捷测试脚本。

**使用方法：**
```bash
# 基本用法
./test_transcribe.sh audio_file.wav

# 带路径的文件
./test_transcribe.sh /path/to/audio.mp3
```

## 输出格式

### JSON 格式输出
```json
{
  "text": "完整的转写文本",
  "language": "检测到的语言",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "段落文本",
      "speaker": "SPEAKER_00",
      "confidence": 0.95
    }
  ],
  "speakers": {
    "SPEAKER_00": "SPEAKER_00"
  },
  "summary": {
    "total_duration": 120.5,
    "total_segments": 25,
    "total_speakers": 2
  },
  "metadata": {
    "processing_time": 45.2,
    "model": "large-v3",
    "device": "cuda",
    "diarization_enabled": true
  }
}
```

### SRT 格式输出
```
1
00:00:00,000 --> 00:00:05,200
[SPEAKER_00] 第一段文本

2
00:00:05,200 --> 00:00:10,500
[SPEAKER_01] 第二段文本
```

## 配置说明

### 环境变量配置
在 `.env` 文件中配置以下参数：

```env
# Whisper 模型配置
WHISPER_MODEL=large-v3
WHISPER_DEVICE=auto
WHISPER_LANGUAGE=zh
WHISPER_BATCH_SIZE=8

# 说话人分离配置
ENABLE_DIARIZATION=true
ENABLE_VAD=true
ENABLE_TITANET=true
HF_TOKEN=your_huggingface_token

# 说话人数量限制
MIN_SPEAKERS=1
MAX_SPEAKERS=10

# VAD 参数
VAD_THRESHOLD=0.5
VAD_MIN_SPEECH_DURATION=0.5
VAD_MAX_SPEECH_DURATION=float('inf')

# TitaNet 模型
TITANET_MODEL=titanet-l
```

### 说话人分离功能

**启用条件：**
1. 配置有效的 `HF_TOKEN`
2. `ENABLE_DIARIZATION=true`
3. Whisper-Diarization 脚本可用

**功能特性：**
- 自动检测说话人数量
- 说话人编号归一化
- 支持 VAD（语音活动检测）
- 支持 TitaNet 嵌入

## 常见问题

### 1. 缺少依赖模块
**错误：** `No module named 'torch'`
**解决：** 安装 PyTorch
```bash
pip install torch torchaudio
```

### 2. 说话人分离未生效
**原因：** 缺少 HF_TOKEN 或 Whisper-Diarization 脚本
**解决：** 
1. 配置有效的 Huggingface 访问令牌
2. 确保 whisper-diarization 目录存在

### 3. 转写超时
**解决：** 增加超时时间或使用更小的模型
```bash
python test_local_transcribe.py audio.wav -t 7200  # 2小时超时
```

### 4. 内存不足
**解决：** 
1. 减小批处理大小：`WHISPER_BATCH_SIZE=4`
2. 使用较小的模型：`WHISPER_MODEL=medium`
3. 使用 CPU 设备：`WHISPER_DEVICE=cpu`

## 性能优化建议

### 1. 硬件要求
- **GPU:** NVIDIA GPU with 8GB+ VRAM (推荐)
- **CPU:** 多核 CPU (至少 4 核)
- **内存:** 16GB+ RAM
- **存储:** SSD 推荐

### 2. 模型选择
- **large-v3:** 最高精度，需要更多资源
- **medium:** 平衡精度和速度
- **small:** 快速处理，精度稍低
- **base:** 最快，精度最低

### 3. 批处理优化
- 根据 GPU 内存调整 `WHISPER_BATCH_SIZE`
- 大文件建议使用较小的批处理大小

## 测试建议

### 1. 音频文件准备
- 使用清晰的音频文件
- 避免背景噪音
- 支持格式：wav, mp3, m4a, flac, ogg

### 2. 测试流程
1. 先用小文件测试基本功能
2. 测试说话人分离功能
3. 测试大文件处理能力
4. 验证输出格式正确性

### 3. 结果验证
- 检查转写文本准确性
- 验证说话人分离效果
- 确认时间戳对齐
- 检查输出文件完整性

## 技术支持

如果遇到问题，请检查：
1. 依赖是否正确安装
2. 配置文件是否正确
3. 音频文件是否有效
4. 系统资源是否充足

更多信息请参考项目主文档。 