---
name: linkfox-sorftime-amazon-product-detail
description: "基于Sorftime数据按ASIN查询亚马逊产品详情与历史趋势，涵盖14个站点。当用户提到Sorftime产品详情、ASIN详情查询、销量走势、价格曲线、价格历史、BSR排名历史、BSR趋势、利润分析、FBA费用分析、毛利率、产品趋势分析、日销量月销量、销售额趋势、Deal促销历史、product detail, sales trend, price history, BSR ranking, profit analysis, FBA fees时触发此技能。即使用户未明确提及\"Sorftime\"，只要其需求涉及按ASIN查询亚马逊产品详情或历史趋势数据，也应触发此技能。"
---

# Sorftime Product Detail

This skill guides you on how to query Amazon product detail and historical trend data by ASIN via Sorftime, helping Amazon sellers analyze product performance, pricing strategy, and competitive positioning.

## Core Concepts

Sorftime Product Detail provides comprehensive product-level data by ASIN, with historical trend data going back to 2021. It covers sales volume & revenue trends, price & promotion tracking, multi-level BSR ranking history, and real-time profit analysis with FBA fee breakdown.

**Key differentiator**: This tool returns trend/time-series data for individual products. If you need to search/filter products across a category, brand, or seller, use the Sorftime Product Search skill instead.

## Data Fields

Response data covers the following categories (see `references/api.md` for complete field reference):

- **Basic info**: title, brand, ASIN, listing URL, images (main + A+), store name, bullet points, product badges, off-sale status, last update date, weight, size
- **Variations**: parent ASIN, variation count, child ASINs, variation attributes
- **Pricing & profit**: sale price, coupon, platform fee, FBA fees (with detail breakdown), FBM shipping cost, profit amount & rate
- **Sales**: official monthly sales (Amazon-published)
- **Rankings**: BSR rank, category tree, sub-category rankings, listing date, days online
- **Ratings**: rating score, rating count, star distribution (1-5 star percentages)
- **Seller**: Buybox seller name/ID/country, FBA status, seller count
- **Listing features**: A+ content, video, brand store, feature ratings, product info, properties
- **Promotions**: brand promotion, deal type, extra savings
- **Trends** (time-series): BSR rank, sub-BSR rank, daily/monthly sales volume, daily/monthly revenue, price, list price, deal status

## Supported Marketplaces

US (United States), GB (United Kingdom), DE (Germany), FR (France), IN (India), CA (Canada), JP (Japan), ES (Spain), IT (Italy), MX (Mexico), AE (United Arab Emirates), AU (Australia), BR (Brazil), SA (Saudi Arabia)

Default marketplace is **US**. Use `us` when the user doesn't specify a marketplace.

**Note**: Sorftime uses lowercase codes (e.g., `us`, `gb`, `de`), and UK is coded as `gb` (not `uk`).

## 调用方式

- **API 端点**：`POST /sorftime/amazon/productDetail`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sorftime_product_detail.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-amazon-product-detail-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## How to Build Queries

The key parameters are `asin` and `marketplace` (both required), plus optional trend date range controls.

### Principles for Building Queries

1. **Always specify the marketplace**: Use lowercase site codes, e.g., `us`, `de`, `jp`
2. **Choose trend inclusion carefully**: Default includes trends (last 15 days). Set `includeTrend: 2` if only basic product info is needed - this saves cost and speeds up response
3. **Specify date range for historical analysis**: Use `queryTrendStartDate` and `queryTrendEndDate` (yyyy-MM-dd) when users need trends beyond the default 15 days. Be aware this costs double
4. **Batch ASINs when comparing**: Up to 10 ASINs can be queried at once, comma-separated - use this for competitive comparison rather than calling one at a time

### Query Examples for Common Scenarios

**1. Quick product check (default 15-day trend)**
```
asin: B00FLYWNYQ, marketplace: us
```

**2. Long-range trend analysis (specify dates)**
```
asin: B00FLYWNYQ, marketplace: us
queryTrendStartDate: 2025-01-01, queryTrendEndDate: 2025-03-31
```

**3. Batch ASIN comparison**
```
asin: B0088PUEPK,B00U26V4VQ,B0CVM8TXHP, marketplace: us
```

**4. Product info only, no trends**
```
asin: B0088PUEPK, marketplace: us, includeTrend: 2
```

**5. BSR ranking history (German market)**
```
asin: B00FLYWNYQ, marketplace: de
queryTrendStartDate: 2024-06-01, queryTrendEndDate: 2025-01-01
```

## Trend Data Interpretation

Trend arrays use an interleaved format: even indices are dates, odd indices are values.

```
[20250101, 150, 20250102, 180, 20250103, 165, ...]
 ^date     ^val ^date     ^val ^date     ^val
```

- **Sales volume/revenue trends**: value of `-1` means "cannot estimate" (e.g., category changed to Amazon Renewed)
- **Price trends**: units are in local currency smallest unit (cents for USD); `-1` means no available price that day
- **BSR rank trends**: for `bsrRankTrend`, format is `[{NodeId: xxx, Rank: [date, rank, ...]}]` per sub-category
- **Deal trend**: value `1` = has active Deal that day, `0` = no Deal

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Price unit awareness**: Trend data uses smallest currency unit (cents for USD). Convert to standard currency when displaying to users
4. **Sales estimation caveat**: Values of `-1` in sales/revenue fields mean "cannot estimate" - explain this to the user rather than showing -1 directly
5. **Trend visualization**: When showing trend data, present key data points in a readable table rather than dumping raw arrays
6. **Off-sale handling**: When `offSale` is true, clearly inform the user the product is currently unavailable/off-sale
7. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria

## Important Limitations

- **Max 10 ASINs** per query
- **Trend cost**: Default returns last 15 days; querying > 15 days costs double
- **Non-structured data**: Results do not support secondary analysis via `_dataQuery_executeDynamicQuery`
- **Sales estimation**: Products in non-standard categories (e.g., Amazon Renewed) may return -1 for sales fields

## User Expression & Scenario Quick Reference

**Applicable** - Product detail and trend queries by ASIN:

| User Says | Scenario |
|-----------|----------|
| "查一下这个ASIN的销量走势" | Sales trend |
| "这个产品最近价格变化如何" | Price history |
| "帮我看看这个产品的利润空间" | Profit analysis |
| "这个ASIN的BSR排名趋势" | Ranking history |
| "对比一下这几个ASIN的数据" | Multi-ASIN comparison |
| "这个产品的FBA费用是多少" | FBA fee breakdown |
| "产品上架多久了，评分怎么样" | Basic product info |
| "这个产品还在售吗" | Off-sale status check |
| "这个产品有没有Deal促销记录" | Deal history |
| "看看这个产品的变体信息" | Variation details |

**Not applicable** - Needs beyond single-product detail:
- Searching/filtering products across a category or brand (use Sorftime Product Search)
- ABA search term ranking data (use ABA Data Explorer)
- Advertising / PPC strategy
- Product reviews content analysis
- Patent or trademark checks

**Boundary judgment**: When users say "product analysis" or "competitor comparison", if it boils down to checking specific ASINs' detail data and trend curves, then this skill applies. If they're asking to discover or filter products across a market, it does not apply.

## 积分消耗规则

按动态规则计费：消耗积分 = Sorftime内部查询次数 × 12。Sorftime内部查询次数：不同查询条件需要的查询次数可能不同，该次数由Sorftime决定。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
