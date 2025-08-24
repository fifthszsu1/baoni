from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import logging
from datetime import datetime
from services.openai_service import OpenAIService
from services.xmind_service import XMindService

logger = logging.getLogger(__name__)

# 创建命名空间
text_analysis_ns = Namespace('text_analysis', description='英文文本分析与XMind生成相关接口')

# API模型定义
text_input_model = text_analysis_ns.model('TextInput', {
    'text': fields.String(required=True, description='需要分析的英文文本', example='This is a sample English text for reading comprehension analysis.')
})

analysis_result_model = text_analysis_ns.model('AnalysisResult', {
    'success': fields.Boolean(description='分析是否成功'),
    'analysis': fields.String(description='分析结果（markdown格式）'),
    'xmind_filename': fields.String(description='生成的XMind文件名'),
    'download_url': fields.String(description='XMind文件下载链接'),
    'tokens_used': fields.Integer(description='使用的token数量'),
    'error': fields.String(description='错误信息')
})

@text_analysis_ns.route('/text')
class TextAnalysis(Resource):
    """文本分析接口"""
    
    @text_analysis_ns.expect(text_input_model)
    @text_analysis_ns.marshal_with(analysis_result_model)
    @text_analysis_ns.doc(
        'analyze_text',
        description='分析英文文本，提取主要思想并生成XMind思维导图',
        responses={
            200: '分析成功',
            400: '请求参数错误', 
            500: '服务器内部错误'
        }
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
            
            # 生成XMind文件
            logger.info("Starting XMind file generation")
            logger.info(f"Analysis result length: {len(analysis_result.get('analysis', ''))}")
            
            try:
                xmind_result = xmind_service.generate_xmind(
                    analysis_result['analysis'], 
                    text
                )
                logger.info(f"XMind service returned: success={xmind_result.get('success')}")
                
            except Exception as e:
                logger.error(f"Exception during XMind generation: {str(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {
                    'success': False,
                    'analysis': analysis_result['analysis'],
                    'error': f'XMind generation exception: {str(e)}'
                }, 500
            
            if not xmind_result['success']:
                logger.error(f"XMind generation failed with error: {xmind_result.get('error')}")
                return {
                    'success': False,
                    'analysis': analysis_result['analysis'],
                    'error': f'XMind file generation failed: {xmind_result["error"]}'
                }, 500
            
            # 返回成功结果
            return {
                'success': True,
                'analysis': analysis_result['analysis'],
                'xmind_filename': xmind_result['filename'],
                'download_url': xmind_result['download_url'],
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