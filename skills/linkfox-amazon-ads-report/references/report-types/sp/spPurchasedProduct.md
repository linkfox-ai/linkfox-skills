---
reportTypeId: spPurchasedProduct
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/purchased-product
timeUnit: [SUMMARY, DAILY]
groupBy: [asin]
format: [GZIP_JSON]
filters: []
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP Purchased Product

Sponsored Products purchased product reports contain performance data for products that were purchased, but were not advertised as part of a campaign. The purchased product report contains both targeting expressions and keyword IDs. After you have received your report, you can filter on keywordType to distinguish between targeting expressions and keywords.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | spPurchasedProduct |
| Maximum date range | 31 days |
| Data retention | 95 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | asin |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| date |
| startDate |
| endDate |
| addToList |
| addToListFromClicks |
| qualifiedBorrows |
| qualifiedBorrowsFromClicks |
| royaltyQualifiedBorrows |
| royaltyQualifiedBorrowsFromClicks |
| portfolioId |
| campaignName |
| campaignId |
| adGroupName |
| adGroupId |
| keywordId |
| keyword |
| keywordType |
| advertisedAsin |
| purchasedAsin |
| advertisedSku |
| campaignBudgetCurrencyCode |
| matchType |
| unitsSoldClicks1d |
| unitsSoldClicks7d |
| unitsSoldClicks14d |
| unitsSoldClicks30d |
| sales1d |
| sales7d |
| sales14d |
| sales30d |
| purchases1d |
| purchases7d |
| purchases14d |
| purchases30d |
| unitsSoldOtherSku1d |
| unitsSoldOtherSku7d |
| unitsSoldOtherSku14d |
| unitsSoldOtherSku30d |
| salesOtherSku1d |
| salesOtherSku7d |
| salesOtherSku14d |
| salesOtherSku30d |
| purchasesOtherSku1d |
| purchasesOtherSku7d |
| purchasesOtherSku14d |
| purchasesOtherSku30d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |

## Group by asin

**Additional metrics**: N/A

**Filters**: N/A

## Sample call

```bash
curl --location --request POST 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxx' \
--data-raw '{
    "name":"SP purchased product report 7/5-7/10",
    "startDate":"2022-07-05",
    "endDate":"2022-07-10",
    "configuration":{
        "adProduct":"SPONSORED_PRODUCTS",
        "groupBy":["asin"],
        "columns":["purchasedAsin","advertisedAsin","adGroupName","campaignName","sales14d","campaignId","adGroupId","keywordId","keywordType","keyword"],
        "reportTypeId":"spPurchasedProduct",
        "timeUnit":"SUMMARY",
        "format":"GZIP_JSON"
    }
}'
```
