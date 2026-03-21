#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import get_config


class EmailService:
    def __init__(self):
        config = get_config()
        email_config = config.get('email', {}) if config else {}

        self.smtp_host = email_config.get('smtp_host', 'smtp.gmail.com')
        self.smtp_port = email_config.get('smtp_port', 587)
        self.smtp_user = email_config.get('smtp_user', '')
        self.smtp_password = email_config.get('smtp_password', '')
        self.use_tls = email_config.get('use_tls', True)
        self.from_email = email_config.get('from_email', self.smtp_user)
        self.from_name = email_config.get('from_name', '统计图制作系统')

    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)

            context = ssl.create_default_context()

            if self.use_tls:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls(context=context)
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)

            return {
                'success': True,
                'message': '邮件发送成功'
            }

        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': '邮件认证失败，请检查SMTP配置'
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                'success': False,
                'error': '收件人邮箱地址无效'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'邮件发送失败: {str(e)}'
            }

    def send_password_reset_email(self, to_email: str, reset_link: str, username: str) -> Dict:
        subject = "【统计图制作系统】密码重置请求"

        body = f"""
尊敬的用户 {username}，您好！

我们收到了您的密码重置请求。如果您没有发起此请求，请忽略此邮件。

要重置您的密码，请点击以下链接：
{reset_link}

此链接将在1小时后失效。

如果您在点击链接时遇到问题，请复制以下链接到浏览器地址栏：
{reset_link}

为了保护您的账户安全，请不要将验证码或链接分享给他人。

此致
统计图制作系统团队
        """.strip()

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 统计图制作系统</h1>
        </div>
        <div class="content">
            <h2>密码重置请求</h2>
            <p>尊敬的用户 <strong>{username}</strong>，您好！</p>
            <p>我们收到了您的密码重置请求。如果您没有发起此请求，请忽略此邮件。</p>

            <p>要重置您的密码，请点击以下按钮：</p>
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">重置密码</a>
            </p>

            <p>或者复制以下链接到浏览器地址栏：</p>
            <p style="word-break: break-all; color: #667eea;">{reset_link}</p>

            <div class="warning">
                ⚠️ <strong>安全提示：</strong><br>
                • 此链接将在1小时后失效<br>
                • 请不要将链接分享给他人<br>
                • 如果这不是您本人操作，请忽略此邮件
            </div>
        </div>
        <div class="footer">
            <p>此致<br>统计图制作系统团队</p>
            <p>© 2024 统计图制作系统. 保留所有权利.</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return self.send_email(to_email, subject, body, html_body)

    def is_configured(self) -> bool:
        return bool(self.smtp_user and self.smtp_password)


email_service = EmailService()


if __name__ == "__main__":
    print("=" * 60)
    print("📧 邮件服务配置测试")
    print("=" * 60)

    config = get_config()
    email_config = config.get('email', {}) if config else {}

    print(f"\nSMTP服务器: {email_config.get('smtp_host', '未配置')}")
    print(f"SMTP端口: {email_config.get('smtp_port', '未配置')}")
    print(f"用户名: {email_config.get('smtp_user', '未配置')}")
    print(f"使用TLS: {email_config.get('use_tls', '未配置')}")

    if email_service.is_configured():
        print("\n✅ 邮件服务已配置")
        print("\n测试邮件发送...")
        test_email = input("\n请输入测试收件人邮箱（直接回车跳过）: ").strip()
        if test_email:
            result = email_service.send_email(
                test_email,
                "测试邮件",
                "这是一封测试邮件，用于验证邮件服务配置。"
            )
            if result['success']:
                print("✅ 测试邮件发送成功！")
            else:
                print(f"❌ 测试邮件发送失败: {result['error']}")
    else:
        print("\n⚠️ 邮件服务未配置")
        print("\n请在 config.json 中添加邮件配置：")
        print("""
{
  "email": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "use_tls": true,
    "from_email": "your-email@gmail.com",
    "from_name": "统计图制作系统"
  }
}
        """)
