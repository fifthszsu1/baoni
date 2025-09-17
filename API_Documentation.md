# 英语读后续写AI打分系统 - 小程序API文档

## 概述

本文档描述了英语读后续写AI打分系统为小程序提供的RESTful API接口。系统提供完整的作文评分流程：题目管理、图片OCR识别、AI智能评分、结果查询等功能。

**基础信息**
- **基础URL**: `http://localhost:5001/api/miniprogram`
- **内容类型**: `application/json` (除文件上传接口)
- **字符编码**: `UTF-8`
- **API版本**: `v1.0`

## 核心业务流程

```
1. 获取题目列表 → 2. 选择题目和评分规则 → 3. 拍照上传作文 → 
4. 系统OCR识别 → 5. AI评分处理 → 6. 返回评分结果
```

---

## 🎯 题目管理接口

### 1. 获取题目列表

**接口地址**: `GET /topics`

**功能描述**: 获取可用的题目列表，支持分页和筛选

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| teacher_id | int | 否 | 教师ID，筛选特定教师的题目 | 1 |
| difficulty | string | 否 | 难度等级：easy/medium/hard | medium |
| page | int | 否 | 页码，默认1 | 1 |
| per_page | int | 否 | 每页数量，默认20 | 10 |

**请求示例**:
```bash
GET /api/miniprogram/topics?difficulty=medium&page=1&per_page=10
```

**响应示例**:
```json
[
  {
    "id": 1,
    "title": "友谊的力量",
    "content": "阅读下面材料，根据其内容和所给段落开头语续写两段...",
    "content_type": "text",
    "difficulty_level": "medium",
    "word_count_requirement": "150词左右",
    "key_points": [
      "理解友谊的真正含义",
      "描述朋友间的相互支持",
      "展现友谊带来的积极变化"
    ],
    "created_at": "2025-09-16T08:30:00Z"
  }
]
```

### 2. 获取题目详情

**接口地址**: `GET /topics/{topic_id}`

**功能描述**: 获取指定题目的详细信息

**路径参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| topic_id | int | 是 | 题目ID |

**请求示例**:
```bash
GET /api/miniprogram/topics/1
```

**响应示例**:
```json
{
  "id": 1,
  "title": "友谊的力量",
  "content": "阅读下面材料，根据其内容和所给段落开头语续写两段，使之构成一篇完整的短文...",
  "content_type": "text",
  "difficulty_level": "medium",
  "word_count_requirement": "150词左右",
  "key_points": [
    "理解友谊的真正含义",
    "描述朋友间的相互支持",
    "展现友谊带来的积极变化",
    "体现友谊的珍贵价值",
    "表达对友谊的感悟",
    "续写内容与主题紧密相关"
  ],
  "created_at": "2025-09-16T08:30:00Z"
}
```

---

## 📏 评分规则接口

### 3. 获取评分规则列表

**接口地址**: `GET /scoring-rules`

**功能描述**: 获取可用的评分规则列表

**请求示例**:
```bash
GET /api/miniprogram/scoring-rules
```

**响应示例**:
```json
[
  {
    "id": 1,
    "rule_name": "高中英语读后续写标准评分规则",
    "rule_description": "适用于高中英语读后续写题目的标准评分规则，共分为6个档次",
    "max_score": 25,
    "min_score": 0,
    "is_default": true
  }
]
```

---

## 📝 作文提交与评分接口

### 4. 提交作文图片（核心接口）

**接口地址**: `POST /compositions/submit`

**功能描述**: 上传学生手写作文图片，系统自动进行OCR识别、信息提取和AI评分

**请求方式**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| image | file | 是 | 作文图片文件(PNG/JPG/JPEG/GIF/BMP) | - |
| topic_id | int | 是 | 题目ID | 1 |
| scoring_rule_id | int | 是 | 评分规则ID | 1 |
| teacher_id | int | 否 | 教师ID | 1 |

**请求示例**:
```bash
curl -X POST \
  http://localhost:5001/api/miniprogram/compositions/submit \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@composition.jpg' \
  -F 'topic_id=1' \
  -F 'scoring_rule_id=1' \
  -F 'teacher_id=1'
```

**响应示例**:
```json
{
  "success": true,
  "message": "作文提交成功，评分完成",
  "data": {
    "composition_id": 123,
    "student_name": "张三",
    "student_id": null,
    "score": 18.5,
    "score_range": "16-20分",
    "word_count": 145,
    "feedback": "详细评价：这篇续写作文在内容和语言方面表现良好...\n\n优点：内容与主题相关; 语法结构比较多样; 表达比较流畅\n\n不足：个别词汇使用不够准确; 部分句子结构可以更加丰富\n\n建议：增加更多高级词汇; 注意句式变化; 加强逻辑连贯性",
    "processing_time": 15.6
  }
}
```

**错误响应示例**:
```json
{
  "success": false,
  "message": "OCR识别失败: 图片中未识别到文本内容",
  "data": null
}
```

---

## 📊 查询接口

### 5. 获取作文详情

**接口地址**: `GET /compositions/{composition_id}`

**功能描述**: 获取指定作文的详细信息和评分结果

**路径参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| composition_id | int | 是 | 作文ID |

**请求示例**:
```bash
GET /api/miniprogram/compositions/123
```

**响应示例**:
```json
{
  "composition_id": 123,
  "student_name": "张三",
  "student_id": null,
  "score": 18.5,
  "score_range": "16-20分",
  "word_count": 145,
  "feedback": "详细评价：这篇续写作文在内容和语言方面表现良好...",
  "processing_status": "completed",
  "submitted_at": "2025-09-16T10:30:00Z",
  "processed_at": "2025-09-16T10:30:15Z"
}
```

### 6. 获取作文列表

**接口地址**: `GET /compositions`

**功能描述**: 获取作文列表，支持多种筛选条件

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| student_name | string | 否 | 学生姓名（模糊搜索） | 张 |
| topic_id | int | 否 | 题目ID | 1 |
| teacher_id | int | 否 | 教师ID | 1 |
| status | string | 否 | 处理状态：pending/processing/completed/failed | completed |
| page | int | 否 | 页码，默认1 | 1 |
| per_page | int | 否 | 每页数量，默认20 | 10 |

**请求示例**:
```bash
GET /api/miniprogram/compositions?student_name=张&status=completed&page=1&per_page=10
```

**响应示例**:
```json
[
  {
    "composition_id": 123,
    "student_name": "张三",
    "student_id": null,
    "score": 18.5,
    "word_count": 145,
    "processing_status": "completed",
    "submitted_at": "2025-09-16T10:30:00Z",
    "processed_at": "2025-09-16T10:30:15Z"
  }
]
```

---

## 🔧 管理接口

### 9. 创建评分规则

**接口地址**: `POST /admin/scoring-rules`

**功能描述**: 创建新的评分规则

**请求方式**: `application/json`

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| rule_name | string | 是 | 评分规则名称 | "自定义评分规则" |
| rule_description | string | 否 | 规则描述 | "适用于特定类型的作文评分" |
| max_score | int | 是 | 最高分数 | 25 |
| min_score | int | 是 | 最低分数 | 0 |
| score_ranges | object | 是 | 分数档次JSON对象 | 见下方示例 |
| is_default | boolean | 否 | 是否为默认规则 | false |
| teacher_id | int | 否 | 创建教师ID | 1 |

**score_ranges格式示例**:
```json
{
  "21-25分": {
    "min_score": 21,
    "max_score": 25,
    "description": "优秀：内容丰富，逻辑清晰，语言流畅",
    "key_points": ["内容丰富", "逻辑清晰", "语言流畅"]
  },
  "16-20分": {
    "min_score": 16,
    "max_score": 20,
    "description": "良好：内容较完整，表达较流畅",
    "key_points": ["内容较完整", "表达较流畅"]
  }
}
```

**请求示例**:
```bash
curl -X POST \
  http://localhost:5001/api/miniprogram/admin/scoring-rules \
  -H 'Content-Type: application/json' \
  -d '{
    "rule_name": "自定义评分规则",
    "rule_description": "适用于特定类型的作文评分",
    "max_score": 25,
    "min_score": 0,
    "score_ranges": {
      "21-25分": {
        "min_score": 21,
        "max_score": 25,
        "description": "优秀：内容丰富，逻辑清晰，语言流畅",
        "key_points": ["内容丰富", "逻辑清晰", "语言流畅"]
      }
    },
    "is_default": false,
    "teacher_id": 1
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "评分规则创建成功",
  "data": {
    "id": 2,
    "rule_name": "自定义评分规则",
    "rule_description": "适用于特定类型的作文评分",
    "max_score": 25,
    "min_score": 0,
    "is_default": false,
    "status": "active",
    "created_at": "2025-09-16T12:30:00Z"
  }
}
```

### 10. 创建题目

**接口地址**: `POST /admin/topics`

**功能描述**: 创建新题目，支持文本输入或图片OCR识别两种方式

#### 方式一：文本题目创建

**请求方式**: `application/json`

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| title | string | 是 | 题目标题 | "环境保护的重要性" |
| content | string | 是 | 题目内容 | "阅读下面材料，根据其内容..." |
| content_type | string | 是 | 内容类型，固定为"text" | "text" |
| difficulty_level | string | 是 | 难度等级：easy/medium/hard | "medium" |
| word_count_requirement | string | 否 | 字数要求 | "150词左右" |
| key_points | array | 否 | 关键要点列表 | ["环保意识", "具体措施"] |
| teacher_id | int | 否 | 创建教师ID | 1 |

**请求示例**:
```bash
curl -X POST \
  http://localhost:5001/api/miniprogram/admin/topics \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "环境保护的重要性",
    "content": "阅读下面材料，根据其内容和所给段落开头语续写两段...",
    "content_type": "text",
    "difficulty_level": "medium",
    "word_count_requirement": "150词左右",
    "key_points": ["环保意识", "具体措施", "个人责任"],
    "teacher_id": 1
  }'
```

#### 方式二：图片题目创建（OCR识别）

**请求方式**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| image | file | 是 | 题目图片文件 | - |
| title | string | 是 | 题目标题 | "环境保护的重要性" |
| difficulty_level | string | 是 | 难度等级：easy/medium/hard | "medium" |
| word_count_requirement | string | 否 | 字数要求 | "150词左右" |
| key_points | string | 否 | 关键要点（JSON数组字符串或逗号分割） | '["环保意识", "具体措施"]' |
| teacher_id | int | 否 | 创建教师ID | 1 |

**请求示例**:
```bash
curl -X POST \
  http://localhost:5001/api/miniprogram/admin/topics \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@topic_image.jpg' \
  -F 'title=环境保护的重要性' \
  -F 'difficulty_level=medium' \
  -F 'word_count_requirement=150词左右' \
  -F 'key_points=["环保意识", "具体措施", "个人责任"]' \
  -F 'teacher_id=1'
```

**响应示例**:
```json
{
  "success": true,
  "message": "题目创建成功（已完成OCR识别）",
  "data": {
    "id": 2,
    "title": "环境保护的重要性",
    "content": "阅读下面材料，根据其内容和所给段落开头语续写两段，使之构成一篇完整的短文...",
    "content_type": "image",
    "image_url": "/downloads/topic_abc123_image.jpg",
    "difficulty_level": "medium",
    "word_count_requirement": "150词左右",
    "key_points": ["环保意识", "具体措施", "个人责任"],
    "status": "active",
    "created_at": "2025-09-16T12:35:00Z",
    "ocr_confidence": 85.6,
    "ocr_lines_count": 12
  }
}
```

---

## 👨‍🏫 辅助接口

### 7. 获取教师列表

**接口地址**: `GET /teachers`

**功能描述**: 获取系统中的教师列表

**请求示例**:
```bash
GET /api/miniprogram/teachers
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "系统管理员",
      "school": "系统"
    }
  ]
}
```

### 8. 健康检查

**接口地址**: `GET /health`

**功能描述**: 检查系统服务状态

**请求示例**:
```bash
GET /api/miniprogram/health
```

**响应示例**:
```json
{
  "success": true,
  "message": "服务正常",
  "data": {
    "database": "connected",
    "ocr_service": "available",
    "timestamp": "2025-09-16T10:30:00Z"
  }
}
```

---

## 🔧 技术规范

### HTTP状态码

| 状态码 | 描述 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述信息",
  "data": null
}
```

### 数据格式说明

#### 处理状态 (processing_status)
- `pending`: 待处理
- `processing`: 处理中
- `completed`: 处理完成
- `failed`: 处理失败

#### 难度等级 (difficulty_level)
- `easy`: 简单
- `medium`: 中等
- `hard`: 困难

#### 内容类型 (content_type)
- `text`: 文本题目
- `image`: 图片题目

---

## 💡 小程序开发建议

### 1. 图片上传优化
```javascript
// 推荐的图片压缩配置
wx.compressImage({
  src: tempFilePath,
  quality: 80,  // 压缩质量
  success: (res) => {
    // 使用压缩后的图片上传
    this.uploadComposition(res.tempFilePath);
  }
});
```

### 2. 错误处理
```javascript
// 统一错误处理
const handleApiError = (error) => {
  if (error.success === false) {
    wx.showToast({
      title: error.message || '操作失败',
      icon: 'error'
    });
  }
};
```

### 3. 加载状态管理
```javascript
// 作文提交时显示加载状态
wx.showLoading({
  title: '正在识别和评分...',
  mask: true
});

// 完成后隐藏加载
wx.hideLoading();
```

### 4. 轮询查询结果（如果需要异步处理）
```javascript
// 如果评分是异步的，可以轮询查询结果
const pollResult = (compositionId) => {
  const timer = setInterval(() => {
    wx.request({
      url: `/api/miniprogram/compositions/${compositionId}`,
      success: (res) => {
        if (res.data.processing_status === 'completed') {
          clearInterval(timer);
          // 显示评分结果
          this.showResult(res.data);
        }
      }
    });
  }, 2000); // 每2秒查询一次
};
```

### 5. 管理功能使用
```javascript
// 创建评分规则
const createScoringRule = (ruleData) => {
  wx.request({
    url: '/api/miniprogram/admin/scoring-rules',
    method: 'POST',
    header: {
      'content-type': 'application/json'
    },
    data: ruleData,
    success: (res) => {
      if (res.data.success) {
        wx.showToast({
          title: '评分规则创建成功',
          icon: 'success'
        });
      }
    }
  });
};

// 从图片创建题目
const createTopicFromImage = (imagePath, topicData) => {
  wx.uploadFile({
    url: '/api/miniprogram/admin/topics',
    filePath: imagePath,
    name: 'image',
    formData: topicData,
    success: (res) => {
      const result = JSON.parse(res.data);
      if (result.success) {
        wx.showToast({
          title: '题目创建成功',
          icon: 'success'
        });
      }
    }
  });
};
```

---

## 🚀 部署和测试

### 本地测试环境
```bash
# 启动服务
docker-compose up -d

# 初始化数据库
python init_db.py

# 测试健康检查
curl http://localhost:5001/api/miniprogram/health
```

### API文档访问
- **Swagger UI**: http://localhost:5001/swagger/
- **在线测试**: 可直接在Swagger界面测试所有接口

### 示例数据
系统启动后会自动创建：
- 默认教师：系统管理员
- 默认评分规则：高中英语读后续写标准评分规则
- 示例题目：友谊的力量

---

## 📞 技术支持

如有技术问题，请检查：
1. 数据库连接是否正常
2. OCR服务是否可用（需要安装Tesseract）
3. Azure OpenAI配置是否正确
4. 图片格式和大小是否符合要求

系统日志可以帮助定位问题，建议在开发阶段开启详细日志记录。 