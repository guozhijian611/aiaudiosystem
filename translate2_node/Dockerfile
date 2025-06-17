# 使用官方Python 3.11运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY main.py .
COPY config.py .
COPY .env.example .env

# 创建必要的目录
RUN mkdir -p /app/work /app/temp /app/logs /app/models

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app/src'); from api_client import APIClient; sys.exit(0 if APIClient().health_check() else 1)"

# 暴露端口（虽然这个服务不需要，但为了规范）
EXPOSE 8080

# 运行应用
CMD ["python", "/app/main.py"] 