from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import logging
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

from models import db, Topic, ScoringRule, Composition, Teacher
from services.composition_scoring_service import CompositionScoringService

logger = logging.getLogger(__name__)

# 创建小程序API命名空间
miniprogram_ns = Namespace('miniprogram', description='小程序API接口')

# 数据模型定义
create_scoring_rule_model = miniprogram_ns.model('CreateScoringRule', {
    'rule_name': fields.String(required=True, description='评分规则名称'),
    'rule_description': fields.String(description='规则描述'),
    'max_score': fields.Integer(required=True, description='最高分数'),
    'min_score': fields.Integer(required=True, description='最低分数'),
    'score_ranges': fields.Raw(required=True, description='分数档次JSON对象'),
    'is_default': fields.Boolean(description='是否为默认规则', default=False),
    'teacher_id': fields.Integer(description='创建教师ID')
})

create_topic_model = miniprogram_ns.model('CreateTopic', {
    'title': fields.String(required=True, description='题目标题'),
    'content': fields.String(description='题目内容（文本题目时必填）'),
    'content_type': fields.String(required=True, description='内容类型', enum=['text', 'image']),
    'difficulty_level': fields.String(required=True, description='难度等级', enum=['easy', 'medium', 'hard']),
    'word_count_requirement': fields.String(description='字数要求'),
    'key_points': fields.List(fields.String, description='关键要点列表'),
    'teacher_id': fields.Integer(description='创建教师ID')
})

topic_model = miniprogram_ns.model('Topic', {
    'id': fields.Integer(required=True, description='题目ID'),
    'title': fields.String(required=True, description='题目标题'),
    'content': fields.String(required=True, description='题目内容'),
    'content_type': fields.String(required=True, description='内容类型', enum=['text', 'image']),
    'difficulty_level': fields.String(required=True, description='难度等级', enum=['easy', 'medium', 'hard']),
    'word_count_requirement': fields.String(description='字数要求'),
    'key_points': fields.List(fields.String, description='关键要点'),
    'created_at': fields.String(description='创建时间')
})

scoring_rule_model = miniprogram_ns.model('ScoringRule', {
    'id': fields.Integer(required=True, description='评分规则ID'),
    'rule_name': fields.String(required=True, description='规则名称'),
    'rule_description': fields.String(description='规则描述'),
    'max_score': fields.Integer(required=True, description='最高分数'),
    'min_score': fields.Integer(required=True, description='最低分数'),
    'is_default': fields.Boolean(description='是否为默认规则')
})

composition_submit_model = miniprogram_ns.model('CompositionSubmit', {
    'topic_id': fields.Integer(required=True, description='题目ID'),
    'scoring_rule_id': fields.Integer(required=True, description='评分规则ID'),
    'teacher_id': fields.Integer(description='教师ID（可选）')
})

composition_result_model = miniprogram_ns.model('CompositionResult', {
    'composition_id': fields.Integer(required=True, description='作文ID'),
    'student_name': fields.String(description='学生姓名'),
    'student_id': fields.String(description='学号'),
    'score': fields.Float(description='评分'),
    'score_range': fields.String(description='分数档次'),
    'word_count': fields.Integer(description='字数统计'),
    'feedback': fields.String(description='评分反馈'),
    'processing_status': fields.String(description='处理状态', enum=['pending', 'processing', 'completed', 'failed']),
    'submitted_at': fields.String(description='提交时间'),
    'processed_at': fields.String(description='处理完成时间')
})

# 初始化评分服务
scoring_service = CompositionScoringService()

@miniprogram_ns.route('/topics')
class TopicListAPI(Resource):
    @miniprogram_ns.doc('get_topics')
    @miniprogram_ns.marshal_list_with(topic_model)
    def get(self):
        """获取题目列表"""
        try:
            # 获取查询参数
            teacher_id = request.args.get('teacher_id', type=int)
            difficulty = request.args.get('difficulty')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 构建查询
            query = Topic.query.filter_by(status='active')
            
            if teacher_id:
                query = query.filter_by(teacher_id=teacher_id)
            
            if difficulty:
                query = query.filter_by(difficulty_level=difficulty)
            
            # 分页查询
            topics = query.order_by(Topic.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return [topic.to_dict() for topic in topics.items]
            
        except Exception as e:
            logger.error(f"获取题目列表失败: {str(e)}")
            miniprogram_ns.abort(500, f'获取题目列表失败: {str(e)}')

@miniprogram_ns.route('/topics/<int:topic_id>')
class TopicDetailAPI(Resource):
    @miniprogram_ns.doc('get_topic_detail')
    @miniprogram_ns.marshal_with(topic_model)
    def get(self, topic_id):
        """获取题目详情"""
        try:
            topic = Topic.query.get(topic_id)
            if not topic or topic.status != 'active':
                miniprogram_ns.abort(404, '题目不存在或已下线')
            
            return topic.to_dict()
            
        except Exception as e:
            logger.error(f"获取题目详情失败: {str(e)}")
            miniprogram_ns.abort(500, f'获取题目详情失败: {str(e)}')

@miniprogram_ns.route('/scoring-rules')
class ScoringRuleListAPI(Resource):
    @miniprogram_ns.doc('get_scoring_rules')
    @miniprogram_ns.marshal_list_with(scoring_rule_model)
    def get(self):
        """获取评分规则列表"""
        try:
            # 获取活跃的评分规则，默认规则排在前面
            rules = ScoringRule.query.filter_by(status='active').order_by(
                ScoringRule.is_default.desc(), 
                ScoringRule.created_at.desc()
            ).all()
            
            return [rule.to_dict() for rule in rules]
            
        except Exception as e:
            logger.error(f"获取评分规则列表失败: {str(e)}")
            miniprogram_ns.abort(500, f'获取评分规则列表失败: {str(e)}')

@miniprogram_ns.route('/compositions/submit')
class CompositionSubmitAPI(Resource):
    @miniprogram_ns.doc('submit_composition')
    @miniprogram_ns.expect(composition_submit_model)
    def post(self):
        """提交作文图片进行评分"""
        try:
            # 检查是否有文件上传
            if 'image' not in request.files:
                miniprogram_ns.abort(400, '请上传作文图片')
            
            file = request.files['image']
            if file.filename == '':
                miniprogram_ns.abort(400, '请选择要上传的图片文件')
            
            # 检查文件类型
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            if not ('.' in file.filename and 
                   file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                miniprogram_ns.abort(400, '不支持的图片格式，请上传PNG、JPG、JPEG、GIF或BMP格式的图片')
            
            # 获取请求参数
            data = request.form.to_dict()
            topic_id = int(data.get('topic_id'))
            scoring_rule_id = int(data.get('scoring_rule_id'))
            teacher_id = data.get('teacher_id', type=int)
            
            # 验证参数
            if not topic_id or not scoring_rule_id:
                miniprogram_ns.abort(400, '题目ID和评分规则ID不能为空')
            
            # 读取图片数据
            image_data = file.read()
            
            # 保存图片文件（可选，用于备份）
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"开始处理作文图片: {filename}, 题目ID: {topic_id}, 评分规则ID: {scoring_rule_id}")
            
            # 调用评分服务处理图片
            result = scoring_service.process_composition_image(
                image_data=image_data,
                topic_id=topic_id,
                scoring_rule_id=scoring_rule_id,
                teacher_id=teacher_id
            )
            
            if result['success']:
                # 更新作文记录的图片路径
                composition = Composition.query.get(result['composition_id'])
                if composition:
                    composition.original_image_url = f"/downloads/{filename}"
                    db.session.commit()
                
                return {
                    'success': True,
                    'message': '作文提交成功，评分完成',
                    'data': result
                }
            else:
                # 如果处理失败，删除已保存的图片
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                return {
                    'success': False,
                    'message': result['error'],
                    'data': None
                }, 400
                
        except Exception as e:
            logger.error(f"提交作文失败: {str(e)}")
            return {
                'success': False,
                'message': f'提交作文失败: {str(e)}',
                'data': None
            }, 500

@miniprogram_ns.route('/compositions/<int:composition_id>')
class CompositionDetailAPI(Resource):
    @miniprogram_ns.doc('get_composition_detail')
    @miniprogram_ns.marshal_with(composition_result_model)
    def get(self, composition_id):
        """获取作文详情和评分结果"""
        try:
            composition = Composition.query.get(composition_id)
            if not composition:
                miniprogram_ns.abort(404, '作文记录不存在')
            
            return composition.to_dict()
            
        except Exception as e:
            logger.error(f"获取作文详情失败: {str(e)}")
            miniprogram_ns.abort(500, f'获取作文详情失败: {str(e)}')

@miniprogram_ns.route('/compositions')
class CompositionListAPI(Resource):
    @miniprogram_ns.doc('get_compositions')
    @miniprogram_ns.marshal_list_with(composition_result_model)
    def get(self):
        """获取作文列表（支持按学生姓名、题目等筛选）"""
        try:
            # 获取查询参数
            student_name = request.args.get('student_name')
            topic_id = request.args.get('topic_id', type=int)
            teacher_id = request.args.get('teacher_id', type=int)
            status = request.args.get('status')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 构建查询
            query = Composition.query
            
            if student_name:
                query = query.filter(Composition.student_name.like(f'%{student_name}%'))
            
            if topic_id:
                query = query.filter_by(topic_id=topic_id)
            
            if teacher_id:
                query = query.filter_by(teacher_id=teacher_id)
            
            if status:
                query = query.filter_by(processing_status=status)
            
            # 分页查询，按提交时间倒序
            compositions = query.order_by(Composition.submitted_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return [comp.to_dict() for comp in compositions.items]
            
        except Exception as e:
            logger.error(f"获取作文列表失败: {str(e)}")
            miniprogram_ns.abort(500, f'获取作文列表失败: {str(e)}')

@miniprogram_ns.route('/teachers')
class TeacherListAPI(Resource):
    @miniprogram_ns.doc('get_teachers')
    def get(self):
        """获取教师列表"""
        try:
            teachers = Teacher.query.filter_by(status='active').all()
            
            return {
                'success': True,
                'data': [{'id': t.id, 'name': t.name, 'school': t.school} for t in teachers]
            }
            
        except Exception as e:
            logger.error(f"获取教师列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取教师列表失败: {str(e)}'
            }, 500

@miniprogram_ns.route('/health')
class HealthCheckAPI(Resource):
    @miniprogram_ns.doc('health_check')
    def get(self):
        """健康检查"""
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            
            # 检查OCR服务
            ocr_available = scoring_service.ocr_service.is_available()
            
            return {
                'success': True,
                'message': '服务正常',
                'data': {
                    'database': 'connected',
                    'ocr_service': 'available' if ocr_available else 'unavailable',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                'success': False,
                'message': f'服务异常: {str(e)}'
            }, 500

# ========== 管理接口 ==========

@miniprogram_ns.route('/admin/scoring-rules')
class CreateScoringRuleAPI(Resource):
    @miniprogram_ns.doc('create_scoring_rule')
    @miniprogram_ns.expect(create_scoring_rule_model)
    def post(self):
        """创建新的评分规则"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            required_fields = ['rule_name', 'max_score', 'min_score', 'score_ranges']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'message': f'缺少必填字段: {field}'
                    }, 400
            
            # 验证分数范围
            max_score = data['max_score']
            min_score = data['min_score']
            if max_score <= min_score:
                return {
                    'success': False,
                    'message': '最高分数必须大于最低分数'
                }, 400
            
            # 验证评分档次格式
            score_ranges = data['score_ranges']
            if not isinstance(score_ranges, dict):
                return {
                    'success': False,
                    'message': '评分档次必须是JSON对象格式'
                }, 400
            
            # 验证教师是否存在（如果提供了teacher_id）
            teacher_id = data.get('teacher_id')
            if teacher_id:
                teacher = Teacher.query.get(teacher_id)
                if not teacher:
                    return {
                        'success': False,
                        'message': f'教师ID {teacher_id} 不存在'
                    }, 400
            
            # 检查规则名称是否已存在
            existing_rule = ScoringRule.query.filter_by(rule_name=data['rule_name']).first()
            if existing_rule:
                return {
                    'success': False,
                    'message': f'评分规则名称 "{data["rule_name"]}" 已存在'
                }, 400
            
            # 如果设置为默认规则，需要将其他规则的默认状态取消
            if data.get('is_default', False):
                ScoringRule.query.filter_by(is_default=True).update({'is_default': False})
            
            # 创建评分规则
            new_rule = ScoringRule(
                rule_name=data['rule_name'],
                rule_description=data.get('rule_description', ''),
                score_ranges=score_ranges,
                max_score=max_score,
                min_score=min_score,
                is_default=data.get('is_default', False),
                status='active',
                created_by=teacher_id
            )
            
            db.session.add(new_rule)
            db.session.commit()
            
            logger.info(f"创建评分规则成功: {new_rule.rule_name}, ID: {new_rule.id}")
            
            return {
                'success': True,
                'message': '评分规则创建成功',
                'data': new_rule.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建评分规则失败: {str(e)}")
            return {
                'success': False,
                'message': f'创建评分规则失败: {str(e)}'
            }, 500

@miniprogram_ns.route('/admin/topics')
class CreateTopicAPI(Resource):
    @miniprogram_ns.doc('create_topic')
    @miniprogram_ns.expect(create_topic_model)
    def post(self):
        """创建新题目（支持文本或图片OCR识别）"""
        try:
            # 判断是否为文件上传（图片题目）
            if request.content_type and 'multipart/form-data' in request.content_type:
                return self._create_topic_from_image()
            else:
                return self._create_topic_from_text()
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建题目失败: {str(e)}")
            return {
                'success': False,
                'message': f'创建题目失败: {str(e)}'
            }, 500
    
    def _create_topic_from_text(self):
        """从文本数据创建题目"""
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'content_type', 'difficulty_level']
        for field in required_fields:
            if not data.get(field):
                return {
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }, 400
        
        # 文本题目必须有内容
        if data['content_type'] == 'text' and not data.get('content'):
            return {
                'success': False,
                'message': '文本题目必须提供题目内容'
            }, 400
        
        # 验证教师是否存在
        teacher_id = data.get('teacher_id')
        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return {
                    'success': False,
                    'message': f'教师ID {teacher_id} 不存在'
                }, 400
        
        # 创建题目
        new_topic = Topic(
            title=data['title'],
            content=data.get('content', ''),
            content_type=data['content_type'],
            difficulty_level=data['difficulty_level'],
            word_count_requirement=data.get('word_count_requirement'),
            key_points=data.get('key_points', []),
            teacher_id=teacher_id,
            status='active'
        )
        
        db.session.add(new_topic)
        db.session.commit()
        
        logger.info(f"创建文本题目成功: {new_topic.title}, ID: {new_topic.id}")
        
        return {
            'success': True,
            'message': '题目创建成功',
            'data': new_topic.to_dict()
        }
    
    def _create_topic_from_image(self):
        """从图片OCR识别创建题目"""
        # 检查文件上传
        if 'image' not in request.files:
            return {
                'success': False,
                'message': '请上传题目图片'
            }, 400
        
        file = request.files['image']
        if file.filename == '':
            return {
                'success': False,
                'message': '请选择要上传的图片文件'
            }, 400
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and 
               file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return {
                'success': False,
                'message': '不支持的图片格式，请上传PNG、JPG、JPEG、GIF或BMP格式的图片'
            }, 400
        
        # 获取表单数据
        data = request.form.to_dict()
        
        # 验证必填字段
        required_fields = ['title', 'difficulty_level']
        for field in required_fields:
            if not data.get(field):
                return {
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }, 400
        
        # 验证教师是否存在
        teacher_id = data.get('teacher_id', type=int)
        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return {
                    'success': False,
                    'message': f'教师ID {teacher_id} 不存在'
                }, 400
        
        # 读取图片数据
        image_data = file.read()
        
        # 保存图片文件
        filename = secure_filename(f"topic_{uuid.uuid4().hex}_{file.filename}")
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"开始OCR识别题目图片: {filename}")
        
        # 使用OCR识别图片内容
        ocr_result = scoring_service.ocr_service.extract_text_from_image(image_data)
        
        if not ocr_result['success']:
            # 如果OCR失败，删除已保存的图片
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return {
                'success': False,
                'message': f'图片OCR识别失败: {ocr_result["error"]}'
            }, 400
        
        ocr_content = ocr_result['extracted_text']
        
        # 解析关键要点（如果提供）
        key_points = []
        if data.get('key_points'):
            try:
                import json
                key_points = json.loads(data['key_points'])
            except:
                # 如果不是JSON格式，按逗号分割
                key_points = [point.strip() for point in data['key_points'].split(',') if point.strip()]
        
        # 创建题目
        new_topic = Topic(
            title=data['title'],
            content=ocr_content,
            content_type='image',
            image_url=f"/downloads/{filename}",
            difficulty_level=data['difficulty_level'],
            word_count_requirement=data.get('word_count_requirement'),
            key_points=key_points,
            teacher_id=teacher_id,
            status='active'
        )
        
        db.session.add(new_topic)
        db.session.commit()
        
        logger.info(f"创建图片题目成功: {new_topic.title}, ID: {new_topic.id}")
        
        return {
            'success': True,
            'message': '题目创建成功（已完成OCR识别）',
            'data': {
                **new_topic.to_dict(),
                'ocr_confidence': ocr_result.get('confidence', 0),
                'ocr_lines_count': ocr_result.get('lines_count', 0)
            }
        } 