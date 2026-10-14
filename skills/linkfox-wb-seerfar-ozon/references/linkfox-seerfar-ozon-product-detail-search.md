---
name: linkfox-seerfar-ozon-product-detail-search
description: Seerfar Ozon 商品详情查询：按 Ozon 商品 SKU 拉取单个商品的完整详情，返回标题、价格（卢布）、评分、评论数、QA数、统计窗口内总销量与日均销量、销售额、库存、类目排名、每日销量趋势、品牌、卖家、配送方式（FBO/FBS/OZON）、重量、上架时间/天数/月数等。用于单品深度分析、竞品商品拆解、Ozon 选品评估、Listing 诊断、销量趋势与类目排名跟踪。当用户提到 Ozon 商品详情、Ozon 单品分析、Ozon SKU 查询、竞品商品数据、Ozon 销量趋势、Ozon 类目排名、Ozon 库存、Ozon 上架时间、Seerfar Ozon 商品搜索、Ozon product detail, Ozon SKU lookup, single product analysis, competitor product teardown, Ozon sales trend, category rank 时触发此技能。即使用户未明确提到"Seerfar"，只要其意图是查看某个 Ozon 商品的详细数据，也应触发此技能。
---

# Seerfar Ozon Product Detail Search

This skill fetches the full detail of a single Ozon product by its SKU from the Seerfar analytics database — title, price (₽), rating, reviews, QA count, sales (total + daily average + daily trend), revenue, stock, category rank, brand, seller, fulfillment (FBO/FBS/OZON), weight and listing age. The starting point for single-product deep analysis, competitor product teardown, listing diagnostics and sales-trend tracking.

## Core Concepts

**Unit of data is a single product, looked up by `sku`**: pass one Ozon SKU, get that product's full detail. This is a *product-level* view (one SKU), not a shop catalog, keyword or category view.

**Where the SKU comes from**: `sku` is the Ozon product SKU — the same `sku` returned by other Seerfar Ozon tools (shop search, keyword back search, category search, market keyword search). If the user only has a product name, URL or shop, first obtain the `sku` from one of those listing-level sources, then call this skill for the deep dive.

**Sales window**: `dateRange` controls the sales/metrics window — `totalSales`, `dailySales`, `totalRevenue` and `salesTrendVOList` are computed over this range. Default `past_30_days`. Options: `past_7_days` / `past_30_days` / `past_60_days` / `past_90_days` / `past_180_days` / `past_365_days`.

**Sales & price currency**: `price` is in Russian rubles (₽), indicated by `currency`. `totalSales` is units over the window; `dailySales` is the average units/day; `totalRevenue` is revenue over the window.

**Listing age**: `upTime` is the listing timestamp (ms); `upDays` / `upMonths` are the derived age in days / months.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sku | string | yes | Ozon product SKU (e.g. `175924376`). The same `sku` from other Seerfar Ozon tools. |
| dateRange | string | no | Sales/metrics window. Default `past_30_days`. One of: `past_7_days`, `past_30_days`, `past_60_days`, `past_90_days`, `past_180_days`, `past_365_days`. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `sku` is required.

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/productDetailSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-product-detail-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/productDetailSearch",
  "arguments": {
    "sku": "175924376"
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
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项 |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 返回记录数（命中时为 `1`，未命中为 `0`） |
| totalSales | integer | 统计窗口内总销量 |
| dailySales | number | 平均每天销量（≈ totalSales / 窗口天数） |
| totalRevenue | number | 统计窗口内销售额（卢布） |
| stock | integer | 库存 |
| startDate | string | 统计窗口起始日期（如 `2026-06-01`） |
| endDate | string | 统计窗口结束日期（如 `2026-06-30`） |
| salesTrendVOList | array | 每日销量数据序列（见下方） |
| categoryRanks | array | 商品类目排名历史（见下方） |
| products | array | 商品详情列表（单 SKU 查询命中时 1 条，未命中为空） |
| data | array | 返回数据，内容与 `products` 完全一致 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

> 未命中的 SKU：返回成功（`code:"200"`、`errcode:200`），但 `total:0`、`products:[]`，且销量聚合字段（`totalSales` / `dailySales` / `totalRevenue` / `stock` / `startDate` / `endDate`）不返回。判断"商品无数据"应基于 `total=0` 或 `products` 为空，而非 `errcode`。

### products[*] / data[*] 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID，映射自 `sku` |
| title | string | 商品标题 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| reviewRating | number | 商品评分 |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewCount | integer | 评论数 |
| questionsAndAnswers | integer | QA 数量 |
| brandName | string | 品牌名称 |
| brand | string | 统一品牌，映射自 `brandName` |
| brandId | integer | 品牌 ID |
| brandUrl | string | 品牌链接 |
| sellerName | string | 卖家名称 |
| sellerId | integer | 卖家 ID（负值为 Ozon 平台自营卖家，如 `-4` Ozon Россия） |
| fulfillment | array | 商品配送方式，如 `["FBO"]`、`["OZON"]`，可能含多个值 |
| upTime | integer | 上架时间，毫秒时间戳 |
| upDays | integer | 上架天数 |
| upMonths | integer | 上架月数 |
| imageUrl | string | 统一主图 URL，映射自 `imageUrls` 首张 |
| imageUrls | array | 商品图片 URL 列表 |
| productUrl | string | 商品 URL |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目信息（见下方） |
| monthlySalesUnits | integer | 统一月销量，实际取值等于当前统计窗口的 `totalSales` |
| monthlySalesRevenue | number | 统一月销售额，实际取值等于当前统计窗口的 `totalRevenue` |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，标识 Seerfar Ozon 接口（如 `Seerfar-Ozon-查竞品`） |
| weight | number | 商品重量，单位 g（数字/服务类商品可能不返回，见字段差异） |
| grossMargin | number | 毛利率（schema 定义，实测部分商品不返回，见字段差异） |

> **`data` 与 `products`**：两者内容完全一致，单 SKU 查询命中时各含 1 条记录。

### salesTrendVOList[*] 每日销量对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期（如 `2026-06-01`） |
| sales | integer | 当日销量（可能为 `0`） |
| revenue | number | 当日销售额（卢布） |
| price | number | 当日价格（卢布） |
| stock | integer | 当日库存 |
| reviewCount | integer | 截至当日评论数（累计） |
| reviewRating | number | 截至当日评分 |

### categoryRanks[*] 类目排名对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 月份（如 `2026-02`；当月为具体日期 `2026-07-01`） |
| rank | integer | 类目排名 |
| count | integer | 统计计数（以网关实际口径为准） |

> `categoryRanks` 仅含 `date` / `rank` / `count`，不含类目名称；类目名称/路径请取自 `categoryInfo`。

### categoryInfo 类目信息对象

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 类目路径（原文） |
| category | object | 末级类目对象（字段见下方） |
| fullCategoryId | array | 完整类目 ID 路径（字符串数组，根→末级，如 `["99999999", "99999999_200001489", "99999999_200001489_970727001"]`） |

#### category 对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitle | string | 类目中文名 |
| enTitle | string | 类目英文名 |
| title | string | 类目原文标题 |
| level | integer | 类目层级 |
| id | string | 类目 ID |
| pid | string | 父类目 ID |
| crossBorderSellable | boolean | 是否支持跨境销售 |
| disabled | boolean | 是否停用 |


## Usage Examples

**1. Default 30-day detail for a product**
```json
{"sku": "175924376"}
```

**2. Last 7 days (recent momentum)**
```json
{"sku": "175924376", "dateRange": "past_7_days"}
```

**3. Last 90 days (quarterly trend)**
```json
{"sku": "175924376", "dateRange": "past_90_days"}
```

**4. Full year (lifecycle view)**
```json
{"sku": "175924376", "dateRange": "past_365_days"}
```

## How to Build Queries

1. **Resolve the SKU first**: if the user gives a product name, URL or shop rather than a SKU, obtain the `sku` from a listing-level Seerfar Ozon source (shop search / keyword back search / category search / market keyword search) before calling this skill.
2. **Pick `dateRange` by intent**: short windows (`past_7_days` / `past_30_days`) for recent momentum and current stock; long windows (`past_90_days` / `past_180_days` / `past_365_days`) for lifecycle, seasonality and ranking stability.
3. **Read aggregates, then trend**: start with top-level `totalSales` / `dailySales` / `totalRevenue` / `stock` / `categoryRanks` for a snapshot, then drill into `salesTrendVOList` for the daily series.
4. **One SKU per call**: this endpoint takes a single `sku`; to compare products, call once per SKU.

## Display Rules

1. **Present data only**: show the product metrics in a clear layout without subjective advice.
2. **Lead with identity + snapshot**: `title`, `sku`, `price` (₽), `reviewRating` (`reviewCount` reviews, `questionsAndAnswers` Q&A), then the sales snapshot (`totalSales`, `dailySales`, `totalRevenue`, `stock`) and the window (`startDate`–`endDate`).
3. **Category ranks**: `categoryRanks` is a monthly rank history (`{date, rank, count}`) — it has no category name, so show the category path from `categoryInfo` (`titlePath` / `cnTitlePath`) alongside the rank history.
4. **Sales trend**: `salesTrendVOList` is a daily series (`{date, sales, revenue, price, stock, reviewCount, reviewRating}`) — summarize (peak day, trend direction) rather than dumping every row; offer the persisted file for the full series. Some days may have `sales: 0` — treat as no-sales, not missing data.
5. **Seller & brand**: show `sellerName` (`sellerId` — negative means an Ozon platform seller) and `brandName` (`brandId`) so the user can trace the seller/brand.
6. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`, or `["OZON"]` for platform-sold items); join multiple values with `/`.
7. **Listing age**: render `upTime` as a date (ms timestamp) alongside `upDays` / `upMonths`.
8. **Conditional fields**: `weight` (physical goods only) and `grossMargin` are schema-defined but absent for some products (e.g. digital goods / Ozon platform sellers) — show `-` when missing rather than failing. `monthlySalesUnits` / `monthlySalesRevenue` mirror the window's `totalSales` / `totalRevenue` and are safe to read directly.
9. **Empty result**: a non-existent `sku` returns success with `total:0` and empty `products` — tell the user the SKU may be wrong rather than reporting a system error.
10. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain from `msg` / `errmsg` and suggest fixes (check SKU, retry on rate-limit).

## Important Limitations

- **`sku` is required**; omitting it returns a parameter error.
- **Single-SKU endpoint**: returns one product's detail; no batch/list mode. Compare products by calling once per SKU.
- **`dateRange` only affects sales aggregates + trend**: product metadata (title, price, rating, brand, seller, weight, fulfillment) is a point-in-time snapshot, not windowed.
- **Conditional fields**: `weight` (physical goods only) and `grossMargin` are schema-defined but not always returned — absent for digital goods / Ozon platform sellers. `monthlySalesUnits` / `monthlySalesRevenue` are returned and mirror the window's `totalSales` / `totalRevenue`.
- **Sales/revenue are Seerfar model estimates** over the chosen window, not Ozon-official figures.
- **`total` reflects returned record count** (1 when the SKU is found), not a catalog total.

## User Expression & Scenario Quick Reference

**Applicable** — deep-dive on one Ozon product:

| User Says | Scenario |
|-----------|----------|
| "查看这个 Ozon 商品的详情" / "这个 SKU 的数据" | Single product detail |
| "这个竞品最近30天卖了多少" / "日均销量多少" | Sales snapshot (`totalSales` / `dailySales`) |
| "这个商品销售额多少" | Revenue (`totalRevenue`) |
| "这个商品库存多少" | Stock check (`stock`) |
| "这个商品在类目里排第几" | Category rank (`categoryRanks`) |
| "这个商品最近销量趋势" / "哪天卖得最好" | Daily sales trend (`salesTrendVOList`) |
| "这个商品是谁家的/什么品牌" | Seller + brand (`sellerName` / `brandName`) |
| "这个商品上架多久了" | Listing age (`upDays` / `upMonths`) |

**Not applicable** — needs beyond one product's detail:
- A shop's full product catalog → use the Seerfar Ozon shop search skill.
- Discovering Ozon keywords → use market keyword search / keyword mining / keyword back search.
- Browsing the category tree → use category search.
- Multiple products' summary at once → call this skill per SKU, or use a listing-level source.

**Boundary judgment**: if the user already has a specific Ozon SKU (or obtained one from a listing-level source) and wants that product's full metrics — sales, revenue, stock, category rank, trend, brand, seller — start here. If they want to discover products, keywords or shops, route to the corresponding Seerfar Ozon skill first.

## 积分消耗规则

消耗 12 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/linkfox-seerfar-ozon-product-detail-search-api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
