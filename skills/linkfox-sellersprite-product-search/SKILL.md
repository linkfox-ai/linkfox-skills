---
name: linkfox-sellersprite-product-search
description: 使用卖家精灵数据搜索和筛选亚马逊商品，支持价格、月销量、BSR排名、毛利率、评分、配送方式、标签、卖家来源等多维度条件，覆盖多个亚马逊站点。当用户提到亚马逊选品调研、产品筛选、销量过滤、产品发掘、BSR分析、小众商品发现、竞品分析、市场机会评估、按商品维度的市场规模估算、毛利率筛选、SellerSprite product selection, Amazon product selection, sales filtering, BSR analysis, profit screening, market analysis, product selection tool时触发此技能。即使用户未明确提及"卖家精灵"，只要其需求涉及筛选和分析亚马逊商品级数据进行选品，也应触发此技能。
---

# SellerSprite Product Search

This skill guides you on how to search, filter, and analyze Amazon product data via the SellerSprite product database, helping Amazon sellers make data-driven product selection decisions.

## Core Concepts

SellerSprite Product Search provides access to a comprehensive Amazon product database with rich filtering dimensions. It supports real-time data (last 30 days) as well as monthly historical snapshots for year-over-year and month-over-month comparisons. Supported `marketplace` codes are **only**: US, UK, DE, FR, JP, CA, IT, ES, MX, and IN (same as the gateway schema).

**BSR (Best Sellers Rank)**: A lower BSR value means better sales performance in its category. A BSR of 1 means the top-selling product in that category. When a user says "BSR improved", it means the numeric value decreased; "BSR dropped" means the value increased.

**Data snapshot**: The `dataSnapshotMonth` parameter controls which time period to query. Use `nearly` (the default) for real-time last-30-day data, or a `yyyyMM` string (e.g., `202412`) to query a historical monthly snapshot. This is useful for seasonal analysis and year-over-year comparison.

**Match types for keywords**: When searching by keyword, three matching strategies are available:
- **Phrase match** (default): Product titles must contain the keyword phrase
- **Fuzzy match**: Broader matching with related terms
- **Exact match**: Strict exact-string matching

## Parameter Guide

### Search & Filtering

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| keyword | string | Search keyword; translate to the target marketplace language (e.g., English for US, German for DE) | - |
| matchType | integer | 1 = Phrase match, 2 = Fuzzy match, 3 = Exact match | 1 |
| excludeKeywords | string | Keywords to exclude from results | - |
| marketplace | string | Marketplace code (allowed set only): US, UK, DE, FR, JP, CA, IT, ES, MX, IN | US |
| nodeLabel | string | Amazon category name | - |
| nodeIdPath | string | Amazon category node ID | - |
| filterSubNode | boolean | Whether to filter by subcategory node (only effective when nodeLabel or nodeIdPath is set) | - |
| dataSnapshotMonth | string | Data snapshot month in `yyyyMM` format, or `nearly` for real-time last 30 days | nearly |

### Price & Financials

| Parameter | Type | Description |
|-----------|------|-------------|
| minPrice / maxPrice | number | Price range filter |
| minProfit / maxProfit | number | Gross margin range (1-100, unit: %) |
| minRevenue / maxRevenue | number | Monthly revenue range |
| minFba / maxFba | number | FBA fee range |

### Sales & Ranking

| Parameter | Type | Description |
|-----------|------|-------------|
| minUnits / maxUnits | integer | Monthly sales volume range |
| minAmzUnit / maxAmzUnit | integer | Child-ASIN last-30-day sales range (**only** when querying last-30-day style data, e.g. `dataSnapshotMonth: "nearly"`) |
| minUnitsGrowthRate / maxUnitsGrowthRate | number | Monthly sales growth rate (%) |
| minBsr / maxBsr | integer | Main-category BSR rank range |
| minBsrGrowthRate / maxBsrGrowthRate | number | BSR growth rate (%) |
| minBsrGrowthCount / maxBsrGrowthCount | integer | BSR growth count |
| minSubNodeBsrRank / maxSubNodeBsrRank | integer | Subcategory BSR rank (requires filterSubNode = true) |

### Reviews & Ratings

| Parameter | Type | Description |
|-----------|------|-------------|
| minRating / maxRating | number | Rating score range (0-5); 3.8-4.3 indicates product improvement opportunity |
| minRatings / maxRatings | integer | Number of ratings range (0-10000) |
| minRatingsGrowthCount / maxRatingsGrowthCount | integer | Monthly new ratings count |
| minListingQualityScore / maxListingQualityScore | number | Listing quality score range |

### Product Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| minVariations / maxVariations | integer | Variation count range |
| minWeights / maxWeights | number | Weight range |
| weightUnit | string | Weight unit: g, kg, oz, lb (required if weight filters are used) |
| dimensionType | string | Package dimension type (marketplace-specific codes) |
| minSellers / maxSellers | integer | Number of sellers range |

### Badges & Fulfillment

| Parameter | Type | Description |
|-----------|------|-------------|
| badgeBestSeller | string | Best Seller badge: Y / N / empty (all) |
| badgeAmazonsChoice | string | Amazon's Choice badge: Y / N / empty (all) |
| badgeNewRelease | string | New Release badge: Y / N / empty (all) |
| fulfillment | string | Fulfillment type: AMZ, FBA, FBM (comma-separated for multiple) |
| showVariation | string | Show variations: Y / N (default N) |

### Seller & Brand

| Parameter | Type | Description |
|-----------|------|-------------|
| sellerNation | string | Seller country code (e.g., US, CN, HK); comma-separated for multiple |
| includeSellers / excludeSellers | string | Include / exclude specific sellers |
| includeBrands / excludeBrands | string | Include / exclude specific brands |

### Listing & Pagination

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| hideUnlistedProduct | boolean | Hide delisted products | true |
| listedWithinLastMonths | integer | Listed within last N months (1, 3, 6, 12, or 24) | - |
| page | integer | Page number, starting from 1 | 1 |
| size | integer | Results per page (10-100) | 20 |

### Sorting

Use the `order` object with two fields:

| Field | Type | Description |
|-------|------|-------------|
| field | string | Sort field: total_units, total_amount, bsr_rank, price, rating, reviews, profit, reviews_rate, available_date, questions, total_units_growth, total_amount_growth, reviews_increasement, bsr_rank_cv, bsr_rank_cr, amz_unit; use `""` when you intentionally omit a business sort key (per gateway schema) |
| desc | string | `"true"` for descending, `"false"` for ascending |

Default sort: `total_units` descending.

### Optional gateway / session fields

If the hosting environment supplies them, you may pass `chatId`, `uid`, `requestId`, and `teamId` as strings (see `references/api.md`). They are not required for ad-hoc script calls.

## 调用方式

- **API 端点**：`POST /sellersprite/productSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sellersprite_product_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-product-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Find high-sales products in a niche**
Search for products with keyword "yoga mat" in the US marketplace with monthly sales above 500 units, sorted by monthly sales descending.
```json
{
  "keyword": "yoga mat",
  "marketplace": "US",
  "minUnits": 500,
  "order": {"field": "total_units", "desc": "true"}
}
```

**2. Discover new product opportunities with low competition**
Find recently listed products (within 6 months) in the US with fewer than 50 ratings and monthly revenue above $5,000.
```json
{
  "keyword": "desk organizer",
  "marketplace": "US",
  "listedWithinLastMonths": 6,
  "maxRatings": 50,
  "minRevenue": 5000,
  "order": {"field": "total_units", "desc": "true"}
}
```

**3. Product improvement opportunity mining**
Find products with ratings between 3.8 and 4.3 (improvement sweet spot), monthly sales above 300, in a specific category.
```json
{
  "keyword": "phone case",
  "marketplace": "US",
  "minRating": 3.8,
  "maxRating": 4.3,
  "minUnits": 300,
  "order": {"field": "total_units", "desc": "true"}
}
```

**4. High-margin product screening**
Find products with gross margin above 40%, price between $15 and $50, at least 100 monthly sales.
```json
{
  "marketplace": "US",
  "minProfit": 40,
  "minPrice": 15,
  "maxPrice": 50,
  "minUnits": 100,
  "order": {"field": "profit", "desc": "true"}
}
```

**5. Seasonal year-over-year comparison**
Query last year's December snapshot data to compare with current data for seasonal product planning.
```json
{
  "keyword": "christmas lights",
  "marketplace": "US",
  "dataSnapshotMonth": "202412",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**6. Chinese seller competitive landscape**
Find FBA-fulfilled products from Chinese sellers in a category with high monthly sales.
```json
{
  "keyword": "bluetooth speaker",
  "marketplace": "US",
  "sellerNation": "CN",
  "fulfillment": "FBA",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**7. Best Seller & Amazon's Choice badge holders**
Find products carrying the Best Seller badge with strong sales performance.
```json
{
  "keyword": "water bottle",
  "marketplace": "US",
  "badgeBestSeller": "Y",
  "order": {"field": "total_units", "desc": "true"}
}
```

**8. Fast-growing products by sales growth rate**
Find products with monthly sales growth rate above 50%.
```json
{
  "keyword": "standing desk",
  "marketplace": "US",
  "minUnitsGrowthRate": 50,
  "order": {"field": "total_units_growth", "desc": "true"}
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Key columns to prioritize: ASIN, title, price, monthly sales, monthly revenue, BSR rank, rating, ratings count, gross margin, fulfillment type
2. **BSR clarification**: When showing BSR data, remind users that lower values mean better rankings
3. **Gross margin note**: Gross margin values are percentages. Remind users this is an estimate based on price minus FBA fees and estimated costs
4. **Pagination awareness**: When the total count exceeds the returned page size, inform the user of the total result count and suggest adjusting page or size parameters to see more results
5. **Snapshot labeling**: When displaying historical snapshot data, clearly label the data period (e.g., "Data from December 2024 snapshot") to avoid confusion with real-time data
6. **Error handling**: When a query fails, explain the reason based on the `message` field and suggest adjusting query criteria
7. **Weight unit reminder**: When the user provides weight filters without specifying a unit, ask them to confirm the weight unit (g, kg, oz, or lb) before proceeding
8. **Keyword translation**: When the user provides keywords in a language different from the target marketplace, translate the keyword to the appropriate language and note the translation
## Important Limitations

- **Result cap**: Each page returns a maximum of 100 records (size parameter max is 100)
- **Historical snapshots**: Only past monthly snapshots are available; future dates are not supported
- **Weight unit required**: If any weight filter is used, the `weightUnit` must also be provided
- **Subcategory BSR**: The subcategory BSR rank filters only work when `filterSubNode` is set to `true`
- **Listed time enum only**: The `listedWithinLastMonths` parameter only accepts specific values: 1, 3, 6, 12, or 24
- **Child ASIN 30-day sales filters**: `minAmzUnit` / `maxAmzUnit` apply only to last-30-day style queries (typically `dataSnapshotMonth: "nearly"`); do not rely on them for historical `yyyyMM` snapshots

## User Expression & Scenario Quick Reference

**Applicable** -- Product-level data queries on Amazon:

| User Says | Scenario |
|-----------|----------|
| "Find products with high sales in XX category" | Niche product search |
| "Show me low-competition products", "new product opportunities" | Blue ocean product discovery |
| "Which products have high margins" | Profitability screening |
| "Products with rising sales", "trending products" | Growth trend detection |
| "What are Chinese sellers selling well" | Competitive landscape analysis |
| "Recently launched products doing well" | New product tracking |
| "Products with bad reviews but good sales" | Product improvement opportunities |
| "Compare this category with last year" | Seasonal / YoY analysis |
| "FBA products under $30 with 1000+ sales" | Multi-criteria product filtering |
| "Best sellers in XX category" | Badge-based product discovery |

**Not applicable** -- Needs beyond product-level search data:
- ABA search term / keyword analysis (use ABA Data Explorer instead)
- Advertising / PPC campaign data
- Product review text analysis
- Listing copywriting or optimization
- Supplier sourcing or manufacturing costs
- Logistics and inventory planning

**Boundary judgment**: When users say "product research" or "market analysis", if it boils down to filtering Amazon products by sales, price, BSR, ratings, and other product attributes, then this skill applies. If they are asking about keyword search volume, search term rankings, or click/conversion share data, the ABA Data Explorer skill is more appropriate.

## 积分消耗规则

消耗 15 积分。

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
