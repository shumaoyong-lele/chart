def settings():
    while True:
        print("===========设置===========")
        types = input("请选择([0]个性化,[1]通用,[2]返回:")

        if types == '0' or types == "个性化":
            print("正在加载必要的文件...")
            try:
                from settings.personal import personal
                print("文件加载完成！")
                personal()
            except ImportError as e:
                print(f"加载文件时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '1' or types == "通用":
            print("正在加载必要的文件...")
            try:
                from settings.common import common
                print("文件加载完成！")
                common()
            except ImportError as e:
                print(f"加载文件时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '2' or types == "返回":
            print("返回主菜单...")
            return
        else:
            print("输入错误，请重新选择！")
