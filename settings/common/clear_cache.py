import os
import shutil

def clear_cache():
    print("正在清理缓存...")

    cache_dirs = ["__pycache__", "chart/__pycache__", "settings/__pycache__", "settings/common/__pycache__"]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"已清理缓存目录: {cache_dir}")

    print("缓存清理完成！")
    input("输入任意键返回...")