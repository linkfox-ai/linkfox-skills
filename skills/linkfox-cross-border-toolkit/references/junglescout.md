# Jungle Scout — Tool Reference

## 1. Keyword by Keyword (关键词拓展)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-keyword`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp`. Default `us` |
| searchTerms | string | Yes | Seed keyword (single keyword string) |

#### Optional — Result Control

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| needCount | int | No | Total number of results to return |
| sort | string | No | Sort field. Default `-monthly_search_volume_exact` (exact search volume desc) |

#### Optional — Search Volume Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minMonthlySearchVolumeExact | int | No | Minimum exact search volume |
| maxMonthlySearchVolumeExact | int | No | Maximum exact search volume |
| minMonthlySearchVolumeBroad | int | No | Minimum broad search volume |
| maxMonthlySearchVolumeBroad | int | No | Maximum broad search volume |

#### Optional — Other Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minWordCount | int | No | Minimum word count (for long-tail keyword filtering) |
| maxWordCount | int | No | Maximum word count |
| minOrganicProductCount | int | No | Minimum organic product count |
| maxOrganicProductCount | int | No | Maximum organic product count |

#### Sort Options

| Value | Description |
|-------|-------------|
| name / -name | Keyword name asc/desc |
| dominant_category / -dominant_category | Dominant category asc/desc |
| monthly_trend / -monthly_trend | Monthly trend asc/desc |
| quarterly_trend / -quarterly_trend | Quarterly trend asc/desc |
| monthly_search_volume_exact / -monthly_search_volume_exact | Exact search volume asc/desc (default: desc) |
| monthly_search_volume_broad / -monthly_search_volume_broad | Broad search volume asc/desc |
| recommended_promotions / -recommended_promotions | Recommended promotions asc/desc |
| sp_brand_ad_bid / -sp_brand_ad_bid | Brand ad bid asc/desc |
| ppc_bid_broad / -ppc_bid_broad | PPC broad bid asc/desc |
| ppc_bid_exact / -ppc_bid_exact | PPC exact bid asc/desc |
| ease_of_ranking_score / -ease_of_ranking_score | Ranking difficulty asc/desc |
| relevancy_score / -relevancy_score | Relevancy score asc/desc |
| organic_product_count / -organic_product_count | Organic product count asc/desc |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| keywordInfoList | array | Keyword info list |

#### keywordInfoList Item

| Field | Type | Description |
|-------|------|-------------|
| name | string | Keyword text |
| country | string | Marketplace code |
| monthlySearchVolumeExact | integer | Monthly exact match search volume |
| monthlySearchVolumeBroad | integer | Monthly broad match search volume |
| monthlyTrend | number | Month-over-month search volume change (%) |
| quarterlyTrend | number | Quarter-over-quarter search volume change (%) |
| dominantCategory | string | Dominant category in search results |
| relevancyScore | integer | Relevancy score to seed keyword |
| easeOfRankingScore | integer | Ease of ranking (higher = easier) |
| organicProductCount | integer | Number of organic products in results |
| sponsoredProductCount | integer | Number of sponsored products in results |
| ppcBidExact | number | Exact match PPC suggested bid (USD) |
| ppcBidBroad | number | Broad match PPC suggested bid (USD) |
| spBrandAdBid | number | Sponsored Brand ad suggested bid (USD) |
| recommendedPromotions | integer | Recommended promotion giveaway count |

### Key Usage Notes

- **Marketplaces**: 10 Amazon sites — us, uk, de, in, ca, fr, it, es, mx, jp. Default `us`.
- **Single keyword per call**: `searchTerms` accepts only one seed keyword.
- Search volume values are monthly estimates, not real-time.
- `easeOfRankingScore`: 1-3 = difficult, 4-6 = moderate, 7-10 = easy.

---

## 2. Keyword by ASIN (ASIN反查关键词)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-asin`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| asins | array\<string\> | Yes | ASIN list, max 10 ASINs |

#### Optional — Result Control

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| needCount | int | No | Total number of results (auto-paginated internally) |
| includeVariants | boolean | No | Include variant product keywords |
| sort | string | No | Sort field. Default `-monthly_search_volume_exact`. See sort options table |

#### Optional — Search Volume Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minMonthlySearchVolumeExact | int | No | Min monthly exact search volume (1-999999) |
| maxMonthlySearchVolumeExact | int | No | Max monthly exact search volume (1-999999) |
| minMonthlySearchVolumeBroad | int | No | Min monthly broad search volume (1-999999) |
| maxMonthlySearchVolumeBroad | int | No | Max monthly broad search volume (1-999999) |

#### Optional — Keyword Feature Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minWordCount | int | No | Min word count (1-99999) |
| maxWordCount | int | No | Max word count (1-99999) |
| minOrganicProductCount | int | No | Min organic search result count (1-99999) |
| maxOrganicProductCount | int | No | Max organic search result count (1-99999) |

#### Sort Options

| Value | Description |
|-------|-------------|
| name / -name | Keyword name asc/desc |
| dominant_category / -dominant_category | Dominant category asc/desc |
| monthly_trend / -monthly_trend | Monthly trend asc/desc |
| quarterly_trend / -quarterly_trend | Quarterly trend asc/desc |
| monthly_search_volume_exact / -monthly_search_volume_exact | Exact search volume asc/desc (default: desc) |
| monthly_search_volume_broad / -monthly_search_volume_broad | Broad search volume asc/desc |
| recommended_promotions / -recommended_promotions | Recommended promotions asc/desc |
| sp_brand_ad_bid / -sp_brand_ad_bid | SP brand ad bid asc/desc |
| ppc_bid_broad / -ppc_bid_broad | PPC broad bid asc/desc |
| ppc_bid_exact / -ppc_bid_exact | PPC exact bid asc/desc |
| ease_of_ranking_score / -ease_of_ranking_score | Ranking difficulty asc/desc |
| relevancy_score / -relevancy_score | Relevancy score asc/desc |
| organic_product_count / -organic_product_count | Organic product count asc/desc |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| keywordInfoList | array | Keyword info list |

#### keywordInfoList Item

| Field | Type | Description |
|-------|------|-------------|
| name | string | Keyword text |
| country | string | Marketplace code |
| monthlySearchVolumeExact | integer | Monthly exact match search volume |
| monthlySearchVolumeBroad | integer | Monthly broad match search volume |
| monthlyTrend | float | Monthly trend (%) |
| quarterlyTrend | float | Quarterly trend (%) |
| dominantCategory | string | Dominant category |
| relevancyScore | integer | Relevancy score to ASIN (0-100) |
| easeOfRankingScore | integer | Ease of ranking (0-100, higher = easier) |
| organicRank | integer | ASIN's organic search rank |
| sponsoredRank | integer | ASIN's sponsored ad rank |
| overallRank | integer | Overall rank position |
| organicProductCount | integer | Total products in organic results |
| sponsoredProductCount | integer | Total products in ad results |
| ppcBidExact | float | Exact match PPC bid (USD) |
| ppcBidBroad | float | Broad match PPC bid (USD) |
| spBrandAdBid | float | SP Brand ad bid (USD) |
| recommendedPromotions | integer | Recommended promotions count |
| primaryAsin | string | Top-ranking ASIN for this keyword |
| relativeOrganicPosition | float | ASIN's relative organic position |
| relativeSponsoredPosition | float | ASIN's relative sponsored position |
| organicRankingAsinsCount | integer | Queried ASINs with organic ranking |
| sponsoredRankingAsinsCount | integer | Queried ASINs with sponsored ranking |
| avgCompetitorOrganicRank | float | Average organic rank of queried ASINs |
| avgCompetitorSponsoredRank | float | Average sponsored rank of queried ASINs |
| variationLowestOrganicRank | integer | Best organic rank among variants |
| variationLowestSponsoredRank | integer | Best sponsored rank among variants |
| competitorOrganicRank | array | Per-ASIN organic ranks: `[{asin, organicRank}]` |
| competitorSponsoredRank | array | Per-ASIN sponsored ranks: `[{asin, sponsoredRank}]` |
| updatedAt | string | Data last updated time |

### Key Usage Notes

- **Max 10 ASINs** per request.
- `marketplace` and `asins` are both required.
- Use `includeVariants: true` to include variant keywords.
- `updatedAt` indicates data freshness; ranking data is not real-time.

---

## 3. Keyword Historical Search Volume (关键词历史搜索量)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/historical-search-volume`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| keyword | string | Yes | Keyword to query |
| startDate | string | Yes | Start date (YYYY-MM-DD) |
| endDate | string | Yes | End date (YYYY-MM-DD); max 366 days from startDate |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| historicalSearchVolumeList | array | Historical search volume periods |

#### historicalSearchVolumeList Item

| Field | Type | Description |
|-------|------|-------------|
| id | string | Period identifier (market/keyword/date range) |
| estimateStartDate | string | 7-day period start date (YYYY-MM-DD) |
| estimateEndDate | string | 7-day period end date (YYYY-MM-DD) |
| estimatedExactSearchVolume | integer | Exact match search volume for that week |
| type | string | Fixed value: `historical_keyword_search_volume` |

### Key Usage Notes

- **All 4 parameters are required**.
- **Max span**: 366 days between startDate and endDate; split into multiple calls if longer.
- **Granularity**: Weekly (7-day periods), not daily.
- Only provides exact match search volume, not broad match.

---

## 4. Keyword Share of Voice (关键词市场份额)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/share-of-voice`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| keyword | string | Yes | Keyword to analyze |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| shareOfVoice | object | Share of Voice data |

#### shareOfVoice Object

| Field | Type | Description |
|-------|------|-------------|
| id | string | Resource identifier |
| type | string | Fixed value: `share_of_voice` |
| estimated30DaySearchVolume | integer | 30-day exact match search volume |
| exactSuggestedBidMedian | number | PPC bid median (USD) |
| productCount | integer | Total products in first 3 pages |
| updatedAt | string | Data update timestamp |
| topAsinsModelStartDate | string | Top ASIN click/conversion data window start |
| topAsinsModelEndDate | string | Top ASIN click/conversion data window end |
| brands | array | Brand SOV breakdown list |
| topAsins | array | TOP 3 ASIN click/conversion list |

#### brands Item

| Field | Type | Description |
|-------|------|-------------|
| brand | string | Brand name |
| organicProducts | integer | Organic listings in first 3 pages |
| sponsoredProducts | integer | Sponsored listings count |
| combinedProducts | integer | Total listings (organic + sponsored) |
| organicBasicSov | number | Organic simple ratio (0–1) |
| organicWeightedSov | number | Organic position-weighted ratio (0–1) |
| sponsoredBasicSov | number | Sponsored simple ratio (0–1) |
| sponsoredWeightedSov | number | Sponsored position-weighted ratio (0–1) |
| combinedBasicSov | number | Combined simple ratio (0–1) |
| combinedWeightedSov | number | Combined position-weighted ratio (0–1) |
| organicAveragePosition | number | Average organic ranking position |
| sponsoredAveragePosition | number | Average sponsored ranking position |
| combinedAveragePosition | number | Average combined ranking position |
| organicAveragePrice | number | Average price of organic products |
| sponsoredAveragePrice | number | Average price of sponsored products |
| combinedAveragePrice | number | Average price of all products |

#### topAsins Item

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| name | string | Product title |
| brand | string | Brand name |
| clicks | integer | Click count (30-day window) |
| conversions | integer | Conversion count (30-day window) |
| conversionRate | number | Conversion rate (0–1) |

### Key Usage Notes

- **One keyword per call**; multi-keyword comparison requires separate calls.
- Covers first 3 pages of search results (~48-60 products).
- SOV is a point-in-time snapshot, not historical trend.
- SOV values are 0–1 decimals; display as percentages (×100).

---

## 5. Product Database (产品数据库)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/product-database/query`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |

#### Keyword Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| includeKeywords | string | No | Title/ASIN include keywords, comma-separated, max 100 items, each max 50 chars |
| excludeKeywords | string | No | Title/ASIN exclude keywords, comma-separated, max 100 items, each max 50 chars |

#### Category Filter

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| categories | string | No | Category names, comma-separated. Must match site standard categories. US examples: Appliances, Arts Crafts & Sewing, Automotive, Baby, Beauty & Personal Care, Books, Cell Phones & Accessories, Clothing Shoes & Jewelry, Computers, Electronics, Garden & Outdoor, Grocery & Gourmet Food, Health Household & Baby Care, Home & Kitchen, Industrial & Scientific, Kitchen & Dining, Office Products, Pet Supplies, Sports & Outdoors, Tools & Home Improvement, Toys & Games, Video Games, etc. |

#### Price / Sales / Revenue

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minPrice | number | No | Minimum price |
| maxPrice | number | No | Maximum price |
| minSales | integer | No | Minimum monthly sales |
| maxSales | integer | No | Maximum monthly sales |
| minRevenue | number | No | Minimum monthly revenue |
| maxRevenue | number | No | Maximum monthly revenue |

#### Reviews / Rating

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minReviews | integer | No | Minimum review count |
| maxReviews | integer | No | Maximum review count |
| minRating | number | No | Minimum rating (1.0-5.0) |
| maxRating | number | No | Maximum rating (1.0-5.0) |

#### Weight / Size / BSR / LQS

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minWeight | number | No | Minimum weight (pounds) |
| maxWeight | number | No | Maximum weight (pounds) |
| minRank | integer | No | Minimum BSR rank |
| maxRank | integer | No | Maximum BSR rank |
| minLqs | integer | No | Minimum LQS score (1-10) |
| maxLqs | integer | No | Maximum LQS score (1-10) |

#### Seller / Product Type

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minSellers | integer | No | Minimum seller count |
| maxSellers | integer | No | Maximum seller count |
| minNet | number | No | Minimum net profit |
| maxNet | number | No | Maximum net profit |
| sellerTypes | string | No | Seller types, comma-separated: `amz` (Amazon self-operated), `fba`, `fbm` |
| productTiers | string | No | Product size tiers, comma-separated: `oversize`, `standard` |
| excludeTopBrands | boolean | No | Exclude top brands |
| excludeUnavailableProducts | boolean | No | Exclude unavailable products |

#### Date / Pagination / Sort

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minUpdatedAt | string | No | Data update start date (YYYY-MM-DD) |
| maxUpdatedAt | string | No | Data update end date (YYYY-MM-DD) |
| needCount | integer | No | Total results to return (auto-paginated internally) |
| sort | string | No | Sort field: `name`, `-name`, `category`, `-category`, `revenue`, `-revenue`, `sales`, `-sales`, `price`, `-price`, `rank`, `-rank`, `reviews`, `-reviews`, `lqs`, `-lqs`, `sellers`, `-sellers`. Prefix `-` = descending. Default: `name` |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| productDatabaseList | array | Product data list |

#### productDatabaseList Item

| Field | Type | Description |
|-------|------|-------------|
| id | string | Product identifier |
| title | string | Product title |
| brand | string | Brand name |
| category | string | Primary category |
| breadcrumbPath | string | Full category path |
| price | number | Current price (USD) |
| approximate30DayUnitsSold | integer | Estimated 30-day sales |
| approximate30DayRevenue | number | Estimated 30-day revenue (USD) |
| productRank | integer | BSR rank |
| reviews | integer | Total reviews |
| rating | number | Average rating (1.0-5.0) |
| listingQualityScore | integer | LQS (1-10) |
| numberOfSellers | integer | Number of sellers |
| sellerType | string | Seller type (amz/fba/fbm) |
| imageUrl | string | Product main image URL |
| dateFirstAvailable | string | First available date |
| weightValue | number | Product weight |
| weightUnit | string | Weight unit |
| lengthValue | number | Length |
| widthValue | number | Width |
| heightValue | number | Height |
| dimensionsUnit | string | Dimensions unit |
| parentAsin | string | Parent ASIN |
| isParent | boolean | Is parent product |
| isVariant | boolean | Is variant product |
| isStandalone | boolean | Is standalone product |
| isAvailable | boolean | Is available for purchase |
| buyBoxOwner | string | Buy Box holder name |
| buyBoxOwnerSellerId | string | Buy Box holder seller ID |
| updatedAt | string | Data update time |
| feeBreakdown | object | Fee details: `fbaFee`, `referralFee`, `variableClosingFee`, `totalFees` |
| subcategoryRanks | array | Sub-category BSR ranks: `[{subcategory, rank, id}]` |
| type | string | Resource type |
| variants | array | Variant list |
| upcList | array | UPC codes |
| eanList | array | EAN codes |
| isbnList | array | ISBN codes |
| gtinList | array | GTIN codes |
| dateFirstAvailableIsEstimated | boolean | Whether first available date is estimated |

### Key Usage Notes

- `marketplace` is the only required parameter; all others are optional filters.
- `categories` must match the site's standard category names exactly.
- Keywords: max 100 items, each max 50 characters.
- Weight is in pounds; rating is 1.0-5.0.
- Internal auto-pagination: specify `needCount` for total desired results.

---

## 6. Sales Estimates (ASIN销售估算)

**Endpoint**: `POST https://tool-gateway.linkfox.com/tool-jungle-scout/sales-estimates/query`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Target marketplace code. Values: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| asin | string | Yes | Amazon ASIN to query |
| startDate | string | Yes | Start date (YYYY-MM-DD) |
| endDate | string | Yes | End date (YYYY-MM-DD); must be earlier than today |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Tokens consumed |
| salesEstimateList | array | Sales estimate results |

#### salesEstimateList Item

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Queried ASIN |
| id | string | Data point identifier |
| type | string | Fixed value: `sales_estimate_result` |
| parentAsin | string | Parent ASIN (for variants) |
| isParent | boolean | Is parent product |
| isVariant | boolean | Is variant product |
| isStandalone | boolean | Is standalone product |
| variants | array | Variant ASIN array |
| dailyEstimates | array | Daily estimate data |

#### dailyEstimates Item

| Field | Type | Description |
|-------|------|-------------|
| date | string | Date (YYYY-MM-DD) |
| estimatedUnitsSold | integer | Estimated units sold that day |
| lastKnownPrice | number | Last known price (USD) |

### Key Usage Notes

- **All 4 parameters are required**.
- **endDate must be before today** — cannot query today or future dates.
- **One ASIN per call**; compare multiple ASINs with separate calls.
- Daily granularity; price is in USD.

---

## Common Error Codes (All Jungle Scout Tools)

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse response data normally |
| 401 | Auth failure | Check `Authorization` header with correct API Key |
| Other | Business error | Refer to `errmsg` field for details |

## Supported Marketplaces (All Jungle Scout Tools)

| Marketplace | Code |
|-------------|------|
| United States | us |
| United Kingdom | uk |
| Germany | de |
| India | in |
| Canada | ca |
| France | fr |
| Italy | it |
| Spain | es |
| Mexico | mx |
| Japan | jp |
