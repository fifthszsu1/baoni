# 直接使用nginx镜像
FROM nginx:latest

# 先构建前端（本地构建，避免网络问题）
# 注意：这需要您本地先运行 npm run build

# 复制构建好的前端文件
COPY dist/ /usr/share/nginx/html/

# 复制nginx配置  
COPY nginx.conf /etc/nginx/nginx.conf

# 安装curl用于健康检查
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 创建日志目录
RUN mkdir -p /var/log/nginx

# 设置权限
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"] 