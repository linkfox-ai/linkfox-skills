---
reportTypeId: spSearchTerm
adProduct: SPONSORED_PRODUCTS
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
  dataRetentionDays: 65
---

# SP 搜索词

搜索词报告按定向表达式和关键词拆分搜索词效果。只包含产生至少一次广告点击的展示；可用 `keywordType` 筛选定向表达式或关键词。

> **说明**
> 商品详情页广告位没有关联搜索关键词时，报告中的搜索词为星号 `*`。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | spSearchTerm |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | searchTerm |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| impressions |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| clicks |
| costPerClick |
| clickThroughRate |
| cost |
| purchases1d |
| purchases7d |
| purchases14d |
| purchases30d |
| purchasesSameSku1d |
| purchasesSameSku7d |
| purchasesSameSku14d |
| purchasesSameSku30d |
| unitsSoldClicks1d |
| unitsSoldClicks7d |
| unitsSoldClicks14d |
| unitsSoldClicks30d |
| sales1d |
| sales7d |
| sales14d |
| sales30d |
| attributedSalesSameSku1d |
| attributedSalesSameSku7d |
| attributedSalesSameSku14d |
| attributedSalesSameSku30d |
| unitsSoldSameSku1d |
| unitsSoldSameSku7d |
| unitsSoldSameSku14d |
| unitsSoldSameSku30d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| salesOtherSku7d |
| unitsSoldOtherSku7d |
| acosClicks7d |
| acosClicks14d |
| roasClicks7d |
| roasClicks14d |
| keywordId |
| keyword |
| campaignBudgetCurrencyCode |
| date |
| startDate |
| endDate |
| portfolioId |
| searchTerm |
| campaignName |
| campaignId |
| campaignBudgetType |
| campaignBudgetAmount |
| campaignStatus |
| keywordBid |
| adGroupName |
| adGroupId |
| keywordType |
| matchType |
| targeting |
| adKeywordStatus |

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

### 仅定向表达式

```json
{
  "name": "SP search term report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "searchTerm"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adGroupId",
      "date",
      "targeting",
      "searchTerm",
      "keywordType",
      "keywordId"
    ],
    "filters": [
      {
        "field": "keywordType",
        "values": [
          "TARGETING_EXPRESSION",
          "TARGETING_EXPRESSION_PREDEFINED"
        ]
      }
    ],
    "reportTypeId": "spSearchTerm",
    "timeUnit": "DAILY",
    "format": "GZIP_JSON"
  }
}
```

### 仅关键词

```json
{
  "name": "SB search terms report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
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
      "keywordType",
      "keyword",
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
    "reportTypeId": "spSearchTerm",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
