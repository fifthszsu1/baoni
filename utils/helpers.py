import os
import re
import hashlib
from typing import Optional, List
from datetime import datetime

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全的字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 清理后的安全文件名
    """
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    
    # 如果文件名为空或只有扩展名，生成默认名称
    if not filename or filename.startswith('.'):
        filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return filename

def generate_file_hash(content: str) -> str:
    """
    生成内容的MD5哈希值
    
    Args:
        content (str): 文件内容
        
    Returns:
        str: MD5哈希值
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def validate_text_content(text: str) -> tuple[bool, Optional[str]]:
    """
    验证文本内容是否适合分析
    
    Args:
        text (str): 要验证的文本
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not text or not text.strip():
        return False, "文本内容不能为空"
    
    text = text.strip()
    
    # 检查最小长度
    if len(text) < 50:
        return False, "文本内容太短，请提供至少50个字符的内容"
    
    # 检查最大长度（避免处理过长的文本）
    if len(text) > 10000:
        return False, "文本内容太长，请提供不超过10000个字符的内容"
    
    # 检查是否主要包含英文内容
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(re.sub(r'\s+', '', text))
    
    if total_chars > 0 and english_chars / total_chars < 0.5:
        return False, "请提供主要包含英文字母的文本内容"
    
    return True, None

def clean_upload_folder(upload_folder: str, max_age_hours: int = 24):
    """
    清理上传文件夹中的旧文件
    
    Args:
        upload_folder (str): 上传文件夹路径
        max_age_hours (int): 文件最大保留时间（小时）
    """
    try:
        if not os.path.exists(upload_folder):
            return
        
        current_time = datetime.now()
        
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            
            if os.path.isfile(file_path):
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                # 删除超过指定时间的文件
                if age_hours > max_age_hours:
                    try:
                        os.remove(file_path)
                        print(f"删除旧文件: {filename}")
                    except OSError:
                        pass  # 忽略删除失败的情况
                        
    except Exception as e:
        print(f"清理上传文件夹失败: {str(e)}")

def extract_text_preview(text: str, max_length: int = 200) -> str:
    """
    提取文本预览
    
    Args:
        text (str): 完整文本
        max_length (int): 最大预览长度
        
    Returns:
        str: 文本预览
    """
    if len(text) <= max_length:
        return text
    
    # 尝试在词边界处截断
    preview = text[:max_length]
    last_space = preview.rfind(' ')
    
    if last_space > max_length * 0.8:  # 如果最后一个空格不太靠前
        preview = preview[:last_space]
    
    return preview + "..." 