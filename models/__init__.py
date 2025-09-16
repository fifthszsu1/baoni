# 数据库模型包
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型
from .teacher import Teacher
from .scoring_rule import ScoringRule
from .topic import Topic
from .composition import Composition

__all__ = ['db', 'Teacher', 'ScoringRule', 'Topic', 'Composition'] 