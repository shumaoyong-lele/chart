"""
饼图生成模块
功能：根据输入数据生成饼图
参数：
- labels: 各部分标签列表
- sizes: 各部分大小列表
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

def pie_chart(labels, sizes, title):
    """生成饼图的主函数"""
    
    # 设置中文字体
    try:
        rcParams["font.sans-serif"] = ["CascadiaMono", "HarmonyOS Sans SC"]
        rcParams["font.size"] = 12
    except Exception as e:
        try:
            rcParamsrcParams["font.sans-serif"] = ["arial","msyh"]
        except Exception as e:
            print(f"字体设置错误: {e}")
            exit()
    rcParams["axes.unicode_minus"] = False
    
    # 绘制饼图
    plt.figure(figsize=(8,8))  # 正方形画布
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(title, fontsize=14)
    plt.axis('equal')  # 确保饼图是圆形
    plt.tight_layout()
    plt.show()