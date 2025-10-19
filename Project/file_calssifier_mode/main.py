import os

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import OpenAIEmbeddings

from Project.file_calssifier_mode.pdf_analysis import pdf_analysis
from Project.file_calssifier_mode.pdf_split_and_embed import pdf_split_and_embed
from Project.file_calssifier_mode.utils import move_files


def start_file_classify_task():
    # 获取当前运行路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上级运行路径（项目根目录）
    project_root = os.path.dirname(script_dir)

    unclassified_folder = os.path.join(project_root, "Resource", "Unclassified")
    classified_folder = os.path.join(project_root, "Resource", "Classified")
    save_data_folder = os.path.join(project_root, "DB", "common")
    save_embed_folder = os.path.join(project_root, "DB", "embedding")

    # 将爬取的文件提取文本并简单分析
    analysed_data = pdf_analysis(unclassified_folder,save_data_folder)
    # 将提取的文本嵌入向量
    success_filename_list=pdf_split_and_embed(analysed_data, save_embed_folder,save_data_folder)
    # 将处理完的pdf移动到classified文件夹
    move_files(unclassified_folder, classified_folder,success_filename_list)
    print("finish pipeline pdf handling")




if __name__ == "__main__":
    start_file_classify_task()


    # 下面为调试流程，测试向量库可否正确检索，完成pdf的分析和切分直接调上面的函数
    # 重新从磁盘加载向量库
    from langchain_community.vectorstores import FAISS

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    save_embed_folder = os.path.join(project_root, "DB", "embedding")
    embeddings_model = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key="sk-c750cbedece2432f823d3100c91bdd14",

    )
    loaded_vector_db = FAISS.load_local(save_embed_folder, embeddings_model, allow_dangerous_deserialization=True)

    # 进行相似性搜索测试
    query="what is attention?"
    docs = loaded_vector_db.similarity_search(query, k=2)
    print("start test")
    print("query={query}")
    for i in range(len(docs)):

        print(f"found no.{i+1} related content(in vector view):", docs[i].page_content)
        print("relevant metadata:", docs[i].metadata)  # 这里将显示您保存的元数据
