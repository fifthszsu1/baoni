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
        分析英文文本，从what、why、how的角度提取中心思想
        
        Args:
            text (str): 需要分析的英文文本
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 构建专门用于what、why、how分析的提示词
            system_prompt = """你是一位专业的英文文章分析师。请从what、why、how三个维度分析提供的英文文章，帮助高中生更好地理解文本的核心内容。

请严格按照以下格式输出分析结果（使用markdown格式）：

# 文章分析

## What（是什么）
- [文章讨论的主要话题、现象或问题是什么]
- [文章提到的关键概念、人物、事件或观点是什么]
- [作者想要传达的主要信息是什么]
- [文章的核心观点和主要内容是什么]

## Why（为什么）
- [作者为什么要讨论这个话题]
- [文章中提到的现象或问题产生的原因是什么]
- [作者为什么持有这样的观点或立场]
- [这个话题为什么重要或值得关注]

## How（怎么样）
- [作者是如何论证自己观点的]
- [文章是如何组织结构和展开论述的]
- [作者提出了哪些解决方案或建议]
- [读者应该如何理解和应用这些内容]

请确保每个部分有3-4个要点，分析要深入浅出，适合高中生的理解水平。只需要输出中文分析，不需要英文内容。
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