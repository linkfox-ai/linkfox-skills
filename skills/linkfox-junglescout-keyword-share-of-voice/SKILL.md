---
name: linkfox-junglescout-keyword-share-of-voice
description: Jungle Scout关键词市场份额（Share of Voice）分析，返回亚马逊搜索结果前3页的品牌声量占比（自然/广告/综合）、30天精确搜索量、PPC竞价中位数及TOP3 ASIN点击转化数据，覆盖10个站点。当用户提到品牌市场份额、品牌声量占比、搜索结果品牌分布、Share of Voice、SOV分析、品牌竞争格局、广告位占比、自然排名品牌占比、PPC竞价分析、品牌垄断分析、keyword share of voice, brand visibility, organic vs sponsored share, brand dominance, PPC bid analysis, search result brand distribution, competitive landscape, weighted SOV, top ASIN clicks conversions时触发此技能。即使用户未明确提及"Share of Voice"或"SOV"，只要其需求涉及分析某个亚马逊关键词搜索结果中各品牌的市场占有率或竞争格局，也应触发此技能。
---

# Jungle Scout — 关键词市场份额 Share of Voice

This skill queries Share of Voice (SOV) data for Amazon keywords via the Jungle Scout data source, returning brand visibility distribution across the first 3 pages of search results, along with search volume, PPC bid estimates, and top ASIN click/conversion metrics across 10 Amazon marketplaces.

## Core Concepts

Share of Voice measures **how much of the search results real estate a brand occupies** for a given keyword. Jungle Scout analyzes the first 3 pages of Amazon search results and calculates each brand's presence in three dimensions:

- **Organic SOV**: Brand visibility from organic (non-sponsored) search result positions
- **Sponsored SOV**: Brand visibility from sponsored/advertising placements
- **Combined SOV**: Overall brand visibility merging both organic and sponsored results

Each dimension has two calculation methods:

- **Basic SOV**: Simple product count ratio — number of a brand's products ÷ total products on the 3 pages
- **Weighted SOV**: Position-adjusted ratio that gives higher weight to top positions and factors like Amazon's Choice badge; this is the more meaningful metric for competitive analysis

The tool also returns:

- **30-day exact search volume**: Total estimated searches in the past 30 days
- **PPC bid median**: Median suggested bid for this keyword, useful for advertising cost estimation
- **TOP3 ASIN click & conversion data**: The top 3 ASINs by clicks, with click count, conversion count, and conversion rate

## Data Fields

### brands (Brand SOV Breakdown)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Brand Name | brand | Brand name as shown in search results | Anker |
| Organic Products | organicProducts | Number of organic listings in the first 3 pages | 5 |
| Sponsored Products | sponsoredProducts | Number of sponsored listings | 3 |
| Combined Products | combinedProducts | Total listings (organic + sponsored) | 8 |
| Organic Basic SOV | organicBasicSov | Organic simple ratio (0–1) | 0.083 |
| Organic Weighted SOV | organicWeightedSov | Organic position-weighted ratio (0–1) | 0.112 |
| Sponsored Basic SOV | sponsoredBasicSov | Sponsored simple ratio (0–1) | 0.15 |
| Sponsored Weighted SOV | sponsoredWeightedSov | Sponsored position-weighted ratio (0–1) | 0.18 |
| Combined Basic SOV | combinedBasicSov | Combined simple ratio (0–1) | 0.133 |
| Combined Weighted SOV | combinedWeightedSov | Combined position-weighted ratio (0–1) | 0.152 |
| Organic Avg Position | organicAveragePosition | Average ranking position in organic results | 12.4 |
| Sponsored Avg Position | sponsoredAveragePosition | Average ranking position in sponsored results | 5.0 |
| Combined Avg Position | combinedAveragePosition | Average ranking position across all results | 9.5 |
| Organic Avg Price | organicAveragePrice | Average price of organic products | 29.99 |
| Sponsored Avg Price | sponsoredAveragePrice | Average price of sponsored products | 25.99 |
| Combined Avg Price | combinedAveragePrice | Average price of all products | 28.49 |

### topAsins (TOP 3 ASIN Click & Conversion)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ASIN | asin | Amazon Standard Identification Number | B09V3KXJPB |
| Product Name | name | Product title | Anker Portable Charger... |
| Brand | brand | Product brand | Anker |
| Clicks | clicks | Click count (30-day window) | 15200 |
| Conversions | conversions | Conversion count (30-day window) | 4560 |
| Conversion Rate | conversionRate | Conversion rate (0–1) | 0.30 |

### Top-Level Summary Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ID | id | Resource identifier | — |
| Type | type | Fixed value | share_of_voice |
| 30-Day Search Volume | estimated30DaySearchVolume | Exact search volume over 30 days | 125000 |
| PPC Bid Median | exactSuggestedBidMedian | Median suggested PPC bid (USD) | 1.25 |
| Product Count | productCount | Total products in the first 3 pages | 60 |
| Updated At | updatedAt | Data freshness timestamp | 2026-04-10T00:00:00 |
| Top ASINs Start Date | topAsinsModelStartDate | Click/conversion data window start | 2026-03-11 |
| Top ASINs End Date | topAsinsModelEndDate | Click/conversion data window end | 2026-04-10 |
| Cost Token | costToken | Tokens consumed by this call | 1 |

## Supported Marketplaces

us (United States), uk (United Kingdom), de (Germany), in (India), ca (Canada), fr (France), it (Italy), es (Spain), mx (Mexico), jp (Japan)

Default marketplace is **us**. Use us when the user doesn't specify a marketplace.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/junglescout_keyword_sov.py` directly to run queries.

## How to Build Queries

Only two parameters are needed: `marketplace` and `keyword`.

### Principles for Building API Calls

1. **Marketplace mapping**: "美国站" → `us`, "日本站" → `jp`, "德国站" → `de`; default to `us` when unspecified
2. **Keyword**: Pass the user's keyword as-is (lowercase English preferred)
3. **One keyword per call**: Each request analyzes one keyword; for multi-keyword comparison, make separate calls

### Common Query Scenarios

**1. Brand dominance check — Who owns this keyword?**
```json
{
  "marketplace": "us",
  "keyword": "portable charger"
}
```
Focus on `combinedWeightedSov` to see which brands dominate the search results page.

**2. PPC competitive analysis — Is this keyword worth bidding on?**
```json
{
  "marketplace": "us",
  "keyword": "wireless earbuds"
}
```
Compare `exactSuggestedBidMedian` with the keyword's search volume to gauge cost-efficiency. Check `sponsoredWeightedSov` to see how heavily competitors invest in ads.

**3. Conversion efficiency of top ASINs**
```json
{
  "marketplace": "de",
  "keyword": "kopfhörer kabellos"
}
```
Examine the `topAsins` array to find whether the top-clicked products convert well. High clicks + low conversion rate may indicate opportunity.

**4. Identify market gaps — Are there underserved positions?**
```json
{
  "marketplace": "jp",
  "keyword": "ヨガマット"
}
```
If no single brand has a `combinedWeightedSov` above 0.15, the keyword is fragmented and may be easier to enter. Combine with search volume to assess market size.

**5. Compare organic vs sponsored presence**
```json
{
  "marketplace": "uk",
  "keyword": "running shoes"
}
```
A brand with high `sponsoredWeightedSov` but low `organicWeightedSov` relies heavily on ads; this can inform competitive strategy.

## Display Rules

1. **Brand table**: Show the brands table sorted by `combinedWeightedSov` descending; highlight the **top 5 brands** for quick comprehension
2. **SOV as percentage**: Display SOV values as percentages (multiply by 100), e.g., 0.152 → 15.2%
3. **Context header**: Before the table, show the keyword's 30-day search volume (`estimated30DaySearchVolume`) and PPC bid median (`exactSuggestedBidMedian`) as context
4. **Top ASINs section**: Show the TOP 3 ASIN table separately with click count, conversion count, and conversion rate
5. **Competitive summary**: After the data, provide a brief competitive landscape summary: whether the keyword is dominated by a few brands or fragmented, and note any large gaps between organic and sponsored presence
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **Coverage**: Only the first 3 pages of Amazon search results are analyzed (typically ~48–60 products)
- **Single keyword**: One keyword per API call; multi-keyword comparison requires separate calls
- **SOV is a snapshot**: Data reflects a point-in-time crawl, not a historical trend
- **No historical SOV**: This tool does not provide SOV changes over time; use the keyword history tool for volume trends

## User Expression & Scenario Quick Reference

**Applicable** — Brand market share and competitive analysis on Amazon search results:

| User Says | Scenario |
|-----------|----------|
| "这个词谁占的份额最大" | Brand dominance analysis |
| "这个关键词竞争激不激烈" | Competitive landscape assessment |
| "广告位都被谁占了" | Sponsored SOV analysis |
| "有没有品牌垄断这个词" | Monopoly detection |
| "这个词的PPC出价大概多少" | PPC bid estimation |
| "搜索结果里哪些品牌排前面" | Brand visibility ranking |
| "这个词的转化率高不高" | Top ASIN conversion analysis |

**Not applicable** — Beyond keyword Share of Voice scope:
- Historical search volume trends (use keyword history tool)
- Keyword suggestions / keyword mining (use ABA or keyword explorer tools)
- Product-level sales estimation or review analysis
- Listing optimization or copywriting advice
- Non-Amazon platform data

**Boundary judgment**: When users say "竞争分析", "品牌分析", or "市场格局", if the intent is to understand which brands occupy the search results page for a specific keyword (share of voice / brand distribution), this skill applies. If they want product-level sales data, profit margins, or historical trends, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
