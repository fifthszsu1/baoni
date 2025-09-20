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
请从以下7种文体中选择最符合的一种：
[实验研究与报告/事理阐释类论说文/新兴技术介绍/社会发展新现象类/问题解决类说明文/社会发展与变迁类/书评]

## 结构分析
根据识别的文体类型，按照对应的分析框架提取关键词：

### 实验研究与报告：
- **背景介绍**：研究背景、研究主体、话题引入
- **研究过程**：研究设计原理、研究实施过程  
- **归纳文章大意**：主要发现和结论

### 事理阐释类论说文：
- **提出论点**：直接提出、对比引出、现象带出
- **进行论证**：结构、方法
- **得出结论**：具体结论、结论评价
- **归纳文章大意**：核心观点总结

### 新兴技术介绍：
- **技术背景**：现存问题、新技术开发条件、研究目的
- **介绍技术**：基本情况、新技术功用、工作原理
- **技术评价**：新技术好处、局限性
- **发明前景**：市场前景、应用前景
- **归纳文章大意**：技术核心价值

### 现象类：
- **引出现象**：开门见山、引用事例、前后对比
- **说明现象普遍性**：举例说明、数据支撑、具体做法
- **分析原因**：举例分析、原因说明
- **说明影响并表达看法**：说明影响、表达看法

### 问题解决类说明文：
- **提出问题**：引出问题、话题引入
- **解决措施**：措施目的、具体做法案例
- **措施成效及评价**：措施成效、措施评价、后续措施
- **归纳文章大意**：解决方案总结

### 社会发展与变迁类：
- **背景介绍**：段落大意、写作意图、理解原因
- **现在发展历程**：理解现在、推断观点态度
- **过去发展历程**：理解原因、推断观点态度  
- **表达看法**：推断观点态度、发展趋势

### 书评：
- **背景介绍**：经历引入、作者背景、图书故事引入、创作背景
- **内容介绍**：图书基本情况、图书章节内容
- **图书推荐**：推断写作目的
- **图书评价**：图书意义、语言风格
- **发表观点**：深入讨论

## 思维导图关键词
- 中心主题：[一个核心关键词]
- 主要分支：[根据文体结构确定的3-5个关键词]
- 次要分支：[每个主分支下2-3个关键词]

注意：
1. 只输出关键词和短语，不要长句
2. 每个关键词不超过8个字（适当增加以适应新结构）
3. 重点突出文章的逻辑结构
4. 如果文章不完全符合某种结构，请灵活调整但保持框架清晰
5. 适合制作思维导图使用"""

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