# 统计图制作系统

本项目是一个基于 Python 的交互式统计图制作系统，支持生成折线图、柱状图、饼图和树状图。用户可通过命令行输入数据，快速生成所需的统计图表。

## 功能特性

- 支持折线图、柱状图、饼图、树状图的生成
- 交互式命令行输入，操作简单
- 自动检测数据有效性
- 支持中文标签显示

## 依赖环境

- Python 3.x
- matplotlib
- squarify（仅树状图需要）

安装依赖：
Python官方：
```sh
pip install matplotlib squarify
```
国内镜像：
```sh
清华大学镜像：
pip install matplotlib squarify -i https://pypi.tuna.tsinghua.edu.cn/simple

阿里云镜像：
pip install matplotlib squarify -i https://mirrors.aliyun.com/pypi/simple/

华为云镜像：
pip install matplotlib squarify -i https://repo.huaweicloud.com/repository/pypi/simple
```

## 使用方法

1. 运行主程序：
    ```sh
    python main.py
    ```
2. 按照提示输入图表类型、标题、标签和数据等信息。
3. 程序会自动生成并展示相应的统计图。

## 文件说明

- `main.py`：主程序，负责用户交互和调度
- `line_chart.py`：折线图生成模块
- `bar_chart.py`：柱状图生成模块
- `pie_chart.py`：饼图生成模块
- `treemap_chart.py`：树状图生成模块

## 示例

生成柱状图示例：

```
请输入图表标题：产品销量
请选择图表类型([0]折线图/[1]柱状图/[2]圆饼图/[3]树状图):1
请输入x轴标签(如:产品): 产品
请输入y轴标签(如:销量): 销量
请输入x轴数据(多个数据用空格分隔，如:产品A 产品B 产品C): 产品A 产品B 产品C
请输入y轴数据(多个数值用空格分隔，如:120 150 90): 120 150 90
```

## 注意事项

- 请确保已安装所有依赖库。
- 若遇到中文乱码，可根据提示调整字体设置。

---

如有问题欢迎反馈！