print("正在导入必要的库...")
try:
    import matplotlib
    matplotlib.use('Agg')  # 使用非交互式后端
    import matplotlib.pyplot as plt
    from utils.font_utils import configure_fonts
    print("库导入完成！")
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib库。")
    exit()

def multi_line_chart(xlabel, ylabel, xdata, ydata_list, labels, title, save_path=None):
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
    plt.tight_layout()
    
    # 保存为文件
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存到: {save_path}")
    
    plt.show()
