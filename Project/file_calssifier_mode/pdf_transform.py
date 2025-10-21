
import PyPDF2
import hashlib




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
        #TODO:更细粒度的转text处理
        file_text = self.__pdf_to_text(full_path)
        #TODO:实现OCR
        self.__pdf_ocr(full_path)

        result = {
            "file_id": file_id,
            "file_text": file_text,
            "file_name": file_name,
        }
        return result

    def __pdf_ocr(self, full_path):
        print("ocr(还没实现)")

    def __pdf_to_text(self, full_path):
        """将PDF文件转换为文本文件"""
        try:
            text_content = ""
            with open(full_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            cleaned_text_content = self.__clean_text(text_content)
            return cleaned_text_content
        except Exception as e:
            print(e)
            print("failed at changing pdf to text")
            return None






    def __generate_file_unique_id(self,pdf_path):

        md5_hash = hashlib.md5()

        # 将字符串编码为字节，然后更新哈希对象
        # 注意：必须对字符串进行编码，因为哈希函数处理的是字节数据
        md5_hash.update(pdf_path.encode('utf-8'))

        # 返回计算出的 MD5 哈希值（32位十六进制字符串）
        return md5_hash.hexdigest()





    def __clean_text(self,content):
        """清理文本，移除特殊字符和多余空格"""
        import re
        content = re.sub(r'[^\x20-\x7E\u4e00-\u9fa5]+', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
