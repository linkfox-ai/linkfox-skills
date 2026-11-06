---
reportTypeId: spPurchasedProduct
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/purchased-product
timeUnit: [SUMMARY, DAILY]
groupBy: [asin]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP 购买商品

SP 购买商品报告提供被购买但未在该活动推广的商品效果，包含定向表达式与关键词 ID。下载后可按 `keywordType` 在本地筛选，区分定向表达式和关键词。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | spPurchasedProduct |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 95 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | asin |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| date |
| startDate |
| endDate |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
| portfolioId |
| campaignName |
| campaignId |
| adGroupName |
| adGroupId |
| keywordId |
| keyword |
| keywordType |
| advertisedAsin |
| purchasedAsin |
| advertisedSku |
| campaignBudgetCurrencyCode |
| matchType |
| unitsSoldClicks1d |
| unitsSoldClicks7d |
| unitsSoldClicks14d |
| unitsSoldClicks30d |
| sales1d |
| sales7d |
| sales14d |
| sales30d |
| purchases1d |
| purchases7d |
| purchases14d |
| purchases30d |
| unitsSoldOtherSku1d |
| unitsSoldOtherSku7d |
| unitsSoldOtherSku14d |
| unitsSoldOtherSku30d |
| salesOtherSku1d |
| salesOtherSku7d |
| salesOtherSku14d |
| salesOtherSku30d |
| purchasesOtherSku1d |
| purchasesOtherSku7d |
| purchasesOtherSku14d |
| purchasesOtherSku30d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |

## 分组：asin

无附加指标。

**筛选**： 无

## 配置示例

```json
{
  "name": "SP purchased product report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "asin"
    ],
    "columns": [
      "purchasedAsin",
      "advertisedAsin",
      "adGroupName",
      "campaignName",
      "sales14d",
      "campaignId",
      "adGroupId",
      "keywordId",
      "keywordType",
      "keyword"
    ],
    "reportTypeId": "spPurchasedProduct",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
