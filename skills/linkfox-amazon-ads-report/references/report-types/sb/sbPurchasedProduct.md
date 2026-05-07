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

## Sample call

```bash
curl --location --request POST 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxx' \
--data-raw '{
    "name":"SB purchased product report 7/5-7/10",
    "startDate":"2022-07-05",
    "endDate":"2022-07-10",
    "configuration":{
        "adProduct":"SPONSORED_BRANDS",
        "groupBy":["purchasedAsin"],
        "columns":["purchasedAsin","attributionType","adGroupName","campaignName","sales14d","startDate","endDate"],
        "reportTypeId":"sbPurchasedProduct",
        "timeUnit":"SUMMARY",
        "format":"GZIP_JSON"
    }
}'
```
