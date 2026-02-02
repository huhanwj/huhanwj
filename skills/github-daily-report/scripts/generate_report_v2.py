#!/usr/bin/env python3
"""
生成工作日报 v2 - 支持智能内容分析和追加更新
"""
import json
from datetime import datetime, timezone
from fetch_commits_with_diff import fetch_today_commits_with_details, generate_llm_prompt


def generate_notion_prompt(commits, mode="create"):
    """
    生成 Notion 操作的提示文本
    
    mode: 
      - "create": 创建新日报
      - "append": 追加到已有日报
    """
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if mode == "create":
        prompt = f"""请帮我生成今日工作日报并推送到 Notion。

日期：{date_str}

今日 GitHub Commits 详情：
"""
    else:
        prompt = f"""请帮我更新今日工作日报，在已有日报后面追加新的内容。

日期：{date_str}

新增的 GitHub Commits 详情：
"""
    
    # 添加 commits 信息
    prompt += generate_llm_prompt(commits).split("\n\n请根据以上")[0]
    
    if mode == "create":
        prompt += f"""

请执行以下操作：
1. 在 Notion 中搜索 "工作日报" 数据库或今日日报页面（标题包含 {date_str}）
2. 如果没有找到，创建一个新的日报页面，标题为 "工作日报 - {date_str}"
3. 根据以上 commits 生成专业的工作日报内容：
   - 用通俗易懂的语言描述工作内容
   - 按项目分组
   - 总结技术亮点和进展
   - 添加时间戳（如需要）
4. 将日报内容写入 Notion

请确认操作并生成日报。
"""
    else:
        prompt += f"""

请执行以下操作：
1. 在 Notion 中搜索今日的日报页面（标题包含 {date_str}）
2. 找到后，在日报末尾追加以下内容：
   - 添加分隔线或时间标记（如 "--- 下午更新 ---"）
   - 根据新增 commits 生成工作内容描述
   - 与上午内容合并，形成完整的日报
3. 更新 Notion 页面

请确认操作并更新日报。
"""
    
    return prompt


def main():
    print("📊 正在获取今日详细 commits（包含文件改动信息）...")
    print("")
    
    commits = fetch_today_commits_with_details()
    
    if not commits:
        print("😴 今日暂无 commits")
        return
    
    print("")
    print("=" * 70)
    print("🌅 场景 1：创建新的日报（上午/第一次）")
    print("=" * 70)
    print("")
    print("在 Kimi CLI 中输入：")
    print("-" * 70)
    print(generate_notion_prompt(commits, mode="create"))
    
    print("")
    print("=" * 70)
    print("🌙 场景 2：追加更新已有日报（下午/晚上）")
    print("=" * 70)
    print("")
    print("在 Kimi CLI 中输入：")
    print("-" * 70)
    print(generate_notion_prompt(commits, mode="append"))
    
    # 同时输出 JSON 供其他工具使用
    result = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_commits": len(commits),
        "commits": commits
    }
    
    # 保存到临时文件
    output_file = "/tmp/github_daily_commits.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("")
    print("=" * 70)
    print(f"📁 详细数据已保存到: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
