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

# SB Purchased Product

Sponsored Brands purchased product reports contain performance data for products that were purchased as a result of your campaign.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbPurchasedProduct |
| Maximum date range | 731 days |
| Data retention | 731 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | purchasedAsin |
| format | GZIP_JSON |

## Base metrics

| Field |
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

## Group by purchasedAsin

**Additional metrics**: N/A

**Filters**: N/A
