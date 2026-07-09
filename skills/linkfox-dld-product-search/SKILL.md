---
name: linkfox-dld-product-search
description: 在中国1688批发平台（阿里巴巴国内B2B市场）上搜索和分析商品，用于找货源、供应商发现和选品。当用户提到1688商品搜索、1688找货源、在1688上找供应商、批发商品查询、工厂货源、一件代发供应商搜索、1688关键词选品、批发价格对比、按销量筛选、任何1688平台上的选品调研、1688 search, 1688 product selection, find suppliers, factory lookup, wholesale pricing, supplier search, domestic sourcing, 1688 products时触发此技能。即使用户未明确说"1688"，只要其需求涉及搜索批发商品、寻找国内供应商或从国内市场采购，也应触发此技能。
---

# 1688 Product Search (DianLeiDa)

This skill guides you on how to search and analyze products on the 1688 wholesale platform, helping e-commerce sellers and sourcing professionals find quality suppliers and profitable products.

## Core Concepts

This tool provides keyword-based product search on 1688 (China's largest B2B wholesale marketplace). It aggregates product listings with sales data, pricing tiers, supplier credentials, and fulfillment options. Data is sourced from DianLeiDa (store radar analytics) and covers real-time product listings with 7-day and 30-day sales metrics.

**Key terminology**:
- **Wholesale price** (`price`): The price per unit when ordering at the minimum batch quantity
- **Dropship price** (`consignPrice`): The price per unit for single-item dropshipping (typically higher than wholesale)
- **TrustPass years** (`tpYear`): The number of years the supplier has held Alibaba's TrustPass membership, indicating business longevity
- **Sales count** (`salesQuantity`): Total units sold in the selected time period
- **Order count** (`salesOrderCount`): Total number of separate orders in the selected time period
- **Estimated sales volume** (`estimatedSalesAmount`): Estimated revenue in the selected time period

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Product Title | title | Full product listing title | ... |
| Product ID | offerId | Unique 1688 product identifier | 805578065498 |
| Product URL | asinUrl | Direct link to the product listing | https://detail.1688.com/... |
| Image URL | imageUrl | Product main image | https://cbu01.alicdn.com/... |
| Wholesale Price | price | Unit price at batch quantity (CNY) | 12.50 |
| Dropship Price | consignPrice | Unit price for single-piece dropship (CNY) | 18.90 |
| Price Tiers | quantityPrices | Volume-based pricing breakdown | ... |
| Min Order Qty | quantityBegin | Minimum order quantity | 2 |
| Sales Order Count | salesOrderCount | Number of orders in the period | 350 |
| Sales Quantity | salesQuantity | Units sold in the period | 1200 |
| Est. Sales Amount | estimatedSalesAmount | Estimated revenue in the period | 45000 |
| Delivery Time | deliveryTime | Promised shipping time | 24h |
| Listing Date | availableDate | When the product was first listed | 2025-03-15 |
| Category | levelName | Product category path | ... |
| Shop Name | company | Supplier/store name | ... |
| Shop ID | shopId | Unique store identifier | ... |
| Shop URL | shopUrl | Link to the supplier's store | https://shop... |
| Currency | currency | Price currency (always CNY) | CNY |
| Data Type | dataType | Period indicator: weeklyData or monthlyData | monthlyData |

## Parameter Guide

### Search Keyword

The most important parameter. **Keywords must be in Chinese.** If the user provides an English term, translate it to Chinese before querying.

- `keyWord` (string, max 50 chars): The Chinese search term
- `searchType`: 1 = fuzzy match (default), 3 = exact match
- `goodsUrl`: Search by product URL instead of keyword
- `productIds`: Search by specific product IDs (comma-separated, max 20)

### Time Period

- `cycle`: `"7"` for last 7 days, `"30"` for last 30 days

### Sorting

- `sortField`: Field to sort by. Default: `orderCount30d`
  - `orderCount7d` / `orderCount30d` -- order count
  - `saleCount7d` / `saleCount30d` -- units sold
  - `saleVolume7d` / `saleVolume30d` -- estimated revenue
  - `offerCreateTime` -- listing date
  - `price` -- wholesale price
  - `consignPrice` -- dropship price
- `sortType`: `"desc"` (default) or `"asc"`

### Price Filters

- `beginPrice` / `endPrice`: Wholesale price range (CNY)
- `beginConsignPrice` / `endConsignPrice`: Dropship price range (CNY)

### Sales Filters

- `beginOrderCount` / `endOrderCount`: Order count range
- `beginSaleCount` / `endSaleCount`: Units sold range
- `beginSaleVolume` / `endSaleVolume`: Revenue range (CNY)

### Supplier Filters

- `companyType`: 0 = any (default), 1 = store, 2 = factory
- `shiLiType`: Seller tier. Comma-separated multi-select:
  - `superFactory` -- Super Factory
  - `Power` -- Power Merchant
  - `TrustPass` -- TrustPass members only
- `beginTpYear` / `endTpYear`: TrustPass membership year range

### Product Tags

- `offerType`: 0 = any, 2 = new product, 3 = 1688 Select, 4 = cross-border, 5 = customizable, 6 = top store pick

### Fulfillment & Services

- `sendTime`: Shipping speed. Comma-separated: `"24"`, `"48"`, `"72"`
- `faceToFaceSupport`: Platform face-sheet support. Comma-separated:
  - `441218` (Taobao), `386434` (Douyin), `422914` (Pinduoduo), `422978` (Xiaohongshu), `386370` (Kuaishou)
- `proxyRights`: Dropship benefits. Comma-separated:
  - `4360897` (free shipping dropship), `449154` (buy now pay later)
- `shopService`: Seller services. Comma-separated:
  - `4057409` (worry-free purchase), `888777` (deep verification report)
- `buyerProtections`: Buyer guarantees. Comma-separated Chinese strings:
  - `商品包邮` (free shipping), `7天包退货` (7-day returns), `支持运费险` (shipping insurance)

### Listing Date Filter

- `beginOfferCreateTime` / `endOfferCreateTime`: Date range in `YYYY-MM-DD` format

### Pagination

- `pageIndex`: Page number, starting from 1 (default: 1)
- `pageSize`: Results per page, 10-100 (default: 20)

### Example Queries

**1. Basic keyword search -- top sellers for "yoga mat"**
```json
{"keyWord": "瑜伽垫", "cycle": "30", "sortField": "saleCount30d", "sortType": "desc", "pageSize": 20}
```

**2. Factory-only search with price range**
```json
{"keyWord": "蓝牙耳机", "companyType": 2, "beginPrice": 10, "endPrice": 50, "cycle": "30", "sortField": "orderCount30d"}
```

**3. Cross-border products with dropship support**
```json
{"keyWord": "手机壳", "offerType": 4, "proxyRights": "4360897", "cycle": "7", "sortField": "saleVolume7d"}
```

**4. New products listed recently, sorted by listing date**
```json
{"keyWord": "夏季连衣裙", "offerType": 2, "sortField": "offerCreateTime", "sortType": "desc", "pageSize": 50}
```

**5. High-volume products from Super Factories**
```json
{"keyWord": "数据线", "shiLiType": "superFactory", "beginSaleCount": 1000, "cycle": "30", "sortField": "saleCount30d"}
```

**6. Search by product URL**
```json
{"goodsUrl": "https://detail.1688.com/offer/805578065498.html", "cycle": "30"}
```

## Display Rules

1. **Present data clearly**: Show results in structured tables with product title, price, sales metrics, and supplier info. Include product URLs so users can visit listings directly.
2. **Price context**: Always show both wholesale price and dropship price when available, so users can compare margins.
3. **Sales metrics**: Clearly label whether metrics are 7-day or 30-day figures based on the `cycle` parameter used.
4. **Image display**: When `imageUrl` is available, display product images to help users visually identify products.
5. **Pagination notice**: When `total` exceeds the returned page size, inform users of the total result count and that they can request additional pages.
6. **Error handling**: If a query returns an error, explain the issue and suggest adjusting parameters (e.g., broadening filters, checking keyword spelling).
7. **Keyword translation**: If the user provides English product terms, translate to Chinese before calling the API, and note this translation in your response.
## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Find suppliers for XX on 1688" | Keyword product search |
| "What's selling well on 1688" | Top-selling product discovery |
| "Find cheap XX from factories" | Factory sourcing with price filters |
| "1688 dropshipping suppliers for XX" | Dropship-enabled product search |
| "Compare prices for XX on 1688" | Price comparison across suppliers |
| "New products on 1688 for XX" | New product discovery |
| "Find 1688 products for cross-border" | Cross-border product sourcing |
| "Which 1688 suppliers ship within 24h" | Fulfillment speed filtering |
| "Top factories for XX" | Super Factory / Power Merchant search |
| "Find this 1688 product" (with URL or ID) | Direct product lookup |

## Not Applicable

- Amazon or other non-1688 platform product research
- 1688 store/shop-level analytics (store traffic, store rankings)
- 1688 advertising or promotion strategies
- Product review or rating analysis
- Logistics cost calculation or freight estimation
- Order placement or transaction processing
- User already has local product data files to analyze

**Boundary judgment**: When users say "sourcing", "find suppliers", or "wholesale products", if it involves searching for specific products on the 1688 platform with filters like price, sales, or supplier type, this skill applies. If they need store-level analytics, advertising optimization, or operations beyond product search, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
