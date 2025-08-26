@echo off
chcp 65001 >nul
echo === 先构建前端再启动Docker服务 ===

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo 检查npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm
    pause
    exit /b 1
)

echo.
echo 步骤1: 进入前端目录并安装依赖...
cd frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    npm config set registry https://registry.npmmirror.com
    npm install
    if errorlevel 1 (
        echo npm install失败，尝试使用yarn...
        yarn install
        if errorlevel 1 (
            echo 前端依赖安装失败
            pause
            exit /b 1
        )
    )
) else (
    echo 前端依赖已存在
)

echo.
echo 步骤2: 构建前端...
npm run build
if errorlevel 1 (
    echo 前端构建失败
    cd ..
    pause
    exit /b 1
)

echo 前端构建成功！
cd ..

echo.
echo 步骤3: 启动Docker服务...
docker-compose down --remove-orphans
docker-compose up --build -d

echo.
echo 等待服务启动...
timeout /t 10 >nul

echo.
echo 检查服务状态...
docker-compose ps

echo.
echo 如果服务正常启动，访问地址：
echo   前端应用: http://localhost:8081
echo   后端API: http://localhost:5001
echo   API文档: http://localhost:5001/swagger/
echo.
echo 默认登录信息:
echo   用户名: baoni
echo   密码: lulu220519
echo.
pause 