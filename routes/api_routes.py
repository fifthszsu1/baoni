from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import logging
from datetime import datetime
from services.openai_service import OpenAIService
from services.xmind_service import XMindService
from services.auth_service import AuthService, require_auth

logger = logging.getLogger(__name__)

# 创建命名空间
text_analysis_ns = Namespace('text_analysis', description='英文文本分析与XMind生成相关接口')
auth_ns = Namespace('auth', description='用户认证相关接口')

# API模型定义
text_input_model = text_analysis_ns.model('TextInput', {
    'text': fields.String(required=True, description='需要分析的英文文本', example='This is a sample English text for reading comprehension analysis.')
})

analysis_result_model = text_analysis_ns.model('AnalysisResult', {
    'success': fields.Boolean(description='分析是否成功'),
    'analysis': fields.String(description='分析结果（markdown格式）'),
    'mindmap_data': fields.Raw(description='思维导图结构化数据'),
    'tokens_used': fields.Integer(description='使用的token数量'),
    'error': fields.String(description='错误信息')
})

# 认证相关模型
login_model = auth_ns.model('LoginCredentials', {
    'username': fields.String(required=True, description='用户名', example='baoni'),
    'password': fields.String(required=True, description='密码', example='lulu220519')
})

login_result_model = auth_ns.model('LoginResult', {
    'success': fields.Boolean(description='登录是否成功'),
    'token': fields.String(description='JWT认证令牌'),
    'username': fields.String(description='用户名'),
    'message': fields.String(description='结果消息'),
    'error': fields.String(description='错误信息')
})

@text_analysis_ns.route('/text')
class TextAnalysis(Resource):
    """文本分析接口"""
    
    @require_auth
    @text_analysis_ns.expect(text_input_model)
    @text_analysis_ns.marshal_with(analysis_result_model)
    @text_analysis_ns.doc(
        'analyze_text',
        description='分析英文文本，提取主要思想并生成思维导图数据',
        responses={
            200: '分析成功',
            400: '请求参数错误',
            401: '未授权访问', 
            500: '服务器内部错误'
        },
        security='Bearer Auth'
    )
    def post(self):
        """
        分析英文文本并生成XMind思维导图
        
        接收英文文本，使用Azure OpenAI进行分析，
        提取主要思想和结构，并生成XMind格式的思维导图文件
        """
        try:
            # 获取请求数据
            data = request.get_json()
            if not data or 'text' not in data:
                return {
                    'success': False,
                    'error': 'Please provide text content to analyze'
                }, 400
            
            text = data['text'].strip()
            if not text:
                return {
                    'success': False,
                    'error': 'Text content cannot be empty'
                }, 400
            
            if len(text) < 50:
                return {
                    'success': False,
                    'error': 'Text content is too short, please provide at least 50 characters of English text'
                }, 400
            
            # 初始化服务
            openai_service = OpenAIService()
            xmind_service = XMindService()
            
            # 调用OpenAI分析文本
            logger.info(f"Starting text analysis, length: {len(text)}")
            analysis_result = openai_service.analyze_text(text)
            
            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': f'Text analysis failed: {analysis_result["error"]}'
                }, 500
            
            # 生成思维导图结构数据
            logger.info("Generating mindmap structure data")
            logger.info(f"Analysis result length: {len(analysis_result.get('analysis', ''))}")
            
            try:
                # 只解析结构，不生成文件
                mindmap_data = xmind_service.parse_markdown_to_structure(
                    analysis_result['analysis']
                )
                logger.info(f"Mindmap structure generated successfully")
                
            except Exception as e:
                logger.error(f"Exception during mindmap structure generation: {str(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'success': False,
                    'analysis': analysis_result['analysis'],
                    'error': f'Mindmap structure generation exception: {str(e)}'
                }, 500
            
            # 返回成功结果
            return {
                'success': True,
                'analysis': analysis_result['analysis'],
                'mindmap_data': mindmap_data,
                'tokens_used': analysis_result.get('tokens_used', 0)
            }, 200
            
        except Exception as e:
            logger.error(f"API processing failed: {str(e)}")
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, 500

@text_analysis_ns.route('/test')
class ConnectionTest(Resource):
    """连接测试接口"""
    
    @text_analysis_ns.doc('test_connection', description='测试Azure OpenAI连接')
    def get(self):
        """测试Azure OpenAI服务连接"""
        try:
            openai_service = OpenAIService()
            result = openai_service.test_connection()
            
            if result['success']:
                return {
                    'success': True,
                    'message': result['message'],
                    'model': result['model'],
                    'timestamp': str(datetime.now())
                }, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 500
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500

# 登录接口
@auth_ns.route('/login')
class Login(Resource):
    """用户登录接口"""
    
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(login_result_model)
    @auth_ns.doc(
        'user_login',
        description='用户登录认证',
        responses={
            200: '登录成功',
            401: '认证失败',
            400: '请求参数错误'
        }
    )
    def post(self):
        """
        用户登录
        
        验证用户名和密码，成功后返回JWT token
        """
        try:
            # 获取请求数据
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                return {
                    'success': False,
                    'error': '请提供用户名和密码'
                }, 400
            
            username = data['username'].strip()
            password = data['password'].strip()
            
            if not username or not password:
                return {
                    'success': False,
                    'error': '用户名和密码不能为空'
                }, 400
            
            # 验证登录
            auth_service = AuthService()
            result = auth_service.login(username, password)
            
            if result['success']:
                return {
                    'success': True,
                    'token': result['token'],
                    'username': result['username'],
                    'message': result['message']
                }, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 401
                
        except Exception as e:
            logger.error(f"登录处理失败: {str(e)}")
            return {
                'success': False,
                'error': f'登录处理失败: {str(e)}'
            }, 500

@auth_ns.route('/verify')
class VerifyToken(Resource):
    """Token验证接口"""
    
    @require_auth
    @auth_ns.doc(
        'verify_token',
        description='验证JWT token是否有效',
        responses={
            200: 'Token有效',
            401: 'Token无效或已过期'
        },
        security='Bearer Auth'
    )
    def get(self):
        """
        验证当前token是否有效
        """
        user_info = request.current_user
        return {
            'success': True,
            'username': user_info['username'],
            'message': 'Token验证成功'
        }, 200 