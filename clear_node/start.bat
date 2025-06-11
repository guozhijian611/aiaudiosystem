@echo off
chcp 65001 >nul

echo ======================================
echo Clear Node 启动脚本
echo 音频清理节点 v1.0.0
echo ======================================

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt

REM 检查环境配置文件
if not exist ".env" (
    if exist ".env.example" (
        echo 复制环境配置文件...
        copy .env.example .env
        echo 请编辑 .env 文件配置相关参数
    ) else (
        echo 警告: 未找到环境配置文件
    )
)

REM 创建必要目录
echo 创建工作目录...
if not exist "work" mkdir work
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs

REM 检查ClearVoice是否存在
if not exist "ClearerVoice-Studio" (
    echo 警告: 未找到ClearerVoice-Studio目录
    echo 请确保ClearerVoice-Studio项目已正确放置在当前目录下
)

REM 设置环境变量
set PYTHONPATH=%cd%\src;%cd%\ClearerVoice-Studio\clearvoice;%PYTHONPATH%

echo ======================================
echo 启动Clear Node...
echo ======================================

REM 启动程序
python src\main.py

pause