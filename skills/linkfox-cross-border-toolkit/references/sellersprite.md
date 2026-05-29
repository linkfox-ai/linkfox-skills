# SellerSprite — Tool Reference

## SellerSprite Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/sellersprite/productSearch`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

**Search & Keywords**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword; translate to the target marketplace language |
| matchType | integer | No | Match mode: `1`=Phrase (default), `2`=Fuzzy, `3`=Exact |
| excludeKeywords | string | No | Keywords to exclude from results |
| marketplace | string | No | Marketplace code. Default: `US`. Values: `US`, `UK`, `DE`, `FR`, `JP`, `CA`, `IT`, `ES`, `MX`, `IN` |

**Category Filtering**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| nodeLabel | string | No | Amazon category name |
| nodeIdPath | string | No | Amazon category node ID |
| filterSubNode | boolean | No | Filter by subcategory (only works when nodeLabel or nodeIdPath is set) |

**Data Snapshot**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| dataSnapshotMonth | string | No | Snapshot month `yyyyMM` (e.g., `202412`), or `nearly` for real-time last 30 days. Default: `nearly`. Only past snapshots supported |

**Price & Financials**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minPrice / maxPrice | number | No | Price range filter (>= 0) |
| minProfit / maxProfit | number | No | Gross margin range (1-100, unit: %) |
| minRevenue / maxRevenue | number | No | Monthly revenue range (>= 0) |
| minFba / maxFba | number | No | FBA fee range (>= 0) |

**Sales & Ranking**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minUnits / maxUnits | integer | No | Monthly sales volume range (>= 0) |
| minUnitsGrowthRate / maxUnitsGrowthRate | number | No | Monthly sales growth rate (%) |
| minBsr / maxBsr | integer | No | Main-category BSR rank range |
| minBsrGrowthRate / maxBsrGrowthRate | number | No | BSR growth rate (%) |
| minBsrGrowthCount / maxBsrGrowthCount | integer | No | BSR growth count |
| minSubNodeBsrRank / maxSubNodeBsrRank | integer | No | Subcategory BSR rank (requires `filterSubNode=true`) |

**Reviews & Ratings**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minRating / maxRating | number | No | Rating range (0-5); 3.8-4.3 = product improvement opportunity zone |
| minRatings / maxRatings | integer | No | Rating count range (0-10000) |
| minRatingsGrowthCount / maxRatingsGrowthCount | integer | No | Monthly new ratings count (>= 0) |
| minListingQualityScore / maxListingQualityScore | number | No | Listing quality score range (>= 0) |

**Product Attributes**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| minVariations / maxVariations | integer | No | Variation count range |
| minWeights / maxWeights | number | No | Weight range (>= 0) |
| weightUnit | string | No | Weight unit: `g`, `kg`, `oz`, `lb`. Required if weight filters are used |
| dimensionType | string | No | Package dimension type code (marketplace-specific; see below) |
| minSellers / maxSellers | integer | No | Seller count range |

**Badges & Fulfillment**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| badgeBestSeller | string | No | Best Seller badge: `Y` / `N` / empty (all) |
| badgeAmazonsChoice | string | No | Amazon's Choice badge: `Y` / `N` / empty (all) |
| badgeNewRelease | string | No | New Release badge: `Y` / `N` / empty (all) |
| fulfillment | string | No | Fulfillment type: `AMZ`, `FBA`, `FBM` (comma-separated for multiple) |
| showVariation | string | No | Show variations: `Y` / `N` (default `N`) |

**Seller & Brand**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerNation | string | No | Seller country code (e.g., `US`, `CN`, `HK`); comma-separated for multiple |
| includeSellers / excludeSellers | string | No | Include / exclude specific sellers |
| includeBrands / excludeBrands | string | No | Include / exclude specific brands |

**Listing & Pagination**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| hideUnlistedProduct | boolean | No | Hide delisted products. Default: `true` |
| listedWithinLastMonths | integer | No | Listed within last N months. Enum only: `1`, `3`, `6`, `12`, `24` |
| page | integer | No | Page number (from 1). Default: 1 |
| size | integer | No | Results per page (10-100). Default: 20 |

**Sorting**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order | object | No | Sort config with `field` and `desc` |
| order.field | string | No | Sort field: `total_units`, `total_amount`, `bsr_rank`, `price`, `rating`, `reviews`, `profit`, `reviews_rate`, `available_date`, `questions`, `total_units_growth`, `total_amount_growth`, `reviews_increasement`, `bsr_rank_cv`, `bsr_rank_cr`, `amz_unit`. Default: `total_units` |
| order.desc | string | No | `true`=descending (default), `false`=ascending |

**Package Dimension Type Codes (dimensionType)**

US: `SS` (Small Standard), `LS` (Large Standard), `SO` (Small Oversize), `MO` (Medium Oversize), `LO`/`LB` (Large Oversize), `SP` (Special Oversize), `O` (Other), `ELO` (Extra Large 0-50lb), `EL5O` (Extra Large 50-70lb), `EL7O` (Extra Large 70-150lb), `EL15O` (Extra Large 150lb+)

JP: `SM` (Small), `ST` (Standard), `OV` (Oversize), `SS` (Extra Large), `O` (Other)

CA: `EN` (Envelope), `ST` (Standard), `SO` (Small Oversize), `MO` (Medium Oversize), `LO` (Large Oversize), `SP` (Special Oversize), `O` (Other)

UK/FR/DE/IT/ES: `SL` (Small Envelope), `NL` (Standard Envelope), `LL` (Large Envelope), `ELL` (Extra Large Envelope), `SM` (Small Parcel), `SD` (Standard Parcel), `SB` (Small Oversize), `NB` (Standard Oversize), `LB` (Large Oversize), `SPO` (Special Oversize), `O` (Other)

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total matching products |
| products | array | Product list (see below) |
| columns | array | Column definitions |
| keyword | string | Search keyword used |
| nodeIdPath | string | Category node searched |
| nodeLabel | string | Category name |
| dataSnapshotMonth | string | Data query month |
| sourceType | string | Source type (e.g., `amazon`) |
| type | string | Render style |
| message | string | Message or error info |
| costToken | integer | Token consumption |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| asinUrl | string | Amazon detail URL |
| imageUrl | string | Product image URL |
| price | number | Current price |
| averagePrice | number | Average price |
| primePrice | number | Prime price |
| currency | string | Currency |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales growth rate |
| bsr | integer | BSR rank |
| bsrGrowthRate | number | BSR growth rate |
| rating | number | Rating |
| ratings | integer | Rating count |
| ratingsRate | number | Review rate |
| profit | number | Gross margin (%) |
| fba | number | FBA fee |
| sellerNum | integer | Seller count |
| sellerId | string | BuyBox seller ID |
| sellerName | string | BuyBox seller name |
| sellerNation | string | BuyBox seller nationality |
| brand | string | Brand |
| brandUrl | string | Brand page URL |
| fulfillment | string | Fulfillment: AMZ / FBA / FBM |
| availableDate | string | Listing date (timestamp) |
| availableDateString | string | Listing date (formatted string) |
| variationNum | integer | Variation count |
| variant30DayUnits | integer | Variant monthly sales (units) |
| variant30DayRevenue | number | Variant monthly revenue |
| variant30DayUpdatedAt | string | Variant data update time |
| weight | string | Weight |
| packageWeight | string | Package weight |
| dimension | string | Dimensions |
| packageDimensions | string | Package dimensions |
| dimensionsType | string | Dimensions type |
| packageDimensionType | string | Package dimension type |
| listingQualityScore | number | Listing quality score |
| deliveryPrice | number | Seller shipping fee |
| nodeLabelPath | string | Category path |
| nodeIdPath | string | Node ID path |
| nodeId | integer | Node ID |
| dataSnapshotMonth | string | Data snapshot month |
| badgeBestSeller | string | Best Seller badge (Y/N) |
| badgeAmazonChoice | string | Amazon's Choice badge (Y/N) |
| badgeNewRelease | string | New Release badge (Y/N) |
| badgeVideo | string | Video present (Y/N) |
| badgeEbc | string | A+ page (Y/N) |
| badge | object | Badge summary: `bestSeller`, `amazonChoice`, `newRelease`, `video`, `ebc` |
| subcategories | array | Sub-categories; each has `code`, `rank`, `label` |
| sku | string | SKU |
| keyword | string | Matching keyword |
| sourceType | string | Source type |
| sourceTool | string | Source tool |

### Key Usage Notes
- Max 100 records per page; `listedWithinLastMonths` only accepts enum values: 1, 3, 6, 12, 24
- Weight unit (`weightUnit`) is required when using weight filters
- Subcategory BSR filters only work when `filterSubNode=true`
- 10 marketplaces supported
- Lower BSR = better sales rank
- Gross margin is estimated (price minus FBA fees and estimated costs)

---

## SellerSprite Competitor Lookup

**Endpoint**: `POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | No | Marketplace code. Default: `US`. Values: `US`, `UK`, `DE`, `FR`, `JP`, `CA`, `IT`, `ES`, `MX`, `AU`, `TR`, `IN` |
| keyword | string | No | Search keyword; translate to marketplace language |
| asinList | string | No | ASIN(s), comma-separated, max 40. Format: `^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| sellerName | string | No | Filter by seller name |
| brand | string | No | Filter by brand name |
| nodeLabel | string | No | Category name (colon-separated levels, e.g., `Electronics:Headphones`) |
| nodeIdPath | string | No | Category ID path |
| matchType | integer | No | Keyword match: `1`=Phrase (default), `2`=Fuzzy, `3`=Exact |
| showVariation | string | No | Show variations: `Y` / `N` (default `N`) |
| dataSnapshotMonth | string | No | Snapshot month: `nearly` (default, real-time 30 days) or `yyyyMM` for historical |
| page | integer | No | Page number (from 1). Default: 1 |
| size | integer | No | Results per page (10-100). Default: 50 |
| order | object | No | Sort config (see below) |

**Sort (order object)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| field | string | Yes | Sort field: `total_units`, `total_amount`, `bsr_rank`, `price`, `rating`, `reviews`, `profit`, `reviews_rate`, `available_date`, `questions`, `total_units_growth`, `total_amount_growth`, `reviews_increasement`, `bsr_rank_cv`, `bsr_rank_cr`, `amz_unit`. Default: `total_units` |
| desc | string | Yes | `true`=descending (default), `false`=ascending |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total matching results |
| sourceType | string | Source type (e.g., `amazon`) |
| message | string | Message or error description |
| type | string | Render style |
| nodeLabel | string | Category name echo |
| columns | array | Column definitions |
| products | array | Competitor product list (see below) |
| costToken | integer | Token consumption |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| price | number | Current price |
| primePrice | number | Prime price |
| averagePrice | number | Average price |
| currency | string | Currency |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales growth rate |
| bsr | integer | BSR rank |
| bsrGrowthRate | number | BSR growth rate |
| bsrGrowthCount | integer | BSR growth count |
| rating | number | Rating |
| ratings | integer | Rating count |
| ratingsGrowth | integer | Monthly new ratings |
| ratingsRate | number | Review rate |
| brand | string | Brand |
| brandUrl | string | Brand URL |
| sellerName | string | BuyBox seller name |
| sellerId | string | BuyBox seller ID |
| sellerNation | string | BuyBox seller nationality |
| sellerNum | integer | Seller count |
| fulfillment | string | Fulfillment: AMZ, FBA, FBM |
| availableDate | string | Listing date |
| availableDateString | string | Listing date (formatted) |
| profit | number | Gross margin |
| fba | number | FBA fee |
| deliveryPrice | number | Seller shipping fee |
| imageUrl | string | Product image URL |
| parent | string | Parent ASIN |
| variationNum | integer | Variation count |
| variant30DayUnits | integer | Variant monthly sales (units) |
| variant30DayRevenue | number | Variant monthly revenue |
| variant30DayUpdatedAt | string | Variant data update timestamp |
| amzUnitDateString | string | Variant sales update date |
| listingQualityScore | number | Listing quality score |
| nodeLabelPath | string | Category path |
| nodeIdPath | string | Node ID path |
| nodeId | integer | Node ID |
| dimension | string | Product dimensions |
| dimensionsType | string | Dimensions type |
| weight | string | Weight |
| packageDimensions | string | Package dimensions |
| packageDimensionType | string | Package dimension type |
| packageWeight | string | Package weight |
| sku | string | SKU |
| keyword | string | Matching keyword |
| dataSnapshotMonth | string | Data snapshot month |
| sourceTool | string | Source tool |
| sourceType | string | Source type |
| badgeBestSeller | string | Best Seller badge (Y/N) |
| badgeAmazonChoice | string | Amazon's Choice badge (Y/N) |
| badgeNewRelease | string | New Release badge (Y/N) |
| badgeEbc | string | A+ page (Y/N) |
| badgeVideo | string | Video present (Y/N) |
| badge | object | Badge details: `bestSeller`, `amazonChoice`, `newRelease`, `ebc`, `video` (all Y/N strings) |
| subcategories | array | Sub-category rankings; each has `code`, `rank`, `label` |

### Key Usage Notes
- 12 marketplaces supported (includes AU and TR beyond Product Search)
- Max 40 ASINs per `asinList` query
- 10-100 results per page
- Historical snapshots only for past months; future dates not supported
- Keywords should match the marketplace language for best results
- Category names support multi-level colon-separated paths
- Lower BSR = better sales rank
- Positive BSR growth count means BSR value increased (ranking worsened)
