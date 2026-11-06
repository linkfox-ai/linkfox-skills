---
reportTypeId: spGrossAndInvalids
adProduct: SPONSORED_PRODUCTS
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

# SP 流量总量与无效流量

流量总量与无效流量报告用于 SP / SB / SD 广告活动流量核查，按活动提供请求日期内的总量和无效流量指标，覆盖指定类型的全部活动。例如，SP 报告包含所选日期收到展示的全部 SP 活动。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | spGrossAndInvalids |
| 最大日期跨度 | 365 天 |
| 数据保留期 | 365 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaign |
| format | GZIP_JSON / CSV |

> SP / SB / SD 的流量总量与无效流量报告支持相同的列与配置。

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
  "name": "SP Gross and Invalid Traffic",
  "startDate": "2023-09-05",
  "endDate": "2023-09-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
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
    "reportTypeId": "spGrossAndInvalids",
    "timeUnit": "SUMMARY",
    "format": "CSV"
  }
}
```
