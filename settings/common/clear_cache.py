print("正在清理缓存...")
import os
import shutil

# 检查缓存目录是否存在
if os.path.exists("__pycache__"):
    # 递归删除缓存目录及其内容
    shutil.rmtree("__pycache__")
    print("缓存清理完成！")
else:
    print("缓存目录(1)不存在，无需清理。")

# 检查缓存目录是否存在
if os.path.exists("chart/__pycache__"):
    # 递归删除缓存目录及其内容
    shutil.rmtree("chart/__pycache__")
    print("缓存清理完成！")
else:
    print("缓存目录(2)不存在，无需清理。")

input("输入任意键返回...")

print("正在加载必要的文件...")
try:
    from settings import set
    print("文件加载完成！")
except ImportError as e:
    print(f"加载文件时出错：{e}")
    print("请检查是否存在对应的文件。")
    exit()
