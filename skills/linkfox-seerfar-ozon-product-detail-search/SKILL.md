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

## 调用方式

- **API 端点**：`POST /seerfar/ozon/productDetailSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_product_detail_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-product-detail-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

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

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
