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

## 调用方式

- **API 端点**：`POST /seerfar/ozon/categorySearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_category_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-category-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
