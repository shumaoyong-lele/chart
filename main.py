# 统计图制作系统主程序
# 功能：提供用户界面，根据用户选择调用不同类型的图表生成函数

print("===========欢迎使用统计图制作系统===========")

types = input("请选择([0]制作统计图,[1]设置,[2]退出:")

if types == '0' or types == "制作统计图":
    print("正在加载必要的文件...")
    try:
        from made_chart import made_chart
        print("文件加载完成！")
        made_chart()  # 调用函数
    except ImportError as e:
        print(f"加载文件时出错：{e}")
        print("请检查是否存在对应的文件。")
        exit()
elif types == '1' or types == "设置":
    print("正在加载必要的文件...")
    try:
        from settings import settings
        print("文件加载完成！")
        settings()  # 调用函数
    except ImportError as e:
        print(f"加载文件时出错：{e}")
        print("请检查是否存在对应的文件。")
        exit()
elif types == '2' or types == "退出":
    print("感谢使用！")
    exit()
else:
    print("输入错误，请重新选择！")