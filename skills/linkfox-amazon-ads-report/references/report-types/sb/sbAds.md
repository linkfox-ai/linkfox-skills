---
reportTypeId: sbAds
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/ad
timeUnit: [SUMMARY, DAILY]
groupBy: [ads]
format: [GZIP_JSON]
filters:
  - name: adStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [ads]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Ads

Advertised product reports contain performance data for campaigns at the ad level.

> **Note**
> This report is currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled set to FALSE won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbAds |
| Maximum date range | 31 days |
| Data retention | 60 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | ads |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| addToListFromClicks |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrowsFromClicks |
| adGroupId |
| adGroupName |
| adId |
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
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
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
| unitsSold |
| unitsSoldClicks |
| video5SecondViewRate |
| video5SecondViews |
| videoCompleteViews |
| videoFirstQuartileViews |
| videoMidpointViews |
| videoThirdQuartileViews |
| videoUnmutes |
| viewabilityRate |
| viewableImpressions |

## Group by ads

**Additional metrics**: N/A

**Filters**:
- adStatus (values: ENABLED, PAUSED, ARCHIVED)

## Sample call

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxxx' \
--data '{
    "name":"SB advertised product report 9/5-9/10",
    "startDate":"2023-09-05",
    "endDate":"2023-09-10",
    "configuration":{
        "adProduct":"SPONSORED_BRANDS",
        "groupBy":["ads"],
        "columns":["impressions","clicks","cost","campaignId","adId","adGroupId"],
        "reportTypeId":"sbAds",
        "timeUnit":"SUMMARY",
        "format":"GZIP_JSON"
    }
}'
```
