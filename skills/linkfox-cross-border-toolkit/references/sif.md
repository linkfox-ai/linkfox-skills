# SIF Data Analysis — Tool Reference

## 1. ASIN Keywords (ASIN关键词反查)

**Endpoint**: `POST https://tool-gateway.linkfox.com/sif/asinKeywords`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| asin | string | Yes | — | ASIN code, max 1000 chars. Only one ASIN per request |
| country | string | No | US | Marketplace code. Values: US, CA, MX, UK, DE, FR, IT, ES, JP, IN, AU, BR, NL, SE, PL, TR, AE, SA, SG |
| keyword | string | No | — | Filter results to keywords containing this text. Translate to target marketplace language. Max 1000 chars |
| conditions | string | No | — | Comma-separated condition filters. Values: `nfPosition` (organic traffic), `isSpAd` (SP ad), `isBrandAd` (brand ad), `isVedioAd` (video ad), `isAC` (Amazon's Choice), `isER` (Editorial Recommendations), `isTr` (Top Rated), `isMainKw` (main traffic), `isAccurateKw` (precise traffic), `isAccurateAboveKw` (precise high-volume), `isAccurateTailKw` (precise long-tail), `isPurchaseKw` (purchase-converting), `isQualityKw` (high-quality conversion), `isStableKw` (stable conversion), `isLossKw` (conversion-loss), `isInvalidKw` (invalid-exposure) |
| sortBy | string | No | — | Sort field. Values: `lastRank` (organic rank), `adLastRank` (ad rank), `updateTime` (update time), `searchesRank` (search popularity rank), `estSearchesNum` (monthly search volume). Empty = system default |
| desc | boolean | No | true | Descending order. `false` for ascending |
| pageNum | integer | No | 1 | Page number |
| pageSize | integer | No | 100 | Results per page. Range: 10-100 |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| code | string | Return code |
| msg | string | Message |
| total | integer | Actual data count returned |
| data | array | Keyword data array |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| isParentAsin | boolean | Whether searched ASIN is a parent |
| hasVaiants | boolean | Whether ASIN has variants |
| abaCreateDateWeek | string | Latest weekly ABA time |
| costTime | integer | Processing time (ms) |
| costToken | integer | Tokens consumed |

#### data Item

| Field | Type | Description |
|-------|------|-------------|
| keyword | string | Search keyword |
| asin | string | Product ASIN |
| productNaturalRank | integer | Organic search rank (1 = first position) |
| naturalRankDisplay | string | Organic rank display text |
| productAdRank | integer | SP ad rank position |
| adRankDisplay | string | Ad rank display text |
| weeklySearchVolume | integer | Estimated weekly searches |
| keywordPopularityRank | integer | Keyword search popularity rank (lower = more popular) |
| trafficShare | number | Traffic share this keyword contributes to the ASIN (1 = 100%) |
| displayPositionTypes | array | Display positions: `natural`, `ac`, `sp`, `top`, `bottom`, `er`, `vedio`, `tr`, `trfob` |
| trafficCharacteristicMarkers | array | Traffic markers: `isMainKw`, `isAccurateKw`, `isAccurateAboveKw`, `isAccurateTailKw` |
| conversionPerformanceMarkers | array | Conversion markers: `isPurchaseKw`, `isQualityKw`, `isStableKw`, `isLossKw`, `isInvalidKw` |
| lastNaturalRankTime | string | Last valid organic rank time |
| lastAdRankTime | string | Last valid ad rank time |
| updateTime | string | Data update time |

### Key Usage Notes

- **Single ASIN per request**; multi-ASIN comparison requires separate calls.
- **Page size cap**: Max 100 results per page; use `pageNum` for pagination.
- Keyword filter should be in the target marketplace's language.
- Lower rank value = better position. Rank 1 = top of results.
- **19 marketplaces** supported (vs. Jungle Scout's 10).

---

## 2. ASIN Summary (ASIN流量来源)

**Endpoint**: `POST https://tool-gateway.linkfox.com/sif/asinSummary`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| searchValue | string | Yes | — | ASIN code(s), comma-separated, max 10 ASINs, max 1000 chars |
| country | string | No | US | Marketplace code. Values: US, CA, MX, UK, DE, FR, IT, ES, JP, IN, AU, BR, NL, SE, PL, TR, AE, SA, SG |
| pageNum | integer | No | 1 | Page number |
| pageSize | integer | No | 100 | Results per page. Range: 10-100 |
| desc | boolean | No | true | Descending order |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| code | string | Return code |
| msg | string | Message |
| total | integer | Actual data count returned |
| data | array | ASIN summary data array |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| isParentAsin | boolean | Whether searched ASIN is a parent |
| variantsNum | integer | Variants with keywords count |
| noKeywordVariantsNum | integer | Variants without keywords count |
| costTime | integer | Processing time (ms) |
| costToken | integer | Tokens consumed |

#### data Item

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN code |
| productTitle | string | Full product title |
| productCategory | string | Product category |
| productPrice | number | Current listing price |
| productImageUrl | string | Main product image URL |
| productFeatures | array | Product features/bullet points |
| customerRatingCount | integer | Total customer ratings |
| isVariantProduct | boolean | Whether ASIN is a variant |
| totalExposureScore | number | Total exposure score across all channels |
| totalTrafficKeywordCount | integer | Total keywords across all channels |
| naturalSearchExposureScore | number | Organic search exposure score |
| naturalSearchExposureRatio | number | Organic search share of total exposure |
| naturalSearchKeywordCount | integer | Organic search keyword count |
| sponsoredProductsExposureScore | number | SP ad exposure score |
| sponsoredProductsExposureRatio | number | SP ad share of total exposure |
| sponsoredProductsKeywordCount | integer | SP ad keyword count |
| brandAdExposureScore | number | Brand ad exposure score |
| brandAdExposureRatio | number | Brand ad share of total exposure |
| brandAdKeywordCount | integer | Brand ad total keyword count |
| topBrandAdKeywordCount | integer | Top-of-page brand ad keyword count |
| bottomBrandAdKeywordCount | integer | Bottom-of-page brand ad keyword count |
| videoAdExposureScore | number | Video ad exposure score |
| videoAdExposureRatio | number | Video ad share of total exposure |
| videoAdKeywordCount | integer | Video ad keyword count |
| amazonsChoiceExposureScore | number | Amazon's Choice exposure score |
| amazonsChoiceExposureRatio | number | AC share of total exposure |
| amazonsChoiceKeywordCount | integer | AC keyword count |
| editorialRecommendationsExposureScore | number | Editorial Recommendations exposure score |
| editorialRecommendationsExposureRatio | number | ER share of total exposure |
| editorialRecommendationsKeywordCount | integer | ER keyword count |
| topRatedExposureScore | number | Top Rated exposure score |
| topRatedExposureRatio | number | TR share of total exposure |
| topRatedKeywordCount | integer | TR keyword count |
| frequentlyBoughtKeywordCount | integer | Frequently Bought keyword count |
| ppcTrafficSources | array | PPC ad traffic source markers (SP, Top Brand Ad, Bottom Brand Ad, Video Ad) |
| naturalSearchTrafficSources | array | Organic search traffic markers |
| amazonRecommendationSources | array | Amazon recommendation markers (Best Seller, AC, ER, TR, TRFOB, etc.) |
| promotionalDealSources | array | Promotional deal markers (Coupon, Limited Time Deal, Lowest Price in 30 Days, etc.) |
| isMonitored | boolean | Whether ASIN is on monitoring list |
| monitoringStartTime | string | Monitoring start time |

### Key Usage Notes

- **Max 10 ASINs** per request (comma-separated in `searchValue`).
- **19 marketplaces** supported.
- Exposure scores are relative (useful for cross-channel/cross-ASIN comparison), not absolute traffic volumes.
- Snapshot data, not historical trends.

---

## 3. Keyword Overview (关键词竞品概览)

**Endpoint**: `POST https://tool-gateway.linkfox.com/sif/keywordOverview`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | Yes | — | Search keyword. Translate to target marketplace language. Max 1000 chars |
| country | string | No | US | Marketplace code. Values: US, CA, MX, UK, DE, FR, IT, ES, JP, IN, AU, BR, NL, SE, PL, TR, AE, SA, SG |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| msg | string | Message |
| total | integer | Data count (typically 1) |
| code | string | Return code |
| data | array | Keyword data array |
| costTime | integer | Processing time (ms) |
| costToken | integer | Tokens consumed |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |

#### data Item

| Field | Type | Description |
|-------|------|-------------|
| keyword | string | Queried keyword |
| keywordPopularityRank | integer | Keyword popularity rank (lower = more popular) |
| estimatedWeeklySearchVolume | integer | Estimated weekly search count |
| supplyDemandRatio | number | Supply-demand ratio (product count / monthly search volume; lower = less competition) |
| totalSearchResultProductCount | integer | Total products under this keyword (organic + ads + recommendations) |
| naturalSearchProductCount | integer | Products in organic search results |
| sponsoredProductsCount | integer | Products running SP ads |
| brandAdProductCount | integer | Products running brand ads |
| videoAdProductCount | integer | Products running video ads |
| paidAdvertisingProductCount | integer | All PPC ad products combined |
| amazonChoiceProductCount | integer | Products with AC badge |
| topRatedProductCount | integer | Products in Top Rated section |
| searchRecommendationProductCount | integer | Products recommended during search |
| editorialRecommendationsProductCount | integer | Products in Editorial Recommendations |
| totalMarketplaceKeywordCount | integer | Total keywords in the marketplace |
| keywordDataUpdateTime | string | Data last update time |

### Key Usage Notes

- **Single keyword per request**; returns typically 1 record.
- **19 marketplaces** supported.
- Supply-demand ratio: <1 = high demand / low supply (opportunity); >5 = saturated.
- Keyword should be in the target marketplace's local language for best accuracy.

---

## 4. Keyword Traffic Source Summary (关键词流量来源)

**Endpoint**: `POST https://tool-gateway.linkfox.com/sif/keywordSummary`
**Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| searchKeyword | string | Yes | — | Search keyword. Translate to target marketplace language. Max 1000 chars |
| country | string | No | US | Marketplace code. Values: US, CA, MX, UK, DE, FR, IT, ES, JP, IN, AU, BR, NL, SE, PL, TR, AE, SA, SG |
| condition | string | No | — | Single condition filter. Values: `nfPosition` (organic), `isSpAd` (SP ad), `isTopAd` (top brand ad), `isBottomAd` (bottom brand ad), `isVedioAd` (video ad), `isAC` (Amazon's Choice), `isER` (Editorial Recommendations), `isTR` (Top Rated), `isTRFOB` (Top Rated Frequently Bought), `isBrandAd` (brand ad combined), `isPPCAd` (all PPC ads), `isSearchRecommend` (search recommendation) |
| pageNum | integer | No | 1 | Page number |
| pageSize | integer | No | 100 | Results per page. Range: 10-100 |
| desc | boolean | No | true | Descending order |

### Response Fields

#### Top-Level

| Field | Type | Description |
|-------|------|-------------|
| code | string | Return code |
| msg | string | Message |
| total | integer | Actual data count returned |
| data | array | Product keyword traffic data array |
| columns | array | Render columns |
| type | string | Render style |
| title | string | Title |
| isParentAsin | boolean | Whether parent ASIN |
| variantsNum | integer | Variants with keywords count |
| noKeywordVariantsNum | integer | Variants without keywords count |
| costTime | integer | Processing time (ms) |
| costToken | integer | Tokens consumed |

#### data Item

| Field | Type | Description |
|-------|------|-------------|
| asin | string | ASIN code |
| productTitle | string | Full product title |
| productCategory | string | Product category |
| productPrice | number | Current listing price |
| productImageUrl | string | Main product image URL |
| productFeatures | array | Product features/bullet points |
| customerRatingCount | integer | Total customer ratings |
| isVariantProduct | boolean | Whether ASIN is a variant |
| isMonitored | boolean | Whether on monitoring list |
| monitoringStartTime | string | Monitoring start time |
| totalTrafficKeywordCount | integer | Total traffic keywords across all channels |
| totalExposureScore | number | Total exposure score |
| naturalSearchKeywordCount | integer | Organic search keyword count |
| naturalSearchExposureScore | number | Organic search exposure score |
| naturalSearchExposureRatio | number | Organic search exposure ratio |
| naturalSearchTrafficSources | array | Organic search traffic markers |
| sponsoredProductsKeywordCount | integer | SP ad keyword count |
| sponsoredProductsExposureScore | number | SP ad exposure score |
| sponsoredProductsExposureRatio | number | SP ad exposure ratio |
| brandAdKeywordCount | integer | Brand ad total keyword count |
| brandAdExposureScore | number | Brand ad exposure score |
| brandAdExposureRatio | number | Brand ad exposure ratio |
| topBrandAdKeywordCount | integer | Top-of-page brand ad keyword count |
| bottomBrandAdKeywordCount | integer | Bottom-of-page brand ad keyword count |
| videoAdKeywordCount | integer | Video ad keyword count |
| videoAdExposureScore | number | Video ad exposure score |
| videoAdExposureRatio | number | Video ad exposure ratio |
| amazonsChoiceKeywordCount | integer | AC keyword count |
| amazonsChoiceExposureScore | number | AC exposure score |
| amazonsChoiceExposureRatio | number | AC exposure ratio |
| editorialRecommendationsKeywordCount | integer | ER keyword count |
| editorialRecommendationsExposureScore | number | ER exposure score |
| editorialRecommendationsExposureRatio | number | ER exposure ratio |
| topRatedKeywordCount | integer | TR keyword count |
| topRatedExposureScore | number | TR exposure score |
| topRatedExposureRatio | number | TR exposure ratio |
| frequentlyBoughtKeywordCount | integer | Frequently Bought keyword count |
| ppcTrafficSources | array | PPC ad traffic source markers |
| amazonRecommendationSources | array | Amazon recommendation markers (Best Seller, AC, ER, TR, TRFOB, etc.) |
| promotionalDealSources | array | Promotional deal markers (Coupon, Limited Time Deal, Lowest Price in 30 Days, etc.) |

### Key Usage Notes

- **Single condition filter** per request. Compare multiple traffic sources with separate calls.
- **19 marketplaces** supported.
- Max 100 results per page; use pagination for large result sets.
- Keyword should be in the marketplace's local language for best accuracy.
- Exposure ratios are 0-1 decimals; display as percentages.

---

## Common Error Codes (All SIF Tools)

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse response data normally |
| 401 | Auth failure | Check `Authorization` header with correct API Key |
| Other | Business error | Refer to `errmsg` field for details |

## Supported Marketplaces (All SIF Tools)

19 Amazon marketplaces:

| Marketplace | Code |
|-------------|------|
| United States | US |
| Canada | CA |
| Mexico | MX |
| United Kingdom | UK |
| Germany | DE |
| France | FR |
| Italy | IT |
| Spain | ES |
| Japan | JP |
| India | IN |
| Australia | AU |
| Brazil | BR |
| Netherlands | NL |
| Sweden | SE |
| Poland | PL |
| Turkey | TR |
| United Arab Emirates | AE |
| Saudi Arabia | SA |
| Singapore | SG |
