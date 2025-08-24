import openai
from openai import AzureOpenAI
import logging
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class OpenAIService:
    """Azure OpenAI服务类"""
    
    def __init__(self):
        """初始化Azure OpenAI客户端"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = Config.AZURE_DEPLOYMENT_NAME
    
    def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        分析英文文本，提取主要思想和结构
        
        Args:
            text (str): 需要分析的英文文本
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 构建专门用于阅读理解分析的提示词
            system_prompt = """You are a professional English reading comprehension analyst. Please analyze the provided English article and extract its main ideas and structure to help high school students better understand the text.

Please output the analysis results in the following format (using markdown format):

# Article Analysis

## 1. Main Theme
- Briefly summarize the core theme of the article

## 2. Article Structure
- Analyze the logical structure of the article (e.g., introduction-body-conclusion)
- Identify the role and relationship of each paragraph

## 3. Key Arguments
- Extract the main viewpoints from the article
- List supporting evidence

## 4. Important Details
- Key facts and data
- Important examples and explanations

## 5. Language Features
- The writing style of the article
- Important rhetorical devices

## 6. Reading Comprehension Points
- Potential exam focus points
- Understanding difficulty hints

Please ensure the analysis content is well-organized and suitable for high school students' comprehension level. Output everything in English only."""

            user_prompt = f"Please analyze the following English article:\n\n{text}"
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis_result = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis_result,
                'original_text': text,
                'tokens_used': response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试Azure OpenAI连接"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                max_tokens=50
            )
            
            return {
                'success': True,
                'message': '连接测试成功',
                'model': self.deployment_name
            }
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 