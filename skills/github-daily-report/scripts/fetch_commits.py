#!/usr/bin/env python3
"""
获取 GitHub 今日 commits
"""
import requests
from datetime import datetime, timezone, timedelta
from config_manager import get_github_token, get_github_username, get_repositories


def get_today_commits_for_repo(repo, username, token):
    """获取指定仓库今日的 commits"""
    # 计算今天和明天的日期（UTC）
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # 格式化为 ISO 8601
    since = today_start.isoformat()
    until = today_end.isoformat()
    
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "author": username,
        "since": since,
        "until": until,
        "per_page": 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    
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
    else:
        print(f"⚠️ 获取 {repo} 失败: {response.status_code}")
        return []


def fetch_all_commits():
    """获取所有配置的仓库的今日 commits"""
    token = get_github_token()
    username = get_github_username()
    repos = get_repositories()
    
    if not all([token, username, repos]):
        print("❌ 配置不完整，请先运行: python config_manager.py")
        return []
    
    all_commits = []
    print(f"\n📊 正在获取 {username} 今日的 commits...")
    
    for repo in repos:
        print(f"  检查 {repo}...", end=" ")
        commits = get_today_commits_for_repo(repo, username, token)
        if commits:
            print(f"✓ 找到 {len(commits)} 个")
            all_commits.extend(commits)
        else:
            print("无")
    
    # 按时间排序
    all_commits.sort(key=lambda x: x["time"])
    
    print(f"\n✅ 共找到 {len(all_commits)} 个 commits")
    return all_commits


if __name__ == "__main__":
    commits = fetch_all_commits()
    if commits:
        print("\n今日 Commits:")
        for c in commits:
            print(f"  [{c['repo']}] {c['sha']}: {c['message'].split(chr(10))[0]}")
