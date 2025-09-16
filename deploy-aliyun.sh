#!/bin/bash

echo "=== 阿里云部署脚本 ==="
echo "开始部署到阿里云环境..."

# 检查是否有前端构建产物
if [ ! -d "frontend/dist" ]; then
    echo "前端构建产物不存在，开始构建前端..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "前端构建完成"
else
    echo "前端构建产物已存在，跳过构建"
fi

# 停止现有容器
echo "停止现有容器..."
docker-compose down

# 清理Docker缓存
echo "清理Docker缓存..."
docker system prune -f

# 重新构建并启动服务
echo "重新构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 检查后端健康状态
echo "检查后端健康状态..."
for i in {1..30}; do
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    else
        echo "等待后端服务启动... ($i/30)"
        sleep 2
    fi
done

# 检查前端服务
echo "检查前端服务..."
if curl -f http://localhost:8081 > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务可能未正常启动"
fi

echo ""
echo "=== 部署完成 ==="
echo "前端访问地址: http://你的服务器IP:8081"
echo "后端API地址: http://你的服务器IP:5001"
echo ""
echo "如果遇到问题，请检查Docker日志:"
echo "docker-compose logs -f" 