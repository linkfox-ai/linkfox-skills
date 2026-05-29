# TikTok — Tool Reference

## EchoTik Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/echotik/listProduct`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Product keyword (translate to the local language of the target marketplace). Max 1000 chars |
| region | string | No | Region code, default `US`. Values: US, ID, TH, PH, MY, VN, GB, MX, SG, SA, BR, ES, JP, DE, IT, FR |
| categoryKeywordCN | string | No | Product category (must be in Chinese). Max 1000 chars |
| minTotalSaleCnt | integer | No | Total sales volume (min) |
| maxTotalSaleCnt | integer | No | Total sales volume (max) |
| minTotalSale30dCnt | integer | No | 30-day sales volume (min) |
| maxTotalSale30dCnt | integer | No | 30-day sales volume (max) |
| minTotalSaleGmvAmt | string | No | Total GMV (min). Max 1000 chars |
| maxTotalSaleGmvAmt | string | No | Total GMV (max). Max 1000 chars |
| minTotalSaleGmv30dAmt | string | No | 30-day GMV (min). Max 1000 chars |
| maxTotalSaleGmv30dAmt | string | No | 30-day GMV (max). Max 1000 chars |
| minSpuAvgPrice | number | No | SPU average price (min) |
| maxSpuAvgPrice | number | No | SPU average price (max) |
| minProductRating | number | No | Product rating (min) |
| maxProductRating | number | No | Product rating (max) |
| minReviewCount | integer | No | Review count (min) |
| maxReviewCount | integer | No | Review count (max) |
| minProductCommissionRate | number | No | Commission rate (min), decimal e.g. 0.05 = 5% |
| maxProductCommissionRate | number | No | Commission rate (max), decimal e.g. 0.05 = 5% |
| minTotalIflCnt | integer | No | Influencer count (min) |
| maxTotalIflCnt | integer | No | Influencer count (max) |
| minTotalVideoCnt | integer | No | Promotion video count (min) |
| maxTotalVideoCnt | integer | No | Promotion video count (max) |
| minTotalViewsCnt | integer | No | Promotion views (min) |
| maxTotalViewsCnt | integer | No | Promotion views (max) |
| minFirstCrawlDt | integer | No | Listing date (min), YYYYMMDD format |
| maxFirstCrawlDt | integer | No | Listing date (max), YYYYMMDD format |
| saleDays | integer | No | Days since listing |
| productSortField | integer | No | Sort: 1=total sales, 2=total GMV, 3=avg price, 4=7d sales, 5=30d sales, 6=7d GMV, 7=30d GMV. Default `1` |
| sortType | integer | No | 0=ascending, 1=descending. Default `1` |
| pageNum | integer | No | Page number. Default `1` |
| pageSize | integer | No | Results per page. Default `50` |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total record count |
| products | array | Product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| productId | string | Unique product ID |
| productName | string | Product name |
| title | string | Product title |
| imageUrl | string | Product image URL |
| coverUrl | string | Cover image URL |
| productImageUrls | array | Product image URL list |
| categoryName | string | Category name |
| categoryIds | array | Category ID list |
| region | string | Region code |
| currency | string | Currency |
| price | number | Product price |
| minPrice | number | Min price |
| maxPrice | number | Max price |
| spuAvgPrice | number | SPU average price |
| productRating | number | Rating |
| reviewCount | integer | Review count |
| ratings | integer | Ratings count |
| productCommissionRate | number | Commission rate (decimal) |
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | 1-day sales |
| totalSale7dCnt | integer | 7-day sales |
| totalSale15dCnt | integer | 15-day sales |
| totalSale30dCnt | integer | 30-day sales |
| totalSale60dCnt | integer | 60-day sales |
| totalSale90dCnt | integer | 90-day sales |
| monthlySalesUnits | integer | Monthly sales |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | 1-day GMV |
| totalSaleGmv7dAmt | number | 7-day GMV |
| totalSaleGmv15dAmt | number | 15-day GMV |
| totalSaleGmv30dAmt | number | 30-day GMV |
| totalSaleGmv60dAmt | number | 60-day GMV |
| totalSaleGmv90dAmt | number | 90-day GMV |
| firstCrawlDt | integer | Listing date (YYYYMMDD) |
| availableDate | string | Listing timestamp |
| discount | string | Discount info |
| freeShippingText | string | Free shipping flag |
| offMarkText | string | Discount mark |
| salesFlagText | string | Sales method |
| salesTrendFlagText | string | Sales trend flag |
| isSShopText | string | S-shop flag |
| salePropsInfo | array | SKU specs |
| sourceTool | string | Source tool |
| sourceType | string | Source type |
| asin | string | Product ID |

### Key Usage Notes
- Commission rate is decimal (0.05 = 5%). Convert user percentages to decimal before calling.
- Listing date uses YYYYMMDD integer format (e.g. 20240101).
- Keyword should be translated to the target marketplace's local language.
- 16 markets supported: US, ID, TH, PH, MY, VN, GB, MX, SG, SA, BR, ES, JP, DE, IT, FR.

---

## EchoTik New Product Ranking

**Endpoint**: `POST https://tool-gateway.linkfox.com/echotik/listNewProductRank`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | Yes | Query date, format `YYYY-MM-DD` |
| region | string | No | Region code, default `US`. Values: US, ID, TH, PH, MY, VN, GB, MX, SG, SA, BR, ES, JP, DE, IT, FR |
| pageNum | integer | No | Page number, default `1` |
| pageSize | integer | No | Results per page, default `50` |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total record count |
| products | array | New product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| title | string | Product title |
| asin | string | Product ID |
| region | string | Region code |
| price | number | SPU average price |
| minPrice | number | Min price |
| maxPrice | number | Max price |
| currency | string | Currency |
| totalSaleCnt | integer | Total sales |
| totalSale30dCnt | integer | 30-day sales |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv30dAmt | number | 30-day GMV |
| salesTrendFlagText | string | Sales trend: 0=stable, 1=rising, 2=declining |
| totalVideoCnt | integer | Video count |
| totalLiveCnt | integer | Live stream count |
| totalIflCnt | integer | Influencer count |
| productCommissionRate | number | Commission rate |
| productRating | number | Rating |
| reviewCount | integer | Review count |
| availableDate | string | First tracked date |
| categoryId | string | Category ID |
| imageUrl | string | Product image URL |
| productImageUrls | array | Product image URL list |
| sourceTool | string | Source tool |
| sourceType | string | Source type |

### Key Usage Notes
- The `date` parameter is **mandatory** — there is no default date.
- Data is a daily snapshot, not aggregated over weeks or months.
- 16 markets supported (same as EchoTik Product Search).
- Sales trend flag: 0 = Stable, 1 = Rising, 2 = Declining.

---

## FastMoss Product Search

**Endpoint**: `POST https://tool-gateway.linkfox.com/fastmoss/productSearch`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword (product title fuzzy match) |
| region | string | No | Region code. Values: US, GB, MX, ES, DE, IT, FR, ID, VN, MY, TH, PH, BR, JP, SG |
| category | string | No | Category name in English (auto-matched to TikTok category ID) |
| shopType | integer | No | Shop type: 1=local, 2=cross-border |
| isTopSelling | boolean | No | Filter hot-selling products only |
| isNewListed | boolean | No | Filter new products only |
| isSshop | boolean | No | Filter TikTok fully-managed (S-shop) products only |
| isFreeShipping | boolean | No | Filter free-shipping products only |
| isLocalWarehouse | boolean | No | Filter local warehouse products only |
| unitsSoldRange | object | No | Sales volume range: `{"min": 100, "max": 5000}` |
| commissionRateRange | object | No | Commission rate range: `{"min": 0.05, "max": 0.20}` (decimal, 0.10=10%) |
| creatorCountRange | object | No | Creator count range: `{"min": 10, "max": 500}` |
| orderField | string | No | Sort field: `day7_units_sold`, `day7_gmv`, `commission_rate`, `total_units_sold`, `total_gmv`, `creator_count`. Default: descending |
| page | integer | No | Page number, default `1` |
| pageSize | integer | No | Items per page, max `10`, default `10` |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total matching records |
| products | array | Product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| title | string | Product title |
| productId | string | Product ID |
| region | string | Region code |
| price | number | Product price |
| minPrice | number | Min price |
| maxPrice | number | Max price |
| currency | string | Currency code |
| totalSaleCnt | integer | Total cumulative sales |
| totalSale1dCnt | integer | 1-day sales |
| totalSale7dCnt | integer | 7-day sales |
| totalSale28dCnt | integer | 28-day sales |
| totalSale90dCnt | integer | 90-day sales |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv7dAmt | number | 7-day GMV |
| totalSaleGmv28dAmt | number | 28-day GMV |
| totalVideoCnt | integer | Promotion video count |
| totalLiveCnt | integer | Live stream count |
| totalIflCnt | integer | Influencer count |
| productCommissionRate | number | Commission rate (decimal, 0.10=10%) |
| productRating | number | Rating |
| reviewCount | integer | Review count |
| skuCount | integer | SKU count |
| shopName | string | Shop name |
| shopSellerId | string | Seller ID |
| shopTotalUnitsSold | integer | Shop total sales |
| isCrossBorder | integer | 1=cross-border, 0=local |
| isSShopText | string | Fully-managed shop flag |
| freeShippingText | string | Free shipping flag |
| availableDate | string | Listing date |
| categoryName | string | Category name |
| salesTrendFlagText | string | Sales trend label |
| tiktokUrl | string | TikTok product link |
| fastmossUrl | string | FastMoss detail link |
| imageUrl | string | Product image URL |

### Key Usage Notes
- Max 10 items per page.
- 15 markets supported: US, GB, MX, ES, DE, IT, FR, ID, VN, MY, TH, PH, BR, JP, SG.
- Range filters use object format: `{"min": value, "max": value}`.
- Commission rate is decimal (0.10 = 10%).
- `isCrossBorder`: 1 = cross-border shop, 0 = local shop.

---

## FastMoss Top Selling Rankings

**Endpoint**: `POST https://tool-gateway.linkfox.com/fastmoss/productRankTopSelling`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Region code. Values: US, GB, MX, ES, ID, VN, MY, TH, PH |
| dateInfo | object | Yes | Date spec with `type` and `value` |
| dateInfo.type | string | Yes | Time granularity: `day`, `week`, `month` |
| dateInfo.value | string | Yes | Date value: day → `YYYY-MM-DD`, week → `YYYY-周数` (e.g. `2025-18`), month → `YYYY-MM` |
| category | string | No | Category name in English (auto-matched to TikTok category ID) |
| orderby | object | No | Sort rule with `field` and `order` |
| orderby.field | string | No | Sort field: `units_sold`, `gmv`, `total_units_sold`, `total_gmv`, `growth_rate` |
| orderby.order | string | No | Sort direction: `desc` (default), `asc` |
| page | integer | No | Page number, default `1` |
| pageSize | integer | No | Items per page, max `10`, default `10` |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total record count |
| products | array | Top-selling product list |
| columns | array | Render column definitions |
| type | string | Render style |
| costToken | integer | Token cost |

**Product object:**

| Field | Type | Description |
|-------|------|-------------|
| title | string | Product title |
| productId | string | Product ID |
| region | string | Region code |
| price | number | Product price |
| minPrice | number | Min price |
| maxPrice | number | Max price |
| currency | string | Currency |
| totalSaleCnt | integer | Total sales |
| totalSale1dCnt | integer | 1-day sales (dateType=day) |
| totalSale7dCnt | integer | 7-day sales (dateType=week) |
| totalSale30dCnt | integer | 30-day sales (dateType=month) |
| totalSaleGmvAmt | number | Total GMV |
| totalSaleGmv1dAmt | number | 1-day GMV (dateType=day) |
| totalSaleGmv7dAmt | number | 7-day GMV (dateType=week) |
| totalSaleGmv30dAmt | number | 30-day GMV (dateType=month) |
| growthRate | number | Growth rate (percentage) |
| shopName | string | Shop name |
| shopTotalUnitsSold | integer | Shop total sales |
| shopSellerId | string | Shop seller ID |
| categoryName | string | Category name |
| productCommissionRate | number | Commission rate (basis points, 1000=10%) |
| imageUrl | string | Product image URL |
| offShelvesText | string | Delisted status: "是"=delisted, "否"=active |

### Key Usage Notes
- Both `region` and `dateInfo` are **mandatory**.
- No keyword search — use FastMoss Product Search for that.
- Max 10 items per page.
- 9 markets supported: US, GB, MX, ES, ID, VN, MY, TH, PH.
- Commission rate is in **basis points** (1000 = 10%) — differs from other TikTok tools.
- Data has T+1 statistical delay.
- `dateInfo.value` format must match the `type`: day → `YYYY-MM-DD`, week → `YYYY-周数`, month → `YYYY-MM`.
