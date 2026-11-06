---
reportTypeId: sdAdGroup
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/ad-group
timeUnit: [SUMMARY, DAILY]
groupBy: [adGroup, matchedTarget]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 65
---

# SD 广告组

广告组报告按广告组展示效果，覆盖指定类型在请求日期内有投放活动的全部活动。SD 广告组报告还可按 `matchedTarget` 获取更细粒度数据。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdAdGroup |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | adGroup / matchedTarget |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| addToCartViews |
| adGroupId |
| adGroupName |
| addToList |
| addToListFromClicks |
| addToListFromViews |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| qualifiedBorrowsFromViews |
| royaltyQualifiedBorrows |
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
| impressionsViews |
| newToBrandPurchases |
| kindleEditionNormalizedPagesRead |
| kindleEditionNormalizedPagesReadFromClicks |
| kindleEditionNormalizedPagesReadFromViews |
| kindleEditionNormalizedPagesRoyalties |
| kindleEditionNormalizedPagesRoyaltiesFromClicks |
| kindleEditionNormalizedPagesRoyaltiesFromViews |
| newToBrandPurchasesClicks |
| newToBrandSales |
| newToBrandSalesClicks |
| newToBrandUnitsSold |
| newToBrandUnitsSoldClicks |
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

## 分组：adGroup

附加指标：

| 字段 |
|---|
| cumulativeReach |
| impressionsFrequencyAverage |
| newToBrandDetailPageViewClicks |
| newToBrandDetailPageViewRate |
| newToBrandDetailPageViews |
| newToBrandDetailPageViewViews |
| newToBrandECPDetailPageView |

**筛选**： 无

## 分组：matchedTarget

附加指标：

| 字段 |
|---|
| matchedTargetAsin |

**筛选**： 无

## 配置示例

```json
{
  "name": "SD ad group report",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "adGroup"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adGroupId",
      "adGroupName",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sdAdGroup",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
