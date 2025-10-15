import json
import logging
from typing import Generator, Dict, Any, List
from openai import AzureOpenAI
from config import Config

logger = logging.getLogger(__name__)

class ChatService:
    """AI聊天服务类"""
    
    def __init__(self):
        """初始化Azure OpenAI客户端"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = Config.AZURE_DEPLOYMENT_NAME
        
        # 系统提示词
        self.system_prompt = """你是一个专业的AI助手，名叫小宝。你具备以下特点：

1. **友好专业**：以友善、专业的态度回答用户问题
2. **知识渊博**：在各个领域都有深入的了解，能提供准确的信息
3. **逻辑清晰**：回答问题时思路清晰，条理分明
4. **实用导向**：注重为用户提供实际有用的建议和信息
5. **中文回复**：主要使用中文与用户交流，但也能处理英文内容

请根据用户的问题，提供准确、有用、友好的回答。如果遇到不确定的问题，请诚实说明并建议用户寻求专业帮助。"""

    def chat_stream(self, messages: List[Dict[str, str]], user_id: str = "default") -> Generator[str, None, None]:
        """
        流式聊天对话
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "消息内容"}, ...]
            user_id: 用户ID（可用于后续实现用户会话管理）
            
        Yields:
            str: 流式返回的消息片段
        """
        try:
            # 构建完整的消息列表（包含系统提示词）
            full_messages = [{"role": "system", "content": self.system_prompt}]
            full_messages.extend(messages)
            
            # 调用Azure OpenAI流式API
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=full_messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True  # 启用流式输出
            )
            
            # 逐个返回流式数据
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            yield f"抱歉，聊天服务遇到了问题：{str(e)}"
    
    def chat_single(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        单次聊天对话（非流式）
        
        Args:
            message: 用户消息
            conversation_history: 对话历史
            
        Returns:
            Dict: 包含回复和状态的字典
        """
        try:
            # 构建消息历史
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": message})
            
            # 调用Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            reply = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return {
                'success': True,
                'reply': reply,
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            logger.error(f"聊天失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'reply': None
            }
    
    def test_chat_connection(self) -> Dict[str, Any]:
        """测试聊天服务连接"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": "你好，这是一个连接测试"}
                ],
                max_tokens=100
            )
            
            return {
                'success': True,
                'message': '聊天服务连接正常',
                'reply': response.choices[0].message.content,
                'model': self.deployment_name
            }
        except Exception as e:
            logger.error(f"聊天服务连接测试失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
