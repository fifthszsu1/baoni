-- 英语读后续写打分系统默认数据插入脚本
-- 创建时间: 2025-09-16

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

USE baoni_scoring_db;

-- 插入默认教师（系统管理员）
INSERT INTO teachers (name, email, phone, school, status) VALUES 
('系统管理员', 'admin@baoni.com', '13800138000', '系统', 'active');

-- 获取刚插入的教师ID
SET @admin_teacher_id = LAST_INSERT_ID();

-- 插入默认评分规则（高中英语读后续写标准）
INSERT INTO scoring_rules (
    rule_name, 
    rule_description, 
    score_ranges, 
    max_score, 
    min_score, 
    is_default, 
    status, 
    created_by
) VALUES (
    '高中英语读后续写标准评分规则',
    '适用于高中英语读后续写题目的标准评分规则，共分为6个档次',
    JSON_OBJECT(
        '21-25分', JSON_OBJECT(
            'min_score', 21,
            'max_score', 25,
            'description', '能写到以上5-6个要点，创造了丰富、合理的内容，富有逻辑性，续写完整，与原文情境融洽度高；使用了多样且恰当的词汇和语法结构，表达流畅，语言错误很少，且完全不影响理解；自然有效地使用了段落间、语句间衔接手段，全文结构清晰，前后呼应，意义连贯。',
            'key_points', JSON_ARRAY('内容丰富合理', '逻辑性强', '续写完整', '情境融洽', '词汇语法多样', '表达流畅', '错误极少', '衔接自然', '结构清晰', '意义连贯')
        ),
        '16-20分', JSON_OBJECT(
            'min_score', 16,
            'max_score', 20,
            'description', '能写到以上5个要点，使用了比较多样且恰当的词汇和语法结构，表达比较流畅，有个别错误，但不影响理解；比较有效地使用了语句间衔接手段，全文结构比较清晰，意义比较连贯。',
            'key_points', JSON_ARRAY('5个要点', '词汇语法比较多样', '表达比较流畅', '个别错误不影响理解', '衔接比较有效', '结构比较清晰', '意义比较连贯')
        ),
        '11-15分', JSON_OBJECT(
            'min_score', 11,
            'max_score', 15,
            'description', '能写到以上4-5个要点，有一定的逻辑性，续写基本完整，与原文情境相关；表达方式不够多样性，表达有些许错误，但基本不影响理解；全文结构比较清晰，意义比较连贯。',
            'key_points', JSON_ARRAY('4-5个要点', '有一定逻辑性', '续写基本完整', '与原文相关', '表达方式不够多样', '有些许错误', '基本不影响理解', '结构比较清晰')
        ),
        '6-10分', JSON_OBJECT(
            'min_score', 6,
            'max_score', 10,
            'description', '能写到以上3-4个要点，内容和逻辑上有一些重大问题，续写不够完整，与原文有一定程度脱节；所用的词汇有限，语法结构单调，错误较多且比较低级，影响理解；全文结构不够清晰，意义欠连贯。',
            'key_points', JSON_ARRAY('3-4个要点', '内容逻辑有重大问题', '续写不够完整', '与原文脱节', '词汇有限', '语法单调', '错误较多', '影响理解', '结构不清晰')
        ),
        '1-5分', JSON_OBJECT(
            'min_score', 1,
            'max_score', 5,
            'description', '能写到以上1-2个要点，内容和逻辑上有较多重大问题，或有部分内容抄自原文，续写不完整，与原文情境基本脱节；语法结构单调，错误极多，严重影响理解；全文结构不清晰，意义不连贯。',
            'key_points', JSON_ARRAY('1-2个要点', '内容逻辑重大问题较多', '部分抄袭原文', '续写不完整', '与原文基本脱节', '语法单调', '错误极多', '严重影响理解', '结构不清晰', '意义不连贯')
        ),
        '0分', JSON_OBJECT(
            'min_score', 0,
            'max_score', 0,
            'description', '未作答；所写内容无法看清以致无法评判；所写内容全部抄自原文或与题目要求完全不相关。',
            'key_points', JSON_ARRAY('未作答', '内容无法看清', '全部抄袭', '与题目完全不相关')
        )
    ),
    25,
    0,
    TRUE,
    'active',
    @admin_teacher_id
);

-- 插入一个示例题目
INSERT INTO topics (
    title,
    content,
    content_type,
    difficulty_level,
    word_count_requirement,
    key_points,
    teacher_id,
    status
) VALUES (
    '友谊的力量',
    '阅读下面材料，根据其内容和所给段落开头语续写两段，使之构成一篇完整的短文。\n\n注意：\n1. 续写词数应为150左右；\n2. 请按如下格式在答题卡的相应位置作答。\n\n段落1开头：Looking at my best friend, I realized...\n段落2开头：From that day on, our friendship...',
    'text',
    'medium',
    '150词左右',
    JSON_ARRAY(
        '理解友谊的真正含义',
        '描述朋友间的相互支持',
        '展现友谊带来的积极变化',
        '体现友谊的珍贵价值',
        '表达对友谊的感悟',
        '续写内容与主题紧密相关'
    ),
    @admin_teacher_id,
    'active'
);

-- 插入MySQL配置优化
-- 这些配置将通过config文件设置，此处仅作说明
-- 注释：建议在 mysql/config/my.cnf 中添加以下配置：
-- [mysqld]
-- character-set-server=utf8mb4
-- collation-server=utf8mb4_unicode_ci
-- max_connections=200
-- innodb_buffer_pool_size=256M
-- innodb_log_file_size=64M 