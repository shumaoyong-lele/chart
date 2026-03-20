print("正在导入必要的库...")
try:
    import matplotlib.pyplot as plt
    from utils.font_utils import configure_fonts
    print("库导入完成！")
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib库。")
    exit()

def multi_line_chart(xlabel, ylabel, xdata, ydata_list, labels, title):
    if not configure_fonts():
        exit()

    plt.figure(figsize=(10, 6))
    for ydata, label in zip(ydata_list, labels):
        plt.plot(xdata, ydata, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()