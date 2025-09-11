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
        解析markdown文本为固定的3层思维导图结构
        根节点: Article Analysis
        一级节点: Main Theme, Article Structure, Key Arguments, Important Details, Language Features, Reading Comprehension Points
        二级节点: 每个一级节点下的具体内容点
        
        Args:
            markdown_text (str): markdown格式的分析结果
            
        Returns:
            Dict: 解析后的思维导图结构化数据（固定3层）
        """
        lines = markdown_text.split('\n')
        
        # 固定的3层结构
        structure = {
            'title': 'Article Analysis',
            'children': [
                {'title': 'Main Theme', 'children': []},
                {'title': 'Article Structure', 'children': []},
                {'title': 'Key Arguments', 'children': []},
                {'title': 'Important Details', 'children': []},
                {'title': 'Language Features', 'children': []},
                {'title': 'Reading Comprehension Points', 'children': []}
            ]
        }
        
        # 创建一级节点的映射，便于快速查找
        section_map = {}
        for section in structure['children']:
            section_map[section['title']] = section
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 一级标题 (# Article Analysis) - 忽略，使用固定标题
            if line.startswith('# '):
                continue
                
            # 二级标题 (## Main Theme, ## Article Structure, etc.)
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
                    if 'theme' in title_lower or '主题' in title_lower:
                        current_section = section_map['Main Theme']
                    elif 'structure' in title_lower or '结构' in title_lower:
                        current_section = section_map['Article Structure']
                    elif 'argument' in title_lower or '观点' in title_lower or '论点' in title_lower:
                        current_section = section_map['Key Arguments']
                    elif 'detail' in title_lower or '细节' in title_lower or '事实' in title_lower:
                        current_section = section_map['Important Details']
                    elif 'language' in title_lower or 'feature' in title_lower or '语言' in title_lower or '特征' in title_lower:
                        current_section = section_map['Language Features']
                    elif 'comprehension' in title_lower or 'reading' in title_lower or '理解' in title_lower or '阅读' in title_lower:
                        current_section = section_map['Reading Comprehension Points']
                
            # 三级标题 (### 子标题) - 在固定3层结构中忽略
            elif line.startswith('### '):
                continue
                    
            # 列表项 (- 内容 或 * 内容) - 作为二级节点
            elif (line.startswith('- ') or line.startswith('* ')) and current_section:
                content = line[2:].strip()
                if content:
                    # 清理内容
                    content = self._clean_content(content)
                    if content:  # 确保清理后的内容不为空
                        item = {'title': content, 'children': []}
                        current_section['children'].append(item)
                        
            # 数字列表 (1. 内容) - 作为二级节点
            elif re.match(r'^\d+\.\s', line) and current_section:
                content = re.sub(r'^\d+\.\s', '', line).strip()
                if content:
                    content = self._clean_content(content)
                    if content:
                        item = {'title': content, 'children': []}
                        current_section['children'].append(item)
        
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