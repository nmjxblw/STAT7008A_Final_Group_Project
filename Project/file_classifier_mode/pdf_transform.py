import PyPDF2
import hashlib
import os
import re


class PDFTransformer:
    def run(self, input_queue, output_queue):
        """
        从队列获取PDF，处理后放入下一队列
        先完成了文字处理,如果需要OCR可以再添加
        这个接口为数据流处理预留
        """

    def transform(self, folder_path, file_name):
        full_path = folder_path + file_name
        """基于文件名生成md5 id"""
        file_id = self.__generate_file_unique_id(file_name)
        
        # 提取基础文本
        file_text = self.__pdf_to_text(full_path)
        
        # 极简OCR策略（针对CV论文）
        ocr_text = self.__smart_ocr(full_path, file_text)
        if ocr_text:
            file_text = file_text + "\n" + ocr_text if file_text else ocr_text
            print(f" OCR识别完成，额外提取{len(ocr_text)}字符")

        result = {
            "file_id": file_id,
            "file_text": file_text,
            "file_name": file_name,
        }
        return result

    def __smart_ocr(self, full_path, base_text):
        """极简OCR策略（simple模式）- 专为CV论文设计
        
        三条规则：
        1. 整页无文本 → 页级OCR
        2. 文本很少且有图 → 页级OCR  
        3. 命中关键图 → 区域OCR
        
        成本保护：
        - 每文档最多OCR 3页
        - 每页最多OCR 2个图
        - 低置信度文本丢弃
        """
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io
            
            # 关键图关键词
            KEY_KEYWORDS = [
                "pipeline", "framework", "diagram", "chart", 
                "PR", "ROC", "heatmap", "ablation", "comparison"
            ]
            
            doc = fitz.open(full_path)
            total_pages = len(doc)
            
            ocr_results = []
            pages_ocred = 0
            max_pages = 3  # 成本保护：最多OCR 3页
            
            print(f" 开始智能OCR分析（{total_pages}页，最多处理{max_pages}页）")
            
            for page_num in range(total_pages):
                if pages_ocred >= max_pages:
                    print(f"️  已达OCR页数上限（{max_pages}页），停止")
                    break
                
                page = doc[page_num]
                
                # 提取页面文本
                page_text = page.get_text()
                char_count = len(page_text.strip())
                
                # 获取页面图片
                images = page.get_images(full=True)
                has_images = len(images) > 0
                
                # 规则1: 整页无文本 → 页级OCR
                if char_count == 0:
                    print(f"  P{page_num+1}: 无文本 → 页级OCR")
                    page_ocr = self.__ocr_page(page)
                    if page_ocr:
                        ocr_results.append(page_ocr)
                        pages_ocred += 1
                    continue
                
                # 规则2: 文本很少且有图 → 页级OCR
                if char_count < 150 and has_images:
                    print(f"  P{page_num+1}: 文本少({char_count}字符)+有图 → 页级OCR")
                    page_ocr = self.__ocr_page(page)
                    if page_ocr:
                        ocr_results.append(page_ocr)
                        pages_ocred += 1
                    continue
                
                # 规则3: 命中关键图 → 区域OCR（最多2个图）
                if has_images:
                    key_figures = self.__find_key_figures(page, page_text, KEY_KEYWORDS)
                    if key_figures:
                        print(f"  P{page_num+1}: 发现{len(key_figures)}个关键图 → 区域OCR")
                        figure_ocr = self.__ocr_figures(page, doc, key_figures[:2])  # 最多2个
                        if figure_ocr:
                            ocr_results.append(figure_ocr)
                            pages_ocred += 1
            
            doc.close()
            
            full_ocr_text = "\n".join(ocr_results)
            print(f" OCR完成: 处理{pages_ocred}页，提取{len(full_ocr_text)}字符")
            return full_ocr_text
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return ""
    
    def __ocr_page(self, page):
        """对整页进行OCR"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # 渲染为图片（150 DPI）
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            # OCR识别
            text = pytesseract.image_to_string(image, lang='eng')
            return text.strip()
            
        except Exception as e:
            return ""
    
    def __find_key_figures(self, page, page_text, keywords):
        """查找包含关键词的Figure/Table"""
        key_figures = []
        
        # 查找Figure和Table的caption
        caption_pattern = r'(Figure|Fig\.|Table)\s+\d+[:\.]?\s*([^\n]+)'
        captions = re.findall(caption_pattern, page_text, re.IGNORECASE)
        
        for cap_type, cap_text in captions:
            # 检查是否包含关键词
            cap_lower = cap_text.lower()
            if any(kw.lower() in cap_lower for kw in keywords):
                key_figures.append({
                    'type': cap_type,
                    'text': cap_text
                })
        
        return key_figures
    
    def __ocr_figures(self, page, doc, figures):
        """对特定图片区域进行OCR"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            results = []
            images = page.get_images(full=True)
            
            # 简化：对页面中的前N个图片做OCR
            for img_idx, img in enumerate(images[:len(figures)]):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # OCR识别
                    text = pytesseract.image_to_string(image, lang='eng')
                    if text.strip():
                        results.append(text.strip())
                        
                except Exception:
                    pass
            
            return "\n".join(results)
            
        except Exception:
            return ""

    def __pdf_to_text(self, full_path):
        """将PDF文件转换为文本文件"""
        try:
            text_content = ""
            with open(full_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            cleaned_text_content = self.__clean_text(text_content)
            return cleaned_text_content
        except Exception as e:
            print(e)
            print("failed at changing pdf to text")
            return None

    def __generate_file_unique_id(self, pdf_path):

        md5_hash = hashlib.md5()

        # 将字符串编码为字节，然后更新哈希对象
        # 注意：必须对字符串进行编码，因为哈希函数处理的是字节数据
        md5_hash.update(pdf_path.encode("utf-8"))

        # 返回计算出的 MD5 哈希值（32位十六进制字符串）
        return md5_hash.hexdigest()

    def __clean_text(self, content):
        """清理文本，移除特殊字符和多余空格"""
        import re

        content = re.sub(r"[^\x20-\x7E\u4e00-\u9fa5]+", " ", content)
        content = re.sub(r"\s+", " ", content)
        return content.strip()
