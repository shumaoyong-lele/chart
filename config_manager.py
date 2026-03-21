# Supabase 配置
# 此文件由程序自动生成，请勿手动修改

import json
import os
import uuid

CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(data):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_config():
    """初始化配置（首次运行时调用）"""
    print("\n" + "="*50)
    print("首次运行，需要配置 Supabase 连接信息")
    print("="*50)
    
    # 生成或获取 UID（数字）
    existing_config = load_config()
    if existing_config and 'uid' in existing_config:
        uid = existing_config['uid']
        print(f"\n已有用户 ID: {uid}")
    else:
        # 生成 6 位数字 UID
        import random
        uid = str(random.randint(100000, 999999))
        print(f"\n生成用户 ID: {uid}")
    
    # 询问 Supabase 信息
    print("\n请输入 Supabase 配置信息：")
    
    # 获取项目引用
    project_ref = input("Supabase Project Ref (如：bmtmanijtqhnuvmrehvw): ").strip()
    while not project_ref:
        project_ref = input("请输入 Project Ref: ").strip()
    
    # 获取数据库密码
    db_password = input("Supabase Database Password: ").strip()
    while not db_password:
        db_password = input("请输入 Database Password: ").strip()
    
    # 构建连接字符串
    db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
    
    # 保存配置
    config_data = {
        "uid": uid,
        "supabase": {
            "project_ref": project_ref,
            "db_url": db_url,
            "use_supabase": True
        }
    }
    
    save_config(config_data)
    
    print("\n✅ 配置已保存到 config.json")
    print(f"用户 ID: {uid}")
    
    return config_data

def get_config():
    """获取配置（如果不存在则初始化）"""
    config = load_config()
    if config is None:
        config = init_config()
    return config

# 直接运行时测试
if __name__ == "__main__":
    config = get_config()
    print("\n当前配置：")
    print(json.dumps(config, indent=2, ensure_ascii=False))
