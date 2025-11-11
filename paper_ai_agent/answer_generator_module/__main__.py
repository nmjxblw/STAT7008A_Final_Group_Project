from .semantic_service import SemanticService

def main():
    """演示程序"""
    # 初始化语义服务
    service = SemanticService()

    # 测试查询列表
    user_queries = [
        "Find me documents about RAG-based LLM question answering system design.",
        "What is the difference between RAG and standard LLM QA? Please explain based on documents.",
        "Show me the company policy for 2025.",
        "Explain the Transformer architecture.",
    ]

    # 执行测试
    for q in user_queries:
        print("\n==============================")
        print(f"User query: {q}")

        # 1) 设置用户需求
        service.set_demand(q)

        # 2) 获取服务响应
        resp = service.get_LLM_reply()

        # 3) 输出结果
        if resp.get("type") == "file_query":
            print("→ Detected intent: FILE_QUERY")
            print("→ Top matched documents:")
            for item in resp.get("results", []):
                print(f"  - {item['title']} (relevance={item['relevance_percent']})")
        else:
            print("→ Detected intent: QA")
            print("→ Answer:")
            print(resp.get("reply", ""))

if __name__ == "__main__":
    main()