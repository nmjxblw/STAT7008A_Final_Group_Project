if __name__ == "__main__":
    print(f"{__package__}.{__name__} 被作为主程序运行，启动 launcher 模块...")
    from launcher_module import run
    import cProfile

    cProfile.run(
        statement="run()",
        filename=f"{__package__}{__name__}_result.out",
        sort="cumulative",
    )
