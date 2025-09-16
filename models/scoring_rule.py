from datetime import datetime
import json
from . import db

class ScoringRule(db.Model):
    """评分规则模型"""
    __tablename__ = 'scoring_rules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rule_name = db.Column(db.String(100), nullable=False, comment='规则名称')
    rule_description = db.Column(db.Text, comment='规则描述')
    score_ranges = db.Column(db.JSON, nullable=False, comment='分数档次和描述，JSON格式存储')
    max_score = db.Column(db.Integer, nullable=False, default=25, comment='最高分数')
    min_score = db.Column(db.Integer, nullable=False, default=0, comment='最低分数')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认规则')
    status = db.Column(db.Enum('active', 'inactive'), default='active', comment='状态')
    created_by = db.Column(db.Integer, db.ForeignKey('teachers.id'), comment='创建者ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    compositions = db.relationship('Composition', backref='scoring_rule', lazy='dynamic')
    
    def __repr__(self):
        return f'<ScoringRule {self.rule_name}>'
    
    def get_score_range_for_score(self, score):
        """根据分数获取对应的档次信息"""
        if not self.score_ranges:
            return None
            
        for range_name, range_info in self.score_ranges.items():
            min_score = range_info.get('min_score', 0)
            max_score = range_info.get('max_score', 25)
            if min_score <= score <= max_score:
                return {
                    'range_name': range_name,
                    'description': range_info.get('description', ''),
                    'key_points': range_info.get('key_points', [])
                }
        return None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'score_ranges': self.score_ranges,
            'max_score': self.max_score,
            'min_score': self.min_score,
            'is_default': self.is_default,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 