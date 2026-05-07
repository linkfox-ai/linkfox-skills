---
reportTypeId: spAdvertisedProduct
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/advertised-product
timeUnit: [SUMMARY, DAILY]
groupBy: [advertiser]
format: [GZIP_JSON]
filters:
  - name: adCreativeStatus
    values: [ENABLED, PAUSED, ARCHIVED]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP Advertised Product

Advertised product reports contain performance data for products that are advertised as part of your campaigns.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | spAdvertisedProduct |
| Maximum date range | 31 days |
| Data retention | 95 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | advertiser |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| date |
| startDate |
| endDate |
| campaignName |
| campaignId |
| adGroupName |
| adGroupId |
| adId |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| portfolioId |
| impressions |
| clicks |
| costPerClick |
| clickThroughRate |
| cost |
| spend |
| campaignBudgetCurrencyCode |
| campaignBudgetAmount |
| campaignBudgetType |
| campaignStatus |
| advertisedAsin |
| advertisedSku |
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
| salesOtherSku7d |
| unitsSoldSameSku1d |
| unitsSoldSameSku7d |
| unitsSoldSameSku14d |
| unitsSoldSameSku30d |
| unitsSoldOtherSku7d |
| kindleEditionNormalizedPagesRead14d |
| kindleEditionNormalizedPagesRoyalties14d |
| acosClicks7d |
| acosClicks14d |
| roasClicks7d |
| roasClicks14d |

## Group by advertiser

Additional metrics: N/A

## Filters

- adCreativeStatus (values: ENABLED, PAUSED, ARCHIVED)

## Sample call

**Endpoint**: `POST https://advertising-api.amazon.com/reporting/reports`

**Headers**:
```
Content-Type: application/vnd.createasyncreportrequest.v3+json
Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxx
Amazon-Advertising-API-Scope: xxxxxxx
Authorization: Bearer Atza|xxxxxxxxxxxxx
```

**Body**:
```json
{
    "name": "SP advertised product report 7/5-7/10",
    "startDate": "2022-07-05",
    "endDate": "2022-07-10",
    "configuration": {
        "adProduct": "SPONSORED_PRODUCTS",
        "groupBy": ["advertiser"],
        "columns": ["impressions", "clicks", "cost", "campaignId", "advertisedAsin"],
        "reportTypeId": "spAdvertisedProduct",
        "timeUnit": "SUMMARY",
        "format": "GZIP_JSON"
    }
}
```
