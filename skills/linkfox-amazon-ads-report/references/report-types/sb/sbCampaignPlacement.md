---
reportTypeId: sbCampaignPlacement
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/placement
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Campaign Placement

Placement reports contain performance data broken down by ad placement.

> **Note**
> For Sponsored Products, there is not a separate placement report. You can get placement-level data using the 'campaignPlacement' groupBy in a campaign report.

> **Note**
> This report is currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled set to FALSE won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbCampaignPlacement |
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
| viewClickThroughRate |

## Group by campaignPlacement

**Additional metrics**: placementClassification

## Group by campaign

**Additional metrics**: N/A

## Sample call

### Campaign placement summary report

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxx' \
--data '{
    "name": "SB placement report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_BRANDS",
        "groupBy": [
            "campaignPlacement"
        ],
        "columns": [
            "impressions",
            "clicks",
            "cost",
            "campaignId",
            "placementClassification",
            "startDate",
            "endDate"
        ],
        "reportTypeId": "sbCampaignPlacement",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
