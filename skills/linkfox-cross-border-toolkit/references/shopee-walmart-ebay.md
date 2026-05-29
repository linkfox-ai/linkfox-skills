# Shopee + Walmart + eBay — Tool Reference

## YouYing Shopee Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/youying/shopee/getProductInfos`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

**Required:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| station | string | Yes | Shopee marketplace. Name or code: malaysia/MY, taiwan_china/Taiwan_CHN, indonesia/ID, thailand/TH, philippines/PH, singapore/SG, vietnam/VN, brazil/BR, mexico/MX, chile/CL, columbia/CO |

**Keyword Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Product title keyword |
| keywordType | integer | No | Match mode: 1=phrase (default), 2=multi-word AND, 3=multi-word OR |
| notExistKeyword | string | No | Exclude products containing this keyword |
| notExistKeywordType | integer | No | Exclusion match mode: 1=phrase (default), 2=AND, 3=OR |

**Price Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| priceMin | number | No | Min price (local currency) |
| priceMax | number | No | Max price (local currency) |

**Sales Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| soldMin | integer | No | 30-day sales (min) |
| soldMax | integer | No | 30-day sales (max) |
| estimateSoldStart | integer | No | Estimated 30-day sales (min) |
| estimateSoldEnd | integer | No | Estimated 30-day sales (max) |
| historicalSoldStart | integer | No | Total sales (min) |
| historicalSoldEnd | integer | No | Total sales (max) |
| paymentStart | number | No | 30-day revenue (min) |
| paymentEnd | number | No | 30-day revenue (max) |

**Rating Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ratingMin | number | No | Rating min (0-5) |
| ratingMax | number | No | Rating max |
| ratingsMin | integer | No | Rating count min |
| ratingsMax | integer | No | Rating count max |
| favoriteMin | integer | No | Favorite count min |
| favoriteMax | integer | No | Favorite count max |

**SKU Filter:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skuNumberStart | integer | No | SKU count min |
| skuNumberEnd | integer | No | SKU count max |

**Date Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| listingDateFrom | string | No | Listing date start (yyyy-MM-dd) |
| listingDateTo | string | No | Listing date end (yyyy-MM-dd) |
| statTimeStart | string | No | Stat time start (yyyy-MM-dd HH:mm:ss) |
| statTimeEnd | string | No | Stat time end (yyyy-MM-dd HH:mm:ss) |
| lastModiTimeStart | string | No | Last crawl time start (yyyy-MM-dd) |
| lastModiTimeEnd | string | No | Last crawl time end (yyyy-MM-dd) |
| approvedDateStart | string | No | Shop opening date start (yyyy-MM-dd) |
| approvedDateEnd | string | No | Shop opening date end (yyyy-MM-dd) |

**Category Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pL1Id | string | No | Level 1 category ID |
| pL2Id | string | No | Level 2 category ID |
| pL3Id | string | No | Level 3 category ID |
| cidList | string | No | Full category path list, multi-group separated by `｜` |

**Shop Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shopIdList | string | No | Shop ID list (comma-separated) |
| notExistShopIdList | string | No | Excluded shop ID list (comma-separated) |
| merchant | string | No | Shop name or username |
| shopLocation | string | No | Shop location |

**Product Attribute Filters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shippingIconType | integer | No | Shop location: 0=local, 1=overseas |
| cbOption | integer | No | Shipping: 0=local, 1=cross-border |
| isShopeeVerified | integer | No | Shopee Verified: 0=no, 1=yes |
| isOfficialShop | integer | No | Official shop: 0=no, 1=yes |
| isHotSales | integer | No | Hot sales: 0=no, 1=yes |
| pids | string | No | Product ID list (max 500, comma-separated) |

**Sorting & Pagination:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| orderBy | string | No | — | Sort field: `rating`, `price`, `historical_sold`, `sold`, `payment`, `favorite`, `ratings`, `gen_time`, `estimate_sold` |
| orderByType | string | No | DESC | Sort direction: `ASC` or `DESC` |
| page | integer | No | 1 | Page number (from 1) |
| pageSize | integer | No | 1000 | Results per page (1-1000) |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Current page record count |
| totalSize | integer | Total result count |
| sourceTool | string | Source tool identifier |
| sourceType | string | Source type: `shopee` |
| columns | array | Render column definitions |
| costToken | integer | Token cost |
| type | string | Render style |
| products | array | Product list |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| pid | string | Product ID |
| title | string | Product title |
| description | string | Product description |
| imageUrl | string | Product image URL |
| productUrl | string | Shopee product link |
| price | number | Default price (local currency) |
| minPrice | number | SKU min price |
| maxPrice | number | SKU max price |
| sold | integer | 30-day sales |
| estimateSold | integer | Estimated 30-day sales |
| historicalSold | integer | Total historical sales |
| payment | number | 30-day revenue (local currency) |
| rating | number | Rating (0-5) |
| ratings | integer | Rating count |
| favorite | integer | Favorite count |
| viewCount | integer | View count |
| stock | integer | Current stock |
| skuNumber | integer | SKU count |
| genTime | string | Listing date |
| statTime | string | Stat time |
| lastModiTime | string | Last crawl time |
| categoryStructure | string | Category path |
| cid | string | Category IDs (comma-separated) |
| shopId | string | Shop ID |
| shopName | string | Shop name |
| shopUrl | string | Shop link |
| userName | string | Shop owner name |
| shopLocation | string | Shop location |
| shopProductsCount | integer | Shop product count |
| approvedDate | string | Shop opening date |
| isOfficialShop | integer | Official shop (1=yes, 0=no) |
| isShopeeVerified | integer | Shopee Verified (1=yes, 0=no) |
| isHotSales | integer | Hot sales (1=yes, 0=no) |
| shippingIconType | integer | Location type (0=local, 1=overseas, 3/null=unknown) |
| cbOption | integer | Shipping (0=local, 1=cross-border) |
| estimatedDays | integer | Estimated delivery days |
| status | integer | Product status (1=active, 0=delisted, 8=excluded) |
| notExist | integer | Existence (0=exists, 1=not found) |

### Key Usage Notes
- `station` is **mandatory** — always ask the user which marketplace if not specified.
- Prices are in local currency (MYR, TWD, IDR, THB, PHP, SGD, VND, BRL, MXN, CLP, COP).
- `pageSize` max is 1000.
- 11 marketplaces: MY, Taiwan_CHN, ID, TH, PH, SG, VN, BR, MX, CL, CO.

---

## Walmart Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/walmart/search`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No* | Search keyword, max 1024 chars. *At least one of `keyword` or `categoryId` required |
| categoryId | string | No* | Category ID. *At least one of `keyword` or `categoryId` required. `0` = all departments |
| sort | string | No | Sort: `best_seller`, `best_match`, `price_low`, `price_high` |
| page | integer | No | Page number (1-100), default `1` |
| minPrice | number | No | Min price filter |
| maxPrice | number | No | Max price filter |
| spelling | boolean | No | Spelling correction, default `true` |
| softSort | boolean | No | Relevance sort, default `true`. Set `false` to disable |
| storeId | string | No | Store ID for store-specific results |
| device | string | No | Device: `desktop` (default), `tablet`, `mobile` |
| facet | string | No | Filter facets, `key:value` pairs separated by `\|\|` |
| nextDayEnabled | boolean | No | NextDay delivery only, default `false` |
| jsonRestrictor | string | No | JSON field restrictor |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Record count |
| products | array | Product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| productId | string | Walmart product ID |
| usItemId | string | US item ID |
| title | string | Product title |
| description | string | Product description |
| price | number | Current price |
| wasPrice | number | Original price before discount |
| currency | string | Currency code |
| minPrice | number | Min price (multi-option products) |
| pricePerUnitAmount | string | Per-unit price amount |
| pricePerUnit | string | Per-unit price label |
| rating | number | Average rating |
| reviews | integer | Review count |
| sellerName | string | Seller name |
| sellerId | string | Seller ID |
| imageUrl | string | Product image URL |
| productPageUrl | string | Product detail page URL |
| sponsored | boolean | Sponsored listing |
| outOfStock | boolean | Out of stock |
| freeShipping | boolean | Free shipping available |
| twoDayShipping | boolean | Two-day shipping available |
| freeShippingWithWalmartPlus | boolean | Free shipping with Walmart Plus |
| shippingPrice | number | Shipping cost |
| multipleOptionsAvailable | boolean | Has multiple variants |
| variantSwatches | array | Variant options (name, imageUrl, productPageUrl, variantFieldId) |
| sourceTool | string | Source tool |
| sourceType | string | Source type: `walmart` |

### Key Usage Notes
- At least one of `keyword` or `categoryId` must be provided.
- Max 100 pages; default page is 1.
- US-only marketplace.
- Prices in USD.

---

## eBay Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/ebay/search`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword, max 1024 chars |
| ebayDomain | string | No | eBay domain, default `ebay.com`. Values: ebay.com, ebay.co.uk, ebay.de, ebay.fr, ebay.it, ebay.es, ebay.ca, ebay.com.au, ebay.nl, ebay.at, ebay.ch, ebay.pl, ebay.ie, ebay.com.hk, ebay.com.my, ebay.com.sg |
| page | integer | No | Page number, default `1` |
| pageSize | integer | No | Results per page: 25, 50, 100, or 200. Default `50` |
| orderBy | string | No | Sort code, default `12` (Best Match). Values: 1=ending soonest, 2=price lowest, 3=price highest, 7=nearest, 10=newly listed, 12=best match, 15=price+shipping lowest, 16=price+shipping highest, 18=new first, 19=used first |
| priceMin | number | No | Min price |
| priceMax | number | No | Max price |
| itemCondition | string | No | Condition codes, pipe-separated. Values: 1000(New), 1500(New other), 1750(New with defects), 2000(Certified Refurbished), 2010(Excellent Refurbished), 2020(Very Good Refurbished), 2030(Good Refurbished), 2500(Seller refurbished), 2750(Like New), 3000(Used), 7000(For parts) |
| buyingFormat | string | No | Format: `Auction`, `BIN` (Buy It Now), `BO` (Best Offer) |
| showOnly | string | No | Display filters, comma-separated: Complete, Sold, FR(Free returns), RPA(Returns accepted), AS(Authorized seller), Savings, SaleItems, Lots, Charity, AV, FS(Free shipping), LPickup |
| location | integer | No | Seller country code (e.g. 1=US, 2=Canada, 3=UK, 45=China, 77=Germany) |
| prefLoc | string | No | Location scope: 1=Domestic, 2=Regional, 3=Worldwide |
| zipCode | string | No | ZIP/postal code for delivery filtering |
| categoryId | integer | No | eBay category ID |
| noCache | boolean | No | Bypass cache, default `false` |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total matching results |
| products | array | Product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| productId | string | eBay product ID |
| title | string | Product title |
| subtitle | string | Product subtitle |
| price | number | Current/sold price |
| minPrice | number | Price range start (multi-variant) |
| maxPrice | number | Price range end (multi-variant) |
| oldPrice | number | Original price before discount |
| currency | string | Currency (USD, GBP, EUR, etc.) |
| condition | string | Condition description |
| link | string | eBay product detail link |
| imageUrl | string | Product image URL |
| shipping | string | Shipping info |
| location | string | Item location |
| sellerName | string | Seller name |
| sellerReviews | integer | Seller review count |
| positiveFeedbackInPercentage | number | Seller positive feedback % |
| salesQuantity | integer | Sold quantity |
| bidsCount | integer | Bid count (auction items) |
| returns | string | Return policy info |
| promotion | string | Promotion info |
| sponsored | boolean | Sponsored listing |
| sourceType | string | Source type: `ebay` |
| sourceTool | string | Source tool |

### Key Usage Notes
- 16 eBay domains supported across US, UK, EU, Australia, Asia.
- Max 200 results per page.
- Prices in the local currency of the searched domain.
- `showOnly: "Sold,Complete"` returns sold listings for price research.
- Buying formats: Auction, BIN (Buy It Now), BO (Best Offer).
- No historical trend data — only current live listings.
