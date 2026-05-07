---
reportTypeId: spTargeting
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/targeting
timeUnit: [SUMMARY, DAILY]
groupBy: [targeting]
format: [GZIP_JSON]
filters:
  - name: adKeywordStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [targeting]
  - name: keywordType
    values: [BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED]
    applicableWhenGroupBy: [targeting]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP Targeting

Targeting reports contain performance metrics broken down by both targeting expressions and keywords.

> **Note**
> Targeting reports are not supported for Sponsored TV non-endemic advertisers.

## Requesting keywords vs. targets

To see only targeting expressions, set the keywordType filter to TARGETING_EXPRESSION and TARGETING_EXPRESSION_PREDEFINED. To see only keywords, set the keywordType filter to BROAD, PHRASE, and EXACT.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | spTargeting |
| Maximum date range | 31 days |
| Data retention | 95 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | targeting |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| impressions |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| clicks |
| costPerClick |
| clickThroughRate |
| cost |
| purchases1d |
| purchases7d |
| purchases14d |
| purchases30d |
| purchasesSameSku1d |
| purchasesSameSku7d |
| purchasesSameSku14d |
| purchasesSameSku30d |
| unitsSoldClicks1d |
| unitsSoldClicks7d |
| unitsSoldClicks14d |
| unitsSoldClicks30d |
| sales1d |
| sales7d |
| sales14d |
| sales30d |
| attributedSalesSameSku1d |
| attributedSalesSameSku7d |
| attributedSalesSameSku14d |
| attributedSalesSameSku30d |
| unitsSoldSameSku1d |
| unitsSoldSameSku7d |
| unitsSoldSameSku14d |
| unitsSoldSameSku30d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| salesOtherSku7d |
| unitsSoldOtherSku7d |
| acosClicks7d |
| acosClicks14d |
| roasClicks7d |
| roasClicks14d |
| keywordId |
| keyword |
| campaignBudgetCurrencyCode |
| date |
| startDate |
| endDate |
| portfolioId |
| campaignName |
| campaignId |
| campaignBudgetType |
| campaignBudgetAmount |
| campaignStatus |
| keywordBid |
| adGroupName |
| adGroupId |
| keywordType |
| matchType |
| targeting |
| topOfSearchImpressionShare |

## Group by targeting

**Additional metrics**: adKeywordStatus

**Filters**:
- adKeywordStatus (values: ENABLED, PAUSED, ARCHIVED)
- keywordType (values: BROAD, PHRASE, EXACT, TARGETING_EXPRESSION, TARGETING_EXPRESSION_PREDEFINED)

## Sample calls

### Targeting expressions only

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxx' \
--data '{
    "name": "SP targeting report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_PRODUCTS",
        "groupBy": [
            "targeting"
        ],
        "columns": [
            "adGroupId",
            "campaignId",
            "targeting",
            "keywordId",
            "matchType",
            "impressions",
            "clicks",
            "cost",
            "purchases1d",
            "purchases7d",
            "purchases14d",
            "purchases30d",
            "startDate",
            "endDate"
        ],
        "filters": [
            {
                "field": "keywordType",
                "values": [
                    "TARGETING_EXPRESSION",
                    "TARGETING_EXPRESSION_PREDEFINED"
                ]
            }
        ],
        "reportTypeId": "spTargeting",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```

### Keywords only

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxx' \
--data '{
    "name": "SP keywords report 9/5-9/10",
    "startDate": "2023-09-05",
    "endDate": "2023-09-10",
    "configuration": {
        "adProduct": "SPONSORED_PRODUCTS",
        "groupBy": [
            "targeting"
        ],
        "columns": [
            "adGroupId",
            "campaignId",
            "keywordId",
            "matchType",
            "keyword",
            "impressions",
            "clicks",
            "cost",
            "purchases1d",
            "purchases7d",
            "purchases14d",
            "purchases30d",
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
        "reportTypeId": "spTargeting",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}'
```
