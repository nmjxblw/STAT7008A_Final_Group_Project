import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.embeddings.dashscope import DashScopeEmbeddings
import json
import hashlib


def pdf_split_and_embed(analysed_data, save_embed_folder, save_data_folder):
    def save_to_database(filename, file_info, save_data_folder):
        """将结果保存到简单的文件数据库中"""
        # 如果数据库文件已存在，加载现有数据
        db_file = save_data_folder + "\\pdf_analysis_database.json"
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                database = json.load(f)
        else:
            database = {}
        database[filename] = {
            "file_id": file_info["file_id"],
            "file_name": filename,
            "title": file_info["title"],
            "summary": file_info["summary"],
            "keywords": file_info["keywords"],
        }

        # 保存到JSON文件
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)

    """
    
        将初步分析的结果向量化，确认成功后将embedding保存到向量库->保存原始信息和简单分析信息->转移文件夹
        
        
        
        
        
        
        """
    print(f"开始尝试对{len(analysed_data)}个文件进行切分")
    success_filename_list = []
    # 初始化模型
    embeddings_model = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key="sk-c750cbedece2432f823d3100c91bdd14",

    )

    # 1. 加载文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # 块大小
        chunk_overlap=200,  # 块重叠
        separators=["\n\n", "\n", ".", "!", "?", " "]  # 分隔符
    )

    try:
        vector_db = FAISS.load_local(save_embed_folder, embeddings_model, allow_dangerous_deserialization=True)
        print(f"loading current db {vector_db.index.ntotal} vectors")
    except:
        print("failed at loading odl vector DB, creating a new one...")
        vector_db = None

    for filename, file_info in analysed_data.items():
        doc = Document(
            page_content=file_info["text"],  # 这是已经从PDF提取并清理的文本
            metadata={
                "filename": filename,
                "file_id": file_info.get("file_id", ""),
                "title": file_info.get("title", ""),
                "summary": file_info.get("summary", ""),
                "keywords": ", ".join(file_info.get("keywords", [])),  # 将关键词列表转为字符串

            }
        )
        # 2. 文本分割
        one_split = text_splitter.split_documents([doc])

        # 3. 准备存储向量和元数据

        # 默认直接存储split后的chunk和其对应原先text级别的元数据，
        # 如果后续需要手动修改元数据（如需要对应到切分的chunk位于原始text的具体位置再使用注释掉的自定义功能）

        # 3.1 为每个split生成唯一ID（例如基于内容哈希）
        # def generate_doc_id(text, filename, chunk_index):
        #     unique_string = f"{text[:50]}_{filename}_{chunk_index}"  # 取文本前50字符、来源、页码组合
        #     return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

        # metadata_store = {}
        # documents_for_vector_db = []
        #
        # for i, doc in enumerate(all_splits):
        #     # 生成chunk的唯一ID
        #     doc_id = generate_doc_id(doc.page_content, doc.metadata.get('filename', ''), i)
        #
        #     # 在元数据中记录偏移量信息
        #     # 假设doc.metadata中已包含source和page（PDFLoader会自动提供）
        #     # 构建新的元数据
        #     custom_metadata = {
        #         "doc_id": doc_id,
        #         "filename": doc.metadata.get('filename', 'unknown'),
        #         "file_id": doc.metadata.get('file_id', ''),
        #         "title": doc.metadata.get('title', ''),
        #         "summary": doc.metadata.get("summary", ""),
        #         "keywords": doc.metadata.get("keywords", []),  # 将关键词列表转为字符串
        #         "content_preview": doc.page_content[:100] + "..."
        #     }
        #
        #     # 更新文档的元数据
        #     doc.metadata.update(custom_metadata)
        #
        #     # 保存到元数据账本
        #     metadata_store[doc_id] = custom_metadata
        #     documents_for_vector_db.append(doc)

        # 4. 生成嵌入向量并存入向量库,并且将分析信息存入common库

        try:
            if vector_db is None:
                vector_db = FAISS.from_documents(one_split, embeddings_model)
            else:
                vector_db.add_documents(one_split)
            save_to_database(filename, file_info, save_data_folder)
            success_filename_list.append(filename)
        except Exception as e:
            print(f"error:{e}")
            print(f"current file:{filename} embed failed,will not store by db(common and vector), nor move to 'Classified' folder)")
    # 5. 保存到文件
    # 5.1 保存向量库
    VECTOR_DB_PATH = save_embed_folder
    if vector_db:
        vector_db.save_local(VECTOR_DB_PATH)

    # 如后续需要单独查看元数据再启用
    # # 5.2 保存元数据存储（账本）
    # METADATA_STORE_PATH = "metadata_store.json"
    # with open(METADATA_STORE_PATH, 'w', encoding='utf-8') as f:
    #     json.dump(metadata_store, f, ensure_ascii=False, indent=2)
    #

    print("Finish Knowledge Base Updating!")
    print(f"Save at {VECTOR_DB_PATH}")
    # print(f"元数据账本已保存至：{METADATA_STORE_PATH}")
    return success_filename_list
