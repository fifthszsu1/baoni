from flask import Flask, send_from_directory
from flask_restx import Api, Resource
from flask_cors import CORS
import os
import logging
from config import Config

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化配置
    Config.init_app(app)
    
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
        title='英文文本分析与XMind生成API',
        description='使用Azure OpenAI分析英文文本并生成XMind思维导图的RESTful API',
        doc='/swagger/',
        prefix='/api'
    )
    
    # 注册命名空间
    from routes.api_routes import text_analysis_ns
    api.add_namespace(text_analysis_ns, path='/analyze')
    
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