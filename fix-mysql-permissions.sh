#!/bin/bash

# MySQL权限问题修复脚本

echo "🔧 修复MySQL权限和配置问题..."

# 1. 完全停止和清理MySQL相关容器
echo "1. 停止并清理MySQL容器..."
docker-compose down
docker container rm baoni-mysql 2>/dev/null || true
docker volume rm baoni_mysql_data 2>/dev/null || true

# 2. 清理数据目录并设置正确权限
echo "2. 清理数据目录并设置权限..."
rm -rf data/mysql
mkdir -p data/mysql
chmod 755 data/mysql

# 3. 使用简化的MySQL配置
echo "3. 使用简化的MySQL配置..."
cp mysql/config/mysql8-simple.cnf mysql/config/my.cnf
echo "✅ 配置文件已更新为简化版本"

# 4. 创建必要的目录
echo "4. 创建必要的目录..."
mkdir -p mysql/logs
chmod 755 mysql/logs

# 5. 修改docker-compose.yml使用更简单的配置
echo "5. 临时修改docker-compose配置..."
cat > docker-compose-temp.yml << 'EOF'
services:
  mysql:
    image: mysql:8.0
    container_name: baoni-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: BaoniRoot@2025
      MYSQL_DATABASE: baoni_scoring_db
      MYSQL_USER: baoni_user
      MYSQL_PASSWORD: baoni_password
    ports:
      - "3307:3306"
    volumes:
      - ./data/mysql:/var/lib/mysql
    networks:
      - baoni-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: baoni-backend
    ports:
      - "5001:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - DATABASE_URL=mysql+pymysql://baoni_user:baoni_password@mysql:3306/baoni_scoring_db?charset=utf8mb4
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
    networks:
      - baoni-network
    restart: unless-stopped
    depends_on:
      mysql:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: baoni-frontend
    ports:
      - "8081:80"
    depends_on:
      - backend
    networks:
      - baoni-network
    restart: unless-stopped
    environment:
      - VUE_APP_API_BASE_URL=""

networks:
  baoni-network:
    driver: bridge

volumes:
  uploads-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./uploads
EOF

# 6. 启动MySQL服务
echo "6. 启动MySQL服务（使用临时配置）..."
docker-compose -f docker-compose-temp.yml up -d mysql

# 7. 等待MySQL完全启动
echo "7. 等待MySQL完全启动..."
echo "这可能需要1-2分钟，请耐心等待..."

for i in {1..60}; do
    if docker exec baoni-mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "✅ MySQL启动成功！"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "❌ MySQL启动超时"
        docker logs baoni-mysql
        exit 1
    fi
    echo "等待MySQL启动... ($i/60)"
    sleep 2
done

# 8. 测试数据库连接
echo "8. 测试数据库连接..."
if docker exec baoni-mysql mysql -u root -pBaoniRoot@2025 -e "SELECT 1;" 2>/dev/null; then
    echo "✅ 数据库连接测试成功！"
else
    echo "❌ 数据库连接测试失败"
    docker logs baoni-mysql
    exit 1
fi

# 9. 创建数据库和用户（如果需要）
echo "9. 确保数据库和用户存在..."
docker exec baoni-mysql mysql -u root -pBaoniRoot@2025 -e "
CREATE DATABASE IF NOT EXISTS baoni_scoring_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'baoni_user'@'%' IDENTIFIED BY 'baoni_password';
GRANT ALL PRIVILEGES ON baoni_scoring_db.* TO 'baoni_user'@'%';
FLUSH PRIVILEGES;
" 2>/dev/null

echo "✅ 数据库和用户配置完成"

# 10. 启动其他服务
echo "10. 启动后端和前端服务..."
docker-compose -f docker-compose-temp.yml up -d

# 11. 等待所有服务启动
echo "11. 等待所有服务启动..."
sleep 20

# 12. 检查服务状态
echo "12. 检查服务状态..."
docker-compose -f docker-compose-temp.yml ps

# 13. 初始化数据库
echo "13. 初始化数据库表和数据..."
if command -v python3 &> /dev/null; then
    python3 init_db.py
elif command -v python &> /dev/null; then
    python init_db.py
else
    echo "⚠️ Python未找到，请手动运行 python init_db.py"
fi

echo ""
echo "🎉 MySQL修复完成！"
echo ""
echo "📋 服务信息："
echo "   - MySQL: localhost:3307"
echo "   - 后端API: http://localhost:5001"
echo "   - 前端: http://localhost:8081"
echo ""
echo "🔧 后续步骤："
echo "   1. 验证服务正常：curl http://localhost:5001/health"
echo "   2. 如果一切正常，可以将 docker-compose-temp.yml 重命名为 docker-compose.yml"
echo "   3. 或者将简化配置合并到原始的 docker-compose.yml 中"
echo ""
echo "📝 注意：此次使用了简化配置，去除了可能导致权限问题的日志配置" 