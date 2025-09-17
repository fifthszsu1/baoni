#!/bin/bash

# 英语作文评分系统 - 阿里云生产环境部署脚本

echo "🚀 开始部署英语作文评分系统到阿里云..."

# 检查环境变量
if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "❌ 错误: 请设置 AZURE_OPENAI_API_KEY 环境变量"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data/mysql
mkdir -p nginx/ssl
mkdir -p uploads

# 检查SSL证书
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "⚠️  警告: SSL证书不存在，请将证书文件放置到 nginx/ssl/ 目录"
    echo "   cert.pem - SSL证书文件"
    echo "   key.pem  - SSL私钥文件"
    echo ""
    echo "💡 如果暂时没有SSL证书，可以使用以下命令生成自签名证书（仅用于测试）："
    echo "   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem"
    echo ""
    read -p "是否继续部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新Nginx配置中的域名
if [ -n "$DOMAIN_NAME" ]; then
    echo "🔧 更新域名配置: $DOMAIN_NAME"
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" nginx/conf.d/api.conf
else
    echo "⚠️  请在nginx/conf.d/api.conf中手动替换 your-domain.com 为你的实际域名"
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose -f docker-compose.prod.yml up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 初始化数据库
echo "🗄️  初始化数据库..."
python3 init_db.py

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 测试API连接
echo "🧪 测试API连接..."
if [ -n "$DOMAIN_NAME" ]; then
    curl -k https://$DOMAIN_NAME/health
else
    curl http://localhost/health
fi

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 部署信息："
echo "   - MySQL端口: 3307"
echo "   - HTTP端口: 80"
echo "   - HTTPS端口: 443"
echo "   - API基础URL: https://$DOMAIN_NAME/api/"
echo ""
echo "🔧 后续配置："
echo "   1. 确保阿里云安全组开放了 80、443 端口"
echo "   2. 在小程序管理后台配置域名白名单"
echo "   3. 配置域名DNS解析到服务器IP"
echo ""
echo "📖 API文档: https://$DOMAIN_NAME/api/swagger/"
echo ""
echo "🎉 系统已就绪，可以开始使用！" 