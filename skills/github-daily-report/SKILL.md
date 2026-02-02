---
name: github-daily-report
description: 自动获取 GitHub 今日 commits（含详细改动），使用 LLM 智能生成工作日报并推送到 Notion。支持分时段多次更新。当用户需要写日报、总结今日工作、或追加更新日报时触发此 skill。
---

# GitHub Daily Report

自动获取 GitHub 今日 commits（包含详细的文件改动信息），使用 LLM 智能分析并生成**通俗易懂的工作日报**，通过 MCP 推送到 Notion。**支持中午、晚上分时段多次追加更新**。

## 核心特性

- 📊 **智能分析** - 不只是复制 commit message，LLM 会理解改动内容并翻译成人话
- 📝 **自动日报** - 生成专业、易读的工作日报
- 🔄 **分次更新** - 支持中午写一次，晚上继续追加
- 🔗 **MCP 集成** - 直接推送到 Notion，无需手动操作

## 快速开始

### 1. 配置（仅需一次）

```bash
# GitHub 配置
mkdir -p ~/.config/github-daily-report
cat > ~/.config/github-daily-report/config.json << 'EOF'
{
  "github_token": "ghp_your_token",
  "github_username": "huhanwj",
  "repositories": [
    "huhanwj/RGB-Th-Benchmark",
    "huhanwj/paper-reading",
    "huhanwj/Network-Log-Agent",
    "huhanwj/VLM-Thermal-HRI",
    "huhanwj/Pouring-Agent"
  ]
}
EOF

# Notion MCP 配置
kimi mcp remove notion 2>/dev/null || true
kimi mcp add --transport http --auth oauth notion https://mcp.notion.com/mcp
kimi mcp auth notion
```

### 2. 使用

**生成日报（含详细分析）**：

```bash
cd ~/.kimi/skills/github-daily-report/scripts
python generate_report_v2.py
```

然后将输出的提示文本复制到 Kimi CLI 中执行。

---

## 使用场景

### 场景 1：上午/中午 - 创建日报

运行脚本后，复制输出到 Kimi CLI：

> **"请帮我生成今日工作日报并推送到 Notion。**
> 
> **今日 GitHub Commits 详情：**
> - [commits 详细信息]
> 
> **请执行以下操作：**
> 1. 在 Notion 中搜索 "工作日报" 数据库或今日日报页面
> 2. 如果没有找到，创建一个新的日报页面，标题为 "工作日报 - 2026-02-02"
> 3. 根据以上 commits **生成通俗易懂的工作内容描述**（不要直接复制 commit message）
> 4. 将日报内容写入 Notion"

### 场景 2：下午/晚上 - 追加更新

同样的脚本，选择追加模式：

> **"请帮我更新今日工作日报，在已有日报后面追加新的内容。**
> 
> **新增的 GitHub Commits 详情：**
> - [新增的 commits 信息]
> 
> **请执行以下操作：**
> 1. 在 Notion 中搜索今日的日报页面
> 2. 在日报末尾追加内容，添加分隔线如 "--- 晚上更新 ---"
> 3. 生成新增工作的描述
> 4. 更新 Notion 页面"

---

## 工作流程详解

### 数据获取流程

```
用户运行脚本
    ↓
获取配置的仓库列表 (5 个仓库)
    ↓
遍历每个仓库，获取今日 commits
    ↓
对每个 commit，获取详细改动（文件、行数）
    ↓
生成 LLM 提示文本（两种模式：创建/追加）
    ↓
用户复制提示文本到 Kimi CLI
    ↓
Kimi 通过 MCP 操作 Notion
```

### Kimi 的智能处理

Kimi 拿到 commits 数据后会：

1. **理解改动内容** - 不只是看 commit message，还会分析改动的文件
2. **翻译成"人话"** - 把技术提交变成工作描述，比如：
   - ❌ "feat: Add IRGPT dataset Colab tutorial"
   - ✅ "完成了 IRGPT 数据集的 Colab 教程编写，包含数据加载和可视化功能"
3. **按项目分组** - 清晰展示不同仓库的工作进展
4. **突出亮点** - 总结关键进展和技术突破

---

## 手动操作示例

### 直接对话生成日报

在 Kimi CLI 中：

```
帮我根据今天的 GitHub 工作生成日报。

我的今日 commits：
1. RGB-Th-Benchmark: 添加了 IRGPT 数据集的 Colab 教程，支持数据加载和可视化
2. RGB-Th-Benchmark: 修复了 notebook 中的任务名称处理问题  
3. paper-reading: 添加了 IRGPT 论文阅读笔记

请生成一份专业的工作日报，用通俗易懂的语言描述今天做的工作，然后保存到 Notion 的 "工作日报" 数据库。
```

### 追加更新示例

```
帮我更新今天的工作日报。

下午新增的工作：
1. RGB-Th-Benchmark: 添加了本地版本的 IRGPT 教程，支持自动下载
2. RGB-Th-Benchmark: 更新了 .gitignore 并将 README 翻译成英文

请在 Notion 中找到今天已有的日报，在末尾追加这部分内容，添加 "--- 晚上更新 ---" 分隔线。
```

---

## 配置文件说明

### config.json

```json
{
  "github_token": "ghp_xxxxx",
  "github_username": "huhanwj",
  "repositories": [
    "huhanwj/RGB-Th-Benchmark",
    "huhanwj/paper-reading"
  ]
}
```

| 字段 | 说明 |
|------|------|
| `github_token` | GitHub Personal Access Token (需要 repo 权限) |
| `github_username` | GitHub 用户名 |
| `repositories` | 要监控的仓库列表，脚本会检查这些仓库的今日 commits |

---

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `generate_report_flexible.py` | **推荐** - 灵活版，支持自定义时间范围和指定 Notion 位置 |
| `generate_report_v2.py` | 支持分时段创建/追加日报 |
| `fetch_commits_with_diff.py` | 获取 commits 及详细改动信息 |
| `fetch_commits.py` | 简单版本，只获取基础 commit 信息 |
| `fetch_all_commits.py` | 搜索所有仓库的 commits |
| `config_manager.py` | 配置管理工具 |

---

## 使用场景示例

### 场景：跨天统计（如凌晨工作算前一天）

```bash
python generate_report_flexible.py
# 选择 2) 自定义日期范围
# 开始: 2026-02-02 00:00
# 结束: 2026-02-03 06:00  （凌晨6点前都算2月2日）
# 日报日期: 2026-02-02 (Feb 02)
# Notion 位置: 25-26
```

然后复制输出的提示文本到 Kimi CLI，Kimi 会：
1. 在 Notion 的 "25-26" 页面下查找/创建 "2026-02-02" 的日报
2. 生成通俗易懂的工作日报
3. 推送到指定位置

---

## MCP 操作命令

```bash
# 查看 MCP 状态
kimi mcp list

# 测试 Notion 连接
kimi mcp test notion

# 重新授权
kimi mcp auth notion

# 运行时使用 MCP
kimi  # 进入对话后，输入提示文本
```

---

## 故障排除

### 获取 commits 为空

1. 检查配置文件：`cat ~/.config/github-daily-report/config.json`
2. 确认仓库名正确
3. 确认 GitHub Token 有 repo 权限
4. 检查时区：脚本使用 UTC 时间计算"今日"

### Notion 推送失败

1. 检查 MCP 授权：`kimi mcp auth notion`
2. 确认 Notion 数据库已添加 Integration 连接
3. 检查数据库是否有"标题"字段

### 追加更新找不到日报

确保日报标题包含日期格式（如 "2026-02-02"），这样 MCP 搜索才能找到。
