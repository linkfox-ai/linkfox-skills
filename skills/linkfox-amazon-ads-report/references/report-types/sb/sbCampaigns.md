---
reportTypeId: sbCampaigns
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/campaign
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign]
format: [GZIP_JSON]
filters:
  - name: campaignStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [campaign]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 广告活动

活动报告按活动展示效果，覆盖指定广告类型在请求日期内有投放活动的全部活动。例如，SP 活动报告返回所选日期收到展示的全部 SP 活动数据。活动报告也可按广告组和广告位细分，具体可用分组以本文件配置为准。

> **说明**
> 筛选器必须由请求中的全部 `groupBy` 值共同支持。对于活动报告，只有包含单个 `groupBy` 值时才支持筛选。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbCampaigns |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaign |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
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
| brandStorePageView |
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
| topOfSearchImpressionShare |
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
| viewClickThroughRate |

## 分组：campaign

附加指标：

| 字段 |
|---|
| campaignBudgetAmount |
| campaignBudgetCurrencyCode |
| campaignBudgetType |
| longTermSales |
| longTermROAS |
| topOfSearchImpressionShare |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| campaignStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 配置示例

```json
{
  "name": "SB campaigns report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "campaign"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sbCampaigns",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
