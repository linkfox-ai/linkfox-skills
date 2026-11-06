---
reportTypeId: sdCampaigns
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/campaign
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign, matchedTarget]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 65
---

# SD 广告活动

活动报告按活动展示效果，覆盖指定广告类型在请求日期内有投放活动的全部活动。SD 活动报告还可按 `matchedTarget` 获取更细粒度数据。

> **说明**
> 筛选器必须由请求中的全部 `groupBy` 值共同支持。对于活动报告，只有包含单个 `groupBy` 值时才支持筛选。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdCampaigns |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaign / matchedTarget |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| addToCartViews |
| addToList |
| addToListFromClicks |
| addToListFromViews |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| qualifiedBorrowsFromViews |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
| royaltyQualifiedBorrowsFromViews |
| brandedSearches |
| brandedSearchesClicks |
| brandedSearchesViews |
| brandedSearchRate |
| campaignBudgetCurrencyCode |
| campaignId |
| campaignName |
| clicks |
| cost |
| date |
| detailPageViews |
| detailPageViewsClicks |
| eCPAddToCart |
| eCPBrandSearch |
| endDate |
| impressions |
| impressionsViews |
| kindleEditionNormalizedPagesRead |
| kindleEditionNormalizedPagesReadFromClicks |
| kindleEditionNormalizedPagesReadFromViews |
| kindleEditionNormalizedPagesRoyalties |
| kindleEditionNormalizedPagesRoyaltiesFromClicks |
| kindleEditionNormalizedPagesRoyaltiesFromViews |
| newToBrandPurchases |
| newToBrandPurchasesClicks |
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

## 分组：campaign

附加指标：

| 字段 |
|---|
| campaignBudgetAmount |
| campaignStatus |
| costType |
| cumulativeReach |
| impressionsFrequencyAverage |
| longTermSales |
| longTermROAS |
| newToBrandDetailPageViewClicks |
| newToBrandDetailPageViewRate |
| newToBrandDetailPageViews |
| newToBrandDetailPageViewViews |
| newToBrandECPDetailPageView |
| newToBrandSales |

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
  "name": "SD campaigns report",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "campaign"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "campaignName",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sdCampaigns",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
