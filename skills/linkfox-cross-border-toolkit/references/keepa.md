# Keepa — Tool Reference

## Keepa Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/keepa/productSearch`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

**Marketplace (Required)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| domain | string | Yes | Amazon marketplace ID: `1`=US, `2`=UK, `3`=DE, `4`=FR, `5`=JP, `6`=CA, `8`=IT, `9`=ES, `10`=IN, `11`=MX |

**Keyword Filtering**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Title keyword (case-insensitive; space=AND; double-quote phrases; prefix `-` to exclude; `&` replaced by space; max 50 keywords, max 1000 chars) |

**Category Filtering**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| rootCategory | array[int] | No | Root category IDs (max 50) |
| rootCategoryNames | array[string] | No | Root category names (max 50); used when rootCategory is empty; system auto-resolves IDs |
| categoriesInclude | array[int] | No | Sub-category IDs to include (max 50) |
| categoriesIncludeNames | array[string] | No | Sub-category names to include (max 50); supports full paths with `:` or `>` separators |
| categoriesExclude | array[int] | No | Sub-category IDs to exclude (max 50) |
| categoriesExcludeNames | array[string] | No | Sub-category names to exclude (max 50); supports full paths |

**Sales & Ranking Filters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| currentSalesGte / currentSalesLte | integer | No | Current BSR range (lower = better rank) |
| avg90SalesGte / avg90SalesLte | integer | No | 90-day average BSR range |
| deltaPercent90SalesGte / deltaPercent90SalesLte | integer | No | 90-day BSR change percentage range |
| monthlySoldGte / monthlySoldLte | integer | No | Monthly sales units range |
| srAvgGte / srAvgLte | integer | No | Historical average BSR range (for srAvgMonth) |
| srAvgMonth | string | No | Historical BSR month (format: YYYYMM, within last 36 months) |

**Price Filters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| currentNewGte / currentNewLte | integer | No | Current new price range (smallest currency unit, e.g., cents) |
| currentBuyBoxShippingGte / currentBuyBoxShippingLte | integer | No | Buy Box price incl. shipping range (smallest currency unit) |

**Review & Rating Filters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| currentCountReviewsGte / currentCountReviewsLte | integer | No | Review count range |
| currentRatingGte / currentRatingLte | number | No | Rating range (0.0-5.0) |

**Package & Dimensions Filters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| packageLengthGte / packageLengthLte | integer | No | Package length range (mm) |
| packageWidthGte / packageWidthLte | integer | No | Package width range (mm) |
| packageHeightGte / packageHeightLte | integer | No | Package height range (mm) |
| packageWeightGte / packageWeightLte | integer | No | Package weight range (grams) |

**Other Filters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| brand | array[string] | No | Brand names (OR match) |
| color | array[string] | No | Colors (OR match) |
| size | array[string] | No | Sizes (OR match) |
| availableDateGte / availableDateLte | string | No | Listing date range (yyyy-MM-dd) |
| buyBoxIsAmazon | boolean | No | Buy Box seller is Amazon |
| buyBoxIsFBA | boolean | No | Buy Box is FBA fulfilled |
| isHazMat | boolean | No | Hazardous material flag |
| variationCountGte / variationCountLte | integer | No | Variation count range |
| currentCountNewGte / currentCountNewLte | integer | No | Number of new offers range |
| outOfStockPercentage90Gte / outOfStockPercentage90Lte | integer | No | 90-day out-of-stock percentage range |
| singleVariation | boolean | No | Return only one variation per parent ASIN |
| productType | array[int] | No | Product types: 0=standard, 1=downloadable, 2=ebook, 5=variation parent. Default: [0,1,2] |

**Data Options**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| history | integer | No | Include historical data (price history, sales rank, monthly sales). Default: `0` (no), `1` = yes |
| rating | integer | No | Include rating info. Default: `1` (yes) |

**Pagination & Sorting**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (from 1). Default: 1 |
| perPage | integer | No | Results per page (min 50, max 100). Default: 50 |
| sort | array[object] | No | Sort rules (max 3); each: `{"fieldName": "...", "sortDirection": "asc|desc"}`. Sortable: `availableDate`, `currentSales`, `monthlySold`, `currentRating`, `currentCountReviews`, `currentBuyBoxShipping`, `currentNew` |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total rows |
| perPage | integer | Per page count |
| currentPage | integer | Current page |
| totalCount | integer | Total count |
| sourceType | string | Source type: `keepa` |
| type | string | Render style |
| columns | array | Column definitions |
| costToken | integer | Token consumption |
| products | array | Product list (see below) |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| manufacturer | string | Manufacturer |
| model | string | Model |
| price | number | Current price (local currency) |
| primePrice | number | Prime price |
| currency | string | Currency |
| salesRank | integer | Sales rank |
| salesRank30 | integer | 30-day avg sales rank |
| salesRank90 | integer | 90-day avg sales rank |
| salesRank180 | integer | 180-day avg sales rank |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnits1MonthAgo .. monthlySalesUnits12MonthsAgo | integer | Monthly sales for each of the past 12 months |
| rating | number | Rating (0.0-5.0) |
| ratings | integer | Rating count |
| reviewCount | integer | Review count |
| availableDate | string | Listing date (yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update (yyyy-MM-dd HH:mm:ss) |
| imageUrl | string | Image URL |
| productImageUrls | array | Product image list |
| asinUrl | string | Amazon detail URL |
| categoryTree | string | Category tree |
| categoryTreeId | string | Category tree ID |
| rootCategory | integer | Root category ID |
| subcategories | array | Sub-categories; each has `code` (ID), `rank`, `label` |
| fulfillment | string | Fulfillment: AMZ, FBA, FBM |
| buyBoxSellerId | string | Buy Box seller ID |
| sellerNum | integer | Seller count |
| parentAsin | string | Parent ASIN |
| variationNum | integer | Variation count |
| color | string | Color |
| dimension | string | Dimensions |
| dimensionsType | string | Dimensions type |
| material | string | Material |
| weight | string | Weight (grams) |
| packageWeight | string | Package weight (grams) |
| packageLength | integer | Package length (mm) |
| packageWidth | integer | Package width (mm) |
| packageHeight | integer | Package height (mm) |
| packageDimensions | string | Package dimensions |
| packageQuantity | integer | Package quantity; 0 or -1 = N/A |
| itemLength | integer | Item length (mm); 0 or -1 = N/A |
| itemWidth | integer | Item width (mm); 0 or -1 = N/A |
| itemHeight | integer | Item height (mm); 0 or -1 = N/A |
| isAdultProduct | boolean | Adult product |
| isHazmat | boolean | Hazardous material |
| referralFeePercentage | number | Referral fee % |
| fbaFees | number | FBA fees (local currency) |
| profit | number | Profit margin % (e.g., 25.5 = 25.5%) |
| urlSlug | string | URL slug |
| sourceType | string | Source type: `keepa` |
| sourceTool | string | Source tool |

### Key Usage Notes
- Prices are in smallest currency unit (cents); e.g., `$25.99` = `2599`
- Max 100 results per page, min 50
- Max 3 sort rules, max 50 categories/keywords per filter
- Setting `history=1` significantly increases response size and token cost
- Lower BSR = better sales rank

---

## Keepa Product Detail (Product Request)

**Endpoint**: `POST https://tool-gateway.linkfox.com/keepa/productRequest`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asin | string | Yes | ASIN(s), comma-separated, max 100. Max length 3000 chars. Example: `B0088PUEPK` or `B0088PUEPK,B00U26V4VQ,B07M68S376` |
| domain | string | Yes | Amazon marketplace ID: `1`=US, `2`=UK, `3`=DE, `4`=FR, `5`=JP, `6`=CA, `8`=IT, `9`=ES, `10`=IN, `11`=MX, `12`=BR |
| history | integer | No | Include historical data (monthly sales for past 12 months, avg sales rank 30/90/180 days). `1`=yes, `0`=no (default) |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total rows |
| perPage | integer | Per page count |
| sourceType | string | Source type: `keepa` |
| columns | array | Column definitions |
| costToken | integer | Token consumption |
| totalCount | integer | Total count |
| currentPage | integer | Current page |
| type | string | Render style |
| products | array | Product list (see below) |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| manufacturer | string | Manufacturer |
| model | string | Model |
| color | string | Color |
| material | string | Material |
| price | number | Current price (local currency) |
| primePrice | number | Prime price |
| currency | string | Currency |
| rating | number | Rating (0.0-5.0) |
| ratings | integer | Rating count |
| reviewCount | integer | Review count |
| salesRank | integer | Sales rank |
| salesRank30 | integer | 30-day avg sales rank |
| salesRank90 | integer | 90-day avg sales rank |
| salesRank180 | integer | 180-day avg sales rank |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnits1MonthAgo | integer | 1 month ago monthly sales |
| monthlySalesUnits2MonthsAgo | integer | 2 months ago monthly sales |
| monthlySalesUnits3MonthsAgo | integer | 3 months ago monthly sales |
| monthlySalesUnits4MonthsAgo | integer | 4 months ago monthly sales |
| monthlySalesUnits5MonthsAgo | integer | 5 months ago monthly sales |
| monthlySalesUnits6MonthsAgo | integer | 6 months ago monthly sales |
| monthlySalesUnits7MonthsAgo | integer | 7 months ago monthly sales |
| monthlySalesUnits8MonthsAgo | integer | 8 months ago monthly sales |
| monthlySalesUnits9MonthsAgo | integer | 9 months ago monthly sales |
| monthlySalesUnits10MonthsAgo | integer | 10 months ago monthly sales |
| monthlySalesUnits11MonthsAgo | integer | 11 months ago monthly sales |
| monthlySalesUnits12MonthsAgo | integer | 12 months ago monthly sales |
| availableDate | string | Listing date (yyyy-MM-dd HH:mm:ss) |
| lastUpdate | string | Last update (yyyy-MM-dd HH:mm:ss) |
| imageUrl | string | Image URL |
| productImageUrls | array | Product image list |
| asinUrl | string | Amazon detail URL |
| urlSlug | string | URL slug |
| itemLength | integer | Item length (mm); 0 or -1 = N/A |
| itemWidth | integer | Item width (mm); 0 or -1 = N/A |
| itemHeight | integer | Item height (mm); 0 or -1 = N/A |
| dimension | string | Dimensions |
| dimensionsType | string | Dimensions type |
| weight | string | Weight (grams) |
| packageLength | integer | Package length (mm) |
| packageWidth | integer | Package width (mm) |
| packageHeight | integer | Package height (mm) |
| packageWeight | string | Package weight (grams) |
| packageDimensions | string | Package dimensions |
| packageQuantity | integer | Package quantity; 0 or -1 = N/A |
| fulfillment | string | Fulfillment: AMZ, FBA, FBM |
| fbaFees | number | FBA fees (local currency) |
| referralFeePercentage | number | Referral fee % |
| profit | number | Profit margin % (e.g., 25.5 = 25.5%) |
| buyBoxSellerId | string | Buy Box seller ID |
| sellerNum | integer | Seller count |
| variationNum | integer | Variation count |
| parentAsin | string | Parent ASIN |
| rootCategory | integer | Root category ID |
| categoryTree | string | Category tree |
| categoryTreeId | string | Category tree ID |
| subcategories | array | Sub-categories; each has `code`, `rank`, `label` |
| isAdultProduct | boolean | Adult product |
| isHazmat | boolean | Hazardous material |
| sourceType | string | Source type: `keepa` |
| sourceTool | string | Source tool |

### Key Usage Notes
- Max 100 ASINs per request; ASIN string max 3000 chars
- 11 marketplaces supported (US, UK, DE, FR, JP, CA, IT, ES, IN, MX, BR)
- Does NOT return product descriptions or review content
- Historical data (monthly sales for 12 months) only returned when `history=1`
- `lastUpdate` indicates data freshness

---

## Keepa Product Time-Series (History)

**Endpoint**: `POST https://tool-gateway.linkfox.com/keepa/productSeries`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asin | string | Yes | Single ASIN only. Max length 1000 |
| domain | string | Yes | Amazon marketplace ID: `1`=US, `2`=UK, `3`=DE, `4`=FR, `5`=JP, `6`=CA, `8`=IT, `9`=ES, `10`=IN, `11`=MX, `12`=BR |
| days | integer | No | Historical days to retrieve (1-365). Default: `90` |
| showPrice | integer | No | `1` = return lowest new price curve |
| showPriceList | integer | No | `1` = return list/strikethrough price curve |
| showPriceDeal | integer | No | `1` = return lightning deal price curve |
| showPricePrime | integer | No | `1` = return Prime exclusive price curve |
| showPriceFba | integer | No | `1` = return third-party FBA price curve |
| showPriceFbm | integer | No | `1` = return third-party FBM price curve |
| showPriceCoupon | integer | No | `1` = return post-coupon Buy Box price curve |
| showBsrMain | integer | No | `1` = return main category BSR curve |
| showSellerCount | integer | No | `1` = return seller count curve |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| buyboxPrice | array | Buy Box price series (`{time, value}` objects) |
| price | array | Lowest new price series |
| priceList | array | List/strikethrough price series |
| priceDeal | array | Deal price series |
| pricePrime | array | Prime price series |
| priceFba | array | FBA price series |
| priceFbm | array | FBM price series |
| priceCoupon | array | Coupon price series |
| bsrMain | array | Main category BSR; each element has `categoryName` and `points` (`{time, value}`) |
| bsrSub | array | Sub-category BSR; each element has `categoryName` and `points` (`{time, value}`) |
| sellerCount | array | Seller count series (`{time, value}`) |
| rating | array | Rating series (`{time, value}`) |
| ratingCount | array | Rating count series (`{time, value}`) |
| monthlySold | array | Monthly sales series (`{time, value}`) |
| costToken | integer | Token consumption |

### Key Usage Notes
- Single ASIN per query only
- Max 365 days of history
- Core series always returned: Buy Box price, rating, rating count, monthly sales, sub-category BSR
- Optional series require explicit `show*=1` flags
- Data points are at irregular intervals (Keepa captures on change, not fixed daily)
- 11 marketplaces supported
- Lower BSR value = better sales rank
