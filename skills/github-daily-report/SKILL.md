---
name: github-daily-report
description: 自动获取 GitHub 今日 commits，使用 LLM 智能生成工作日报，并推送到 Notion。用于每日工作结束时生成本日工作日报。当用户需要写日报、总结今日工作、生成工作日报时触发此 skill。
---

# GitHub Daily Report

自动获取 GitHub 今日 commits，使用 LLM 智能生成工作日报，并推送到 Notion。

## 快速开始

在 Kimi CLI 中执行：

```
使用 github-daily-report skill
```

或简单输入：

```
帮我生成本日日报
```

## 工作流程

1. **检查配置** → 如缺少配置，交互式提示输入
2. **获取 Commits** → 从配置的 GitHub 仓库获取今日 commits
3. **生成日报** → 使用 LLM 将 commits 整理成工作日报
4. **推送 Notion** → 将日报推送到 Notion 数据库

## 配置项

首次使用需要配置（会自动提示）：

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `github_token` | GitHub Personal Access Token | GitHub Settings → Developer settings → Personal access tokens |
| `github_username` | GitHub 用户名 | 你的 GitHub 用户名 |
| `repositories` | 要监控的仓库列表 | 格式: `owner/repo1, owner/repo2` |
| `notion_token` | Notion Integration Token | Notion Settings → Integrations → New integration |
| `notion_database_id` | Notion 数据库 ID | 打开数据库页面，URL 中的 ID |

配置文件存储在 `~/.config/github-daily-report/config.json`

## Notion 数据库要求

数据库需要包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | Title | 日报标题 |
| 日期 | Date | 日报日期 |

## 手动配置

如需手动修改配置，运行：

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python config_manager.py
```

## 手动获取 Commits（调试用）

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python fetch_commits.py
```

## 手动推送到 Notion（调试用）

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python push_to_notion.py
```
