def made_chart():
    print("正在加载必要的文件...")
    try:
        from chart.line_chart import line_chart
        from chart.bar_chart import bar_chart
        from chart.pie_chart import pie_chart
        from chart.multi_line_chart import multi_line_chart
        print("文件加载完成！")
    except ImportError as e:
        print(f"加载文件时出错：{e}")
        print("请检查是否存在对应的文件。")
        return

    title = input("请输入图表标题：")
    types = input("请选择图表类型([0]折线图/[1]柱状图/[2]圆饼图/[3]复式折线图):")

    if types == "折线图" or types == "0":
        xlabel = input("请输入x轴标签(如:星期): ")
        ylabel = input("请输入y轴标签(如:温度): ")
        print("请输入x轴数据(多个数据用空格分隔，如:周一 周二 周三):")
        xdata = input().split()
        print("请输入y轴数据(多个数值用空格分隔，如:22 24 21):")
        ydata = list(map(float, input().split()))
        if len(xdata) != len(ydata):
            print(f"错误: x轴数据数量({len(xdata)})与y轴数据数量({len(ydata)})不匹配")
            return
        print("正在制作折线图...")
        line_chart(xlabel, ylabel, xdata, ydata, title)

    elif types == "柱状图" or types == "1":
        xlabel = input("请输入x轴标签(如:产品): ")
        ylabel = input("请输入y轴标签(如:销量): ")
        print("请输入x轴数据(多个数据用空格分隔，如:产品A 产品B 产品C):")
        xdata = input().split()
        print("请输入y轴数据(多个数值用空格分隔，如:120 150 90):")
        ydata = list(map(float, input().split()))
        if len(xdata) != len(ydata):
            print(f"错误: x轴数据数量({len(xdata)})与y轴数据数量({len(ydata)})不匹配")
            return
        print("正在制作柱状图...")
        bar_chart(xlabel, ylabel, xdata, ydata, title)

    elif types == "圆饼图" or types == "2":
        print("请输入各部分标签(用空格分隔，如:苹果 香蕉 橙子):")
        labels = input().split()
        print("请输入各部分大小(用空格分隔，如:30 45 25):")
        sizes = list(map(float, input().split()))
        if len(labels) != len(sizes):
            print(f"错误: 标签数量({len(labels)})与数据数量({len(sizes)})不匹配")
            return
        if sum(sizes) <= 0:
            print("错误: 各部分大小总和必须大于0")
            return
        print("正在制作圆饼图...")
        pie_chart(labels, sizes, title)

    elif types == "复式折线图" or types == "3":
        xlabel = input("请输入x轴标签(如:月份): ")
        ylabel = input("请输入y轴标签(如:销售额): ")
        print("请输入x轴数据(多个数据用空格分隔，如:1月 2月 3月):")
        xdata = input().split()

        ydata_list = []
        labels = []
        while True:
            print("请输入折线标签(输入空行结束，如:产品A):")
            label = input().strip()
            if not label:
                break
            labels.append(label)
            print(f"请输入{label}的y轴数据(多个数值用空格分隔，如:100 200 150):")
            ydata = list(map(float, input().split()))
            if len(xdata) != len(ydata):
                print(f"错误: x轴数据数量({len(xdata)})与y轴数据数量({len(ydata)})不匹配")
                return
            ydata_list.append(ydata)

        if len(ydata_list) < 2:
            print("错误: 复式折线图需要至少2组数据")
            return

        print("正在制作复式折线图...")
        multi_line_chart(xlabel, ylabel, xdata, ydata_list, labels, title)
    else:
        print("输入错误，请重新选择！")