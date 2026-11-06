---
reportTypeId: sdPurchasedProduct
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/purchased-product
timeUnit: [SUMMARY, DAILY]
groupBy: [asin]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 65
---

# SD 购买商品

SD 购买商品报告提供活动带来的品牌光环购买效果，即被购买 ASIN 与推广 ASIN 不同的商品。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdPurchasedProduct |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 65 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | asin |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| adGroupId |
| adGroupName |
| asinBrandHalo |
| addToList |
| addToListFromClicks |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrowsFromClicks |
| addToListFromViews |
| qualifiedBorrows |
| qualifiedBorrowsFromViews |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromViews |
| campaignBudgetCurrencyCode |
| campaignId |
| campaignName |
| conversionsBrandHalo |
| conversionsBrandHaloClicks |
| date |
| endDate |
| kindleEditionNormalizedPagesRead |
| kindleEditionNormalizedPagesReadFromClicks |
| kindleEditionNormalizedPagesReadFromViews |
| kindleEditionNormalizedPagesRoyalties |
| kindleEditionNormalizedPagesRoyaltiesFromClicks |
| kindleEditionNormalizedPagesRoyaltiesFromViews |
| promotedAsin |
| promotedSku |
| salesBrandHalo |
| salesBrandHaloClicks |
| startDate |
| unitsSoldBrandHalo |
| unitsSoldBrandHaloClicks |

## 分组：asin

无附加指标。

**筛选**： 无

## 配置示例

```json
{
  "name": "SD purchased product report",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "asin"
    ],
    "columns": [
      "promotedAsin",
      "asinBrandHalo",
      "adGroupName",
      "campaignName",
      "salesBrandHalo",
      "conversionsBrandHalo",
      "campaignId",
      "adGroupId"
    ],
    "reportTypeId": "sdPurchasedProduct",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
