import os
import pickle
from collections import Counter

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import DashScopeEmbeddings
import json
import hashlib


class PDFRagWorker:
    def __init__(self, use_local_embedding=False):
        """初始化PDFRagWorker
        
        Args:
            use_local_embedding: 是否使用本地embedding模型
                - True: 使用本地HuggingFace模型（需下载，但免费）
                - False: 使用DashScope API（需API key，但更快）
        """
        self.use_local_embedding = use_local_embedding
        self.detected_language = None  # 检测到的语言（在处理文档时自动检测）
    
    def run(self, input_queue, output_queue):
        """
        这个接口为数据流处理预留
        """

    def set_retrival_knowledge(self, previous_file_data_dict):
        """
        在这里将原文进行语义转换和存储
        """
        # 自动检测文档语言
        self.detected_language = self.__detect_language(previous_file_data_dict.get("file_text", ""))
        print(f" 检测到文档语言: {self.detected_language}")
        
        # 这里基于embedding和faiss存储
        self.__pdf_split_and_embed(previous_file_data_dict)

        # 使用bm25进行词频统计和存储
        self.__build_bm25_index(previous_file_data_dict)
    
    def __detect_language(self, text, sample_size=2000):
        """检测文本语言（中文/英文）
        
        Args:
            text: 待检测文本
            sample_size: 采样大小
            
        Returns:
            'zh' 或 'en'
        """
        if not text:
            return 'en'  # 默认英文
        
        # 采样前sample_size字符
        sample = text[:sample_size]
        
        # 统计中文字符数量
        chinese_chars = len([c for c in sample if '\u4e00' <= c <= '\u9fff'])
        total_chars = len(sample)
        
        # 如果中文字符占比>20%，认为是中文文档
        if total_chars > 0 and (chinese_chars / total_chars) > 0.2:
            return 'zh'
        else:
            return 'en'
    
    def __get_embedding_model(self):
        """获取embedding模型（根据语言自动选择合适模型）
        
        Returns:
            embeddings_model: LangChain的embedding模型对象
        """
        if self.use_local_embedding:
            # 使用本地HuggingFace模型
            print("使用本地Embedding模型")
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                import os.path
                
                # 根据检测到的语言选择模型
                if self.detected_language == 'zh':
                    model_name = "BAAI/bge-small-zh-v1.5"  # 中文模型，约400MB
                    print(f"  选择中文模型: {model_name}")
                else:
                    model_name = "sentence-transformers/all-MiniLM-L6-v2"  # 英文模型，约90MB
                    print(f"  选择英文模型: {model_name}")
                
                # 检查模型是否已下载
                cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
                model_dir_name = f"models--{model_name.replace('/', '--')}"
                model_path = os.path.join(cache_dir, model_dir_name)
                
                if os.path.exists(model_path):
                    print(f"  本地模型已缓存: {model_path}")
                else:
                    print(f"  本地模型未找到，开始自动下载...")
                    print(f"  模型大小: {'~400MB' if self.detected_language == 'zh' else '~90MB'}")
                    print(f"  下载位置: {cache_dir}")
                
                # 加载模型（如果不存在会自动下载）
                embeddings_model = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},  # 使用CPU，如有GPU可改为'cuda'
                    encode_kwargs={'normalize_embeddings': True}
                )
                print(f"本地模型加载成功: {model_name}")
                return embeddings_model
                
            except Exception as e:
                print(f"本地模型加载失败: {e}")
                print("首次使用需要下载模型，请确保网络连接")
                print("或安装: pip install sentence-transformers")
                print("降级使用API模式")
                # 降级到API模式
                self.use_local_embedding = False
        
        # 使用API（默认或降级）
        print("使用DashScope API进行Embedding")
        api_key = os.getenv("DASHSCOPE_API_KEY", "")
        
        if not api_key:
            print("警告: DASHSCOPE_API_KEY 未设置")
            print("请设置环境变量或在代码中配置API key")
        
        embeddings_model = DashScopeEmbeddings(
            model="text-embedding-v4",
            dashscope_api_key=api_key,
        )
        return embeddings_model

    def __pdf_split_and_embed(self, previous_file_data_dict):

        print(f'开始尝试对{previous_file_data_dict["file_name"]}进行切分')

        # 获取embedding模型（支持本地和API两种方式）
        embeddings_model = self.__get_embedding_model()
        
        # 1. 获取文档切分
        splitted_docs = self.__content_split(previous_file_data_dict)

        # 2. 进行embedding
        # 这里需要维护一个后端全局的vector_db,要能在后端程序启动时加载,后端程序结束时保存.这里先暂时写为运行到这行代码时加载,运行结束后释放
        self.__embed(splitted_docs, embeddings_model)

    def __content_split(self, previous_file_data_dict):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 块大小
            chunk_overlap=200,  # 块重叠
            separators=["\n\n", "\n", ".", "!", "?", " "],  # 分隔符
        )

        doc = Document(
            page_content=previous_file_data_dict[
                "file_text"
            ],  # 这是已经从PDF提取并清理的文本
            metadata={
                "file_name": previous_file_data_dict["file_name"],
                "file_id": previous_file_data_dict["file_id"],
                "file_title": previous_file_data_dict["file_title"],
                "file_summary": previous_file_data_dict["file_summary"],
                "file_keywords": ", ".join(
                    previous_file_data_dict["file_keywords"]
                ),  # 将关键词列表转为字符串
            },
        )
        # 2. 文本分割
        splitted_doc = text_splitter.split_documents([doc])
        return splitted_doc

    def __embed(self, docs, embeddings_model):
        # 项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # faiss文件保存目录
        save_embed_folder = os.path.join(project_root, "DB", "embedding")
        os.makedirs(save_embed_folder, exist_ok=True)
        
        # 检查是否存在index文件
        index_file = os.path.join(save_embed_folder, "index.faiss")
        
        if os.path.exists(index_file):
            # 加载现有索引
            vector_db = FAISS.load_local(
                save_embed_folder, embeddings_model, allow_dangerous_deserialization=True
            )
            # 添加新文档
            vector_db.add_documents(docs)
        else:
            # 首次创建索引
            vector_db = FAISS.from_documents(docs, embeddings_model)
        
        # 保存索引
        vector_db.save_local(save_embed_folder)

    def __build_bm25_index(self, previous_file_data_dict):
        """构建BM25索引并进行词频统计
        
        将文档分词后存储到BM25语料库，并统计高频词。
        
        Args:
            previous_file_data_dict: 包含文件信息的字典
                - file_id: 文件唯一标识
                - file_text: 文件文本内容
                - file_name: 文件名
                - file_keywords: 关键词列表
                
        Returns:
            None (结果保存到文件系统)
            
        Storage:
            - DB/bm25/corpus.pkl: BM25语料库（包含所有文档的分词结果）
            - DB/bm25/term_freq.json: 词频统计结果
        """
        try:
            print(f'开始对{previous_file_data_dict["file_name"]}构建BM25索引')
            
            # 1. 文本分词
            tokens = self.__tokenize_text(previous_file_data_dict["file_text"])
            
            if not tokens:
                print("警告: 分词结果为空，跳过BM25索引构建")
                return
            
            # 2. 词频统计
            term_frequency = self.__calculate_term_frequency(tokens)
            
            # 3. 加载或创建语料库（存储在DB/BM25目录下）
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bm25_folder = os.path.join(project_root, "DB", "BM25")
            os.makedirs(bm25_folder, exist_ok=True)
            
            corpus_path = os.path.join(bm25_folder, "bm25_corpus.pkl")
            
            # 加载现有语料库
            if os.path.exists(corpus_path):
                with open(corpus_path, 'rb') as f:
                    corpus = pickle.load(f)
            else:
                corpus = []
            
            # 4. 添加新文档到语料库
            doc_entry = {
                'file_id': previous_file_data_dict['file_id'],
                'file_name': previous_file_data_dict['file_name'],
                'tokens': tokens,  # 分词结果
                'term_frequency': term_frequency,  # 词频统计
                'metadata': {
                    'file_title': previous_file_data_dict.get('file_title', ''),
                    'file_summary': previous_file_data_dict.get('file_summary', ''),
                    'file_keywords': previous_file_data_dict.get('file_keywords', [])
                }
            }
            
            # 检查是否已存在（避免重复）
            existing_ids = [doc['file_id'] for doc in corpus]
            if doc_entry['file_id'] in existing_ids:
                # 更新已存在的文档
                for i, doc in enumerate(corpus):
                    if doc['file_id'] == doc_entry['file_id']:
                        corpus[i] = doc_entry
                        print(f"更新现有文档: {doc_entry['file_name']}")
                        break
            else:
                # 添加新文档
                corpus.append(doc_entry)
                print(f"添加新文档到BM25语料库: {doc_entry['file_name']}")
            
            # 5. 保存语料库
            with open(corpus_path, 'wb') as f:
                pickle.dump(corpus, f)
            
            # 6. 保存词频统计到JSON（便于查看）
            term_freq_path = os.path.join(bm25_folder, "term_freq.json")
            
            # 加载现有词频统计
            if os.path.exists(term_freq_path):
                with open(term_freq_path, 'r', encoding='utf-8') as f:
                    all_term_freq = json.load(f)
            else:
                all_term_freq = {}
            
            # 更新词频统计
            all_term_freq[previous_file_data_dict['file_id']] = {
                'file_name': previous_file_data_dict['file_name'],
                'top_terms': term_frequency[:50],  # 保存前50个高频词
                'total_tokens': len(tokens),
                'unique_tokens': len(set(tokens))
            }
            
            # 保存
            with open(term_freq_path, 'w', encoding='utf-8') as f:
                json.dump(all_term_freq, f, ensure_ascii=False, indent=2)
            
            print(f"BM25索引构建完成，当前语料库文档数: {len(corpus)}")
            print(f"文档词数: {len(tokens)}, 独特词数: {len(set(tokens))}")
            print(f"Top 10 高频词: {[term for term, _ in term_frequency[:10]]}")
            
        except Exception as e:
            print(f"BM25索引构建失败: {e}")
            import traceback
            traceback.print_exc()
    
    def __get_stopwords(self, language='en'):
        """获取停用词表
        
        Args:
            language: 'zh' 或 'en'
            
        Returns:
            set: 停用词集合
        """
        if language == 'zh':
            # 中文停用词表
            stopwords = {
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
                '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
                '看', '好', '自己', '这', '那', '里', '来', '他', '她', '它', '们', '为',
                '与', '及', '对', '把', '被', '从', '以', '向', '用', '于', '将', '让',
                '给', '而', '则', '或', '且', '但', '却', '因', '所', '因为', '所以',
                '如果', '虽然', '然而', '因此', '并且', '还是', '或者', '不是', '这个',
                '那个', '什么', '怎么', '为什么', '哪里', '谁', '多少', '几', '些', '每',
                '比', '更', '最', '非常', '特别', '已', '已经', '正在', '曾', '曾经'
            }
        else:
            # 英文停用词表（包含连词、代词、介词、be动词等）
            stopwords = {
                # 冠词
                'a', 'an', 'the',
                # be动词
                'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
                # 助动词
                'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might',
                'can', 'could', 'must', 'ought', 'have', 'has', 'had',
                # 代词
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'theirs',
                'my', 'mine', 'your', 'yours', 'his', 'her', 'hers', 'its', 'our', 'ours',
                'this', 'that', 'these', 'those', 'who', 'whom', 'whose', 'which', 'what',
                'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
                # 介词
                'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
                'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further',
                'then', 'once', 'of',
                # 连词
                'and', 'but', 'or', 'nor', 'so', 'yet', 'as', 'if', 'when', 'where',
                'while', 'because', 'although', 'though', 'since', 'unless', 'until',
                # 其他常见词
                'not', 'no', 'yes', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
                'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very',
                'just', 'now', 'here', 'there', 'how', 'why',
            }
        
        return stopwords
    
    def __tokenize_text(self, text):
        """对文本进行分词（根据语言选择分词工具）
        
        中文使用jieba分词，英文使用空格分词+标点处理。
        自动过滤停用词。
        
        Args:
            text: 待分词的文本
            
        Returns:
            list: 分词后的词语列表（已过滤停用词）
        """
        try:
            import re
            
            if not text:
                return []
            
            # 获取停用词表
            stopwords = self.__get_stopwords(self.detected_language)
            
            # 根据语言选择分词方法
            if self.detected_language == 'zh':
                # 中文：使用jieba分词
                try:
                    import jieba
                    tokens = jieba.lcut(text)
                except ImportError:
                    print("警告: jieba未安装，中文分词效果将受影响")
                    tokens = text.split()
            else:
                # 英文：使用正则分词（按单词边界分割）
                # 保留字母和数字组成的单词
                tokens = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            
            # 过滤：去除停用词、单字符、纯数字、纯标点
            filtered_tokens = []
            for token in tokens:
                token = token.strip().lower()
                
                # 基本长度过滤
                if len(token) < 2:
                    continue
                
                # 停用词过滤
                if token in stopwords:
                    continue
                
                # 过滤纯数字
                if token.isdigit():
                    continue
                
                # 中文特殊标点过滤
                if all(c in '，。！？、；：""''【】（）《》' for c in token):
                    continue
                
                filtered_tokens.append(token)
            
            return filtered_tokens
            
        except Exception as e:
            print(f"分词失败: {e}")
            # 降级方案：简单空格分词
            return [word.strip().lower() for word in text.split() if len(word.strip()) > 1]
    
    def __calculate_term_frequency(self, tokens):
        """计算词频统计
        
        Args:
            tokens: 分词列表
            
        Returns:
            list: [(词语, 频次), ...] 按频次降序排列
        """
        if not tokens:
            return []
        
        # 使用Counter统计词频
        term_counts = Counter(tokens)
        
        # 按频次降序排序
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_terms
