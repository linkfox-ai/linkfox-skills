---
reportTypeId: sbAdGroup
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/ad-group
timeUnit: [SUMMARY, DAILY]
groupBy: [adGroup]
format: [GZIP_JSON]
filters:
  - name: adStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [adGroup]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 广告组

广告组报告按广告组展示效果，覆盖指定广告类型在请求日期内有投放活动的广告组。例如，SB 广告组报告返回所选日期收到展示的全部 SB 广告组数据。

> **说明**
> SP 没有独立广告组报告，可在活动报告中使用 `adGroup` 分组获取广告组数据。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbAdGroup |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | adGroup |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| adGroupId |
| adGroupName |
| adStatus |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
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

## 分组：adGroup

无附加指标。

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| adStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 分组：campaign

无附加指标。

## 配置示例

```json
{
  "name": "SB ad group report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "adGroup"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adGroupId",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sbAdGroup",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
