from flask import Flask, send_from_directory
from flask_restx import Api, Resource
from flask_cors import CORS
import os
import logging
from config import Config
from models import db

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化配置
    Config.init_app(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("数据库表创建成功")
        except Exception as e:
            app.logger.error(f"数据库初始化失败: {str(e)}")
            # 不抛出异常，允许应用启动
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # 初始化Flask-RESTX API
    api = Api(
        app, 
        version='1.0', 
        title='英文文本分析与思维导图生成API',
        description='使用Azure OpenAI分析英文文本并生成思维导图数据的RESTful API，支持JWT认证',
        doc='/swagger/',
        prefix='/api',
        security='Bearer Auth',
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "在请求头中添加 'Bearer ' + JWT token"
            }
        }
    )
    
    # 注册命名空间
    from routes.api_routes import text_analysis_ns, auth_ns, chat_ns
    from routes.miniprogram_routes import miniprogram_ns
    api.add_namespace(text_analysis_ns, path='/analyze')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(chat_ns, path='/chat')
    api.add_namespace(miniprogram_ns, path='/miniprogram')
    
    # 静态文件路由
    @app.route('/downloads/<filename>')
    def download_file(filename):
        """下载生成的文件"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        """服务健康检查"""
        return {
            'status': 'healthy',
            'service': '英文文本分析与XMind生成服务',
            'version': '1.0'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG']) 