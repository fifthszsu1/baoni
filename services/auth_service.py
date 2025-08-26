import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, current_app
from config import Config
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.secret_key = Config.SECRET_KEY
        self.username = Config.LOGIN_USERNAME
        self.password = Config.LOGIN_PASSWORD
    
    def validate_credentials(self, username: str, password: str) -> bool:
        """
        验证用户凭据
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 验证是否成功
        """
        return username == self.username and password == self.password
    
    def generate_token(self, username: str) -> str:
        """
        生成JWT token
        
        Args:
            username (str): 用户名
            
        Returns:
            str: JWT token
        """
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24),  # 24小时有效期
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT token
        
        Args:
            token (str): JWT token
            
        Returns:
            Dict: 解码后的payload，如果验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的token")
            return None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            Dict: 登录结果
        """
        if self.validate_credentials(username, password):
            token = self.generate_token(username)
            return {
                'success': True,
                'token': token,
                'username': username,
                'message': '登录成功'
            }
        else:
            return {
                'success': False,
                'error': '用户名或密码错误'
            }

def require_auth(f):
    """
    需要认证的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return {'success': False, 'error': '缺少认证头'}, 401
        
        try:
            # 格式: "Bearer <token>"
            if not auth_header.startswith('Bearer '):
                return {'success': False, 'error': '认证头格式错误'}, 401
            
            token = auth_header.split(' ')[1]
            auth_service = AuthService()
            payload = auth_service.verify_token(token)
            
            if not payload:
                return {'success': False, 'error': 'Token无效或已过期'}, 401
            
            # 将用户信息添加到request对象
            request.current_user = payload
            
        except Exception as e:
            logger.error(f"认证验证失败: {str(e)}")
            return {'success': False, 'error': '认证验证失败'}, 401
        
        return f(*args, **kwargs)
    
    return decorated_function 