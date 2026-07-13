---
name: linkfox-mpstats-ozon-product-detail
description: MPSTATS Ozon 俄罗斯站 SKU 全量详情批量查询。一次最多传 100 个 Ozon 商品 ID，返回每个 SKU 的价格、折扣、Ozon Card 价、评分、评论数、库存、销量、销售额、潜在销售额/损失销售额、上架日期、图片等完整商品卡。当用户提到 Ozon 商品详情、Ozon SKU 详情、Ozon 价格/评分/销量/库存核对、批量 Ozon SKU 查询、竞品 Ozon 基础数据拉取、Ozon 竞品卡片、MPSTATS Ozon detail, Ozon SKU detail, Ozon product card, Ozon batch lookup, Russian marketplace product detail 时触发此技能。即使用户未明确说"MPSTATS"，只要意图是按 Ozon SKU 拉取全量商品卡数据，也应触发此技能。
---

# MPSTATS Ozon Product Detail (Batch)

This skill batch-fetches the full product card for one or more Ozon (Russia) SKUs via MPSTATS. Returned fields include price, Ozon Card price, discount, rating, reviews, stock, monthly sales units, monthly sales revenue, lost profit, potential revenue, first listing date, image, and more.

## Core Concepts

**Batch semantics**: Pass up to **100** `productIds` in a single call. The server fans out concurrently and automatically retries each failed SKU once; partial success is allowed, so a mixed list is normal.

**Fulfillment model per SKU**: Each product card carries `deliveryScheme`:
- `FBO` — Fulfillment by Ozon (stock in Ozon warehouses)
- `FBS` — Fulfillment by Seller (seller-shipped)

Pass `includeFbs: true` to allow FBS SKUs and FBS-scoped metrics into the response; `false` (or omitted) keeps the result FBO-centric. This switch applies to the whole batch.

**Previous-period comparison**: The card includes `previousSalesUnits` / `previousRevenue` — sales and revenue from the equal-length period immediately before `[startDate, endDate]` — ready for MoM / period-over-period diffs without extra calls.

**Revenue potential**: `revenuePotential` projects what the SKU could have earned if it had been in stock every day of the window; compare with `monthlySalesRevenue` to quantify stock-out drag, together with `lostProfit` / `lostProfitPercent`.

**Date window**: `startDate` / `endDate` define the period for all period-aggregated metrics. Latest selectable date is **yesterday** (T-1); today and future dates are rejected.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productIds | array<integer\|string> | yes | Ozon SKU list, up to **100** per call |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| includeFbs | boolean | no | `true` to include FBS data; `false` = FBO-only |

## 调用方式

- **API 端点**：`POST /mpstats/ozon/productDetail`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/mpstats_ozon_product_detail.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-product-detail-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Single-SKU detail**
```json
{"productIds": [1786874757]}
```

**2. Batch lookup with period**
```json
{
  "productIds": [1786874757, 151623766, 142257239],
  "startDate": "2025-03-01",
  "endDate": "2025-03-31",
  "includeFbs": true
}
```

**3. FBO-only snapshot**
```json
{"productIds": [1786874757, 151623766], "includeFbs": false}
```

**4. SKUs discovered upstream — full card**
```json
{"productIds": [<list from mpstats-ozon-product-search>]}
```

## How to Chain with Other Ozon Skills

1. **Search → detail**: Use `mpstats-ozon-product-search` to resolve a keyword / brand / seller into `productId`s, then pass them here for full metrics.
2. **Detail vs trend**: This endpoint is a **period aggregate** per SKU; for day-by-day time-series on a single SKU, use `mpstats-ozon-product-trend`.
3. **Detail vs drill-downs**: When the input dimension is a brand / category / seller (not a SKU list), prefer `brand-products` / `category-products` / `seller-products` — they already return aggregated metrics per SKU under that dimension.

## Display Rules

1. **Compact table** — lead with `productId`, `title`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `reviewCount`, `balance`, `deliveryScheme`, `firstDate`. Pull `revenuePotential` / `lostProfit` / `lostProfitPercent` in when the user asks about stock-out impact.
2. **Currency** — Ozon native currency is **RUB**; the `currency` field carries the symbol. Do not silently relabel.
3. **Partial success** — the response carries `successCount` / `failedCount` / `failures`; when `failedCount > 0`, list the failed `productId`s from `failures` to the user rather than silently dropping them.
4. **Period-over-period** — when both current and `previous*` fields are present, render them side-by-side or as diff; don't report a single-period number as "trend".
5. **With-stock vs all-days** — `salesPerDayWithStock` / `dailySalesRevenueWithStock` only count days that had inventory; distinguish from the plain `salesPerDay` / `dailySalesRevenue`.
6. **Delivery model** — prefer the per-SKU `deliveryScheme` value over assuming FBO; remind users when a batch mixes FBO and FBS.
7. **No business advice** — present data; do not extrapolate "this SKU is worth selling" without a wider analysis.

## Important Limitations

- **100-SKU batch cap** — split larger input lists and call multiple times; the Agent must paginate.
- **Ozon-only** — this tool does not cover Wildberries or other Russian marketplaces.
- **T-1 data** — `endDate` must not be today or future.
- **FBS coverage** — some categories have partial FBS coverage; if the input set is FBS-heavy, expect sparser cards.
- **Field set differs from brand/seller** — this endpoint does **not** return `brandId`, `country`, `category`, `minPrice` / `maxPrice` / `averagePrice`, `balanceFbs`, `frozenStocks`, `warehousesCount`, `daysInSite` / `daysInStock` / `turnoverDays`, `position` / `categoryPosition` / `revenueSharePercent`, `isFbs`. Use `brand-products` / `category-products` / `seller-products` if those are needed.
- **No translation** — titles are returned in Russian; translate on demand when presenting to Chinese / English users.

## User Expression & Scenario Quick Reference

**Applicable** — Per-SKU Ozon card lookup:

| User Says | Scenario |
|-----------|----------|
| "Pull Ozon details for these SKUs" | Batch card fetch |
| "What's the price / rating / stock of Ozon SKU 1786874757" | Single-SKU card |
| "Competitor's Ozon listings, give me sales & rating" | Competitor card audit |
| "Compare FBO vs FBO+FBS metrics for this SKU set" | Fulfillment-model comparison |

**Not applicable** — Needs beyond per-SKU card:

- Keyword-based discovery → use `mpstats-ozon-product-search`
- Day-by-day time-series for one SKU → use `mpstats-ozon-product-trend`
- Listing copy / reviews / images analysis beyond URL → out of scope
- Brand / category / seller drill-down with filters → use the matching drill-down skill

**Boundary judgment**: If the user already has a **SKU list** and wants per-SKU sales / price / stock / rating, this is the skill. If they don't yet have SKUs, route through the search or drill-down skills first.

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
