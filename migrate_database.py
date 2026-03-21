#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from sqlalchemy import text

print("=" * 70)
print("🔧 数据库迁移 - 移除salt字段")
print("=" * 70)

db = DatabaseManager()

is_sqlite = 'sqlite' in str(db.engine.url).lower()

print(f"\n检测到数据库类型: {'SQLite' if is_sqlite else 'PostgreSQL'}")

print("\n检查数据库表结构...")
try:
    if is_sqlite:
        result = db.session.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
    else:
        result = db.session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        columns = [row[0] for row in result]

    print(f"当前字段: {columns}")

    if 'salt' in columns:
        print("\n发现salt字段，准备移除...")

        try:
            if is_sqlite:
                try:
                    db.session.execute(text("ALTER TABLE users DROP COLUMN salt"))
                    db.session.commit()
                    print("✓ salt字段已成功移除")
                except Exception as e:
                    if "near \"DROP\": syntax error" in str(e):
                        print("SQLite不支持直接DROP COLUMN，创建新表...")
                        db.session.execute(text("""
                            CREATE TABLE users_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username VARCHAR(100) UNIQUE NOT NULL,
                                password_hash VARCHAR(255) NOT NULL,
                                uid VARCHAR(20) UNIQUE NOT NULL,
                                is_active BOOLEAN DEFAULT 1,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        db.session.execute(text("""
                            INSERT INTO users_new (id, username, password_hash, uid, is_active, created_at)
                            SELECT id, username, password_hash, uid, is_active, created_at FROM users
                        """))
                        db.session.execute(text("DROP TABLE users"))
                        db.session.execute(text("ALTER TABLE users_new RENAME TO users"))
                        db.session.commit()
                        print("✓ 新表结构已创建并迁移数据")
                    else:
                        raise e
            else:
                db.session.execute(text("ALTER TABLE users DROP COLUMN salt"))
                db.session.commit()
                print("✓ salt字段已成功移除")

        except Exception as e:
            print(f"✗ 移除字段失败: {e}")
            db.session.rollback()
            print("\n建议：手动执行以下SQL:")
            if is_sqlite:
                print("  CREATE TABLE users_new AS SELECT id, username, password_hash, uid, is_active, created_at FROM users;")
                print("  DROP TABLE users;")
                print("  ALTER TABLE users_new RENAME TO users;")
            else:
                print("  ALTER TABLE users DROP COLUMN salt;")
            sys.exit(1)
    else:
        print("✓ salt字段已不存在")

except Exception as e:
    print(f"✗ 检查表结构失败: {e}")
    db.session.rollback()

print("\n验证新表结构...")
try:
    if is_sqlite:
        result = db.session.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
    else:
        result = db.session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        columns = [row[0] for row in result]

    print(f"新字段: {columns}")

    if 'salt' not in columns and 'password_hash' in columns:
        print("✓ 表结构验证通过")
    else:
        print("✗ 表结构验证失败")
        if 'salt' in columns:
            print("  - salt字段仍然存在")
        if 'password_hash' not in columns:
            print("  - password_hash字段不存在")
        sys.exit(1)

except Exception as e:
    print(f"✗ 验证失败: {e}")
    sys.exit(1)

db.close_session()
print("\n" + "=" * 70)
print("✅ 数据库迁移完成！")
print("=" * 70)
