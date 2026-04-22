# Sorftime — Tool Reference

## Sorftime Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Amazon marketplace code (lowercase): `us`, `gb`, `de`, `fr`, `in`, `ca`, `jp`, `es`, `it`, `mx`, `ae`, `au`, `br`, `sa`. Note: UK is `gb` (not `uk`) |
| queryMode | integer | No | Query mode. `1` = single-condition (default); `2` = multi-condition AND combination |
| queryType | integer | No | Query type (1-16), only effective when `queryMode=1`. See query type table below |
| queryValue | string | No | Query value; format varies by `queryMode` and `queryType`. For `queryMode=2`, pass JSON array: `[{"QueryType":1,"Content":"B0CVM8TXHP"},{"QueryType":8,"Content":"100,500"}]` |
| page | integer | No | Page number. Default: 1. Max 100 products per page |
| queryMonth | string | No | Historical snapshot month (`yyyy-MM`). Omit for real-time data. Supported from January 2024 |

**Query Types (for queryMode=1)**

| queryType | Name | queryValue Format | Example |
|-----------|------|-------------------|---------|
| 1 | ASIN Similar | ASIN | `B0CVM8TXHP` |
| 2 | Category | NodeId | `3743561` |
| 3 | Brand | Brand name | `Anker` |
| 4 | Seller Name | Store name | `AnkerDirect` |
| 5 | Seller ID | SellerId | `A294P4X9EWVXLJ` |
| 6 | ABA Keyword | Keyword | `Power Bank` |
| 7 | Title/Attribute Match | Keywords | `10,000mAh 30W` |
| 8 | Price Range | `min,max` (in cents) | `1,1000` (=$0.01~$10) |
| 9 | Monthly Sales Range | `min,max` | `100,1000` |
| 10 | Seasonal Products | Month list | `1,2,3` (peak in Jan-Mar) |
| 11 | Listing Date Range | `start,end` (yyyy-MM-dd) | `2024-06-01,2024-12-01` |
| 12 | Rating Range | `min,max` | `3,5` |
| 13 | Review Count Range | `min,max` | `10,500` |
| 14 | Rank Range | `bsr_min,bsr_max;sub_min,sub_max` | `500,5000;1,100` |
| 15 | Fulfillment | `FBA` / `FBM` | `FBA,FBM` |
| 16 | Variation Count | `min,max` | `1,50` |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| code | integer | Response code (200 = success) |
| msg | string | Response message |
| total | integer | Total result count |
| page | integer | Current page |
| pageCount | integer | Total pages (max 200) |
| costTime | integer | Processing time (ms) |
| costToken | integer | Token consumption |
| requestConsumed | integer | Request count consumed |
| products | array | Product list (see below) |
| columns | array | Column definitions |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price before Coupon (local currency) |
| salesPrice | number | Actual selling price after Coupon (local currency) |
| oldPrice | number | Strikethrough/list price (local currency) |
| coupon | number | Coupon: >0 = discount amount in cents (500=$5); <0 = percentage (-10=10% off) |
| salesRank | integer | BSR rank in main category |
| monthlySalesUnits | integer | Monthly sales units (Listing level); -1 = cannot estimate |
| monthlySalesRevenue | number | Monthly revenue (local currency); -1 = N/A |
| listingSalesVolumeOfDaily | integer | Daily sales volume; -1 = cannot estimate |
| listingSalesOfDaily | number | Daily revenue (local currency); -1 = N/A |
| rating | number | Rating (0.0-5.0) |
| ratings | integer | Rating count |
| availableDate | string | Listing date (yyyy-MM-dd) |
| onlineDays | integer | Days since listing |
| fbaFees | number | FBA fulfillment fee (local currency) |
| platformFee | number | Platform commission (local currency) |
| profitAmount | number | Profit = sale price - FBA - commission (local currency) |
| profitRate | number | Profit margin % (e.g., 25.83 = 25.83%) |
| isFBA | boolean | Whether Buybox seller uses FBA |
| buyboxSeller | string | Buybox winning seller name |
| buyboxSellerAddress | string | Seller country code (CN, US, etc.); null if Amazon-operated |
| buyBoxSellerId | string | Buybox seller ID |
| category | array | Main category [name, NodeId] |
| bsrCategory | array | Sub-category rankings [{nodeId, name, rank, date}] |
| variationNum | integer | Variation count |
| parentAsin | string | Parent ASIN (null if no variations) |
| weight | number | Weight (grams) |
| size | array | Dimensions in cm [longest, 2nd, shortest] |
| imageUrl | string | Main product image URL |
| asinUrl | string | Amazon product page URL |

### Key Usage Notes
- Max 100 products per page, max 200 pages
- Price filters (queryType=8) use smallest currency unit (cents)
- Historical snapshots from January 2024; AU, BR, IN do NOT support lookback
- US, GB, DE support full lookback; other sites only Top 100 in lookback
- queryType=1 finds *similar* products, not the ASIN itself
- queryType=6 only supports ABA keywords, not arbitrary search terms
- Sales value of `-1` means "cannot estimate"
- Use open ranges by omitting one end: `,1000` = up to 1000; `100,` = 100+

---

## Sorftime Product Detail

**Endpoint**: `POST https://tool-gateway.linkfox.com/sorftime/amazon/productDetail`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asin | string | Yes | ASIN(s), comma-separated, max 10. Example: `B0088PUEPK` or `B0088PUEPK,B00U26V4VQ` |
| marketplace | string | Yes | Amazon marketplace code (lowercase): `us`, `gb`, `de`, `fr`, `in`, `ca`, `jp`, `es`, `it`, `mx`, `ae`, `au`, `br`, `sa`. Note: UK is `gb` |
| includeTrend | integer | No | Include trend data. `1` = yes (default); `2` = no (basic info only, saves cost) |
| queryTrendStartDate | string | No | Trend start date (`yyyy-MM-dd`). Default returns last 15 days. Querying >15 days costs double |
| queryTrendEndDate | string | No | Trend end date (`yyyy-MM-dd`) |

### Response Fields

Top-level:

| Field | Type | Description |
|-------|------|-------------|
| code | integer | Response code (200 = success) |
| msg | string | Response message |
| total | integer | Result count |
| costTime | integer | Processing time (ms) |
| costToken | integer | Token consumption |
| requestConsumed | integer | Request count consumed |
| sourceType | string | Source type |
| products | array | Product detail list (see below) |
| columns | array | Column definitions |

Product object:

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN |
| title | string | Product title |
| brand | string | Brand |
| parentAsin | string | Parent ASIN (null if no variations) |
| category | array | Main category [name, NodeId] |
| bsrCategory | array | Sub-category rank list [{nodeId, name, rank, date}] |
| availableDate | string | Listing date (yyyy-MM-dd) |
| onlineDays | integer | Days since listing |
| price | number | Sale price after Coupon (local currency) |
| coupon | number | Coupon: >0 = amount in cents (500=$5); <0 = percentage (-10=10% off) |
| platformFee | number | Platform commission (local currency) |
| fbaFees | number | FBA fulfillment fee (local currency) |
| fbaDetail | array | FBA breakdown: [delivery fee, "month_range:storage_fee", ...] |
| profitAmount | number | Profit (local currency) |
| profitRate | number | Profit margin % |
| salesRank | integer | BSR rank in main category |
| rankTrend | array | Main category BSR history, interleaved [date, rank, ...] |
| bsrRankTrend | array | Sub-category BSR history [{NodeId, Rank: [date, rank, ...]}] |
| rating | number | Rating (0.0-5.0) |
| ratings | integer | Rating count |
| fiveStarRatings | number | 5-star percentage (e.g., 57.7 = 57.7%) |
| fourStarRatings | number | 4-star percentage |
| threeStarRatings | number | 3-star percentage |
| twoStarRatings | number | 2-star percentage |
| oneStarRatings | number | 1-star percentage |
| listingSalesVolumeOfDailyTrend | array | Daily sales volume trend, interleaved [date, volume, ...]; -1 = cannot estimate |
| listingSalesVolumeOfMonthTrend | array | Monthly sales volume trend, interleaved [date, volume, ...]; -1 = cannot estimate |
| listingSalesOfDailyTrend | array | Daily revenue trend, interleaved [date, revenue, ...]; unit = cents; -1 = N/A |
| listingSalesOfMonthTrend | array | Monthly revenue trend, interleaved [date, revenue, ...]; unit = cents; -1 = N/A |
| priceTrend | array | Sale price history; unit = cents; -1 = no price that day |
| listPriceTrend | array | Strikethrough price history; unit = cents; -1 = N/A |
| buyboxSeller | string | Buybox winning seller name |
| buyboxSellerAddress | string | Seller country code; null if Amazon-operated |
| isFBA | boolean | Whether Buybox seller uses FBA |
| sellerNum | integer | Number of sellers |
| aPlus | boolean | Has A+ content |
| hasVideo | boolean | Has video on listing |
| hasBrandStore | boolean | Has brand storefront |
| weight | number | Weight (grams) |
| size | array | Dimensions in cm [longest, 2nd, shortest] |

### Key Usage Notes
- Max 10 ASINs per query
- Default returns last 15 days of trends; querying >15 days costs double
- Historical trend data goes back to 2021
- Trend arrays use interleaved format: even indices = dates (yyyyMMdd), odd indices = values
- Price/revenue trend values are in smallest currency unit (cents for USD)
- Sales value of `-1` means "cannot estimate"
- 14 marketplaces supported
- Set `includeTrend: 2` for basic info only (saves cost and response size)
