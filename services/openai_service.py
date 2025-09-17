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
        分析英文文本，先判断文体类型，然后根据文体结构生成思维导图
        
        Args:
            text (str): 需要分析的英文文本
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 构建新的文体分析提示词
            system_prompt = """你是一位专业的英文文章分析师。请先判断文章的文体类型，然后根据文体特点进行结构化分析，输出关键词思维导图。

请严格按照以下格式输出分析结果（使用markdown格式）：

# 文章分析

## 文体类型
[说明文/议论文]

## 结构分析
先判断文章的文体类型，然后根据文体类型进行结构分析。
说明文 的结构通常是分类、对比、流程、因果等，侧重于有条理地展开说明。
议论文 的经典结构是提出论点 -> 提供论据 -> 总结呼吁

### 如果是说明文：
判断属于以下哪种结构类型，并提取关键词：
- **分类说明**：主要概念 → 分类标准 → 各类别特点
- **对比说明**：对比对象 → 对比角度 → 差异要点  
- **流程说明**：起始状态 → 关键步骤 → 最终结果
- **因果说明**：现象描述 → 原因分析 → 结果影响

### 如果是议论文：
按照经典议论文结构提取关键词：
- **论点**：核心观点
- **论据**：主要证据1、主要证据2、主要证据3
- **总结呼吁**：结论要点

## 思维导图关键词
- 中心主题：[一个核心关键词]
- 主要分支：[3-5个关键词]
- 次要分支：[每个主分支下2-3个关键词]

注意：
1. 只输出关键词和短语，不要长句
2. 每个关键词不超过5个字
3. 重点突出文章的逻辑结构
4. 适合制作思维导图使用"""

            user_prompt = f"请分析以下英文文章的文体类型和结构，并提取关键词用于制作思维导图：\n\n{text}"
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500  # 减少token数量，因为输出更简洁
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