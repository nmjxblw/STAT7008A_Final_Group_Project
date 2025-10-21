import json

from langchain_openai import OpenAI


class PDFContentAnalyser:
    def run(self,input_queue, output_queue):
        """"
        调用提取文本队列中的数据流,
        这个接口为数据流处理预留
        """
        #这里从消息队列取出之前的处理结果
        ###

        #分析
        #new_file_data_dict=self.start_analyze(previous_file_data_dict)

        #投入到下一步的消息队列
        ###



    def analyze(self,previous_file_data_dict):
        """
        这里开始分析,现在只有文本分析,后面加OCR可以扩展
        """
        #文本
        new_file_data_dict=self.__generate_summary_and_keywords(previous_file_data_dict)

        #OCR
        # new_file_data_dict=ocr_method()

        return new_file_data_dict
    def __generate_summary_and_keywords(self, file_data_dict):
        """
        根据文本,让llm生成信息
        """
        file_text_content=file_data_dict["file_text"]
        ai_result=self.__call_ai_model(file_text_content)
        file_data_dict.update(
            {
                "file_title": ai_result["title"],
                "file_summary": ai_result["summary"],
                "file_keywords": ai_result["keywords"],
            }
        )
        return file_data_dict


    def __call_ai_model(self,text):
        api_key = ""
        # 初始化OpenAI客户端
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        # 创建简单数据库文件

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
                    result = {"title": "", "summary": result_text, "keywords": []}
            except:
                # 如果JSON解析失败，使用原始文本作为摘要
                result = {"title": "", "summary": result_text, "keywords": []}

            return result

        except Exception as e:
            print(f"调用AI API时出错: {e}")
            return {"summary": "failed when analyzing", "keywords": []}

