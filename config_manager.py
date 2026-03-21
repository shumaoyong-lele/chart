import json
import os
import uuid
import secrets
import re

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_valid_project_ref(ref):
    pattern = r'^[a-z]{20,}$'
    return bool(re.match(pattern, ref))

def is_valid_db_password(password):
    return len(password) >= 6

def generate_uid():
    return str(secrets.randbelow(900000) + 100000)

def generate_reset_token():
    return secrets.token_urlsafe(32)

def print_header(title):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_success(msg):
    print(f"\u2705 {msg}")

def print_error(msg):
    print(f"\u274c {msg}")

def print_info(msg):
    print(f"\u2139\ufe0f {msg}")

def verify_connection(db_url):
    from sqlalchemy import create_engine
    try:
        engine = create_engine(db_url, connect_timeout=5)
        conn = engine.connect()
        conn.close()
        return True
    except Exception as e:
        print_error(f"连接失败: {e}")
        return False

def init_config():
    print_header("首次运行配置")

    existing_config = load_config()
    uid = generate_uid()
    if existing_config and 'uid' in existing_config:
        uid = existing_config['uid']
        print_info(f"已有用户 ID: {uid}")
    else:
        print_info(f"生成新用户 ID: {uid}")

    print_header("Supabase 配置")

    project_ref = ""
    while not project_ref:
        temp = input("\nSupabase Project Ref (如：bmtmanijtqhnuvmrehvw): ").strip()
        if is_valid_project_ref(temp):
            project_ref = temp
        else:
            print_error("Project Ref 格式不正确，应为20位以上小写字母")

    db_password = ""
    while not db_password:
        temp = input("Supabase Database Password: ").strip()
        if is_valid_db_password(temp):
            db_password = temp
        else:
            print_error("密码长度至少6位")

    db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    print_info("正在验证数据库连接...")
    if verify_connection(db_url):
        print_success("数据库连接成功")
    else:
        print_error("数据库连接失败，请检查配置")
        retry = input("是否重试? (y/n): ").strip().lower()
        if retry == 'y':
            return init_config()
        return None

    config_data = {
        "uid": uid,
        "supabase": {
            "project_ref": project_ref,
            "db_url": db_url,
            "use_supabase": True
        }
    }

    save_config(config_data)
    print_success(f"配置已保存到 {CONFIG_FILE}")
    print_info(f"用户 ID: {uid}")

    return config_data

def change_uid():
    print_header("修改用户 ID")
    current_config = load_config()
    if not current_config:
        print_error("配置文件不存在")
        return None

    old_uid = current_config.get('uid', '未知')
    new_uid = ""

    temp = input(f"请输入新用户 ID (6位数字，当前: {old_uid}): ").strip()
    if temp:
        if temp.isdigit() and len(temp) == 6:
            new_uid = temp
        else:
            print_error("用户 ID 必须为6位数字")
            return None
    else:
        new_uid = generate_uid()
        print_info(f"已生成新用户 ID: {new_uid}")

    current_config['uid'] = new_uid
    save_config(current_config)
    print_success(f"用户 ID 已更改: {old_uid} -> {new_uid}")
    return current_config

def reconfigure_supabase():
    print_header("重新配置 Supabase")
    current_config = load_config()
    if not current_config:
        print_error("配置文件不存在")
        return None

    project_ref = ""
    while not project_ref:
        temp = input("\nSupabase Project Ref: ").strip()
        if is_valid_project_ref(temp):
            project_ref = temp
        else:
            print_error("Project Ref 格式不正确")

    db_password = ""
    while not db_password:
        temp = input("Supabase Database Password: ").strip()
        if is_valid_db_password(temp):
            db_password = temp
        else:
            print_error("密码长度至少6位")

    db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    print_info("正在验证数据库连接...")
    if verify_connection(db_url):
        print_success("数据库连接成功")
    else:
        print_error("数据库连接失败")
        return None

    current_config['supabase'] = {
        "project_ref": project_ref,
        "db_url": db_url,
        "use_supabase": True
    }

    save_config(current_config)
    print_success("Supabase 配置已更新")
    return current_config

def show_config():
    config = load_config()
    if config:
        print("\n当前配置：")
        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        print_error("配置文件不存在")

def reset_config():
    print_header("重置配置")
    confirm = input("确定要删除所有配置吗? (yes/no): ").strip().lower()
    if confirm == 'yes':
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            print_success("配置已重置")
        else:
            print_error("配置文件不存在")

def config_menu():
    while True:
        print_header("配置管理")
        print("1. 显示当前配置")
        print("2. 修改用户 ID")
        print("3. 重新配置 Supabase")
        print("4. 重置配置")
        print("5. 退出")

        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            change_uid()
        elif choice == '3':
            reconfigure_supabase()
        elif choice == '4':
            reset_config()
        elif choice == '5':
            break
        else:
            print_error("无效选择")

def get_config():
    config = load_config()
    if config is None:
        config = init_config()
    return config

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--menu':
            config_menu()
        elif sys.argv[1] == '--show':
            show_config()
        else:
            print("用法: python config_manager.py [--menu|--show]")
    else:
        config = get_config()
        print("\n当前配置：")
        print(json.dumps(config, indent=2, ensure_ascii=False))