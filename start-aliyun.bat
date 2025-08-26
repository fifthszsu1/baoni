@echo off
chcp 65001 >nul

echo 🚀 开始阿里云部署...

REM 停止现有容器
echo 📦 停止现有容器...
docker-compose down

REM 清理镜像（可选）
echo 🧹 清理旧镜像...
docker system prune -f

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
timeout /t 10 /nobreak >nul

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

echo 🎉 部署完成！
echo 📱 前端地址: http://localhost:8081
echo 🔧 后端地址: http://localhost:5001
echo 📚 API文档: http://localhost:5001/swagger/

pause 