# `GST_MTR_B2B`

> **分类**：15. Tax Reports  
> **说明**：GST Monthly Tax Report B2B  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-business)（章节：**GST Merchant Tax Report - Business to Business**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Requested/scheduled**：This report can only be scheduled.
- **Report output type**：Comma-separated flat file
- **Store availability**：IN
- **要点**：Provides detailed information about sales, refunds, and cancellations from Amazon Business invoices issued within a date range that you specify.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-business>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GST_MTR_B2B",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GST_MTR_B2B",
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
