from datetime import datetime
from . import db

class Teacher(db.Model):
    """教师模型"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='教师姓名')
    email = db.Column(db.String(255), unique=True, comment='教师邮箱')
    phone = db.Column(db.String(20), comment='联系电话')
    school = db.Column(db.String(255), comment='学校名称')
    status = db.Column(db.Enum('active', 'inactive'), default='active', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    topics = db.relationship('Topic', backref='teacher', lazy='dynamic')
    scoring_rules = db.relationship('ScoringRule', backref='creator', lazy='dynamic')
    compositions = db.relationship('Composition', backref='graded_by_teacher', lazy='dynamic')
    
    def __repr__(self):
        return f'<Teacher {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'school': self.school,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 