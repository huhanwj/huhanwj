#!/usr/bin/env python3
"""
灵活版工作日报生成器
- 支持自定义日期范围（如包含次日凌晨）
- 支持指定 Notion 目标位置
"""
import requests
from datetime import datetime, timezone, timedelta
import json
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from config_manager import get_github_token, get_github_username, get_repositories


def get_commits_in_range(repo, username, token, start_time, end_time):
    """获取指定时间范围内的 commits"""
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "author": username,
        "since": start_time.isoformat(),
        "until": end_time.isoformat(),
        "per_page": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            commits = response.json()
            return [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"],
                    "repo": repo,
                    "url": c["html_url"],
                    "time": c["commit"]["committer"]["date"]
                }
                for c in commits
            ]
    except Exception as e:
        print(f"  请求失败 {repo}: {e}")
    
    return []


def get_commit_detail(repo, sha, token):
    """获取单个 commit 的详细信息"""
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "stats": data.get("stats", {}),
                "files": [
                    {
                        "filename": f["filename"],
                        "status": f["status"],
                        "additions": f["additions"],
                        "deletions": f["deletions"],
                        "changes": f["changes"]
                    }
                    for f in data.get("files", [])
                ]
            }
    except Exception as e:
        print(f"  获取详情失败: {e}")
    
    return None


def fetch_commits_with_range(start_time, end_time):
    """获取指定时间范围的 commits"""
    token = get_github_token()
    username = get_github_username()
    repos = get_repositories()
    
    if not token or not username:
        print("❌ GitHub 配置不完整")
        return []
    
    if not repos:
        print("❌ 未配置监控的仓库列表")
        return []
    
    all_commits = []
    print(f"📊 正在获取 {username} 的 commits...")
    print(f"   时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   监控仓库: {', '.join(repos)}")
    print("")
    
    for repo in repos:
        print(f"  📁 {repo}...", end=" ", flush=True)
        commits = get_commits_in_range(repo, username, token, start_time, end_time)
        
        # 获取详细信息
        detailed_commits = []
        for c in commits:
            detail = get_commit_detail(repo, c["sha"], token)
            if detail:
                c.update(detail)
            detailed_commits.append(c)
        
        if detailed_commits:
            print(f"✅ {len(detailed_commits)} 个")
            all_commits.extend(detailed_commits)
        else:
            print("无")
    
    # 按时间排序
    all_commits.sort(key=lambda x: x["time"])
    
    print("")
    print(f"✅ 共找到 {len(all_commits)} 个 commits")
    
    return all_commits


def generate_llm_prompt(commits, report_date, notion_location):
    """生成 LLM 提示文本"""
    if not commits:
        return f"今日 ({report_date}) 暂无 commits"
    
    prompt = f"""请帮我生成工作日报并推送到 Notion 的指定位置。

**日报日期**: {report_date}
**Notion 目标位置**: {notion_location}

**今日 GitHub Commits 详情**（共 {len(commits)} 个）：

"""
    
    for c in commits:
        prompt += f"【{c['repo']}】\n"
        prompt += f"Commit: {c['sha']}\n"
        prompt += f"Message: {c['message']}\n"
        
        if "stats" in c:
            stats = c["stats"]
            prompt += f"改动: +{stats.get('additions', 0)} / -{stats.get('deletions', 0)} 行\n"
        
        if "files" in c and c["files"]:
            prompt += "涉及文件:\n"
            for f in c["files"][:8]:
                status_icon = {"added": "+", "modified": "~", "removed": "-"}.get(f["status"], "?")
                prompt += f"  {status_icon} {f['filename']} ({f['changes']}行)\n"
            if len(c["files"]) > 8:
                prompt += f"  ... 等共 {len(c['files'])} 个文件\n"
        
        prompt += "\n"
    
    prompt += f"""
请执行以下操作：

1. 在 Notion 的 "{notion_location}" 页面/数据库中，查找或创建日期为 "{report_date}" 的日报
   - 如果已存在，追加内容
   - 如果不存在，创建新页面

2. 根据以上 commits 生成通俗易懂的工作日报：
   - 用"人话"描述工作内容（不要直接复制 commit message）
   - 按项目/仓库分组
   - 说明解决了什么问题、完成了什么功能
   - 突出技术亮点

3. 将日报保存到 Notion

请确认并生成日报。
"""
    
    return prompt


def main():
    now = datetime.now(timezone.utc)
    
    print("=" * 70)
    print("📅 GitHub Daily Report - 灵活版")
    print("=" * 70)
    print("")
    print("选择统计模式：")
    print("  1) 昨天 + 今天凌晨 (默认到凌晨6点)")
    print("  2) 自定义日期范围")
    print("  3) 今天 (默认0点到现在)")
    print("")
    
    choice = input("请选择 [1/2/3] (默认1): ").strip() or "1"
    
    if choice == "1":
        # 昨天 00:00 ~ 今天 06:00
        yesterday = now - timedelta(days=1)
        start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now.hour < 6:
            # 如果现在还不到6点，就以现在为结束时间
            end_time = now
        report_date = yesterday.strftime("%Y-%m-%d (%b %d)")
        
    elif choice == "2":
        # 自定义
        print("\n输入日期范围 (格式: YYYY-MM-DD HH:MM)")
        start_str = input("开始时间 [2026-02-02 00:00]: ").strip() or "2026-02-02 00:00"
        end_str = input("结束时间 [2026-02-03 06:00]: ").strip() or "2026-02-03 06:00"
        
        try:
            start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except:
            print("❌ 日期格式错误")
            return
        
        report_date = input("日报显示日期 [2026-02-02]: ").strip() or "2026-02-02"
        
    else:
        # 今天 00:00 ~ 现在
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now
        report_date = now.strftime("%Y-%m-%d (%b %d)")
    
    print("")
    print("-" * 70)
    notion_location = input("Notion 目标位置 [25-26]: ").strip() or "25-26"
    print("-" * 70)
    
    # 获取 commits
    commits = fetch_commits_with_range(start_time, end_time)
    
    if not commits:
        print("\n😴 该时间段暂无 commits")
        return
    
    # 生成提示
    prompt = generate_llm_prompt(commits, report_date, notion_location)
    
    print("")
    print("=" * 70)
    print("📝 请复制以下内容到 Kimi CLI：")
    print("=" * 70)
    print("")
    print(prompt)
    print("")
    print("=" * 70)
    
    # 保存到文件
    output_file = "/tmp/github_daily_report_prompt.txt"
    with open(output_file, 'w') as f:
        f.write(prompt)
    print(f"📁 提示文本已保存到: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
