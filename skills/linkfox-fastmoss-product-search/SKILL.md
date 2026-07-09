---
name: linkfox-fastmoss-product-search
description: 基于FastMoss数据搜索和筛选TikTok全球电商商品，支持关键词搜索、多维度筛选（类目、店铺类型、佣金率、销量、达人数等）和排序。当用户提到TikTok选品、TikTok商品搜索、TikTok产品数据、TikTok达人带货、TikTok佣金率、TikTok爆款追踪、TikTok GMV分析、TikTok product search, TikTok product research, TikTok creator sales, TikTok commission rate, TikTok GMV analysis, FastMoss时触发此技能。即使用户未明确提及"FastMoss"，只要其需求涉及在TikTok平台搜索商品数据或分析商品表现，也应触发此技能。
---

# FastMoss - TikTok Product Search

This skill guides you on how to search and filter TikTok Shop product data using FastMoss, helping sellers and marketers discover product opportunities, evaluate sales performance, and identify influencer-driven products across 15 TikTok markets worldwide.

## Core Concepts

FastMoss is a well-known TikTok e-commerce data platform that tracks product performance across multiple TikTok marketplaces. This tool provides keyword-based product search with rich filtering capabilities, returning detailed product data including multi-period sales (7-day/28-day/90-day/total), GMV (revenue), pricing, ratings, review counts, commission rates, influencer promotion statistics, and shop information.

**Sales metrics**: Products include multi-period sales data — 7-day, 28-day, 90-day, and total sales. The same granularity applies to GMV (Gross Merchandise Value) amounts.

**Commission rate**: Stored as a decimal (e.g., 0.10 means 10%). When displaying to the user, convert to percentage format.

**Shop types**: Products can be filtered by shop type — local shops (1) or cross-border shops (2). The `isCrossBorder` field (1=cross-border, 0=local) and `isSShopText` field (TikTok fully-managed shop) provide additional shop classification.

## Parameter Guide

### Search & Filtering

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword (product title fuzzy match) |
| region | string | No | Market region code. Supported: US, GB, MX, ES, DE, IT, FR, ID, VN, MY, TH, PH, BR, JP, SG |
| category | string | No | Category name in English, matched to TikTok category ID. Non-English should be translated first |
| shopType | integer | No | Shop type: 1=local shop, 2=cross-border shop |

### Boolean Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| isTopSelling | boolean | No | Filter hot-selling products only |
| isNewListed | boolean | No | Filter new products only |
| isSshop | boolean | No | Filter TikTok fully-managed (S-shop) products only |
| isFreeShipping | boolean | No | Filter free-shipping products only |
| isLocalWarehouse | boolean | No | Filter local warehouse products only |

### Range Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| unitsSoldRange | object | No | Sales volume range filter: `{min, max}` |
| commissionRateRange | object | No | Commission rate range filter: `{min, max}` |
| creatorCountRange | object | No | Creator/influencer count range filter: `{min, max}` |

### Sorting & Pagination

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| orderField | string | No | Sort field: day7_units_sold, day7_gmv, commission_rate, total_units_sold, total_gmv, creator_count. Default: descending |
| page | integer | No | Page number, default 1 |
| pageSize | integer | No | Items per page, max 10, default 10 |

### Supported Markets (15)

US (United States), GB (United Kingdom), MX (Mexico), ES (Spain), DE (Germany), IT (Italy), FR (France), ID (Indonesia), VN (Vietnam), MY (Malaysia), TH (Thailand), PH (Philippines), BR (Brazil), JP (Japan), SG (Singapore)

## 调用方式

- **API 端点**：`POST /fastmoss/productSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/fastmoss_product_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-fastmoss-product-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Data Fields

Key fields returned for each product:

| Field | Description |
|-------|-------------|
| title | Product name |
| productId | Unique product identifier |
| region | Market region code |
| price, minPrice, maxPrice | Product price and price range |
| currency | Currency code |
| totalSaleCnt | Total cumulative sales |
| totalSale1dCnt, totalSale7dCnt, totalSale28dCnt, totalSale90dCnt | Sales by period |
| totalSaleGmvAmt, totalSaleGmv7dAmt, totalSaleGmv28dAmt | GMV by period |
| totalVideoCnt, totalLiveCnt, totalIflCnt | Video count, live count, influencer count |
| productCommissionRate | Commission rate (decimal, 0.10 = 10%) |
| productRating, reviewCount | Rating and review count |
| skuCount | Number of SKUs |
| shopName, shopSellerId, shopTotalUnitsSold | Shop information |
| isCrossBorder | 1=cross-border, 0=local |
| isSShopText, freeShippingText | Fully-managed shop flag, free shipping flag |
| salesTrendFlagText | Sales trend label |
| categoryName | Product category |
| tiktokUrl, fastmossUrl, imageUrl | Links and image |

## Usage Examples

**1. Basic Keyword Search — Find top-selling products**
```json
{
  "keyword": "phone case",
  "region": "US",
  "orderField": "total_units_sold",
  "pageSize": 10
}
```

**2. High-Commission Product Discovery — Products with commission >= 10%**
```json
{
  "keyword": "beauty",
  "region": "US",
  "commissionRateRange": {"min": 0.10},
  "orderField": "commission_rate"
}
```

**3. Cross-Border Shop Products — Filter by shop type**
```json
{
  "keyword": "gadget",
  "region": "US",
  "shopType": 2,
  "orderField": "day7_units_sold"
}
```

**4. Influencer-Hot Products — Products promoted by many creators**
```json
{
  "keyword": "skincare",
  "region": "US",
  "creatorCountRange": {"min": 50},
  "orderField": "creator_count"
}
```

**5. Hot-Selling New Products on TikTok**
```json
{
  "keyword": "fashion",
  "region": "GB",
  "isTopSelling": true,
  "isNewListed": true,
  "orderField": "day7_gmv"
}
```

## Display Rules

1. **Present data only**: Show query results in organized tables with key columns — product name, price, total sales, 7-day sales, GMV, rating, commission rate, and number of promoting influencers. Do not make subjective business advice
2. **Commission formatting**: Commission rate is a decimal (0.10 = 10%) — always display as percentage for readability
3. **Cross-border awareness**: `isCrossBorder`: 1 = cross-border shop, 0 = local shop. Display clearly
4. **Currency awareness**: Include the currency field from the response when displaying prices and GMV
5. **Trend labels**: Display `salesTrendFlagText` directly as the trend indicator
6. **Shop flags**: Display `freeShippingText` and `isSShopText` directly (values are readable text)
7. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting parameters

## Important Limitations

- No required parameters (all optional), but at minimum provide keyword or category for meaningful results
- Max 10 items per page

## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Find trending products on TikTok" | Keyword search sorted by sales |
| "TikTok products with high commission" | Filter by commission rate range |
| "What's selling well on TikTok Shop US" | Regional product search by sales |
| "Search TikTok cross-border shop products" | Filter by shopType=2 |
| "Which products have many influencers promoting them" | Filter by creator count range |
| "TikTok fully-managed shop products" | Filter with isSshop=true |
| "TikTok product research for Southeast Asia" | Search specific SE Asian regions |
| "New hot-selling products on TikTok" | Use isTopSelling + isNewListed flags |
| "FastMoss product data" | Direct platform reference |

## Not Applicable Scenarios

- TikTok influencer/creator analytics (follower counts, engagement rates of creators)
- TikTok video performance analytics (views, likes, shares on specific videos)
- TikTok advertising / ad campaign management
- Amazon, Shopee, or other non-TikTok platform product data
- TikTok Shop store-level analytics
- Product listing creation or optimization advice
- Logistics, fulfillment, or shipping analysis

**Boundary judgment**: When users say "product research" or "what should I sell on TikTok", if it involves searching and filtering products by sales data, pricing, or commission rates on TikTok Shop, then this skill applies. If they're asking about content strategy, video creation, or influencer outreach, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
