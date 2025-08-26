@echo off
chcp 65001 >nul
echo === 英文文本分析系统 Docker 启动脚本 (中国版) ===

REM 设置中国镜像源
set USE_CHINA_MIRROR=true

REM 检查是否存在.env文件
if not exist ".env" (
    echo 警告: .env文件不存在，正在创建模板...
    if exist "env_template.txt" (
        copy "env_template.txt" ".env" >nul
        echo 请编辑.env文件并填入正确的配置信息！
        echo 特别注意要设置正确的Azure OpenAI配置！
    ) else (
        echo 错误: 找不到env_template.txt模板文件
        pause
        exit /b 1
    )
)

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker没有运行，请先启动Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否可用
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: docker-compose未安装或不可用
    pause
    exit /b 1
)

echo 正在使用中国镜像源构建和启动服务...
echo 如果仍然遇到网络问题，请检查网络连接或尝试使用VPN

REM 清理旧容器和镜像
echo 清理旧的容器和镜像...
docker-compose down --remove-orphans
docker system prune -f

REM 构建并启动服务
docker-compose up --build -d

REM 等待服务启动
echo 正在检查服务状态...
timeout /t 10 >nul

echo 服务启动完成！
echo.
echo 访问地址:
echo   前端应用: http://localhost:8081
echo   后端API: http://localhost:5001
echo   API文档: http://localhost:5001/swagger/
echo.
echo 默认登录信息:
echo   用户名: baoni
echo   密码: lulu220519
echo.
echo 如果服务启动有问题，请检查日志: docker-compose logs
echo 如果仍有网络问题，可以尝试:
echo   1. 重启Docker服务
echo   2. 使用VPN
echo   3. 配置Docker镜像加速器
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo.
pause 