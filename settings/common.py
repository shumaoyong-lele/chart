def common():
    print("===========通用设置===========")
    types = input("请选择([0]清理缓存,[1]返回:)")

    if types == '0' or types == "清理缓存":
        print("正在清理缓存...")
        try:
            from settings.common.clear_cache import clear_cache
            clear_cache()
            print("缓存清理完成！")
        except ImportError as e:
            print(f"清理缓存时出错：{e}")
            print("请检查是否存在对应的文件。")
            exit()
    elif types == '1' or types == "返回":
        print("正在加载必要的文件...")
        try:
            from settings import settings
            print("文件加载完成！")
            settings()
        except ImportError as e:
            print(f"加载文件时出错：{e}")
            print("请检查是否存在对应的文件。")
            exit()
    else:
        print("输入错误！")
        exit()