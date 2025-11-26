if __name__ == "__main__":
    print(f"{__package__}.{__name__} 被作为主程序运行，启动 launcher 模块...")

    profile_filename = f"app_runtime_result.stats"
    from file_classifier_module import test_retrieval
    import cProfile

    cProfile.run(
        statement="test_retrieval()",
        filename=profile_filename,
        sort="cumulative",
    )
    import pstats

    text_filename = "profile_readable.txt"
    with open(text_filename, "w", encoding="utf-8") as f:
        ps = pstats.Stats(profile_filename, stream=f)
        ps.strip_dirs().sort_stats("cumulative").print_stats()
