---
reportTypeId: sdGrossAndInvalids
adProduct: SPONSORED_DISPLAY
officialDocUrl: https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/gross-and-invalids
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

# SD Gross and Invalid Traffic

Gross and invalid traffic reports provide Sponsored Display advertisers transparency into the nature of traffic on their campaigns. The report includes all campaigns of the requested ad type and provides transparency on gross and invalid traffic metrics at the campaign level for the requested days.

> **Note**
> Sponsored Products, Sponsored Brands, and Sponsored Display all support the same columns and configurations for the gross and invalid traffic report.

## Configuration

| Configuration | Value |
|---|---|
| reportTypeId | sdGrossAndInvalids |
| Maximum date range | 365 days |
| Data retention | 365 days |
| timeUnit | SUMMARY or DAILY |
| groupBy | campaign |
| format | GZIP_JSON or CSV |

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
