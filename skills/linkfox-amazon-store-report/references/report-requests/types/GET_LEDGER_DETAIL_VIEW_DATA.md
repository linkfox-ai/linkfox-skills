# `GET_LEDGER_DETAIL_VIEW_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Inventory ledger detail  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---detailed-view)（章节：**Inventory Ledger Report - Detailed View**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Use the Inventory Ledger Report - Detailed View to analyze your inventory movements to and from Amazon fulfillment centers, including products that are sold, returned, removed/disposed, damaged, lost, and found. You can view all historical movements of your inventory for 18 months in this report. This report accepts the following reportOptions values: You can pass multiple parameters to ReportOptions as shown in the following example: "reportOptions":{"eventType":"Adjustments", "FNSKU" : "X00001", "MSKU" : "Test"}
- **reportOptions（摘录）**：
  - eventType: Filters report data for a particular warehouse event. Default is the empty string, which returns all events. Other possible values are as follows: Adjustments CustomerReturns Receipts Shipments VendorReturns WhseTransfers Examples: "reportOptions":{"eventType":""} "reportOptions":{"eventType":"Adjustments"}
  - FNSKU: Include FNSKU value to view report data for that particular FNSKU.
  - MSKU: Include MSKU value to view report data for all active FNSKU mappings of that MSKU.
  - ASIN: Include ASIN value to view report data for all active FNSKU mappings of that ASIN.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---detailed-view>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_LEDGER_DETAIL_VIEW_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_LEDGER_DETAIL_VIEW_DATA",
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
