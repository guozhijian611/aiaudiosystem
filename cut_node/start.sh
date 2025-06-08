#!/bin/bash

# Cut Node 启动脚本

set -e

echo "================================================="
echo "           Cut Node 启动脚本"
echo "================================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置相关参数，然后重新运行此脚本"
    echo "主要配置项："
    echo "  - RABBITMQ_HOST: RabbitMQ 服务器地址"
    echo "  - API_BASE_URL: 后端 API 地址"
    exit 1
fi

# 检查是否需要构建镜像
if [ "$1" = "--build" ] || [ "$1" = "-b" ]; then
    echo "重新构建 Docker 镜像..."
    docker-compose build --no-cache
fi

# 停止现有服务
echo "停止现有服务..."
docker-compose down

# 启动服务
echo "启动 Cut Node 服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 显示日志
echo ""
echo "================================================="
echo "服务启动完成！"
echo ""
echo "查看日志: docker-compose logs -f cut_node"
echo "查看状态: docker-compose ps"
echo "停止服务: docker-compose down"
echo ""
echo "RabbitMQ 管理界面: http://localhost:15672"
echo "用户名: guest, 密码: guest"
echo "================================================="

# 询问是否查看日志
read -p "是否查看实时日志？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f cut_node
fi