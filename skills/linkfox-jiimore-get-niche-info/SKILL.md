---
name: linkfox-jiimore-get-niche-info
description: 查询并分析极目数据的亚马逊细分市场洞察，包括市场指标、买家评论、竞争格局、价格走势和增长趋势。当用户提到细分市场分析、市场洞察、细分市场数据、市场竞争分析、品牌集中度、新品上架成功率、断货率、价格趋势、评论洞察、市场需求评分、niche market insights, market metrics, competition analysis, price trends, growth trends, Jiimore data, market intelligence, out-of-stock rate时触发此技能。即使用户未明确提及"极目"或"细分市场"，只要其需求涉及通过市场ID查询特定亚马逊细分市场的市场级情报，也应触发此技能。
---

# Jiimore Niche Market Info

This skill guides you on how to query and analyze Amazon niche market data via the Jiimore data service, helping Amazon sellers gain deep insights into specific niche markets including competition, pricing, reviews, and growth trends.

## 调用方式

- **API 端点**：`POST /jiimore/getNicheInfo`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/jiimore_get_niche_info.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-get-niche-info-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Core Concepts

A **niche market** in Jiimore represents a fine-grained product segment on Amazon. Each niche is identified by a unique `nicheId`. This tool retrieves comprehensive market intelligence for a single niche at a time, covering:

- **Market overview**: niche title, demand score, product count, brand count, selling partner count
- **Pricing**: average price, minimum price, maximum price
- **Search & conversion**: weekly/quarterly search volume, search volume growth, search conversion rate, click-to-sale conversion rate, units sold
- **Competition concentration**: top 5 / top 20 product and brand click share (current, 90-day, 360-day snapshots)
- **Product launches**: new products launched, successful launches across 90-day / 180-day / 360-day windows
- **Inventory health**: average out-of-stock rate over time
- **Seller maturity**: average brand age, average selling partner age
- **Review insights**: average review rating, average review count, positive and negative customer review insights
- **Advertising**: ACOS (advertising cost of sales), sponsored products percentage
- **Profitability**: profit margin > 50% SKU ratio, break-even ratio, return rate

**Supported marketplaces**: US (United States), JP (Japan), DE (Germany). Default is **US**.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| nicheId | string | Yes | The niche market ID to query. Maximum 1000 characters. Only one ID per request. |
| countryCode | string | No | Marketplace code. Allowed values: `US`, `JP`, `DE`. Defaults to `US`. |

### How to Use Parameters

1. **nicheId is mandatory**: The user must provide or you must identify the niche market ID. This is a string identifier for a specific Amazon niche segment.
2. **countryCode defaults to US**: Only specify a different value when the user explicitly mentions Japan (`JP`) or Germany (`DE`).
3. **Single ID per call**: This tool only supports one niche ID per request. If the user wants to compare multiple niches, make separate calls.

## Usage Examples

**1. Basic niche market lookup (US)**
Query niche market data for a given niche ID in the US marketplace:
```
nicheId: "12345678"
countryCode: "US"
```

**2. Query a niche in the Japan marketplace**
```
nicheId: "87654321"
countryCode: "JP"
```

**3. Query a niche in the Germany marketplace**
```
nicheId: "11223344"
countryCode: "DE"
```

## Analysis Guidance

When presenting results, organize the rich data into logical sections for the user:

### Market Overview
- Niche title (English and Chinese translation if available)
- Demand score, product count, brand count, selling partner count
- Reference ASIN image (if available)

### Pricing & Profitability
- Average price, min price, max price
- Profit margin > 50% SKU ratio, break-even ratio, return rate
- ACOS

### Search & Demand Trends
- Weekly and quarterly search volume and growth rates
- Search conversion rate, click conversion rate
- Units sold (weekly/quarterly)

### Competition Landscape
- Top 5 and top 20 product/brand click share (current vs. 90-day vs. 360-day)
- Brand count trends, selling partner count trends
- Sponsored products percentage over time

### Product Launch Activity
- New products launched and successful launches across time windows
- Launch success rate (semiannual)

### Review & Customer Insights
- Average review rating and count trends
- Positive and negative customer review insights
- Product star rating impact

### Inventory & Operations
- Average out-of-stock rate trends

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables or grouped sections without subjective business advice unless specifically requested.
2. **Trend comparison**: When the response includes current, 90-day-ago, and 360-day-ago data points, present them side-by-side so users can easily spot trends.
3. **Percentage formatting**: Display share and rate values as percentages (e.g., 0.35 as 35.0%).
4. **Review insights**: If positive/negative customer review insights are present, list them as bullet points.
5. **Image display**: If `referenceAsinImageUrl` is present, display or link to the niche reference image.
6. **Error handling**: When a query fails, explain the reason based on the response and suggest checking the niche ID or country code.
## Important Limitations

- **Single ID only**: Only one niche ID can be queried per request. Batch queries are not supported.
- **Three marketplaces**: Only US, JP, and DE are supported.
- **Niche ID required**: The user must supply the niche ID; this tool cannot search for niches by keyword or category.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about a specific Amazon niche market:

| User Says | Scenario |
|-----------|----------|
| "Look up this niche market", "niche ID info" | Basic niche lookup |
| "How competitive is this niche", "brand concentration" | Competition analysis |
| "What's the average price in this niche" | Pricing intelligence |
| "Search volume for this niche", "demand trends" | Search & demand analysis |
| "How many new products launched", "launch success rate" | Product launch tracking |
| "Review rating in this niche", "buyer feedback insights" | Review analysis |
| "Out-of-stock rate", "inventory health" | Inventory analysis |
| "Is this niche worth entering", "niche opportunity" | Comprehensive niche evaluation |

**Not applicable** -- Needs beyond niche market lookup:

- Searching for niches by keyword or category (this tool requires a known niche ID)
- Individual ASIN-level product analysis
- ABA search term data (use the ABA Data Explorer instead)
- Advertising campaign management or PPC optimization
- Listing copywriting or review management


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
