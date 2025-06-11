FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsox-fmt-all \
    sox \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制ClearVoice项目
COPY ClearerVoice-Studio/ ./ClearerVoice-Studio/

# 复制源代码
COPY src/ ./src/
COPY .env* ./

# 创建工作目录
RUN mkdir -p /app/work /app/temp /app/logs

# 设置环境变量
ENV PYTHONPATH=/app/src:/app/ClearerVoice-Studio/clearvoice:$PYTHONPATH
ENV WORK_DIR=/app/work
ENV TEMP_DIR=/app/temp
ENV CLEARVOICE_PATH=/app/ClearerVoice-Studio/clearvoice

# 暴露端口（如果需要健康检查接口）
EXPOSE 8080

# 启动命令
CMD ["python", "src/main.py"]