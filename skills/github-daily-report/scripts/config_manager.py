#!/usr/bin/env python3
"""
配置管理模块：管理 GitHub 和 Notion 的 API Token
"""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "github-daily-report"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # 设置权限为仅用户可读写
    os.chmod(CONFIG_DIR, 0o700)


def load_config():
    """加载配置"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def get_github_token():
    """获取 GitHub Token，如果不存在则提示输入"""
    config = load_config()
    token = config.get('github_token')
    if not token:
        token = input("请输入 GitHub Personal Access Token: ").strip()
        if token:
            config['github_token'] = token
            save_config(config)
            print("✓ GitHub Token 已保存")
    return token


def get_notion_token():
    """获取 Notion Integration Token，如果不存在则提示输入"""
    config = load_config()
    token = config.get('notion_token')
    if not token:
        token = input("请输入 Notion Integration Token: ").strip()
        if token:
            config['notion_token'] = token
            save_config(config)
            print("✓ Notion Token 已保存")
    return token


def get_notion_database_id():
    """获取 Notion Database ID，如果不存在则提示输入"""
    config = load_config()
    db_id = config.get('notion_database_id')
    if not db_id:
        print("\n请确保你已经在 Notion 中：")
        print("1. 创建了一个 Integration")
        print("2. 将 Integration 连接到你的数据库")
        print("3. 数据库需要有 '日期' (Date) 和 '工作内容' (Title) 字段")
        db_id = input("\n请输入 Notion Database ID: ").strip()
        if db_id:
            config['notion_database_id'] = db_id
            save_config(config)
            print("✓ Notion Database ID 已保存")
    return db_id


def get_github_username():
    """获取 GitHub 用户名，如果不存在则提示输入"""
    config = load_config()
    username = config.get('github_username')
    if not username:
        username = input("请输入 GitHub 用户名: ").strip()
        if username:
            config['github_username'] = username
            save_config(config)
            print("✓ GitHub 用户名已保存")
    return username


def get_repositories():
    """获取要监控的仓库列表"""
    config = load_config()
    repos = config.get('repositories', [])
    if not repos:
        print("\n请输入要监控的仓库（格式: owner/repo，多个用逗号分隔）")
        print("例如: huhanwj/project1, huhanwj/project2")
        repos_input = input("仓库列表: ").strip()
        if repos_input:
            repos = [r.strip() for r in repos_input.split(',')]
            config['repositories'] = repos
            save_config(config)
            print(f"✓ 已保存 {len(repos)} 个仓库")
    return repos


def show_config():
    """显示当前配置"""
    config = load_config()
    print("\n当前配置:")
    print(f"  GitHub Token: {'已设置' if config.get('github_token') else '未设置'}")
    print(f"  GitHub 用户名: {config.get('github_username', '未设置')}")
    print(f"  Notion Token: {'已设置' if config.get('notion_token') else '未设置'}")
    print(f"  Notion Database ID: {config.get('notion_database_id', '未设置')}")
    print(f"  监控仓库: {', '.join(config.get('repositories', [])) or '未设置'}")


def reset_config():
    """重置配置"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("✓ 配置已重置")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "show":
            show_config()
        elif sys.argv[1] == "reset":
            reset_config()
        else:
            print("用法: python config_manager.py [show|reset]")
    else:
        # 交互式配置
        print("=== GitHub Daily Report 配置 ===")
        get_github_token()
        get_github_username()
        get_repositories()
        get_notion_token()
        get_notion_database_id()
        print("\n✓ 配置完成！")
