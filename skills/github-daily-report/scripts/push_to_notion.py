#!/usr/bin/env python3
"""
将日报推送到 Notion
"""
import requests
from datetime import datetime, timezone
from config_manager import get_notion_token, get_notion_database_id


def push_to_notion(report_content, date=None):
    """将日报推送到 Notion"""
    token = get_notion_token()
    database_id = get_notion_database_id()
    
    if not all([token, database_id]):
        print("❌ Notion 配置不完整")
        return False
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 使用今天的日期
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 准备页面内容（将报告分割成多个段落块）
    content_blocks = []
    for line in report_content.strip().split('\n'):
        if line.strip():
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
    
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "标题": {
                "title": [{"text": {"content": f"工作日报 - {date}"}}]
            },
            "日期": {
                "date": {"start": date}
            }
        },
        "children": content_blocks if content_blocks else []
    }
    
    # 如果数据库有其他字段，可以在这里添加
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        page = response.json()
        print(f"✅ 日报已推送到 Notion")
        print(f"   链接: {page.get('url', 'N/A')}")
        return True
    else:
        print(f"❌ 推送失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False


if __name__ == "__main__":
    # 测试用
    test_report = """今日工作总结：

1. 完成了项目 A 的功能开发
2. 修复了项目 B 的 bug
3. 参加了团队会议"""
    push_to_notion(test_report)
