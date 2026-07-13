---
name: linkfox-wallysmarter-product-detail
description: 通过WallySmarter查询Walmart商品详情，包含价格历史和销量趋势。当用户提到Walmart商品详情、沃尔玛产品数据、WallySmarter、沃尔玛价格走势、沃尔玛销量趋势、Walmart product detail, Walmart price history, Walmart sales trend, WallySmarter product时触发此技能。即使用户未明确提及"WallySmarter"，只要其需求涉及查看沃尔玛单个商品的详细信息、历史价格变化或销量走势，也应触发此技能。
---

# WallySmarter Product Detail

This skill retrieves detailed product information from Walmart via WallySmarter, including pricing history and sales volume trends.

## Core Concepts

WallySmarter Product Detail looks up a single Walmart product by its ItemId and returns comprehensive product attributes along with historical pricing and sales data. This is a product-level deep-dive tool, complementing the broader `linkfox-walmart-search` skill that operates at the search/listing level.

**Data scope**: Returns current product attributes (title, price, brand, ratings, fulfillment type, etc.) plus historical stats when `includeStats` is enabled (default).

**Non-structured output**: The tool returns mixed structured and non-structured data. It does NOT support secondary analysis via `@智能数据查询`.

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| productId | integer | Yes | — | Walmart Item ID. Found in product URLs: `https://www.walmart.com/ip/<productId>` |
| includeStats | boolean | No | true | Whether to include historical price and sales data |

## Product Data Fields

| Field | Description |
|-------|-------------|
| title | Product title |
| description | Product description |
| price | Current selling price (USD) |
| wasPrice | Strikethrough price (USD) |
| minPrice | Lowest price (USD) |
| brand | Brand name |
| rating | Average rating (0.0–5.0) |
| reviews | Total review count |
| salesEstimate | Estimated sales volume (units) |
| revenue | Estimated revenue (USD) |
| sellerName | Seller name |
| fulfillmentType | Fulfillment: MARKETPLACE or WFS |
| productPageUrl | Product page URL |
| imageUrl | Product image URL |
| departmentName | Department category name |
| departmentId | Department ID |
| listingScore | Listing quality score |
| contentScore | Content quality score |
| outOfStock | Stock status: 0=in stock, 1=out of stock |
| sponsored | Ad flag: 0=organic, 1=sponsored |
| isBranded | Brand flag: 0=no, 1=yes |
| multipleOptionsAvailable | Variant flag: 0=no, 1=yes |
| usItemId | Internal US Item ID |
| createdAt | Product creation timestamp |
| updatedAt | Last update timestamp |
| stats | Historical price and sales trend data object |

## Usage Examples

**1. Basic product lookup (with history)**
Get full details for a Walmart product including price and sales trends:
```json
{"productId": 5177343351}
```

**2. Product detail only (no history)**
Get product attributes without historical data for faster response:
```json
{"productId": 5169493923, "includeStats": false}
```

## Display Rules

1. **Present data clearly**: Show product details in a structured format. Do not add subjective business recommendations unless asked.
2. **Price formatting**: Display current price alongside wasPrice when available to highlight discounts. Always show USD symbol.
3. **Trend summary**: When stats data is available, summarize price and sales trends (e.g., "Price dropped 15% over the last 30 days").
4. **Score context**: Explain listingScore and contentScore in context (higher = better quality listing).
5. **Stock and fulfillment**: Clearly flag out-of-stock items and fulfillment type (WFS vs Marketplace).
6. **Single product**: This tool queries one product at a time. If the user needs multiple products, call the tool separately for each ItemId.

## Important Limitations

- Only supports lookup by Walmart ItemId (the numeric ID in the product URL)
- Returns non-structured data — NOT compatible with `@智能数据查询` for secondary analysis
- Single ItemId per call; batch queries require multiple invocations
- Historical data availability depends on WallySmarter's tracking coverage

## User Expression & Scenario Quick Reference

**Applicable** — Walmart single-product deep-dive:

| User Says | Scenario |
|-----------|----------|
| "查一下这个Walmart商品的详情" | Basic product lookup |
| "这个沃尔玛产品最近价格走势如何" | Price trend analysis |
| "WallySmarter查Walmart商品5177343351" | Direct ID lookup |
| "沃尔玛这个产品销量怎么样" | Sales estimate check |
| "Walmart product detail for item XX" | English variant |
| "这个Walmart产品最近有没有降价" | Price change detection |

**Not applicable** — Needs beyond single product detail:

- Walmart product search by keyword (use `linkfox-walmart-search`)
- Bulk product comparison across multiple items simultaneously
- Walmart seller account or advertising metrics
- Real-time inventory or delivery estimates
- Category-level market analysis

**Boundary judgment**: If the user has a specific Walmart product ID or URL and wants detailed attributes, pricing history, or sales trends, this skill applies. If they want to search/browse products by keyword or category, use `linkfox-walmart-search` instead.

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

## 积分消耗规则

按动态规则计费：消耗积分 = tokens × 10.5。只查商品详情、不带历史统计时 tokens = 1；顺带查近 90 天历史统计时每个商品详情 tokens = 2。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
