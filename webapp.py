#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计图制作系统 - Web 端 (Flask)
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import get_config
from database import DatabaseManager
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# 初始化
config = get_config()
uid = config.get('uid', 'unknown')
db = DatabaseManager()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', uid=uid)


@app.route('/api/charts', methods=['GET'])
def get_charts():
    """获取所有图表"""
    charts = db.get_all_charts(limit=20)
    return jsonify(charts)


@app.route('/api/charts/<int:chart_id>', methods=['GET'])
def get_chart(chart_id):
    """获取单个图表"""
    chart = db.get_chart_by_id(chart_id)
    if chart:
        return jsonify(chart)
    return jsonify({'error': '未找到'}), 404


@app.route('/api/charts', methods=['POST'])
def create_chart():
    """创建图表"""
    data = request.json
    
    title = data.get('title')
    chart_type = data.get('chart_type')
    xdata = data.get('xdata', [])
    ydata = data.get('ydata', [])
    labels = data.get('labels', [])
    created_by = data.get('created_by', str(uid))
    
    # 生成图表
    img_buffer = io.BytesIO()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == 'line':
        ax.plot(xdata, ydata, marker='o')
    elif chart_type == 'bar':
        ax.bar(xdata, ydata)
    elif chart_type == 'pie':
        ax.pie(ydata, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')
    
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    
    # 保存到数据库
    if chart_type == 'pie':
        chart_id = db.save_chart(title, chart_type, labels, ydata, created_by=created_by)
    else:
        chart_id = db.save_chart(title, chart_type, xdata, ydata, created_by=created_by)
    
    # 返回图片 base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return jsonify({
        'success': True,
        'chart_id': chart_id,
        'image': f'data:image/png;base64,{img_base64}'
    })


@app.route('/api/charts/<int:chart_id>', methods=['DELETE'])
def delete_chart(chart_id):
    """删除图表"""
    success = db.delete_chart(chart_id)
    return jsonify({'success': success})


if __name__ == '__main__':
    print(f"用户 ID: {uid}")
    print("启动 Web 服务: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
