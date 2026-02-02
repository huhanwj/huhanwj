#!/usr/bin/env python3
"""
获取所有 GitHub 仓库的今日 commits
"""
import requests
from datetime import datetime, timezone
import json
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from config_manager import get_github_token, get_github_username


def get_all_repos(token, username):
    """获取用户的所有仓库（包括参与的）"""
    repos = []
    page = 1
    
    # 获取用户自己的仓库
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        headers = {"Authorization": f"token {token}"}
        params = {"per_page": 100, "page": page, "sort": "pushed", "direction": "desc"}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"获取仓库列表失败: {response.status_code}")
            break
        
        data = response.json()
        if not data:
            break
        
        repos.extend([r["full_name"] for r in data])
        page += 1
        
        # 限制只获取最近活跃的 200 个仓库
        if len(repos) >= 200:
            break
    
    # 获取用户参与的仓库（有 push 权限的）
    page = 1
    while True:
        url = "https://api.github.com/user/repos"
        headers = {"Authorization": f"token {token}"}
        params = {"per_page": 100, "page": page, "affiliation": "collaborator", "sort": "pushed"}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break
        
        data = response.json()
        if not data:
            break
        
        for r in data:
            if r["full_name"] not in repos:
                repos.append(r["full_name"])
        
        page += 1
        if page > 5:  # 限制页数
            break
    
    return repos


def get_today_commits(repo, username, token):
    """获取指定仓库今日的 commits"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59)
    
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "author": username,
        "since": today_start.isoformat(),
        "until": today_end.isoformat(),
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
        elif response.status_code == 409:
            # 空仓库
            return []
        else:
            return []
    except Exception as e:
        print(f"  请求失败 {repo}: {e}")
        return []


def main():
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ 缺少 GitHub 配置")
        return
    
    print(f"🔍 正在获取 {username} 的所有仓库...")
    repos = get_all_repos(token, username)
    print(f"✅ 共找到 {len(repos)} 个仓库")
    print("")
    
    print(f"📊 正在检查今日的 commits...")
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
    
    # 按时间排序
    all_commits.sort(key=lambda x: x["time"])
    
    print("")
    print("=" * 60)
    print(f"📈 统计结果：{len(repos_with_commits)} 个仓库有今日 commits")
    print(f"📈 总 commits 数：{len(all_commits)}")
    print("=" * 60)
    print("")
    
    if all_commits:
        print("📋 今日 Commits 详情：")
        print("")
        current_repo = None
        for c in all_commits:
            if c["repo"] != current_repo:
                current_repo = c["repo"]
                print(f"\n【{current_repo}】")
            msg = c["message"].split('\n')[0][:50]
            print(f"  • [{c['sha']}] {msg}")
    else:
        print("😴 今日暂无 commits")
    
    # 保存结果供后续使用
    result = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_commits": len(all_commits),
        "repos_with_commits": repos_with_commits,
        "commits": all_commits
    }
    
    # 输出为 JSON 格式（便于其他脚本解析）
    print("\n" + "=" * 60)
    print("📤 JSON 格式输出：")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
