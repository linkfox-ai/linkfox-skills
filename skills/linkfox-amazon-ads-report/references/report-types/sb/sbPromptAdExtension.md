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

# SB Prompt 广告扩展

Prompt 广告扩展报告提供 SP 与 SB 的 AI 提示广告效果指标。Prompt 通过智能建议和引导问题展示相关商品信息，帮助买家在 Amazon 对话体验中发现商品。

## Prompt 说明

Prompt 可整合到现有 SP / SB 活动，无需额外设置，在买家决策时通过以下方式帮助发现商品：

- 在买家关键决策时展示商品专业信息。
- 用相关商品信息触达高意向买家。
- 预判并回答买家的商品问题。

产生点击的 Prompt 会出现在现有 SP / SB 报告中，可通过 Amazon Ads 控制台暂停单条 Prompt。

## 配置

| 配置项 | 值 |
|---|---|
| reportTypeId | sbPromptAdExtension |
| 最大日期跨度 | 90 天 |
| 数据保留期 | 95 天 |
| timeUnit | SUMMARY / DAILY |
| groupBy | promptAdExtension |
| format | GZIP_JSON / XLSX |

## 基础指标

| 字段 |
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

## 分组：promptAdExtension

无附加指标。

**筛选**：

| 筛选字段 | values 类型 | 可选值 |
|---|---|---|
| marketplaceId | array[string] | US |

## 配置示例

```json
{
  "name": "SB prompt ad extension report 4/13-4/16",
  "startDate": "2026-04-13",
  "endDate": "2026-04-16",
  "configuration": {
    "adProduct": "SPONSORED_BRANDS",
    "groupBy": [
      "promptAdExtension"
    ],
    "columns": [
      "date",
      "campaignId",
      "campaignName",
      "adGroupId",
      "adGroupName",
      "adId",
      "adName",
      "creativeExtensionId",
      "promptText",
      "impressions",
      "clicks",
      "cost",
      "purchases7d",
      "sales7d",
      "newToBrandPurchases",
      "newToBrandSales"
    ],
    "reportTypeId": "sbPromptAdExtension",
    "timeUnit": "DAILY",
    "format": "GZIP_JSON"
  }
}
```
