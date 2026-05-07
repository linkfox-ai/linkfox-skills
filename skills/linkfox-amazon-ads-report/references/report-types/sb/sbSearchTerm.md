---
reportTypeId: sbSearchTerm
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/search-term
timeUnit: [SUMMARY, DAILY]
groupBy: [searchTerm]
format: [GZIP_JSON]
filters:
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED]
    applicableWhenGroupBy: [searchTerm]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 60
---

# SB Search Term

Search term reports contain search term performance metrics broken down by targeting expressions and keywords. Note that search term reports only include impressions that resulted in at least one ad click. Use the keywordType filter to include either targeting expressions or keywords in your report.

> **Note**
> If a placement does not have a search keyword associated with it on a product detail page, the search term in the report will be an asterisk `*`.

> **Note**
> This report is currently available in preview. During the preview period, data related to Sponsored Brands campaigns with flag isMultiAdGroupsEnabled set to FALSE won't be available. Once version 3 reporting supports all Sponsored Brands campaigns, we will announce general availability in the release notes.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbSearchTerm |
| Maximum date range | 31 days |
| Data retention | 60 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | searchTerm |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| adGroupId |
| adGroupName |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
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
| endDate |
| impressions |
| keywordBid |
| keywordId |
| keywordText |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| matchType |
| purchases |
| purchasesClicks |
| sales |
| salesClicks |
| searchTerm |
| startDate |
| unitsSold |
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

## Group by searchTerm

**Additional metrics**: adKeywordStatus

**Filters**:
- keywordType (values: BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED)

## Sample call

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxx' \
--data '{
    "name": "SP search terms report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_BRANDS",
        "groupBy": [
            "searchTerm"
        ],
        "columns": [
            "impressions",
            "clicks",
            "cost",
            "campaignId",
            "adGroupId",
            "startDate",
            "endDate",
            "matchType",
            "keywordId",
            "searchTerm"
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
        "reportTypeId": "sbSearchTerm",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
