---
name: linkfox-seerfar-ozon-market-keyword-search
description: Seerfar Ozon 市场热词搜索：按搜索热度、增长、商品数、卖家数、竞品数、价格、销量、转化集中度等多维指标筛选 Ozon（及 Wildberries）市场关键词，返回每个关键词的月搜热度、增长、市场空间、竞品/卖家数、均价、加购转化、Top 商品等市场画像，用于 Ozon 选词、蓝海词挖掘与市场机会分析。当用户提到 Ozon 热词、Ozon 关键词市场分析、Ozon 选词、Ozon 蓝海词、Ozon 搜索热度、Wildberries 关键词、Seerfar Ozon、Ozon market keyword search, Ozon keyword research, blue ocean keywords Ozon 时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是按指标筛选 Ozon 市场关键词并查看市场画像，也应触发此技能。
---

# Seerfar Ozon Market Keyword Search

This skill searches Ozon marketplace keywords in the Seerfar analytics database and filters them by rich performance metrics — search volume, 30-day growth, product/seller/competitor counts, average price, monthly sales/revenue, conversion & view concentration, ratings/reviews, and more. Each returned keyword carries a full market profile (market space, return/cancellation rate, top products, Chinese translation), making it the starting point for Ozon keyword selection, blue-ocean term mining, and market-opportunity analysis.

## Core Concepts

**Unit of data is the keyword, not the SKU**: unlike a product search, this endpoint returns marketplace search terms ("热词"), each enriched with market metrics. You discover *which search terms* are worth targeting on Ozon.

**Platform coverage**: each keyword record carries a `platform` field (`0` = Ozon, `1` = Wildberries). The dataset is Ozon-centric; Wildberries rows appear where available. There is no input to restrict the platform — filter client-side if needed.

**Date semantics**: `searchDate` selects the data month. Pass `2026-04-01` to get March 2026 data; omit it for the last 30 days. Metrics such as `searchVolume` (月搜热度) and `count30GrowthRate` (月搜增长) are relative to the selected period.

**Match mode**: `matchType` controls how the `keywords` array is matched — `0` exact, `1` fuzzy. Choose the mode that fits your discovery intent when filtering by keyword text.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | object | yes | Pagination `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| keywords | array<string> | no | Keyword list to filter (max 1000); combined with `matchType`. |
| matchType | integer | no | Keyword match mode: `0` exact, `1` fuzzy. |
| searchDate | string | no | Data date `yyyy-MM-dd`; default last 30 days. `2026-04-01` → March 2026 data. |
| categories | array<string> | no | Category ID list (max 1000). |
| searchVolume | {min,max} | no | Monthly search volume range. |
| searchChange30 | {min,max} | no | 30-day search change range. |
| monthlySales | {min,max} | no | Monthly sales range. |
| monthlyRevenue | {min,max} | no | Monthly revenue range. |
| price | {min,max} | no | Average price range. |
| productViews | {min,max} | no | Product view range. |
| products | {min,max} | no | Product count range. |
| volume | {min,max} | no | Volume range. |
| marketSpace | {min,max} | no | Market space range. |
| conversionSharing | {min,max} | no | Conversion concentration range. |
| reviews | {min,max} | no | Review count range. |
| ratings | {min,max} | no | Rating range. |
| sellers | {min,max} | no | Seller count range. |
| weight | {min,max} | no | Weight range. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. Only `page` is required.

## 调用方式

- **API 端点**：`POST /seerfar/ozon/marketKeywordSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_market_keyword_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-market-keyword-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Hottest keywords right now (sort by search volume)**
```json
{"page": {"page": 1, "pageSize": 10, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**2. Blue-ocean terms — high volume, few sellers**
```json
{"page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}, "searchVolume": {"min": 10000}, "sellers": {"max": 50}}
```

**3. Filter by keyword text (fuzzy, Russian)**
```json
{"page": {"page": 1, "pageSize": 20}, "keywords": ["телефон"], "matchType": 1}
```

**4. A specific data month with a sales floor**
```json
{"page": {"page": 1, "pageSize": 20}, "searchDate": "2026-04-01", "monthlySales": {"min": 1000}}
```

## How to Build Queries

1. **Lead with `page.orders`**: the dataset is large — always sort by the metric you care about (`searchVolume` DESC for popularity, `count30GrowthRate` DESC for rising terms, `sellers` ASC for low competition).
2. **Stack range filters to find opportunities**: combine a high `searchVolume` floor with a low `sellers` ceiling to surface blue-ocean keywords; add `conversionSharing` / `marketSpace` bounds to qualify demand.
3. **Use `keywords` + `matchType` to scope a niche**: pass seed terms in Russian with `matchType: 1` (fuzzy) to enumerate related long-tail terms.
4. **Pick the right `searchDate`**: omit it for current trends (last 30 days); pass an explicit date for month-over-month comparison.

## Display Rules

1. **Present data only**: show keyword metrics in a clear table without subjective advice.
2. **Lead with keyword columns**: `query` / `queryCn` (Chinese translation), then `searchVolume`, `count30GrowthRate`, `productCount`, `sellers`, `avgPrice`.
3. **Russian keywords**: preserve the original `query`; the `queryCn` field provides a Chinese translation when available.
4. **Platform tag**: when both Ozon and Wildberries rows are present, show `platform` (0/1) so the user can distinguish them.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting filters.

## Important Limitations

- **`page` is required**: a payload without `page` is rejected.
- **No platform selector**: the Ozon/Wildberries mix is controlled server-side; filter client-side via the `platform` field.
- **Category IDs are opaque**: `categories` requires Seerfar category IDs, not human-readable names.
- **Pagination caps**: use `pageSize` and `page` to page; very large `pageSize` values may be capped server-side.
- **Nested fields**: `products[*]` (Top 商品) and `categoryInfos[*]` (类目路径与可跨境标识) are structured and decision-useful — see `references/api.md` for sub-fields. `dimension` / `columns` are opaque or partially populated; `relevancy` / `titleDensity` / `wordCount` are usually absent.

## User Expression & Scenario Quick Reference

**Applicable** — Ozon keyword market research:

| User Says | Scenario |
|-----------|----------|
| "Ozon 热词 / 热搜词有哪些" | Hottest keywords by search volume |
| "Ozon 蓝海词、低竞争高搜索的词" | Blue-ocean term mining (high volume, few sellers) |
| "Ozon 上升词 / 近期增长快的词" | Rising keywords (growth sort) |
| "围绕某个俄语词的长尾词" | Fuzzy keyword expansion |
| "Ozon 某关键词的市场空间/竞品数/卖家数" | Keyword market profile |

**Not applicable** — Needs beyond keyword market data:
- A specific SKU's price/sales/stock → use a product-level Seerfar Ozon data source, not this keyword endpoint.
- A specific seller's catalog → use a seller/shop-level Seerfar Ozon data source.
- Category-tree browsing → use a category-level Seerfar Ozon data source.
- Non-Ozon/Wildberries marketplaces → not covered here.

**Boundary judgment**: if the user wants to **discover and rank search terms** on Ozon by market metrics, start here. If they already have a SKU / seller / category and want entities under it, route to the corresponding Seerfar Ozon data source.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
