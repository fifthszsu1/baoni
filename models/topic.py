from datetime import datetime
from . import db

class Topic(db.Model):
    """题目模型"""
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False, comment='题目标题')
    content = db.Column(db.Text, nullable=False, comment='题目内容')
    content_type = db.Column(db.Enum('text', 'image'), default='text', comment='内容类型：文本或图片')
    image_url = db.Column(db.String(500), comment='题目图片URL（如果是图片类型）')
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard'), default='medium', comment='难度等级')
    word_count_requirement = db.Column(db.String(50), comment='字数要求，如"150词左右"')
    key_points = db.Column(db.JSON, comment='关键要点，JSON格式存储')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), comment='创建题目的教师ID')
    status = db.Column(db.Enum('active', 'inactive'), default='active', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    compositions = db.relationship('Composition', backref='topic', lazy='dynamic')
    
    def __repr__(self):
        return f'<Topic {self.title}>'
    
    def get_key_points_list(self):
        """获取关键要点列表"""
        if isinstance(self.key_points, list):
            return self.key_points
        return []
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_type': self.content_type,
            'image_url': self.image_url,
            'difficulty_level': self.difficulty_level,
            'word_count_requirement': self.word_count_requirement,
            'key_points': self.key_points,
            'teacher_id': self.teacher_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 