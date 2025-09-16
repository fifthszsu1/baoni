#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和插入测试数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Teacher, ScoringRule, Topic, Composition
import json

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 检查是否已有数据
            if Teacher.query.first():
                print("⚠️ 数据库已有数据，跳过初始化")
                return
            
            # 创建默认教师
            admin_teacher = Teacher(
                name='系统管理员',
                email='admin@baoni.com',
                phone='13800138000',
                school='系统',
                status='active'
            )
            db.session.add(admin_teacher)
            db.session.commit()
            print("✅ 默认教师创建成功")
            
            # 创建默认评分规则
            score_ranges = {
                "21-25分": {
                    "min_score": 21,
                    "max_score": 25,
                    "description": "能写到以上5-6个要点，创造了丰富、合理的内容，富有逻辑性，续写完整，与原文情境融洽度高；使用了多样且恰当的词汇和语法结构，表达流畅，语言错误很少，且完全不影响理解；自然有效地使用了段落间、语句间衔接手段，全文结构清晰，前后呼应，意义连贯。",
                    "key_points": ["内容丰富合理", "逻辑性强", "续写完整", "情境融洽", "词汇语法多样", "表达流畅", "错误极少", "衔接自然", "结构清晰", "意义连贯"]
                },
                "16-20分": {
                    "min_score": 16,
                    "max_score": 20,
                    "description": "能写到以上5个要点，使用了比较多样且恰当的词汇和语法结构，表达比较流畅，有个别错误，但不影响理解；比较有效地使用了语句间衔接手段，全文结构比较清晰，意义比较连贯。",
                    "key_points": ["5个要点", "词汇语法比较多样", "表达比较流畅", "个别错误不影响理解", "衔接比较有效", "结构比较清晰", "意义比较连贯"]
                },
                "11-15分": {
                    "min_score": 11,
                    "max_score": 15,
                    "description": "能写到以上4-5个要点，有一定的逻辑性，续写基本完整，与原文情境相关；表达方式不够多样性，表达有些许错误，但基本不影响理解；全文结构比较清晰，意义比较连贯。",
                    "key_points": ["4-5个要点", "有一定逻辑性", "续写基本完整", "与原文相关", "表达方式不够多样", "有些许错误", "基本不影响理解", "结构比较清晰"]
                },
                "6-10分": {
                    "min_score": 6,
                    "max_score": 10,
                    "description": "能写到以上3-4个要点，内容和逻辑上有一些重大问题，续写不够完整，与原文有一定程度脱节；所用的词汇有限，语法结构单调，错误较多且比较低级，影响理解；全文结构不够清晰，意义欠连贯。",
                    "key_points": ["3-4个要点", "内容逻辑有重大问题", "续写不够完整", "与原文脱节", "词汇有限", "语法单调", "错误较多", "影响理解", "结构不清晰"]
                },
                "1-5分": {
                    "min_score": 1,
                    "max_score": 5,
                    "description": "能写到以上1-2个要点，内容和逻辑上有较多重大问题，或有部分内容抄自原文，续写不完整，与原文情境基本脱节；语法结构单调，错误极多，严重影响理解；全文结构不清晰，意义不连贯。",
                    "key_points": ["1-2个要点", "内容逻辑重大问题较多", "部分抄袭原文", "续写不完整", "与原文基本脱节", "语法单调", "错误极多", "严重影响理解", "结构不清晰", "意义不连贯"]
                },
                "0分": {
                    "min_score": 0,
                    "max_score": 0,
                    "description": "未作答；所写内容无法看清以致无法评判；所写内容全部抄自原文或与题目要求完全不相关。",
                    "key_points": ["未作答", "内容无法看清", "全部抄袭", "与题目完全不相关"]
                }
            }
            
            default_rule = ScoringRule(
                rule_name='高中英语读后续写标准评分规则',
                rule_description='适用于高中英语读后续写题目的标准评分规则，共分为6个档次',
                score_ranges=score_ranges,
                max_score=25,
                min_score=0,
                is_default=True,
                status='active',
                created_by=admin_teacher.id
            )
            db.session.add(default_rule)
            db.session.commit()
            print("✅ 默认评分规则创建成功")
            
            # 创建示例题目
            sample_topic = Topic(
                title='友谊的力量',
                content='阅读下面材料，根据其内容和所给段落开头语续写两段，使之构成一篇完整的短文。\n\n注意：\n1. 续写词数应为150左右；\n2. 请按如下格式在答题卡的相应位置作答。\n\n段落1开头：Looking at my best friend, I realized...\n段落2开头：From that day on, our friendship...',
                content_type='text',
                difficulty_level='medium',
                word_count_requirement='150词左右',
                key_points=[
                    '理解友谊的真正含义',
                    '描述朋友间的相互支持',
                    '展现友谊带来的积极变化',
                    '体现友谊的珍贵价值',
                    '表达对友谊的感悟',
                    '续写内容与主题紧密相关'
                ],
                teacher_id=admin_teacher.id,
                status='active'
            )
            db.session.add(sample_topic)
            db.session.commit()
            print("✅ 示例题目创建成功")
            
            print("\n🎉 数据库初始化完成！")
            print(f"📊 教师数量: {Teacher.query.count()}")
            print(f"📋 评分规则数量: {ScoringRule.query.count()}")
            print(f"📝 题目数量: {Topic.query.count()}")
            print(f"📄 作文数量: {Composition.query.count()}")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_database() 