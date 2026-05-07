---
reportTypeId: sbAdGroup
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/ad-group
timeUnit: [SUMMARY, DAILY]
groupBy: [adGroup]
format: [GZIP_JSON]
filters:
  - name: adStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [adGroup]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Ad Group

Ad group reports contain performance data broken down at the ad group level. Ad group reports include all campaigns of the requested sponsored ad type that have performance activity for the requested days. For example, a Sponsored Brands ad group report returns performance data for all Sponsored Brands ad groups that received impressions on the chosen dates.

> **Note**
> For Sponsored Products, there is not a separate ad group report. You can get ad group-level data using the ad group groupBy in a campaign report.

> **Note**
> This report currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled=False won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbAdGroup |
| Maximum date range | 31 days |
| Data retention | 60 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | adGroup |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| adGroupId |
| adGroupName |
| adStatus |
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

## Group by adGroup

**Additional metrics**: N/A

**Filters**:
- adStatus (values: ENABLED, PAUSED, ARCHIVED)

## Group by campaign

**Additional metrics**: N/A

## Sample call

### Ad group summary report grouped by ad group

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxxx' \
--data '{
    "name": "SB ad group report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_BRANDS",
        "groupBy": [
            "adGroup"
        ],
        "columns": [
            "impressions",
            "clicks",
            "cost",
            "campaignId",
            "adGroupId",
            "startDate",
            "endDate"
        ],
        "reportTypeId": "sbAdGroup",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
