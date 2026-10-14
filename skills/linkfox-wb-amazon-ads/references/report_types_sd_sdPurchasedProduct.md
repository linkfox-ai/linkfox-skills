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

# SD Purchased Product

Sponsored Display purchased product reports contain performance data for products that were purchased as part of brand-halo activity associated with your campaigns (purchased ASINs that differ from the promoted ASIN).

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sdPurchasedProduct |
| Maximum date range | 31 days |
| Data retention | 65 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | asin |
| format | GZIP_JSON |

## Base metrics

| Field |
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

## Group by asin

**Additional metrics**: N/A

**Filters**: N/A
