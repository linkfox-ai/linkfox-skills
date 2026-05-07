# `GET_XML_BROWSE_TREE_DATA`

> **分类**：4. Browse Tree Reports  
> **说明**：Browse tree hierarchy (XML format)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Browse Tree Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree#browse-tree-report)（章节：**Browse Tree Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Availability**：Sellers
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：XML
- **Schema**：[BrowseTreeReport.xsd](https://images-na.ssl-images-amazon.com/images/G/01/mwsportal/doc/en_US/Reports/XSDs/BrowseTreeReport.xsd)
- **要点**：Contains browse tree hierarchy information and node refinement information for the Amazon retail website in any marketplace. This report accepts the following reportOptions values: 📘Note:The seller must be registered in any marketplace that you specify using the MarketplaceId value. Also, your request must be sent to an endpoint that corresponds to the MarketplaceId that you specify. Otherwise, the service returns an error. 📘Note:If RootNodesOnly and BrowseNodeId are both included in the reportOptions parameter, RootNodesOnly takes precedence. 📘Note:Amazon recommends that you do not include the MarketplaceIds parameter with calls to the createReport operation that request the Browse Tree Report. If there is ever a conflict between a MarketplaceIds parameter value and the MarketplaceId value of the reportOptions parameter, the MarketplaceId value takes precedence.
- **reportOptions（摘录）**：
  - MarketplaceId – Specifies the marketplace from which you want browse tree information. If MarketplaceId is not included in the reportOptions parameter, the report contains browse tree information from the seller's default marketplace.
  - RootNodesOnly - A string value that must be either true or false. When you set RootNodesOnly to true, the report contains only the root nodes from the marketplace that you specify using MarketplaceId (or from your default marketplace if you do not specify MarketplaceId). When you set RootNodesOnly to false, or if you do not include RootNodesOnly in the ReportOptions parameter, the value of BrowseNodeId determines the content of the report.
  - BrowseNodeId – Specifies the top node of the browse tree hierarchy in the report. If BrowseNodeId is not included in the ReportOptions parameter, and if RootNodesOnly is false or is not included in the ReportOptions parameter, then the report contains the entire browse node hierarchy from the marketplace specified using MarketplaceId (or from the seller's default marketplace, if MarketplaceId is not specified). Note that if you include an invalid BrowseNodeId in your request, the service returns a report that contains no data.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree#browse-tree-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_BROWSE_TREE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_BROWSE_TREE_DATA",
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
