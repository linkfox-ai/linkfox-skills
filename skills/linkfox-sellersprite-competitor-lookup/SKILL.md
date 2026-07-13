---
name: linkfox-sellersprite-competitor-lookup
description: 使用卖家精灵数据在亚马逊上查找和分析竞品，覆盖12个站点，包含销量、BSR、定价、评分和增长趋势等商品指标。当用户提到竞品查询、竞品分析、ASIN反查、竞争商品研究、查找相似商品、市场竞品发现、商品对标、竞品销量估算、分析竞争Listing、competitor analysis, ASIN reverse lookup, competitor sales, competitor research, SellerSprite, market competitor discovery, competitor trends时触发此技能。即使用户未明确提及"卖家精灵"或"竞品查询"，只要其需求涉及通过ASIN、关键词、卖家名称、品牌或品类发现和分析亚马逊竞品，也应触发此技能。
---

# SellerSprite Competitor Lookup

This skill guides you on how to query and analyze Amazon competitor product data, helping Amazon sellers discover competing products, benchmark performance, and extract actionable competitive intelligence.

## Core Concepts

The SellerSprite Competitor Lookup tool provides comprehensive Amazon product data across 12 marketplaces. It allows querying products by ASIN, keyword, seller name, brand, or category, and returns detailed metrics including monthly sales volume, revenue, BSR ranking, pricing, ratings, and growth trends.

**Data snapshots**: The tool supports both real-time data (last 30 days) and historical monthly snapshots. Use `nearly` (default) for current data or a `yyyyMM` format (e.g., `202501`) for historical snapshots. Historical snapshots capture all active listings for that month, enabling year-over-year and seasonal comparisons.

**Category hierarchy**: Amazon category names support multi-level paths separated by colons (`:`). For example, `Electronics:Computers & Accessories:Monitors`. Convert user-provided category descriptions into the proper colon-separated format.

## Supported Marketplaces

US (United States), UK (United Kingdom), DE (Germany), FR (France), JP (Japan), CA (Canada), IT (Italy), ES (Spain), MX (Mexico), AU (Australia), TR (Turkey), IN (India)

Default marketplace is **US**. Use US when the user does not specify a marketplace.

## Parameter Guide

### Search Filters

| Parameter | Description | Example |
|-----------|-------------|---------|
| marketplace | Amazon marketplace code | `US`, `UK`, `DE`, `JP` |
| keyword | Search keyword (translate to the marketplace language) | `wireless earbuds` |
| asinList | One or more ASINs, comma-separated (max 40) | `B072MQ5BRX,B08N5WRWNW` |
| sellerName | Seller name to filter by | `Anker Direct` |
| brand | Brand name to filter by | `Anker` |
| nodeLabel | Amazon category name (colon-separated levels) | `Electronics:Headphones` |
| nodeIdPath | Amazon category ID path | `172282` |
| matchType | Keyword match mode: 1 = phrase, 2 = fuzzy, 3 = exact (default 1) | `1` |
| showVariation | Show product variations: `Y` or `N` (default `N`) | `N` |
| dataSnapshotMonth | Data snapshot month (`nearly` for real-time, or `yyyyMM`) | `nearly` |

### Pagination & Sorting

| Parameter | Description | Example |
|-----------|-------------|---------|
| page | Page number, starting from 1 | `1` |
| size | Results per page, 10-100 (default 50) | `50` |
| order.field | Sort field (see sort options below) | `total_units` |
| order.desc | Sort direction: `true` = descending, `false` = ascending | `true` |

### Sort Field Options

| Field | Description |
|-------|-------------|
| total_units | Monthly sales units |
| total_amount | Monthly sales revenue |
| bsr_rank | BSR ranking |
| price | Price |
| rating | Rating score |
| reviews | Number of reviews |
| profit | Gross margin |
| reviews_rate | Review rate |
| available_date | Listing date |
| questions | Q&A count |
| total_units_growth | Monthly sales unit growth rate |
| total_amount_growth | Monthly revenue growth rate |
| reviews_increasement | Monthly new reviews |
| bsr_rank_cv | 7-day BSR growth count |
| bsr_rank_cr | 7-day BSR growth rate |
| amz_unit | Variant sales units |

### Key Response Fields

| Field | Description |
|-------|-------------|
| asin | Product ASIN |
| title | Product title |
| price | Current price |
| monthlySalesUnits | Monthly sales volume |
| monthlySalesRevenue | Monthly sales revenue |
| bsr | BSR ranking |
| bsrGrowthRate | BSR growth rate |
| bsrGrowthCount | BSR growth count |
| rating | Rating score |
| ratings | Number of ratings |
| ratingsGrowth | Monthly new ratings |
| ratingsRate | Review rate |
| brand | Brand name |
| sellerName | BuyBox seller |
| sellerNation | BuyBox seller nationality |
| fulfillment | Fulfillment type (AMZ/FBA/FBM) |
| availableDateString | Listing date |
| profit | Gross margin |
| nodeLabelPath | Category path |
| imageUrl | Product image URL |
| monthlySalesUnitsGrowthRate | Monthly sales growth rate |
| listingQualityScore | Listing quality score |
| variationNum | Number of variations |
| parent | Parent ASIN |
| badgeBestSeller | Best Seller badge (Y/N) |
| badgeAmazonChoice | Amazon's Choice badge (Y/N) |
| badgeEbc | A+ Content (Y/N) |
| badgeVideo | Video present (Y/N) |

## 调用方式

- **API 端点**：`POST /sellersprite/competitor-lookup`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sellersprite_competitor_lookup.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-competitor-lookup-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Look up competitors by ASIN**
```json
{
  "marketplace": "US",
  "asinList": "B072MQ5BRX,B08N5WRWNW"
}
```
Use case: Analyze specific competing products by their ASINs.

**2. Search competitors by keyword**
```json
{
  "marketplace": "US",
  "keyword": "wireless earbuds",
  "matchType": 1,
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
Use case: Discover top-selling products for a keyword, sorted by monthly sales.

**3. Filter by brand and category**
```json
{
  "marketplace": "US",
  "brand": "Anker",
  "nodeLabel": "Electronics:Headphones",
  "order": {"field": "total_amount", "desc": "true"}
}
```
Use case: Analyze a specific brand's product lineup within a category.

**4. Find products by seller name**
```json
{
  "marketplace": "DE",
  "sellerName": "Anker Direct",
  "order": {"field": "bsr_rank", "desc": "false"}
}
```
Use case: View all products from a particular seller sorted by BSR.

**5. Historical snapshot comparison**
```json
{
  "marketplace": "US",
  "keyword": "space heater",
  "dataSnapshotMonth": "202412",
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
Use case: Analyze seasonal product performance using historical data snapshots.

**6. Show product variations**
```json
{
  "marketplace": "JP",
  "asinList": "B0XXXXXXXXX",
  "showVariation": "Y"
}
```
Use case: Examine all variation-level data for a product family.

## Display Rules

1. **Present data clearly**: Show query results in well-formatted tables. Include key metrics such as ASIN, title, price, monthly sales, BSR, rating, and brand. Do not provide subjective business advice unless the user asks for it.
2. **Keyword language**: When searching by keyword, always translate the keyword to the target marketplace language (e.g., English for US/UK, German for DE, Japanese for JP). Remind the user of this if they provide keywords in the wrong language.
3. **BSR clarification**: When displaying BSR data, remind users that a lower BSR value indicates stronger sales performance.
4. **Growth metrics**: When showing growth rates, clarify whether positive values mean improvement or decline (positive BSR growth count means BSR increased, which means worsened ranking).
5. **Pagination notice**: When the total result count exceeds the returned page size, inform the user of the total count and offer to fetch additional pages.
6. **Badge highlights**: When products carry badges (Best Seller, Amazon's Choice, A+ Content, Video), highlight these in the results as they are important competitive signals.
7. **Error handling**: When a query fails, explain the reason based on the `message` field and suggest adjusting query parameters.
8. **Snapshot guidance**: When users want to do seasonal or trend analysis, proactively suggest using historical snapshots (e.g., last year's same month) for comparison.
## Important Limitations

- **Result cap**: Each page returns 10-100 records (controlled by `size`). Use pagination for larger result sets.
- **ASIN limit**: A maximum of 40 ASINs can be queried at once via `asinList`.
- **Historical snapshots**: Only existing monthly snapshots can be queried; future dates are not supported.
- **Keyword language**: Keywords should match the marketplace language for best results.

## User Expression & Scenario Quick Reference

**Applicable** -- Amazon competitor product data queries:

| User Says | Scenario |
|-----------|----------|
| "Find competitors for this ASIN" | ASIN-based competitor lookup |
| "Top sellers for wireless earbuds" | Keyword-based product discovery |
| "What is this seller selling" | Seller product portfolio analysis |
| "Show me products in Electronics category" | Category-based browsing |
| "Monthly sales for these ASINs" | Sales estimation for specific products |
| "New products gaining traction" | Growth trend detection |
| "Compare products across brands" | Brand benchmarking |
| "How was this niche last December" | Historical snapshot analysis |
| "Best sellers with high ratings" | Multi-metric filtering |
| "FBA vs FBM in this category" | Fulfillment type analysis |

**Not applicable** -- Needs beyond competitor product data:

- ABA search term data or keyword ranking (use ABA Data Explorer instead)
- Advertising / PPC campaign management
- Product reviews content or sentiment analysis
- Listing copywriting or optimization suggestions
- Supplier sourcing or manufacturing costs
- Account health or policy compliance

## 积分消耗规则

消耗 15 积分。

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
