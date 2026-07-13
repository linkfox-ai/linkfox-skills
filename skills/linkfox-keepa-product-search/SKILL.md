---
name: linkfox-keepa-product-search
description: 基于Keepa数据的亚马逊高级商品搜索与筛选，支持品类、价格、月销量、关键词、BSR排名、评论数、评分、包装尺寸、重量、配送方式等多维度条件。当用户提到Keepa选品、亚马逊商品查找、高级选品、BSR筛选、按销售排名选品、月销量过滤、关键词选品、品类选品、竞品筛选、小众商品发掘、历史排名筛选、Keepa product selection, advanced product selection, BSR filtering, sales filtering, category search, competitor screening, historical data filtering, Amazon product selection时触发此技能。即使用户未明确提及"Keepa"，只要其需求涉及多条件亚马逊商品搜索、按销售指标筛选商品或超越简单关键词搜索的高级选品，也应触发此技能。
---

# Keepa Product Search

This skill guides you on how to search and filter Amazon products using Keepa's extensive product database, helping Amazon sellers find products that match specific criteria across multiple dimensions.

## Core Concepts

This tool provides advanced Amazon product search powered by Keepa data. Unlike a simple Amazon storefront search, it supports multi-criteria filtering: category, price range, monthly sales volume, BSR (Best Sellers Rank), keyword matching (positive and negative), review counts, ratings, package dimensions, weight, fulfillment type, historical sales rank, and more. It returns detailed product data including pricing, titles, images, listing dates, materials, weights, monthly sales for the past 12 months, and more.

**BSR (Best Sellers Rank)**: A lower `salesRank` value means better sales performance. Rank 1 is the best-selling product in its category. When a user says "top-selling products", they want low BSR values.

**Price unit**: Prices are expressed in the smallest currency unit (e.g., cents for USD). So `$25.99` = `2599`. Always convert when building queries and when displaying results.

**Category names**: The `categoriesIncludeNames` parameter supports multi-level category paths separated by a colon `:` or the `>` character. Automatically convert user input into the correct format.

## Parameters

### Marketplace (Required)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| domain | string | Yes | Amazon marketplace ID | - |

**Domain ID mapping:**

| ID | Marketplace |
|----|-------------|
| 1 | Amazon.com (United States) |
| 2 | Amazon.co.uk (United Kingdom) |
| 3 | Amazon.de (Germany) |
| 4 | Amazon.fr (France) |
| 5 | Amazon.co.jp (Japan) |
| 6 | Amazon.ca (Canada) |
| 8 | Amazon.it (Italy) |
| 9 | Amazon.es (Spain) |
| 10 | Amazon.in (India) |
| 11 | Amazon.com.mx (Mexico) |

Default marketplace is **1** (US). Use domain `1` when the user doesn't specify a marketplace.

### Keyword Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | Title keyword filter (case-insensitive; space = AND; wrap phrases in double quotes; prefix with `-` to exclude; `&` is replaced by space; max 50 keywords, max 1000 chars) |

### Category Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| rootCategory | array[int] | Root category IDs (max 50) |
| rootCategoryNames | array[string] | Root category names (max 50); used when rootCategory is empty; system auto-resolves IDs |
| categoriesInclude | array[int] | Sub-category IDs to include (max 50) |
| categoriesIncludeNames | array[string] | Sub-category names to include (max 50); supports full category paths with `:` or `>` separators |
| categoriesExclude | array[int] | Sub-category IDs to exclude (max 50) |
| categoriesExcludeNames | array[string] | Sub-category names to exclude (max 50); supports full category paths |

### Sales & Ranking Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentSalesGte | integer | Current BSR -- minimum (higher number = worse rank) |
| currentSalesLte | integer | Current BSR -- maximum (lower number = better rank) |
| avg90SalesGte | integer | 90-day average BSR -- minimum |
| avg90SalesLte | integer | 90-day average BSR -- maximum |
| deltaPercent90SalesGte | integer | 90-day BSR change percentage -- minimum |
| deltaPercent90SalesLte | integer | 90-day BSR change percentage -- maximum |
| monthlySoldGte | integer | Monthly sales units -- minimum |
| monthlySoldLte | integer | Monthly sales units -- maximum |
| srAvgGte | integer | Historical average BSR -- minimum (for a specific month) |
| srAvgLte | integer | Historical average BSR -- maximum (for a specific month) |
| srAvgMonth | string | Historical BSR month selection (format: YYYYMM, within last 36 months) |

### Price Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentNewGte | integer | Current new price -- minimum (smallest currency unit) |
| currentNewLte | integer | Current new price -- maximum (smallest currency unit) |
| currentBuyBoxShippingGte | integer | Current Buy Box price including shipping -- minimum (smallest currency unit) |
| currentBuyBoxShippingLte | integer | Current Buy Box price including shipping -- maximum (smallest currency unit) |

### Review & Rating Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentCountReviewsGte | integer | Review count -- minimum |
| currentCountReviewsLte | integer | Review count -- maximum |
| currentRatingGte | number | Rating -- minimum (0.0-5.0) |
| currentRatingLte | number | Rating -- maximum (0.0-5.0) |

### Package & Dimensions Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| packageLengthGte / packageLengthLte | integer | Package length range (mm) |
| packageWidthGte / packageWidthLte | integer | Package width range (mm) |
| packageHeightGte / packageHeightLte | integer | Package height range (mm) |
| packageWeightGte / packageWeightLte | integer | Package weight range (grams) |

### Other Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| brand | array[string] | Brand names (OR match) |
| color | array[string] | Colors (OR match) |
| size | array[string] | Sizes (OR match) |
| availableDateGte / availableDateLte | string | Listing date range (yyyy-MM-dd) |
| buyBoxIsAmazon | boolean | Buy Box seller is Amazon |
| buyBoxIsFBA | boolean | Buy Box is FBA fulfilled |
| isHazMat | boolean | Hazardous material flag |
| variationCountGte / variationCountLte | integer | Variation count range |
| currentCountNewGte / currentCountNewLte | integer | Number of new offers range |
| outOfStockPercentage90Gte / outOfStockPercentage90Lte | integer | 90-day out-of-stock percentage range |
| singleVariation | boolean | Return only one variation per parent ASIN |
| productType | array[int] | Product types: 0=standard, 1=downloadable, 2=ebook, 5=variation parent |

### Data Options

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| history | integer | Include historical data (price history, sales rank, monthly sales per month) | 0 (no) |
| rating | integer | Include rating info | 1 (yes) |

### Pagination & Sorting

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| page | integer | Page number (starting from 1) | 1 |
| perPage | integer | Results per page (min 50, max 100) | 50 |
| sort | array[object] | Sort rules (max 3); each object: `{"fieldName": "...", "sortDirection": "asc|desc"}` | - |

**Sortable fields**: `availableDate`, `currentSales`, `monthlySold`, `currentRating`, `currentCountReviews`, `currentBuyBoxShipping`, `currentNew`

## 调用方式

- **API 端点**：`POST /keepa/productSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/keepa_product_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-keepa-product-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## How to Build Queries

Construct the request parameters based on the user's intent:

1. **Determine the marketplace**: Map the user's target country to the correct `domain` ID value
2. **Set keyword filters**: Use `keyword` for title-based filtering with positive and negative terms
3. **Set category scope**: Use `categoriesIncludeNames` or `rootCategoryNames` to scope by category; convert user input into proper category path format
4. **Apply numeric filters**: Map sales volume, price, BSR, review, and rating requirements to the appropriate Gte/Lte parameters
5. **Set sort order**: If the user wants results sorted by sales, price, or rating, configure the `sort` array
6. **Enable historical data**: Set `history` to `1` if the user needs monthly sales trends or price history

### Usage Examples

**1. Search for electronics with monthly sales over 1000 on US marketplace**
```json
{"domain": "1", "rootCategoryNames": ["Electronics"], "monthlySoldGte": 1000}
```

**2. Find products in a price range with good ratings**
```json
{"domain": "1", "currentBuyBoxShippingGte": 1500, "currentBuyBoxShippingLte": 5000, "currentRatingGte": 4.0, "keyword": "wireless charger"}
```

**3. New products listed in the last 6 months with low review counts**
```json
{"domain": "1", "availableDateGte": "2025-10-01", "currentCountReviewsLte": 50, "monthlySoldGte": 500}
```

**4. BSR rank filtering for competitive analysis**
```json
{"domain": "1", "categoriesIncludeNames": ["Home & Kitchen"], "currentSalesLte": 5000, "sort": [{"fieldName": "monthlySold", "sortDirection": "desc"}]}
```

**5. Find non-Amazon FBA products with good sales**
```json
{"domain": "1", "buyBoxIsAmazon": false, "buyBoxIsFBA": true, "monthlySoldGte": 300, "currentRatingGte": 4.0}
```

**6. Lightweight small products for easy shipping**
```json
{"domain": "1", "packageWeightLte": 500, "packageLengthLte": 200, "packageWidthLte": 150, "packageHeightLte": 100, "monthlySoldGte": 200}
```

**7. Search on Japan marketplace with historical data**
```json
{"domain": "5", "keyword": "USB charger", "history": 1, "monthlySoldGte": 100}
```

**8. Brand-specific search excluding hazardous materials**
```json
{"domain": "1", "brand": ["Anker", "UGREEN"], "isHazMat": false, "sort": [{"fieldName": "monthlySold", "sortDirection": "desc"}]}
```

## Display Rules

1. **Present data clearly**: Show search results in well-structured tables with key fields: ASIN, title, price, BSR, monthly sales, rating, review count, brand
2. **Price conversion**: Convert prices from smallest currency unit to standard format (e.g., 2599 -> $25.99)
3. **BSR clarification**: When showing BSR data, remind users that lower values mean better sales ranking
4. **Monthly sales history**: When historical data is included, present the 12-month sales trend clearly
5. **Pagination notice**: Inform users of the total result count and suggest fetching additional pages if needed
6. **Image links**: If image URLs are available, mention them but do not attempt to render them inline unless the user requests it
7. **Error handling**: When a query fails, explain the reason and suggest adjusting filter criteria
## Important Limitations

- **Result cap**: Maximum 100 results per page, minimum 50
- **Sort limit**: Maximum 3 sort rules per query
- **Category limit**: Maximum 50 category IDs or names per filter
- **Keyword limit**: Maximum 50 keywords in keyword parameter
- **Historical data cost**: Setting `history=1` increases response size and token cost significantly
- **Price unit**: All price values are in the smallest currency unit (cents, pence, etc.)

## User Expression & Scenario Quick Reference

**Applicable** -- Multi-criteria Amazon product search and filtering:

| User Says | Scenario |
|-----------|----------|
| "Find products with monthly sales over X" | Sales volume filtering |
| "Search for products in XX category" | Category-based product discovery |
| "Products with BSR under X" | Sales rank filtering |
| "New products listed in the last N months" | New product discovery |
| "Products priced between $X and $Y" | Price range filtering |
| "FBA products with good ratings" | Fulfillment + rating filter |
| "Lightweight products under X grams" | Package dimension filtering |
| "Products from brand XX" | Brand-specific search |
| "Show me historical sales data for XX" | Historical sales analysis |
| "Advanced product selection", "product screening" | Multi-criteria product research |
| "Niche product hunting", "find low-competition products" | Competitive gap analysis |
| "BSR trends", "sales rank history" | Historical rank filtering |

**Not applicable** -- Needs beyond product search:
- Real-time Amazon search result page simulation (use Amazon Search)
- Historical search term volume or ranking trends (use ABA data)
- Product review content or sentiment analysis
- Advertising campaign management or bid optimization
- Listing optimization or copywriting suggestions
- Inventory or supply chain data

**Boundary judgment**: When users say "product research" or "find products", if it involves filtering by sales metrics, BSR, price, category, and other structured criteria, this skill applies. If they want to see what appears on the actual Amazon search page for a keyword, use Amazon Search instead. If they want search term analytics, use ABA data.

## 积分消耗规则

按动态规则计费：消耗积分 = 0.045 × (找商品阶段消耗的 Keepa token + 拉取商品详情阶段消耗的 Keepa token)。先找商品，再拉商品详情；若第一段未找到商品，则只计找商品阶段消耗。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
