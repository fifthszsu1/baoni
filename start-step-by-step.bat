@echo off
chcp 65001 >nul
echo === 分步骤启动英文文本分析系统 ===

REM 设置中国镜像源
set USE_CHINA_MIRROR=true

REM 检查是否存在.env文件
if not exist ".env" (
    echo 警告: .env文件不存在，正在创建模板...
    if exist "env_template.txt" (
        copy "env_template.txt" ".env" >nul
        echo 请编辑.env文件并填入正确的配置信息！
        echo 特别注意要设置正确的Azure OpenAI配置！
    )
)

echo 步骤1: 清理旧容器和镜像...
docker-compose down --remove-orphans
docker system prune -f

echo.
echo 步骤2: 先构建和启动后端服务...
docker-compose up --build -d backend

echo.
echo 等待后端服务启动...
timeout /t 10 >nul

echo.
echo 检查后端服务状态...
docker-compose ps backend
docker-compose logs --tail=20 backend

echo.
echo 步骤3: 测试后端API是否工作...
curl -f http://localhost:5000/health 2>nul
if errorlevel 1 (
    echo 后端服务可能还没准备好，让我们查看详细日志...
    docker-compose logs backend
    echo.
    echo 是否继续构建前端？(Y/N):
    set /p continue=
    if /i not "%continue%"=="Y" goto end
) else (
    echo 后端服务启动成功！
)

echo.
echo 步骤4: 构建和启动前端服务...
docker-compose up --build -d frontend

echo.
echo 等待前端服务启动...
timeout /t 15 >nul

echo.
echo 检查所有服务状态...
docker-compose ps

echo.
echo 如果一切正常，访问地址：
echo   前端应用: http://localhost:8081
echo   后端API: http://localhost:5001
echo   API文档: http://localhost:5001/swagger/
echo.
echo 默认登录信息:
echo   用户名: baoni
echo   密码: lulu220519

:end
echo.
pause 