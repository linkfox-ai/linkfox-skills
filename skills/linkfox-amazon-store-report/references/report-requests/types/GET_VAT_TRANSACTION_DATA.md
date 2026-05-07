# `GET_VAT_TRANSACTION_DATA`

> **分类**：15. Tax Reports  
> **说明**：VAT transaction data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-transactions-report)（章节：**Amazon VAT Transactions Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Requested/scheduled**：This report can only be requested and is available from the third of each month. If you request the report before the third of the month, then Amazon returns a status of FATAL.
- **Report output type**：Tab-delimited flat file
- **Store availability**：Germany, Spain, Italy, France, and UK.
- **要点**：📘NoteThis reports ignores the marketplaceId parameter and will return data for all available stores. Provides detailed information for sales, returns, refunds, cross border inbound, and cross border fulfillment center transfers.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-transactions-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_VAT_TRANSACTION_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_VAT_TRANSACTION_DATA",
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
