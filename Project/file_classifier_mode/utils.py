

def get_pdf_text(pdf_path,filename):
    """获取文本，包括基本清理文本内容"""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"  {filename} 文本提取失败，跳过...")
        return None
    else:
        # 清理文本
        clean_text_content = clean_text(text)
        return clean_text_content
def extract_text_from_pdf(pdf_path):
    """从PDF文件中提取文本"""
    import PyPDF2
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"提取PDF文本时出错 {pdf_path}: {e}")
        return None

def clean_text(text):
    """清理文本，移除特殊字符和多余空格"""
    import re
    text = re.sub(r'[^\x20-\x7E\u4e00-\u9fa5]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


import os
import shutil


def move_files(source, target, success_filename_list):
    """
    根据文件名列表，将源文件夹中存在的对应文件移动到目标文件夹
    """
    try:
        # 检查文件夹
        if not os.path.exists(source):
            raise Exception(f"source folder {source} not exists")

        if not os.path.exists(target):
            os.makedirs(target)

        # 移动文件
        moved_count = 0
        for filename in success_filename_list:
            src_path = os.path.join(source, filename)
            dst_path = os.path.join(target, filename)

            if os.path.exists(src_path):
                shutil.move(src_path, dst_path)
                print(f"Moved: {filename}")
                moved_count += 1
            else:
                print(f"Not found: {filename}")

        print(f"Finished. Moved {moved_count} files")
        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False