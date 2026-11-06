---
reportTypeId: sbPurchasedProduct
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/purchased-product
timeUnit: [SUMMARY, DAILY]
groupBy: [purchasedAsin]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 731
  dataRetentionDays: 731
---

# SB 购买商品

SB 购买商品报告提供因广告活动而被购买商品的效果数据。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbPurchasedProduct |
| 最大日期跨度 | 731 天 |
| 数据保留期 | 731 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | purchasedAsin |
| format | GZIP_JSON |

## 基础指标

| 字段 |
|------|
| campaignId |
| adGroupId |
| date |
| startDate |
| endDate |
| campaignBudgetCurrencyCode |
| campaignName |
| campaignPriceTypeCode |
| adGroupName |
| attributionType |
| purchasedAsin |
| ordersClicks14d |
| productName |
| productCategory |
| sales14d |
| salesClicks14d |
| orders14d |
| unitsSold14d |
| newToBrandSales14d |
| newToBrandPurchases14d |
| newToBrandUnitsSold14d |
| newToBrandSalesPercentage14d |
| newToBrandPurchasesPercentage14d |
| newToBrandUnitsSoldPercentage14d |
| unitsSoldClicks14d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |

## 分组：purchasedAsin

无附加指标。

**筛选**： 无

## 配置示例

```json
{
  "name": "SB purchased product report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "purchasedAsin"
    ],
    "columns": [
      "purchasedAsin",
      "attributionType",
      "adGroupName",
      "campaignName",
      "sales14d",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sbPurchasedProduct",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```
