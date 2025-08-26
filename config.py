import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Flask应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 登录配置
    LOGIN_USERNAME = os.environ.get('LOGIN_USERNAME', 'baoni')
    LOGIN_PASSWORD = os.environ.get('LOGIN_PASSWORD', 'lulu220519')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Azure OpenAI配置
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT') or 'https://your-endpoint.openai.azure.com/'
    AZURE_DEPLOYMENT_NAME = os.environ.get('AZURE_DEPLOYMENT_NAME') or 'gpt-4'
    AZURE_API_VERSION = os.environ.get('AZURE_API_VERSION') or '2025-01-01-preview'
    
    # API配置
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建上传文件夹
        upload_dir = os.path.join(os.getcwd(), Config.UPLOAD_FOLDER)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 验证Azure OpenAI配置
        required_keys = [
            'AZURE_OPENAI_API_KEY', 
            'AZURE_OPENAI_ENDPOINT', 
            'AZURE_DEPLOYMENT_NAME', 
            'AZURE_API_VERSION'
        ]
        
        missing_keys = [key for key in required_keys if not getattr(Config, key)]
        if missing_keys:
            print(f"警告: 缺少环境变量: {', '.join(missing_keys)}，将使用默认配置")
            # 不再抛出异常，允许使用默认配置 