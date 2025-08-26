#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 英文文本分析系统 Docker 启动脚本 ===${NC}"

# 检查是否存在.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: .env文件不存在，正在创建模板...${NC}"
    if [ -f "env_template.txt" ]; then
        cp env_template.txt .env
        echo -e "${YELLOW}请编辑.env文件并填入正确的配置信息！${NC}"
        echo -e "${RED}特别注意要设置正确的Azure OpenAI配置！${NC}"
    else
        echo -e "${RED}错误: 找不到env_template.txt模板文件${NC}"
        exit 1
    fi
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker没有运行，请先启动Docker${NC}"
    exit 1
fi

# 检查Docker Compose是否可用
if ! command -v docker-compose > /dev/null 2>&1; then
    echo -e "${RED}错误: docker-compose未安装${NC}"
    exit 1
fi

echo -e "${GREEN}正在构建和启动服务...${NC}"

# 构建并启动服务
docker-compose up --build -d

# 检查服务状态
echo -e "${GREEN}正在检查服务状态...${NC}"
sleep 5

backend_status=$(docker-compose ps -q backend | xargs docker inspect -f '{{.State.Status}}')
frontend_status=$(docker-compose ps -q frontend | xargs docker inspect -f '{{.State.Status}}')

echo -e "${GREEN}服务状态:${NC}"
echo -e "后端服务: ${backend_status}"
echo -e "前端服务: ${frontend_status}"

if [ "$backend_status" = "running" ] && [ "$frontend_status" = "running" ]; then
    echo -e "${GREEN}✓ 所有服务已成功启动！${NC}"
    echo -e "${GREEN}访问地址:${NC}"
    echo -e "  前端应用: ${YELLOW}http://localhost:8081${NC}"
    echo -e "  后端API: ${YELLOW}http://localhost:5001${NC}"
    echo -e "  API文档: ${YELLOW}http://localhost:5001/swagger/${NC}"
    echo ""
    echo -e "${GREEN}默认登录信息:${NC}"
    echo -e "  用户名: ${YELLOW}baoni${NC}"
    echo -e "  密码: ${YELLOW}lulu220519${NC}"
else
    echo -e "${RED}× 服务启动失败，请检查日志:${NC}"
    echo -e "${YELLOW}查看日志命令: docker-compose logs${NC}"
fi

echo ""
echo -e "${GREEN}常用命令:${NC}"
echo -e "  查看日志: ${YELLOW}docker-compose logs -f${NC}"
echo -e "  停止服务: ${YELLOW}docker-compose down${NC}"
echo -e "  重启服务: ${YELLOW}docker-compose restart${NC}" 