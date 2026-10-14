---
reportTypeId: sbGrossAndInvalids
adProduct: SPONSORED_BRANDS
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/gross-and-invalid-traffic
timeUnit: [SUMMARY, DAILY]
groupBy: [campaign]
format: [GZIP_JSON, CSV]
filters:
  - name: campaignStatus
    values: [ENABLED, PAUSED, ARCHIVED]
    applicableWhenGroupBy: [campaign]
dateRange:
  maxSpanDays: 365
  dataRetentionDays: 365
---

# SB Gross and Invalid Traffic

Gross and invalid traffic report provides Sponsored Products, Sponsored Brands and Sponsored Display advertisers transparency into the nature of traffic on their campaigns. This report include all campaigns of the requested ad type and provides transparency on gross and invalid traffic metrics at campaign level for the requested days. For example, a Sponsored Products gross and invalid traffic report returns gross and invalid traffic metrics for all Sponsored Products campaigns that received impressions on the chosen dates.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sbGrossAndInvalids |
| Maximum date range | 365 days |
| Data retention | 365 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | campaign |
| format | GZIP_JSON or CSV |

> Sponsored Products, Sponsored Brands, and Sponosred Display all support the same columns and configurations for the gross and invalid traffic report.

## Base metrics

| Field |
|------|
| campaignName |
| campaignStatus |
| clicks |
| date |
| endDate |
| grossClickThroughs |
| grossImpressions |
| impressions |
| invalidClickThroughRate |
| invalidClickThroughs |
| invalidImpressionRate |
| invalidImpressions |
| startDate |

## Group by campaign

**Additional metrics**: N/A

**Filters**:
- campaignStatus (values: ENABLED, PAUSED, ARCHIVED)
