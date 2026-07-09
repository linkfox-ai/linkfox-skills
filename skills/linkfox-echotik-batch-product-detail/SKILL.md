---
name: linkfox-echotik-batch-product-detail
description: 批量查询TikTok商品详情数据，包括多周期销量与GMV（1天/7天/15天/30天/60天/90天/累计）、直播销量与直播GMV、带货视频与达人数据、播放量、价格、评分、评论数、佣金比例及上下架/全托管状态，支持通过商品ID或TikTok Shop商品URL批量获取。当用户提到TikTok商品详情、批量查询TikTok商品、TikTok商品销量分析、TikTok商品GMV、TikTok直播销量、TikTok带货数据、TikTok商品价格评分、批量获取TikTok商品信息、EchoTik商品详情、TikTok product detail, batch product lookup, TikTok sales analysis, TikTok GMV, TikTok live sales, TikTok influencer data时触发此技能。即使用户未明确提及"EchoTik"，只要其需求涉及根据商品ID或商品URL批量获取TikTok商品的详细销售与营销数据，也应触发此技能。
---

# EchoTik TikTok Batch Product Detail

This skill guides you on how to fetch detailed performance metrics for a batch of TikTok Shop products, helping sellers and operators compare candidate products side-by-side using sales, GMV, live-stream, video, and influencer data.

## Core Concepts

This tool retrieves full detail metrics for up to **1000** TikTok Shop products in a single call. You identify products by ID and/or by TikTok Shop product URL; the backend extracts the `productId` from each URL and merges it with any IDs you supplied, then returns per-product analytics.

**Input options** (at least one is needed; both can be combined):
- `productIds` — array of TikTok product IDs
- `productUrls` — array of TikTok Shop product URLs (e.g. `https://shop.tiktok.com/us/pdp/<slug>/<productId>?...`); the trailing `productId` is extracted from each URL

**Multi-period metrics**: Sales, GMV, live count, video count, influencer count, and views are each reported across `1d / 7d / 15d / 30d / 60d / 90d` windows plus a cumulative total, so you can read both recent momentum and long-run totals.

**Prices are in USD**: `minPrice`, `maxPrice`, and `spuAvgPrice` are USD values.

**Status flags** (integers): `salesTrendFlag` — `0`=stable, `1`=rising, `2`=falling; `isSShop` — fully-managed (全托管) shop; `offMark` — delisted; `freeShipping` — free shipping.

**vs. search**: This is detail **lookup for known products** (you already have IDs/URLs). To *discover* products by keyword, use `linkfox-echotik-product-search`; for new-product rankings use `linkfox-echotik-new-product-rank`.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| productIds | array&lt;string&gt; | No* | TikTok product IDs (up to 1000 items) | - |
| productUrls | array&lt;string&gt; | No* | TikTok Shop product URLs; the `productId` is extracted from each and merged with `productIds` (up to 1000 items) | - |

\* At least one of `productIds` / `productUrls` must be provided; both can be passed together.

## 调用方式

- **API 端点**：`POST /echotik/batchProductDetail`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/echotik_batch_product_detail.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-batch-product-detail-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Batch lookup by product IDs**
```json
{
  "productIds": ["1729382310407603945", "1729382310407603946"]
}
```

**2. Batch lookup by product URLs**
```json
{
  "productUrls": [
    "https://shop.tiktok.com/us/pdp/phone-case/1729382310407603945",
    "https://shop.tiktok.com/us/pdp/case-for-phone/1729382310407603946"
  ]
}
```

**3. Mixed IDs and URLs (merged server-side)**
```json
{
  "productIds": ["1729382310407603945"],
  "productUrls": ["https://shop.tiktok.com/us/pdp/phone-case/1729382310407603946"]
}
```

## Display Rules

1. **Present a comparison table**: Show one row per product with key columns — name, price (USD), total sales, 30-day sales, total GMV, rating, review count, commission rate, and number of promoting influencers
2. **Multi-period context**: When comparing momentum, surface the relevant window (e.g. 7d/30d) alongside the cumulative total rather than only the total
3. **Currency**: Prices are in USD; label them as USD
4. **Commission formatting**: Display `productCommissionRate` as a percentage (e.g. `0.05` → "5%")
5. **Trend flag**: Render `salesTrendFlag` as stable/rising/falling for quick scanning
6. **Status badges**: Mark `isSShop` (全托管), `offMark` (delisted), and `freeShipping` where relevant so users don't compare a delisted product unknowingly
7. **Image reference**: If `imageUrl` / `productImageUrls` is present, mention that images are available
8. **Long descriptions**: `descDetail` can be long HTML/text — summarize or note its availability instead of dumping it
9. **Missing product handling**: If a requested product returns no record, list which IDs/URLs had no data so the user can verify them
10. **Error handling**: When a query fails, explain the reason from the `errmsg`/`error` field and suggest checking the IDs/URLs

## Important Limitations

- **Batch cap**: Up to 1000 products per request
- **Pricing currency**: All price fields are in USD
- **Estimated data**: Sales, GMV, and attribution figures are analytics estimates, not exact platform figures
- **Lookup only**: This tool does not search by keyword or category — it resolves specific IDs/URLs you already have

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Look up the details for these TikTok products" | Batch detail by product IDs |
| "Pull sales data for these TikTok links" | Batch detail by product URLs |
| "Compare the GMV of these TikTok products" | Batch lookup, surface GMV columns |
| "Which of these TikTok products are trending up" | Batch lookup, read `salesTrendFlag` |
| "Are any of these TikTok products delisted / 全托管" | Batch lookup, read `offMark` / `isSShop` |
| "Get live-stream sales for these TikTok products" | Batch lookup, surface live sales/GMV |

### Not Applicable Scenarios

- Discovering products by keyword (use `linkfox-echotik-product-search`)
- New / trending product rankings (use `linkfox-echotik-new-product-rank`)
- Promotional videos linked to a product (use `linkfox-echotik-product-video`)
- Resolving a TikTok video download link (use `linkfox-echotik-get-video-download-url`)
- TikTok creator/influencer profile analytics
- Non-TikTok platform product data

### Boundary Judgment

When users say "analyze these TikTok products", check whether they already have specific product IDs or TikTok Shop URLs (this skill) or want to *find* products by keyword/category (the search skill). If they paste a list of IDs/URLs and want sales/GMV/livestream details, this skill applies. If they ask "what should I sell on TikTok" or "find trending products", it does not.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
