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

# SD 流量总量与无效流量

流量总量与无效流量报告帮助 SD 广告主核查活动流量性质，覆盖指定类型全部活动，按活动提供请求日期内的总量和无效流量指标。

> **说明**
> SP / SB / SD 的流量总量与无效流量报告支持相同的列与配置。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sdGrossAndInvalids |
| 最大日期跨度 | 365 天 |
| 数据保留期 | 365 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaign |
| format | GZIP_JSON / CSV |

## 基础指标

| 字段 |
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

## 分组：campaign

无附加指标。

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| campaignStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 配置示例

```json
{
  "name": "SD Gross and Invalid Traffic",
  "startDate": "2025-03-05",
  "endDate": "2025-03-10",
  "configuration": {
    "adProduct": "SPONSORED_DISPLAY",
    "groupBy": [
      "campaign"
    ],
    "columns": [
      "campaignName",
      "grossImpressions",
      "grossClickThroughs",
      "invalidClickThroughs",
      "invalidClickThroughRate",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "sdGrossAndInvalids",
    "timeUnit": "SUMMARY",
    "format": "CSV"
  }
}
```
