---
name: linkfox-mpstats-ozon-product-search
description: MPSTATS Ozon 俄罗斯站商品搜索与反查。按俄语关键词或 SKU 在 MPSTATS 数据库中检索 Ozon 商品，返回商品 ID、标题、品牌和卖家信息，是 Ozon 选品与竞品链路的起点。当用户提到 Ozon 选品、Ozon 商品搜索、俄罗斯电商选品、Ozon 关键词搜索、Ozon SKU 查询、MPSTATS Ozon、Ozon product search, MPSTATS Ozon, Russian marketplace, Ozon SKU lookup, Ozon keyword search 时触发此技能。即使用户未明确提到"MPSTATS"，只要其意图是在 Ozon 俄罗斯站按关键词或 SKU 发现或反查商品，也应触发此技能。
---

# MPSTATS Ozon Product Search

This skill searches Ozon (Russia) products in the MPSTATS analytics database by Russian keyword or SKU list. It is the **entry point** for Ozon product discovery and competitor lookup — downstream drill-downs (brand/category/seller/detail/trend) typically start from the IDs returned here.

## Core Concepts

**MPSTATS Ozon coverage**: Ozon is Russia's largest general-category marketplace. MPSTATS indexes Ozon product listings and sales history. This endpoint returns the **basic identity card only** — 10 fields: `productId` / `title` / `productPageUrl` / `imageUrl` / `brand` / `brandId` / `sellerName` / `sellerId` plus `sourceType` / `sourceTool`. Per-SKU price / sales / rating / stock / turnover / ranking are **not** returned here — the backend `OzonProductSearchItem` DTO is intentionally narrow. For those metrics, chain into `mpstats-ozon-product-detail` (batch full card, 36 fields) or the `brand/category/seller-products` drill-downs (39 fields).

**Language requirement**: Keywords must be in **Russian** (Cyrillic) — or the Latin-script form actually used on the Ozon storefront. If the user supplies an English or Chinese keyword, translate it to Russian first and note the translation.

**At-least-one input rule**: The input schema marks both filters as optional, but the tool's business rule requires at least one of `keyword` / `productIds` to be supplied. The two can be combined to narrow results. For brand- or seller-scoped discovery, use `mpstats-ozon-brand-products` / `mpstats-ozon-seller-products` instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | conditional | Russian search keyword, e.g., `кроссовки` (sneakers) |
| productIds | array<integer\|string> | conditional | Ozon SKU list |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; defaults to one year ago |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; defaults to yesterday, **cannot** be today or future |

At least one of `keyword` / `productIds` must be supplied. The endpoint returns at most ~36 records in a single call (an upstream-acknowledged cap), and there are no pagination / sort / filter inputs — narrow via keyword/SKU and date window instead.

## 调用方式

- **API 端点**：`POST /mpstats/ozon/productSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/mpstats_ozon_product_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-mpstats-ozon-product-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Usage Examples

**1. Keyword search — sneakers in Russian**
```json
{"keyword": "кроссовки"}
```

**2. SKU batch reverse lookup**
```json
{"productIds": [1786874757, 151623766, 142257239]}
```

**3. Dated window for period-specific search**
```json
{"keyword": "футболка", "startDate": "2025-02-01", "endDate": "2025-02-28"}
```

## How to Chain with Other Ozon Skills

1. **Keyword → drill-down**: Search → pick `productId` → call `mpstats-ozon-product-detail` (batch metrics) or `mpstats-ozon-product-trend` (single-SKU time-series).
2. **Brand drill-down**: For brand-scoped product listings with full metrics, call `mpstats-ozon-brand-products` directly with the brand display name.
3. **Seller drill-down**: For seller-scoped product listings with full metrics, call `mpstats-ozon-seller-products` directly with the seller ID.

## Display Rules

1. **Lead with identity columns** — this endpoint returns only 10 identity fields. Headline the table with `productId`, `title`, `brand`, `sellerName`; include `productPageUrl` / `imageUrl` as secondary columns. Do **not** add price / sales / rating / stock columns — they are not in the response.
2. **Russian titles** — preserve the original Russian title; optionally offer an English or Chinese translation on user request.
3. **Result count** — the endpoint returns at most ~36 records and has no pagination. If `total` exceeds what was returned, suggest narrowing the keyword/SKU set or date window rather than asking for more pages.
4. **Route to drill-downs for any business metric** — business metrics are never in this response. If the user asks for sales / price / rating / stock / turnover / ranking, **always** route to `mpstats-ozon-product-detail` (single or batch) or the `*-products` drill-downs. Do not fabricate or estimate from identity fields.
5. **Error handling** — when `code` / `errcode` is non-200, explain the reason from `msg` / `errmsg` and suggest adjusting inputs (supply at least one of `keyword` / `productIds`, use Russian, narrow date range).

## Important Limitations

- **At least one of `keyword` / `productIds` required** — empty payloads are rejected by the tool's business rule even though `required` is empty in inputSchema.
- **Russian / Latin only** — non-Russian keywords generally return empty results.
- **Date range** — `endDate` cannot be today or a future date; data is T-1.
- **Hard result cap** — upstream returns at most ~36 records per call and exposes no pagination/sort/filter. Cannot be bypassed; narrow the query instead.
- **No business metrics** — price / sales / rating / stock / turnover / ranking are **not** in this endpoint's response at all. The backend `OzonProductSearchItem` DTO declares exactly 10 identity fields. This is a hard contract, not a sparse payload — do not assume missing metric fields could be filled in by re-calling with different dates.

## User Expression & Scenario Quick Reference

**Applicable** — Ozon product discovery / identity resolution:

| User Says | Scenario |
|-----------|----------|
| "Search Ozon for sneakers / headphones / ..." | Keyword discovery |
| "I have a list of Ozon SKUs, pull their names" | Batch SKU reverse lookup |
| "Translate this keyword to Russian and search Ozon" | Cross-language discovery |

**Not applicable** — Needs beyond discovery:

- Reliable per-SKU sales / revenue / stock / rating metrics → use `mpstats-ozon-product-detail` (batch card) or the `*-products` drill-down skills.
- Brand-scoped product listing → use `mpstats-ozon-brand-products` directly.
- Seller-scoped product listing → use `mpstats-ozon-seller-products` directly.
- Time-series trend for a single SKU → use `mpstats-ozon-product-trend`.
- Wildberries or other non-Ozon Russian marketplaces → not covered here.
- Category-tree navigation / Russian category path lookup → use `mpstats-ozon-category-products` with a known path.

**Boundary judgment**: If the user wants to **find or identify** Ozon products, start here. If they already have an ID or a dimension (brand / category / seller) and want **metrics** under it, go to the corresponding drill-down skill directly.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
