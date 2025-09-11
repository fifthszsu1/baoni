import openai
from openai import AzureOpenAI
import logging
from typing import Optional, Dict, Any
from config import Config
import base64

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

    def extract_text_from_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        从图片中提取英文文章内容
        
        Args:
            image_data (bytes): 图片的二进制数据
            
        Returns:
            Dict: 包含提取结果的字典
        """
        try:
            # 将图片转换为base64编码
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 构建专门用于OCR的提示词
            system_prompt = """You are a professional OCR (Optical Character Recognition) assistant. Your task is to extract all English text content from the uploaded image accurately.

IMPORTANT INSTRUCTIONS:
1. Extract ALL visible English text from the image, maintaining the original structure and formatting as much as possible
2. If the image contains an English article, essay, or document, transcribe it completely
3. Preserve paragraph breaks, bullet points, and basic formatting
4. If there are titles, headings, or subheadings, include them
5. Only extract text - do not add explanations, comments, or descriptions about the image
6. If the text is unclear or partially obscured, do your best to transcribe what is visible
7. If no English text is found, respond with "No English text detected in the image"

Please provide the extracted text directly without any additional commentary."""

            user_prompt = "Please extract all English text content from this image:"
            
            # 调用GPT-4 Vision API
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # 需要支持vision的模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # 低温度确保准确性
                max_tokens=2000
            )
            
            extracted_text = response.choices[0].message.content
            
            # 检查是否成功提取到文本
            if extracted_text and extracted_text.strip() != "No English text detected in the image":
                return {
                    'success': True,
                    'extracted_text': extracted_text.strip(),
                    'tokens_used': response.usage.total_tokens if response.usage else 0
                }
            else:
                return {
                    'success': False,
                    'error': '图片中未检测到英文文本或文本不清晰',
                    'extracted_text': None
                }
            
        except Exception as e:
            logger.error(f"图片文字识别失败: {str(e)}")
            return {
                'success': False,
                'error': f'图片识别失败: {str(e)}',
                'extracted_text': None
            }
    
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