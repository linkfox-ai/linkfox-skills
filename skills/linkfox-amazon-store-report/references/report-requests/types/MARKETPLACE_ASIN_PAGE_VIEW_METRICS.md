# `MARKETPLACE_ASIN_PAGE_VIEW_METRICS`

> **分类**：12. 监管合规报告  
> **说明**：ASIN 页面浏览指标  
> **可用范围**：仅卖家

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：[`marketplaceAsinPageViewMetrics.md`](../marketplaceAsinPageViewMetrics.md)
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[监管合规报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#marketplace-asin-page-view-metrics)（章节：**Marketplace ASIN Page View Metrics**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **角色**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights)
- **可用范围**：卖家
- **站点范围**：DE, FR, IT, ES, NL, PL, SE, BE (EU-8), UK, and IE.
- **按需/计划**：本报告可按需请求或计划生成。

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#marketplace-asin-page-view-metrics>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "MARKETPLACE_ASIN_PAGE_VIEW_METRICS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

`scripts/get_report.py`、`references/api.md`。

## 另见

- `references/report-types.md`
