---
name: linkfox-seerfar-ozon-product-report-search
description: Seerfar Ozon 商品报表搜索：按销量、销售额、销量/销售额增长率、购物车转化率、下单转化率、价格、评分、评论数、QA数、变体数、浏览量、毛利率、退货取消率、广告费用份额、重量/体积、上架时间、品牌、卖家、配送方式、标签等多维指标筛选 Ozon 商品，返回每个商品的 SKU、标题、价格（卢布）、销量、销售额、损失销售额、转化率、评分、评论、品牌、卖家、配送方式、上架天数/月数等完整商品报表字段，用于 Ozon 选品、竞品商品分析、热销商品挖掘、价格带/转化带筛选。当用户提到 Ozon 商品报表、Ozon 选品、Ozon 商品筛选、Ozon 商品分析、Ozon 热销商品、Ozon 竞品商品分析、Ozon product report, Ozon product screener, filter Ozon products by sales, Ozon best-seller mining, Seerfar Ozon 商品报表时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是按多指标筛选 Ozon 商品并查看商品级报表，也应触发此技能。
---

# Seerfar Ozon Product Report Search

This skill searches the Seerfar Ozon product database and filters products by rich performance metrics — monthly sales, revenue, growth, cart/order conversion, price, rating, reviews, brand, seller, fulfillment model, listing age, gross margin, and more. Each returned row is a full product-report record, making this the starting point for Ozon product selection (选品), competitor product analysis, best-seller mining, and price/conversion-band screening.

## Core Concepts

**Unit of data is the product, not the keyword**: this endpoint returns product-level rows (one per SKU), each enriched with full report metrics. You discover *which products* match your criteria — unlike the market-keyword endpoint, which returns search terms.

**This is a product screener / 商品报表**: filter the Ozon product database by metric ranges (`{min, max}`), not only by keyword/brand/seller. Stack a high `monthlySales` floor with a low `price` ceiling to surface affordable high-volume products, or qualify conversion quality with a high `convToCartPdp` floor and a low `returnCancellationRate` ceiling; sort by `sales` DESC to mine best-sellers.

**Unified vs raw duplicate fields**: the response carries six alias pairs that hold the same value under two keys — `sku`/`productId`, `sales`/`monthlySalesUnits`, `revenue`/`monthlySalesRevenue`, `reviewRating`/`rating`, `brandName`/`brand`, `productUrl`/`productPageUrl`. Read either; do not expect them to differ.

**Date semantics**: `searchDate` selects the data month. Pass `2026-04-01` for March 2026 data; omit it for the last 30 days. Sales/revenue figures are relative to the selected period.

**`data` and `products` are identical**: both top-level arrays carry the same product rows. `total` is the total matching count (e.g. ~27.8M with no filter, 1 when filtering to a single SKU).

**Ozon only**: `sourceType` is fixed to `ozon`. `fulfillment` values are `OZON`, `FBO`, `FBS`, `RFBS`, `FBP`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | object | yes | Pagination + sort: `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| skus | array<int> | no | SKU list to restrict to (max 10). |
| keywords | array<string> | no | Keyword list to filter product titles. |
| categoryIds | array<string> | no | Seerfar category ID list. |
| sellerName | array<string> | no | Seller name list. |
| brand | object | no | `{brandName: array<string>, type: int}`. `type`: `0` include, `1` exclude, `2` no brand. |
| fulfillment | array<string> | no | Fulfillment filter: `OZON`/`FBO`/`FBS`/`RFBS`/`FBP`. |
| labels | array<int> | no | Badge filter: `0` new, `1` authentic, `2` best-seller. |
| creationDate | integer | no | Listing-age filter (months): `1`/`3`/`6`/`12`/`24`. |
| variationsMerge | integer | no | Merge variants: `0` no, `1` yes. |
| searchDate | string | no | Data date `yyyy-MM-dd`; default last 30 days. `2026-04-01` → March 2026. |
| tag | string | no | Tag word. |
| monthlySales | {min,max} | no | Monthly sales range. |
| monthlySalesRate | {min,max} | no | Sales growth-rate range (filters `salesRate`). |
| monthlyRevenue | {min,max} | no | Monthly revenue range. |
| price | {min,max} | no | Price range (RUB). |
| convToCartPdp | {min,max} | no | Cart conversion rate range. |
| reviewRating | {min,max} | no | Rating range. |
| reviewCount | {min,max} | no | Review count range. |
| questionsAndAnswers | {min,max} | no | Q&A count range. |
| variants | {min,max} | no | Variant count range. |
| drr | {min,max} | no | Ad-cost share range. |
| grossMargin | {min,max} | no | Gross margin range. |
| returnCancellationRate | {min,max} | no | Return/cancellation rate range. |
| weight | {min,max} | no | Weight range (g). |
| volume | {min,max} | no | Volume range (L). |
| uId / memberId | string | no | User / member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. Only `page` is required.

## 调用方式

- **API 端点**：`POST /seerfar/ozon/productReportSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_product_report_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-product-report-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Top sellers right now (sort by sales)**
```json
{"page": {"page": 1, "pageSize": 10, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**2. Blue-ocean products — high sales, low price band**
```json
{"page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}, "monthlySales": {"min": 5000}, "price": {"max": 500}}
```

**3. Best-sellers in a category, FBO fulfillment**
```json
{"page": {"page": 1, "pageSize": 20, "orders": [{"field": "revenue", "direction": "DESC"}]}, "categoryIds": ["15621031_200000933_93182"], "fulfillment": ["FBO"], "labels": [2]}
```

**4. New listings from the last 30 days, sorted by growth**
```json
{"page": {"page": 1, "pageSize": 20, "orders": [{"field": "salesRate", "direction": "DESC"}]}, "creationDate": 1}
```

**5. Look up specific SKUs**
```json
{"page": {"page": 1, "pageSize": 10}, "skus": [2107989735]}
```

## How to Build Queries

1. **Lead with `page.orders`**: the dataset is huge (tens of millions of products) — always sort by the metric you care about (`sales` DESC for best-sellers, `salesRate` DESC for rising products, `price` ASC for cheap volume, `reviewRating` DESC for well-reviewed).
2. **Stack range filters to find opportunities**: combine a `monthlySales` floor with a `price` ceiling, or a `convToCartPdp` floor with a low `returnCancellationRate`, to qualify demand-vs-risk.
3. **Scope with `categoryIds` / `brand` / `sellerName`**: narrow to a niche before sorting, so the top rows are relevant.
4. **Use `creationDate` + `labels` for fresh demand**: `creationDate: 1` (new listings) paired with `labels: [2]` (best-seller badge) finds breakout products.
5. **Pick the right `searchDate`**: omit for current trends (last 30 days); pass an explicit date for month-over-month comparison.

## Display Rules

1. **Present data only**: show product metrics in a clear table without subjective advice.
2. **Lead with product columns**: `title`, `sku`, `price` (₽), `sales`, `revenue`, `rating`, `reviewCount`, then `brand` / `sellerName` / `fulfillment`.
3. **Currency**: `price`/`revenue`/`missedRevenue` are in Russian rubles (₽); show the currency so scale is not misread.
4. **Unified/raw aliases**: prefer the unified fields (`productId`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `brand`, `productPageUrl`) or note they equal the raw ones — do not present both as if independent.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting filters or retrying (rate-limit `1003`).

## Important Limitations

- **`page` is required**: a payload without `page` is rejected.
- **`skus` cap**: at most 10 SKUs per request.
- **Category IDs are opaque**: `categoryIds` requires Seerfar category IDs (from a category search), not human-readable names.
- **Duplicate alias pairs**: six fields are duplicated under raw + unified keys (see Core Concepts) — same value, two keys.
- **`total` is the full match count**: with no filter it can reach tens of millions; always sort and page rather than iterating blindly.
- **Rate limiting**: `errcode 1003` ("请求过于频繁，请稍后再试") means throttle — wait and retry rather than lowering `pageSize`.
- **Sort fields**: valid `orders[].field` values are the response metric fields (e.g. `sales`, `revenue`, `price`, `reviewRating`, `reviewCount`, `salesRate`); the `columns` array marks which are sortable.

## User Expression & Scenario Quick Reference

**Applicable** — Ozon product-level screening:

| User Says | Scenario |
|-----------|----------|
| "Ozon 选品 / 按销量销售额筛选商品" | Product screener (range filters + sort) |
| "Ozon 热销商品 / 畅销品" | Best-seller mining (`labels:[2]` or sort `sales` DESC) |
| "Ozon 上升商品 / 新品爆款" | Rising/new products (`creationDate:1`, sort `salesRate` DESC) |
| "Ozon 高转化低退货商品" | Conversion-quality screen (`convToCartPdp` min, `returnCancellationRate` max) |
| "Ozon 某品牌/卖家商品表现" | Brand/seller filter + sort |
| "查这几个 SKU 的报表" | `skus` lookup |

**Not applicable** — Needs beyond product-level reports:
- Keyword market data (search terms, search volume) → market-keyword-search.
- Keyword expansion around a seed term → keyword-mining.
- A specific shop's full catalog → shop-search.
- A category's products with category-level aggregates → category-search.
- Reverse keyword lookup for a product → keyword-back-search.
- Non-Ozon marketplaces → not covered here.

**Boundary judgment**: if the user wants to **screen Ozon products by metrics and read product-level report rows**, start here. If they want keyword-level market data, a single shop's catalog, or a category aggregate, route to the corresponding Seerfar Ozon data source.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
