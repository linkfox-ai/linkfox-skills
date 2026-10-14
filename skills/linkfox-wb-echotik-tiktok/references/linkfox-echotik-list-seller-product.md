# linkfox-echotik-list-seller-product 子能力归档

---
name: linkfox-echotik-list-seller-product
description: 查询某个TikTok Shop店铺（卖家）的在售商品列表，通过sellerId获取该店铺全部商品，返回商品标题、价格、多周期(1天/7天/15天/30天/60天/90天/总)销量与销售额(GMV)、评分、评论数、佣金比例、上架时间、带货方式、品类等指标。当用户提到TikTok店铺商品、TikTok店铺在售商品、TikTok卖家商品列表、TikTok店铺选品、查看TikTok店铺卖什么、TikTok店铺商品分析、EchoTik店铺商品、TikTok Shop seller products, TikTok store products, TikTok seller product list, EchoTik store product list时触发此技能。即使用户未明确提及"EchoTik"或"TikTok"，只要其需求涉及查看某个TikTok Shop店铺（已知sellerId）的在售商品及其销量/价格/佣金表现，也应触发此技能。
---

# EchoTik TikTok Seller Product List

This skill lists the in-store products of a single TikTok Shop seller (store) by its `sellerId`, helping cross-border sellers and marketers see exactly what a store sells and how each product performs — multi-period sales and GMV, price, rating, reviews, and commission rate.

## Core Concepts

EchoTik is a TikTok Shop analytics platform. Given a store's `sellerId`, this tool returns that store's product catalog with per-product metrics: title, image, price (and SPU average / min / max), sales volume and GMV across 1d/7d/15d/30d/60d/90d/total windows, rating, review count, commission rate, listing date, sales channel, and category.

**Where to get a `sellerId`**: Obtain it from the **EchoTik TikTok Seller Search** skill (`linkfox-echotik-list-seller`), which lists and filters TikTok Shop stores by region, category, GMV, trend, and store type; or from the **EchoTik TikTok Seller Detail** skill (`linkfox-echotik-seller-detail`).

**Pagination quirk**: `pageSize` must be a multiple of 10 (max 100). The official upstream API caps a single page at 10; this tool internally pulls multiple pages of 10 and merges them, so `pageSize=50` returns up to 50 merged products.

## Data Fields

The response's `products` array contains product objects. Key fields:

| Field | Description |
|-------|-------------|
| productId / asin | Product unique ID |
| title / productName | Product title |
| imageUrl / coverUrl | Product image URL |
| productImageUrls | Product image URL list |
| price | Product price |
| spuAvgPrice | SPU average price |
| minPrice / maxPrice | Min / max price |
| currency | Currency |
| totalSaleCnt | Total sales volume |
| totalSale1dCnt / 7dCnt / 15dCnt / 30dCnt / 60dCnt / 90dCnt | Sales volume (1d/7d/15d/30d/60d/90d, incremental) |
| totalSaleGmvAmt | Total GMV (revenue) |
| totalSaleGmv1dAmt / 7dAmt / 15dAmt / 30dAmt / 60dAmt / 90dAmt | GMV (1d/7d/15d/30d/60d/90d, incremental) |
| monthlySalesUnits | Monthly sales |
| productRating | Product rating |
| ratings / reviewCount | Review count |
| productCommissionRate | Commission rate (decimal, e.g. 0.05 = 5%) |
| categoryName / categoryIds | Product category name / ID list |
| salesFlagText | Main sales channel (video/livestream) |
| salesTrendFlagText | Sales trend |
| firstCrawlDt / availableDate | Listing date (YYYYMMDD integer / date string) |
| discount / offMarkText / freeShippingText | Discount / promo mark / free-shipping flag |
| isSShopText | S-store flag |
| salePropsInfo | Sales attribute info (variants: propId/propName/propValue) |
| region | Marketplace code |
| sourceTool / sourceType | Source tool / type |

Top-level fields: `errcode`, `errmsg`, `total`, `columns`, `type`, `costToken`.

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| sellerId | string | Yes | - | TikTok Shop store ID. Obtain from the Seller Search / Seller Detail skill. Max length 1000 |
| sellerProductSortField | integer | No | 1 | Sort field: 1=total sales, 2=total GMV, 3=SPU avg price, 4=7-day sales, 5=7-day GMV |
| sortType | integer | No | 1 | Sort order: 0=ascending, 1=descending |
| pageNum | integer | No | 1 | Page number (starts at 1) |
| pageSize | integer | No | 50 | Page size — must be a multiple of 10, max 100 |

## MCP 调用

- 响应字段来源：`skills/linkfox-echotik-list-seller-product/references/api.md`。仅从该文件核对本 reference 的响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`echotik/listSellerProduct`
- `arguments`：直接使用下方请求参数组成的 JSON 对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "echotik/listSellerProduct",
  "arguments": {
    "sellerId": "7495514739648989419",
    "pageNum": 1,
    "pageSize": 20
  }
}
```

## 解决认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 缺失、MCP 连接 401、下游业务 401、402/积分不足、403 和其他错误。WorkBuddy 自动授权，不要求用户提供 Key、token、手机号或 Authorization。

## Usage Examples

**1. List a store's top products by total sales**
```json
{
  "sellerId": "7495514739648989419",
  "sellerProductSortField": 1,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

**2. Rank a store's products by 7-day GMV (recent momentum)**
```json
{
  "sellerId": "7495514739648989419",
  "sellerProductSortField": 5,
  "sortType": 1
}
```

**3. Cheapest products in a store (price ascending)**
```json
{
  "sellerId": "7495514739648989419",
  "sellerProductSortField": 3,
  "sortType": 0
}
```

## Display Rules

1. **Present data clearly**: Show products in a table with key columns — product image, title, price, total sales, 30-day sales/GMV, rating, review count, and commission rate
2. **Sales & GMV granularity**: When relevant, show total sales and total GMV; mention multi-period breakdowns (1d/7d/15d/30d/60d/90d) are available in the saved JSON
3. **Commission formatting**: Display `productCommissionRate` as a percentage for readability (e.g. show 0.05 as "5%")
4. **Currency awareness**: Include the `currency` field when displaying prices and GMV
5. **Image reference**: When `imageUrl` is present, surface it so the user can visually compare products
6. **Result count**: Always inform the user of `total` records and the current page; suggest pagination or tighter sorting when the result set is large
7. **No secondary processing**: Results are live queries, not stored in a database; secondary SQL/data processing is not available

## Important Limitations

1. **sellerId required**: `sellerId` is mandatory; obtain it from the EchoTik TikTok Seller Search skill (`linkfox-echotik-list-seller`) or Seller Detail skill (`linkfox-echotik-seller-detail`), or a known store link/ID.
2. **Store-scoped only**: This lists one store's products; to discover/filter products across all TikTok Shop, use the EchoTik TikTok Product Search skill (`linkfox-echotik-list-product`).
3. **pageSize rule**: Must be a multiple of 10 (max 100). Other values may be rejected or adjusted.
4. **Listing date format**: `firstCrawlDt` uses `YYYYMMDD` integers (e.g. `20240504`).
5. **No region/keyword filter**: This tool only takes a `sellerId` and sort/pagination — it does not accept keyword, region, or category filters (the store's marketplace is inferred from the seller).
6. **Data real-time nature**: Results are live queries, not stored in a database; secondary SQL/data processing is not available.

## User Expression & Scenario Quick Reference

**Applicable** — See what a specific TikTok Shop store sells:

| User Says | Scenario |
|-----------|----------|
| "TikTok店铺商品" / "TikTok store products" | List a store's products by sellerId |
| "这个TikTok店铺在卖什么" | View a store's product catalog |
| "查看这家TikTok店铺的商品" | Deep-dive a store found via search/detail |
| "TikTok店铺销量最高的商品" | Sort store products by total sales |
| "TikTok店铺近期爆款" | Sort by 7-day sales/GMV |
| "这家店哪些商品佣金高" | Review commission rate per product |

**Not applicable** — Needs beyond one store's product list:

- Discovering/filtering products across all TikTok Shop (use EchoTik TikTok Product Search)
- Listing or filtering TikTok Shop stores (use EchoTik TikTok Seller Search)
- A single store's full profile (use EchoTik TikTok Seller Detail)
- TikTok creator/influencer or video analytics
- Amazon, Shopee, or other non-TikTok platform data

**Boundary judgment**: When users say "这个店铺卖什么" or "查看店铺商品" with a known store (sellerId or store link), this skill applies. If they want to search products across TikTok Shop by keyword/region/category, use the Product Search skill instead.

## 积分消耗规则

消耗 5 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*

---

## API 详细归档

# EchoTik-TikTok店铺商品列表 API 参考

## MCP 调用（API 归档）

- 响应字段来源：`skills/linkfox-echotik-list-seller-product/references/api.md`。仅从该文件核对本 reference 的响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`echotik/listSellerProduct`
- `arguments`：直接使用下方请求参数组成的 JSON 对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "echotik/listSellerProduct",
  "arguments": {
    "sellerId": "7495514739648989419",
    "pageNum": 1,
    "pageSize": 20
  }
}
```

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sellerId | string | 是 | - | 店铺ID（TikTok Shop 小店ID）。最大长度 1000。从「EchoTik TikTok 店铺搜索」或「EchoTik TikTok 店铺详情」技能的返回结果获取 |
| sellerProductSortField | integer | 否 | 1 | 列表排序字段：1=总销量(total_sale_cnt)、2=总销售额(total_sale_gmv_amt)、3=SPU平均价格(spu_avg_price)、4=7天销量(total_sale_7d_cnt)、5=7天销售额(total_sale_gmv_7d_amt) |
| sortType | integer | 否 | 1 | 排序顺序：0=升序(asc)、1=降序(desc) |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；官方接口单页上限10，内部按10每页多次拉取后合并 |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功（详见下方错误码） |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| products | array | 店铺商品列表（详见下方商品字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品唯一标识ID |
| asin | string | 产品ID（同 productId） |
| title / productName | string | 商品名称 |
| imageUrl | string | 商品图片URL |
| coverUrl | string | 封面图URL |
| productImageUrls | array | 商品图片URL列表 |
| price | number | 商品价格 |
| spuAvgPrice | number | SPU平均价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币 |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 1天内总销量(增量) |
| totalSale7dCnt | integer | 7天内总销量(增量) |
| totalSale15dCnt | integer | 15天内总销量(增量) |
| totalSale30dCnt | integer | 30天内总销量(增量) |
| totalSale60dCnt | integer | 60天内总销量(增量) |
| totalSale90dCnt | integer | 90天内总销量(增量) |
| monthlySalesUnits | integer | 月销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 1天内总销售额(增量) |
| totalSaleGmv7dAmt | number | 7天内总销售额(增量) |
| totalSaleGmv15dAmt | number | 15天内总销售额(增量) |
| totalSaleGmv30dAmt | number | 30天内总销售额(增量) |
| totalSaleGmv60dAmt | number | 60天内总销售额(增量) |
| totalSaleGmv90dAmt | number | 90天内总销售额(增量) |
| productRating | number | 商品评分 |
| ratings | integer | 评论数 |
| reviewCount | integer | 评论数量 |
| productCommissionRate | number | 商品佣金比例（小数，如 0.05 表示 5%） |
| categoryName | string | 商品品类名称 |
| categoryIds | array | 商品品类ID列表 |
| salesFlagText | string | 带货方式 |
| salesTrendFlagText | string | 销售趋势标记 |
| firstCrawlDt | integer | 上架日期（yyyyMMdd 格式，如 20240504） |
| availableDate | string | 上架时间(时间戳/日期) |
| discount | string | 折扣信息 |
| offMarkText | string | 是否有优惠标记 |
| freeShippingText | string | 是否包邮 |
| isSShopText | string | 是否S店 |
| salePropsInfo | array | 销售属性信息（含 propId/propName/salePropValues[propValueId/propValue/image]） |
| region | string | 区域代码 |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errcode 字段区分（errcode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数校验错误 | 参数取值非法（如 `sellerId` 为空、`pageSize` 非10倍数）。参考 `errmsg` 获取具体字段与合法值集合 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 参数示例

使用本 reference 上方的完整 `proxy_call` 参数；不得改用旧 HTTP 示例或旧查询脚本。

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-echotik-list-seller-product",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`linkfox-echotik-list-seller-product`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise


