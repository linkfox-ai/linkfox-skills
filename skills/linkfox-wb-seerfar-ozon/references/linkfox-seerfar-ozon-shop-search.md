---
name: linkfox-seerfar-ozon-shop-search
description: Seerfar Ozon 店铺商品搜索：按 Ozon 店铺（卖家）ID 拉取该店铺的商品列表，返回每个商品的近30天销量、价格、评分、重量、配送方式（FBO/FBS）、卖家类型（本土/跨境）、退货取消率，以及店铺近30天总销量。用于竞品店铺商品分析、店铺爆品挖掘、卖家商品结构拆解。当用户提到 Ozon 店铺商品、Ozon 卖家商品列表、竞品店铺分析、Ozon 店铺爆品、Ozon 卖家分析、Seerfar Ozon 店铺搜索、Ozon shop search, Ozon seller products, competitor shop analysis, Ozon store products 时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是查看某 Ozon 店铺/卖家的商品与销量数据，也应触发此技能。
---

# Seerfar Ozon Shop Search

This skill lists the products of a specific Ozon shop (seller) from the Seerfar analytics database. Given a shop `id`, it returns each product's 30-day sales, price, rating, weight, fulfillment model (FBO/FBS), seller type (local / cross-border) and return/cancellation rate, plus the shop's total 30-day sales — the starting point for competitor-shop product analysis, best-seller mining, and seller catalog teardown.

## Core Concepts

**Unit of data is the product, scoped to one shop**: pass a single shop `id` and receive that shop's product catalog with performance metrics. This is a *shop-level* view, not a keyword or category view.

**Where the shop `id` comes from**: `id` is the Seerfar seller/shop identifier — the same `sellerId` returned by other Seerfar Ozon tools (e.g. product report / product detail search). Negative ids (e.g. `-2` Ozon Express, `-4` Ozon Fresh) are Ozon's own platform sellers; positive ids are third-party sellers. If the user only has a shop name or product, first obtain the `sellerId` from a product-level Seerfar Ozon source, then call this skill.

**Seller type**: each product carries `sellerType` — `0` local (本土), `1` cross-border (跨境). A shop is typically all one type; use it to judge whether a competitor is a domestic or cross-border seller.

**Sales & price currency**: `sales` / `monthlySalesUnits` are 30-day units; `price` is in Russian rubles (₽), indicated by `currency`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | yes | Shop (seller) ID — the `sellerId` from other Seerfar Ozon tools. Negative = Ozon platform seller. |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. |
| page.page | integer | no | Page number, from 1 (default 1). |
| page.pageSize | integer | no | Page size, default 20. **Max 20** — larger values are rejected (`errcode 1002`). |
| page.orders | array | no | Sort rules, elements `{field, direction}`; `direction` `DESC`/`ASC`. Common fields: `sales`, `price`, `reviewRating`, `upTime`. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `id` and `page` are required.

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/shopSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-shop-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/shopSearch",
  "arguments": {
    "id": 1362816,
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
| total | integer | **本页返回记录数**（等于当前页数据条数，并非店铺商品总数） |
| totalSales | integer | 店铺近 30 天总销量 |
| totalRevenue | integer | 店铺总销售额（卢布） |
| dailySales | integer | 店铺日均销量 |
| rating | number | 店铺评分（0-5） |
| productCount | integer | 店铺商品总数（全店铺，非本页条数） |
| fulfillment | object | 店铺配送方式分布，键为配送方式（`FBO`/`FBS`），值为该方式商品数，如 `{"FBO": 72, "FBS": 4}`（与商品级 `fulfillment` 数组不同） |
| data | array | 店铺商品列表（详见下方） |
| products | array | 店铺商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

### data[*] / products[*] 店铺商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 统一商品 ID，映射自 `sku` |
| sku | integer | 商品 SKU |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewRating | number | 商品评分 |
| weight | number | 商品重量，单位 g |
| sales | integer | 商品近 30 天销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| upTime | integer | 商品上架时间，毫秒时间戳 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| imageUrl | string | 统一主图 URL |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| sellerType | integer | 卖家类型：`0` 本土，`1` 跨境 |
| returnCancellationRate | number | 商品退货取消率（%） |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查店铺` |

> **字段差异**：`returnCancellationRate` 对第三方卖家普遍返回，但对 Ozon 平台自营卖家（`id` 为负值）常常缺失，使用前需判空。
> **schema 中定义但实际不返回**：`productPageUrl`（统一商品页 URL）、`monthlySalesRevenue`（统一月销售额）、`brand`（统一品牌）在 outputSchema 中标注"上游无对应字段，保持 null"，实际响应中**不返回**这些字段（既非 null 也非空），不要依赖它们。


## Usage Examples

**1. A shop's best-sellers (sort by 30-day sales)**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**2. A shop's newest listings (sort by upload time)**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "upTime", "direction": "DESC"}]}}
```

**3. A shop's highest-priced products**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "price", "direction": "DESC"}]}}
```

**4. Page deeper into a shop's catalog**
```json
{"id": 1362816, "page": {"page": 2, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

## How to Build Queries

1. **Always pass `page.orders`**: the catalog can be large — sort by the metric you care about (`sales` DESC for best-sellers, `upTime` DESC for new arrivals, `price` DESC for premium SKUs).
2. **Keep `pageSize` ≤ 20**: the gateway caps page size at 20. Use `page.page` to paginate; check `hasNextPage` to know whether more pages exist.
3. **Resolve the shop `id` first**: if the user gives a shop/product name rather than an id, obtain the `sellerId` from a product-level Seerfar Ozon source before calling this skill.
4. **Use shop-level aggregates for context**: `totalSales` / `totalRevenue` / `dailySales` are shop-wide totals (independent of the page), `productCount` is the full catalog size, `rating` is the shop rating, and top-level `fulfillment` shows the FBO/FBS split — all quick health indicators for the whole shop.

## Display Rules

1. **Present data only**: show the shop's product metrics in a clear table without subjective advice.
2. **Lead with shop context, then product columns**: state shop-level aggregates first — `totalSales` (30-day total), `totalRevenue` (total revenue, ₽), `productCount` (catalog size), `dailySales`, `rating`, and `fulfillment` distribution (e.g. FBO 72 / FBS 4) — then a table of `sku`, `price`, `sales`, `reviewRating`, `weight`, `sellerType`, `fulfillment`, `returnCancellationRate`.
3. **Seller type label**: render `sellerType` as 本土/跨境 (0/1) so the user reads it at a glance.
4. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`); join multiple values with `/`.
5. **Missing `returnCancellationRate`**: for Ozon platform sellers (negative `id`) this field is often absent — show `-` rather than failing.
6. **Pagination guidance**: when `hasNextPage` is true, tell the user more pages are available via `page.page`; remind them `pageSize` is capped at 20.
7. **Empty shop**: a non-existent `id` returns success with `total=0` and no data — tell the user the id may be wrong rather than reporting a system error.
8. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest fixes (add `page`, lower `pageSize`, retry on rate-limit).

## Important Limitations

- **`id` and `page` are both required**; omitting either returns `errcode 400`.
- **`pageSize` max 20**: exceeding it returns `errcode 1002`.
- **`total` is the page row count**, not the shop's full catalog size — use `hasNextPage` to decide whether to fetch more pages.
- **No text/keyword filter**: this endpoint filters by shop only; to find a shop by name, use another Seerfar Ozon source first.
- **Field variance by seller type**: `returnCancellationRate` is populated for third-party sellers but frequently absent for Ozon platform sellers (negative `id`). Schema-defined `productPageUrl`, `monthlySalesRevenue`, `brand` are not returned (upstream has no source, omitted rather than null).

## User Expression & Scenario Quick Reference

**Applicable** — analyzing one Ozon shop/seller's catalog:

| User Says | Scenario |
|-----------|----------|
| "分析下这个 Ozon 店铺的商品" / "这个卖家在卖什么" | Shop product catalog |
| "这家店最畅销的商品是什么" | Best-seller mining (sort by sales) |
| "这家店最近上了哪些新品" | New arrivals (sort by upTime) |
| "这个竞品店铺的价格带/客单价" | Price-band analysis (sort by price) |
| "这家店是本土还是跨境卖家" | Seller type check (sellerType) |
| "这个店铺总销量多少" | Shop health (totalSales) |

**Not applicable** — Needs beyond one shop's catalog:
- Discovering Ozon keywords by market metrics → use the Seerfar Ozon market keyword search skill.
- A single product's full detail → use a product-level Seerfar Ozon source (this skill returns catalog-level fields only).
- Browsing the category tree → use a category-level Seerfar Ozon source.
- Finding which shop sells a given product → use a product-level Seerfar Ozon source to get the `sellerId` first.

**Boundary judgment**: if the user already has a shop/seller ID (or a `sellerId` obtained from a product lookup) and wants to enumerate or rank that shop's products by sales/price/rating, start here. If they want market-level keyword discovery or a single product's deep detail, route to the corresponding Seerfar Ozon skill.

## 积分消耗规则

消耗 12 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/linkfox-seerfar-ozon-shop-search-api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
