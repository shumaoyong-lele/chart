#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import get_config
from database import DatabaseManager
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.font_utils import configure_fonts
import io
import base64

app = Flask(__name__)

def get_secret_key():
    if os.environ.get('SECRET_KEY'):
        return os.environ.get('SECRET_KEY')

    secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.secret_key')
    if os.path.exists(secret_file):
        with open(secret_file, 'rb') as f:
            key = f.read()

        if isinstance(key, bytes) and len(key) < 32:
            import secrets
            key = secrets.token_hex(32).encode()
            with open(secret_file, 'wb') as f:
                f.write(key)
            os.chmod(secret_file, 0o600)

        if isinstance(key, bytes):
            return key
        return key.encode() if isinstance(key, str) else key
    else:
        import secrets
        key = secrets.token_hex(32)
        with open(secret_file, 'w') as f:
            f.write(key)
        os.chmod(secret_file, 0o600)
        return key

app.secret_key = get_secret_key()

config = get_config()
uid = config.get('uid', 'unknown') if config else 'unknown'
db = DatabaseManager()


def error_handler(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'uid' not in session:
            return jsonify({'error': '需要登录'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return render_template('index.html', uid=uid)


@app.route('/api/auth/register', methods=['POST'])
@error_handler
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or len(username) < 3:
        return jsonify({'success': False, 'error': '用户名至少需要3个字符'}), 400

    if not password or len(password) < 6:
        return jsonify({'success': False, 'error': '密码至少需要6个字符'}), 400

    result = db.register_user(username, password)

    if result['success']:
        session['uid'] = result['uid']
        session['username'] = result['username']
        return jsonify({
            'success': True,
            'uid': result['uid'],
            'username': result['username']
        })
    else:
        return jsonify(result), 400


@app.route('/api/auth/login', methods=['POST'])
@error_handler
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'error': '请输入用户名和密码'}), 400

    result = db.authenticate_user(username, password)

    if result['success']:
        session['uid'] = result['uid']
        session['username'] = result['username']
        return jsonify({
            'success': True,
            'uid': result['uid'],
            'username': result['username']
        })
    else:
        return jsonify(result), 401


@app.route('/api/auth/logout', methods=['POST'])
@error_handler
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '已成功退出登录'})


@app.route('/api/auth/me', methods=['GET'])
@error_handler
def get_current_user():
    if 'uid' in session:
        user = db.get_user_by_uid(session['uid'])
        if user:
            return jsonify({
                'success': True,
                'logged_in': True,
                'uid': session['uid'],
                'username': session.get('username')
            })
    return jsonify({'logged_in': False})


@app.route('/api/auth/change-password', methods=['POST'])
@error_handler
@login_required
def change_password():
    data = request.json
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': '新密码至少需要6个字符'}), 400

    result = db.change_password(session['uid'], old_password, new_password)

    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/charts', methods=['GET'])
@error_handler
def get_charts():
    if 'uid' not in session:
        return jsonify([])

    limit = int(request.args.get('limit', 20))
    created_by = session['uid']

    charts = db.get_all_charts(limit=limit, created_by=created_by)

    for chart in charts:
        if chart.get('image_data'):
            chart['image'] = f"data:image/png;base64,{chart['image_data']}"
            del chart['image_data']

    return jsonify(charts)


@app.route('/api/charts/<int:chart_id>', methods=['GET'])
@error_handler
def get_chart(chart_id):
    chart = db.get_chart_by_id(chart_id)
    if not chart:
        return jsonify({'error': '图表不存在'}), 404

    if 'uid' in session:
        if chart['created_by'] != session['uid']:
            return jsonify({'error': '无权访问此图表'}), 403

    if chart['image_data']:
        chart['image'] = f"data:image/png;base64,{chart['image_data']}"
        del chart['image_data']

    return jsonify(chart)


@app.route('/api/charts', methods=['POST'])
@error_handler
@login_required
def create_chart():
    data = request.json

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': '图表标题不能为空'}), 400

    chart_type = data.get('chart_type', 'bar')
    xdata = data.get('xdata', [])
    ydata = data.get('ydata', [])
    labels = data.get('labels', [])
    created_by = session.get('uid', str(uid))

    configure_fonts()
    img_buffer = io.BytesIO()

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == 'line':
        ax.plot(xdata, ydata, marker='o')
    elif chart_type == 'bar':
        ax.bar(xdata, ydata, color='steelblue', alpha=0.8)
    elif chart_type == 'pie':
        ax.pie(ydata, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
    elif chart_type == 'multi_line':
        for yd, label in zip(ydata, labels):
            ax.plot(xdata, yd, marker='o', label=label)
        ax.legend()

    ax.set_title(title, fontsize=14)
    ax.set_xlabel(data.get('xlabel', ''), fontsize=12)
    ax.set_ylabel(data.get('ylabel', ''), fontsize=12)
    plt.tight_layout()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

    if chart_type == 'pie':
        chart_id = db.save_chart(title, chart_type, labels, ydata, created_by=created_by, image_data=img_base64)
    else:
        chart_id = db.save_chart(title, chart_type, xdata, ydata, labels if chart_type == 'multi_line' else None, created_by=created_by, image_data=img_base64)

    return jsonify({
        'success': True,
        'chart_id': chart_id,
        'image': f'data:image/png;base64,{img_base64}'
    })


@app.route('/api/charts/<int:chart_id>', methods=['PUT'])
@error_handler
@login_required
def update_chart(chart_id):
    data = request.json
    title = data.get('title')
    xdata = data.get('xdata')
    ydata = data.get('ydata')

    success = db.update_chart(chart_id, title=title, xdata=xdata, ydata=ydata)
    return jsonify({'success': success})


@app.route('/api/charts/<int:chart_id>', methods=['DELETE'])
@error_handler
@login_required
def delete_chart(chart_id):
    success = db.delete_chart(chart_id)
    return jsonify({'success': success})


@app.route('/api/charts/search', methods=['GET'])
@error_handler
def search_charts():
    keyword = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    charts = db.search_charts(keyword, limit=limit)
    return jsonify(charts)


@app.route('/api/stats', methods=['GET'])
@error_handler
def get_stats():
    created_by = request.args.get('created_by')

    if 'uid' in session and not created_by:
        created_by = session['uid']

    total = db.get_chart_count(created_by=created_by)
    return jsonify({'total': total, 'uid': session.get('uid', uid)})


@app.route('/api/config', methods=['GET'])
@error_handler
def get_user_config():
    return jsonify({
        'uid': uid,
        'use_supabase': config.get('supabase', {}).get('use_supabase', False) if config else False
    })


@app.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    return render_template('forgot_password.html')


@app.route('/reset-password', methods=['GET'])
def reset_password_page():
    token = request.args.get('token', '')
    if not token:
        return render_template('error.html', message='重置链接无效'), 400
    return render_template('reset_password.html', token=token)


@app.route('/api/auth/forgot-password', methods=['POST'])
@error_handler
def request_password_reset():
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'success': False, 'error': '请输入用户名'}), 400

    ip_address = request.remote_addr or '127.0.0.1'

    try:
        from services.password_reset_service import password_reset_service
        result = password_reset_service.request_password_reset(username, ip_address)

        if result['success']:
            from services.email_service import email_service
            if email_service.is_configured():
                reset_link = f"http://localhost:5000/reset-password?token={result['token']}"
                email_result = email_service.send_password_reset_email(
                    username,
                    reset_link,
                    username
                )
                if not email_result['success']:
                    return jsonify({
                        'success': False,
                        'error': '邮件发送失败，请稍后重试'
                    }), 500
                return jsonify({
                    'success': True,
                    'message': '密码重置链接已发送到您的邮箱'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'密码重置令牌: {result["token"]} (仅用于测试)',
                    'token': result['token'],
                    'reset_link': f'http://localhost:5000/reset-password?token={result["token"]}'
                })
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/reset-password', methods=['POST'])
@error_handler
def reset_password():
    data = request.json
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not token:
        return jsonify({'success': False, 'error': '重置令牌不能为空'}), 400

    if not new_password:
        return jsonify({'success': False, 'error': '请输入新密码'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'error': '两次输入的密码不一致'}), 400

    try:
        from services.password_reset_service import password_reset_service

        strength_check = password_reset_service.check_password_strength(new_password)
        if not strength_check['is_valid']:
            errors = []
            if not strength_check['checks']['min_length']:
                errors.append('密码长度至少8个字符')
            if not strength_check['checks']['has_uppercase']:
                errors.append('密码需要包含大写字母')
            if not strength_check['checks']['has_lowercase']:
                errors.append('密码需要包含小写字母')
            if not strength_check['checks']['has_digit']:
                errors.append('密码需要包含数字')
            if not strength_check['checks']['has_special']:
                errors.append('密码需要包含特殊字符')
            return jsonify({
                'success': False,
                'error': '; '.join(errors)
            }), 400

        result = password_reset_service.reset_password(token, new_password)

        if result['success']:
            return jsonify({
                'success': True,
                'message': '密码重置成功，请使用新密码登录'
            })
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print(f"用户 ID: {uid}")
    print("启动 Web 服务: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)