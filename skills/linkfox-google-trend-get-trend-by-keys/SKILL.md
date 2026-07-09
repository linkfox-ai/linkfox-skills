---
name: linkfox-google-trend-get-trend-by-keys
description: Google Trends关键词搜索热度对比与趋势分析，支持全球区域和自定义时间范围。当用户提到谷歌趋势、关键词随时间变化的热度、搜索兴趣对比、关键词趋势分析、季节性趋势检测、区域搜索热度、关键词热力图、多个关键词在Google上的对比、Google Trends, keyword popularity comparison, search trends, seasonal analysis, regional popularity, keyword comparison时触发此技能。即使用户未明确说"Google Trends"，只要其需求涉及对比不同时间段或区域的关键词搜索热度趋势，也应触发此技能。
---

# Google Trends Keyword Trend Analysis

This skill guides you on how to query and analyze Google Trends keyword search interest data, helping users understand how keyword popularity changes over time across different regions.

## Core Concepts

Google Trends provides normalized search interest data (0-100 scale) reflecting how popular a given search term is relative to its peak popularity in the selected region and time range. A value of 100 represents peak popularity, 50 means the term is half as popular as its peak, and 0 means insufficient data.

**Important language rule**: Keywords must be in the language of the target country. For example, use English keywords for the US, German keywords for Germany, Japanese keywords for Japan. If the user provides keywords in the wrong language, translate them before querying.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | The search keyword to analyze (max 100 characters). Must be in the target country's language. |
| region | string | No | Country/region code. Defaults to `US`. |
| dayRangeStart | string | No | Start date for the time range (format: YYYY-MM-DD, from 2004 onward). |
| dayRangeEnd | string | No | End date for the time range (format: YYYY-MM-DD, from 2004 onward). |

When both `dayRangeStart` and `dayRangeEnd` are provided, the custom time range takes priority.

## Supported Regions

US (United States), GB (United Kingdom), JP (Japan), CA (Canada), MX (Mexico), DE (Germany), FR (France), IT (Italy), ES (Spain), NL (Netherlands), AU (Australia), SG (Singapore), AE (United Arab Emirates), BR (Brazil), IN (India), TR (Turkey), PL (Poland), SE (Sweden)

Default region is **US**. Use US when the user doesn't specify a region.

## 调用方式

- **API 端点**：`POST /googleTrend/getTrendByKeys`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/google_trends_keyword.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-google-trend-get-trend-by-keys-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## How to Build Queries

### Principles for Effective Queries

1. **Use the correct language**: Always ensure keywords match the target region's language. Translate first if needed.
2. **Specify a region**: Default is US, but always confirm the user's intended market.
3. **Use date ranges for focused analysis**: For seasonal trends or specific event analysis, provide `dayRangeStart` and `dayRangeEnd`.
4. **Keep keywords concise**: Google Trends works best with short, focused search terms.

### Usage Examples

**1. Basic Keyword Trend (Default Region & Time)**
```json
{"keyword": "wireless charger"}
```
Query the overall search interest trend for "wireless charger" in the US.

**2. Keyword Trend in a Specific Region**
```json
{"keyword": "Ladekabel", "region": "DE"}
```
Query the search interest for "Ladekabel" (charging cable) in Germany.

**3. Custom Date Range Analysis**
```json
{"keyword": "christmas gifts", "region": "US", "dayRangeStart": "2024-09-01", "dayRangeEnd": "2025-01-31"}
```
Analyze the seasonal trend of "christmas gifts" in the US from September 2024 through January 2025.

**4. Year-over-Year Comparison**
```json
{"keyword": "sunscreen", "region": "AU", "dayRangeStart": "2023-01-01", "dayRangeEnd": "2025-12-31"}
```
Compare multi-year seasonality of "sunscreen" in Australia.

**5. Regional Market Research**
```json
{"keyword": "yoga mat", "region": "GB"}
```
Check the popularity trend of "yoga mat" in the United Kingdom.

**6. Emerging Trend Detection**
```json
{"keyword": "AI glasses", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-12-31"}
```
Track the rise of "AI glasses" search interest over the past two years in the US.

## Display Rules

1. **Present data clearly**: Show trend data in well-formatted tables or describe the trend curve. Include key data points such as peak values, troughs, and notable changes.
2. **Explain the scale**: Remind users that Google Trends values are on a 0-100 normalized scale, where 100 = peak popularity in the selected scope.
3. **Highlight patterns**: Point out seasonal patterns, sudden spikes, or sustained growth/decline when visible in the data.
4. **Chart data availability**: When the response includes `chartOption`, mention that visualization data is available and describe the trend shape.
5. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., check keyword spelling, try a different date range, ensure the keyword is in the correct language).
## Important Limitations

- **No secondary SQL processing**: Results from this tool are unstructured and cannot be fed into dynamic query tools for secondary analysis.
- **Normalized values**: Trend values are relative (0-100), not absolute search volumes.
- **Data availability**: Data is available from 2004 onward, but very niche terms may have sparse data.
- **Single keyword per call**: Each API call handles one keyword. For multi-keyword comparisons, make separate calls and compare results.
- **Language requirement**: Keywords must match the target region's language for accurate results.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about keyword search popularity trends:

| User Says | Scenario |
|-----------|----------|
| "How popular is XX keyword on Google" | Basic trend lookup |
| "Is XX trending up or down" | Trend direction analysis |
| "When does XX peak in searches" | Seasonal peak detection |
| "Compare popularity of XX across months" | Seasonal pattern analysis |
| "Is XX gaining traction in Germany" | Regional trend check |
| "What's the search trend for XX over the past year" | Historical trend analysis |
| "Holiday search trends for XX" | Seasonal / event-driven analysis |

**Not applicable** -- Needs beyond Google Trends search interest data:

- Google Ads keyword planner or bid/CPC data
- Absolute search volume numbers (Google Trends provides relative, not absolute data)
- Social media trending topics (Twitter/X, TikTok, etc.)
- Amazon-specific search term data (use ABA Data Explorer instead)
- Website traffic analytics (Google Analytics, SimilarWeb, etc.)
- Keyword ranking on search engine result pages (SEO rank tracking)

**Boundary judgment**: When users say "keyword research" or "market trend analysis", if it specifically relates to search interest popularity over time from Google's perspective, this skill applies. If they want absolute traffic numbers, advertising metrics, or e-commerce-platform-specific data, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
