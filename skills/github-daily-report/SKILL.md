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
  "github_username": "huhanwj"
}
EOF
```

2. **配置 Notion MCP**（仅需一次）

```bash
# 移除可能存在的错误配置
kimi mcp remove notion 2>/dev/null || true

# 重新添加，使用 OAuth 认证
kimi mcp add --transport http --auth oauth notion https://mcp.notion.com/mcp

# 授权（会打开浏览器）
kimi mcp auth notion
```

## 使用方法

### 方式 1：完全自动化（推荐）

在 Kimi CLI 中直接输入：

```
帮我生成本日工作日报并推送到 Notion
```

Kimi 会自动：
1. 搜索你所有 GitHub 仓库的今日 commits
2. 生成格式化的工作日报
3. 询问或搜索 Notion 目标位置
4. 通过 MCP 推送日报

### 方式 2：分步操作

**步骤 1**：运行脚本获取 commits

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python generate_report.py
```

这会输出今日所有 commits 和准备好的提示文本。

**步骤 2**：复制提示文本到 Kimi CLI

将脚本输出的提示文本复制到 Kimi CLI 对话中，Kimi 会生成日报并通过 MCP 推送到 Notion。

### 方式 3：指定 Notion 位置

```
获取今日 GitHub commits，生成工作日报并保存到 Notion 的 "工作日报" 数据库
```

或指定具体页面：

```
根据今日 commits 生成日报，追加到 Notion 页面 "2026年2月" 中
```

## 工作流程

1. **搜索 Commits** → 遍历所有 GitHub 仓库，查找今日 commits
2. **生成日报** → 使用 LLM 将 commits 整理成工作日报
3. **推送 Notion** → 通过 MCP 将日报写入 Notion

## 配置说明

### GitHub 配置

配置文件：`~/.config/github-daily-report/config.json`

| 字段 | 说明 | 获取方式 |
|------|------|----------|
| `github_token` | GitHub Personal Access Token | GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)，勾选 `repo` 权限 |
| `github_username` | GitHub 用户名 | 你的 GitHub 用户名 |

### Notion MCP 配置

MCP 配置存储在 `~/.kimi/mcp.json`。

**管理命令**：

```bash
# 查看已配置的 MCP 服务器
kimi mcp list

# 测试连接
kimi mcp test notion

# 重新授权
kimi mcp auth notion

# 移除配置
kimi mcp remove notion
```

## Notion 数据库/页面要求

通过 MCP，Kimi 可以：
- 搜索现有页面/数据库
- 在数据库中创建新页面
- 在现有页面追加内容
- 创建新页面

**建议的数据库结构**（可选）：

| 字段 | 类型 | 说明 |
|------|------|------|
| 标题 | Title | 日报标题 |
| 日期 | Date | 日报日期 |
| 项目 | Select/Multi-select | 涉及的项目（可选）|

## 故障排除

### MCP 授权失败

```bash
# 检查是否正确添加了 OAuth 参数
kimi mcp list

# 如果看到 "does not use OAuth"，需要重新添加
kimi mcp remove notion
kimi mcp add --transport http --auth oauth notion https://mcp.notion.com/mcp
kimi mcp auth notion
```

### 获取 commits 失败

```bash
# 检查配置
cat ~/.config/github-daily-report/config.json

# 测试获取
python ~/.kimi/skills/github-daily-report/scripts/fetch_all_commits.py
```

### Notion 推送失败

- 确认已完成 OAuth 授权：`kimi mcp auth notion`
- 确认 Notion 数据库已连接 Integration：在 Notion 页面右上角 `...` → `Add connections`
