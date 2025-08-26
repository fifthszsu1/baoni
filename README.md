# 英文文本分析系统

一个前后端分离的英文文本分析系统，采用Vue.js前端 + Flask后端架构。系统可以接收英文文本（特别适合高中阅读理解文章），使用Azure OpenAI进行智能分析，提取主要思想和结构，并在前端直接展示思维导图。

## 功能特性

- 🔍 **智能文本分析**: 使用Azure OpenAI GPT模型深度分析英文文本
- 📊 **结构化解读**: 提取文章主题、论点、细节和语言特色
- 🧠 **在线思维导图**: 前端直接展示可交互的思维导图，支持缩放和导航
- 📚 **教育导向**: 特别优化用于高中英语阅读理解分析
- 🔐 **用户认证**: JWT Token认证机制，安全可靠
- 🎨 **现代UI**: 基于Element Plus的美观用户界面
- 🐳 **Docker部署**: 一键部署，支持Docker Compose
- 🌐 **前后端分离**: Vue.js前端 + Flask后端，架构清晰
- 📖 **API文档**: 完整的Swagger API文档

## 技术栈

### 后端
- **框架**: Flask 3.0.0
- **API文档**: Flask-RESTX (Swagger UI)
- **认证**: JWT Token
- **AI服务**: Azure OpenAI GPT
- **配置管理**: python-dotenv

### 前端
- **框架**: Vue.js 3.3.0
- **UI组件**: Element Plus 2.3.0
- **状态管理**: Pinia 2.1.0
- **路由**: Vue Router 4.2.0
- **HTTP客户端**: Axios 1.4.0

### 部署
- **容器化**: Docker & Docker Compose
- **Web服务器**: Nginx (前端反向代理)

## 快速开始

### 使用Docker部署（推荐）

#### 1. 环境要求
- Docker 和 Docker Compose
- 8GB 内存（推荐）

#### 2. 配置环境变量
将 `env_template.txt` 复制为 `.env` 并配置：

```env
# Azure OpenAI配置（必须填写）
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4
AZURE_API_VERSION=2025-01-01-preview

# 用户认证配置
LOGIN_USERNAME=baoni
LOGIN_PASSWORD=lulu220519

# 其他配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

#### 3. 启动服务

**Linux/macOS:**
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**Windows:**
```batch
start-docker.bat
```

**手动启动:**
```bash
docker-compose up --build -d
```

#### 4. 访问应用
- **前端应用**: http://localhost:8081
- **后端API**: http://localhost:5001
- **API文档**: http://localhost:5001/swagger/

#### 5. 默认登录信息
- **用户名**: baoni
- **密码**: lulu220519

### 本地开发部署

#### 后端
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp env_template.txt .env
# 编辑.env文件

# 启动后端服务
python app.py
```

#### 前端
```bash
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run serve
```

## 系统使用

### 登录系统
1. 访问前端应用 http://localhost:8081
2. 使用默认账号登录：`baoni` / `lulu220519`
3. 登录成功后进入主界面

### 分析文本
1. 在文本框中输入英文文本（至少50个字符）
2. 点击"分析文本"按钮
3. 等待AI分析完成
4. 查看思维导图和文字分析结果

### API接口

#### 认证接口
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/verify` - 验证Token

#### 分析接口
- `POST /api/analyze/text` - 分析文本（需认证）
- `GET /api/analyze/test` - 测试连接

#### 文档
- `GET /swagger/` - Swagger API文档

**API请求需要在Header中包含认证信息:**
```
Authorization: Bearer <jwt_token>
```

## 文本要求

- **最小长度**: 50个字符
- **最大长度**: 10,000个字符  
- **语言要求**: 主要包含英文内容
- **适用类型**: 阅读理解文章、议论文、说明文等

## 输出格式

### Markdown分析结果包含：
1. **主题概要** - 文章核心主题
2. **文章结构** - 逻辑结构分析
3. **关键论点** - 主要观点和论据
4. **重要细节** - 关键事实和例证
5. **语言特色** - 写作风格和修辞手法
6. **阅读理解要点** - 考试重点和难点提示

### XMind思维导图：
- 结构化的可视化展示
- 层次清晰的知识点组织
- 便于复习和理解的格式

## 项目结构
```
baoni/
├── app.py                     # Flask主应用
├── config.py                  # 配置文件
├── requirements.txt           # Python依赖包
├── services/                  # 服务层
│   ├── auth_service.py        # 认证服务
│   ├── openai_service.py      # Azure OpenAI服务
│   └── xmind_service.py       # 思维导图解析服务
├── routes/                    # 路由层
│   └── api_routes.py          # API路由定义
├── utils/                     # 工具函数
│   └── helpers.py             # 辅助函数
├── uploads/                   # 上传文件存储
├── frontend/                  # Vue.js前端
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── views/             # 页面
│   │   ├── store/             # 状态管理
│   │   ├── router/            # 路由配置
│   │   └── api/               # API接口封装
│   ├── public/                # 静态文件
│   ├── package.json           # Node.js依赖
│   └── Dockerfile             # 前端Docker配置
├── docker-compose.yml         # Docker编排配置
├── Dockerfile.backend         # 后端Docker配置
├── start-docker.sh            # Docker启动脚本(Linux/macOS)
├── start-docker.bat           # Docker启动脚本(Windows)
├── env_template.txt           # 环境变量模板
└── README.md                  # 项目说明
```

## 开发指南

### 添加新的分析功能
1. 在 `services/openai_service.py` 中修改提示词模板
2. 在 `services/xmind_service.py` 中调整结构解析逻辑
3. 更新API模型定义

### 自定义XMind样式
修改 `services/xmind_service.py` 中的 `create_xmind_from_structure` 方法。

## Docker管理命令

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 清理缓存和重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 生产环境部署

### 1. 安全配置
- 修改默认用户名和密码
- 使用强密钥替换 `SECRET_KEY`
- 配置HTTPS
- 设置防火墙规则

### 2. 性能优化
- 使用生产级数据库
- 配置Redis缓存
- 启用Nginx gzip压缩
- 设置CDN加速

### 3. 监控和日志
- 配置日志聚合
- 设置健康检查
- 监控资源使用情况

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请创建Issue或联系项目维护者。 