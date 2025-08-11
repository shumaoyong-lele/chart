print("正在导入必要的库...")
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    print("库导入完成！")
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib库。")
    exit()

def multi_line_chart(xlabel, ylabel, xdata, ydata_list, labels, title):
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
    
    plt.figure(figsize=(10, 6))
    for ydata, label in zip(ydata_list, labels):
        plt.plot(xdata, ydata, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()