---
reportTypeId: sdTargeting
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/targeting
timeUnit: [SUMMARY, DAILY]
groupBy: [targeting, matchedTarget]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 65
---

# SD 定向

定向报告按定向表达式拆分效果；SD 还可按 `matchedTarget` 展示实际匹配的 ASIN。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdTargeting |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | targeting / matchedTarget |
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
| targetingExpression |
| targetingId |
| targetingText |
| unitsSold |
| unitsSoldClicks |
| videoCompleteViews |
| videoFirstQuartileViews |
| videoMidpointViews |
| videoThirdQuartileViews |
| videoUnmutes |
| viewabilityRate |
| viewClickThroughRate |

## 分组：targeting

附加指标：

| 字段 |
|---|
| adKeywordStatus |
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

### targeting 分组

```json
{
  "name": "SD targeting report",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "targeting"
    ],
    "columns": [
      "adGroupId",
      "campaignId",
      "targetingId",
      "targetingText",
      "targetingExpression",
      "impressions",
      "clicks",
      "cost",
      "purchases",
      "sales",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sdTargeting",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```

### matchedTarget 分组

```json
{
  "name": "SD targeting matched-target report",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "matchedTarget"
    ],
    "columns": [
      "adGroupId",
      "campaignId",
      "matchedTargetAsin",
      "impressions",
      "clicks",
      "cost",
      "purchases",
      "sales",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sdTargeting",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
