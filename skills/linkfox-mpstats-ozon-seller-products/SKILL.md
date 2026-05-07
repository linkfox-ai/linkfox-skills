---
name: linkfox-mpstats-ozon-seller-products
description: MPSTATS Ozon 俄罗斯站按卖家 ID 下钻商品列表。返回该卖家下全部 SKU 的销量、销售额、价格、评分、库存、周转、损失销售额等完整指标，支持多维数值筛选、排序、货币换算。用于店铺结构分析、卖家爆款拆解、竞争对手店铺对标。当用户提到 Ozon 卖家商品、Ozon 店铺分析、Ozon 卖家下钻、Ozon 卖家 SKU、Ozon 店铺爆款、Ozon 竞争店铺、MPSTATS seller, Ozon seller drill-down, Ozon shop audit, Russian marketplace seller SKUs, Ozon store structure 时触发此技能。即使用户未明确说"MPSTATS"，只要意图是按 Ozon 卖家 ID 看该店铺下全部商品的销售表现，也应触发此技能。
---

# MPSTATS Ozon Seller Products

This skill drills into all Ozon (Russia) products sold by a given seller, returning per-SKU sales, revenue, price, rating, stock, turnover, lost profit, and more. Designed for store-structure audits, bestseller dissection within a shop, and head-to-head competitor-store comparison.

## Core Concepts

**Seller ID, not name**: `sellerId` must be a **numeric string** — the `sellerId` field Ozon / MPSTATS uses to identify a shop. Do **not** pass a brand name, category path, or human-readable seller name. If you only have the seller name, resolve the ID via `mpstats-ozon-product-search` (seller-filtered) and read `sellerId` from the result.

**Filters & ops**: Same AND-combined numeric filter model as `brand-products` and `category-products`. See Filter Reference.

**Currency**: Default `RUB`; override with `currency` / `currencyRate` for USD / EUR / CNY views.

**FBO / FBS**: `includeFbs: true` folds FBS into the numbers; `false` keeps FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | yes | Ozon seller ID as numeric string, e.g. `"3628678"` |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column (`sales`, `revenue`, ...) |
| sortDirection | string | no | `asc` / `desc` |
| currency | string | no | Currency code, default `RUB` |
| currencyRate | integer | no | Custom rate for non-default currency |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter list |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales`, `final_price`, `rating`, `comments`, `balance`, `revenue`, `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2`).

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, response structure, and error codes. You can also execute `scripts/mpstats_ozon_seller_products.py` directly for ad-hoc queries.

## Usage Examples

**1. Seller's top-100 by sales**
```json
{
  "sellerId": "3628678",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 100
}
```

**2. Store's revenue top-20**
```json
{
  "sellerId": "3628678",
  "sortField": "revenue",
  "sortDirection": "desc",
  "pageSize": 20
}
```

**3. High-turnover star products**
```json
{
  "sellerId": "3628678",
  "filters": [
    {"field": "sales", "op": "GTE", "value": 30},
    {"field": "turnover_days", "op": "LTE", "value": 20}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**4. Stockout pain points for the store**
```json
{
  "sellerId": "3628678",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 100000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

**5. USD-converted store audit**
```json
{
  "sellerId": "3628678",
  "currency": "USD",
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact store table** — key columns: `productId`, `title`, `brand`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `balance`, `turnoverDays`, `lostProfit`, `position`.
2. **Revenue share = within this seller query** — 0-100%; clarify the base.
3. **Russian titles** — preserve; translate on user request.
4. **Currency labeling** — if converted, note `"已按 USD 换算"`.
5. **Pagination** — for stores with thousands of SKUs, suggest tighter filters before paging deep.
6. **No buying advice** — the skill shows the store's book, not whether their SKUs are worth copying.

## Important Limitations

- **Numeric seller ID only** — passing a seller **name** will not resolve; go through `mpstats-ozon-product-search` first.
- **Page cap** — max 100 rows per page.
- **T-1 data** — `endDate` cannot be today or a future date.
- **No business advice** — data-only.
- **Ozon-only** — Wildberries / other Russian marketplaces are separate.

## User Expression & Scenario Quick Reference

**Applicable** — Seller-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Show me everything seller 3628678 sells, by sales" | Store SKU map |
| "What are this Ozon store's top revenue products" | Store bestseller drill |
| "How many SKUs does the store have with turnover <20 days" | Operational health filter |
| "Where is this store losing money to stockouts" | Lost-profit scan |
| "Compare two Ozon stores' SKU counts and sales" | Store-vs-store benchmarking (call twice) |

**Not applicable** — Needs beyond seller drill-down:

- Only seller **name** known → use `mpstats-ozon-product-search` to resolve the ID
- Brand-scoped drill → `mpstats-ozon-brand-products`
- Category-scoped drill → `mpstats-ozon-category-products`
- Single-SKU time-series → `mpstats-ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the **dimension is a specific seller** and you want the per-SKU table under that shop. For "who are the top sellers in category X" you'd use category drill-down and group by seller client-side.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
