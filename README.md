# 英文文本分析与XMind生成服务

一个基于Flask的web服务，可以接收英文文本（特别适合高中阅读理解文章），使用Azure OpenAI进行智能分析，提取主要思想和结构，并生成XMind格式的思维导图文件。

## 功能特性

- 🔍 **智能文本分析**: 使用Azure OpenAI GPT模型深度分析英文文本
- 📊 **结构化解读**: 提取文章主题、论点、细节和语言特色
- 🧠 **思维导图生成**: 自动生成XMind格式的可视化思维导图
- 📚 **教育导向**: 特别优化用于高中英语阅读理解分析
- 🌐 **RESTful API**: 标准的REST接口，易于集成
- 📖 **Swagger文档**: 完整的API文档和在线测试界面

## 技术栈

- **后端框架**: Flask 3.0.0
- **API文档**: Flask-RESTX (Swagger UI)
- **AI服务**: Azure OpenAI GPT-5-chat
- **思维导图**: xmind 1.2.0
- **配置管理**: python-dotenv

## 安装与配置

### 1. 环境要求
- Python 3.8+
- pip包管理器

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
将 `.env.example` 复制为 `.env`，并配置以下环境变量：

```env
AZURE_OPENAI_API_KEY=你的Azure_OpenAI_API密钥
AZURE_OPENAI_ENDPOINT=你的Azure_OpenAI端点
AZURE_DEPLOYMENT_NAME=你的模型部署名称
AZURE_API_VERSION=API版本
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### 4. 启动服务
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API接口

### Swagger文档
访问 `http://localhost:5000/swagger/` 查看完整的API文档和在线测试界面。

### 主要接口

#### 1. 文本分析 - POST `/api/analyze/text`
分析英文文本并生成XMind思维导图。

**请求示例**:
```json
{
    "text": "Education is the most powerful weapon which you can use to change the world. Nelson Mandela's words ring true today more than ever. In an era of rapid technological advancement and global interconnectedness, the role of education has evolved significantly..."
}
```

**响应示例**:
```json
{
    "success": true,
    "analysis": "# 文章分析\n\n## 1. 主题概要\n- 教育的重要性和变革力量...",
    "xmind_filename": "analysis_20250823_220745_abc123def.xmind",
    "download_url": "/downloads/analysis_20250823_220745_abc123def.xmind",
    "tokens_used": 1250
}
```

#### 2. 连接测试 - GET `/api/analyze/test`
测试Azure OpenAI服务连接状态。

#### 3. 文件下载 - GET `/downloads/<filename>`
下载生成的XMind文件。

#### 4. 健康检查 - GET `/health`
检查服务运行状态。

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
├── app.py                  # Flask主应用
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── services/              # 服务层
│   ├── openai_service.py  # Azure OpenAI服务
│   └── xmind_service.py   # XMind生成服务
├── routes/                # 路由层
│   └── api_routes.py      # API路由定义
├── utils/                 # 工具函数
│   └── helpers.py         # 辅助函数
├── uploads/               # 生成文件存储
└── README.md             # 项目说明
```

## 开发指南

### 添加新的分析功能
1. 在 `services/openai_service.py` 中修改提示词模板
2. 在 `services/xmind_service.py` 中调整结构解析逻辑
3. 更新API模型定义

### 自定义XMind样式
修改 `services/xmind_service.py` 中的 `create_xmind_from_structure` 方法。

## 部署建议

### 生产环境配置
- 设置 `FLASK_ENV=production`
- 配置反向代理（如Nginx）
- 使用WSGI服务器（如Gunicorn）
- 设置日志记录和监控

### Docker部署
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请创建Issue或联系项目维护者。 