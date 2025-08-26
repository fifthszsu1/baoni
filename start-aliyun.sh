#!/bin/bash

# 阿里云部署脚本 - 简化版本
echo "🚀 开始阿里云部署..."

# 停止现有容器
echo "📦 停止现有容器..."
docker-compose down

# 清理镜像（可选）
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建并启动后端
echo "🔧 构建后端..."
docker-compose up -d --build backend

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 30

# 检查后端健康状态
echo "🏥 检查后端健康状态..."
if curl -f http://localhost:5001/health; then
    echo "✅ 后端启动成功"
else
    echo "❌ 后端启动失败"
    docker-compose logs backend
    exit 1
fi

# 构建并启动前端
echo "🎨 构建前端..."
docker-compose up -d --build frontend

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 10

# 检查前端健康状态
echo "🏥 检查前端健康状态..."
if curl -f http://localhost:8081/; then
    echo "✅ 前端启动成功"
else
    echo "❌ 前端启动失败"
    docker-compose logs frontend
    exit 1
fi

echo "🎉 部署完成！"
echo "📱 前端地址: http://localhost:8081"
echo "🔧 后端地址: http://localhost:5001"
echo "📚 API文档: http://localhost:5001/swagger/" 