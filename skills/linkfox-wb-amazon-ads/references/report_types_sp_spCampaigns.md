---
reportTypeId: spCampaigns
adProduct: SPONSORED_PRODUCTS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/campaign
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign, adGroup, campaignPlacement]
format: [GZIP_JSON]
filters:
  - name: campaignStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [campaign]
  - name: adStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [adGroup]
  - name: campaignSite
    values: [AmazonBusiness]
    applicableWhenGroupBy: [campaignPlacement]
dateRange:
  maxSpanDays: 31
  dataRetentionDays: 95
---

# SP Campaigns

Campaign reports contain performance data broken down at the campaign level. Campaign reports include all campaigns of the requested sponsored ad type that have performance activity for the requested days. For example, a Sponsored Products campaign report returns performance data for all Sponsored Products campaigns that received impressions on the chosen dates. Campaign reports can also be grouped by ad group and placement for more granular data.

> **Note**
> You can only use a filter that is supported by all groupBy values included in a report configuration. For campaign reports, this means that filters are only supported when you include a single groupBy value.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | spCampaigns |
| Maximum date range | 31 days |
| Data retention | 95 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | campaign, adGroup, or campaignPlacement |
| format | GZIP_JSON |

## Base metrics

| Field |
|------|
| impressions |
| addToList |
| qualifiedBorrows |
| royaltyQualifiedBorrows |
| clicks |
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
| date |
| startDate |
| endDate |
| campaignBiddingStrategy |
| costPerClick |
| clickThroughRate |
| spend |

## Group by campaign

**Additional metrics**: campaignName, campaignId, campaignStatus, campaignBudgetAmount, campaignBudgetType, campaignRuleBasedBudgetAmount, campaignApplicableBudgetRuleId, campaignApplicableBudgetRuleName, campaignBudgetCurrencyCode, topOfSearchImpressionShare

**Filters**:
- campaignStatus (values: ENABLED, PAUSED, ARCHIVED)

## Group by adGroup

**Additional metrics**: adGroupName, adGroupId, adStatus

**Filters**:
- adStatus (values: ENABLED, PAUSED, ARCHIVED)

## Group by campaignPlacement

**Additional metrics**: placementClassification, campaignName, campaignId, campaignStatus, campaignBudgetAmount, campaignBudgetType, campaignRuleBasedBudgetAmount, campaignApplicableBudgetRuleId, campaignApplicableBudgetRuleName, campaignBudgetCurrencyCode, topOfSearchImpressionShare

**Filters**:
- campaignSite (values: AmazonBusiness)

> **Note**
> Amazon Business performance data is available starting 9/5/2024 onwards only.
>
> The Amazon Business Bid Adjustment and Reporting for Sponsored Products will be coming soon to Bulksheets.
>
> Other groupBy parameters apart from campaignPlacement are not supported.

> **Note**
> Grouping by campaignPlacement will generate the same report as grouping by campaign and campaignPlacement.

