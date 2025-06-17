@echo off
chcp 65001
echo ========================================
echo        Translate2 Node 启动脚本
echo ========================================

REM 检查 conda 是否安装
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Conda 未安装，请先安装 Conda
    echo 下载地址: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM 检查环境配置文件
if not exist ".env" (
    echo 创建环境配置文件...
    copy .env.example .env
    echo 请编辑 .env 文件配置相关参数，然后重新运行此脚本
    echo 主要配置项：
    echo   - HF_TOKEN: Hugging Face Token（必需）
    echo   - RABBITMQ_HOST: RabbitMQ 服务器地址
    echo   - API_BASE_URL: 后端 API 地址
    pause
    exit /b 1
)

REM 检查 conda 环境是否存在
conda env list | findstr "whisper-diarization" >nul
if %errorlevel% neq 0 (
    echo 创建 conda 环境...
    conda env create -f environment.yml
)

REM 激活环境
echo 激活 conda 环境...
call conda activate whisper-diarization

REM 检查 Whisper-Diarization 是否安装
if not exist "whisper-diarization" (
    echo 安装 Whisper-Diarization...
    git clone https://github.com/guillaumekln/whisper-diarization.git
    cd whisper-diarization
    pip install -e .
    cd ..
)

REM 创建必要的目录
echo 创建必要的目录...
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "work" mkdir work
if not exist "models" mkdir models

REM 启动服务
echo 启动 Translate2 Node 服务...
python main.py

pause 