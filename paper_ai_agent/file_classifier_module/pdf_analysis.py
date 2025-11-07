import json

from langchain_openai import OpenAI


class PDFContentAnalyzer:
    def run(self, input_queue, output_queue):
        """ "
        调用提取文本队列中的数据流,
        这个接口为数据流处理预留
        """
        # 这里从消息队列取出之前的处理结果
        ###

        # 分析
        # new_file_data_dict=self.start_analyze(previous_file_data_dict)

        # 投入到下一步的消息队列
        ###

    def analyze(self, previous_file_data_dict):
        """
        这里开始分析,现在只有文本分析,后面加OCR可以扩展
        """
        # 文本
        new_file_data_dict = self.__generate_summary_and_keywords(
            previous_file_data_dict
        )

        # OCR
        # new_file_data_dict=ocr_method()

        return new_file_data_dict

    def __generate_summary_and_keywords(self, file_data_dict):
        """
        根据文本,让llm生成信息
        """
        file_text_content = file_data_dict["file_text"]
        ai_result = self.__call_ai_model(file_text_content)

        # 使用AI结果或默认值
        file_data_dict.update(
            {
                "file_title": ai_result.get(
                    "title", file_data_dict.get("file_name", "Untitled")
                ),
                "file_summary": ai_result.get(
                    "summary", "Summary generation failed - API key not configured"
                ),
                "file_keywords": ai_result.get("keywords", []),
            }
        )
        return file_data_dict

    def __call_ai_model(self, text):
        api_key = ""

        # 如果没有API key，返回默认值
        if not api_key:
            print("️  DeepSeek API Key未配置，跳过AI分析")
            return {"title": "", "summary": "", "keywords": []}

        try:
            # 初始化OpenAI客户端
            from openai import OpenAI as OpenAIClient

            client = OpenAIClient(api_key=api_key, base_url="https://api.deepseek.com")

            """调用大模型API生成摘要和关键词"""
            # 智能提取关键章节（优先Abstract, Introduction, Method, Conclusion）
            key_text = self.__extract_key_sections(text, max_chars=10000)

            prompt = f"""
                Please give me the superior main title of the text paper, generate a refined and brief summary(150-250 words) and 5 keywords, according to the content of a paper or thesis:
                text content:
                {key_text}
    
                Return with following pattern without any other redundant description:
                {{
                    "title": "here is the title of the paper",
                    "summary": "here is the summary of the paper",
                    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
                }}
                """

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in this field of study,"
                        " with deep insights into computers and artificial intelligence. "
                        "Your way of explaining is humorous, witty, and easy to understand, "
                        "yet remains professional.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.3,
            )

            if response.choices[0].message.content is None:
                raise ValueError("Empty response from AI model")
            result_text = response.choices[0].message.content.strip()

            # 尝试解析JSON响应
            try:
                # 提取JSON部分（避免模型返回额外文本）
                import re

                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
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
            return {"title": "", "summary": "", "keywords": []}

    def __extract_key_sections(self, text, max_chars=10000):
        """智能提取论文关键章节

        优先级：Abstract > Introduction > Method/Approach > Conclusion > 其他
        """
        import re

        if len(text) <= max_chars:
            return text

        # 尝试提取各个章节
        sections = {}

        # 1. Abstract（最重要）
        abstract_match = re.search(
            r"(abstract|ABSTRACT)[\s\n]+(.*?)(?=\n\n[A-Z]|introduction|INTRODUCTION|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if abstract_match:
            sections["abstract"] = abstract_match.group(2)[:800]

        # 2. Introduction
        intro_match = re.search(
            r"(introduction|INTRODUCTION)[\s\n]+(.*?)(?=\n\n[0-9A-Z]|related work|RELATED|method|METHOD|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if intro_match:
            sections["introduction"] = intro_match.group(2)[:2000]

        # 3. Method/Approach
        method_match = re.search(
            r"(method|methodology|approach|METHODOLOGY|APPROACH)[\s\n]+(.*?)(?=\n\n[0-9A-Z]|experiment|EXPERIMENT|result|RESULT|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if method_match:
            sections["method"] = method_match.group(2)[:3000]

        # 4. Conclusion
        conclusion_match = re.search(
            r"(conclusion|CONCLUSION|summary|SUMMARY)[\s\n]+(.*?)(?=\n\n[A-Z]|reference|REFERENCE|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if conclusion_match:
            sections["conclusion"] = conclusion_match.group(2)[:1000]

        # 拼接提取的内容
        extracted = []
        for section in ["abstract", "introduction", "method", "conclusion"]:
            if section in sections:
                extracted.append(sections[section])

        result = "\n\n".join(extracted)

        # 如果提取失败或太短，使用前max_chars字符
        if len(result) < 1000:
            return text[:max_chars]

        return result[:max_chars]
