# Translate2 Node 快速开始指南

## 快速测试转写功能

### 1. 准备音频文件
将您要测试的音频文件放在项目目录中，支持的格式：
- WAV (.wav)
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- OGG (.ogg)

### 2. 选择测试方式

#### 方式一：使用命令行脚本（推荐）
```bash
# Linux/Mac
python test_local_transcribe.py your_audio.wav

# 或者使用便捷脚本
./test_transcribe.sh your_audio.wav
```

```cmd
# Windows
python test_local_transcribe.py your_audio.wav

# 或者使用批处理脚本
test_transcribe.bat your_audio.wav
```

#### 方式二：使用简单示例
1. 将音频文件重命名为 `example_audio.wav`
2. 运行：
```bash
python example_transcribe.py
```

### 3. 查看结果
测试完成后，结果文件将保存在 `output/` 目录中：
- `your_audio_transcribe.json` - 详细的JSON格式结果
- `your_audio_transcribe.srt` - 字幕格式结果

### 4. 配置说话人分离（可选）
如果要启用说话人分离功能：

1. 获取 Huggingface 访问令牌：
   - 访问 https://huggingface.co/settings/tokens
   - 创建新的访问令牌

2. 配置环境变量：
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，添加您的令牌
echo "HF_TOKEN=your_token_here" >> .env
```

3. 重新运行测试，说话人分离功能将自动启用

## 常见问题解决

### 问题1：缺少依赖模块
```bash
# 安装基础依赖
pip install torch torchaudio pika requests python-dotenv psutil loguru

# 或者使用conda
conda env create -f environment.yml
conda activate whisper-diarization
```

### 问题2：说话人分离未生效
- 检查是否配置了 `HF_TOKEN`
- 确认 `ENABLE_DIARIZATION=true`
- 验证 whisper-diarization 目录存在

### 问题3：转写速度慢
- 使用较小的模型：修改 `.env` 中的 `WHISPER_MODEL=medium`
- 使用GPU加速：确保 `WHISPER_DEVICE=cuda`
- 调整批处理大小：`WHISPER_BATCH_SIZE=4`

## 高级用法

### 自定义参数
```bash
# 指定输出文件
python test_local_transcribe.py audio.wav -o custom_output.json

# 设置超时时间（秒）
python test_local_transcribe.py audio.wav -t 1800

# 详细输出
python test_local_transcribe.py audio.wav -v

# 完整参数
python test_local_transcribe.py audio.wav -o output.json -t 3600 -v
```

### 批量处理
```bash
# 处理多个文件
for file in *.wav; do
    python test_local_transcribe.py "$file"
done
```

## 输出示例

### JSON 输出
```json
{
  "text": "这是转写的完整文本内容",
  "language": "zh",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "第一段文本",
      "speaker": "SPEAKER_00",
      "confidence": 0.95
    }
  ],
  "summary": {
    "total_duration": 120.5,
    "total_segments": 25,
    "total_speakers": 2
  }
}
```

### SRT 输出
```
1
00:00:00,000 --> 00:00:03,500
[SPEAKER_00] 第一段文本

2
00:00:03,500 --> 00:00:07,200
[SPEAKER_01] 第二段文本
```

## 下一步

- 查看详细文档：`README_TRANSCRIBE_TEST.md`
- 配置队列服务：参考主项目文档
- 集成到您的应用：使用 API 接口

祝您使用愉快！ 