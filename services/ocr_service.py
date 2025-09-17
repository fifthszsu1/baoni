import logging
from typing import Optional, Dict, Any
import io
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

class OCRService:
    """Tesseract OCR图片文字识别服务"""
    
    def __init__(self):
        """初始化Tesseract OCR"""
        try:
            import pytesseract
            # 测试Tesseract是否可用
            pytesseract.get_tesseract_version()
            self.tesseract = pytesseract
            logger.info("Tesseract OCR初始化成功")
            self.available = True
        except Exception as e:
            logger.error(f"Tesseract OCR初始化失败: {str(e)}")
            self.tesseract = None
            self.available = False
    
    def extract_text_from_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        从图片中提取英文文本
        
        Args:
            image_data (bytes): 图片的二进制数据
            
        Returns:
            Dict: 包含提取结果的字典
        """
        if not self.available:
            return {
                'success': False,
                'error': 'OCR服务未正确初始化',
                'extracted_text': None
            }
        
        try:
            # 将二进制数据转换为PIL图像
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB格式（如果是RGBA或其他格式）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"开始OCR识别，图片尺寸: {image.size}")
            
            # 使用PIL进行图像预处理，避免OpenCV依赖
            # 转为灰度图
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(2.0)
            
            # 锐化图像
            sharpened_image = enhanced_image.filter(ImageFilter.SHARPEN)
            
            # 如果图片太小，放大2倍提高识别率
            width, height = sharpened_image.size
            if width < 1000 or height < 1000:
                new_size = (width * 2, height * 2)
                processed_image = sharpened_image.resize(new_size, Image.Resampling.LANCZOS)
            else:
                processed_image = sharpened_image
            
            # 使用Tesseract进行OCR识别
            # 配置参数：识别中英文，优化识别精度
            custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
            
            # 获取详细识别结果（包含置信度）
            data = self.tesseract.image_to_data(processed_image, config=custom_config, output_type=self.tesseract.Output.DICT)
            
            # 提取文本和置信度
            extracted_words = []
            total_confidence = 0
            valid_words = 0
            
            for i in range(len(data['text'])):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()
                
                # 只保留置信度较高的文本（> 30）
                if confidence > 30 and text:
                    extracted_words.append(text)
                    total_confidence += confidence
                    valid_words += 1
            
            if not extracted_words:
                # 如果没有识别到高置信度文本，尝试简单的OCR
                simple_text = self.tesseract.image_to_string(processed_image, config=custom_config).strip()
                if simple_text:
                    return {
                        'success': True,
                        'extracted_text': simple_text,
                        'confidence': 0,
                        'lines_count': len(simple_text.split('\n'))
                    }
                else:
                    return {
                        'success': False,
                        'error': '图片中未识别到文本内容',
                        'extracted_text': None
                    }
            
            # 组合识别的文本，保持原有的空格和换行结构
            extracted_text = ' '.join(extracted_words)
            
            # 简单的文本后处理：合并断行
            lines = []
            current_line = []
            
            for word in extracted_words:
                current_line.append(word)
                # 如果单词以句号、问号、感叹号结尾，认为是句子结束
                if word.endswith(('.', '!', '?')):
                    lines.append(' '.join(current_line))
                    current_line = []
            
            # 添加剩余的单词
            if current_line:
                lines.append(' '.join(current_line))
            
            final_text = '\n'.join(lines) if lines else extracted_text
            avg_confidence = total_confidence / valid_words if valid_words > 0 else 0
            
            logger.info(f"OCR识别成功，识别了 {valid_words} 个单词，平均置信度: {avg_confidence:.1f}")
            
            return {
                'success': True,
                'extracted_text': final_text,
                'confidence': avg_confidence,
                'lines_count': len(lines)
            }
            
        except Exception as e:
            logger.error(f"OCR识别失败: {str(e)}")
            return {
                'success': False,
                'error': f'OCR识别过程中发生错误: {str(e)}',
                'extracted_text': None
            }
    
    def is_available(self) -> bool:
        """检查OCR服务是否可用"""
        return self.available 