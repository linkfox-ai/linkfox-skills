# `GET_PROMOTION_PERFORMANCE_REPORT`

> **分类**：11. 绩效报告  
> **说明**：促销表现  
> **可用范围**：卖家与 Vendor

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：[`promotionReport.md`](../promotionReport.md)
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[绩效报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#promotions-performance-report)（章节：**Promotions Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **角色**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights), [Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **可用范围**：具备 Selling Partner Insights 角色的卖家，以及具备 Brand Analytics 角色且已参加 Amazon 品牌备案的 Vendor。
- **按需/计划**：本报告仅可按需请求。
- **输出格式**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#promotions-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_PROMOTION_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

`scripts/get_report.py`、`references/api.md`。

## 另见

- `references/report-types.md`
