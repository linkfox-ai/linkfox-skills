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

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/keywordBackSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-keyword-back-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/keywordBackSearch",
  "arguments": {
    "skuIds": [
      4380710124
    ],
    "hasVariant": 1,
    "page": {
      "page": 1,
      "pageSize": 10,
      "orders": [
        {
          "field": "searchVolume",
          "direction": "DESC"
        }
      ]
    }
  }
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，不得使用 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 `headers`、API Key、token、JWT、手机号或其他凭证。
- 同一任务内相同 `toolName + arguments` 不重复调用；收费调用失败、空结果或结果不理想时不自动重试。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text JSON 只解析一次，随后检查下游 `errcode`/`errorCode`/`code`/`errmsg`/`msg`，最后读取业务字段。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失、MCP 连接 401、下游 401/402/403 及积分不足均按 `references/onboarding.md` 分层处理。
- 不要求用户填写 Authorization 或 API Key；不自动选套餐、下单、支付或轮询。
## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 关键词反查数据（详见下方） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

### data[*] 关键词反查对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 关键词（俄语原文） |
| queryCn | string | 关键词中文翻译 |
| platform | integer | 平台：`0` Ozon，`1` Wildberries |
| searchVolume | integer | 月搜热度 |
| count30GrowthRate | number | 月搜增长（%，可为负） |
| productCount | integer | 商品数（部分行可能缺失） |
| competingProducts | integer | 竞品数 |
| sellers | integer | 卖家数 |
| avgPrice | number | 平均价格 |
| itemsViews | number | 商品可见度 |
| viewSharing | number | 浏览集中度（%） |
| conversionSharing | number | 转化集中度（%） |
| marketSpace | number | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| titleDensity | number | 标题密度 |
| wordCount | integer | 字数 |
| categories | array | 类目 ID 数组 |
| dimension | object | 维度对象，承载反查专属指标（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |

> **字段填充（以真实响应为准）**：`dimension`（维度对象）**每行均返回**，承载反查专属指标（`type` / `naturalRank` / `exposure` / `conversion` / `x`，详见下方）。`titleDensity`（标题密度）、`wordCount`（字数）每行均返回。`productCount`（商品数）大部分行返回，个别行可能为 `null`。`relevancy`（相关度）虽在 outputSchema / `columns` 中定义，但实测 `data[*]` **不返回**；`categoryInfos`（类目信息）同样**不返回**（同族 `keywordMining` 亦不返回，`marketKeywordSearch` 返回——勿假设一致）。

#### dimension 维度对象字段

每行 `data[*]` 均返回 `dimension`，承载该搜索词相对反查 SKU 的专属指标；输入侧的 `type` / `naturalRank` / `adRank` / `exposure` / `conversion` 筛选项即作用于这些值。

| 字段 | 类型 | 说明 |
|------|------|------|
| type | integer | 搜索词渠道：`0` 自然搜索词、`1` 广告搜索词 |
| naturalRank | integer | 自然排名（反查 SKU 在该词下的自然位次） |
| exposure | number | 曝光（0–1） |
| conversion | number | 转化率（0–1） |
| x | array | 位置/分页指示，语义不透明 |

> 广告词（`type:1`）行可能额外携带 `adRank`；本次测试 SKU 仅有自然词（`type:0`，按 `type:["1"]` 查询 `total:0`），未观测到 `adRank`，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

> ⚠️ 实测 `data[*]` 行中**不返回** `categoryInfos`（仅在 `columns` 列定义中出现）；下方字段为 outputSchema 定义，仅供出现时参考。

| 字段 | 类型 | 说明 |
|------|------|------|
| titleCn | string | 类目中文名 |
| titleEn | string | 类目英文名 |
| titleRu | string | 类目俄语名 |
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 俄语类目路径 |
| id | string | 类目 ID |
| crossBorderSellable | boolean | 是否可跨境销售 |


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
- **Nested fields**: `products[*]` (Top 商品) and `dimension` (per-term back-search metrics: `type`, `naturalRank`, `exposure`, `conversion`, `x`) are structured and decision-useful — see `references/linkfox-seerfar-ozon-keyword-back-search-api.md` for sub-fields. `categoryInfos` is defined in the schema/columns but is **not** returned in `data[*]` on this endpoint (same as the keyword-mining sibling; the market-keyword-search sibling does return it — don't assume parity). `relevancy` is likewise defined in the schema but **not** returned.

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

## 积分消耗规则

消耗 12 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/linkfox-seerfar-ozon-keyword-back-search-api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
