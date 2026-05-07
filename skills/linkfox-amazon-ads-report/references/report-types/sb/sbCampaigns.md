---
reportTypeId: sbCampaigns
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/campaign
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign]
format: [GZIP_JSON]
filters:
  - name: campaignStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [campaign]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Campaigns

Campaign reports contain performance data broken down at the campaign level. Campaign reports include all campaigns of the requested sponsored ad type that have performance activity for the requested days. For example, a Sponsored Products campaign report returns performance data for all Sponsored Products campaigns that received impressions on the chosen dates. Campaign reports can also be grouped by ad group and placement for more granular data.

> **Note**
> You can only use a filter that is supported by all groupBy values included in a report configuration. For campaign reports, this means that filters are only supported when you include a single groupBy value.

> **Note**
> This report currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled=False won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbCampaigns |
| Maximum date range | 31 days |
| Data retention | 60 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | campaign |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
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
| brandStorePageView |
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
| topOfSearchImpressionShare |
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
| viewClickThroughRate |

## Group by campaign

**Additional metrics**: campaignBudgetAmount, campaignBudgetCurrencyCode, campaignBudgetType, longTermSales, longTermROAS, topOfSearchImpressionShare

**Filters**:
- campaignStatus (values: ENABLED, PAUSED, ARCHIVED)

## Sample calls

### Campaign summary report grouped by campaign

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxx' \
--data '{
    "name": "SB campaigns report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_BRANDS",
        "groupBy": [
            "campaign"
        ],
        "columns": [
            "impressions",
            "clicks",
            "cost",
            "campaignId",
            "startDate",
            "endDate"
        ],
        "reportTypeId": "sbCampaigns",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
