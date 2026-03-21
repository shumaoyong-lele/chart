"""
饼图生成模块
功能：根据输入数据生成饼图
参数：
- labels: 各部分标签列表
- sizes: 各部分大小列表
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

def pie_chart(labels, sizes, title, save_path=None):
    """生成饼图的主函数"""
    if not configure_fonts():
        exit()

    plt.figure(figsize=(8,8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(title, fontsize=14)
    plt.axis('equal')
    plt.tight_layout()
    
    # 保存为文件
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存到: {save_path}")
    
    plt.show()
