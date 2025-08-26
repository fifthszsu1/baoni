@echo off
chcp 65001 >nul
echo === 离线模式启动（只启动后端服务）===

echo 检查.env文件...
if not exist ".env" (
    echo 警告: .env文件不存在，正在创建模板...
    if exist "env_template.txt" (
        copy "env_template.txt" ".env" >nul
        echo 请编辑.env文件并填入正确的Azure OpenAI配置！
    )
)

echo.
echo 步骤1: 清理旧容器...
docker-compose down --remove-orphans

echo.
echo 步骤2: 只构建和启动后端服务...
docker-compose up --build -d backend

echo.
echo 等待后端服务启动...
timeout /t 15 >nul

echo.
echo 检查后端服务状态...
docker-compose ps backend
docker-compose logs --tail=10 backend

echo.
echo 测试后端API...
curl -f http://localhost:5001/health
if errorlevel 1 (
    echo 后端服务可能还没准备好，查看详细日志：
    docker-compose logs backend
) else (
    echo 后端服务启动成功！
)

echo.
echo 后端服务访问地址：
echo   后端API: http://localhost:5001
echo   API文档: http://localhost:5001/swagger/
echo.
echo 您可以：
echo   1. 直接使用API接口（通过Postman等工具）
echo   2. 稍后手动启动前端：cd frontend && npm run serve
echo   3. 稍后构建前端容器：docker-compose up --build -d frontend
echo.
echo 默认登录信息:
echo   用户名: baoni
echo   密码: lulu220519
echo.
pause 