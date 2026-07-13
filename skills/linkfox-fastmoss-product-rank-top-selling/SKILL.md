---
name: linkfox-fastmoss-product-rank-top-selling
description: 通过FastMoss数据查询TikTok全球电商市场的热销商品排行榜，支持按日/周/月维度和类目维度分析。当用户提到TikTok热销榜、TikTok爆品排行、TikTok销量排行、TikTok GMV排名、TikTok类目热销、TikTok选品周报、TikTok top-selling rankings, TikTok bestseller charts, TikTok GMV ranking, TikTok category hot sellers, TikTok weekly product report, FastMoss时触发此技能。即使用户未明确提及"FastMoss"，只要其需求涉及查看TikTok平台的热销排行榜或按时间维度的销售排名，也应触发此技能。
---

# FastMoss - TikTok Top Selling Rankings

This skill guides you on how to query and analyze the TikTok top selling product rankings via the FastMoss data source, helping cross-border e-commerce sellers identify hot-selling products across TikTok's global markets by day, week, or month.

## Core Concepts

The TikTok Top Selling Ranking tracks the best-performing products on TikTok Shop across 9 global markets. It reveals which products are leading in sales volume, GMV, and growth rate over configurable time windows (daily, weekly, monthly). This is an essential tool for product scouting, trend analysis, and competitive intelligence in TikTok e-commerce.

**Data scope**: The ranking covers 9 TikTok Shop markets and supports three time granularities — day, week, and month — via the `dateInfo` parameter. Each product entry includes sales volume, GMV, growth rate, commission rate, shop information, category, and more.

**dateInfo format is important**:
- type: `"day"` -> value: `"2025-02-01"` (YYYY-MM-DD)
- type: `"week"` -> value: `"2025-18"` (year-weekNumber)
- type: `"month"` -> value: `"2025-02"` (year-month)

**Pagination**: Results are paginated. Use `page` (page number, starting from 1) and `pageSize` (items per page, max 10, default 10) to navigate through the result set. 

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Market region code (US, GB, MX, ES, ID, VN, MY, TH, PH) |
| dateInfo | object | Yes | Date specification with `type` (day/week/month) and `value` (see format above) |
| category | string | No | Category name in English, matched to TikTok category ID. Non-English input should be translated first |
| orderby | object | No | Sorting: `field` (units_sold/gmv/total_units_sold/total_gmv/growth_rate) + `order` (desc/asc). Default: desc |
| page | integer | No | Page number, default 1 |
| pageSize | integer | No | Items per page, max 10, default 10 |

## Supported Markets

| Code | Market |
|------|--------|
| US | United States |
| GB | United Kingdom |
| MX | Mexico |
| ES | Spain |
| ID | Indonesia |
| VN | Vietnam |
| MY | Malaysia |
| TH | Thailand |
| PH | Philippines |

Default market is **US**. Use US when the user does not specify a market.

## 调用方式

- **API 端点**：`POST /fastmoss/productRankTopSelling`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/fastmoss_product_rank_top_selling.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-fastmoss-product-rank-top-selling-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Today's top selling products in the US (daily)**
Query the US market for a specific day to see which products lead in sales.
```
region: "US", dateInfo: {"type": "day", "value": "2026-04-15"}
```

**2. Weekly top sellers in the UK**
Check the UK market for weekly best-performing products.
```
region: "GB", dateInfo: {"type": "week", "value": "2026-15"}
```

**3. Monthly GMV leaders in Southeast Asia**
Scout the Indonesian market for monthly top sellers sorted by GMV.
```
region: "ID", dateInfo: {"type": "month", "value": "2026-03"}, orderby: {"field": "gmv", "order": "desc"}
```

**4. Category-specific ranking**
Find top selling products in a specific category.
```
region: "US", dateInfo: {"type": "day", "value": "2026-04-15"}, category: "Beauty"
```

## Data Fields (Response)

| Field | API Name | Description |
|-------|----------|-------------|
| Product Title | title | Name of the product |
| Product ID | productId | Unique product identifier |
| Region | region | Market region code |
| Price | price | Product price |
| Min Price | minPrice | Lowest price |
| Max Price | maxPrice | Highest price |
| Currency | currency | Currency code |
| Total Sales | totalSaleCnt | Total units sold |
| 1-Day Sales | totalSale1dCnt | Units sold in the last 1 day (when dateType=day) |
| 7-Day Sales | totalSale7dCnt | Units sold in the last 7 days (when dateType=week) |
| 30-Day Sales | totalSale30dCnt | Units sold in the last 30 days (when dateType=month) |
| Total GMV | totalSaleGmvAmt | Total gross merchandise value |
| 1-Day GMV | totalSaleGmv1dAmt | GMV in the last 1 day (when dateType=day) |
| 7-Day GMV | totalSaleGmv7dAmt | GMV in the last 7 days (when dateType=week) |
| 30-Day GMV | totalSaleGmv30dAmt | GMV in the last 30 days (when dateType=month) |
| Growth Rate | growthRate | Sales growth rate (percentage) |
| Shop Name | shopName | Name of the seller's shop |
| Shop Total Units Sold | shopTotalUnitsSold | Total units sold by the shop |
| Shop Seller ID | shopSellerId | Unique shop seller identifier |
| Category Name | categoryName | Product category |
| Commission Rate | productCommissionRate | Commission rate in basis points (1000 = 10%) |
| Image URL | imageUrl | Product image URL |
| Delisted Status | offShelvesText | Delisted indicator ("是" = delisted, "否" = active) |

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Growth rate**: Growth rate is in percentage -- show with % sign
3. **Commission rate**: Commission rate is in basis points (1000 = 10%) -- convert to percentage for display
4. **Currency awareness**: Always display currency alongside prices since different markets use different currencies
5. **dateInfo format**: Validate and remind users of the correct format for the selected time granularity
6. **Delisted status**: `offShelvesText` value "是" means delisted, "否" means active -- clarify this for users

## Important Limitations

- **dateInfo is mandatory**: Both `type` and `value` must be provided with specific format requirements
- **No keyword search**: This tool does NOT support keyword search (use linkfox-fastmoss-product-search for that)
- **Max 10 items per page**: The `pageSize` parameter cannot exceed 10
- **Data delay**: Data has T+1 statistical delay

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok top selling product rankings and trend analysis:

| User Says | Scenario |
|-----------|----------|
| "What are the top selling products on TikTok" | Top selling ranking lookup |
| "TikTok bestsellers this week", "hot products on TikTok Shop" | Weekly/daily ranking query |
| "TikTok GMV ranking", "highest revenue products on TikTok" | GMV-based ranking |
| "TikTok category hot sellers", "top selling beauty products on TikTok" | Category-specific ranking |
| "TikTok weekly product report", "monthly top sellers" | Time-dimension analysis |
| "FastMoss top selling", "FastMoss ranking data" | Direct data source reference |
| "Which products are growing fastest on TikTok" | Growth rate sorted ranking |

**Not applicable** -- Needs beyond TikTok top selling rankings:

- Amazon product research or ABA keyword data
- TikTok advertising / ad campaign management
- TikTok content creation or video editing
- Product reviews or listing copywriting
- TikTok product keyword search (use linkfox-fastmoss-product-search instead)
- Profit margin calculations or pricing strategy

**Boundary judgment**: When users say "product research" or "what's selling well", if the context clearly involves TikTok Shop or TikTok e-commerce rankings, this skill applies. If they are asking about Amazon, Shopify, or other platforms, it does not apply. If they want to search products by keyword rather than browse rankings, use linkfox-fastmoss-product-search instead.

## 积分消耗规则

消耗 10.5 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
