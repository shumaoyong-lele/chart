"""
折线图生成模块
功能：根据输入数据生成折线图
参数：
- xlabel: x轴标签
- ylabel: y轴标签
- xdata: x轴数据列表
- ydata: y轴数据列表
- title: 图表标题
- save_path: 保存路径（可选）
"""

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

def line_chart(xlabel, ylabel, xdata, ydata, title, save_path=None):
    """生成折线图的主函数"""
    if not configure_fonts():
        exit()

    plt.figure(figsize=(10,5))
    plt.plot(xdata, ydata, marker="o", color="black", linewidth=2)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    # 保存为文件
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存到: {save_path}")
    
    plt.show()
