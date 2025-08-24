@echo off
echo ==================================
echo  英文文本分析与XMind生成服务
echo ==================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 设置环境变量（如果.env文件不存在）
if not exist ".env" (
    echo 警告: 未找到.env文件，请确保已配置Azure OpenAI相关环境变量
    echo.
    echo 请参考.env.example文件创建.env配置文件
    echo.
)

REM 检查依赖是否安装
echo 检查Python依赖包...
pip list | findstr "Flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 创建uploads目录
if not exist "uploads" mkdir uploads

echo.
echo 启动服务...
echo 服务地址: http://localhost:5000
echo Swagger文档: http://localhost:5000/swagger/
echo 健康检查: http://localhost:5000/health
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动Flask应用
python app.py

pause 