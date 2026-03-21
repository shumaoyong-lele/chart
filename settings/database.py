def database():
    """数据库管理功能"""
    from database import db

    while True:
        print("\n========== 数据库管理 ==========")
        print("[0] 查看所有图表")
        print("[1] 查看指定图表")
        print("[2] 删除图表")
        print("[3] 返回")

        choice = input("请选择: ").strip()

        if choice == '0':
            print("\n--- 图表列表 ---")
            charts = db.get_all_charts(limit=20)

            if not charts:
                print("暂无图表数据")
            else:
                for chart in charts:
                    print(f"\n[ID: {chart['id']}]")
                    print(f"标题: {chart['title']}")
                    print(f"类型: {chart['chart_type']}")
                    print(f"创建时间: {chart['created_at']}")
                    print(f"创建者: {chart['created_by']}")

                    # 显示数据预览
                    x_labels = chart['x_labels']
                    y_data = chart['y_data']

                    if chart['chart_type'] == 'pie':
                        labels = chart['labels']
                        print(f"标签: {', '.join(labels)}")
                        print(f"数据: {', '.join(map(str, y_data))}")
                    else:
                        print(f"X轴: {', '.join(x_labels[:5])}{'...' if len(x_labels) > 5 else ''}")
                        print(f"Y轴: {', '.join(map(str, y_data[:5]))}{'...' if len(y_data) > 5 else ''}")

        elif choice == '1':
            chart_id = input("请输入图表 ID: ").strip()
            try:
                chart_id = int(chart_id)
            except ValueError:
                print("❌ 无效的 ID")
                continue

            chart = db.get_chart_by_id(chart_id)

            if chart:
                print(f"\n--- 图表详情 [ID: {chart['id']}] ---")
                print(f"标题: {chart['title']}")
                print(f"类型: {chart['chart_type']}")
                print(f"创建时间: {chart['created_at']}")
                print(f"创建者: {chart['created_by']}")

                x_labels = chart['x_labels']
                y_data = chart['y_data']

                if chart['chart_type'] == 'pie':
                    labels = chart['labels']
                    print(f"标签: {', '.join(labels)}")
                    print(f"数据: {', '.join(map(str, y_data))}")
                else:
                    print(f"\nX轴数据 ({len(x_labels)} 项):")
                    for i, (x, y) in enumerate(zip(x_labels, y_data)):
                        print(f"  {i+1}. {x}: {y}")

            else:
                print(f"❌ 未找到 ID 为 {chart_id} 的图表")

        elif choice == '2':
            chart_id = input("请输入要删除的图表 ID: ").strip()
            try:
                chart_id = int(chart_id)
            except ValueError:
                print("❌ 无效的 ID")
                continue

            db.delete_chart(chart_id)

        elif choice == '3':
            print("返回...")
            return
        else:
            print("❌ 无效选择，请重新输入")
