#!/usr/bin/env python3
"""
生成工作日报并准备推送到 Notion
"""
import json
from datetime import datetime, timezone
from fetch_all_commits import get_all_repos, get_today_commits, get_github_token, get_github_username


def generate_markdown_report(commits_data):
    """生成 Markdown 格式的工作日报"""
    date = commits_data["date"]
    total = commits_data["total_commits"]
    repos = commits_data["repos_with_commits"]
    commits = commits_data["commits"]
    
    lines = []
    lines.append(f"# 工作日报 - {date}")
    lines.append("")
    lines.append(f"**今日提交**: {total} 个 commits 分布在 {len(repos)} 个仓库")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 按仓库分组
    current_repo = None
    for c in commits:
        if c["repo"] != current_repo:
            current_repo = c["repo"]
            lines.append(f"## 📁 {current_repo}")
            lines.append("")
        
        # 获取第一行作为标题
        msg_lines = c["message"].split('\n')
        title = msg_lines[0][:60]
        
        lines.append(f"**[{c['sha']}]** {title}")
        
        # 如果有详细描述，也加上
        if len(msg_lines) > 1:
            detail = '\n'.join(msg_lines[1:]).strip()
            if detail:
                lines.append(f"> {detail[:200]}..." if len(detail) > 200 else f"> {detail}")
        
        lines.append("")
    
    return '\n'.join(lines)


def generate_summary(commits_data):
    """生成供 LLM 使用的总结"""
    date = commits_data["date"]
    total = commits_data["total_commits"]
    repos = commits_data["repos_with_commits"]
    commits = commits_data["commits"]
    
    summary = f"今日 ({date}) 共提交 {total} 个 commits，涉及 {len(repos)} 个项目：\n\n"
    
    for repo in repos:
        repo_commits = [c for c in commits if c["repo"] == repo]
        summary += f"【{repo}】\n"
        for c in repo_commits:
            msg = c["message"].split('\n')[0][:50]
            summary += f"  - {msg}\n"
        summary += "\n"
    
    return summary


def main():
    print("📊 正在获取所有仓库的今日 commits...")
    print("")
    
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ 缺少 GitHub 配置")
        return
    
    repos = get_all_repos(token, username)
    print(f"✅ 找到 {len(repos)} 个仓库，开始检查...")
    print("")
    
    all_commits = []
    repos_with_commits = []
    
    for i, repo in enumerate(repos, 1):
        print(f"  [{i}/{len(repos)}] {repo}...", end=" ", flush=True)
        commits = get_today_commits(repo, username, token)
        if commits:
            print(f"✅ {len(commits)} 个")
            all_commits.extend(commits)
            repos_with_commits.append(repo)
        else:
            print("无")
    
    all_commits.sort(key=lambda x: x["time"])
    
    commits_data = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_commits": len(all_commits),
        "repos_with_commits": repos_with_commits,
        "commits": all_commits
    }
    
    print("")
    print("=" * 60)
    
    if not all_commits:
        print("😴 今日暂无 commits")
        return
    
    print(f"📈 找到 {len(all_commits)} 个 commits")
    print("=" * 60)
    print("")
    
    # 输出生成的报告
    report = generate_markdown_report(commits_data)
    summary = generate_summary(commits_data)
    
    print("📝 生成的工作日报：")
    print("-" * 60)
    print(report)
    print("-" * 60)
    print("")
    
    # 输出生成 Notion 内容的提示
    print("💡 复制下面的内容到 Kimi CLI 进行 Notion 推送：")
    print("")
    print("=" * 60)
    print("根据以下今日工作提交，生成工作日报并保存到 Notion：")
    print("")
    print(summary)
    print("")
    print("请生成格式化的工作日报，并通过 MCP 推送到 Notion。")
    print("=" * 60)


if __name__ == "__main__":
    main()
