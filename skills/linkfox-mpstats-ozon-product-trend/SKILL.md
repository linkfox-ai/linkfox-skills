---
name: linkfox-mpstats-ozon-product-trend
description: MPSTATS Ozon 俄罗斯站单个 SKU 的分日时间序列表现。按日期粒度返回一个 Ozon 商品的销量、价格、库存、评分等指标，可选附带搜索位次/可见性数据，用于验证增长趋势、季节性、异常波动。当用户提到 Ozon 趋势、Ozon 销量趋势、Ozon 价格走势、Ozon 分日数据、Ozon 库存走势、Ozon 搜索位次、Ozon 商品历史、MPSTATS trend, Ozon daily performance, Ozon time series, Ozon search visibility, Russian marketplace product history 时触发此技能。即使用户未明确说"MPSTATS"，只要意图是看某个 Ozon 商品的分日/时间段走势，也应触发此技能。
---

# MPSTATS Ozon Product Trend (Daily Time-Series)

This skill returns a daily time-series of a single Ozon (Russia) SKU — sales units, price, stock, rating, and optionally search-position / visibility metrics. It is the go-to for validating growth, seasonality, or anomalies for a specific product.

## Core Concepts

**Single-SKU scope**: Each call analyzes exactly **one** `productId`. For batch per-SKU snapshots (period aggregates), use `mpstats-ozon-product-detail` instead.

**Daily granularity**: The response is an array of daily points (top-level field `data`) across the `[startDate, endDate]` window. Each point carries a `hasData` boolean — if `hasData=false`, the day has no observation (distinct from `sales=0` with `hasData=true`).

**T-1 delay**: MPSTATS trend data is delayed by one day; the latest selectable end date is **yesterday**. Today or future dates are rejected.

**Search-visibility add-on**: Set `includeSearchStats: true` to append search-position / visibility signals. Some niches (especially small categories) may not have search-stats coverage — expect partial or empty fields in those cases.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productId | integer | yes | Ozon SKU (numeric) |
| startDate | string | no | Window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Window end, `YYYY-MM-DD`; latest = yesterday |
| includeFbs | boolean | no | Include FBS data alongside FBO |
| includeSearchStats | boolean | no | Attach search position / visibility signals |

## 调用方式

- **API 端点**：`POST /mpstats/ozon/productTrend`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/mpstats_ozon_product_trend.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-product-trend-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Usage Examples

**1. Monthly trend for a SKU**
```json
{
  "productId": 1786874757,
  "startDate": "2025-03-01",
  "endDate": "2025-03-31"
}
```

**2. Trend with search visibility**
```json
{
  "productId": 1786874757,
  "startDate": "2025-02-01",
  "endDate": "2025-02-28",
  "includeSearchStats": true
}
```

**3. Combined FBO+FBS trend**
```json
{
  "productId": 151623766,
  "startDate": "2025-01-01",
  "endDate": "2025-01-31",
  "includeFbs": true
}
```

## How to Chain with Other Ozon Skills

1. **Discovery → trend**: Use `mpstats-ozon-product-search` to find a SKU, then check growth / volatility here before committing.
2. **Aggregate vs time-series**: `mpstats-ozon-product-detail` gives a one-number-per-metric period view; this skill shows the day-by-day shape behind those numbers.
3. **Drill-down → trend**: After `brand-products` / `category-products` / `seller-products` surfaces a hot SKU, use this skill to validate whether the hotness is recent, seasonal, or sustained.

## Display Rules

1. **Prefer a simple table or sparkline-friendly output** — one row per date with `date`, `price`, `sales`, `balance`, `rating`, `comments`; do not overfit a 90-point series into a single paragraph.
2. **Use `hasData` to distinguish gaps from zero sales** — `hasData=false` means the day has no observation; don't report it as a zero-sale day.
3. **Call out anomalies** — large single-day spikes or stockouts (`balance=0` runs where `hasData=true`) should be flagged factually, not as buying advice.
4. **Currency is RUB** unless upstream layer is already converting (the `currency` field per point carries the symbol, e.g. `₽`); state the currency when showing price movement.
5. **Revenue is not returned per day** — if the user asks for daily revenue, estimate via `sales * price` and note it's an estimate.
6. **`includeSearchStats` gaps** — when no search-visibility fields come back, note "搜索位次数据在该赛道暂不可用" rather than silently omitting.
7. **No business advice** — present the shape; leave "should we buy this listing?" to the user.

## Important Limitations

- **Single SKU per call** — cannot pass a list of `productId`s; loop at the Agent layer if needed.
- **T-1 data** — `endDate` cannot be today or a future date.
- **Search stats optional** — `includeSearchStats=true` doesn't guarantee coverage for all niches.
- **Ozon-only** — Wildberries and other Russian marketplaces are not covered.
- **Missing days** — the series may have nulls / gaps where no data was captured; do not treat nulls as zero sales.

## User Expression & Scenario Quick Reference

**Applicable** — Single-SKU temporal analysis:

| User Says | Scenario |
|-----------|----------|
| "What's the sales trend of Ozon SKU 1786874757 last month" | Monthly time-series |
| "Is this Ozon listing seasonal or stable" | Seasonality check |
| "Did this Ozon product have stockouts recently" | Stock anomaly detection |
| "Price walk for this Ozon product over Q1" | Price movement |
| "Did this listing's search position improve" | Search visibility (requires `includeSearchStats`) |

**Not applicable** — Needs beyond single-SKU time-series:

- Batch snapshot of many SKUs → `mpstats-ozon-product-detail`
- Brand / category / seller drill-down → matching `*-products` skill
- Pre-IDed discovery → `mpstats-ozon-product-search`

**Boundary judgment**: Use this skill when the question starts with "how did this ONE product change over time". For multi-SKU comparisons or dimension-level filtering, go elsewhere.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
