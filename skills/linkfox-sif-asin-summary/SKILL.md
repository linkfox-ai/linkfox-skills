---
name: linkfox-sif-asin-summary
description: 使用SIF（搜索情报框架）数据分析ASIN的流量来源构成与曝光分布，覆盖本期/上期/新进/退出周期对比。当用户提到ASIN流量来源、流量结构分析、自然流量与付费流量占比、曝光得分拆解、周期对比、新进/退出流量词、竞品流量分析、SP广告关键词数量、品牌广告曝光、Amazon's Choice曝光、编辑推荐曝光、Top Rated曝光、视频广告曝光、自然搜索曝光比例、PPC流量来源、促销秒杀流量来源、推荐位结构拆解、ASIN traffic analysis, traffic sources, organic traffic share, ad traffic share, exposure analysis, traffic structure, period-over-period comparison, keyword churn, SIF时触发此技能。即使用户未明确提及"SIF"，只要其需求涉及分析ASIN的流量来源、曝光渠道分布、跨周期对比或竞品流量结构对比，也应触发此技能。
---

# SIF ASIN Summary

This skill guides you on how to query and analyze ASIN-level traffic source data, helping Amazon sellers understand the exposure and traffic structure of any product across multiple channels.

## Core Concepts

SIF (Search Intelligence Framework) ASIN Summary provides a comprehensive breakdown of an ASIN's traffic sources on Amazon. It reveals how a product's total exposure is distributed across organic search, Sponsored Products ads, brand ads, video ads, Amazon's Choice, Editorial Recommendations, and Top Rated recommendations. This is essential for competitive analysis and traffic strategy optimization.

**Exposure score**: A composite metric reflecting the overall visibility of a product across all keywords in a given channel. A higher score means greater exposure. The **exposure ratio** fields show what percentage of total exposure comes from each channel (values range 0~1 or 0~100 depending on the field).

**Traffic keyword count**: The total number of keywords through which a product is discovered, broken down by channel (organic search, SP ads, brand ads, video ads, etc.).

## Data Fields

> Field-name suffixes: `*Prev` = previous-period value; `*In` / `*Out` = keywords entering / exiting this period (for period-over-period comparison).

| Field | API Name | Description |
|-------|----------|-------------|
| ASIN | asin | Amazon Standard Identification Number |
| Product Title | productTitle | Full product title on Amazon |
| Product Category | productCategory | Product category on Amazon |
| Product Price | productPrice | Current listing price |
| Product Image URL | productImageUrl | Main product image link |
| Product Features | productFeatures | Bullet-point product features list |
| Customer Rating Count | customerRatingCount | Total number of customer ratings |
| Product Star Rating | productStarRating | Product star rating (0–5) |
| Product Rating Score | productRatingScore | Product rating score (0–5, as shown on Amazon) |
| Is Variant Product | isVariantProduct | Whether the ASIN is a variant (e.g., different color/size) |
| Recent Monthly Sales Bucket | recentMonthlySalesBucket | Bucketed last-month sales (e.g. `"300+"`, `"1,000+"`) — only populated for keywordSummary path |
| Is Monitored | isMonitored | Whether the ASIN is on the monitoring list |
| Monitoring Start Time | monitoringStartTime | When the ASIN was added to monitoring |
| Data Period Start Date | dataPeriodStartDate | Start date of the returned data period (yyyy-MM-dd) |
| Total Exposure Score | totalExposureScore | Composite exposure score across all channels |
| Total Exposure Score Prev | totalExposureScorePrev | Total exposure score in the previous period |
| Total Traffic Keyword Count | totalTrafficKeywordCount | Total keywords across all channels |
| Total Keywords In / Out / Prev | totalTrafficKeywordCountIn / Out / Prev | New / exited / previous-period counterparts |
| Natural Search Exposure Score | naturalSearchExposureScore | Exposure score from organic search |
| Natural Search Exposure Ratio | naturalSearchExposureRatio | Organic search share of total exposure |
| Natural Search Exposure Score Prev | naturalSearchExposureScorePrev | Previous-period organic exposure score |
| Natural Search Keyword Count | naturalSearchKeywordCount | Keywords found in organic search results |
| Natural Keywords In / Out / Prev | naturalSearchKeywordCountIn / Out / Prev | New / exited / previous-period counterparts |
| SP Ad Exposure Score | sponsoredProductsExposureScore | Exposure score from Sponsored Products ads |
| SP Ad Exposure Ratio | sponsoredProductsExposureRatio | SP ad share of total exposure |
| SP Ad Exposure Score Prev | sponsoredProductsExposureScorePrev | Previous-period SP exposure score |
| SP Ad Keyword Count | sponsoredProductsKeywordCount | Keywords with SP ad placements |
| Brand Ad Exposure Score | brandAdExposureScore | Exposure score from brand ads |
| Brand Ad Exposure Ratio | brandAdExposureRatio | Brand ad share of total exposure |
| Brand Ad Exposure Score Prev | brandAdExposureScorePrev | Previous-period brand ad exposure score |
| Brand Ad Keyword Count | brandAdKeywordCount | Total brand ad keywords |
| Top Brand Ad Keyword Count | topBrandAdKeywordCount | Keywords in top-of-page brand ads |
| Bottom Brand Ad Keyword Count | bottomBrandAdKeywordCount | Keywords in bottom-of-page brand ads |
| Video Ad Exposure Score | videoAdExposureScore | Exposure score from video ads |
| Video Ad Exposure Ratio | videoAdExposureRatio | Video ad share of total exposure |
| Video Ad Exposure Score Prev | videoAdExposureScorePrev | Previous-period video ad exposure score |
| Video Ad Keyword Count | videoAdKeywordCount | Keywords with video ad placements |
| Amazon's Choice Exposure Score | amazonsChoiceExposureScore | Exposure score from AC badge |
| Amazon's Choice Exposure Ratio | amazonsChoiceExposureRatio | AC share of total exposure |
| Amazon's Choice Exposure Score Prev | amazonsChoiceExposureScorePrev | Previous-period AC exposure score |
| Amazon's Choice Keyword Count | amazonsChoiceKeywordCount | Keywords with AC badge |
| AC Keywords In / Out | amazonsChoiceKeywordCountIn / Out | New / exited AC keywords this period |
| Editorial Recommendations Exposure Score | editorialRecommendationsExposureScore | Exposure from editorial recommendations |
| Editorial Recommendations Exposure Ratio | editorialRecommendationsExposureRatio | ER share of total exposure |
| Editorial Recommendations Keyword Count | editorialRecommendationsKeywordCount | Keywords with ER placements |
| Top Rated Exposure Score | topRatedExposureScore | Exposure from Top Rated recommendations |
| Top Rated Exposure Ratio | topRatedExposureRatio | TR share of total exposure |
| Top Rated Keyword Count | topRatedKeywordCount | Keywords with TR placements |
| Frequently Bought Keyword Count | frequentlyBoughtKeywordCount | Keywords in frequently-bought recommendations |
| Recommend Position Exposure Score | recommendPositionExposureScore | Total recommendation-position exposure score |
| Recommend Ad Exposure Score | recommendAdExposureScore | Ad portion of recommendation-position exposure |
| Recommend Non-ad Exposure Score | recommendNonadExposureScore | Non-ad portion of recommendation-position exposure |
| Non-AC Recommend Exposure Score | nonAcRecommendExposureScore | Recommendation-position exposure excluding AC slots |
| Recommend Keyword Count | recommendKeywordCount | Total recommendation-position keywords |
| Recommend Ad Keyword Count | recommendAdKeywordCount | Ad portion of recommendation keywords |
| Recommend Non-ad Keyword Count | recommendNonadKeywordCount | Non-ad portion of recommendation keywords |
| PPC Traffic Sources | ppcTrafficSources | List of paid ad types (SP, Top Brand Ad, Bottom Brand Ad, Video Ad) |
| Natural Search Traffic Sources | naturalSearchTrafficSources | Organic search type markers |
| Amazon Recommendation Sources | amazonRecommendationSources | Recommendation types (Best Seller, AC, ER, TR, TRFOB, etc.) |
| Promotional Deal Sources | promotionalDealSources | Active promotions (Coupon, Limited Time Deal, Lowest Price in 30 Days, etc.) |

## Supported Marketplaces

13 marketplaces: US (United States), UK (United Kingdom), DE (Germany), CA (Canada), JP (Japan), FR (France), ES (Spain), IT (Italy), MX (Mexico), AU (Australia), AE (United Arab Emirates), BR (Brazil), SA (Saudi Arabia).

Default marketplace is **US**. Use US when the user does not specify a marketplace. Codes outside this list will be rejected by the API pattern.

## 调用方式

- **API 端点**：`POST /sif/asinSummary`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sif_asin_summary.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-asin-summary-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Parameter Guide

### searchValue (required)

One or more ASIN codes separated by commas. Maximum 10 ASINs per request.

- Single ASIN: `B0XXXXXXXX`
- Multiple ASINs: `B0XXXXXXXX,B0YYYYYYYY,B0ZZZZZZZZ`

### country (optional)

Marketplace code. Defaults to `US`. See the Supported Marketplaces section for all valid codes.

### Time window (optional)

- `last7d` (boolean, default `true`): Use the latest 7 days. When `false`, the API uses `startDate`/`endDate` to define the window.
- `startDate` (string, `yyyy-MM-dd`): Start date for a custom window. Takes effect when `last7d=false`; if omitted, the system's latest ABA week is used.
- `endDate` (string, `yyyy-MM-dd`): End date paired with `startDate`.

### conditions (optional)

Comma-separated traffic-channel filters. Only returns ASIN-summary rows that have traffic from at least one of the listed channels. Valid values:

- `nf` — natural search
- `sp` — SP ads
- `sb` — SB regular
- `sbv` — video ads (SBV)
- `ad` — any ad traffic
- `acAd` — SP recommendation
- `totalPeriod.in` — newly-entered traffic keywords this period

### sortBy (optional)

Sort field. Leave empty for system default. Valid values:

`totalKeywordNum` (total keyword count), `naturalKeywordNum` (natural keyword count), `brandKeywordNum` (brand ad keyword count), `vedioKeywordNum` (video ad keyword count), `acKeywordNum` (AC keyword count), `erKeywordNum` (ER keyword count), `trKeywordNum` (TR keyword count), `sumScore` (all-keyword total exposure), `totalNfScore` (all natural exposure), `totalSpSocre` (all SP exposure; note the spelling), `totalBrandScore` (all brand ad exposure), `totalVedioScore` (all video ad exposure), `totalAcScore` (all AC exposure), `totalTrScore` (all TR exposure), `totalErScore` (all ER exposure).

### Pagination

- `pageNum`: Page number, defaults to 1
- `pageSize`: Results per page, minimum 10, maximum **10000**, defaults to **10000**

### Sorting

- `desc`: Sort in descending order when `true` (default), ascending when `false`

## Usage Examples

**1. Single ASIN traffic breakdown**
> "Show me the traffic sources for B09V3KXJPB on the US marketplace"

Query with `searchValue = "B09V3KXJPB"`, `country = "US"`.

**2. Multi-ASIN competitor comparison**
> "Compare traffic structures of B09V3KXJPB and B0BN1K7WJP on Amazon US"

Query with `searchValue = "B09V3KXJPB,B0BN1K7WJP"`, `country = "US"`.

**3. Specific marketplace query**
> "Analyze traffic sources for B07XJ8C8F5 on Amazon Japan"

Query with `searchValue = "B07XJ8C8F5"`, `country = "JP"`.

**4. Organic vs paid traffic analysis**
> "What percentage of B09V3KXJPB's exposure comes from organic search vs ads?"

Query the ASIN, then compare `naturalSearchExposureRatio` against `sponsoredProductsExposureRatio`, `brandAdExposureRatio`, and `videoAdExposureRatio`.

**5. Ad channel deep-dive**
> "How many keywords does B0BN1K7WJP advertise on through SP, brand ads, and video ads?"

Query the ASIN and present `sponsoredProductsKeywordCount`, `brandAdKeywordCount`, `topBrandAdKeywordCount`, `bottomBrandAdKeywordCount`, and `videoAdKeywordCount`.

**6. Period-over-period comparison**
> "How did this ASIN's total keywords change compared to last week?"

Query the ASIN and present `totalTrafficKeywordCount` (current), `totalTrafficKeywordCountPrev` (previous), `totalTrafficKeywordCountIn` (new this period), `totalTrafficKeywordCountOut` (exited this period). Do the same for the natural-search variant with the `naturalSearchKeywordCount*` family.

**7. Custom date range**
> "Traffic structure for B0XXX between 2026-03-08 and 2026-03-14"

```
searchValue: "B0XXX", country: "US", last7d: false, startDate: "2026-03-08", endDate: "2026-03-14"
```

**8. Filter by traffic channel and sort by SP exposure**
> "Top SP-running ASINs among my 10 products, sorted by SP exposure"

```
searchValue: "B0A,B0B,...,B0J", conditions: "sp", sortBy: "totalSpSocre", desc: true
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables; separate product metadata, current-period scores, keyword counts, and period-over-period comparison columns into logical groups for readability
2. **Percentage formatting**: When displaying exposure ratios, format them as percentages (e.g., 0.45 as 45.0%) for easier comprehension
3. **Traffic structure summary**: When a user queries a single ASIN, proactively summarize the traffic structure (e.g., "65% organic, 25% SP ads, 10% brand ads") to give an at-a-glance overview
4. **Period annotation**: Whenever showing `*In` / `*Out` / `*Prev` fields, label the period explicitly (e.g., "vs. previous 7 days"; or the resolved `startDate ~ endDate` range). Do not present period-over-period deltas without naming the comparison window.
5. **Competitor comparison layout**: When multiple ASINs are queried, use a side-by-side comparison table so differences are immediately visible
6. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest checking the ASIN validity or marketplace selection
7. **Variant awareness**: If `isVariantProduct` is true, note that the ASIN is a variant and the user may want to also check the parent ASIN for a complete picture.
## Important Limitations

- **ASIN cap per request**: Maximum 10 ASINs can be queried in a single call
- **Page size cap**: Maximum 10000 results per page
- **Marketplace coverage**: 13 marketplaces only — IN / NL / SE / PL / TR / SG are no longer available
- **Snapshot vs window**: Default window is the latest 7 days (`last7d=true`). To query a different window, set `last7d=false` and pass `startDate`/`endDate`
- **Exposure scores are relative**: Scores are useful for cross-channel and cross-ASIN comparison, but are not absolute traffic volumes

## User Expression & Scenario Quick Reference

**Applicable** -- Traffic source and exposure analysis for Amazon ASINs:

| User Says | Scenario |
|-----------|----------|
| "Where does this ASIN's traffic come from" | Traffic source breakdown |
| "How much organic traffic does this product have" | Natural search exposure analysis |
| "Is this competitor running a lot of ads" | SP/brand/video ad exposure check |
| "Compare traffic structures of these ASINs" | Multi-ASIN competitor comparison |
| "Does this product have Amazon's Choice" | AC/ER/TR recommendation check |
| "What ad channels is this ASIN using" | PPC traffic source identification |
| "How many keywords does this ASIN rank for" | Traffic keyword count analysis |
| "Is this product relying on paid or organic traffic" | Organic vs paid traffic split |
| "How did keywords change vs last week" | Period-over-period comparison (In/Out/Prev) |
| "How many new organic keywords did this ASIN get" | New-in keyword count (`naturalSearchKeywordCountIn`) |
| "Pull the numbers for a specific date range" | Custom time window via `startDate`/`endDate` |
| "Rank 10 ASINs by SP exposure" | `sortBy=totalSpSocre` across a batch |

**Not applicable** -- Needs beyond ASIN traffic source data:
- Arbitrary multi-week historical trend curves (this tool exposes current + previous period only; use ABA data for long trends)
- Keyword-level search volume or ranking data for the ASIN (use ABA data or the ASIN-keywords tool instead)
- Sales estimation or revenue analysis
- Listing optimization or copywriting
- Advertising bid or budget recommendations

## 积分消耗规则

消耗 9 积分。

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
