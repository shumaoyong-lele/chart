def main():
    print("===========欢迎使用统计图制作系统===========")

    while True:
        print("\n===========主菜单===========")
        print("[0] 制作统计图")
        print("[1] 设置")
        print("[2] 数据库管理")
        print("[3] 退出")
        types = input("请选择: ").strip()

        if types == '0' or types == "制作统计图":
            print("正在加载必要的文件...")
            try:
                from made_chart import made_chart
                print("文件加载完成！")
                made_chart()
            except ImportError as e:
                print(f"加载文件时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '1' or types == "设置":
            print("正在加载必要的文件...")
            try:
                from settings import settings
                print("文件加载完成！")
                settings()
            except ImportError as e:
                print(f"加载文件时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '2' or types == "数据库管理":
            print("正在加载必要的文件...")
            try:
                import settings.database as db_module
                db_module.database()
            except ImportError as e:
                print(f"加载文件时出错：{e}")
                print("请检查是否存在对应的文件。")
        elif types == '3' or types == "退出":
            print("感谢使用！")
            return
        else:
            print("输入错误，请重新选择！")

if __name__ == "__main__":
    main()