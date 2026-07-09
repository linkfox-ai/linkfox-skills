---
name: linkfox-echotik-list-new-product-rank
description: 通过EchoTik新品排行数据，发现TikTok Shop 16个区域市场的热门新品。当用户提到TikTok新品排行、TikTok热销商品、TikTok Shop爆品、短视频电商选品、TikTok新品发掘、跨境TikTok选品、TikTok new product rankings, TikTok bestsellers, short-video product selection, TikTok viral products, new product ranking, TikTok product trends时触发此技能。即使用户未明确提及"EchoTik"或"新品排行"，只要其需求涉及发现TikTok Shop上的热卖新品或新兴商品趋势，也应触发此技能。
---

# EchoTik - TikTok New Product Ranking

This skill guides you on how to query and analyze the TikTok Shop new product ranking data via the EchoTik data source, helping cross-border e-commerce sellers identify trending new products across TikTok's regional markets.

## Core Concepts

The TikTok New Product Ranking tracks recently listed products that are gaining traction on TikTok Shop. It reveals which new products are selling well, their pricing, sales volume, influencer coverage, and live-stream activity. This is an essential tool for product scouting, trend analysis, and competitive intelligence in the short-video e-commerce space.

**Data scope**: The ranking covers 16 TikTok Shop markets and provides daily snapshots of new products along with their performance metrics (sales volume, revenue, influencer count, video count, live-stream count, commission rate, ratings, and more).

**Pagination**: Results are paginated. Use `pageNum` (page number, starting from 1) and `pageSize` (items per page, default 50) to navigate through the result set.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | Yes | Query date in `YYYY-MM-DD` format |
| region | string | No | Market region code. Default: `US`. See Supported Markets below |
| pageNum | integer | No | Page number, starting from 1 (default: 1) |
| pageSize | integer | No | Number of products per page (default: 50) |

## Supported Markets

| Code | Market |
|------|--------|
| US | United States |
| GB | United Kingdom |
| ID | Indonesia |
| TH | Thailand |
| PH | Philippines |
| MY | Malaysia |
| VN | Vietnam |
| MX | Mexico |
| SG | Singapore |
| SA | Saudi Arabia |
| BR | Brazil |
| ES | Spain |
| JP | Japan |
| DE | Germany |
| IT | Italy |
| FR | France |

Default market is **US**. Use US when the user does not specify a market.

## 调用方式

- **API 端点**：`POST /echotik/listNewProductRank`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/echotik_list_new_product_rank.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-list-new-product-rank-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Today's trending new products in the US**
Query the US market for the current date to see which new products are gaining traction.
```
date: "2025-06-15", region: "US"
```

**2. Discover hot new products in Southeast Asia**
Check the Indonesian or Thai market for new product opportunities.
```
date: "2025-06-15", region: "ID"
```

**3. Browse the UK market new product ranking**
Scout the UK TikTok Shop for trending new arrivals.
```
date: "2025-06-15", region: "GB"
```

**4. Paginate through a large result set**
Retrieve the second page of 20 results for the US market.
```
date: "2025-06-15", region: "US", pageNum: 2, pageSize: 20
```

## Data Fields (Response)

| Field | API Name | Description |
|-------|----------|-------------|
| Product Title | title | Name of the product |
| Product ID | asin | Unique product identifier |
| Region | region | Market region code |
| Price (Avg) | price | Average SPU price |
| Min Price | minPrice | Lowest price |
| Max Price | maxPrice | Highest price |
| Currency | currency | Currency code |
| Total Sales | totalSaleCnt | Total units sold |
| 30-Day Sales | totalSale30dCnt | Units sold in the last 30 days |
| Total Revenue | totalSaleGmvAmt | Total gross merchandise value |
| 30-Day Revenue | totalSaleGmv30dAmt | Revenue in the last 30 days |
| Sales Trend | salesTrendFlagText | Sales trend indicator (0 = stable, 1 = rising, 2 = declining) |
| Total Videos | totalVideoCnt | Number of associated videos |
| Total Live Streams | totalLiveCnt | Number of associated live streams |
| Total Influencers | totalIflCnt | Number of influencers promoting the product |
| Commission Rate | productCommissionRate | Product commission rate |
| Rating | productRating | Average product rating |
| Review Count | reviewCount | Number of product reviews |
| First Seen Date | availableDate | Date the product was first tracked |
| Category ID | categoryId | Product category identifier |
| Image URL | imageUrl | Product image URL |
| Image URLs | productImageUrls | List of product image URLs |

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Sales trend clarification**: When showing sales trend data, translate the numeric flag into human-readable labels: 0 = Stable, 1 = Rising, 2 = Declining
3. **Currency awareness**: Always display prices alongside their currency code since different markets use different currencies
4. **Volume notice**: When results are large, show a summary of the top products and remind users they can paginate for more results
5. **Image handling**: If product image URLs are available, mention them but do not attempt to render images inline unless the environment supports it
6. **Error handling**: When a query fails, explain the reason and suggest adjusting the date or region parameters
## Important Limitations

- **Date required**: The `date` parameter is mandatory; there is no default date
- **Daily granularity**: Data is a daily snapshot, not weekly or monthly
- **Pagination**: Use `pageNum` and `pageSize` to navigate large result sets; not all products are returned in a single call

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok Shop new product discovery and trend analysis:

| User Says | Scenario |
|-----------|----------|
| "What new products are trending on TikTok" | New product ranking lookup |
| "TikTok bestsellers today", "hot products on TikTok Shop" | Daily ranking query |
| "New product opportunities in Southeast Asia TikTok" | Regional market scouting |
| "Which new items are selling well on TikTok UK" | Region-specific ranking |
| "TikTok product scouting", "short-video e-commerce trends" | General product discovery |
| "Show me rising new products on TikTok" | Trend-filtered ranking |
| "TikTok influencer product picks", "what are TikTok creators promoting" | Influencer-driven product discovery |

**Not applicable** -- Needs beyond TikTok new product rankings:

- Amazon product research or ABA keyword data
- TikTok advertising / ad campaign management
- TikTok content creation or video editing
- Product reviews or listing copywriting
- Historical trend analysis spanning many months (this tool provides daily snapshots)
- Profit margin calculations or pricing strategy

**Boundary judgment**: When users say "product research" or "what's selling well", if the context clearly involves TikTok Shop or short-video e-commerce, this skill applies. If they are asking about Amazon, Shopify, or other platforms, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
