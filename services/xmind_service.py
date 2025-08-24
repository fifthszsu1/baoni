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
        解析markdown文本为层次结构
        
        Args:
            markdown_text (str): markdown格式的分析结果
            
        Returns:
            Dict: 解析后的结构化数据
        """
        lines = markdown_text.split('\n')
        structure = {
            'title': 'Article Analysis',
            'children': []
        }
        
        current_section = None
        current_subsection = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 一级标题 (# Article Analysis)
            if line.startswith('# '):
                structure['title'] = line[2:].strip()
                
            # 二级标题 (## 1. 主题概要)
            elif line.startswith('## '):
                section_title = line[3:].strip()
                current_section = {
                    'title': section_title,
                    'children': []
                }
                structure['children'].append(current_section)
                current_subsection = None
                
            # 三级标题 (### 子标题)
            elif line.startswith('### '):
                if current_section:
                    subsection_title = line[4:].strip()
                    current_subsection = {
                        'title': subsection_title,
                        'children': []
                    }
                    current_section['children'].append(current_subsection)
                    
            # 列表项 (- 内容)
            elif line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                if content:
                    item = {'title': content, 'children': []}
                    if current_subsection:
                        current_subsection['children'].append(item)
                    elif current_section:
                        current_section['children'].append(item)
                        
            # 数字列表 (1. 内容)
            elif re.match(r'^\d+\.\s', line):
                content = re.sub(r'^\d+\.\s', '', line).strip()
                if content:
                    item = {'title': content, 'children': []}
                    if current_subsection:
                        current_subsection['children'].append(item)
                    elif current_section:
                        current_section['children'].append(item)
                        
            # 普通段落文本
            elif line and not line.startswith('#'):
                if current_section and line not in ['```', '---']:
                    # 如果是普通文本，添加到当前节点
                    item = {'title': line, 'children': []}
                    if current_subsection:
                        current_subsection['children'].append(item)
                    elif current_section:
                        current_section['children'].append(item)
        
        return structure
    
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