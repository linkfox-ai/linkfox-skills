---
name: linkfox-seerfar-ozon-keyword-back-search
description: Seerfar Ozon 关键词反查：按商品 SKU 列表（最多 20 个）反查 Ozon（及 Wildberries）搜索关键词，返回这些商品出现在哪些搜索词下（自然搜索词/广告搜索词），并按搜索热度、增长、商品数、卖家数、竞品数、自然排名、广告排名、曝光、转化、加购转化等多维指标筛选，每个关键词附带月搜热度、增长、市场空间、竞品/卖家数、均价、加购转化、Top 商品及自然/广告渠道、排名、曝光、转化（dimension）等市场画像，用于 Ozon 关键词反查、Listing 选词优化、竞品流量词挖掘与广告词分析。当用户提到 Ozon 关键词反查、Ozon 反查关键词、Ozon SKU 反查、Ozon 商品流量词、Ozon 竞品出单词、Ozon 自然词/广告词反查、Seerfar Ozon、Ozon keyword back search, Ozon reverse keyword lookup, Ozon SKU keyword reverse 时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是按商品 SKU 反查 Ozon 搜索关键词并查看市场画像，也应触发此技能。
---

# Seerfar Ozon Keyword Back-Search

This skill reverse-looks-up Ozon search keywords **by a list of product SKU IDs** in the Seerfar analytics database: pass up to 20 SKUs (your own listing or a competitor's) and it returns the search terms those products appear under — organic and/or ad — each enriched with a full market profile (search volume, 30-day growth, product/seller/competitor counts, average price, conversion concentration, top products, plus per-term organic/ad channel, natural rank, exposure, and conversion in the `dimension` object). It is the starting point for Ozon keyword reverse lookup, listing-title optimization, and competitor traffic-word discovery.

## Core Concepts

**SKU-driven, not keyword-driven**: unlike keyword mining (expand *from* a seed term) or market keyword search (browse the whole market), this endpoint takes `skuIds` and returns the search terms *those specific products* rank for. The direction is product → keywords (reverse).

**`hasVariant` is required**: every request must declare whether to exclude variants — `0` keep variants, `1` exclude variants. Pick `1` when you want de-duplicated keyword coverage for a parent listing.

**Natural vs ad terms**: `type` filters the search-term channel — `["0"]` organic (自然搜索词) only, `["1"]` ad (广告搜索词) only; omit to get both. Combine with the `naturalRank` / `adRank` range filters to qualify positioning.

**Back-search metrics live in `dimension`**: each returned term carries a `dimension` object with the reverse-lookup-specific metrics — `type` (`0` organic / `1` ad), `naturalRank` (the SKU's natural rank for that term), `exposure` (exposure share, 0–1), `conversion` (conversion rate, 0–1), and `x` (opaque position indicator). The input filters `type` / `naturalRank` / `adRank` / `exposure` / `conversion` filter on these same per-term values. Note: `relevancy` is defined in the schema but is **not** returned by this endpoint.

**Platform coverage**: each keyword record carries a `platform` field (`0` = Ozon, `1` = Wildberries). The dataset is Ozon-centric; Wildberries rows appear where available. There is no input to restrict the platform — filter client-side if needed.

**Match mode**: `matchType` controls how `includeKeywords` / `excludeKeywords` are matched — `0` exact, `1` fuzzy.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skuIds | array<integer> | yes | Reverse-lookup SKU list, max 20. |
| hasVariant | integer | yes | Variant exclusion: `0` keep variants, `1` exclude variants. |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| matchType | integer | no | Keyword match mode: `0` exact, `1` fuzzy. |
| type | array<string> | no | Search-term channel filter: `0` organic, `1` ad; omit for both. |
| historyDate | string | no | Historical month `yyyy-MM` (e.g. `2026-02`); omit for current period. |
| includeKeywords | array<string> | no | Terms that must appear (max 1000). |
| excludeKeywords | array<string> | no | Terms to exclude (max 1000). |
| searchVolume | {min,max} | no | Monthly search volume range. |
| searchChange30 | {min,max} | no | 30-day search change range. |
| wordCount | {min,max} | no | Keyword word/char count range. |
| productViews | {min,max} | no | Product view range. |
| products | {min,max} | no | Product count range. |
| sellers | {min,max} | no | Seller count range. |
| marketSpace | {min,max} | no | Market space range. |
| conversionSharing | {min,max} | no | Conversion concentration range. |
| uniqQueriesWCa | {min,max} | no | Cart-add count range. |
| ca | {min,max} | no | Cart-add conversion rate range. |
| conversion | {min,max} | no | Conversion rate range. |
| titleDensity | {min,max} | no | Title density range. |
| adRivalCount | {min,max} | no | Ad competitor count range. |
| adRank | {min,max} | no | Ad rank range. |
| naturalRank | {min,max} | no | Natural rank range. |
| exposure | {min,max} | no | Exposure range. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. `skuIds`, `hasVariant`, and `page` are all required.

## 调用方式

- **API 端点**：`POST /seerfar/ozon/keywordBackSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_keyword_back_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-keyword-back-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Reverse-lookup a single SKU's traffic keywords (sort by search volume)**
```json
{"skuIds": [4380710124], "hasVariant": 0, "page": {"page": 1, "pageSize": 10, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**2. Organic terms where the SKU ranks near the top**
```json
{"skuIds": [4380710124], "hasVariant": 1, "type": ["0"], "naturalRank": {"max": 10}, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**3. Ad search words only, with an ad-rank floor**
```json
{"skuIds": [4380710124], "hasVariant": 0, "type": ["1"], "adRank": {"max": 50}, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**4. Narrow with include / exclude lists**
```json
{"skuIds": [4380710124], "hasVariant": 0, "page": {"page": 1, "pageSize": 20}, "includeKeywords": ["платье"], "excludeKeywords": ["ремень"], "matchType": 1}
```

## How to Build Queries

1. **Always lead with `skuIds` + `hasVariant`**: both are required and define the reverse-lookup target. Use real Ozon SKU IDs (the same IDs returned by Seerfar Ozon product / shop / category skills).
2. **Lead with `page.orders`**: sort by the metric you care about (`searchVolume` DESC for traffic weight, `sellers` ASC for low competition, `count30GrowthRate` DESC for rising terms).
3. **Split organic vs ad with `type`**: pass `["0"]` or `["1"]` to focus a listing-optimization pass (organic) or an ads pass (ad), then bound `naturalRank` / `adRank` to qualify positioning — these filter on the values surfaced in each row's `dimension`.
4. **Use `includeKeywords` / `excludeKeywords` to steer**: force in must-have modifiers and strip noise without running a second query.

## Display Rules

1. **Present data only**: show reverse-looked-up keyword metrics in a clear table without subjective advice.
2. **Lead with keyword columns**: `query` / `queryCn` (Chinese translation), then `searchVolume`, `count30GrowthRate`, `productCount`, `sellers`, `avgPrice`; show `dimension.naturalRank` and `dimension.type` (organic/ad) to convey how the SKU ranks for each term.
3. **Russian keywords**: preserve the original `query`; the `queryCn` field provides a Chinese translation when available.
4. **Channel tag**: when `type` is omitted and both organic and ad rows are present, show `dimension.type` (`0` organic / `1` ad) and `dimension.naturalRank` so the user can distinguish them.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting the SKU list or filters.

## Important Limitations

- **`skuIds` + `hasVariant` + `page` required**: a payload missing any of these is rejected.
- **`skuIds` capped at 20**: pass more than 20 and the request is rejected or truncated.
- **No keyword seed**: this endpoint has no `keyword` parameter — it is reverse (SKU → keywords), not expansion (keyword → keywords). Use the keyword mining skill to expand from a seed.
- **No `searchDate` / `categories` input**: only `historyDate` (historical month) is accepted; there is no category filter. Use the market keyword search skill for month- or category-scoped browsing.
- **Nested fields**: `products[*]` (Top 商品) and `dimension` (per-term back-search metrics: `type`, `naturalRank`, `exposure`, `conversion`, `x`) are structured and decision-useful — see `references/api.md` for sub-fields. `categoryInfos` is defined in the schema/columns but is **not** returned in `data[*]` on this endpoint (same as the keyword-mining sibling; the market-keyword-search sibling does return it — don't assume parity). `relevancy` is likewise defined in the schema but **not** returned.

## User Expression & Scenario Quick Reference

**Applicable** — SKU-driven Ozon keyword reverse lookup:

| User Says | Scenario |
|-----------|----------|
| "反查这个 Ozon 商品 / SKU 的关键词" | Reverse keyword lookup for a SKU |
| "这个 Ozon 链接有哪些搜索词带来流量" | Traffic-word discovery for a listing |
| "Ozon 竞品 SKU 的出单词 / 流量词" | Competitor traffic-word mining |
| "Ozon 某商品的自然词 / 广告词" | Organic vs ad term breakdown |
| "Ozon 关键词反查、按 SKU 反查关键词" | Generic reverse keyword lookup |

**Not applicable** — Needs beyond SKU-driven reverse lookup:
- Browse/rank the whole market's hot keywords (no SKU) → use the Seerfar Ozon market keyword search skill.
- Expand outward from a seed keyword → use the Seerfar Ozon keyword mining skill.
- A specific SKU's price/sales/stock → use a product-level Seerfar Ozon data source.
- A specific seller's catalog → use the Seerfar Ozon shop search skill.
- Category-tree browsing → use the Seerfar Ozon category search skill.

**Boundary judgment**: if the user has a **product/SKU** (own or competitor) and wants the **search terms it ranks for**, start here. If they want to **browse the market** (no SKU) or **expand from a seed keyword**, route to the market keyword search or keyword mining skill respectively.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
