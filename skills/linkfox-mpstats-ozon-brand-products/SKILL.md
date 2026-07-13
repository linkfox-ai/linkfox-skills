---
name: linkfox-mpstats-ozon-brand-products
description: MPSTATS Ozon 俄罗斯站按品牌下钻商品列表。按 Ozon 品牌展示名（俄语/拉丁）返回该品牌下全部商品的销量、销售额、价格、评分、库存、周转、损失销售额等完整指标，支持多维数值筛选、排序、货币换算。用于品牌对标、竞品分析、品牌商品结构研究、ASIN 级（productId 级）爆款拆解。当用户提到 Ozon 品牌下钻、Ozon 品牌商品、Ozon 竞品品牌分析、品牌结构、品牌 SKU、品牌爆款、Ozon 品牌销售、MPSTATS brand, Ozon brand products, brand drill-down, brand competitor analysis, Russian marketplace brand SKUs, brand revenue share 时触发此技能。即使用户未明确说"MPSTATS"，只要意图是按 Ozon 品牌看该品牌下所有商品及其销量/价格/评分表现，也应触发此技能。
---

# MPSTATS Ozon Brand Products

This skill drills into all Ozon (Russia) products sold under a given brand display name, returning each SKU's sales, revenue, price, rating, stock, turnover, lost profit, and more. Built for brand competitor audits, brand SKU structure analysis, and bestseller dissection.

## Core Concepts

**Brand display name**: `brandName` must match what's shown on the Ozon storefront — typically Russian (Cyrillic) or Latin (`adidas`, `Xiaomi`). Do **not** pass a category path, a seller ID, or an internal brand code here. If unsure of the exact spelling, resolve via `mpstats-ozon-product-search` first.

**Filters are AND-combined**: The `filters` array supports multiple numeric conditions ANDed together. Each filter is `{field, op, value, value2?}`. Common fields and operators are in the Filter Reference below.

**Currency & rate**: Default currency is **RUB**. Set `currency: "USD"` (or another code) to have monetary fields converted server-side; `currencyRate` lets you override the default rate if desired.

**FBO / FBS mix**: `includeFbs: true` folds FBS (seller-shipped) stock + sales into the numbers; `false` keeps them FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| brandName | string | yes | Ozon brand display name (Russian or Latin) |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column: `sales`, `revenue`, `final_price`, `balance`, `rating`, ... |
| sortDirection | string | no | `asc` or `desc` |
| currency | string | no | Currency code, default `RUB`; e.g. `USD`, `EUR`, `CNY` |
| currencyRate | integer | no | Custom rate when non-default currency is used |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter conditions (see below) |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales` (monthly units), `final_price` (selling price RUB), `rating` (0-5), `comments` (review count), `balance` (stock), `revenue` (sales amount RUB), `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2` as the upper bound).

## 调用方式

- **API 端点**：`POST /mpstats/ozon/brandProducts`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/mpstats_ozon_brand_products.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-brand-products-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Top-50 by sales for brand `adidas`**
```json
{
  "brandName": "adidas",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 50
}
```

**2. High-rating, mid-price filter**
```json
{
  "brandName": "Xiaomi",
  "filters": [
    {"field": "rating", "op": "GTE", "value": 4.5},
    {"field": "final_price", "op": "BETWEEN", "value": 1000, "value2": 5000}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**3. USD-converted output**
```json
{
  "brandName": "Nike",
  "currency": "USD",
  "sortField": "revenue"
}
```

**4. Include FBS + only in-stock items**
```json
{
  "brandName": "adidas",
  "includeFbs": true,
  "filters": [{"field": "balance", "op": "GT", "value": 0}]
}
```

**5. Lost-profit hunters (out-of-stock pain)**
```json
{
  "brandName": "Nike",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 100000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact brand table** — key columns: `productId`, `title`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `reviewCount`, `balance`, `turnoverDays`, `lostProfit`.
2. **Revenue share context** — `revenueSharePercent` is the SKU's share **within this brand result set**, 0-100; clarify the base when presenting.
3. **Currency labeling** — always state the currency in the table header; if `currency` was overridden, note "已按 USD 换算".
4. **Russian titles** — preserve original; translate on user request.
5. **Pagination** — report total and guide the user to next page or narrower filters when total exceeds the returned page.
6. **No business advice** — present the data; don't project future sales from a snapshot.

## Important Limitations

- **Exact brand-name match** — no fuzzy search; typos return empty results. Verify via `mpstats-ozon-product-search` if unsure.
- **Page cap** — max 100 rows per page; paginate for larger brands.
- **Date window** — `endDate` cannot be today or a future date (T-1 data).
- **Currency conversion** — server-side; historical rates may differ slightly from the user's reference rate.
- **Russian-only titles** — translate only when asked.

## User Expression & Scenario Quick Reference

**Applicable** — Brand-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Show me adidas's top-selling Ozon SKUs" | Brand bestseller drill |
| "What does Xiaomi sell on Ozon, sorted by revenue" | Brand revenue structure |
| "Which brand-X SKUs have rating ≥4.5 and stock >0" | Brand quality filter |
| "Are brand-X's stockouts causing big lost profit" | Lost-profit hunter |
| "Convert brand-X's Ozon sales to USD" | Currency-normalized audit |

**Not applicable** — Needs beyond brand drill-down:

- Unknown exact brand name → first use `mpstats-ozon-product-search`
- Category-level comparison across brands → use `mpstats-ozon-category-products`
- Seller-scoped analysis → use `mpstats-ozon-seller-products`
- Single-SKU time-series → use `mpstats-ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the question centers on **one brand** and you want the per-SKU rollup under it. For "which brand dominates category X" use category drill-down and compare brand rows server-side.

## 积分消耗规则

按动态规则计费：消耗积分 = 12。列表为空返回 0

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
