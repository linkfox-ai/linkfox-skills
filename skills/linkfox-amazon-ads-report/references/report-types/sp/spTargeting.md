---
reportTypeId: spTargeting
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/targeting
timeUnit: [SUMMARY, DAILY]
groupBy: [targeting]
format: [GZIP_JSON]
filters:
  - name: adKeywordStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [targeting]
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED]
    applicableWhenGroupBy: [targeting]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP 定向

定向报告按定向表达式与关键词拆分效果指标。

> **说明**
> 定向报告不支持 Sponsored TV 的非 Amazon 站内销售商品广告主（non-endemic advertisers）。

## 关键词与定向表达式选择

仅查看定向表达式时，将 `keywordType` 设为 `TARGETING_EXPRESSION` 与 `TARGETING_EXPRESSION_PREDEFINED`；仅查看关键词时设为 `BROAD`、`PHRASE`、`EXACT`。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | spTargeting |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 95 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | targeting |
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
| topOfSearchImpressionShare |

## 分组：targeting

附加指标：

| 字段 |
|---|
| adKeywordStatus |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| adKeywordStatus | array[string] | ENABLED, PAUSED, ARCHIVED |
| keywordType | array[string] | BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED |

## 配置示例

### 仅定向表达式

```json
{
  "name": "SP targeting report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "targeting"
    ],
    "columns": [
      "adGroupId",
      "campaignId",
      "targeting",
      "keywordId",
      "matchType",
      "impressions",
      "clicks",
      "cost",
      "purchases1d",
      "purchases7d",
      "purchases14d",
      "purchases30d",
      "startDate",
      "endDate"
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
    "reportTypeId": "spTargeting",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```

### 仅关键词

```json
{
  "name": "SP keywords report 9/5-9/10",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "targeting"
    ],
    "columns": [
      "adGroupId",
      "campaignId",
      "keywordId",
      "matchType",
      "keyword",
      "impressions",
      "clicks",
      "cost",
      "purchases1d",
      "purchases7d",
      "purchases14d",
      "purchases30d",
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
    "reportTypeId": "spTargeting",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
