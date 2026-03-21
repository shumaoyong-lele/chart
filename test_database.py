#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db


def test_database():
    """测试数据库功能"""

    print("=" * 50)
    print("测试数据库功能")
    print("=" * 50)

    # 测试 1: 保存图表
    print("\n[测试 1] 保存图表...")
    chart_id = db.save_chart(
        title="测试图表",
        chart_type="bar",
        xdata=["产品A", "产品B", "产品C"],
        ydata=[120, 150, 90],
        created_by="test_user"
    )

    if chart_id:
        print(f"✅ 图表保存成功，ID: {chart_id}")
    else:
        print("❌ 图表保存失败")
        return

    # 测试 2: 查询所有图表
    print("\n[测试 2] 查询所有图表...")
    charts = db.get_all_charts(limit=10)

    if charts:
        print(f"✅ 查询成功，共 {len(charts)} 条记录")
        for chart in charts:
            print(f"  - ID: {chart['id']}, 标题: {chart['title']}, 类型: {chart['chart_type']}")
    else:
        print("❌ 查询失败或无数据")

    # 测试 3: 查询指定图表
    print("\n[测试 3] 查询指定图表...")
    if charts:
        chart_id = charts[0]['id']
        chart = db.get_chart_by_id(chart_id)

        if chart:
            print(f"✅ 查询成功")
            print(f"  - ID: {chart['id']}")
            print(f"  - 标题: {chart['title']}")
            print(f"  - 类型: {chart['chart_type']}")
            print(f"  - X轴: {chart['x_labels']}")
            print(f"  - Y轴: {chart['y_data']}")
            print(f"  - 创建者: {chart['created_by']}")
        else:
            print("❌ 查询失败")
    else:
        print("❌ 无数据可查询")

    # 测试 4: 删除图表
    print("\n[测试 4] 删除图表...")
    if charts:
        chart_id = charts[0]['id']
        success = db.delete_chart(chart_id)

        if success:
            print(f"✅ 删除成功")
        else:
            print("❌ 删除失败")
    else:
        print("❌ 无数据可删除")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_database()
