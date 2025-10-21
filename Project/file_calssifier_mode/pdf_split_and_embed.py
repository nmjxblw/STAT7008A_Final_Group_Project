import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.embeddings.dashscope import DashScopeEmbeddings
import json
import hashlib

class PDFRagWorker:
    def run(self,input_queue, output_queue):
        """
        这个接口为数据流处理预留
        """

    def set_retrival_knowledge(self,previous_file_data_dict):
        """
        在这里将原文进行语义转换和存储
        """
        # 这里基于embedding和faiss存储
        #TODO:embedding本地部署调用; Faiss的全局启动(与flask对接); 数据切分方式优化
        self.__pdf_split_and_embed(previous_file_data_dict)

        #TODO: 这里使用bm25进行词频统计和存储(需要单独完成一个接口返回词频统计)
        self.__BM25()



    def __pdf_split_and_embed(self, previous_file_data_dict):

        print(f'开始尝试对{previous_file_data_dict["file_name"]}进行切分')

        # 初始化模型,先调用qwen embedding api,如使用本地embedding模型在这里修改
        api_key = ""
        embeddings_model = DashScopeEmbeddings(
            model="text-embedding-v4",
            dashscope_api_key=api_key,

        )
        # 1. 获取文档切分
        splitted_docs=self.__content_split(previous_file_data_dict)

        # 2. 进行embedding
        # 这里需要维护一个后端全局的vector_db,要能在后端程序启动时加载,后端程序结束时保存.这里先暂时写为运行到这行代码时加载,运行结束后释放
        self.__embed(splitted_docs,embeddings_model)








    def __content_split(self,previous_file_data_dict):


        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 块大小
            chunk_overlap=200,  # 块重叠
            separators=["\n\n", "\n", ".", "!", "?", " "]  # 分隔符
            )

        doc = Document(
            page_content=previous_file_data_dict["file_text"],  # 这是已经从PDF提取并清理的文本
            metadata={
                "file_name": previous_file_data_dict["file_name"],
                "file_id": previous_file_data_dict["file_id"],
                "file_title": previous_file_data_dict["file_title"],
                "file_summary": previous_file_data_dict["file_summary"],
                "file_keywords": ", ".join(previous_file_data_dict["file_keywords"]),  # 将关键词列表转为字符串
            }
        )
        # 2. 文本分割
        splitted_doc = text_splitter.split_documents([doc])
        return splitted_doc

    def __embed(self,docs,embeddings_model):
        #项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        #faiss文件保存目录
        save_embed_folder =os.path.join(project_root, "DB", "embedding")
        vector_db = FAISS.load_local(save_embed_folder, embeddings_model, allow_dangerous_deserialization=True)
        if vector_db is None:
            vector_db = FAISS.from_documents(docs, embeddings_model)
        else:
            vector_db.add_documents(docs)
        vector_db.save_local(save_embed_folder)


    def __BM25(self):
        print("还没实现bm25处理逻辑")

