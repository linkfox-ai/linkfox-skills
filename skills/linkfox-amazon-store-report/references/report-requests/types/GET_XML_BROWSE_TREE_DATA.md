# `GET_XML_BROWSE_TREE_DATA`

> **分类**：4. 浏览树报告  
> **说明**：浏览树层级（XML 格式）  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [浏览树报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree#browse-tree-report)（章节：**Browse Tree Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **角色** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **角色**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **可用范围**：卖家
- **按需/计划**：本报告可按需请求或计划生成。
- **输出格式**：XML
- **Schema**：[BrowseTreeReport.xsd](https://images-na.ssl-images-amazon.com/images/G/01/mwsportal/doc/en_US/Reports/XSDs/BrowseTreeReport.xsd)
- **要点**：提供任意 Amazon 零售站点的浏览树层级和节点细化信息，接受下列 reportOptions。卖家必须已注册 MarketplaceId 指定站点，且请求发到对应区域端点，否则报错。RootNodesOnly 与 BrowseNodeId 同时存在时前者优先。Amazon 建议请求浏览树报告时不传 createReport 的 MarketplaceIds；如与 reportOptions 的 MarketplaceId 冲突，后者优先。

#### reportOptions 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| MarketplaceId | string | 指定浏览树所属站点；reportOptions 未提供时使用卖家默认站点。 |
| RootNodesOnly | string | 必须为 true 或 false。true 仅返回 MarketplaceId 指定站点（未指定时默认站点）的根节点；false 或未提供时由 BrowseNodeId 决定报告内容。 |
| BrowseNodeId | string | 指定浏览树顶层节点；未提供且 RootNodesOnly 为 false 或未提供时，返回 MarketplaceId 指定站点（未指定时默认站点）的全部层级。无效 BrowseNodeId 返回空报告。 |

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
