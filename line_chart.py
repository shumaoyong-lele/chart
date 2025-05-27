"""
折线图生成模块
功能：根据输入数据生成折线图
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
    from matplotlib import rcParams  # 用于配置字体等参数
    print("库导入完成！")
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib库。")
    exit()

def line_chart(xlabel, ylabel, xdata, ydata, title):
    """生成折线图的主函数"""
    print("正在生成折线图...")
    
    # 设置中文字体
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
    
    # 绘制折线图
    plt.figure(figsize=(10,5))  # 设置画布大小
    plt.plot(xdata, ydata, marker="o", color="black", linewidth=2)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)  # 修正拼写错误
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()