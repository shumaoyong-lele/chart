print("正在导入必要的库...")
try:
    import matplotlib.pyplot as plt
    import squarify
except ImportError as e:
    print(f"导入库时出错：{e}")
    print("请检查是否安装了matplotlib和squarify库。")
    exit()

def treemap_chart(labels, sizes, title):
    plt.figure(figsize=(10, 6))
    squarify.plot(sizes=sizes, label=labels, alpha=0.7)
    plt.title(title)
    plt.axis('off')
    plt.show()