#!/bin/bash

# Translate Node 运行脚本

# 检查环境是否存在
if ! conda env list | grep -q "whisperx"; then
    echo "错误: whisperx 环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 检查配置文件
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在，请创建并配置环境变量"
    exit 1
fi

echo "启动 Translate Node..."
echo "配置信息:"
echo "- 队列: $(grep QUEUE_NAME .env || echo 'transcribe_queue')"
echo "- RabbitMQ: $(grep RABBITMQ_HOST .env || echo 'localhost')"
echo "- API: $(grep API_BASE_URL .env || echo 'http://localhost:8787')"
echo ""

# 激活环境并运行
conda run -n whisperx python main.py 