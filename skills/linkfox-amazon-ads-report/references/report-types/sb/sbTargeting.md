---
reportTypeId: sbTargeting
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/targeting
timeUnit: [SUMMARY, DAILY]
groupBy: [targeting]
format: [GZIP_JSON]
filters:
  - name: adKeywordStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [targeting]
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED, THEME]
    applicableWhenGroupBy: [targeting]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Targeting

Targeting reports contain performance metrics broken down by both targeting expressions and keywords.

> **Note**
> Targeting reports are not supported for Sponsored TV non-endemic advertisers.

## Requesting keywords vs. targets

To see only targeting expressions, set the keywordType filter to TARGETING_EXPRESSION and TARGETING_EXPRESSION_PREDEFINED. To see only keywords, set the keywordType filter to BROAD, PHRASE, and EXACT.

> **Note**
> This report currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled=False won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbTargeting |
| Maximum date range | 31 days |
| Data retention | 60 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | targeting |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| addToCart |
| addToCartClicks |
| addToCartRate |
| adGroupId |
| adGroupName |
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
| keywordBid |
| keywordId |
| adKeywordStatus |
| keywordText |
| keywordType |
| matchType |
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
| targetingExpression |
| targetingId |
| targetingText |
| targetingType |
| topOfSearchImpressionShare |
| unitsSold |

## Group by targeting

**Additional metrics**: N/A

**Filters**:
- adKeywordStatus (values: ENABLED, PAUSED, ARCHIVED)
- keywordType (values: BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED, THEME)

## Sample call

### Keywords only

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxx' \
--data '{
    "name": "SB keywords report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_BRANDS",
        "groupBy": [
            "targeting"
        ],
        "columns": [
            "adGroupId",
            "campaignId",
            "keywordId",
            "matchType",
            "keywordText",
            "impressions",
            "clicks",
            "cost",
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
        "reportTypeId": "sbTargeting",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
