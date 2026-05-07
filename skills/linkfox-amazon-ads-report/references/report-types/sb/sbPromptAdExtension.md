---
reportTypeId: sbPromptAdExtension
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/prompt-ad-extension
timeUnit: [SUMMARY, DAILY]
groupBy: [promptAdExtension]
format: [GZIP_JSON, XLSX]
filters:
  - name: marketplaceId
    values: [US]
    applicableWhenGroupBy: [promptAdExtension]
dateRange:
  maxSpanDays: 90
  dataRetentionDays: 95
---

# SB Prompt Ad Extension

Prompt Ad Extension reports contain performance data for Sponsored Products and Sponsored Brands ads that include metrics for AI-powered prompt ads. Prompts are designed to help shoppers discover products through conversational experiences on Amazon by surfacing relevant product information through intelligent suggestions and guiding questions.

## About Prompts

Prompts are a new ad format that integrates into your existing Sponsored Products and Sponsored Brands campaigns with zero additional setup required. They enhance product discovery at crucial shopper decision points by:

- Showcasing your product expertise at scale during critical shopper decision moments
- Engaging high-intent shoppers with relevant product information
- Anticipating and answering shopper questions about your products

Prompts with clicks will show in your existing Sponsored Products or Sponsored Brands reporting, and you can pause individual prompts through the Amazon Ads console.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbPromptAdExtension |
| Maximum date range | 90 days |
| Data retention | 95 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | promptAdExtension |
| format | GZIP_JSON or XLSX |

## Base metrics

| Field |
|------|
| date |
| startDate |
| endDate |
| campaignId |
| campaignName |
| adGroupId |
| adGroupName |
| marketplaceId |
| adId |
| adName |
| creativeExtensionId |
| creativeExtensionType |
| portfolioName |
| campaignBudgetCurrencyCode |
| promptText |
| impressions |
| clicks |
| clickThroughRate |
| costPerClick |
| cost |
| spend |
| viewableImpressions |
| acosClicks7d |
| acosClicks14d |
| roasClicks7d |
| roasClicks14d |
| purchases1d |
| purchases7d |
| purchases14d |
| purchases30d |
| purchasesSameSku1d |
| purchasesSameSku7d |
| purchasesSameSku14d |
| purchasesSameSku30d |
| purchasesOtherSku1d |
| purchasesOtherSku7d |
| purchasesOtherSku14d |
| purchasesOtherSku30d |
| unitsSoldClicks1d |
| unitsSoldClicks7d |
| unitsSoldClicks14d |
| unitsSoldClicks30d |
| unitsSoldSameSku1d |
| unitsSoldSameSku7d |
| unitsSoldSameSku14d |
| unitsSoldSameSku30d |
| unitsSoldOtherSku1d |
| unitsSoldOtherSku7d |
| unitsSoldOtherSku14d |
| unitsSoldOtherSku30d |
| sales1d |
| sales7d |
| sales14d |
| sales30d |
| attributedSalesSameSku1d |
| attributedSalesSameSku7d |
| attributedSalesSameSku14d |
| attributedSalesSameSku30d |
| salesOtherSku1d |
| salesOtherSku7d |
| salesOtherSku14d |
| salesOtherSku30d |
| purchaseClickRate7d |
| purchaseClickRate14d |
| newToBrandPurchases |
| newToBrandPurchasesPercentage |
| newToBrandUnitsSold |
| newToBrandUnitsSoldPercentage |
| newToBrandSales |
| newToBrandSalesPercentage |

## Group by promptAdExtension

**Additional metrics**: N/A

**Filters**:
- marketplaceId (values: US)

## Sample call

```bash
curl --location 'https://advertising-api.amazon.com/reporting/reports' \
--header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
--header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxxx' \
--header 'Amazon-Advertising-API-Scope: xxxxxxx' \
--header 'Authorization: Bearer Atza|xxxxxxxxxxx' \
--data '{
    "name":"SB prompt ad extension report 4/13-4/16",
    "startDate":"2026-04-13",
    "endDate":"2026-04-16",
    "configuration":{
        "adProduct":"SPONSORED_BRANDS",
        "groupBy":["promptAdExtension"],
        "columns":["date","campaignId","campaignName","adGroupId","adGroupName","adId","adName","creativeExtensionId","promptText","impressions","clicks","cost","purchases7d","sales7d","newToBrandPurchases","newToBrandSales"],
        "reportTypeId":"sbPromptAdExtension",
        "timeUnit":"DAILY",
        "format":"GZIP_JSON"
    }
}'
```
