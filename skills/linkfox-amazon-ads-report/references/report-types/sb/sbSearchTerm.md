---
reportTypeId: sbSearchTerm
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/search-term
timeUnit: [SUMMARY, DAILY]
groupBy: [searchTerm]
format: [GZIP_JSON]
filters:
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED]
    applicableWhenGroupBy: [searchTerm]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB 搜索词

搜索词报告按定向表达式和关键词拆分搜索词效果。只包含产生至少一次广告点击的展示；可用 `keywordType` 筛选定向表达式或关键词。

> **说明**
> 商品详情页广告位没有关联搜索关键词时，报告中的搜索词为星号 `*`。

> **说明**
> 报告预览期不提供 `isMultiAdGroupsEnabled=False` 的 SB 活动数据。v3 报告支持全部 SB 活动的正式可用状态以 Amazon 版本说明为准，不能假定此限制已解除。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbSearchTerm |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 60 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | searchTerm |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| adGroupId |
| adGroupName |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
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
| endDate |
| impressions |
| keywordBid |
| keywordId |
| keywordText |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| matchType |
| purchases |
| purchasesClicks |
| sales |
| salesClicks |
| searchTerm |
| startDate |
| unitsSold |
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

## 分组：searchTerm

附加指标：

| 字段 |
|---|
| adKeywordStatus |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| keywordType | array[string] | BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED |

## 配置示例

```json
{
  "name": "SP search terms report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "searchTerm"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adGroupId",
      "startDate",
      "endDate",
      "matchType",
      "keywordId",
      "searchTerm"
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
    "reportTypeId": "sbSearchTerm",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
