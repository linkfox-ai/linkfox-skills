---
reportTypeId: sdAdvertisedProduct
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/advertised-product
timeUnit: [SUMMARY, DAILY]
groupBy: [advertiser]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 65
---

# SD 投放商品

投放商品报告提供 SD 活动所推广商品的效果数据。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdAdvertisedProduct |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | advertiser |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartRate |
| addToCartViews |
| addToCartClicks |
| adGroupId |
| adGroupName |
| adId |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| addToListFromViews |
| qualifiedBorrowsFromClicks |
| qualifiedBorrowsFromViews |
| royaltyQualifiedBorrowsFromClicks |
| royaltyQualifiedBorrowsFromViews |
| bidOptimization |
| brandedSearches |
| brandedSearchesClicks |
| brandedSearchesViews |
| brandedSearchRate |
| campaignBudgetCurrencyCode |
| campaignId |
| campaignName |
| clicks |
| cost |
| cumulativeReach |
| date |
| detailPageViews |
| detailPageViewsClicks |
| eCPAddToCart |
| eCPBrandSearch |
| endDate |
| impressions |
| impressionsFrequencyAverage |
| impressionsViews |
| kindleEditionNormalizedPagesRead |
| kindleEditionNormalizedPagesReadFromClicks |
| kindleEditionNormalizedPagesReadFromViews |
| kindleEditionNormalizedPagesRoyalties |
| kindleEditionNormalizedPagesRoyaltiesFromClicks |
| kindleEditionNormalizedPagesRoyaltiesFromViews |
| newToBrandDetailPageViewClicks |
| newToBrandDetailPageViewRate |
| newToBrandDetailPageViews |
| newToBrandDetailPageViewViews |
| newToBrandECPDetailPageView |
| newToBrandPurchases |
| newToBrandPurchasesClicks |
| newToBrandSales |
| newToBrandSalesClicks |
| newToBrandUnitsSold |
| newToBrandUnitsSoldClicks |
| promotedAsin |
| promotedSku |
| purchases |
| purchasesClicks |
| purchasesPromotedClicks |
| sales |
| salesClicks |
| salesPromotedClicks |
| startDate |
| unitsSold |
| unitsSoldClicks |
| videoCompleteViews |
| videoFirstQuartileViews |
| videoMidpointViews |
| videoThirdQuartileViews |
| videoUnmutes |
| viewabilityRate |
| viewClickThroughRate |

## 分组：advertiser

无附加指标。

**筛选**： 无

## 配置示例

```json
{
  "name": "SD advertised product report 3/5-3/10",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "advertiser"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "newToBrandSalesClicks",
      "detailPageViews"
    ],
    "reportTypeId": "sdAdvertisedProduct",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
