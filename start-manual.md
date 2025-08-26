# 手动启动指南

## 方案1: 完全本地开发（推荐）

### 1. 启动后端
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
copy env_template.txt .env
# 编辑.env文件，填入Azure OpenAI配置

# 启动Flask后端
python app.py
```

### 2. 启动前端
```bash
cd frontend

# 安装依赖
npm config set registry https://registry.npmmirror.com
npm install

# 启动开发服务器
npm run serve
```

### 3. 访问地址
- 前端: http://localhost:8081
- 后端: http://localhost:5001

## 方案2: 只用Docker启动后端

### 1. 启动后端容器
```bash
docker-compose up --build -d backend
```

### 2. 本地启动前端
```bash
cd frontend
npm run serve
```

## 方案3: 手动构建前端 + Docker

### 1. 本地构建前端
```bash
cd frontend
npm install
npm run build
cd ..
```

### 2. 启动所有服务
```bash
docker-compose up --build -d
```

## 故障排除

### 网络问题解决方案
1. **设置npm镜像源**:
   ```bash
   npm config set registry https://registry.npmmirror.com
   ```

2. **设置pip镜像源**:
   ```bash
   pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
   ```

3. **Docker镜像加速器**:
   - 在Docker Desktop设置中添加镜像加速器
   - 阿里云: https://registry.cn-hangzhou.aliyuncs.com

### 常用命令
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs backend
docker-compose logs frontend

# 停止服务
docker-compose down

# 重新构建
docker-compose build --no-cache
``` 