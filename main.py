# 统计图制作系统主程序
# 功能：提供用户界面，根据用户选择调用不同类型的图表生成函数

print("===========欢迎使用统计图制作系统===========")

# 加载必要的图表模块
print("正在加载必要的文件...")
try:
    from line_chart import line_chart  # 折线图模块
    from bar_chart import bar_chart    # 柱状图模块
    from pie_chart import pie_chart    # 饼图模块
    print("文件加载完成！")
except ImportError as e:
    print(f"加载文件时出错：{e}")
    print("请检查是否存在对应的文件。")
    exit()

# 获取用户输入
title = input("请输入图表标题：")
types = input("请选择图表类型([0]折线图/[1]柱状图/[2]圆饼图:")

# 折线图处理逻辑
if types == "折线图" or types == "0":
    xlabel = input("请输入x轴标签(如:星期): ")
    ylabel = input("请输入y轴标签(如:温度): ")
    print("请输入x轴数据(多个数据用空格分隔，如:周一 周二 周三):")
    xdata = input().split()
    print("请输入y轴数据(多个数值用空格分隔，如:22 24 21):")
    ydata = list(map(float, input().split()))
    if len(xdata) != len(ydata):
        print(f"错误: x轴数据数量({len(xdata)})与y轴数据数量({len(ydata)})不匹配")
        exit()
    print("正在制作折线图...")
    line_chart(xlabel, ylabel, xdata, ydata, title)

# 柱状图处理逻辑
elif types == "柱状图" or types == "1":
    xlabel = input("请输入x轴标签(如:产品): ")
    ylabel = input("请输入y轴标签(如:销量): ")
    print("请输入x轴数据(多个数据用空格分隔，如:产品A 产品B 产品C):")
    xdata = input().split()
    print("请输入y轴数据(多个数值用空格分隔，如:120 150 90):")
    ydata = list(map(float, input().split()))
    if len(xdata) != len(ydata):
        print(f"错误: x轴数据数量({len(xdata)})与y轴数据数量({len(ydata)})不匹配")
        exit()
    print("正在制作柱状图...")
    bar_chart(xlabel, ylabel, xdata, ydata, title)

# 饼图处理逻辑
elif types == "圆饼图" or types == "2":
    print("请输入各部分标签(用空格分隔，如:苹果 香蕉 橙子):")
    labels = input().split()
    print("请输入各部分大小(用空格分隔，如:30 45 25):")
    sizes = list(map(float, input().split()))
    if len(labels) != len(sizes):
        print(f"错误: 标签数量({len(labels)})与数据数量({len(sizes)})不匹配")
        exit()
    if sum(sizes) <= 0:
        print("错误: 各部分大小总和必须大于0")
        exit()
    print("正在制作圆饼图...")
    pie_chart(labels, sizes, title)