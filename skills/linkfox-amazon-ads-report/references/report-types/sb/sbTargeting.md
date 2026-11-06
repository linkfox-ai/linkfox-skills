---
reportTypeId: sbTargeting
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/targeting
timeUnit: [SUMMARY, DAILY]
groupBy: [targeting]
format: [GZIP_JSON]
filters:
  - name: adKeywordStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [targeting]
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED, THEME]
    applicableWhenGroupBy: [targeting]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 定向

定向报告按定向表达式与关键词拆分效果指标。

> **说明**
> 定向报告不支持 Sponsored TV 的非 Amazon 站内销售商品广告主（non-endemic advertisers）。

## 关键词与定向表达式选择

仅查看定向表达式时，将 `keywordType` 设为 `TARGETING_EXPRESSION` 与 `TARGETING_EXPRESSION_PREDEFINED`；仅查看关键词时设为 `BROAD`、`PHRASE`、`EXACT`。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbTargeting |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | targeting |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| adGroupId |
| adGroupName |
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
| keywordBid |
| keywordId |
| adKeywordStatus |
| keywordText |
| keywordType |
| matchType |
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
| targetingExpression |
| targetingId |
| targetingText |
| targetingType |
| topOfSearchImpressionShare |
| unitsSold |

## 分组：targeting

无附加指标。

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| adKeywordStatus | array[string] | ENABLED, PAUSED, ARCHIVED |
| keywordType | array[string] | BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED, THEME |

## 配置示例

### 仅关键词

```json
{
  "name": "SB keywords report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "targeting"
    ],
    "columns": [
      "adGroupId",
      "campaignId",
      "keywordId",
      "matchType",
      "keywordText",
      "impressions",
      "clicks",
      "cost",
      "startDate",
      "endDate"
    ],
    "filters": [
      {
        "field": "keywordType",
        "values": [
          "BROAD",
          "PHRASE",
          "EXACT"
        ]
      }
    ],
    "reportTypeId": "sbTargeting",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
