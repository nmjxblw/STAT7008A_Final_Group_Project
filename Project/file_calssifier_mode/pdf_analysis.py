import os
import json
import PyPDF2
from openai import OpenAI
import hashlib

from Project.file_calssifier_mode.utils import get_pdf_text


def pdf_analysis(unclassified_folder,save_data_folder):
    """
    处理文件夹中的PDF文件，提取文本并调用大模型生成摘要和关键词，返回结果

    参数:
    unclassified_folder: 包含PDF文件的文件夹路径

    返回:
    dict: 以文件名为主键，包含摘要和关键词的字典
    返回字段：
            "file_id": file_id,
            "file_name": filename,
            "title": ai_result["title"],
            "summary": ai_result["summary"],
            "text":clean_text_content,
            "keywords": ai_result["keywords"]

    """

    api_key="sk-d5e5dd8a995b415d992f46ed82eb9ee2"
    # 初始化OpenAI客户端
    client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")
    # 创建简单数据库文件



    def call_ai_model(text):
        try:
            """调用大模型API生成摘要和关键词"""
            prompt = f"""
                Please give me the superior main title of the text paper, generate a refined and brief summary(150-250 words) and 5 keywords, according to the content of a paper or thesis:
                text content:
                {text}

                Return with following pattern without any other redundant description:
                {{
                    "title": "here is the title of the paper",
                    "summary": "here is the summary of the paper",
                    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
                }}
                """

            response = client.chat.completions.create(
                model="deepseek-chat",  # 可根据需要更改模型
                messages=[
                    {"role": "system", "content": "You are an expert in this field of study,"
                                                  " with deep insights into computers and artificial intelligence. "
                                                  "Your way of explaining is humorous, witty, and easy to understand, "
                                                  "yet remains professional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试解析JSON响应
            try:
                # 提取JSON部分（避免模型返回额外文本）
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"title":"", "summary": result_text, "keywords": []}
            except:
                # 如果JSON解析失败，使用原始文本作为摘要
                result = {"title":"", "summary": result_text, "keywords": []}

            return result

        except Exception as e:
            print(f"调用AI API时出错: {e}")
            return {"summary": "failed when analyzing", "keywords": []}


    # 主处理逻辑
    results = {}
    # 检查文件夹是否存在
    if not os.path.exists(unclassified_folder):
        print(f"Error: folder {unclassified_folder} doesnt exist")
        return results

    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(unclassified_folder)
                 if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("Find no files at target folder")
        return results

    print(f"find {len(pdf_files)} PDF files,start handling...")
    db_file = save_data_folder + "\\pdf_analysis_database.json"
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            database = json.load(f)
    else:
        database = {}
    for i, filename in enumerate(pdf_files, 1):
        print(f"Handling {i}/{len(pdf_files)}: {filename}")

        pdf_path = os.path.join(unclassified_folder, filename)

        # 检查是否已处理过（基于文件名）
        if filename in database:
            print(f"  {filename} had been handled, continue...no analyzing and embedding")

            continue

        #获取pdf文件的文本内容
        clean_text_content=get_pdf_text(pdf_path,filename)
        if not clean_text_content:
            continue

        print(f"  cleaned text length: {len(clean_text_content)} chars")

        # 调用AI模型
        print("  Generating summary and keywords...")
        ai_result = call_ai_model(clean_text_content)

        # 保存到数据库
        file_id = hashlib.md5(filename.encode()).hexdigest()[:8]

        results[filename] = {
            "file_id": file_id,
            "file_name": filename,
            "title": ai_result["title"],
            "summary": ai_result["summary"],
            "text": clean_text_content,
            "keywords": ai_result["keywords"]
        }
        print(f"  {filename} finished handling")

    print(f"Complete! Handled {len(results)} files")
    print(f"return analyzed data...")




    return results


