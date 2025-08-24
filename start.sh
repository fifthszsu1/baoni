#!/bin/bash

echo "=================================="
echo " 英文文本分析与XMind生成服务"
echo "=================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 使用python3或python命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，请确保已配置Azure OpenAI相关环境变量"
    echo
    echo "请参考.env.example文件创建.env配置文件"
    echo
fi

# 检查依赖是否安装
echo "检查Python依赖包..."
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "安装依赖包..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败"
        exit 1
    fi
fi

# 创建uploads目录
mkdir -p uploads

echo
echo "启动服务..."
echo "服务地址: http://localhost:5000"
echo "Swagger文档: http://localhost:5000/swagger/"
echo "健康检查: http://localhost:5000/health"
echo
echo "按 Ctrl+C 停止服务"
echo

# 启动Flask应用
$PYTHON_CMD app.py 