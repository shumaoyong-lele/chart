"""
柱状图生成模块
功能：根据输入数据生成柱状图
参数：
- xlabel: x轴标签
- ylabel: y轴标签
- xdata: x轴数据列表 
- ydata: y轴数据列表
- title: 图表标题
"""

# 导入必要的库
print("正在导入必要的库...")
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    print("库导入完成！")
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib库。")
    exit()

def bar_chart(xlabel, ylabel, xdata, ydata, title):
    """生成柱状图的主函数"""
    # 数据验证
    if len(xdata) != len(ydata):
        print(f"错误: x轴数据长度({len(xdata)})与y轴数据长度({len(ydata)})不一致")
        exit()
    try:
        ydata = [float(y) for y in ydata]  # 确保y轴数据是数值
    except ValueError as e:
        print(f"y轴数据包含非数值内容: {e}")
        exit()
    print("正在使用模拟数据演示...")
    try:
        rcParams["font.sans-serif"] = ["CascadiaMono", "HarmonyOS Sans SC"]
        rcParams["font.size"] = 12  # 设置默认字体大小
    except Exception as e:
        try:
            rcParams["font.sans-serif"] = ["arial","msyh"]
        except Exception as e:
            print(f"字体设置错误: {e}")
            exit()
    rcParams["axes.unicode_minus"] = False
    
    plt.figure(figsize=(10,5))
    plt.bar(xdata, ydata, color='blue', alpha=0.7)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()