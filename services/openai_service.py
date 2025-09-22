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
        分析英文文本，判断文体类型（说明文/议论文），然后根据文体结构生成思维导图
        
        Args:
            text (str): 需要分析的英文文本
            
        Returns:
            Dict: 包含分析结果的字典，包括文体类型和思维导图关键词
        """
        try:
            # 构建优化的文体分析提示词
            system_prompt = """你是专业的英文文章分析师。请分析文章的文体类型并生成思维导图关键词。

# 分析步骤

## 第一步：判断文体类型
从以下4种文体类型中选择最符合的一种：

**事实类说明文** - 解释既定事实、概念或现象
- 特征：描述客观存在的事物，回答"是什么"和"怎么样"
- 包括：事物介绍、概念解释、现象说明、技术原理等

**研究类说明文** - 报告科学研究或实验过程  
- 特征：展示新知识的发现过程，回答"为什么"和"如何证明"
- 包括：实验报告、调查研究、数据分析等

**问题解决类说明文** - 分析问题并提出解决方案
- 特征：识别问题、分析原因、提出对策，回答"怎么办"
- 包括：政策建议、改革方案、技术应用等

**议论文** - 提出观点并进行论证
- 特征：表达作者观点，通过论证说服读者，回答"应该怎样"
- 包括：观点论证、价值判断、立场阐述、评论分析等

## 第二步：提取结构关键词
根据文体类型使用对应框架：

**事实类结构**：引入话题 → 核心定义 → 主要特点 → 分类构成 → 应用意义
**研究类结构**：研究背景 → 研究方法 → 主要发现 → 结论意义  
**问题解决类结构**：问题现状 → 原因分析 → 解决方案 → 效果评估
**议论文结构**：提出论点 → 论证过程 → 反驳质疑 → 总结观点

# 输出格式

## 文体类型
[事实类说明文/研究类说明文/问题解决类说明文/议论文]

## 文章主题
[用1-2个关键词概括文章核心主题]

## 思维导图结构
**中心主题**: [核心关键词]

**主要分支**: 
- 分支1: [关键词]
  - 子分支: [关键词1], [关键词2]
- 分支2: [关键词]  
  - 子分支: [关键词1], [关键词2]
- 分支3: [关键词]
  - 子分支: [关键词1], [关键词2]
- 分支4: [关键词]
  - 子分支: [关键词1], [关键词2]

# 关键要求
1. 关键词简洁精准，每个不超过6个字
2. 突出文章逻辑结构和核心要点
3. 适合制作可视化思维导图
4. 保持层次清晰，便于理解记忆"""

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