#!/bin/bash

echo "🚀 开始阿里云完整部署..."

# 停止现有容器
echo "📦 停止现有容器..."
docker-compose down

# 清理镜像
echo "🧹 清理旧镜像..."
docker system prune -f

# 检查前端构建文件
echo "🔍 检查前端构建文件..."
if [ ! -d "frontend/dist" ] || [ ! -f "frontend/dist/index.html" ]; then
    echo "⚠️  前端构建文件不存在，开始构建..."
    cd frontend
    
    # 安装依赖
    echo "📦 安装前端依赖..."
    npm install
    
    # 构建前端
    echo "🔨 构建前端..."
    npm run build
    
    # 检查构建结果
    if [ ! -f "dist/index.html" ]; then
        echo "❌ 前端构建失败！"
        exit 1
    fi
    
    echo "✅ 前端构建成功"
    cd ..
else
    echo "✅ 前端构建文件已存在"
fi

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
sleep 15

# 检查前端文件
echo "🔍 检查前端文件..."
docker exec baoni-frontend ls -la /usr/share/nginx/html/

# 检查前端健康状态
echo "🏥 检查前端健康状态..."
if curl -f http://localhost:8081/; then
    echo "✅ 前端启动成功"
else
    echo "❌ 前端启动失败"
    docker-compose logs frontend
    exit 1
fi

# 检查nginx配置
echo "🔧 检查nginx配置..."
docker exec baoni-frontend nginx -t

echo "🎉 部署完成！"
echo "📱 前端地址: http://your-server-ip:8081"
echo "🔧 后端地址: http://your-server-ip:5001"
echo "📚 API文档: http://your-server-ip:5001/swagger/"

# 显示容器状态
echo "📊 容器状态:"
docker-compose ps 