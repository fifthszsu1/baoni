import logging
import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal

from .ocr_service import OCRService
from .openai_service import OpenAIService
from models import db, Composition, Topic, ScoringRule

logger = logging.getLogger(__name__)

class CompositionScoringService:
    """作文评分服务 - 集成OCR识别、AI评分和数据存储"""
    
    def __init__(self):
        """初始化服务"""
        self.ocr_service = OCRService()
        self.openai_service = OpenAIService()
    
    def extract_student_info_and_composition(self, ocr_text: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        从OCR文本中提取学生姓名、学号和作文内容
        
        Args:
            ocr_text (str): OCR识别的原始文本
            
        Returns:
            Tuple: (学生姓名, 学号, 作文内容)
        """
        try:
            # 使用AI来解析学生信息和作文内容
            system_prompt = """你是一个专业的文本解析助手。请从学生手写的英语作文OCR识别文本中提取以下信息：

1. 学生姓名（通常在开头，可能是中文）
2. 学号（如果有的话，通常是数字）
3. 纯英文作文内容（去除姓名、学号等信息）

请严格按照以下JSON格式输出：
{
    "student_name": "学生姓名或null",
    "student_id": "学号或null", 
    "composition_content": "纯英文作文内容"
}

注意：
- 如果无法识别姓名或学号，请设为null
- 作文内容必须是纯英文，去除所有中文信息
- 保持作文的原始格式和段落结构"""

            user_prompt = f"请解析以下OCR识别的文本：\n\n{ocr_text}"
            
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON结果
            import json
            try:
                result = json.loads(result_text)
                student_name = result.get('student_name')
                student_id = result.get('student_id')
                composition_content = result.get('composition_content', ocr_text)
                
                # 如果AI返回"null"字符串，转换为None
                if student_name == "null":
                    student_name = None
                if student_id == "null":
                    student_id = None
                    
                return student_name, student_id, composition_content
                
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用简单的正则表达式方法
                logger.warning("AI返回的JSON格式有误，使用备用方法解析")
                return self._extract_student_info_regex(ocr_text)
                
        except Exception as e:
            logger.error(f"AI解析学生信息失败: {str(e)}")
            # 使用备用的正则表达式方法
            return self._extract_student_info_regex(ocr_text)
    
    def _extract_student_info_regex(self, ocr_text: str) -> Tuple[Optional[str], Optional[str], str]:
        """使用正则表达式提取学生信息的备用方法"""
        lines = ocr_text.split('\n')
        student_name = None
        student_id = None
        composition_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 尝试匹配中文姓名（前3行内查找）
            if i < 3 and student_name is None:
                chinese_match = re.search(r'[\u4e00-\u9fa5]{2,4}', line)
                if chinese_match:
                    student_name = chinese_match.group()
                    continue
            
            # 尝试匹配学号（数字）
            if student_id is None:
                id_match = re.search(r'\b\d{8,12}\b', line)
                if id_match:
                    student_id = id_match.group()
                    continue
            
            # 如果这行主要是英文，加入作文内容
            english_chars = len(re.findall(r'[a-zA-Z]', line))
            total_chars = len(line)
            if total_chars > 0 and english_chars / total_chars > 0.5:
                composition_lines.append(line)
        
        composition_content = '\n'.join(composition_lines)
        return student_name, student_id, composition_content
    
    def score_composition(self, composition_content: str, topic: Topic, scoring_rule: ScoringRule) -> Dict[str, Any]:
        """
        使用AI对作文进行评分
        
        Args:
            composition_content (str): 作文内容
            topic (Topic): 题目对象
            scoring_rule (ScoringRule): 评分规则对象
            
        Returns:
            Dict: 评分结果
        """
        try:
            # 构建评分提示词
            system_prompt = f"""你是一位专业的高中英语教师，负责评判英语读后续写作文。

题目信息：
标题：{topic.title}
内容：{topic.content}
关键要点：{', '.join(topic.get_key_points_list())}
字数要求：{topic.word_count_requirement or '150词左右'}

评分标准（{scoring_rule.rule_name}）：
{scoring_rule.rule_description}

评分档次："""

            # 添加评分档次信息
            for range_name, range_info in scoring_rule.score_ranges.items():
                system_prompt += f"\n{range_name}（{range_info['min_score']}-{range_info['max_score']}分）：{range_info['description']}"

            system_prompt += """

请根据以上标准对学生作文进行评分，并严格按照以下JSON格式输出：
{
    "score": 具体分数（数字），
    "score_range": "分数档次名称",
    "word_count": 作文字数统计,
    "strengths": ["优点1", "优点2", "优点3"],
    "weaknesses": ["不足1", "不足2", "不足3"],
    "suggestions": ["建议1", "建议2", "建议3"],
    "detailed_feedback": "详细的评分反馈，包含对内容、语言、结构的具体分析"
}

评分要求：
1. 分数必须在{scoring_rule.min_score}-{scoring_rule.max_score}分范围内
2. 评价要客观公正，既要指出优点也要指出不足
3. 建议要具体可行，有助于学生提高
4. 详细反馈要分析内容、语言、结构三个方面"""

            user_prompt = f"请评分以下学生作文：\n\n{composition_content}"
            
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 解析JSON结果
            import json
            try:
                result = json.loads(result_text)
                
                # 验证分数范围
                score = float(result.get('score', 0))
                if score < scoring_rule.min_score or score > scoring_rule.max_score:
                    score = max(scoring_rule.min_score, min(score, scoring_rule.max_score))
                
                return {
                    'success': True,
                    'score': score,
                    'score_range': result.get('score_range', ''),
                    'word_count': result.get('word_count', 0),
                    'strengths': result.get('strengths', []),
                    'weaknesses': result.get('weaknesses', []),
                    'suggestions': result.get('suggestions', []),
                    'detailed_feedback': result.get('detailed_feedback', ''),
                    'tokens_used': response.usage.total_tokens if response.usage else 0
                }
                
            except json.JSONDecodeError:
                logger.error(f"AI评分返回的JSON格式有误: {result_text}")
                return {
                    'success': False,
                    'error': 'AI评分结果格式错误',
                    'raw_response': result_text
                }
                
        except Exception as e:
            logger.error(f"AI评分失败: {str(e)}")
            return {
                'success': False,
                'error': f'评分过程中发生错误: {str(e)}'
            }
    
    def process_composition_image(self, image_data: bytes, topic_id: int, 
                                scoring_rule_id: int, teacher_id: Optional[int] = None) -> Dict[str, Any]:
        """
        处理作文图片的完整流程：OCR识别 → 信息提取 → AI评分 → 数据存储
        
        Args:
            image_data (bytes): 图片二进制数据
            topic_id (int): 题目ID
            scoring_rule_id (int): 评分规则ID
            teacher_id (Optional[int]): 教师ID
            
        Returns:
            Dict: 处理结果
        """
        try:
            # 获取题目和评分规则
            topic = Topic.query.get(topic_id)
            if not topic:
                return {'success': False, 'error': f'题目ID {topic_id} 不存在'}
                
            scoring_rule = ScoringRule.query.get(scoring_rule_id)
            if not scoring_rule:
                return {'success': False, 'error': f'评分规则ID {scoring_rule_id} 不存在'}
            
            # 创建作文记录
            composition = Composition(
                topic_id=topic_id,
                scoring_rule_id=scoring_rule_id,
                teacher_id=teacher_id,
                original_image_url='',  # 暂时为空，后续需要保存图片
                processing_status='processing'
            )
            db.session.add(composition)
            db.session.commit()
            
            try:
                # 1. OCR识别
                logger.info(f"开始OCR识别作文 {composition.id}")
                ocr_result = self.ocr_service.extract_text_from_image(image_data)
                
                if not ocr_result['success']:
                    composition.update_processing_status('failed', ocr_result['error'])
                    return {
                        'success': False,
                        'error': f"OCR识别失败: {ocr_result['error']}",
                        'composition_id': composition.id
                    }
                
                ocr_text = ocr_result['extracted_text']
                composition.ocr_text = ocr_text
                
                # 2. 提取学生信息和作文内容
                logger.info(f"提取学生信息和作文内容")
                student_name, student_id, composition_content = self.extract_student_info_and_composition(ocr_text)
                
                composition.student_name = student_name
                composition.student_id = student_id
                composition.composition_content = composition_content
                
                # 计算字数
                composition.calculate_word_count()
                
                # 3. AI评分
                logger.info(f"开始AI评分")
                scoring_result = self.score_composition(composition_content, topic, scoring_rule)
                
                if not scoring_result['success']:
                    composition.update_processing_status('failed', scoring_result['error'])
                    return {
                        'success': False,
                        'error': f"AI评分失败: {scoring_result['error']}",
                        'composition_id': composition.id
                    }
                
                # 保存评分结果
                composition.ai_score = Decimal(str(scoring_result['score']))
                
                # 组合反馈信息
                feedback_parts = []
                if scoring_result.get('detailed_feedback'):
                    feedback_parts.append(f"详细评价：{scoring_result['detailed_feedback']}")
                
                if scoring_result.get('strengths'):
                    feedback_parts.append(f"优点：{'; '.join(scoring_result['strengths'])}")
                
                if scoring_result.get('weaknesses'):
                    feedback_parts.append(f"不足：{'; '.join(scoring_result['weaknesses'])}")
                
                if scoring_result.get('suggestions'):
                    feedback_parts.append(f"建议：{'; '.join(scoring_result['suggestions'])}")
                
                composition.ai_feedback = '\n\n'.join(feedback_parts)
                
                # 更新状态为完成
                composition.update_processing_status('completed')
                
                logger.info(f"作文 {composition.id} 处理完成，得分: {composition.ai_score}")
                
                return {
                    'success': True,
                    'composition_id': composition.id,
                    'student_name': student_name,
                    'student_id': student_id,
                    'score': float(composition.ai_score),
                    'score_range': scoring_result.get('score_range'),
                    'word_count': composition.word_count,
                    'feedback': composition.ai_feedback,
                    'processing_time': (datetime.utcnow() - composition.created_at).total_seconds()
                }
                
            except Exception as e:
                composition.update_processing_status('failed', str(e))
                raise
                
        except Exception as e:
            logger.error(f"处理作文图片失败: {str(e)}")
            return {
                'success': False,
                'error': f'处理过程中发生错误: {str(e)}'
            } 