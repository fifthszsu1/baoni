#!/usr/bin/env python3
"""
数据库编码测试脚本
验证中文数据是否正确存储和读取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, ScoringRule, Teacher
import json

def test_encoding():
    """测试数据库编码"""
    app = create_app()
    
    with app.app_context():
        try:
            # 测试插入中文数据
            print("🧪 开始测试数据库编码...")
            
            # 查询现有的评分规则
            rules = ScoringRule.query.all()
            print(f"📋 找到 {len(rules)} 个评分规则")
            
            if rules:
                rule = rules[0]
                print(f"\n📝 评分规则名称: {rule.rule_name}")
                print(f"📝 评分规则描述: {rule.rule_description}")
                
                if rule.score_ranges:
                    print("\n📊 评分档次:")
                    for range_name, range_info in rule.score_ranges.items():
                        print(f"  {range_name}: {range_info.get('description', '')[:50]}...")
                        key_points = range_info.get('key_points', [])
                        if key_points:
                            print(f"    关键要点: {', '.join(key_points[:3])}...")
                
                # 测试中文是否显示正确
                test_chinese = "高中英语读后续写标准评分规则"
                if rule.rule_name == test_chinese:
                    print("✅ 中文数据存储和读取正常")
                else:
                    print(f"❌ 中文数据可能有问题:")
                    print(f"  期望: {test_chinese}")
                    print(f"  实际: {rule.rule_name}")
                    print(f"  字节长度: {len(rule.rule_name.encode('utf-8'))}")
            else:
                print("⚠️ 数据库中没有评分规则数据")
                
            # 测试插入新的中文数据
            print("\n🧪 测试插入新的中文数据...")
            
            # 查找管理员教师
            admin = Teacher.query.filter_by(email='admin@baoni.com').first()
            if not admin:
                print("❌ 未找到管理员教师，请先运行 init_db.py")
                return
            
            # 创建测试评分规则
            test_rule = ScoringRule(
                rule_name='测试中文编码规则',
                rule_description='这是一个测试中文编码的规则，包含各种中文字符：汉字、标点符号等。',
                score_ranges={
                    "优秀": {
                        "min_score": 90,
                        "max_score": 100,
                        "description": "表现优秀，语言流畅，逻辑清晰，内容丰富。",
                        "key_points": ["内容丰富", "逻辑清晰", "语言流畅", "表达准确"]
                    },
                    "良好": {
                        "min_score": 80,
                        "max_score": 89,
                        "description": "表现良好，基本达到要求，有少量错误。",
                        "key_points": ["基本达标", "少量错误", "表达清楚"]
                    }
                },
                max_score=100,
                min_score=0,
                is_default=False,
                status='active',
                created_by=admin.id
            )
            
            db.session.add(test_rule)
            db.session.commit()
            
            # 立即查询验证
            saved_rule = ScoringRule.query.filter_by(rule_name='测试中文编码规则').first()
            if saved_rule:
                print(f"✅ 测试规则插入成功: {saved_rule.rule_name}")
                print(f"📝 描述: {saved_rule.rule_description}")
                
                # 验证JSON中的中文
                if saved_rule.score_ranges:
                    for range_name, range_info in saved_rule.score_ranges.items():
                        print(f"  档次 {range_name}: {range_info.get('description', '')}")
                
                # 删除测试数据
                db.session.delete(saved_rule)
                db.session.commit()
                print("🗑️ 测试数据已清理")
            else:
                print("❌ 测试规则插入失败")
                
        except Exception as e:
            print(f"❌ 编码测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_encoding() 