#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import io
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.font_utils import configure_fonts

from database import DatabaseManager
from config_manager import get_config


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_success(msg):
    print(f"✅ {msg}")


def print_error(msg):
    print(f"❌ {msg}")


def print_info(msg):
    print(f"ℹ️  {msg}")


def check_auth(db, session_uid):
    if not session_uid:
        print_error("请先登录")
        return None
    user = db.get_user_by_uid(session_uid)
    if not user:
        print_error("用户不存在")
        return None
    return user


def register(db):
    print_header("用户注册")

    username = input("用户名: ").strip()
    if not username:
        print_error("用户名不能为空")
        return False

    if len(username) < 3:
        print_error("用户名至少需要3个字符")
        return False

    password = input("密码: ").strip()
    if not password:
        print_error("密码不能为空")
        return False

    if len(password) < 6:
        print_error("密码至少需要6个字符")
        return False

    confirm = input("确认密码: ").strip()
    if password != confirm:
        print_error("两次输入的密码不一致")
        return False

    result = db.register_user(username, password)
    if result['success']:
        print_success(f"注册成功！")
        print_info(f"用户名: {result['username']}")
        print_info(f"UID: {result['uid']}")
        return result['uid']
    else:
        print_error(f"注册失败: {result['error']}")
        return None


def login(db):
    print_header("用户登录")

    username = input("用户名: ").strip()
    if not username:
        print_error("用户名不能为空")
        return None

    password = input("密码: ").strip()
    if not password:
        print_error("密码不能为空")
        return None

    result = db.authenticate_user(username, password)
    if result['success']:
        print_success(f"登录成功！")
        print_info(f"用户名: {result['username']}")
        print_info(f"UID: {result['uid']}")
        return result['uid']
    else:
        print_error(f"登录失败: {result['error']}")
        return None


def create_chart(db, uid):
    print_header("创建图表")

    if not check_auth(db, uid):
        return None

    title = input("图表标题: ").strip()
    if not title:
        print_error("标题不能为空")
        return None

    print("\n图表类型:")
    print("1. 折线图 (line)")
    print("2. 柱状图 (bar)")
    print("3. 饼图 (pie)")
    chart_type_choice = input("请选择 (1-3): ").strip()

    chart_types = {'1': 'line', '2': 'bar', '3': 'pie'}
    chart_type = chart_types.get(chart_type_choice, 'bar')

    xlabel = input("X轴标签 (可选): ").strip()
    ylabel = input("Y轴标签 (可选): ").strip()

    print("\n请输入数据 (每行一个，输入空行结束):")
    xdata = []
    ydata = []

    if chart_type == 'pie':
        print("输入标签和数据，格式: 标签,数值")
        while True:
            line = input().strip()
            if not line:
                break
            if ',' in line:
                parts = line.split(',', 1)
                xdata.append(parts[0].strip())
                try:
                    ydata.append(float(parts[1].strip()))
                except ValueError:
                    print_error("数值格式错误")
                    continue
            else:
                print_info("饼图需要格式: 标签,数值")
    else:
        print("输入X轴数据和Y轴数据，格式: X值,Y值")
        while True:
            line = input().strip()
            if not line:
                break
            if ',' in line:
                parts = line.split(',', 1)
                xdata.append(parts[0].strip())
                try:
                    ydata.append(float(parts[1].strip()))
                except ValueError:
                    print_error("数值格式错误")
                    continue
            else:
                print_info("格式: X值,Y值")

    if not xdata or not ydata:
        print_error("数据不能为空")
        return None

    configure_fonts()
    img_buffer = io.BytesIO()

    fig, ax = plt.subplots(figsize=(10, 6))

    try:
        if chart_type == 'line':
            ax.plot(xdata, ydata, marker='o')
        elif chart_type == 'bar':
            ax.bar(xdata, ydata, color='steelblue', alpha=0.8)
        elif chart_type == 'pie':
            ax.pie(ydata, labels=xdata, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')

        ax.set_title(title, fontsize=14)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)

        plt.tight_layout()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        plt.close()

        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        if chart_type == 'pie':
            chart_id = db.save_chart(title, chart_type, xdata, ydata, created_by=uid, image_data=img_base64)
        else:
            chart_id = db.save_chart(title, chart_type, xdata, ydata, created_by=uid, image_data=img_base64)

        print_success(f"图表创建成功！")
        print_info(f"图表ID: {chart_id}")

        save_choice = input("\n是否保存图片到本地? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = input("文件名 (默认: chart.png): ").strip() or "chart.png"
            with open(filename, 'wb') as f:
                f.write(img_buffer.getvalue())
            print_success(f"图片已保存到: {filename}")

        return chart_id

    except Exception as e:
        print_error(f"创建图表失败: {e}")
        plt.close()
        return None


def list_charts(db, uid):
    print_header("我的图表")

    if not check_auth(db, uid):
        return

    charts = db.get_all_charts(limit=50, created_by=uid)

    if not charts:
        print_info("暂无图表")
        return

    print(f"\n共 {len(charts)} 个图表:\n")
    print(f"{'ID':<5} {'标题':<30} {'类型':<10} {'创建时间':<20}")
    print("-" * 70)

    for chart in charts:
        created_at = chart['created_at'][:19] if chart['created_at'] else '未知'
        title = chart['title'][:28] + '..' if len(chart['title']) > 30 else chart['title']
        print(f"{chart['id']:<5} {title:<30} {chart['chart_type']:<10} {created_at:<20}")


def view_chart(db, uid):
    print_header("查看图表")

    if not check_auth(db, uid):
        return

    list_charts(db, uid)

    chart_id = input("\n请输入图表ID (或按回车返回): ").strip()
    if not chart_id:
        return

    try:
        chart_id = int(chart_id)
    except ValueError:
        print_error("无效的图表ID")
        return

    chart = db.get_chart_by_id(chart_id)

    if not chart:
        print_error("图表不存在")
        return

    if chart['created_by'] != uid:
        print_error("无权访问此图表")
        return

    print(f"\n标题: {chart['title']}")
    print(f"类型: {chart['chart_type']}")
    print(f"创建时间: {chart['created_at']}")

    if chart.get('image_data'):
        save_choice = input("\n是否查看/保存图片? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = input("文件名 (默认: chart_preview.png): ").strip() or "chart_preview.png"

            try:
                img_data = base64.b64decode(chart['image_data'])
                with open(filename, 'wb') as f:
                    f.write(img_data)
                print_success(f"图片已保存到: {filename}")
            except Exception as e:
                print_error(f"保存图片失败: {e}")
    else:
        print_info("此图表暂无预览图片")


def change_password(db, uid):
    print_header("修改密码")

    if not check_auth(db, uid):
        return False

    old_password = input("原密码: ").strip()
    if not old_password:
        print_error("原密码不能为空")
        return False

    new_password = input("新密码: ").strip()
    if not new_password:
        print_error("新密码不能为空")
        return False

    if len(new_password) < 6:
        print_error("新密码至少需要6个字符")
        return False

    confirm = input("确认新密码: ").strip()
    if new_password != confirm:
        print_error("两次输入的密码不一致")
        return False

    result = db.change_password(uid, old_password, new_password)
    if result['success']:
        print_success("密码修改成功")
        return True
    else:
        print_error(f"密码修改失败: {result['error']}")
        return False


def main_menu():
    print_header("统计图制作系统 - 命令行版")
    config = get_config()
    print(f"当前用户ID: {config.get('uid', 'unknown')}")
    print("\n[0] 制作图表")
    print("[1] 我的图表")
    print("[2] 查看图表")
    print("[3] 用户注册")
    print("[4] 用户登录")
    print("[5] 修改密码")
    print("[6] 退出")
    print("\n请选择操作 (0-6): ", end="")


def main():
    config = get_config()
    db = DatabaseManager()
    session_uid = config.get('uid', 'unknown')

    while True:
        main_menu()
        choice = input().strip()

        if choice == '0':
            create_chart(db, session_uid)
        elif choice == '1':
            list_charts(db, session_uid)
        elif choice == '2':
            view_chart(db, session_uid)
        elif choice == '3':
            result = register(db)
            if result:
                session_uid = result
        elif choice == '4':
            result = login(db)
            if result:
                session_uid = result
        elif choice == '5':
            change_password(db, session_uid)
        elif choice == '6':
            print("\n感谢使用！")
            break
        else:
            print_error("无效选择")

        input("\n按回车继续...")


if __name__ == "__main__":
    main()
