# Translate2 Node 优化安装指南

## 依赖文件说明

### environment.yml - Conda 环境配置
- 包含所有基础依赖和 PyTorch 相关包
- 使用 conda 安装更稳定
- 包含 CUDA 支持

### requirements.txt - Pip 依赖配置
- 包含 Python 包依赖
- 与 environment.yml 互补，无重复
- 适合 pip 安装

## 安装步骤

### 方法一：使用 Conda（推荐）

#### 1. 创建环境
```bash
conda env create -f environment.yml
conda activate whisper-diarization
```

#### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

#### 3. 安装 GitHub 依赖
```bash
python install_github_deps.py
```

### 方法二：使用 Pip

#### 1. 创建虚拟环境
```bash
python -m venv whisper-diarization
source whisper-diarization/bin/activate  # Linux/Mac
# 或
whisper-diarization\Scripts\activate     # Windows
```

#### 2. 安装 PyTorch
```bash
# Windows + CUDA
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Windows + CPU
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Linux/Mac
pip install torch torchaudio
```

#### 3. 安装其他依赖
```bash
pip install -r requirements.txt
```

#### 4. 安装 GitHub 依赖
```bash
python install_github_deps.py
```

## 依赖分类说明

### 基础依赖
- `pika`, `requests`, `python-dotenv`, `psutil`, `loguru`
- 用于队列通信、HTTP 请求、配置管理等

### 音频处理
- `librosa`, `soundfile`, `resampy`
- 用于音频文件读取、格式转换等

### Whisper 相关
- `openai-whisper`, `faster-whisper`, `ctranslate2`
- 核心语音识别功能

### Transformers 生态
- `transformers`, `datasets`, `accelerate`, `huggingface_hub`
- 用于模型加载和推理

### 说话人分离
- `pyannote-audio`, `pyannote-core`, `torch-audiomentations`
- 用于说话人识别和分离

### NeMo 工具包
- `nemo_toolkit[asr]`
- NVIDIA 的语音处理工具包

### 其他工具
- `sentencepiece`, `omegaconf`, `wget`, `nltk`
- 辅助工具和库

### GitHub 依赖
- `demucs` - 音频分离
- `deepmultilingualpunctuation` - 多语言标点符号
- `ctc-forced-aligner` - CTC 强制对齐

## 故障排除

### PyTorch 问题
```bash
# Windows 修复
python fix_windows_torch.py

# 通用修复
python fix_torchaudio.py
```

### 兼容性问题
```bash
# 升级到最新版本
python upgrade_to_latest.py

# 测试兼容性
python test_compatibility.py
```

### GitHub 依赖问题
```bash
# 重新安装 GitHub 依赖
python install_github_deps.py
```

## 验证安装

### 1. 基础测试
```bash
python test_compatibility.py
```

### 2. 转写测试
```bash
python test_local_transcribe.py your_audio.wav
```

### 3. 示例测试
```bash
python example_transcribe.py
```

## 性能优化

### 硬件要求
- **GPU**: NVIDIA GPU with 8GB+ VRAM (推荐)
- **CPU**: 多核 CPU (至少 4 核)
- **内存**: 16GB+ RAM
- **存储**: SSD 推荐

### 配置建议
- 使用 conda 环境管理依赖
- 根据 GPU 内存调整批处理大小
- 选择合适的 Whisper 模型大小

## 常见问题

### 1. 依赖冲突
- 使用 conda 环境隔离
- 按顺序安装依赖
- 避免版本冲突

### 2. 编译问题
- 使用预编译的 wheel 包
- 确保 C++ 编译器可用
- 使用 conda 安装复杂依赖

### 3. 网络问题
- 使用国内镜像源
- 配置代理
- 手动下载 wheel 文件

## 下一步

安装完成后：
1. 配置 `.env` 文件
2. 运行转写测试
3. 集成到您的应用
4. 查看详细文档 