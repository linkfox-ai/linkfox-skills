# `GET_FLAT_FILE_OPEN_LISTINGS_DATA`

> **分类**：7. Inventory Reports  
> **说明**：Open listings (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_FLAT_FILE_OPEN_LISTINGS_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：Seller Central sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：Contains a summary of the seller's product listings with the price and quantity for each SKU. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - Custom: A Boolean value that indicates whether a custom report is returned. Default: false. Example: "reportOptions":{"custom":"true"}.
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
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
