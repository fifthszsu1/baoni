# 英语读后续写AI打分系统

## 系统概述

这是一个基于AI的英语读后续写自动打分系统，专为高中英语教学设计。系统能够：

1. 接收题目（文本或图片）
2. 管理评分规则
3. OCR识别学生手写作文
4. AI自动评分和反馈
5. 支持多教师使用

## 系统架构

### 数据库设计

**【Linus式数据结构分析】**
- **核心数据流**: 题目 → 学生作文图片 → OCR文本 → AI评分 → 存储结果
- **数据所有权清晰**: 每个作文属于特定题目和评分规则，教师拥有题目
- **无特殊情况**: 统一的数据结构，无需复杂的条件分支

#### 1. 教师表 (teachers)
```sql
- id: 主键
- name: 教师姓名  
- email: 邮箱（唯一）
- phone: 电话
- school: 学校
- status: 状态(active/inactive)
```

#### 2. 评分规则表 (scoring_rules)
```sql
- id: 主键
- rule_name: 规则名称
- rule_description: 规则描述
- score_ranges: JSON格式的分数档次
- max_score/min_score: 分数范围
- is_default: 是否默认规则
- created_by: 创建教师ID
```

#### 3. 题目表 (topics)
```sql
- id: 主键
- title: 题目标题
- content: 题目内容
- content_type: 内容类型(text/image)
- image_url: 图片URL（如果是图片题目）
- difficulty_level: 难度(easy/medium/hard)
- key_points: JSON格式的关键要点
- teacher_id: 创建教师ID
```

#### 4. 学生作文表 (compositions)
```sql
- id: 主键
- student_name: 学生姓名（OCR识别）
- student_id: 学生学号
- topic_id: 题目ID
- scoring_rule_id: 评分规则ID
- original_image_url: 原始图片URL
- ocr_text: OCR识别文本
- composition_content: 提取的作文内容
- ai_score: AI评分
- ai_feedback: AI反馈
- manual_score: 人工评分
- processing_status: 处理状态
- word_count: 字数统计
```

## 部署说明

### 1. 数据库配置

系统使用MySQL 8.0，端口配置为3307（避免与其他项目冲突）：

```yaml
# docker-compose.yml中的MySQL配置
mysql:
  image: mysql:8.0
  container_name: baoni-mysql
  ports:
    - "3307:3306"  # 避免端口冲突
  environment:
    MYSQL_ROOT_PASSWORD: BaoniRoot@2025
    MYSQL_DATABASE: baoni_scoring_db
    MYSQL_USER: baoni_user
    MYSQL_PASSWORD: baoni_password
```

### 2. 启动系统

```bash
# 1. 启动Docker服务
docker-compose up -d

# 2. 初始化数据库（可选）
python init_db.py

# 3. 查看服务状态
docker-compose ps
```

### 3. 访问地址

- **API文档**: http://localhost:5001/swagger/
- **前端界面**: http://localhost:8081
- **健康检查**: http://localhost:5001/health

## 业务流程

### 1. 题目管理
- 教师可以创建文本或图片题目
- 图片题目需要OCR识别转换为文本
- 每个题目关联关键要点用于评分

### 2. 评分规则管理
- 系统预设标准评分规则（0-25分，6个档次）
- 教师可以创建自定义评分规则
- 评分规则包含详细的档次描述和关键要点

### 3. 作文评分流程
```
小程序上传图片 → OCR识别文本 → AI解析学生信息 → 
AI评分和反馈 → 存储结果 → 返回评分结果
```

### 4. 处理状态跟踪
- `pending`: 待处理
- `processing`: 处理中  
- `completed`: 处理完成
- `failed`: 处理失败

## 预设评分规则

系统预设了高中英语读后续写标准评分规则：

| 档次 | 分数范围 | 主要特征 |
|------|----------|----------|
| 优秀 | 21-25分 | 内容丰富，逻辑清晰，语言流畅，错误极少 |
| 良好 | 16-20分 | 要点完整，表达比较流畅，个别错误不影响理解 |
| 中等 | 11-15分 | 要点基本完整，有一定逻辑性，有些许错误 |
| 及格 | 6-10分 | 要点不够完整，逻辑有问题，错误较多 |
| 不及格 | 1-5分 | 要点很少，逻辑混乱，错误极多 |
| 零分 | 0分 | 未作答或完全不相关 |

## 技术特点

**【Linus式设计原则体现】**

1. **"好品味"设计**
   - 数据结构简洁清晰，无冗余字段
   - 统一的JSON存储复杂数据（评分规则、关键要点）
   - 消除了特殊情况，所有评分都走相同流程

2. **实用主义**
   - 解决真实的教育场景问题
   - 支持人工评分覆盖AI评分
   - 完整的错误处理和状态跟踪

3. **向后兼容**
   - 数据库表设计考虑扩展性
   - API接口版本化
   - 支持多种题目类型和评分规则

4. **简洁性**
   - 4个核心表，关系清晰
   - 业务逻辑直观，无过度抽象
   - 配置简单，部署容易

## 环境要求

- Python 3.8+
- MySQL 8.0
- Docker & Docker Compose
- 阿里云环境（支持OCR和AI服务）

## 开发计划

- [x] 数据库设计和初始化
- [x] Docker配置和部署脚本
- [x] 数据模型定义
- [ ] OCR服务集成
- [ ] AI评分服务
- [ ] 小程序API接口
- [ ] 管理后台界面
- [ ] 性能优化和监控

## 编码问题解决

**【重要】中文编码配置**

系统已完整配置UTF-8编码支持，确保中文数据正确存储：

1. **MySQL配置** (`mysql/config/my.cnf`)
   ```ini
   character-set-server=utf8mb4
   collation-server=utf8mb4_unicode_ci
   ```

2. **数据库连接** (`config.py`)
   ```python
   DATABASE_URL = '...?charset=utf8mb4'
   connect_args = {'charset': 'utf8mb4', 'use_unicode': True}
   ```

3. **SQL脚本** (所有.sql文件开头)
   ```sql
   SET NAMES utf8mb4;
   SET CHARACTER SET utf8mb4;
   ```

4. **验证编码**
   ```bash
   python test_encoding.py  # 测试中文数据存储和读取
   ```

## 注意事项

1. **端口配置**: MySQL使用3307端口，避免与tb-wei项目冲突
2. **数据安全**: 生产环境需要修改默认密码
3. **图片存储**: 建议使用阿里云OSS存储图片
4. **并发处理**: AI评分可能耗时，建议使用异步队列
5. **日志监控**: 重要操作需要记录日志便于排查
6. **中文编码**: 已配置完整的UTF-8支持，如遇乱码请检查客户端编码设置 