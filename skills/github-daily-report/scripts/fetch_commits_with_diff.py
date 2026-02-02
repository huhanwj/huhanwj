#!/usr/bin/env python3
"""
获取 GitHub 今日 commits，包含详细的文件改动信息
"""
import requests
from datetime import datetime, timezone
import json
from config_manager import get_github_token, get_github_username, get_repositories


def get_commit_detail(repo, sha, token):
    """获取单个 commit 的详细信息，包括文件改动"""
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
                "sha": data["sha"][:7],
                "message": data["commit"]["message"],
                "author": data["commit"]["author"]["name"],
                "time": data["commit"]["committer"]["date"],
                "stats": data.get("stats", {}),
                "files": [
                    {
                        "filename": f["filename"],
                        "status": f["status"],  # added, modified, removed
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


def get_today_commits(repo, username, token, include_details=True):
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
            result = []
            
            for c in commits:
                commit_info = {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"],
                    "repo": repo,
                    "url": c["html_url"],
                    "time": c["commit"]["committer"]["date"]
                }
                
                # 如果需要详细信息，获取文件改动
                if include_details:
                    detail = get_commit_detail(repo, c["sha"], token)
                    if detail:
                        commit_info["stats"] = detail["stats"]
                        commit_info["files"] = detail["files"]
                
                result.append(commit_info)
            
            return result
    except Exception as e:
        print(f"  请求失败: {e}")
    
    return []


def fetch_today_commits_with_details():
    """获取今日所有 commits 及详细信息"""
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
    print(f"📊 正在获取 {username} 今日的详细 commits...")
    print(f"   监控仓库: {', '.join(repos)}")
    print("")
    
    for repo in repos:
        print(f"  📁 {repo}...", end=" ", flush=True)
        commits = get_today_commits(repo, username, token, include_details=True)
        if commits:
            print(f"✅ {len(commits)} 个")
            all_commits.extend(commits)
        else:
            print("无")
    
    # 按时间排序
    all_commits.sort(key=lambda x: x["time"])
    
    print("")
    print(f"✅ 共找到 {len(all_commits)} 个 commits")
    
    return all_commits


def generate_llm_prompt(commits):
    """生成给 LLM 的提示文本"""
    if not commits:
        return "今日暂无 commits"
    
    prompt = f"今日 ({datetime.now(timezone.utc).strftime('%Y-%m-%d')}) 共提交 {len(commits)} 个 commits：\n\n"
    
    for c in commits:
        prompt += f"【{c['repo']}】\n"
        prompt += f"Commit: {c['sha']}\n"
        prompt += f"Message: {c['message']}\n"
        
        if "stats" in c:
            stats = c["stats"]
            prompt += f"改动: +{stats.get('additions', 0)} / -{stats.get('deletions', 0)} 行\n"
        
        if "files" in c and c["files"]:
            prompt += "涉及文件:\n"
            for f in c["files"][:10]:  # 限制文件数量
                status_icon = {"added": "+", "modified": "~", "removed": "-"}.get(f["status"], "?")
                prompt += f"  {status_icon} {f['filename']} ({f['changes']}行)\n"
            if len(c["files"]) > 10:
                prompt += f"  ... 等共 {len(c['files'])} 个文件\n"
        
        prompt += "\n"
    
    prompt += """
请根据以上 GitHub commits 信息，生成一份专业的工作日报，要求：

1. **用通俗易懂的语言**描述工作内容，不要直接复制 commit message
2. **总结主要工作成果**，说明做了什么事情、解决了什么问题
3. **按项目分组**，清晰展示不同仓库的工作
4. **突出技术亮点或关键进展**
5. **保持简洁专业**，适合作为工作汇报

请生成可直接用于工作汇报的日报内容。
"""
    
    return prompt


if __name__ == "__main__":
    commits = fetch_today_commits_with_details()
    
    if commits:
        print("\n" + "=" * 60)
        print("📝 供 LLM 使用的提示文本：")
        print("=" * 60)
        print(generate_llm_prompt(commits))
