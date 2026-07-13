---
name: linkfox-echotik-list-product
description: 搜索和分析TikTok商品数据，包括销量、达人带货数据、定价和佣金比例，覆盖16个TikTok Shop站点。当用户提到TikTok商品搜索、TikTok Shop商品分析、TikTok销量数据、达人带货销售、TikTok选品、TikTok佣金比例、TikTok商品排名、EchoTik数据查询、TikTok product search, TikTok sales, influencer sales, TikTok commission, TikTok product selection, short-video e-commerce, TikTok data时触发此技能。即使用户未明确提及"EchoTik"或"TikTok"，只要其需求涉及在TikTok Shop上搜索商品或分析TikTok商品表现指标，也应触发此技能。
---

# EchoTik TikTok Product Search

This skill guides you on how to search and analyze TikTok Shop product data, helping sellers and marketers discover product opportunities, evaluate sales performance, and identify influencer-driven products on TikTok.

## Core Concepts

EchoTik is a TikTok Shop analytics platform that tracks product performance across multiple TikTok marketplaces. This tool provides keyword-based product search with rich filtering capabilities, returning detailed product data including sales volumes (1d/7d/15d/30d/60d/90d/total), GMV (revenue), pricing, ratings, review counts, commission rates, and influencer promotion statistics.

**Sales metrics**: Products include multi-period sales data — 1-day, 7-day, 15-day, 30-day, 60-day, 90-day, and total sales. The same granularity applies to GMV (Gross Merchandise Value) amounts.

**Commission rate**: Stored as a decimal (e.g., 0.05 means 5%). When a user specifies a percentage, convert it to decimal before passing to the API.

**Listing date**: The `firstCrawlDt` field uses a compact integer format `YYYYMMDD` (e.g., `20240101` for January 1, 2024).

## Parameter Guide

### Search & Filtering

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| keyword | string | Product keyword (translate to the local language of the target marketplace) | - |
| region | string | Marketplace code | US |
| categoryKeywordCN | string | Product category (must be in Chinese) | - |

### Sales Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minTotalSaleCnt / maxTotalSaleCnt | integer | Total sales volume range |
| minTotalSale30dCnt / maxTotalSale30dCnt | integer | 30-day sales volume range |
| minTotalSaleGmvAmt / maxTotalSaleGmvAmt | string | Total GMV range |
| minTotalSaleGmv30dAmt / maxTotalSaleGmv30dAmt | string | 30-day GMV range |

### Product Attribute Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minSpuAvgPrice / maxSpuAvgPrice | number | SPU average price range |
| minProductRating / maxProductRating | number | Product rating range |
| minReviewCount / maxReviewCount | integer | Review count range |
| minProductCommissionRate / maxProductCommissionRate | number | Commission rate range (decimal, e.g., 0.05 = 5%) |

### Influencer & Video Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minTotalIflCnt / maxTotalIflCnt | integer | Number of influencers promoting the product |
| minTotalVideoCnt / maxTotalVideoCnt | integer | Number of promotion videos |
| minTotalViewsCnt / maxTotalViewsCnt | integer | Total views on promotion videos |

### Listing Date & Duration

| Parameter | Type | Description |
|-----------|------|-------------|
| minFirstCrawlDt / maxFirstCrawlDt | integer | Listing date range (YYYYMMDD format, e.g., 20240101) |
| saleDays | integer | Days since listing |

### Sorting & Pagination

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| productSortField | integer | Sort field: 1=total sales, 2=total GMV, 3=avg price, 4=7d sales, 5=30d sales, 6=7d GMV, 7=30d GMV | 1 |
| sortType | integer | Sort order: 0=ascending, 1=descending | 1 |
| pageNum | integer | Page number | 1 |
| pageSize | integer | Results per page | 50 |

### Supported Marketplaces

US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France)

Default marketplace is **US**. Use US when the user doesn't specify a marketplace.

## 调用方式

- **API 端点**：`POST /echotik/listProduct`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/echotik_list_product.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-list-product-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Basic Keyword Search — Find top-selling products for a keyword**
```json
{
  "keyword": "phone case",
  "region": "US",
  "productSortField": 1,
  "sortType": 1,
  "pageSize": 20
}
```

**2. High-Commission Product Discovery — Products with commission >= 10%**
```json
{
  "keyword": "beauty",
  "region": "US",
  "minProductCommissionRate": 0.10,
  "productSortField": 5,
  "sortType": 1
}
```

**3. New & Trending Products — Recently listed with strong 30-day sales**
```json
{
  "keyword": "gadget",
  "region": "US",
  "minFirstCrawlDt": 20250101,
  "minTotalSale30dCnt": 1000,
  "productSortField": 5,
  "sortType": 1
}
```

**4. Influencer-Hot Products — Products promoted by many influencers**
```json
{
  "keyword": "skincare",
  "region": "US",
  "minTotalIflCnt": 50,
  "minTotalViewsCnt": 1000000,
  "productSortField": 1,
  "sortType": 1
}
```

**5. Budget-Friendly High-Sellers — Low price + high volume**
```json
{
  "keyword": "accessories",
  "region": "US",
  "maxSpuAvgPrice": 10,
  "minTotalSaleCnt": 5000,
  "productSortField": 2,
  "sortType": 1
}
```

**6. Southeast Asia Market Exploration**
```json
{
  "keyword": "fashion",
  "region": "TH",
  "minTotalSale30dCnt": 500,
  "productSortField": 7,
  "sortType": 1
}
```

## Display Rules

1. **Present data clearly**: Show query results in organized tables with key columns — product name, price, total sales, 30-day sales, GMV, rating, commission rate, and number of promoting influencers
2. **Currency awareness**: Include the currency field from the response when displaying prices and GMV
3. **Commission formatting**: Display commission rates as percentages for readability (e.g., show 0.05 as "5%")
4. **Volume notice**: When results have a large `total` count, show the current page data and inform the user of total available records; suggest adjusting filters or pagination to explore more
5. **Image reference**: If `imageUrl` or `coverUrl` is present, mention it so the user knows product images are available
6. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting parameters
7. **Keyword translation reminder**: When the user targets a non-English marketplace, remind them that the keyword should be in the local language of that marketplace for best results
## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Find trending products on TikTok" | Keyword search sorted by sales |
| "TikTok products with high commission" | Filter by commission rate |
| "What's selling well on TikTok Shop US" | Regional product search by sales |
| "New products blowing up on TikTok" | Filter by listing date + sales |
| "Which products have many influencers promoting them" | Filter by influencer count |
| "Cheap but high-volume TikTok products" | Filter by price + sales |
| "TikTok product research for Southeast Asia" | Search specific SE Asian regions |
| "Products with good reviews on TikTok" | Filter by rating + review count |

## Not Applicable Scenarios

- TikTok influencer/creator analytics (follower counts, engagement rates of creators)
- TikTok video performance analytics (views, likes, shares on specific videos)
- TikTok advertising / ad campaign management
- Amazon, Shopee, or other non-TikTok platform product data
- TikTok Shop store-level analytics
- Product listing creation or optimization advice
- Logistics, fulfillment, or shipping analysis

**Boundary judgment**: When users say "product research" or "what should I sell on TikTok", if it involves searching and filtering products by sales data, pricing, or commission rates on TikTok Shop, then this skill applies. If they're asking about content strategy, video creation, or influencer outreach, it does not apply.

## 积分消耗规则

消耗 4.5 积分。

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
