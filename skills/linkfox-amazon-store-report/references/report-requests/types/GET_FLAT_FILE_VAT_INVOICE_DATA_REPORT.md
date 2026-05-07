# `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT`

> **分类**：8. Invoice Reports  
> **说明**：VAT invoice data (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Invoice Data Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#flat-file-vat-invoice-data-report-vidr)（章节：**Flat File VAT Invoice Data Report (VIDR)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Availability**：Sellers who have enrolled in Amazon's VAT Calculation Service and have opted to upload their own invoices. This report is for both Fulfillment by Amazon and seller-fulfilled orders.
- **Report output type**：Tab-delimited flat file
- **Default**："pendingInvoices" : "true"
- **要点**：Provides all the information required to generate a VAT invoice for each shipment, return, or refund for a seller's order. A shipment is included in this report immediately after it is dispatched. Amazon recommends scheduling this report at least twice a day. This report accepts the following reportOptions values: For information on how to use this report, refer to [VAT Calculation Service](https://developer-docs.amazon.com/sp-api/docs/vat-calculation-service-guide).
- **reportOptions（摘录）**：
  - pendingInvoices – A Boolean value. When true, the report contains only shipments for which invoices and credit notes are pending. This report does not contain shipments for which invoices have already been uploaded successfully. Includes shipments for orders that were placed within the previous 90 days. When false, or if pendingInvoices is not included in reportOptions, the content of the report depends on the value of all. Example: "reportOptions": {"ReportOption=pendingInvoices": "true"}
  - all – A Boolean value. When true, the report contains shipments for orders that were placed within the date range that you specify. Includes shipments of all possible invoice statuses. You must specify the startDate and endDate parameters of the [createReport](https://developer-docs.amazon.com/sp-api/reference/createreport) operation. The dataStartTime and dataEndTime values must correspond to valid first and last days in the specified reportPeriod. For example, dataStartTime must be a Sunday and dataEndTime must be a Saturday when reportPeriod=WEEK. The maximum allowed date range is 30 days. When false, or if all is not included in reportOptions, the content of the report depends on the value of pendingInvoices. Example: "reportOptions": {"ReportOption=All": "true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#flat-file-vat-invoice-data-report-vidr>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT",
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
