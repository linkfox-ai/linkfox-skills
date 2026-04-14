---
name: linkfox-sorftime-product-detail
description: 基于Sorftime数据按ASIN查询亚马逊产品详情与历史趋势，涵盖14个站点。当用户提到Sorftime产品详情、ASIN详情查询、销量走势、价格曲线、价格历史、BSR排名历史、BSR趋势、利润分析、FBA费用分析、毛利率、产品趋势分析、日销量月销量、销售额趋势、Deal促销历史、product detail, sales trend, price history, BSR ranking, profit analysis, FBA fees时触发此技能。即使用户未明确提及"Sorftime"，只要其需求涉及按ASIN查询亚马逊产品详情或历史趋势数据，也应触发此技能。
---

# Sorftime Product Detail

This skill guides you on how to query Amazon product detail and historical trend data by ASIN via Sorftime, helping Amazon sellers analyze product performance, pricing strategy, and competitive positioning.

## Core Concepts

Sorftime Product Detail provides comprehensive product-level data by ASIN, with historical trend data going back to 2021. It covers sales volume & revenue trends, price & promotion tracking, multi-level BSR ranking history, and real-time profit analysis with FBA fee breakdown.

**Key differentiator**: This tool returns trend/time-series data for individual products. If you need to search/filter products across a category, brand, or seller, use the Sorftime Product Search skill instead.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Product Title | title | Product listing title | Anker Portable Charger... |
| Brand | brand | Brand name | Anker |
| ASIN | asin | Amazon Standard Identification Number | B0088PUEPK |
| Parent ASIN | parentAsin | Parent ASIN if has variations, null otherwise | B0088PUEPK |
| Category | category | Main category [name, NodeId] | ["Cell Phones", "2811119011"] |
| Sub-category Rankings | bsrCategory | Sub-category rank list with nodeId, name, rank, date | [{nodeId, name, rank, date}] |
| Listing Date | availableDate | Listing date (yyyy-MM-dd) | 2022-03-15 |
| Days Online | onlineDays | Days since listing | 850 |
| Sale Price | price | Sale price after Coupon, local currency (e.g., USD) | 25.99 |
| Coupon | coupon | >0 = discount amount (500=$5); <0 = percentage (-10=10% off) | -15 |
| Platform Fee | platformFee | Platform commission, local currency | 3.90 |
| FBA Fees | fbaFees | FBA fulfillment fee, local currency | 5.40 |
| FBA Detail | fbaDetail | FBA breakdown: [delivery fee, month:storage fee, ...] | [475, "1-9:5", "10-12:15"] |
| Profit | profitAmount | Sale price - FBA - commission, local currency | 16.69 |
| Profit Rate | profitRate | Profit margin, e.g., 25.83 = 25.83% | 25.83 |
| BSR Rank | salesRank | Best Seller Rank in main category | 1523 |
| BSR Trend | rankTrend | Main category rank history, interleaved [date, rank, ...] | [20250101, 1523, ...] |
| Sub-BSR Trend | bsrRankTrend | Sub-category rank history per node | [{NodeId, Rank: [...]}] |
| Rating | rating | Current rating (0.0-5.0) | 4.70 |
| Rating Count | ratings | Number of ratings | 12580 |
| Star Distribution | fiveStarRatings / fourStar... / oneStar... | Star percentage, e.g., 57.7 = 57.7% | 57.7 |
| Daily Sales Trend | listingSalesVolumeOfDailyTrend | Interleaved [date, volume, ...]; -1 = cannot estimate | [20250101, 150, ...] |
| Monthly Sales Trend | listingSalesVolumeOfMonthTrend | Interleaved [date, volume, ...]; -1 = cannot estimate | [20250101, 4500, ...] |
| Daily Revenue Trend | listingSalesOfDailyTrend | Interleaved [date, revenue, ...]; unit = cents; -1 = N/A | [20250101, 38985, ...] |
| Monthly Revenue Trend | listingSalesOfMonthTrend | Interleaved [date, revenue, ...]; unit = cents; -1 = N/A | [20250101, 1169550, ...] |
| Price Trend | priceTrend | Sale price history; unit = cents; -1 = no price that day | [20250101, 2599, ...] |
| List Price Trend | listPriceTrend | Strikethrough price history; unit = cents; -1 = N/A | [20250101, 3999, ...] |
| Buybox Seller | buyboxSeller | Buybox winning seller name | AnkerDirect |
| Seller Country | buyboxSellerAddress | Seller country code (CN, US, etc.); null if Amazon-operated | CN |
| FBA Status | isFBA | Whether Buybox seller uses FBA | true |
| Seller Count | sellerNum | Number of sellers on this listing | 3 |
| A+ Content | aPlus | Has A+ content | true |
| Video | hasVideo | Has video on listing | true |
| Brand Store | hasBrandStore | Has brand storefront | true |
| Weight | weight | Weight in grams | 350 |
| Size | size | Dimensions in cm [longest, 2nd, shortest] | [18.5, 8.2, 3.1] |

## Supported Marketplaces

US (United States), GB (United Kingdom), DE (Germany), FR (France), IN (India), CA (Canada), JP (Japan), ES (Spain), IT (Italy), MX (Mexico), AE (United Arab Emirates), AU (Australia), BR (Brazil), SA (Saudi Arabia)

Default marketplace is **US**. Use `us` when the user doesn't specify a marketplace.

**Note**: Sorftime uses lowercase codes (e.g., `us`, `gb`, `de`), and UK is coded as `gb` (not `uk`).

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/sorftime_product_detail.py` directly to run queries.

## How to Build Queries

The key parameters are `asin` and `marketplace` (both required), plus optional trend date range controls.

### Principles for Building Queries

1. **Always specify the marketplace**: Use lowercase site codes, e.g., `us`, `de`, `jp`
2. **Choose trend inclusion carefully**: Default includes trends (last 15 days). Set `includeTrend: 2` if only basic product info is needed — this saves cost and speeds up response
3. **Specify date range for historical analysis**: Use `queryTrendStartDate` and `queryTrendEndDate` (yyyy-MM-dd) when users need trends beyond the default 15 days. Be aware this costs double
4. **Batch ASINs when comparing**: Up to 10 ASINs can be queried at once, comma-separated — use this for competitive comparison rather than calling one at a time

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

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Price unit awareness**: Trend data uses smallest currency unit (cents for USD). Convert to standard currency when displaying to users
4. **Sales estimation caveat**: Values of `-1` in sales/revenue fields mean "cannot estimate" — explain this to the user rather than showing -1 directly
5. **Trend visualization**: When showing trend data, present key data points in a readable table rather than dumping raw arrays
6. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria

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

**Not applicable** - Needs beyond single-product detail:
- Searching/filtering products across a category or brand (use Sorftime Product Search)
- ABA search term ranking data (use ABA Data Explorer)
- Advertising / PPC strategy
- Product reviews content analysis
- Patent or trademark checks

**Boundary judgment**: When users say "product analysis" or "competitor comparison", if it boils down to checking specific ASINs' detail data and trend curves, then this skill applies. If they're asking to discover or filter products across a market, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
