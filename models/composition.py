from datetime import datetime
from decimal import Decimal
from . import db

class Composition(db.Model):
    """学生作文模型"""
    __tablename__ = 'compositions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), comment='学生姓名（从图片OCR识别）')
    student_id = db.Column(db.String(50), comment='学生学号（如果能识别到）')
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, comment='对应的题目ID')
    scoring_rule_id = db.Column(db.Integer, db.ForeignKey('scoring_rules.id'), nullable=False, comment='使用的评分规则ID')
    original_image_url = db.Column(db.String(500), nullable=False, comment='原始手写图片URL')
    ocr_text = db.Column(db.Text, comment='OCR识别出的文本内容')
    composition_content = db.Column(db.Text, comment='提取出的作文内容（去除姓名等）')
    ai_score = db.Column(db.DECIMAL(5, 2), comment='AI给出的分数')
    ai_feedback = db.Column(db.Text, comment='AI评分反馈')
    manual_score = db.Column(db.DECIMAL(5, 2), comment='人工评分（如果有）')
    manual_feedback = db.Column(db.Text, comment='人工评分反馈')
    word_count = db.Column(db.Integer, comment='作文字数统计')
    processing_status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed'), 
                                default='pending', comment='处理状态')
    error_message = db.Column(db.Text, comment='错误信息（如果处理失败）')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), comment='批改教师ID')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, comment='提交时间')
    processed_at = db.Column(db.DateTime, comment='处理完成时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Composition {self.id} - {self.student_name or "未知学生"}>'
    
    def get_final_score(self):
        """获取最终分数（优先使用人工评分）"""
        return self.manual_score if self.manual_score is not None else self.ai_score
    
    def get_final_feedback(self):
        """获取最终反馈（优先使用人工反馈）"""
        return self.manual_feedback if self.manual_feedback else self.ai_feedback
    
    def update_processing_status(self, status, error_message=None):
        """更新处理状态"""
        self.processing_status = status
        if error_message:
            self.error_message = error_message
        if status == 'completed':
            self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def calculate_word_count(self):
        """计算作文字数"""
        if self.composition_content:
            # 简单的英文单词计数
            words = self.composition_content.split()
            self.word_count = len([word for word in words if word.strip()])
        return self.word_count
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_name': self.student_name,
            'student_id': self.student_id,
            'topic_id': self.topic_id,
            'scoring_rule_id': self.scoring_rule_id,
            'original_image_url': self.original_image_url,
            'ocr_text': self.ocr_text,
            'composition_content': self.composition_content,
            'ai_score': float(self.ai_score) if self.ai_score else None,
            'ai_feedback': self.ai_feedback,
            'manual_score': float(self.manual_score) if self.manual_score else None,
            'manual_feedback': self.manual_feedback,
            'word_count': self.word_count,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'teacher_id': self.teacher_id,
            'final_score': float(self.get_final_score()) if self.get_final_score() else None,
            'final_feedback': self.get_final_feedback(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 