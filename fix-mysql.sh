#!/bin/bash

# MySQL 8.0 问题修复脚本

echo "🔧 修复MySQL 8.0配置问题..."

# 停止现有的MySQL容器
echo "1. 停止现有MySQL容器..."
docker-compose down mysql
docker container rm baoni-mysql 2>/dev/null || true

# 清理旧的数据（如果需要重新初始化）
read -p "是否清理MySQL数据目录？这将删除所有数据！(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  清理MySQL数据目录..."
    sudo rm -rf data/mysql/*
    echo "✅ 数据目录已清理"
fi

# 创建日志目录
echo "2. 创建必要的目录..."
mkdir -p data/mysql
mkdir -p mysql/logs
chmod 755 mysql/logs

# 使用优化的配置文件
echo "3. 使用MySQL 8.0优化配置..."
if [ -f "mysql/config/mysql8-optimized.cnf" ]; then
    cp mysql/config/my.cnf mysql/config/my.cnf.backup
    cp mysql/config/mysql8-optimized.cnf mysql/config/my.cnf
    echo "✅ 配置文件已更新"
fi

# 启动MySQL服务
echo "4. 启动MySQL服务..."
docker-compose up -d mysql

# 等待MySQL启动
echo "5. 等待MySQL启动..."
sleep 30

# 检查MySQL状态
echo "6. 检查MySQL状态..."
docker-compose logs mysql | tail -20

# 测试连接
echo "7. 测试数据库连接..."
sleep 10

if docker exec baoni-mysql mysqladmin ping -h localhost --silent; then
    echo "✅ MySQL启动成功！"
    
    # 初始化数据库
    echo "8. 初始化数据库..."
    python3 init_db.py
    
    echo "🎉 MySQL修复完成！"
else
    echo "❌ MySQL启动失败，请检查日志："
    docker-compose logs mysql
    exit 1
fi 