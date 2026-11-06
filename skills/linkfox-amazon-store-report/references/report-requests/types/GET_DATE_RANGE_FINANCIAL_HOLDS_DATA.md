# `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA`

> **分类**：10. 支付报告  
> **说明**：指定日期范围的财务冻结  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [支付报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-payment#deferred-transaction-report)（章节：**Deferred Transaction Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **可用范围**：Seller Central 卖家
- **输出格式**：逗号分隔的平面文件
- **角色**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **要点**：延迟交易的时点快照，单份可提供最多 10 年数据。必须先在 [Seller Central](https://developer-docs.amazon.com/sp-api/docs/seller-central-urls) 的 Payments Reports Repository 请求 Deferred Transaction Report，才能用 [Reports v2021-06-30](https://developer-docs.amazon.com/sp-api/reference/reports-v2021-06-30) 获取。

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-payment#deferred-transaction-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_DATE_RANGE_FINANCIAL_HOLDS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_DATE_RANGE_FINANCIAL_HOLDS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `scripts/get_report.py`：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`
