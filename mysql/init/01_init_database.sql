-- 英语读后续写打分系统数据库初始化脚本
-- 创建时间: 2025-09-16

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

USE baoni_scoring_db;

-- 1. 教师表
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '教师姓名',
    email VARCHAR(255) UNIQUE COMMENT '教师邮箱',
    phone VARCHAR(20) COMMENT '联系电话',
    school VARCHAR(255) COMMENT '学校名称',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师表';

-- 2. 评分规则表
CREATE TABLE IF NOT EXISTS scoring_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_description TEXT COMMENT '规则描述',
    score_ranges JSON NOT NULL COMMENT '分数档次和描述，JSON格式存储',
    max_score INT NOT NULL DEFAULT 25 COMMENT '最高分数',
    min_score INT NOT NULL DEFAULT 0 COMMENT '最低分数',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认规则',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    created_by INT COMMENT '创建者ID，关联teachers表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_rule_name (rule_name),
    INDEX idx_is_default (is_default),
    INDEX idx_status (status),
    FOREIGN KEY (created_by) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评分规则表';

-- 3. 题目表
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '题目标题',
    content TEXT NOT NULL COMMENT '题目内容',
    content_type ENUM('text', 'image') DEFAULT 'text' COMMENT '内容类型：文本或图片',
    image_url VARCHAR(500) COMMENT '题目图片URL（如果是图片类型）',
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium' COMMENT '难度等级',
    word_count_requirement VARCHAR(50) COMMENT '字数要求，如"150词左右"',
    key_points JSON COMMENT '关键要点，JSON格式存储',
    teacher_id INT COMMENT '创建题目的教师ID',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_title (title),
    INDEX idx_content_type (content_type),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_status (status),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';

-- 4. 学生作文表
CREATE TABLE IF NOT EXISTS compositions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) COMMENT '学生姓名（从图片OCR识别）',
    student_id VARCHAR(50) COMMENT '学生学号（如果能识别到）',
    topic_id INT NOT NULL COMMENT '对应的题目ID',
    scoring_rule_id INT NOT NULL COMMENT '使用的评分规则ID',
    original_image_url VARCHAR(500) NOT NULL COMMENT '原始手写图片URL',
    ocr_text TEXT COMMENT 'OCR识别出的文本内容',
    composition_content TEXT COMMENT '提取出的作文内容（去除姓名等）',
    ai_score DECIMAL(5,2) COMMENT 'AI给出的分数',
    ai_feedback TEXT COMMENT 'AI评分反馈',
    manual_score DECIMAL(5,2) COMMENT '人工评分（如果有）',
    manual_feedback TEXT COMMENT '人工评分反馈',
    word_count INT COMMENT '作文字数统计',
    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '处理状态',
    error_message TEXT COMMENT '错误信息（如果处理失败）',
    teacher_id INT COMMENT '批改教师ID',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    processed_at TIMESTAMP NULL COMMENT '处理完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_student_name (student_name),
    INDEX idx_topic_id (topic_id),
    INDEX idx_scoring_rule_id (scoring_rule_id),
    INDEX idx_processing_status (processing_status),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_submitted_at (submitted_at),
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE RESTRICT,
    FOREIGN KEY (scoring_rule_id) REFERENCES scoring_rules(id) ON DELETE RESTRICT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生作文表';

-- 创建一些额外的索引优化查询性能
CREATE INDEX idx_compositions_score_range ON compositions(ai_score);
CREATE INDEX idx_compositions_word_count ON compositions(word_count);
CREATE INDEX idx_topics_created_at ON topics(created_at);
CREATE INDEX idx_compositions_created_at ON compositions(created_at); 