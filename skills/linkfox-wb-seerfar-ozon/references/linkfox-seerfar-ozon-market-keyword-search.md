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

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/marketKeywordSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-market-keyword-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/marketKeywordSearch",
  "arguments": {
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
| data | array | 市场热词数据（详见下方） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

### data[*] 关键词市场对象字段

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
| marketSpace | integer | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| categories | array | 类目 ID 数组 |
| categoryInfos | array | 类目信息（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |

> `relevancy`（相关度）、`titleDensity`（标题密度）、`wordCount`（字数）、`dimension`（维度信息）在 outputSchema 中有定义，但实际响应中通常不返回或为 `null`，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

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
- **Nested fields**: `products[*]` (Top 商品) and `categoryInfos[*]` (类目路径与可跨境标识) are structured and decision-useful — see `references/linkfox-seerfar-ozon-market-keyword-search-api.md` for sub-fields. `dimension` / `columns` are opaque or partially populated; `relevancy` / `titleDensity` / `wordCount` are usually absent.

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

## 积分消耗规则

消耗 12 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/linkfox-seerfar-ozon-market-keyword-search-api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
