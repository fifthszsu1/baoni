import xmind
import os
import uuid
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class XMindService:
    """XMind思维导图生成服务"""
    
    def __init__(self):
        """初始化XMind服务"""
        self.upload_folder = Config.UPLOAD_FOLDER
    
    def parse_markdown_to_structure(self, markdown_text: str) -> Dict[str, Any]:
        """
        解析markdown文本为动态的思维导图结构
        根据文体类型（说明文/议论文）生成对应的结构
        
        Args:
            markdown_text (str): markdown格式的分析结果
            
        Returns:
            Dict: 解析后的思维导图结构化数据
        """
        lines = markdown_text.split('\n')
        
        # 初始化基础结构
        structure = {
            'title': '文章分析',
            'children': []
        }
        
        # 检测文体类型
        article_type = None
        structure_type = None
        
        logger.info(f"开始解析markdown文本，总行数: {len(lines)}")
        logger.info(f"原始文本前200字符: {markdown_text[:200]}")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            logger.info(f"第{i+1}行: {line}")
            
            if '文体类型' in line:
                logger.info(f"跳过文体类型标题行: {line}")
                continue
            if '说明文' in line and not article_type:
                article_type = '说明文'
                logger.info(f"检测到文体类型: {article_type}")
            elif '议论文' in line and not article_type:
                article_type = '议论文'
                logger.info(f"检测到文体类型: {article_type}")
            elif '分类说明' in line or '对比说明' in line or '流程说明' in line or '因果说明' in line:
                structure_type = line
                logger.info(f"检测到结构类型: {structure_type}")
                break
            elif '**分类说明**' in line or '**对比说明**' in line or '**流程说明**' in line or '**因果说明**' in line:
                # 处理markdown粗体格式，只提取关键词
                if '**分类说明**' in line:
                    structure_type = '分类说明'
                elif '**对比说明**' in line:
                    structure_type = '对比说明'
                elif '**流程说明**' in line:
                    structure_type = '流程说明'
                elif '**因果说明**' in line:
                    structure_type = '因果说明'
                logger.info(f"检测到粗体结构类型: {structure_type}")
                break
            # 检查是否有结构关键词（更宽松的匹配）
            elif any(keyword in line for keyword in ['论点', '论据', '总结', '呼吁']):
                if not article_type:
                    article_type = '议论文'
                    logger.info(f"通过关键词检测到议论文: {line}")
                break
            elif any(keyword in line for keyword in ['概念', '分类', '对比', '流程', '因果', '现象', '原因', '影响']):
                if not article_type:
                    article_type = '说明文'
                # 尝试从行中提取具体的说明文类型
                if '分类' in line or '概念' in line:
                    structure_type = '分类说明'
                elif '对比' in line or '差异' in line:
                    structure_type = '对比说明'
                elif '流程' in line or '步骤' in line:
                    structure_type = '流程说明'
                elif '因果' in line or '原因' in line or '影响' in line:
                    structure_type = '因果说明'
                logger.info(f"通过关键词检测到说明文，类型: {structure_type}, 触发行: {line}")
                break
        
        logger.info(f"最终检测结果 - 文体类型: {article_type}, 结构类型: {structure_type}")
        
        # 如果都没检测到，尝试从内容中智能推断
        if not article_type and not structure_type:
            content_lower = markdown_text.lower()
            if any(word in content_lower for word in ['argument', 'thesis', 'evidence', 'conclude', 'persuade']):
                article_type = '议论文'
                logger.info("通过英文关键词推断为议论文")
            elif any(word in content_lower for word in ['explain', 'describe', 'process', 'compare', 'contrast', 'classify']):
                article_type = '说明文'
                logger.info("通过英文关键词推断为说明文")
        
        # 根据文体类型设置不同的结构
        if article_type == '说明文':
            if structure_type and '分类说明' in structure_type:
                structure['children'] = [
                    {'title': '主要概念', 'children': []},
                    {'title': '分类标准', 'children': []},
                    {'title': '各类别特点', 'children': []}
                ]
            elif structure_type and '对比说明' in structure_type:
                structure['children'] = [
                    {'title': '对比对象', 'children': []},
                    {'title': '对比角度', 'children': []},
                    {'title': '差异要点', 'children': []}
                ]
            elif structure_type and '流程说明' in structure_type:
                structure['children'] = [
                    {'title': '起始状态', 'children': []},
                    {'title': '关键步骤', 'children': []},
                    {'title': '最终结果', 'children': []}
                ]
            elif structure_type and '因果说明' in structure_type:
                structure['children'] = [
                    {'title': '现象描述', 'children': []},
                    {'title': '原因分析', 'children': []},
                    {'title': '结果影响', 'children': []}
                ]
            else:
                # 默认说明文结构
                structure['children'] = [
                    {'title': '说明对象', 'children': []},
                    {'title': '说明方法', 'children': []},
                    {'title': '说明要点', 'children': []}
                ]
        elif article_type == '议论文':
            structure['children'] = [
                {'title': '论点', 'children': []},
                {'title': '论据', 'children': []},
                {'title': '总结呼吁', 'children': []}
            ]
        else:
            # 兼容旧格式 - 保持what/why/how结构
            structure['children'] = [
                {'title': 'What（是什么）', 'children': []},
                {'title': 'Why（为什么）', 'children': []},
                {'title': 'How（怎么样）', 'children': []}
            ]
        
        # 创建一级节点的映射，便于快速查找
        section_map = {}
        for section in structure['children']:
            section_map[section['title']] = section
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 一级标题 (# 文章分析) - 忽略，使用固定标题
            if line.startswith('# '):
                continue
                
            # 二级标题 (## 中心思想, ## What（是什么）, etc.)
            elif line.startswith('## '):
                section_title = line[3:].strip()
                # 清理标题中的序号
                section_title = re.sub(r'^\d+\.\s*', '', section_title)
                
                # 查找匹配的固定节点
                current_section = None
                for fixed_title, section in section_map.items():
                    if fixed_title.lower() in section_title.lower() or section_title.lower() in fixed_title.lower():
                        current_section = section
                        break
                        
                # 如果没找到匹配的，根据关键词判断
                if not current_section:
                    title_lower = section_title.lower()
                    
                    # 新的文体结构关键词匹配
                    for fixed_title in section_map.keys():
                        fixed_lower = fixed_title.lower()
                        
                        # 直接匹配
                        if fixed_title in section_title or section_title in fixed_title:
                            current_section = section_map[fixed_title]
                            break
                        
                        # 关键词匹配
                        if ('论点' in fixed_lower and ('论点' in title_lower or '观点' in title_lower or '主张' in title_lower)) or \
                           ('论据' in fixed_lower and ('论据' in title_lower or '证据' in title_lower or '支持' in title_lower)) or \
                           ('总结' in fixed_lower and ('总结' in title_lower or '呼吁' in title_lower or '结论' in title_lower)) or \
                           ('概念' in fixed_lower and ('概念' in title_lower or '定义' in title_lower or '主要' in title_lower)) or \
                           ('标准' in fixed_lower and ('标准' in title_lower or '依据' in title_lower or '分类' in title_lower)) or \
                           ('特点' in fixed_lower and ('特点' in title_lower or '特征' in title_lower or '类别' in title_lower)) or \
                           ('对象' in fixed_lower and ('对象' in title_lower or '比较' in title_lower)) or \
                           ('角度' in fixed_lower and ('角度' in title_lower or '方面' in title_lower)) or \
                           ('差异' in fixed_lower and ('差异' in title_lower or '不同' in title_lower or '区别' in title_lower)) or \
                           ('起始' in fixed_lower and ('起始' in title_lower or '开始' in title_lower or '初始' in title_lower)) or \
                           ('步骤' in fixed_lower and ('步骤' in title_lower or '过程' in title_lower or '阶段' in title_lower)) or \
                           ('结果' in fixed_lower and ('结果' in title_lower or '终点' in title_lower or '最终' in title_lower)) or \
                           ('现象' in fixed_lower and ('现象' in title_lower or '描述' in title_lower or '情况' in title_lower)) or \
                           ('原因' in fixed_lower and ('原因' in title_lower or '分析' in title_lower or '成因' in title_lower)) or \
                           ('影响' in fixed_lower and ('影响' in title_lower or '后果' in title_lower or '作用' in title_lower)):
                            current_section = section_map[fixed_title]
                            break
                    
                    # 兼容旧格式的关键词匹配
                    if not current_section:
                        if 'what' in title_lower or '是什么' in title_lower or '什么' in title_lower:
                            for key in section_map.keys():
                                if 'What' in key:
                                    current_section = section_map[key]
                                    break
                        elif 'why' in title_lower or '为什么' in title_lower:
                            for key in section_map.keys():
                                if 'Why' in key:
                                    current_section = section_map[key]
                                    break
                        elif 'how' in title_lower or '怎么样' in title_lower or '如何' in title_lower or '方式' in title_lower:
                            for key in section_map.keys():
                                if 'How' in key:
                                    current_section = section_map[key]
                                    break
                
            # 三级标题 (### 子标题) - 在固定3层结构中忽略
            elif line.startswith('### '):
                continue
                    
            # 列表项 (- 内容 或 * 内容) - 作为二级节点
            elif (line.startswith('- ') or line.startswith('* ')):
                content = line[2:].strip()
                if content:
                    # 检查是否是结构化内容（包含**标题**格式）
                    if '**' in content and '**：' in content:
                        # 提取标题和内容
                        parts = content.split('**：', 1)
                        if len(parts) == 2:
                            title_part = parts[0].replace('**', '').strip()
                            content_part = parts[1].strip()
                            
                            # 根据标题找到对应的节点
                            target_section = None
                            for fixed_title, section in section_map.items():
                                if any(keyword in title_part for keyword in ['起始', '开始', '初始']) and '起始' in fixed_title:
                                    target_section = section
                                    break
                                elif any(keyword in title_part for keyword in ['步骤', '过程', '关键']) and '步骤' in fixed_title:
                                    target_section = section
                                    break
                                elif any(keyword in title_part for keyword in ['结果', '最终', '终点']) and '结果' in fixed_title:
                                    target_section = section
                                    break
                                elif any(keyword in title_part for keyword in ['论点', '观点']) and '论点' in fixed_title:
                                    target_section = section
                                    break
                                elif any(keyword in title_part for keyword in ['论据', '证据']) and '论据' in fixed_title:
                                    target_section = section
                                    break
                                elif any(keyword in title_part for keyword in ['总结', '呼吁']) and '总结' in fixed_title:
                                    target_section = section
                                    break
                            
                            if target_section:
                                # 清理并添加内容
                                clean_content = self._clean_content(content_part)
                                if clean_content:
                                    item = {'title': clean_content, 'children': []}
                                    target_section['children'].append(item)
                                    continue
                    
                    # 如果不是结构化内容，按原逻辑处理
                    if current_section:
                        clean_content = self._clean_content(content)
                        if clean_content:
                            item = {'title': clean_content, 'children': []}
                            current_section['children'].append(item)
                        
            # 数字列表 (1. 内容) - 作为二级节点
            elif re.match(r'^\s*\d+\.\s', line):  # 支持缩进的数字列表
                content = re.sub(r'^\s*\d+\.\s', '', line).strip()
                if content:
                    content = self._clean_content(content)
                    if content:
                        item = {'title': content, 'children': []}
                        # 如果有当前节点，添加到当前节点；否则尝试找到合适的节点
                        if current_section:
                            current_section['children'].append(item)
                        else:
                            # 尝试根据上下文找到合适的节点（通常是"关键步骤"或类似的节点）
                            for section_title, section in section_map.items():
                                if '步骤' in section_title or '过程' in section_title:
                                    section['children'].append(item)
                                    break
        
        # 确保每个一级节点至少有一些内容，如果为空则添加占位内容
        for section in structure['children']:
            if not section['children']:
                section['children'].append({
                    'title': 'Content will be analyzed here - 此处将分析相关内容',
                    'children': []
                })
        
        return structure
    
    def _clean_content(self, content: str) -> str:
        """
        清理和格式化内容文本
        
        Args:
            content (str): 原始内容
            
        Returns:
            str: 清理后的内容
        """
        if not content:
            return ""
            
        # 移除markdown格式
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # 粗体
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # 斜体
        content = re.sub(r'`(.*?)`', r'\1', content)        # 代码
        
        # 移除多余的空格和换行
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 如果内容太长，适当截取（保留完整句子）
        if len(content) > 120:
            # 尝试在句号处截断
            sentences = content.split('.')
            if len(sentences) > 1:
                result = sentences[0] + '.'
                if len(result) < 80 and len(sentences) > 1:
                    result += sentences[1] + '.'
                return result.strip()
            else:
                # 如果没有句号，在合适位置截断
                return content[:100] + '...'
        
        return content
    
    def create_xmind_from_structure(self, structure: Dict[str, Any], original_text: str = "") -> Optional[str]:
        """
        根据结构化数据创建XMind文件
        
        Args:
            structure (Dict): 结构化的分析数据
            original_text (str): 原始文本，用于添加备注
            
        Returns:
            str: 生成的XMind文件路径
        """
        try:
            logger.info(f"Creating XMind file with structure: {structure.get('title', 'No title')}")
            
            # 生成文件名 - 先创建文件名，XMind需要知道文件名才能创建
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"analysis_{timestamp}_{unique_id}.xmind"
            
            # 确保上传目录存在
            if not os.path.exists(self.upload_folder):
                os.makedirs(self.upload_folder)
                logger.info(f"Created upload folder: {self.upload_folder}")
            
            filepath = os.path.join(self.upload_folder, filename)
            logger.info(f"Creating XMind file at: {filepath}")
            
            # 创建workbook和sheet - 使用具体的文件路径
            workbook = xmind.load(filepath)
            sheet = workbook.getPrimarySheet()
            sheet.setTitle("English Article Analysis")
            logger.info("XMind workbook and sheet created successfully")
            
            # 获取根主题
            root_topic = sheet.getRootTopic()
            root_topic.setTitle(structure.get('title', 'Article Analysis'))
            logger.info(f"Set root topic title: {structure.get('title', 'Article Analysis')}")
            
            # 添加原文摘要作为备注
            if original_text:
                preview = original_text[:200] + "..." if len(original_text) > 200 else original_text
                root_topic.setPlainNotes(f"Original Text Preview:\n{preview}")
                logger.info("Added original text preview as notes")
            
            # 递归添加子主题
            children_count = len(structure.get('children', []))
            logger.info(f"Adding {children_count} child topics")
            self._add_topics_recursively(root_topic, structure.get('children', []))
            logger.info("Child topics added successfully")
            
            # 保存文件
            logger.info(f"Saving XMind file to: {filepath}")
            xmind.save(workbook, filepath)
            logger.info("XMind file saved successfully")
            
            # 验证文件是否创建
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"XMind file created successfully: {filepath}, size: {file_size} bytes")
                return filename
            else:
                logger.error("XMind file was not created!")
                return None
            
        except Exception as e:
            logger.error(f"Failed to create XMind file: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def _add_topics_recursively(self, parent_topic, children: List[Dict[str, Any]]):
        """
        递归添加主题节点
        
        Args:
            parent_topic: 父级主题节点
            children (List): 子节点列表
        """
        for child_data in children:
            # 创建子主题
            child_topic = parent_topic.addSubTopic()
            child_topic.setTitle(child_data.get('title', ''))
            
            # 如果有子节点，递归添加
            child_children = child_data.get('children', [])
            if child_children:
                self._add_topics_recursively(child_topic, child_children)
    
    def generate_xmind(self, markdown_analysis: str, original_text: str = "") -> Dict[str, Any]:
        """
        根据markdown分析结果生成XMind文件
        
        Args:
            markdown_analysis (str): markdown格式的分析结果
            original_text (str): 原始文本
            
        Returns:
            Dict: 包含结果信息的字典
        """
        try:
            logger.info("Starting XMind generation process")
            logger.info(f"Markdown analysis length: {len(markdown_analysis)} characters")
            
            # 解析markdown结构
            logger.info("Parsing markdown structure...")
            structure = self.parse_markdown_to_structure(markdown_analysis)
            logger.info(f"Parsed structure - title: {structure.get('title')}, children: {len(structure.get('children', []))}")
            
            # 创建XMind文件
            logger.info("Creating XMind file from structure...")
            filename = self.create_xmind_from_structure(structure, original_text)
            
            if filename:
                logger.info(f"XMind generation completed successfully: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'download_url': f'/downloads/{filename}',
                    'structure': structure
                }
            else:
                logger.error("XMind file generation failed - no filename returned")
                return {
                    'success': False,
                    'error': 'XMind file generation failed'
                }
                
        except Exception as e:
            logger.error(f"XMind generation process failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            } 