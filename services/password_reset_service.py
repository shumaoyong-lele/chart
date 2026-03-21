#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from database.models import UserData
from config_manager import generate_reset_token
from sqlalchemy import text


class PasswordResetService:
    def __init__(self):
        self.db = DatabaseManager()
        self.token_expiry_hours = 1
        self.min_password_length = 8
        self.max_password_length = 72
        self.rate_limit_per_user = 1
        self.rate_limit_window = 300
        self.rate_limit_per_ip = 10
        self.rate_limit_ip_window = 3600

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _is_rate_limited(self, username: str, ip_address: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.rate_limit_window)

        result = self.db.session.execute(
            text(f"SELECT COUNT(*) FROM password_reset_attempts "
                 f"WHERE (user_id = (SELECT id FROM users WHERE username = '{username}') OR ip_address = '{ip_address}') "
                 f"AND created_at > '{window_start.isoformat()}'")
        )
        count = result.scalar()

        return count >= self.rate_limit_per_user

    def _log_attempt(self, username: str, ip_address: str, success: bool):
        try:
            user = self.db.session.query(UserData).filter_by(username=username).first()
            user_id = user.id if user else None

            self.db.session.execute(
                text(f"INSERT INTO password_reset_attempts (user_id, ip_address, created_at, success) "
                     f"VALUES (:user_id, :ip_address, :created_at, :success)"),
                {
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'created_at': datetime.now().isoformat(),
                    'success': success
                }
            )
            self.db.session.commit()
        except Exception as e:
            print(f"记录重置尝试失败: {e}")
            self.db.session.rollback()

    def _cleanup_expired_tokens(self):
        try:
            now = datetime.now().isoformat()
            self.db.session.execute(
                text("DELETE FROM password_reset_tokens WHERE expires_at < :now OR used_at IS NOT NULL"),
                {'now': now}
            )
            self.db.session.commit()
        except Exception as e:
            print(f"清理过期令牌失败: {e}")
            self.db.session.rollback()

    def request_password_reset(self, username: str, ip_address: str) -> Dict:
        try:
            self._cleanup_expired_tokens()

            if self._is_rate_limited(username, ip_address):
                return {
                    'success': False,
                    'error': '请求过于频繁，请稍后再试'
                }

            user = self.db.session.query(self.db.UserData).filter_by(username=username, is_active=True).first()

            if not user:
                self._log_attempt(username, ip_address, False)
                return {
                    'success': False,
                    'error': '用户不存在'
                }

            token = generate_reset_token()
            token_hash = self._hash_token(token)
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)

            self.db.session.execute(
                text("INSERT INTO password_reset_tokens (user_id, token, token_hash, created_at, expires_at, ip_address) "
                     "VALUES (:user_id, :token, :token_hash, :created_at, :expires_at, :ip_address)"),
                {
                    'user_id': user.id,
                    'token': token,
                    'token_hash': token_hash,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expires_at.isoformat(),
                    'ip_address': ip_address
                }
            )
            self.db.session.commit()

            self._log_attempt(username, ip_address, True)

            return {
                'success': True,
                'token': token,
                'user_id': user.id,
                'username': user.username,
                'expires_at': expires_at.isoformat()
            }

        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'请求处理失败: {str(e)}'
            }

    def validate_token(self, token: str) -> Dict:
        try:
            token_hash = self._hash_token(token)

            result = self.db.session.execute(
                text("SELECT t.*, u.username, u.is_active "
                     "FROM password_reset_tokens t "
                     "JOIN users u ON t.user_id = u.id "
                     "WHERE t.token_hash = :token_hash"),
                {'token_hash': token_hash}
            )
            token_data = result.fetchone()

            if not token_data:
                return {
                    'success': False,
                    'error': '重置链接无效'
                }

            if token_data.used_at:
                return {
                    'success': False,
                    'error': '此重置链接已使用'
                }

            if datetime.fromisoformat(str(token_data.expires_at)) < datetime.now():
                return {
                    'success': False,
                    'error': '重置链接已过期'
                }

            if not token_data.is_active:
                return {
                    'success': False,
                    'error': '用户账户已被禁用'
                }

            return {
                'success': True,
                'valid': True,
                'user_id': token_data.user_id,
                'username': token_data.username
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'令牌验证失败: {str(e)}'
            }

    def reset_password(self, token: str, new_password: str) -> Dict:
        try:
            validation = self.validate_token(token)
            if not validation['success']:
                return validation

            if not self._validate_password_strength(new_password):
                return {
                    'success': False,
                    'error': '密码强度不足'
                }

            user_id = validation['user_id']

            try:
                new_password_hash = self.db._hash_password(new_password)
            except ValueError as e:
                return {
                    'success': False,
                    'error': str(e)
                }

            self.db.session.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE id = :user_id"),
                {
                    'password_hash': new_password_hash,
                    'user_id': user_id
                }
            )

            self.db.session.execute(
                text("UPDATE password_reset_tokens SET used_at = :used_at WHERE token_hash = :token_hash"),
                {
                    'used_at': datetime.now().isoformat(),
                    'token_hash': self._hash_token(token)
                }
            )

            self.db.session.commit()

            self.db._cache.clear()

            return {
                'success': True,
                'message': '密码重置成功'
            }

        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'密码重置失败: {str(e)}'
            }

    def _validate_password_strength(self, password: str) -> bool:
        if len(password) < self.min_password_length:
            return False
        if len(password) > self.max_password_length:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False

        return True

    def get_password_requirements(self) -> Dict:
        return {
            'min_length': self.min_password_length,
            'max_length': self.max_password_length,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digit': True,
            'require_special': True
        }

    def check_password_strength(self, password: str) -> Dict:
        checks = {
            'min_length': len(password) >= self.min_password_length,
            'max_length': len(password) <= self.max_password_length,
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }

        strength_score = sum(checks.values())
        if strength_score <= 3:
            strength_level = 'weak'
        elif strength_score <= 5:
            strength_level = 'medium'
        else:
            strength_level = 'strong'

        return {
            'checks': checks,
            'score': strength_score,
            'level': strength_level,
            'is_valid': all([
                checks['min_length'],
                checks['max_length'],
                checks['has_uppercase'],
                checks['has_lowercase'],
                checks['has_digit'],
                checks['has_special']
            ])
        }


password_reset_service = PasswordResetService()


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 密码重置服务测试")
    print("=" * 60)

    service = PasswordResetService()

    print("\n[测试1] 密码强度检查")
    print("-" * 60)
    test_passwords = [
        ("弱密码", "123456"),
        ("中等密码", "Password1"),
        ("强密码", "P@ssw0rd123!")
    ]

    for name, password in test_passwords:
        result = service.check_password_strength(password)
        status = "✅" if result['is_valid'] else "❌"
        print(f"{status} {name} ({password}): {result['level']} (得分: {result['score']}/6)")

    print("\n[测试2] 密码要求")
    print("-" * 60)
    requirements = service.get_password_requirements()
    print(f"最小长度: {requirements['min_length']}")
    print(f"最大长度: {requirements['max_length']}")
    print(f"需要大写字母: {requirements['require_uppercase']}")
    print(f"需要小写字母: {requirements['require_lowercase']}")
    print(f"需要数字: {requirements['require_digit']}")
    print(f"需要特殊字符: {requirements['require_special']}")

    print("\n[测试3] 创建测试令牌")
    print("-" * 60)
    result = service.request_password_reset('test_user', '127.0.0.1')
    if result['success']:
        print(f"✅ 请求成功")
        print(f"Token: {result['token'][:20]}...")
        print(f"过期时间: {result['expires_at']}")

        print("\n[测试4] 验证令牌")
        print("-" * 60)
        validation = service.validate_token(result['token'])
        if validation['success']:
            print(f"✅ 令牌有效")
            print(f"用户ID: {validation['user_id']}")
            print(f"用户名: {validation['username']}")
        else:
            print(f"❌ 令牌无效: {validation['error']}")
    else:
        print(f"❌ 请求失败: {result['error']}")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
