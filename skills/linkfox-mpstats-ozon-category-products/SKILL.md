---
name: linkfox-mpstats-ozon-category-products
description: MPSTATS Ozon 俄罗斯站按俄语类目路径下钻该类目全部商品。返回每个 SKU 的销量、销售额、价格、评分、库存、周转、损失销售额等完整指标，支持多维数值筛选、排序、货币换算。用于类目爆款挖掘、蓝海洞察、类目排名分析、品牌格局观察。当用户提到 Ozon 类目下钻、Ozon 类目商品、Ozon 蓝海挖掘、Ozon 品类爆款、Ozon 类目排名、Ozon 子类目结构、Ozon 赛道 SKU、MPSTATS category, Ozon category drill-down, Russian marketplace niche, Ozon niche mining, Ozon subcategory bestseller 时触发此技能。即使用户未明确说"MPSTATS"，只要意图是按 Ozon 类目路径查看该类目下所有商品的销量/价格/排名表现，也应触发此技能。
---

# MPSTATS Ozon Category Products

This skill drills into all Ozon (Russia) products under a given Russian category path, returning each SKU's sales, revenue, price, rating, stock, turnover, lost profit, and more. Designed for category bestseller mining, blue-ocean niche discovery, and brand-landscape scanning within a specific category.

## Core Concepts

**Russian full-path requirement**: `categoryPath` must be the **full Russian category path** as used on the Ozon platform, with levels separated by `/` — for example, `Одежда/Женская одежда/Футболки и топы женские`. A partial path, English translation, or root-only value will generally return empty results.

**Where to find the path**: Typical workflows resolve the path via an upstream Ozon category-search step (if available in your toolchain) or by pulling a known SKU's `category` field from `mpstats-ozon-product-detail` / `mpstats-ozon-product-search`.

**Filters are AND-combined**: `filters` carries multi-field numeric conditions, each `{field, op, value, value2?}`. See the Filter Reference.

**Currency**: Default `RUB`. Override with `currency` (USD, EUR, CNY, ...) and optionally `currencyRate`.

**FBO / FBS**: `includeFbs: true` folds FBS into stock / sales numbers; `false` keeps FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| categoryPath | string | yes | Full Russian category path separated by `/` |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column: `sales`, `revenue`, `final_price`, `balance`, `rating`, ... |
| sortDirection | string | no | `asc` / `desc` |
| currency | string | no | Currency code, default `RUB` |
| currencyRate | integer | no | Custom rate when non-default currency is used |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter list (see below) |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales` (monthly units), `final_price` (price RUB), `rating` (0-5), `comments` (reviews), `balance` (stock), `revenue` (amount RUB), `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2`).

## 调用方式

- **API 端点**：`POST /mpstats/ozon/categoryProducts`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/mpstats_ozon_category_products.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-category-products-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Usage Examples

**1. Women's T-shirts — top by sales**
```json
{
  "categoryPath": "Одежда/Женская одежда/Футболки и топы женские",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 100
}
```

**2. Blue-ocean hunt (sales ≥ 50, rating ≥ 4.5)**
```json
{
  "categoryPath": "Одежда/Женская одежда/Футболки и топы женские",
  "filters": [
    {"field": "sales", "op": "GTE", "value": 50},
    {"field": "rating", "op": "GTE", "value": 4.5}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**3. Mid-price + strong turnover**
```json
{
  "categoryPath": "Электроника/Наушники",
  "filters": [
    {"field": "final_price", "op": "BETWEEN", "value": 1500, "value2": 5000},
    {"field": "turnover_days", "op": "LTE", "value": 30}
  ]
}
```

**4. USD-converted ranking for cross-market comparison**
```json
{
  "categoryPath": "Электроника/Смартфоны",
  "currency": "USD",
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**5. High lost-profit category scan**
```json
{
  "categoryPath": "Одежда/Мужская одежда/Куртки мужские",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 500000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact category table** — key columns: `productId`, `title`, `brand`, `sellerName`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `balance`, `position`, `revenueSharePercent`.
2. **Revenue share = within this category query** — 0-100%; clarify the basis when presenting.
3. **Russian titles / brands** — preserve original; translate on demand.
4. **Currency labeling** — state the currency; if converted, note `"已按 USD 换算"`.
5. **Pagination** — report `total`; for large categories (tens of thousands of SKUs) suggest tightening filters rather than naively paging through.
6. **Category position** — lower is better; mention this when showing `categoryPosition`.

## Important Limitations

- **Russian full path only** — partial or translated paths return empty.
- **Path discovery is upstream** — this endpoint does not browse the category tree; resolve the path via product detail / search first.
- **Page cap** — max 100 rows per page.
- **T-1 data** — `endDate` cannot be today or a future date.
- **No business advice** — data-only view.

## User Expression & Scenario Quick Reference

**Applicable** — Category-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Bestsellers in category X on Ozon" | Category bestseller mining |
| "Find blue-ocean SKUs in niche Y" | Blue-ocean niche scan |
| "Show mid-price, fast-turnover items in this category" | Multi-criteria niche filter |
| "Which brands dominate this Ozon category" | Brand-landscape pre-cut (then group by brand client-side) |
| "Huge lost-profit opportunities in category X" | Out-of-stock pain hunting |

**Not applicable** — Needs beyond category drill-down:

- Unknown category path → use `mpstats-ozon-product-search` or product detail to discover the exact Russian path
- Brand-scoped drill → `mpstats-ozon-brand-products`
- Seller-scoped drill → `mpstats-ozon-seller-products`
- Single-SKU time-series → `mpstats-ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the **dimension is a category path** and you want the per-SKU roll-up under it. For cross-category comparisons you must run multiple calls and fuse results at the Agent layer.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
