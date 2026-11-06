---
reportTypeId: sbCampaignPlacement
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/placement
timeUnit: [SUMMARY, DAILY]
groupBy: [campaignPlacement, campaign]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 活动广告位

广告位报告按广告展示位置拆分效果。

> **说明**
> SP 没有独立广告位报告，可在活动报告中使用 `campaignPlacement` 分组获取广告位数据。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbCampaignPlacement |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaignPlacement / campaign |
| format | GZIP_JSON |

按广告位查看效果时，使用 `campaignPlacement` 分组，并在 `columns` 中包含该分组的 `placementClassification`；`campaign` 是活动维度，不能代替广告位拆分。

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
| viewClickThroughRate |

## 分组：campaignPlacement

附加指标：

| 字段 |
|---|
| placementClassification |

## 分组：campaign

无附加指标。

## 配置示例

```json
{
  "name": "SB placement report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "campaignPlacement"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "placementClassification",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sbCampaignPlacement",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
