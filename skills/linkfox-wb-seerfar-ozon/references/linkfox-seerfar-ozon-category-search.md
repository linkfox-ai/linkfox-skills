---
name: linkfox-seerfar-ozon-category-search
description: Seerfar Ozon 类目商品搜索：按 Ozon 类目 ID 拉取该类目下的商品列表，返回类目级聚合（类目总销量、总销售额、平均价格、平均评分、季节性）与每个商品的销量、价格、评分、评论数、品牌、卖家、配送方式。用于类目选品分析、类目爆品挖掘、类目容量与价格带分析、季节性判断。当用户提到 Ozon 类目商品、Ozon 类目分析、Ozon 类目选品、Ozon 类目爆品、Ozon 类目总销量、Ozon 类目平均价格、Ozon category search, Ozon category products, category best-sellers, category analysis 时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是查看某 Ozon 类目下的商品与类目级汇总数据，也应触发此技能。
---

# Seerfar Ozon Category Search

This skill lists the products of a specific Ozon category from the Seerfar analytics database. Given a `categoryId`, it returns category-level aggregates (total sales, total revenue, average price, average rating, seasonality) plus each product's sales, price, rating, review count, brand and seller — the starting point for category selection analysis, best-seller mining within a category, and category capacity / price-band analysis.

## Core Concepts

**Unit of data is the product, scoped to one category**: pass a single `categoryId` and receive that category's product list with performance metrics, alongside category-level aggregates. This is a *category-level* view, not a shop or keyword view.

**Where the `categoryId` comes from**: `categoryId` is the Ozon category identifier — a hierarchical path joined by `_` (e.g. `15621032_15621049_115951147`), obtained from the Ozon category document or from other Seerfar Ozon tools. If the user only has a category name, first resolve it to a `categoryId` from an upstream Seerfar Ozon source before calling this skill.

**Category aggregates vs product rows**: the response carries both category-level totals (`totalSales`, `totalRevenue`, `avgPrice`, `rating`, `seasonalityAmplitude`, `seasonalityCoef`, `startDate`/`endDate`) and a paginated product list (`data` / `products`). Use the aggregates for category sizing and the rows for individual product analysis.

**Sales & price currency**: `sales` / `monthlySalesUnits` are units; `price` / `revenue` are in Russian rubles (₽), indicated by `currency`.

**Time window**: by default the data covers the last 30 days (`startDate` / `endDate` show the actual range). Pass `date` as `yyyy-MM` (e.g. `2026-02`) to query a historical month snapshot.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| categoryId | string | yes | Ozon category ID, e.g. `15621032_15621049_115951147` (levels joined by `_`). |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. |
| page.page | integer | no | Page number, from 1 (default 1). |
| page.pageSize | integer | no | Page size, default 20. **Max 20** — larger values are rejected (`errcode 1002`). |
| page.orders | array | no | Sort rules, elements `{field, direction}` (both required); `direction` `DESC`/`ASC`. Common fields: `sales`, `price`, `revenue`, `reviewRating`. |
| date | string | no | Historical month `yyyy-MM` (e.g. `2026-02`); omit for last 30 days. |
| fulfillment | string | no | Fulfillment filter, one of `FBO` / `FBS` / `RFBS` / `FBP` / `OZON`; omit to query all. **Single string, not an array.** |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `categoryId` and `page` are required.

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/categorySearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-category-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/categorySearch",
  "arguments": {
    "categoryId": "15621032_15621049_115951147",
    "page": {
      "page": 1,
      "pageSize": 10,
      "orders": [
        {
          "field": "sales",
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
| id | string | 回显的类目 ID |
| total | integer | **本页返回记录数**（等于当前页 `data` 条数，并非类目商品总数） |
| totalSales | integer | 类目总销量（统计区间内） |
| totalRevenue | number | 类目总销售额（卢布） |
| avgPrice | number | 类目商品平均价格（卢布） |
| rating | number | 类目商品平均评分 |
| seasonalityAmplitude | string | 季节性强度，如 `STRONG_SEASONALITY` |
| seasonalityCoef | string | 季节性阶段，如 `OFF_SEASON` |
| startDate | string | 统计起始日期 |
| endDate | string | 统计结束日期 |
| sellerType | object | **配送方式分布**（非卖家本土/跨境类型），键为配送方式、值为该方式商品数，如 `{"FBO":218,"RFBS":528,"FBP":5,"FBS":240,"OZON":1}` |
| categoryInfo | object | 类目元信息，结构见下方「categoryInfo 结构」 |
| data | array | 类目商品列表（详见下方） |
| products | array | 类目商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

### data[*] / products[*] 类目商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID，映射自 `sku` |
| title | string | 商品标题 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| sales | integer | 商品销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| revenue | number | 商品销售额 |
| monthlySalesRevenue | number | 统一月销售额，映射自 `revenue` |
| reviewRating | number | 商品评分 |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewCount | integer | 评论数 |
| brandName | string | 品牌名称 |
| brand | string | 统一品牌，映射自 `brandName` |
| sellerName | string | 卖家名称 |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| imageUrl | string | 商品图片链接 |
| productUrl | string | 商品链接 |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目归属信息，结构见下方「categoryInfo 结构」 |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查类目` |

> **统一字段 vs 原始字段**：`productId`/`rating`/`brand`/`monthlySalesUnits`/`monthlySalesRevenue`/`productPageUrl` 为后端统一映射字段，与原始 `sku`/`reviewRating`/`brandName`/`sales`/`revenue`/`productUrl` 等价；展示时二选一即可，建议用原始字段（语义更直观）。

### categoryInfo 结构（顶层与每个商品均返回）

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径，如 `鞋类 > 运动鞋和工作鞋 > 举重鞋` |
| enTitlePath | string | 英文类目路径，如 `Footwear > Sports and Work Footwear > Weightlifting Shoes` |
| titlePath | string | 俄文（前台）类目路径，如 `Обувь > Спортивная и рабочая обувь > Штангетки` |
| fullCategoryId | array | 各级类目 ID 数组，如 `["15621032","15621032_15621049","15621032_15621049_115951147"]` |
| category | object | 末级类目对象，含 `cnTitle`/`enTitle`/`title`(俄文)/`level`/`crossBorderSellable`(是否可跨境销售)/`pid`/`disabled`/`id` |

> `categoryInfo` 在顶层与每个 `data[*]` 中均返回且内容一致，可用于核对类目名称（中/英/俄）与可否跨境销售（`category.crossBorderSellable`）。


## Usage Examples

**1. Category best-sellers (sort by 30-day sales)**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**2. Category top-revenue products**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "revenue", "direction": "DESC"}]}}
```

**3. Category premium price band (highest-priced)**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "price", "direction": "DESC"}]}}
```

**4. Historical month snapshot**
```json
{"categoryId": "15621032_15621049_115951147", "date": "2026-02", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**5. Filter to FBO-fulfilled products only**
```json
{"categoryId": "15621032_15621049_115951147", "fulfillment": "FBO", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**6. Page deeper into the category**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 2, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

## How to Build Queries

1. **Always pass `page.orders`**: categories can contain many products — sort by the metric you care about (`sales` DESC for best-sellers, `revenue` DESC for top revenue, `price` DESC for the premium band, `reviewRating` DESC for best-reviewed).
2. **Keep `pageSize` ≤ 20**: the gateway caps page size at 20. Use `page.page` to paginate; check `hasNextPage` to know whether more pages exist.
3. **Resolve the `categoryId` first**: if the user gives a category name rather than an id, obtain the `categoryId` from an upstream Seerfar Ozon source before calling this skill.
4. **Use category aggregates for sizing**: `totalSales`, `totalRevenue`, `avgPrice` and `rating` describe the whole category at a glance — use them for capacity and price-band assessment before drilling into rows.
5. **Use `date` for historical comparison**: pass `date` as `yyyy-MM` to compare a past month against the current 30-day window.
6. **`fulfillment` is a single string**: pass one of `FBO` / `FBS` / `RFBS` / `FBP` / `OZON`, not an array.

## Display Rules

1. **Present data only**: show the category aggregates and product metrics in a clear table without subjective advice.
2. **Lead with category context, then product columns**: state the category name (from `categoryInfo.cnTitlePath` / `enTitlePath` — confirms the right category), then `totalSales`, `totalRevenue`, `avgPrice`, `rating`, seasonality (`seasonalityAmplitude` / `seasonalityCoef`) and date range, plus the fulfillment distribution (`sellerType` map) as a one-line FBO/FBS/RFBS/... split; then a table of `sku`, `title`, `price`, `sales`, `revenue`, `reviewRating`, `reviewCount`, `brandName`, `sellerName`.
3. **Currency**: `price` / `revenue` are in rubles (₽); render with the `currency` symbol.
4. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`); join multiple values with `/`.
5. **Unified vs original fields**: `productId`/`rating`/`brand`/`monthlySalesUnits`/`monthlySalesRevenue`/`productPageUrl` mirror `sku`/`reviewRating`/`brandName`/`sales`/`revenue`/`productUrl` — show one set, prefer the originals.
6. **Pagination guidance**: when `hasNextPage` is true, tell the user more pages are available via `page.page`; remind them `pageSize` is capped at 20.
7. **Empty category**: a non-existent `categoryId` returns success with `total=0` and no data — tell the user the id may be wrong rather than reporting a system error.
8. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest fixes (add `page`, lower `pageSize`, retry on rate-limit).

## Important Limitations

- **`categoryId` and `page` are both required**; omitting either returns `errcode 400`.
- **`pageSize` max 20**: exceeding it returns `errcode 1002`.
- **No text/keyword filter within a category**: this endpoint filters by category (plus optional `fulfillment` and `date`) only; to find products by keyword, use the Seerfar Ozon market keyword search skill.
- **`total` is the page row count**, not the category's total product count — use `hasNextPage` to decide whether to fetch more pages.
- **`sellerType` is a fulfillment distribution, not seller type**: despite the name, the top-level `sellerType` is a map of fulfillment model → product count (`{FBO, RFBS, FBP, FBS, OZON}`); it does not carry 本土/跨境 (local/cross-border) info. `categoryInfo` carries the category name path (CN/EN/RU) and `crossBorderSellable`.

## User Expression & Scenario Quick Reference

**Applicable** — analyzing one Ozon category's products and aggregates:

| User Says | Scenario |
|-----------|----------|
| "分析下这个 Ozon 类目的商品" / "这个类目有多大" | Category sizing (totalSales / totalRevenue / avgPrice) |
| "这个类目最畅销的商品是什么" | Best-seller mining (sort by sales) |
| "这个类目销售额最高的商品" | Top-revenue products (sort by revenue) |
| "这个类目的价格带/客单价" | Price-band analysis (sort by price) |
| "这个类目评分最高的商品" | Best-reviewed (sort by reviewRating) |
| "这个类目上个月的数据" | Historical month snapshot (date) |
| "这个类目 FBO 的商品" | Fulfillment filter |

**Not applicable** — Needs beyond one category's product list:
- One shop/seller's catalog → use the Seerfar Ozon shop search skill.
- Market-level keyword discovery → use the Seerfar Ozon market keyword search skill.
- Keyword mining → use the Seerfar Ozon keyword mining skill.
- A single product's full detail → use a product-level Seerfar Ozon source (this skill returns category-level fields only).

**Boundary judgment**: if the user already has a `categoryId` (or one resolved from an upstream source) and wants to enumerate, rank, or size that category's products by sales/price/rating, start here. If they want a shop's catalog, keyword discovery, or a single product's deep detail, route to the corresponding Seerfar Ozon skill.

## 积分消耗规则

消耗 12 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/linkfox-seerfar-ozon-category-search-api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
