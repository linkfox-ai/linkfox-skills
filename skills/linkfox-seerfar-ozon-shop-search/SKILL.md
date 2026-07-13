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

## 调用方式

- **API 端点**：`POST /seerfar/ozon/shopSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/seerfar_ozon_shop_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-seerfar-ozon-shop-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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
4. **Use `totalSales` for shop-level context**: the response's `totalSales` is the shop's total 30-day sales — a quick health indicator for the whole shop, independent of the current page.

## Display Rules

1. **Present data only**: show the shop's product metrics in a clear table without subjective advice.
2. **Lead with shop context, then product columns**: state `totalSales` (shop 30-day total) first, then a table of `sku`, `price`, `sales`, `reviewRating`, `weight`, `sellerType`, `fulfillment`, `returnCancellationRate`.
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

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
