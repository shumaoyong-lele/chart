def common():
    while True:
        print("===========通用设置===========")
        types = input("请选择([0]清理缓存,[1]返回):")

        if types == '0' or types == "清理缓存":
            print("正在加载必要的文件...")
            try:
                from settings.common.clear_cache import clear_cache
                print("文件加载完成！")
                clear_cache()
            except ImportError as e:
                print(f"清理缓存时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '1' or types == "返回":
            return
        else:
            print("输入错误！")