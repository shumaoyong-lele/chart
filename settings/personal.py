def personal():
    while True:
        types = input("请选择([0]字体,[1]颜色,[2]返回):")

        if types == '0' or types == "字体":
            print("字体设置功能待实现。")
        elif types == '1' or types == "颜色":
            print("颜色设置功能待实现。")
        elif types == '2' or types == "返回":
            return
        else:
            print("输入错误！")