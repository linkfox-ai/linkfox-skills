# Jiimore (极目) — Tool Reference

## 1. Niche Info by Keyword (按关键词查细分市场)

**Endpoint**: `POST https://tool-gateway.linkfox.com/jiimore/getNicheInfoByKeyword`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Search keyword (translate to target marketplace language). Max 1000 chars |

#### Marketplace & Pagination

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| countryCode | string | No | US | Country code: `US`, `JP`, `DE` |
| page | integer | No | 1 | Page number (starts from 1) |
| pageSize | integer | No | 50 | Results per page (10-100) |
| sortField | string | No | unitsSoldT7 | Sort field (see Sorting Options below) |
| sortType | string | No | desc | Sort direction: `desc` or `asc` |

#### Filter Parameters — Product & Pricing

| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| avgPriceMin / avgPriceMax | number | Average price range |

#### Filter Parameters — Search & Sales (7-day)

| Parameter | Type | Description |
|-----------|------|-------------|
| searchVolumeT7Min / searchVolumeT7Max | integer | Weekly search volume range |
| unitsSoldT7Min / unitsSoldT7Max | integer | Weekly units sold range |
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickConversionRateT7Min / clickConversionRateT7Max | number | Weekly click conversion rate (0-1 = 0%-100%) |

#### Filter Parameters — Brand Metrics

| Parameter | Type | Description |
|-----------|------|-------------|
| brandCountMin / brandCountMax | integer | Brand count range |
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share (0-1) |
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |

#### Filter Parameters — Seller Metrics

| Parameter | Type | Description |
|-----------|------|-------------|
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

#### Filter Parameters — Competition & Advertising

| Parameter | Type | Description |
|-----------|------|-------------|
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share (0-1) |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage (0-1) |
| cpcMediumMin / cpcMediumMax | number | CPC median value range |

#### Filter Parameters — New Product & Returns

| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | 180-day new product success rate (0-1) |
| newProductRateT180 | number | 180-day new product ratio minimum (0-1) |
| returnRateT360Min / returnRateT360Max | number | 360-day return rate (0-1) |

#### Sorting Options

| Value | Description |
|-------|-------------|
| unitsSoldT7 | Weekly units sold |
| searchVolumeT7 | Weekly search volume |
| demand | Demand score |
| avgPrice | Average price |
| maximumPrice | Maximum price |
| minimumPrice | Minimum price |
| productCount | Product count |
| searchConversionRateT7 | Weekly search conversion rate |
| clickConversionRateT7 | Weekly click conversion rate |
| searchVolumeGrowthT7 | Search volume growth rate |
| clickCountT7 | Weekly click count |
| clickCountT90 | 90-day click count |
| brandCount | Brand count |
| top5BrandsClickShare | Top 5 brands click share |
| top5ProductsClickShare | Top 5 products click share |
| newProductsLaunchedT180 | 180-day new products launched |
| successfulLaunchesT180 | 180-day successful launches |
| launchRateT180 | 180-day launch success rate |
| returnRateT360 | Annual return rate |
| clickConversionRateT90 | 90-day click conversion rate |
| searchConversionRateT90 | 90-day search conversion rate |
| searchVolumeT90 | 90-day search volume |
| unitsSoldT90 | 90-day units sold |
| unitsSoldGrowthT90 | 90-day sales growth rate |
| searchVolumeGrowthT90 | 90-day search volume growth rate |
| acos | Advertising cost of sales |
| profitRate50 | Profit margin at 50% organic sales |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total count |
| data | array | Niche market info list |
| columns | array | Render columns |
| title | string | Title |
| type | string | Render style |
| costToken | integer | Tokens consumed |

#### data Item (Niche Object)

| Field | Type | Description |
|-------|------|-------------|
| nicheId | string | Niche market ID |
| nicheTitle | string | Niche market title |
| translationZh | string | Niche title (Chinese) |
| demand | integer | Niche demand score |
| productCount | integer | Product count |
| avgPrice | number | Average price |
| minimumPrice | number | Minimum price |
| maximumPrice | number | Maximum price |
| searchVolumeWeekly | integer | Weekly search volume |
| searchVolumeQuarterly | integer | Quarterly search volume |
| searchVolumeGrowthWeekly | number | Weekly search volume growth rate |
| searchVolumeGrowthQuarterly | number | Quarterly search volume growth rate |
| unitsSoldWeekly | integer | Weekly units sold |
| unitsSoldQuarterly | integer | Quarterly units sold |
| clickCountWeekly | integer | Weekly click count |
| clickCountQuarterly | integer | Quarterly click count |
| clickToSaleConversionWeekly | number | Weekly click conversion rate |
| clickConversionRateQuarterly | number | Quarterly click conversion rate |
| searchConversionRateWeekly | number | Weekly search conversion rate |
| searchConversionRateQuarterly | number | Quarterly search conversion rate |
| brandCount | integer | Brand count |
| top5BrandsClickShare | number | Top 5 brands click share |
| top5ProductsClickShare | number | Top 5 products click share |
| avgBrandAgeNow | number | Average brand age (current) |
| avgBrandAgeQuarterly | number | Average brand age (quarterly) |
| newProductsLaunchedSemiannual | integer | New products launched (6-month) |
| successfulLaunchedSemiannual | integer | Successful launches (6-month) |
| launchRateSemiannual | number | Launch success rate (6-month) |
| returnRateAnnual | number | Annual return rate |
| acos | number | ACOS (advertising cost of sales) |
| profitMarginGt50PctSkuRatio | number | SKU ratio with >50% profit margin |
| breakEvenRatio | number | Break-even ratio |
| cpc | object | CPC data: `{ high, medium, low }` |
| categorieList | array | Product category list |
| referenceAsinImageUrl | string | Reference ASIN image URL |

### Key Usage Notes

- **Only US, JP, DE** marketplaces supported.
- Keyword is required; no keyword = no results.
- All percentage/rate values use 0-1 range (not 0-100).
- Max 100 results per page.

---

## 2. Niche Competitor by ASIN (ASIN同细分竞品)

**Endpoint**: `POST https://tool-gateway.linkfox.com/jiimore/pageAsinsByAsin`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asin | string | Yes | Reference ASIN to find competing products for. Max 1000 chars |

#### Marketplace & Pagination

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| countryCode | string | No | US | Country code: `US`, `JP`, `DE` |
| page | integer | No | 1 | Page number (starts from 1) |
| pageSize | integer | No | 50 | Results per page (10-100) |
| sortField | string | No | purchasedClicksT360 | Sort field (see Sorting Options) |
| sortType | string | No | desc | Sort direction: `desc` or `asc` |

#### Filter Parameters — Price & FBA

| Parameter | Type | Description |
|-----------|------|-------------|
| priceMin / priceMax | number | Product price range |
| fbaFeeMin / fbaFeeMax | number | FBA commission range |
| grossProfitMarginMin / grossProfitMarginMax | number | Gross profit margin range |

#### Filter Parameters — Reviews & Ratings

| Parameter | Type | Description |
|-----------|------|-------------|
| totalReviewsMin / totalReviewsMax | integer | Total review count range |
| customerRatingMin / customerRatingMax | number | Customer rating range (0.0-5.0) |

#### Filter Parameters — Click Data (7-day)

| Parameter | Type | Description |
|-----------|------|-------------|
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickCountGrowthT7Min / clickCountGrowthT7Max | number | Weekly click growth rate (0-1) |
| clickConversionRateMin / clickConversionRateMax | number | Click conversion rate (0-1) |

#### Filter Parameters — Click Data (30-day)

| Parameter | Type | Description |
|-----------|------|-------------|
| clickCountT30Min / clickCountT30Max | integer | Monthly click count range |
| clickCountGrowthT30Min / clickCountGrowthT30Max | number | Monthly click growth rate (0-1) |

#### Filter Parameters — Composite Conversion

| Parameter | Type | Description |
|-----------|------|-------------|
| clickConversionRateCompositeMin / clickConversionRateCompositeMax | number | Composite click conversion rate (0-1) |

#### Filter Parameters — Sales & Launch Date

| Parameter | Type | Description |
|-----------|------|-------------|
| salesVolumeT360Min / salesVolumeT360Max | integer | 360-day sales volume range |
| launchDateMin / launchDateMax | string | Launch date range (format: `yyyyMMdd000000`) |

#### Filter Parameters — Niche & Seller

| Parameter | Type | Description |
|-----------|------|-------------|
| nicheCountMin / nicheCountMax | integer | Number of niches the product belongs to |
| sellerCountry | string | Seller country code(s), comma-separated (e.g., `CN,US`) |

#### Sorting Options

| Value | Description |
|-------|-------------|
| purchasedClicksT360 | 360-day purchased clicks (default) |
| totalReviews | Total reviews |
| price | Price |
| launchDate | Launch date |
| clickCountT30 | 30-day click count |
| clickCountT90 | 90-day click count |
| clickCountT7 | 7-day click count |
| clickConversionRate | Click conversion rate |
| clickConversionRateComposite | Composite click conversion rate |
| customerRating | Customer rating |
| clickCountGrowthT7 | Weekly click growth rate |
| clickCountGrowthT30 | Monthly click growth rate |
| currentPrice | Current price |
| fbaFee | FBA commission |
| shippingFee | FBA shipping fee |
| gpm | Gross profit margin |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total records |
| pages | integer | Total pages |
| page | integer | Current page |
| pageSize | integer | Page size |
| data | array | ASIN product list |
| columns | array | Render columns |
| type | string | Render style |
| costToken | integer | Tokens consumed |

#### data Item (Product Object)

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Product ASIN |
| parentAsin | string | Parent ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| currentPrice | number | Current price |
| currency | string | Currency |
| customerRating | number | Rating |
| totalReviews | integer | Review count |
| launchDate | string | Launch date |
| link | string | ASIN link |
| imagesUrl | string | Product main image |
| sellerName | string | Seller name |
| sellerId | string | Seller ID |
| fbaFee | number | FBA commission |
| shippingFee | number | FBA shipping fee |
| gpm | number | Gross profit margin |
| clickConversionRate | number | Click conversion rate (7-day) |
| clickConversionRateComposite | number | Composite click conversion rate |
| clickConversionRateType | string | Conversion rate calculation type |
| clickConversionRateCompositeType | string | Composite rate calculation type |
| clickCountT7 | integer | 7-day click count |
| clickCountT30 | integer | 30-day click count |
| clickCountT90 | integer | 90-day click count |
| clickCountGrowthT7 | number | Weekly click growth rate |
| clickCountGrowthT30 | number | Monthly click growth rate |
| purchasedClicksT360 | integer | 360-day purchased clicks |
| salesVolumeT360 | integer | Annual sales volume |
| nicheCount | integer | Number of niches product belongs to |
| sameNicheTitle | string | Same niche title |
| involvedNum | integer | Involved keyword count |
| involvedFrequency | integer | Involved keyword frequency |
| categoryNames | array | Category info |
| hasMetric | boolean | Whether metrics exist |
| searchValueType | string | Search type: `exact`, `sameNiche`, `category` |
| niches | array | Top 3 niches: `[{nicheId, nicheTitle, demand, image, marketplaceId}]` |
| bestSellersRanking | array | BSR rankings: `[{rank, category}]` |
| trends | array | 90-day trends: `[{day, clickCountT7, reviewCount, reviewRating, bestSellerRanking, averagePriceT7, totalOfferDepthT7}]` |
| lastUpdateTime | string | Last update time |

### Key Usage Notes

- **Only US, JP, DE** marketplaces supported.
- ASIN is required; finds products sharing the same niche segments.
- Launch date format: `yyyyMMdd000000` (e.g., `20240101000000`).
- All rate/percentage values use 0-1 range.
- Max 100 results per page.

---

## 3. Niche Market Info (细分市场洞察)

**Endpoint**: `POST https://tool-gateway.linkfox.com/jiimore/getNicheInfo`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| nicheId | string | Yes | — | Niche market ID. Max 1000 chars. Single ID only |
| countryCode | string | No | US | Country code: `US`, `JP`, `DE` |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Record count |
| data | array | Niche info list |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |

#### data Item — Market Overview

| Field | Type | Description |
|-------|------|-------------|
| nicheId | string | Niche market ID |
| nicheTitle | string | Niche title |
| translationZh | string | Niche title (Chinese) |
| referenceAsinImageUrl | string | Reference image URL |
| marketplaceId | string | Marketplace ID |
| demand | integer | Niche demand score |
| categorieList | array | Product category list |

#### data Item — Product & Brand Counts

| Field | Type | Description |
|-------|------|-------------|
| productCount | integer | Product count |
| productCountNow | integer | Product count (current) |
| productCountT90Before | integer | Product count (90 days ago) |
| productCountT360Before | integer | Product count (360 days ago) |
| brandCount | integer | Brand count |
| brandCountNow | integer | Brand count (current) |
| brandCountT90Before | integer | Brand count (90 days ago) |
| brandCountT360Before | integer | Brand count (360 days ago) |
| brandCountT360Now | integer | Brand count (360-day stat, current) |
| brandCountT360T90Before | integer | Brand count (360-day stat, 90 days ago) |
| brandCountT360T360Before | integer | Brand count (360-day stat, 360 days ago) |
| sellingPartnerCountNow | integer | Seller count (current) |
| sellingPartnerCountT90Before | integer | Seller count (90 days ago) |
| sellingPartnerCountT360Before | integer | Seller count (360 days ago) |
| sellingPartnerCountT360Now | integer | Seller count (360-day stat, current) |
| sellingPartnerCountT360T90Before | integer | Seller count (360-day stat, 90 days ago) |
| sellingPartnerCountT360T360Before | integer | Seller count (360-day stat, 360 days ago) |

#### data Item — Pricing

| Field | Type | Description |
|-------|------|-------------|
| avgPrice | number | Average price |
| avgProductPriceNow | number | Average price (current) |
| avgProductPriceT90Before | number | Average price (90 days ago) |
| avgProductPriceT360Before | number | Average price (360 days ago) |
| minimumPrice | number | Minimum price |
| maximumPrice | number | Maximum price |

#### data Item — Search & Conversion

| Field | Type | Description |
|-------|------|-------------|
| searchVolumeWeekly | integer | Weekly search volume |
| searchVolumeQuarterly | integer | Quarterly search volume |
| searchVolumeGrowthWeekly | number | Weekly search volume growth |
| searchVolumeGrowthQuarterly | number | Quarterly search volume growth |
| searchConversionRateWeekly | number | Weekly search conversion rate |
| searchConversionRateQuarterly | number | Quarterly search conversion rate |
| clickCountWeekly | integer | Weekly click count |
| clickCountQuarterly | integer | Quarterly click count |
| clickConversionRateQuarterly | number | Quarterly click conversion rate |
| clickToSaleConversionWeekly | number | Weekly click conversion rate |
| unitsSoldWeekly | integer | Weekly units sold |
| unitsSoldQuarterly | integer | Quarterly units sold |

#### data Item — Competition: Product Click Share

| Field | Type | Description |
|-------|------|-------------|
| top5ProductsClickShare | number | Top 5 products click share |
| top5ProductsClickShareNow | number | Top 5 products click share (current) |
| top5ProductsClickShareT90Before | number | Top 5 products click share (90 days ago) |
| top5ProductsClickShareT360Before | number | Top 5 products click share (360 days ago) |
| top5ProductsClickShareT360Now | number | Top 5 products click share (360-day stat, current) |
| top5ProductsClickShareT360T90Before | number | Top 5 products click share (360-day stat, 90 days ago) |
| top5ProductsClickShareT360T360Before | number | Top 5 products click share (360-day stat, 360 days ago) |
| top20ProductsClickShareNow | number | Top 20 products click share (current) |
| top20ProductsClickShareT90Before | number | Top 20 products click share (90 days ago) |
| top20ProductsClickShareT360Before | number | Top 20 products click share (360 days ago) |
| top20ProductsClickShareT360Now | number | Top 20 products click share (360-day stat, current) |
| top20ProductsClickShareT360T90Before | number | Top 20 products click share (360-day stat, 90 days ago) |
| top20ProductsClickShareT360T360Before | number | Top 20 products click share (360-day stat, 360 days ago) |

#### data Item — Competition: Brand Click Share

| Field | Type | Description |
|-------|------|-------------|
| top5BrandsClickShare | number | Top 5 brands click share |
| top5BrandsClickShareNow | number | Top 5 brands click share (current) |
| top5BrandsClickShareT90Before | number | Top 5 brands click share (90 days ago) |
| top5BrandsClickShareT360Before | number | Top 5 brands click share (360 days ago) |
| top5BrandsClickShareT360Now | number | Top 5 brands click share (360-day stat, current) |
| top5BrandsClickShareT360T90Before | number | Top 5 brands click share (360-day stat, 90 days ago) |
| top5BrandsClickShareT360T360Before | number | Top 5 brands click share (360-day stat, 360 days ago) |
| top20BrandsClickShareNow | number | Top 20 brands click share (current) |
| top20BrandsClickShareT90Before | number | Top 20 brands click share (90 days ago) |
| top20BrandsClickShareT360Before | number | Top 20 brands click share (360 days ago) |
| top20BrandsClickShareT360Now | number | Top 20 brands click share (360-day stat, current) |
| top20BrandsClickShareT360T90Before | number | Top 20 brands click share (360-day stat, 90 days ago) |
| top20BrandsClickShareT360T360Before | number | Top 20 brands click share (360-day stat, 360 days ago) |

#### data Item — Product Launches

| Field | Type | Description |
|-------|------|-------------|
| newProductsLaunchedSemiannual | integer | New products launched (6-month) |
| newProductsLaunchedT180Now | integer | New products launched (180-day stat, current) |
| newProductsLaunchedT180T90Before | integer | New products launched (180-day stat, 90 days ago) |
| newProductsLaunchedT180T360Before | integer | New products launched (180-day stat, 360 days ago) |
| newProductsLaunchedT360Now | integer | New products launched (360-day stat, current) |
| newProductsLaunchedT360T90Before | integer | New products launched (360-day stat, 90 days ago) |
| newProductsLaunchedT360T360Before | integer | New products launched (360-day stat, 360 days ago) |
| successfulLaunchedSemiannual | integer | Successful launches (6-month) |
| launchRateSemiannual | number | Launch success rate (6-month) |
| successfulLaunchesT90Now | integer | Successful launches (90-day stat, current) |
| successfulLaunchesT90T90Before | integer | Successful launches (90-day stat, 90 days ago) |
| successfulLaunchesT90T360Before | integer | Successful launches (90-day stat, 360 days ago) |
| successfulLaunchesT180Now | integer | Successful launches (180-day stat, current) |
| successfulLaunchesT180T90Before | integer | Successful launches (180-day stat, 90 days ago) |
| successfulLaunchesT180T360Before | integer | Successful launches (180-day stat, 360 days ago) |
| successfulLaunchesT360Now | integer | Successful launches (360-day stat, current) |
| successfulLaunchesT360T90Before | integer | Successful launches (360-day stat, 90 days ago) |
| successfulLaunchesT360T360Before | integer | Successful launches (360-day stat, 360 days ago) |

#### data Item — Inventory & Operations

| Field | Type | Description |
|-------|------|-------------|
| avgOOSRateNow | number | Average out-of-stock rate (current) |
| avgOOSRateT90Before | number | Average out-of-stock rate (90 days ago) |
| avgOOSRateT360Before | number | Average out-of-stock rate (360 days ago) |
| avgOOSRateT360Now | number | Average out-of-stock rate (360-day stat, current) |
| avgOOSRateT360T90Before | number | Average out-of-stock rate (360-day stat, 90 days ago) |
| avgOOSRateT360T360Before | number | Average out-of-stock rate (360-day stat, 360 days ago) |
| primeProductsPercentageNow | number | Prime products percentage (current) |
| primeProductsPercentageT90Before | number | Prime products percentage (90 days ago) |
| primeProductsPercentageT360Before | number | Prime products percentage (360 days ago) |
| primeProductsPercentageT360Now | number | Prime products percentage (360-day stat, current) |
| primeProductsPercentageT360T90Before | number | Prime products percentage (360-day stat, 90 days ago) |
| primeProductsPercentageT360T360Before | number | Prime products percentage (360-day stat, 360 days ago) |

#### data Item — Reviews & Ratings

| Field | Type | Description |
|-------|------|-------------|
| avgReviewRatingNow | number | Average review rating (current) |
| avgReviewRatingT90Before | number | Average review rating (90 days ago) |
| avgReviewRatingT360Before | number | Average review rating (360 days ago) |
| avgReviewCountNow | number | Average review count (current) |
| avgReviewCountT90Before | number | Average review count (90 days ago) |
| avgReviewCountT360Before | number | Average review count (360 days ago) |
| positiveCustomerReviewInsights | array | Positive customer review insights |
| negativeCustomerReviewInsights | array | Negative customer review insights |
| productStarRatingImpact | array | Product star rating impact info |

#### data Item — Seller Maturity

| Field | Type | Description |
|-------|------|-------------|
| avgBrandAgeNow | number | Average brand age (current) |
| avgBrandAgeT90Before | number | Average brand age (90 days ago) |
| avgBrandAgeT360Before | number | Average brand age (360 days ago) |
| avgBrandAgeQuarterly | number | Average brand age (quarterly) |
| avgBrandAgeT360Now | number | Average brand age (360-day stat, current) |
| avgBrandAgeT360T90Before | number | Average brand age (360-day stat, 90 days ago) |
| avgBrandAgeT360T360Before | number | Average brand age (360-day stat, 360 days ago) |
| avgSellingPartnerAgeNow | number | Average seller age (current) |
| avgSellingPartnerAgeT90Before | number | Average seller age (90 days ago) |
| avgSellingPartnerAgeT360Before | number | Average seller age (360 days ago) |
| avgBestSellerRankNow | number | Average BSR rank (current) |
| avgBestSellerRankT90Before | number | Average BSR rank (90 days ago) |
| avgBestSellerRankT360Before | number | Average BSR rank (360 days ago) |

#### data Item — Advertising & Profitability

| Field | Type | Description |
|-------|------|-------------|
| acos | number | ACOS (advertising cost of sales) |
| sponsoredProductsPercentageNow | number | SP ad percentage (current) |
| sponsoredProductsPercentageT90Before | number | SP ad percentage (90 days ago) |
| sponsoredProductsPercentageT360Before | number | SP ad percentage (360 days ago) |
| sponsoredProductsPercentageT360Now | number | SP ad percentage (360-day stat, current) |
| sponsoredProductsPercentageT360T90Before | number | SP ad percentage (360-day stat, 90 days ago) |
| sponsoredProductsPercentageT360T360Before | number | SP ad percentage (360-day stat, 360 days ago) |
| profitMarginGt50PctSkuRatio | number | SKU ratio with >50% profit margin |
| breakEvenRatio | number | Break-even ratio |
| returnRateAnnual | number | Annual return rate |
| cpc | object | CPC data: `{ high, medium, low }` |

### Key Usage Notes

- **nicheId is required**; cannot search by keyword (use Niche by Keyword for that).
- Single niche ID per call; no batch queries.
- Only US, JP, DE supported.
- Response includes current, 90-day-ago, and 360-day-ago snapshots for trend comparison.

---

## 4. Niche Review from Keyword (细分市场评论分析)

**Endpoint**: `POST https://tool-gateway.linkfox.com/jiimore/getNicheReviewFromKeyword`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Search keyword (use target marketplace language). Max 1000 chars |

#### Marketplace & Pagination

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| countryCode | string | No | US | Country code: `US`, `JP`, `DE` |
| page | integer | No | 1 | Page number (starts from 1) |
| pageSize | integer | No | 50 | Results per page (10-100) |

#### Sorting

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| sortField | string | No | unitsSoldT7 | Sort field. Values: `unitsSoldT7`, `searchVolumeT7`, `searchVolumeGrowthT7`, `clickConversionRateT7`, `searchConversionRateT7`, `clickCountT7`, `demand`, `avgPrice`, `maximumPrice`, `minimumPrice`, `productCount`, `brandCount`, `top5BrandsClickShare`, `top5ProductsClickShare`, `clickCountT90`, `clickConversionRateT90`, `searchConversionRateT90`, `searchVolumeT90`, `unitsSoldT90`, `unitsSoldGrowthT90`, `searchVolumeGrowthT90`, `returnRateT360`, `newProductsLaunchedT180`, `successfulLaunchesT180`, `launchRateT180`, `acos`, `profitRate50` |
| sortType | string | No | desc | Sort direction: `desc` or `asc` |

#### Niche Filtering Parameters (all optional)

**Product & Brand Metrics**:

| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| brandCountMin / brandCountMax | integer | Brand count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Sales & Search Volume**:

| Parameter | Type | Description |
|-----------|------|-------------|
| unitsSoldT7Min / unitsSoldT7Max | integer | Units sold (7-day) range |
| searchVolumeT7Min / searchVolumeT7Max | integer | Search volume (7-day) range |
| clickCountT7Min / clickCountT7Max | integer | Click count (7-day) range |

**Conversion & Click Rates** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| clickConversionRateT7Min / clickConversionRateT7Max | number | Click conversion rate (7-day) range |

**Market Concentration** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share range |
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share range |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage range |

**Brand & Seller Age**:

| Parameter | Type | Description |
|-----------|------|-------------|
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**New Product & Return Metrics** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | Launch success rate (180-day) range |
| newProductRateT180 | number | New product percentage (180-day) min |
| returnRateT360Min / returnRateT360Max | number | Return rate (360-day) range |

**Advertising**:

| Parameter | Type | Description |
|-----------|------|-------------|
| cpcMediumMin / cpcMediumMax | number | CPC (current) range |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total count |
| data | array | Niche review data list |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |
| title | string | Title |

#### data Item

| Field | Type | Description |
|-------|------|-------------|
| nicheId | string | Niche market ID |
| nicheName | string | Niche market name |
| keyword | string | Keyword |
| reviewType | string | Review type: 正面评论 (positive) or 负面评论 (negative) |
| topic | string | Review topic |
| percentOfMentions | number | Mention percentage (0-1 = 0%-100%) |
| reviewExample | string | Example review text |

### Key Usage Notes

- Only US, JP, DE marketplaces supported.
- Keyword must be in the target marketplace's language.
- `percentOfMentions` is 0-1 scale; higher = more frequently mentioned topic.
- `reviewType` values are Chinese labels: 正面评论 / 负面评论.
- Niche filtering parameters allow narrowing down which niches' reviews to return.

---

## 5. Product Discovery (产品挖掘)

**Endpoint**: `POST https://tool-gateway.linkfox.com/jiimore/productDiscovery`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

#### Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Search keyword (translate to target marketplace language) |

#### Filtering Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| countryCode | string | No | US | Country code: `US`, `JP`, `DE` |
| priceMin / priceMax | number | No | — | Product price range |
| totalReviewsMin / totalReviewsMax | integer | No | — | Review count range |
| customerRatingMin / customerRatingMax | number | No | — | Rating range |
| clickConversionRateMin / clickConversionRateMax | number | No | — | Click purchase conversion rate (0-1) |
| clickConversionRateCompositeMin / clickConversionRateCompositeMax | number | No | — | Composite conversion rate (0-1) |
| clickCountT7Min / clickCountT7Max | integer | No | — | Weekly click count range |
| clickCountT30Min / clickCountT30Max | integer | No | — | Monthly click count range |
| clickCountGrowthT7Min / clickCountGrowthT7Max | number | No | — | Weekly click growth rate (0-1) |
| clickCountGrowthT30Min / clickCountGrowthT30Max | number | No | — | Monthly click growth rate (0-1) |
| salesVolumeT360Min / salesVolumeT360Max | integer | No | — | Annual sales volume range |
| grossProfitMarginMin / grossProfitMarginMax | number | No | — | Gross profit margin range |
| fbaFeeMin / fbaFeeMax | number | No | — | FBA fee range |
| launchDateMin / launchDateMax | string | No | — | Launch date range (format: `yyyyMMdd000000`) |
| nicheCountMin / nicheCountMax | integer | No | — | Niche market count range |
| sellerCountry | string | No | — | Seller country code(s), comma-separated (e.g., `CN,US`) |

#### Sorting & Pagination

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| sortField | string | No | purchasedClicksT360 | Sort field. Values: `totalReviews`, `price`, `launchDate`, `clickCountT7`, `clickCountT30`, `clickCountT90`, `clickConversionRate`, `clickConversionRateComposite`, `customerRating`, `purchasedClicksT360`, `clickCountGrowthT7`, `clickCountGrowthT30`, `currentPrice`, `fbaFee`, `shippingFee`, `gpm` |
| sortType | string | No | desc | Sort direction: `desc` or `asc` |
| page | integer | No | 1 | Page number |
| pageSize | integer | No | 50 | Results per page (10-100) |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total count |
| sourceTool | string | Tool type: `jiimore` |
| sourceType | string | Source type: `amazon` |
| type | string | Render style |
| title | string | Title |
| costToken | integer | Tokens consumed |
| columns | array | Render columns |
| products | array | Product list |

#### products Item

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Product ASIN |
| parentAsin | string | Parent ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| imageUrl | string | Main product image |
| productImageUrls | array | Product image URL list |
| asinUrl | string | ASIN link |
| ratings | integer | Review count |
| availableDate | string | Launch date (timestamp) |
| availableDateString | string | Launch date (string) |
| categoryNames | array | Category info |
| marketplaceId | string | Marketplace ID |
| clickCountT7 | integer | Weekly click count |
| clickCountT30 | integer | Monthly click count |
| clickCountT90 | integer | Quarterly click count |
| clickConversionRate | number | Click purchase conversion rate |
| clickConversionRateComposite | number | Composite conversion rate |
| grossProfitMargin | number | Gross profit margin |
| fbaFee | number | Amazon FBA commission |
| shippingFee | number | FBA shipping fee |
| sourceTool | string | Tool type: `jiimore` |
| sourceType | string | Source type: `amazon` |

### Key Usage Notes

- **Keyword is mandatory**; no browsing without a keyword.
- Only US, JP, DE marketplaces supported.
- All rate/percentage values must be passed as 0-1 decimals, not percentages.
- Launch date format: `yyyyMMdd000000` (e.g., `20250101000000`).
- Max 100 results per page.

---

## Common Error Codes (All Jiimore Tools)

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse response data normally |
| 401 | Auth failure | Check `Authorization` header with correct API Key |
| Other | Business error | Refer to `errmsg` field for details |

## Supported Marketplaces (All Jiimore Tools)

| Marketplace | Code |
|-------------|------|
| United States | US |
| Japan | JP |
| Germany | DE |
