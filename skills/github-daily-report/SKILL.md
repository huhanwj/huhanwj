---
name: github-daily-report
description: 自动获取 GitHub 今日 commits，使用 LLM 智能生成工作日报，并通过 MCP 推送到 Notion。用于每日工作结束时生成本日工作日报。当用户需要写日报、总结今日工作、生成工作日报时触发此 skill。
---

# GitHub Daily Report

自动获取 GitHub 今日 commits，使用 LLM 智能生成工作日报，并通过 MCP 推送到 Notion。

## 快速开始

### 前置要求

1. **配置 GitHub Token**（仅需一次）

```bash
mkdir -p ~/.config/github-daily-report
cat > ~/.config/github-daily-report/config.json << 'EOF'
{
  "github_token": "ghp_your_github_token",
  "github_username": "huhanwj",
  "repositories": ["huhanwj/project1", "huhanwj/project2"]
}
EOF
```

2. **配置 Notion MCP**（仅需一次）

```bash
# 添加 MCP 服务器
kimi mcp add --transport http notion https://mcp.notion.com/mcp

# OAuth 授权
kimi mcp auth notion
```

3. **开始使用**

在 Kimi CLI 中直接输入：

```
帮我生成本日日报
```

## 工作流程

1. **获取 Commits** → 从配置的 GitHub 仓库获取今日 commits
2. **生成日报** → 使用 LLM 将 commits 整理成工作日报
3. **推送 Notion** → 通过 MCP 将日报写入 Notion

## 配置说明

### GitHub 配置

配置文件：`~/.config/github-daily-report/config.json`

| 字段 | 说明 | 获取方式 |
|------|------|----------|
| `github_token` | GitHub Personal Access Token | GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)，勾选 `repo` 权限 |
| `github_username` | GitHub 用户名 | 你的 GitHub 用户名 |
| `repositories` | 监控的仓库列表 | 格式: `["owner/repo1", "owner/repo2"]` |

### Notion MCP 配置

MCP 配置会自动保存在 `~/.kimi/mcp.json`。

授权后，你可以在 Notion 中：
- 创建新页面
- 搜索现有页面
- 修改页面内容
- 添加评论等

## 使用方法

### 基础用法 - 自动生成日报

```
帮我生成本日日报
```

Kimi 会：
1. 获取今日 GitHub commits
2. 生成工作日报内容
3. 询问你要写入哪个 Notion 页面/数据库
4. 通过 MCP 写入 Notion

### 指定写入位置

```
帮我生成本日日报，写入 Notion 的 "工作日报" 数据库
```

### 自定义日报格式

```
帮我生成本日日报，按项目分组，并突出显示重要更新
```

## 手动脚本（调试用）

如需单独获取 commits：

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python fetch_commits.py
```

## 故障排除

### MCP 连接失败

```bash
# 检查 MCP 服务器状态
kimi mcp list

# 重新授权
kimi mcp auth notion

# 测试连接
kimi mcp test notion
```

### 获取 commits 失败

检查 `~/.config/github-daily-report/config.json` 是否正确配置。
