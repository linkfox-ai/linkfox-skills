---
name: linkfox-google-trend-get-trend-by-time
description: 查询并分析Google Trends在指定时间范围和国家/地区的实时热门话题与热搜。当用户提到谷歌趋势、热门话题、实时热搜、流行趋势、当前热点、近期热门、病毒式话题、时间段热度、区域趋势分析、Google Trends, real-time hot topics, trending topics, popular trends, recent trending searches, trend discovery时触发此技能。即使用户未明确说"Google Trends"，只要其需求涉及发现特定市场近期热门或正在流行的话题和搜索词，也应触发此技能。
---

# Google Trends Time-Range Analysis

This skill guides you on how to query and analyze Google Trends data for trending topics within a configurable time window, helping users discover real-time popular searches and emerging trends across 18 supported regions.

## Core Concepts

Google Trends reflects real user search interest on Google. This tool retrieves **trending topics** (recently popular queries) for a chosen country/region over a specified number of recent days. It is ideal for spotting what is currently gaining traction in a market.

**Key data points per trending query**:
- **query** -- the trending search term
- **searchVolume** -- relative search volume value
- **increasePercentage** -- percentage change in search interest (-100 to 100, unit: %)
- **startTime / endTime** -- timestamps bounding the trend observation window

A positive `increasePercentage` means rising interest; a negative value means declining interest. A value near 100 signals an explosive spike.

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | integer | No | 7 | Time range in days. Common values: 1 (last 24 hours), 2, 7 (past week) |
| region | string | No | US | Country/region code. See Supported Regions below |

### Supported Regions

US (United States), GB (United Kingdom), JP (Japan), CA (Canada), MX (Mexico), DE (Germany), FR (France), IT (Italy), ES (Spain), NL (Netherlands), AU (Australia), SG (Singapore), AE (United Arab Emirates), BR (Brazil), IN (India), TR (Turkey), PL (Poland), SE (Sweden)

Default region is **US**. Use US when the user does not specify a region.

## 调用方式

- **API 端点**：`POST /googleTrend/getTrendByTime`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/google_trends_rising.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-google-trend-get-trend-by-time-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## Usage Examples

**1. What's trending in the US over the past week?**
```json
{"days": 7, "region": "US"}
```

**2. Hot topics in Japan in the last 24 hours**
```json
{"days": 1, "region": "JP"}
```

**3. Trending searches in Germany over the past 2 days**
```json
{"days": 2, "region": "DE"}
```

**4. Recent buzz in Brazil this week**
```json
{"days": 7, "region": "BR"}
```

**5. What's gaining popularity in the UK right now?**
```json
{"days": 1, "region": "GB"}
```

## Display Rules

1. **Present data clearly**: Show trending queries in a well-formatted table with columns for query, search volume, and increase percentage. Sort by search volume or increase percentage as appropriate.
2. **Highlight spikes**: When `increasePercentage` is notably high (e.g., above 50%), call attention to these breakout topics.
3. **Time context**: Always state the time range and region in your summary so the user knows exactly what window the data covers.
4. **Chart data**: If the response includes `chartOption`, describe the chart structure (title, axes, data points) so the user understands the visual trend.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters (e.g., try a different region code or time range).
## Important Limitations

- **Unstructured data**: Results from this tool are unstructured and cannot be fed into secondary SQL-based query tools for further processing.
- **Relative volumes**: Search volume values are relative, not absolute counts.
- **Short time windows**: The `days` parameter controls recency; this tool is designed for recent/real-time trends, not long historical analysis.
- **Region coverage**: Only the 18 listed regions are supported. Unsupported region codes will produce errors.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about trending/popular topics on Google:

| User Says | Scenario |
|-----------|----------|
| "What's trending right now" | Real-time trending topics |
| "Hot searches in [country]" | Regional trend discovery |
| "What topics are popular this week" | Weekly popularity overview |
| "Any viral topics in [market]" | Breakout / spike detection |
| "Show me Google Trends for [region]" | Region-specific trend query |
| "What's buzzing in the last 24 hours" | Short-window trend scan |
| "Trending searches in [country] recently" | Recent trend analysis |
| "What are people searching for in [region]" | General search interest exploration |

**Not applicable** -- Needs beyond trending topic discovery:

- Historical keyword search volume over months/years (use a dedicated Google Trends historical tool)
- Amazon-specific keyword or ASIN analysis (use ABA tools)
- Advertising / PPC campaign management
- Social media trend analysis (Twitter/X, TikTok, etc.)
- SEO ranking or backlink analysis
- Competitor website traffic estimation

**Boundary judgment**: When users say "market trends" or "what's popular", if it boils down to discovering what people are currently searching for on Google in a specific region, this skill applies. If they are asking about stock market trends, social media virality, or long-term historical search patterns, it does not apply.

## 积分消耗规则

消耗 6 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
