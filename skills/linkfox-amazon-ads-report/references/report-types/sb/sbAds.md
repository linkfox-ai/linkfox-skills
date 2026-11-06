---
reportTypeId: sbAds
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/ad
timeUnit: [SUMMARY, DAILY]
groupBy: [ads]
format: [GZIP_JSON]
filters:
  - name: adStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [ads]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 广告

此报告在广告层级展示活动效果。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbAds |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | ads |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| addToListFromClicks |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrowsFromClicks |
| adGroupId |
| adGroupName |
| adId |
| brandedSearches |
| brandedSearchesClicks |
| campaignBudgetAmount |
| campaignBudgetCurrencyCode |
| campaignBudgetType |
| campaignId |
| campaignName |
| campaignStatus |
| clicks |
| cost |
| costType |
| date |
| detailPageViews |
| detailPageViewsClicks |
| eCPAddToCart |
| endDate |
| impressions |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| newToBrandDetailPageViewRate |
| newToBrandDetailPageViews |
| newToBrandDetailPageViewsClicks |
| newToBrandECPDetailPageView |
| newToBrandPurchases |
| newToBrandPurchasesClicks |
| newToBrandPurchasesPercentage |
| newToBrandPurchasesRate |
| newToBrandSales |
| newToBrandSalesClicks |
| newToBrandSalesPercentage |
| newToBrandUnitsSold |
| newToBrandUnitsSoldClicks |
| newToBrandUnitsSoldPercentage |
| purchases |
| purchasesClicks |
| purchasesPromoted |
| sales |
| salesClicks |
| salesPromoted |
| startDate |
| unitsSold |
| unitsSoldClicks |
| video5SecondViewRate |
| video5SecondViews |
| videoCompleteViews |
| videoFirstQuartileViews |
| videoMidpointViews |
| videoThirdQuartileViews |
| videoUnmutes |
| viewabilityRate |
| viewableImpressions |

## 分组：ads

无附加指标。

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| adStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 配置示例

```json
{
  "name": "SB advertised product report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "ads"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adId",
      "adGroupId"
    ],
    "reportTypeId": "sbAds",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
