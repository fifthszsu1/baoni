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

IMPORTANT: Please output the analysis results in the EXACT format below (using markdown format). Each section must contain both English and Chinese content:

# Article Analysis

## Main Theme
- [English description of the core theme]
- [Chinese description of the core theme - 中文描述核心主题]

## Article Structure  
- [English analysis of logical structure, e.g., introduction-body-conclusion]
- [Chinese analysis - 中文分析文章逻辑结构]
- [English description of each paragraph's role and relationship]
- [Chinese description - 中文描述各段落作用和关系]

## Key Arguments
- [English extraction of main viewpoints]
- [Chinese extraction - 中文提取主要观点] 
- [English list of supporting evidence]
- [Chinese list - 中文列出支持证据]

## Important Details
- [English key facts and data]
- [Chinese key facts - 中文重要事实和数据]
- [English important examples and explanations]
- [Chinese examples - 中文重要例子和解释]

## Language Features
- [English description of writing style]
- [Chinese description - 中文描述写作风格]
- [English description of important rhetorical devices]
- [Chinese description - 中文描述重要修辞手法]

## Reading Comprehension Points
- [English potential exam focus points]
- [Chinese focus points - 中文潜在考试重点]
- [English understanding difficulty hints]
- [Chinese hints - 中文理解难度提示]

Please ensure each section has 2-4 bullet points, with each point containing both English and Chinese content. Keep the analysis well-organized and suitable for high school students' comprehension level.
"""

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