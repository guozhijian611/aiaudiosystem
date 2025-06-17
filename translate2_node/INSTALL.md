# Translate2 Node 安装指南

## 快速安装

### 方法一：使用安装脚本（推荐）

#### Linux/Mac
```bash
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd translate2_node

# 运行安装脚本
chmod +x install.sh
./install.sh
```

#### Windows
```cmd
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd translate2_node

# 运行安装脚本
install.bat
```

### 方法二：手动安装

#### 1. 创建 conda 环境
```bash
conda env create -f environment.yml
conda activate whisper-diarization
```

#### 2. 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装 Whisper-Diarization 专用依赖
pip install wget nemo_toolkit[asr]==2.0.0rc0 nltk faster-whisper>=1.1.0

# 安装 GitHub 依赖
pip install git+https://github.com/MahmoudAshraf97/demucs.git
pip install git+https://github.com/oliverguhr/deepmultilingualpunctuation.git
pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git
```

#### 3. 克隆 Whisper-Diarization
```bash
git clone https://github.com/guillaumekln/whisper-diarization.git
```

#### 4. 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件，设置您的配置
```

## 依赖说明

### 核心依赖
- **PyTorch**: 深度学习框架
- **Whisper**: OpenAI 的语音识别模型
- **Faster Whisper**: 优化的 Whisper 实现
- **NeMo**: NVIDIA 的语音处理工具包

### Whisper-Diarization 专用依赖
- **CTC Forced Aligner**: 强制对齐工具
- **Demucs**: 音频分离工具
- **Deep Multilingual Punctuation**: 多语言标点符号模型
- **Pyannote Audio**: 说话人分离工具

### 系统依赖
- **FFmpeg**: 音频处理工具
- **Git**: 版本控制工具
- **Conda**: 环境管理工具

## 配置说明

### 必需配置
1. **HF_TOKEN**: Huggingface 访问令牌（用于说话人分离）
   - 访问 https://huggingface.co/settings/tokens
   - 创建新的访问令牌
   - 添加到 `.env` 文件

2. **Whisper 模型**: 选择合适的模型
   - `large-v3`: 最高精度，需要更多资源
   - `medium`: 平衡精度和速度
   - `small`: 快速处理
   - `base`: 最快，精度最低

### 可选配置
- **设备选择**: `cuda` (GPU) 或 `cpu`
- **批处理大小**: 根据内存调整
- **说话人数量**: 设置最小/最大说话人数

## 验证安装

### 运行测试
```bash
# 基础功能测试
python test.py

# 转写功能测试
python test_local_transcribe.py your_audio.wav
```

### 检查模块
```bash
# 运行模块检查
python install_dependencies.py
```

## 常见问题

### 1. 安装失败
**问题**: `ModuleNotFoundError: No module named 'xxx'`
**解决**: 重新运行安装脚本或手动安装缺失的模块

### 2. 内存不足
**问题**: CUDA out of memory
**解决**: 
- 减小 `WHISPER_BATCH_SIZE`
- 使用较小的模型
- 使用 CPU 设备

### 3. 说话人分离未生效
**问题**: 说话人分离功能被禁用
**解决**:
- 检查 `HF_TOKEN` 是否正确设置
- 确认 `ENABLE_DIARIZATION=true`
- 验证 whisper-diarization 目录存在

### 4. 转写速度慢
**问题**: 转写处理时间过长
**解决**:
- 使用 GPU 加速
- 选择较小的模型
- 调整批处理大小

## 性能优化

### 硬件要求
- **GPU**: NVIDIA GPU with 8GB+ VRAM (推荐)
- **CPU**: 多核 CPU (至少 4 核)
- **内存**: 16GB+ RAM
- **存储**: SSD 推荐

### 软件优化
- 使用 conda 环境管理依赖
- 定期清理缓存文件
- 监控系统资源使用

## 下一步

安装完成后，您可以：
1. 运行转写测试
2. 配置队列服务
3. 集成到您的应用
4. 查看详细文档

更多信息请参考：
- `README_TRANSCRIBE_TEST.md`: 转写测试指南
- `QUICK_START.md`: 快速开始指南
- 主项目文档 