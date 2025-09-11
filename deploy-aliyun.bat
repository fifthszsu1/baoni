@echo off
chcp 65001 >nul

echo 🚀 开始阿里云完整部署...

REM 停止现有容器
echo 📦 停止现有容器...
docker-compose down

REM 清理镜像
echo 🧹 清理旧镜像...
docker system prune -f

REM 检查前端构建文件
echo 🔍 检查前端构建文件...
if not exist "frontend\dist\index.html" (
    echo ⚠️  前端构建文件不存在，开始构建...
    cd frontend
    
    REM 安装依赖
    echo 📦 安装前端依赖...
    npm install
    
    REM 构建前端
    echo 🔨 构建前端...
    npm run build
    
    REM 检查构建结果
    if not exist "dist\index.html" (
        echo ❌ 前端构建失败！
        pause
        exit /b 1
    )
    
    echo ✅ 前端构建成功
    cd ..
) else (
    echo ✅ 前端构建文件已存在
)

REM 构建并启动后端
echo 🔧 构建后端...
docker-compose up -d --build backend

REM 等待后端启动
echo ⏳ 等待后端启动...
timeout /t 30 /nobreak >nul

REM 检查后端健康状态
echo 🏥 检查后端健康状态...
curl -f http://localhost:5001/health
if %errorlevel% equ 0 (
    echo ✅ 后端启动成功
) else (
    echo ❌ 后端启动失败
    docker-compose logs backend
    pause
    exit /b 1
)

REM 构建并启动前端
echo 🎨 构建前端...
docker-compose up -d --build frontend

REM 等待前端启动
echo ⏳ 等待前端启动...
timeout /t 15 /nobreak >nul

REM 检查前端文件
echo 🔍 检查前端文件...
docker exec baoni-frontend ls -la /usr/share/nginx/html/

REM 检查前端健康状态
echo 🏥 检查前端健康状态...
curl -f http://localhost:8081/
if %errorlevel% equ 0 (
    echo ✅ 前端启动成功
) else (
    echo ❌ 前端启动失败
    docker-compose logs frontend
    pause
    exit /b 1
)

REM 检查nginx配置
echo 🔧 检查nginx配置...
docker exec baoni-frontend nginx -t

echo 🎉 部署完成！
echo 📱 前端地址: http://your-server-ip:8081
echo 🔧 后端地址: http://your-server-ip:5001
echo 📚 API文档: http://your-server-ip:5001/swagger/

REM 显示容器状态
echo 📊 容器状态:
docker-compose ps

pause 