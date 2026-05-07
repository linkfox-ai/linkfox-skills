# `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING`

> **分类**：9. Order Reports  
> **说明**：Order shipping (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-shipping)（章节：**Requested or Scheduled Flat File Order Report (Shipping)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：Contains orders from the previous 60 days. This report can be used to ship Amazon orders. Seller Central sellers can only schedule one GET_ORDER_REPORT_DATA_SHIPPING or GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled. 📘NoteThe format of this report will differ slightly depending on whether it is scheduled or requested. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - ShowSalesChannel: A Boolean value that indicates whether an additional column is added to the report that shows the sales channel. Default: false. Example: "reportOptions":{"ShowSalesChannel":"true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-shipping>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING",
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
