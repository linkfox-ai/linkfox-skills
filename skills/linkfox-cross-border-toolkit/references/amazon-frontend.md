# Amazon Frontend — Tool Reference

## Amazon Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/amazon/search`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword; translate to the target marketplace's language (e.g., English for US, German for DE). Max length 1024 |
| amazonDomain | string | No | Amazon marketplace domain. Default: `amazon.com`. Supported: `amazon.com`, `amazon.co.uk`, `amazon.de`, `amazon.fr`, `amazon.it`, `amazon.es`, `amazon.co.jp`, `amazon.ca`, `amazon.com.au`, `amazon.com.br`, `amazon.in`, `amazon.nl`, `amazon.se`, `amazon.pl`, `amazon.sg`, `amazon.sa`, `amazon.ae`, `amazon.com.mx`, `amazon.com.tr`, `amazon.com.be`, `amazon.cn`, `amazon.eg` |
| node | string | No | Amazon category node ID for category-scoped searches. Max length 1000 |
| language | string | No | Language locale code (e.g., `en_US`, `de_DE`, `ja_JP`, `fr_FR`). Max length 1000 |
| sort | string | No | Sort order. Values: `relevanceblender` (Featured/Relevance, default), `price-asc-rank` (Price Low→High), `price-desc-rank` (Price High→Low), `review-rank` (Avg Customer Review), `date-desc-rank` (Newest Arrivals), `exact-aware-popularity-rank` (Best Sellers) |
| page | integer | No | Page number (from 1, ~20 results/page). Default: `1` |
| deliveryZip | string | No | Postal/zip code for delivery location simulation (e.g., US `10001`, UK `EC1A 1BB`, DE `10115`, JP `100-0001`). Max length 1000 |
| device | string | No | Device type: `desktop` (default), `mobile`, `tablet`. Max length 1000 |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total result count |
| keyword | string | Search keyword |
| type | string | Render style |
| columns | array | Column definitions for rendering |
| costToken | integer | Token consumption |
| products | array | Search result list (see below) |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| extractedPrice | number | Extracted price |
| oldPrice | number | Strikethrough price |
| extractedOldPrice | number | Extracted strikethrough price |
| currency | string | Currency |
| priceUnit | string | Price unit |
| extractedPriceUnit | number | Extracted price unit |
| rating | number | Rating score |
| ratings | integer | Rating count |
| position | integer | Position on search page |
| sponsored | boolean | Whether sponsored |
| imageUrl | string | Thumbnail URL |
| asinUrl | string | Product link |
| delivery | string | Delivery info |
| fulfillment | string | Fulfillment info (e.g., FBA) |
| availableDate | string (date) | Listing date |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | string | Monthly sales revenue |
| sellerNation | string | Seller nationality |
| dimension | string | Product dimensions |
| weight | string | Weight |
| options | string | Options |
| offers | string | Offer information |
| badges | string | Amazon search badges |
| tags | string | Tags |
| snapEbtEligible | boolean | SNAP/EBT eligible |
| sourceType | string | Source type: `amazon` |
| sourceTool | string | Source tool identifier |
| keyword | string | Keyword |

### Key Usage Notes
- Real-time data only (live SERP results, not historical)
- ~20 results per page
- Keywords should be in the target marketplace's language
- Supports 22 Amazon marketplaces

---

## Amazon Product Detail

**Endpoint**: `POST https://tool-gateway.linkfox.com/amazon/product/detail`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asins | string | Yes | ASIN list, comma-separated, max 40. Format: `^[A-Z0-9]+(,[A-Z0-9]+){0,39}$`. Example: `B072MQ5BRX,B08N5WRWNW` |
| amazonDomain | string | No | Amazon marketplace domain. Default: `amazon.com`. Supported: `amazon.com`, `amazon.co.uk`, `amazon.de`, `amazon.fr`, `amazon.it`, `amazon.es`, `amazon.co.jp`, `amazon.ca`, `amazon.com.au`, `amazon.com.br`, `amazon.in`, `amazon.nl`, `amazon.se`, `amazon.pl`, `amazon.sg`, `amazon.sa`, `amazon.ae`, `amazon.com.tr`, `amazon.com.mx`, `amazon.eg`, `amazon.cn`, `amazon.com.be` |
| language | string | No | Locale code. Examples: `en_US`, `de_DE`, `fr_FR`, `ja_JP`, `it_IT`, `es_ES`, `pt_BR`, `en_GB`, `zh_CN` |
| deliveryZip | string | No | Delivery zip code. Examples: `10001` (US NYC), `10115` (DE Berlin), `EC1A 1BB` (UK London) |
| device | string | No | Device type: `desktop` (default), `mobile`, `tablet` |
| returnBoughtTogether | boolean | No | Return "Frequently Bought Together" products. Default: `false` |
| returnRelatedProducts | boolean | No | Return related products list. Default: `false` |
| returnAuthorsReviews | boolean | No | Return top customer reviews. Default: `false` |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total count |
| columns | array | Column definitions |
| type | string | Render style |
| costToken | integer | Token consumption |
| products | array | Product list (see below) |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| extractedPrice | number | Extracted price |
| oldPrice | number | Original price |
| extractedOldPrice | number | Extracted original price |
| currency | string | Currency |
| discount | string | Discount info |
| saveWithCoupon | string | Coupon savings amount |
| rating | number | Rating |
| ratings | integer | Review count |
| prime | boolean | Prime eligible |
| stock | string | Stock status |
| delivery | string | Delivery info |
| link | string | Product link |
| linkClean | string | Clean link |
| asinUrl | string | ASIN URL |
| imageUrl | string | Thumbnail |
| thumbnail | string | Thumbnail |
| productImageUrls | array | Product image URL list |
| aboutItem | array | Bullet points (About This Item) |
| productDescription | string | Product description |
| description | string | Description |
| dimension | string | Product dimensions |
| weight | string | Weight |
| tags | string | Tags |
| badges | string | Badges |
| climatePledgeFriendly | boolean | Climate Pledge Friendly |
| snapEbtEligible | boolean | SNAP/EBT eligible |
| boughtLastMonth | string | Bought last month (string) |
| boughtLastMonthCount | integer | Bought last month (number) |
| reviewsSummary | string | Review summary |
| reviewsImages | array | Review image list |
| sourceTool | string | Source tool |
| sourceType | string | Source type: `amazon` |
| pageFileUrl | string | Full page file URL |

Nested — **productDetails** (specifications):

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| manufacturer | string | Manufacturer |
| productDimensions | string | Product dimensions |
| upc | string | UPC code |
| units | string | Units |
| rating | number | Rating |
| review | integer | Review count |

Nested — **customerReviews** (star distribution):

| Field | Type | Description |
|-------|------|-------------|
| fiveStar | integer | 5-star count |
| fourStar | integer | 4-star count |
| threeStar | integer | 3-star count |
| twoStar | integer | 2-star count |
| oneStar | integer | 1-star count |

Nested — **variants** (array):

| Field | Type | Description |
|-------|------|-------------|
| title | string | Variant dimension (e.g., color, size) |
| items | array | Variant items; each has `name`, `asin`, `position`, `selected` |

Nested — **itemSpecifications**: Dynamic key-value pairs for product specs.

Nested — **itemIngredients**: Array of product ingredients.

Optional — **boughtTogether** (when `returnBoughtTogether: true`):

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Title |
| price | string | Price |
| extractedPrice | number | Extracted price |
| priceUnit | string | Unit price |
| extractedPriceUnit | number | Extracted unit price |
| thumbnail | string | Thumbnail |
| link | string | Link |
| linkClean | string | Clean link |
| stock | string | Stock status |
| delivery | array | Delivery info |
| position | integer | Position |

Optional — **relatedProducts** (when `returnRelatedProducts: true`):

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Title |
| price | string | Price |
| extractedPrice | number | Extracted price |
| oldPrice | string | Original price |
| extractedOldPrice | number | Extracted original price |
| priceUnit | string | Unit price |
| extractedPriceUnit | number | Extracted unit price |
| rating | number | Rating |
| reviews | integer | Review count |
| thumbnail | string | Thumbnail |
| link | string | Link |
| linkClean | string | Clean link |
| prime | boolean | Prime eligible |
| sponsored | boolean | Sponsored |
| climatePledgeFriendly | boolean | Climate Pledge Friendly |
| discount | string | Discount |
| badges | array | Badges |
| position | integer | Position |

Optional — **authorsReviews** (when `returnAuthorsReviews: true`):

| Field | Type | Description |
|-------|------|-------------|
| title | string | Review title |
| text | string | Review content |
| author | string | Author |
| authorImage | string | Author avatar |
| authorLink | string | Author link |
| rating | integer | Rating |
| date | string | Date |
| verifiedPurchase | boolean | Verified purchase |
| helpfulVotes | string | Helpful vote count |
| productSize | string | Product size |
| productFlavorName | string | Product flavor name |
| position | integer | Position |

### Key Usage Notes
- Billed per ASIN; batch only what's needed
- Max 40 ASINs per request
- Supports 22 Amazon marketplaces
- Returns current snapshot only (no historical data)

---

## Amazon Product Reviews

**Endpoint**: `POST https://tool-gateway.linkfox.com/amazon/reviews/list`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asin | string | Yes | Amazon product ASIN (single ASIN only) |
| domainCode | string | No | Amazon domain code. Default: `ca`. Values: `ca`, `co.uk`, `in`, `de`, `fr`, `it`, `es`, `co.jp`, `com.au`, `com.br`, `nl`, `se`, `com.mx`, `ae` |
| star1Num | integer | No | Number of 1-star reviews to fetch (0-100). Default: 10 |
| star2Num | integer | No | Number of 2-star reviews to fetch (0-100). Default: 10 |
| star3Num | integer | No | Number of 3-star reviews to fetch (0-100). Default: 10 |
| star4Num | integer | No | Number of 4-star reviews to fetch (0-100). Default: 10 |
| star5Num | integer | No | Number of 5-star reviews to fetch (0-100). Default: 10 |
| filterByKeyword | string | No | Filter reviews containing this keyword. Max length 1000 |
| sortBy | string | No | Sort: `recent` (newest first, default), `helpful` (most helpful first) |
| reviewerType | string | No | Reviewer filter: `all_reviews` (default), `avp_only_reviews` (verified purchases only) |
| mediaType | string | No | Media filter: `all_contents` (default), `media_reviews_only` (reviews with images/videos) |
| formatType | string | No | Format filter: `current_format` (default), `all_formats` |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total review count |
| data | array | Review list (see below) |
| columns | array | Column definitions |
| costToken | integer | Token consumption |
| type | string | Render style |

Review object:

| Field | Type | Description |
|-------|------|-------------|
| reviewId | string | Review ID |
| asin | string | Product ASIN |
| title | string | Review title |
| text | string | Review content |
| rating | string | Rating |
| date | string | Review date |
| userName | string | Reviewer name |
| verified | boolean | Verified purchase |
| vine | boolean | Vine Voice review |
| numberOfHelpful | integer | Helpful vote count |
| imageUrlList | array | Review image list |
| videoUrlList | array | Review video list |
| domainCode | string | Country code |
| productTitle | string | Product title |
| productRating | string | Product rating |
| countRatings | integer | Product rating count |
| countReviews | integer | Product review count |
| variationId | string | Variation ID |
| variationList | array | Variation list |
| profilePath | string | Reviewer profile path |
| currentPage | integer | Current page |
| sortStrategy | string | Sort strategy |
| statusCode | integer | Status code |
| statusMessage | string | Status message |
| locale | object | Locale information |
| reviewSummary | object | Review summary data |
| filters | object | Applied filters |

### Key Usage Notes
- One ASIN per request only
- Max 100 reviews per star rating per request
- Supports 14 marketplaces
- Default marketplace is Canada (`ca`); always confirm user's intended marketplace
- Reviews returned in original language

---

## Amazon Image-Based Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/amazon/searchByImage`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| imageUrl | string | Yes | Publicly accessible image URL. Max length 1000 |
| amazonDomain | string | Yes | Amazon domain. Default: `amazon.com`. Supported: `amazon.com`, `amazon.co.uk`, `amazon.de`, `amazon.fr`, `amazon.it`, `amazon.es`, `amazon.co.jp`, `amazon.in` (8 marketplaces only) |
| sort | string | No | Sort order: `default`, `price-asc-rank`, `price-desc-rank`, `rating-asc-rank`, `rating-desc-rank`, `ratings-asc-rank`, `ratings-desc-rank` |
| deliveryZip | string | No | Delivery zip code within the marketplace country. Defaults per marketplace: US=10001, UK=EC1A 1BB, DE=10115, FR=75001, IT=00100, ES=28001, JP=100-0001, IN=110034. Max length 1000 |
| countryOrAreaCode | string | No | Cross-border delivery country code (e.g., `CN`, `JP`, `KR`, `TW`, `HK`, `MO`, `SG`, `TH`, `VN`, `PH`, `MY`). Cannot be used together with `deliveryZip`. India does not support cross-border delivery. Max length 1000 |
| aggregateByKeepaData | boolean | No | Enrich results with Keepa data (sales rank, monthly sales, FBA fees, dimensions, etc.) |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total rows |
| totalCount | integer | Total count |
| perPage | integer | Per page count |
| currentPage | integer | Current page |
| type | string | Render style |
| sourceType | string | Source type |
| columns | array | Column definitions |
| costToken | integer | Token consumption |
| products | array | Product list (see below) |

Core product fields:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| imageUrl | string | Image URL |
| asinUrl | string | Amazon detail page URL |
| price | number | Current price (local currency) |
| oldPrice | number | Strikethrough price |
| currency | string | Currency |
| rating | number | Rating (0.0-5.0) |
| ratings | integer | Rating count |
| brand | string | Brand |
| sourceTool | string | Source tool |
| sourceType | string | Source type |

Keepa enrichment fields (when `aggregateByKeepaData: true`):

| Field | Type | Description |
|-------|------|-------------|
| salesRank | integer | Sales rank (Keepa) |
| salesRank30 | integer | 30-day avg sales rank (Keepa) |
| salesRank90 | integer | 90-day avg sales rank (Keepa) |
| salesRank180 | integer | 180-day avg sales rank (Keepa) |
| monthlySalesUnits | integer | Monthly sales units (Keepa) |
| monthlySalesRevenue | number | Monthly sales revenue (Keepa) |
| monthlySalesUnits1MonthAgo ~ monthlySalesUnits12MonthsAgo | integer | Monthly sales 1-12 months ago (Keepa) |
| reviewCount | integer | Review count (Keepa) |
| fbaFees | number | FBA fees in local currency (Keepa) |
| profit | number | Profit margin % (e.g., 25.5 = 25.5%) (Keepa) |
| referralFeePercentage | number | Referral fee % (Keepa) |
| fulfillment | string | Fulfillment: AMZ, FBA, FBM (Keepa) |
| primePrice | number | Prime price (Keepa) |
| buyBoxSellerId | string | Buy Box seller ID (Keepa) |
| sellerNum | integer | Seller count (Keepa) |
| variationNum | integer | Variation count (Keepa) |
| parentAsin | string | Parent ASIN (Keepa) |
| availableDate | string | Listing date yyyy-MM-dd HH:mm:ss (Keepa) |
| lastUpdate | string | Last update yyyy-MM-dd HH:mm:ss (Keepa) |
| manufacturer | string | Manufacturer (Keepa) |
| model | string | Model (Keepa) |
| color | string | Color (Keepa) |
| material | string | Material (Keepa) |
| weight | string | Weight in grams (Keepa) |
| dimension | string | Dimensions (Keepa) |
| itemLength | integer | Item length mm (Keepa); 0 or -1 = N/A |
| itemWidth | integer | Item width mm (Keepa); 0 or -1 = N/A |
| itemHeight | integer | Item height mm (Keepa); 0 or -1 = N/A |
| packageLength | integer | Package length mm (Keepa) |
| packageWidth | integer | Package width mm (Keepa) |
| packageHeight | integer | Package height mm (Keepa) |
| packageWeight | string | Package weight grams (Keepa) |
| packageDimensions | string | Package dimensions (Keepa) |
| packageQuantity | integer | Items in package (Keepa); 0 or -1 = N/A |
| dimensionsType | string | Dimensions type (Keepa) |
| categoryTree | string | Category tree (Keepa) |
| categoryTreeId | string | Category tree ID (Keepa) |
| rootCategory | integer | Root category ID (Keepa) |
| isAdultProduct | boolean | Adult product (Keepa) |
| isHazmat | boolean | Hazardous material (Keepa) |
| urlSlug | string | URL slug (Keepa) |
| productImageUrls | array | Product image list (Keepa) |

### Key Usage Notes
- Only 8 marketplaces supported (US, UK, DE, FR, IT, ES, JP, IN)
- Image URL must be publicly accessible
- `deliveryZip` and `countryOrAreaCode` are mutually exclusive
- India marketplace does not support cross-border delivery

---

## Amazon Market Opportunity Report

**Endpoint**: `POST https://tool-gateway.linkfox.com/amazon/opportunity/reportByKeyword`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)
**User-Agent**: `LinkFox-Skill/1.0`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site | string | Yes | Amazon marketplace code. Currently only `US` is supported |
| keyword | string | Yes | Search keyword to generate the insight report for |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| code | string | Response code |
| msg | string | Message or error info |
| stdout | string | Full business insight report in Markdown format (covers: market potential, product characteristics, user reviews, customer profile, search trends, pricing analysis) |
| costTime | integer | Processing time (ms) |
| costToken | integer | Token consumption |
| type | string | Response type |

### Key Usage Notes
- US marketplace only
- Returns a Markdown report (non-structured), not JSON data
- Report is AI-generated from real-time Amazon data
- Processing may be slower than simple data lookups
- Report is a point-in-time snapshot

---

## ABA Data Explorer (Amazon Brand Analytics)

**Endpoint**: `POST https://tool-gateway.linkfox.com/aba/intelligentQuery`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| analysisDescription | string | Yes | Natural language description of the query intent. Must be precise: specify marketplace, time ranges, numeric thresholds, deduplication logic |
| region | string | No | Marketplace code. Default: `US`. Values: `US`, `DE`, `BR`, `CA`, `AU`, `JP`, `AE`, `ES`, `FR`, `IT`, `SA`, `TR`, `MX`, `SE`, `NL` |
| createDownloadUrl | boolean | No | Generate CSV download link. Default: `false`. Set to `true` when user requests download/export |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Query success flag |
| tables | array | Result data; each element has `data` (rows), `columns` (column definitions), `name` (sheet name) |
| total | integer | Total result count |
| downloadUrl | string | CSV download URL (when `createDownloadUrl: true`) |
| msg | string | Additional message |
| downloadNote | string | Download-related notes |
| code | string | Return code |
| costTime | integer | Processing time (ms) |
| costToken | integer | Token consumption |

### Key Usage Notes
- Nearly 3 years of weekly-granularity ABA search term data
- 15 marketplaces supported
- `analysisDescription` is the key parameter — must be specific and precise
- Download links contain max 10,000 records
- Lower `searchFrequencyRank` = higher search popularity (rank 1 is most popular)
- Data fields include: searchTerm, reportStartDate, region, searchFrequencyRank, clickedAsin, clickedItemName, clickShareRank, clickShare (0~1), conversionShare (0~1)
