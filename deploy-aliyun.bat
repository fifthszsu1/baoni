@echo off
chcp 65001 > nul

echo === 阿里云部署脚本 ===
echo 开始部署到阿里云环境...

REM 检查是否有前端构建产物
if not exist "frontend\dist" (
    echo 前端构建产物不存在，开始构建前端...
    cd frontend
    call npm install
    call npm run build
    cd ..
    echo 前端构建完成
) else (
    echo 前端构建产物已存在，跳过构建
)

REM 停止现有容器
echo 停止现有容器...
docker-compose down

REM 清理Docker缓存
echo 清理Docker缓存...
docker system prune -f

REM 重新构建并启动服务
echo Rebuilding and starting services...
docker-compose up -d --build

REM 等待服务启动
echo Waiting for services to start...
timeout /t 10 > nul

REM 检查服务状态
echo Checking service status...
docker-compose ps

REM 检查后端健康状态
echo Checking backend health...
set /a count=0
:check_backend
set /a count+=1
curl -f http://localhost:5001/health > nul 2>&1
if %errorlevel% equ 0 (
    echo Backend service started successfully
    goto check_frontend
)
if %count% lss 30 (
    echo Waiting for backend service... (%count%/30)
    timeout /t 2 > nul
    goto check_backend
)

:check_frontend
REM 检查前端服务
echo Checking frontend service...
curl -f http://localhost:8081 > nul 2>&1
if %errorlevel% equ 0 (
    echo Frontend service started successfully
) else (
    echo Frontend service may not be running properly
)

echo.
echo === 部署完成 ===
echo 前端访问地址: http://你的服务器IP:8081
echo 后端API地址: http://你的服务器IP:5001
echo.
echo 如果遇到问题，请检查Docker日志:
echo docker-compose logs -f

pause 