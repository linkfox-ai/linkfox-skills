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

# SP 广告活动

活动报告按活动展示效果，覆盖指定广告类型在请求日期内有投放活动的全部活动。例如，SP 活动报告返回所选日期收到展示的全部 SP 活动数据。活动报告也可按广告组和广告位细分，具体可用分组以本文件配置为准。

> **说明**
> 筛选器必须由请求中的全部 `groupBy` 值共同支持。对于活动报告，只有包含单个 `groupBy` 值时才支持筛选。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | spCampaigns |
| 最大日期跨度 | 31 天 |
| 数据保留期 | 95 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | campaign, adGroup, / campaignPlacement |
| format | GZIP_JSON |

## 基础指标

| 字段 |
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

## 分组：campaign

附加指标：

| 字段 |
|---|
| campaignName |
| campaignId |
| campaignStatus |
| campaignBudgetAmount |
| campaignBudgetType |
| campaignRuleBasedBudgetAmount |
| campaignApplicableBudgetRuleId |
| campaignApplicableBudgetRuleName |
| campaignBudgetCurrencyCode |
| topOfSearchImpressionShare |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| campaignStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 分组：adGroup

附加指标：

| 字段 |
|---|
| adGroupName |
| adGroupId |
| adStatus |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| adStatus | array[string] | ENABLED, PAUSED, ARCHIVED |

## 分组：campaignPlacement

附加指标：

| 字段 |
|---|
| placementClassification |
| campaignName |
| campaignId |
| campaignStatus |
| campaignBudgetAmount |
| campaignBudgetType |
| campaignRuleBasedBudgetAmount |
| campaignApplicableBudgetRuleId |
| campaignApplicableBudgetRuleName |
| campaignBudgetCurrencyCode |
| topOfSearchImpressionShare |

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| campaignSite | array[string] | AmazonBusiness |

> **说明**
> Amazon Business 效果数据仅从 2024-09-05 起可用。
>
> SP 的 Amazon Business 竞价调整与报告属于 Bulksheets 的计划支持内容，实际可用性需单独确认。
>
> Amazon Business 筛选场景仅支持 `campaignPlacement` 分组。

## 配置示例

### campaign + adGroup 分组

```json
{
  "name": "SP campaigns report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "campaign",
      "adGroup"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "adGroupId",
      "date"
    ],
    "reportTypeId": "spCampaigns",
    "timeUnit": "DAILY",
    "format": "GZIP_JSON"
  }
}
```

### campaign + campaignPlacement 分组

```json
{
  "name": "SP campaigns report 7/5-7/10",
  "startDate": "2022-07-05",
  "endDate": "2022-07-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "campaign",
      "campaignPlacement"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "placementClassification",
      "startDate",
      "endDate"
    ],
    "reportTypeId": "spCampaigns",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```

### campaignPlacement 分组（campaignSite=AmazonBusiness）

```json
{
  "name": "SP campaigns report 9/07-9/10",
  "startDate": "2024-09-07",
  "endDate": "2024-09-10",
  "configuration": {
    "adProduct": "SPONSORED_PRODUCTS",
    "groupBy": [
      "campaignPlacement"
    ],
    "columns": [
      "impressions",
      "clicks",
      "cost",
      "campaignId",
      "placementClassification",
      "startDate",
      "endDate"
    ],
    "filters": [
      {
        "field": "campaignSite",
        "values": [
          "AmazonBusiness"
        ]
      }
    ],
    "reportTypeId": "spCampaigns",
    "timeUnit": "SUMMARY",
    "format": "GZIP_JSON"
  }
}
```

> **说明**
> 仅按 `campaignPlacement` 分组，与同时按 `campaign` 和 `campaignPlacement` 分组会生成相同报告。
