---
name: linkfox-walmart-search
description: 按关键词、品类、价格区间等条件搜索和浏览沃尔玛商品listing。当用户提到Walmart商品搜索、沃尔玛商品listing、沃尔玛价格对比、沃尔玛竞品分析、沃尔玛选品调研、沃尔玛市场数据、在沃尔玛上查找商品、Walmart search, Walmart products, Walmart product selection, Walmart pricing, Walmart competitors, Walmart market时触发此技能。即使用户未明确提及"Walmart搜索"，只要其需求涉及在沃尔玛上搜索商品、查看商品可售状态、对比沃尔玛价格或分析沃尔玛商品listing，也应触发此技能。
---

# Walmart Product Search

This skill enables you to search and retrieve Walmart product listing data, helping e-commerce sellers and researchers extract actionable insights from Walmart's marketplace.

## Core Concepts

Walmart Product Search retrieves real-time product listing data from Walmart's marketplace. It supports keyword-based search, category browsing, price filtering, sorting options, and device-specific results. This is a direct search tool that returns current product listings as they appear on Walmart.com.

**Search modes**: You can search by keyword, by category ID, or by combining both. At least one of `keyword` or `categoryId` must be provided.

**Sorting options**: Results can be sorted by `best_seller`, `best_match`, `price_low` (price ascending), or `price_high` (price descending). When no sort is specified, the default relevance-based ranking applies.

**Pagination**: Results are paginated with a default of page 1. The maximum page number is 100.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No* | Search keyword (max 1024 chars). *At least one of keyword or categoryId must be provided |
| categoryId | string | No* | Category ID for browsing. *At least one of keyword or categoryId must be provided. Use `0` for all departments |
| sort | string | No | Sort order: `best_seller`, `best_match`, `price_low`, `price_high` |
| page | integer | No | Page number (1-100, default 1) |
| minPrice | number | No | Minimum price filter |
| maxPrice | number | No | Maximum price filter |
| spelling | boolean | No | Enable spelling correction (default true) |
| softSort | boolean | No | Sort by relevance (default true). Set to false to disable |
| storeId | string | No | Store ID for store-specific results |
| device | string | No | Device type: `desktop` (default), `tablet`, `mobile` |
| facet | string | No | Filter facets in `key:value` format, separated by `\|\|` |
| nextDayEnabled | boolean | No | Show only NextDay delivery results (default false) |
| jsonRestrictor | string | No | JSON field restrictor to limit returned fields |

## Product Data Fields

| Field | Description |
|-------|-------------|
| productId | Walmart product ID |
| usItemId | US item ID |
| title | Product title |
| description | Product description |
| price | Current price |
| wasPrice | Original price before discount |
| currency | Currency code |
| minPrice | Minimum price (for multi-option products) |
| pricePerUnitAmount | Per-unit price amount |
| pricePerUnit | Per-unit price label |
| rating | Average rating score |
| reviews | Total number of reviews |
| sellerName | Seller name |
| sellerId | Seller ID |
| imageUrl | Product thumbnail URL |
| productPageUrl | Product detail page URL |
| sponsored | Whether the listing is a sponsored ad |
| outOfStock | Whether the product is out of stock |
| freeShipping | Whether free shipping is available |
| twoDayShipping | Whether two-day shipping is available |
| freeShippingWithWalmartPlus | Free shipping with Walmart Plus membership |
| shippingPrice | Shipping cost |
| multipleOptionsAvailable | Whether the product has multiple variants |
| variantSwatches | List of variant options with names and images |

## Usage Examples

**1. Basic keyword search**
Search for products matching a keyword:
```json
{"keyword": "wireless earbuds"}
```

**2. Price-filtered search**
Find products within a specific price range:
```json
{"keyword": "laptop stand", "minPrice": 10, "maxPrice": 50}
```

**3. Best sellers in a category**
Browse top-selling products sorted by popularity:
```json
{"keyword": "coffee maker", "sort": "best_seller"}
```

**4. Budget shopping -- lowest price first**
Find the cheapest options for a product:
```json
{"keyword": "phone case", "sort": "price_low"}
```

**5. Category browsing with pagination**
Browse a specific category across multiple pages:
```json
{"categoryId": "976759_976787", "page": 2}
```

**6. Store-specific inventory check**
Search products available at a specific Walmart store:
```json
{"keyword": "tent", "storeId": "1862"}
```

**7. Mobile results simulation**
See results as they appear on mobile devices:
```json
{"keyword": "water bottle", "device": "mobile"}
```

**8. Combined filters**
Apply multiple filters for precise results:
```json
{"keyword": "running shoes", "minPrice": 30, "maxPrice": 80, "sort": "best_match"}
```

## Display Rules

1. **Present data clearly**: Show search results in well-structured tables with key fields (title, price, rating, reviews, seller). Do not add subjective buying recommendations unless the user asks for analysis.
2. **Price formatting**: Always display prices with the currency symbol. When `wasPrice` is present, show both current and original prices to highlight discounts.
3. **Rating context**: Display ratings alongside review counts so users can judge credibility (e.g., "4.5 stars from 1,230 reviews").
4. **Stock status**: Clearly flag out-of-stock items so users do not overlook availability issues.
5. **Sponsored labeling**: Mark sponsored products so users can distinguish organic from paid placements.
6. **Pagination guidance**: When results have a large total count, inform the user of the total and suggest paginating with the `page` parameter to see more.
7. **Error handling**: When a query fails, explain the error clearly and suggest adjusting parameters (e.g., broadening the keyword, changing filters).
8. **Product links**: When showing results, include `productPageUrl` so users can navigate directly to the Walmart product page.
## User Expression & Scenario Quick Reference

**Applicable** -- Walmart product listing queries:

| User Says | Scenario |
|-----------|----------|
| "Search Walmart for XX" | Keyword search |
| "Find cheap XX on Walmart" | Price-filtered search |
| "What's the best-selling XX on Walmart" | Best-seller sort |
| "Compare prices for XX on Walmart" | Price comparison |
| "Is XX in stock at Walmart" | Availability check |
| "Show me Walmart products under $50" | Price-range browse |
| "What are the top-rated XX on Walmart" | Rating-based filtering |
| "Walmart competitor products for XX" | Competitive research |

**Not applicable** -- Needs beyond Walmart product listings:
- Walmart seller account management or advertising
- Walmart order tracking or purchase history
- Product reviews text analysis (only rating/count is available)
- Historical price tracking or price trend analysis
- Walmart affiliate or API key management

**Boundary judgment**: When users say "product research" or "competitor analysis" in the context of Walmart, if their need involves searching for current product listings, prices, ratings, or seller information, then this skill applies. If they are asking about advertising strategy, account metrics, or historical sales data, it does not apply.


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
