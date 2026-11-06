# `GET_XML_VAT_INVOICE_DATA_REPORT`

> **分类**：8. 发票报告  
> **说明**：VAT 发票数据（XML）  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Invoice Data Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#xml-vat-invoice-data-report-vidr)（章节：**XML VAT Invoice Data Report (VIDR)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **角色** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **角色**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **可用范围**：已参加 Amazon VAT Calculation Service 且选择自行上传发票的卖家；覆盖 FBA 与卖家自配送订单。
- **输出格式**：XML
- **默认值**："pendingInvoices" : "true".
- **要点**：包含为卖家订单的每次发货、退货和退款生成 VAT 发票所需全部信息。货件发出后即纳入报告；Amazon 建议每天至少计划生成两次。接受下列 reportOptions，使用说明见 [VAT Calculation Service](https://developer-docs.amazon.com/sp-api/docs/vat-calculation-service-guide)。

#### reportOptions 筛选含义与构参

以下按官方描述保留筛选含义。官方同页的含义名和示例请求键并不一致，不能据此确认两种写法可互换；显式筛选时沿用已确认可用的 `reportOptions`，不自动改名、同时发送多种写法或切换写法重试。未指定筛选时使用官方所述的待开票默认行为。

[Reports API 官方模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/reports-api-model/reports_2021-06-30.json)将 `reportOptions` 定义为字符串值映射，布尔含义使用字符串 `"true"` / `"false"`；脚本原样透传，不自动转换。日期请求字段为 `dataStartTime` / `dataEndTime`，不构造 `startDate` / `endDate`。

| 筛选含义（不作为已确认请求键） | 类型 | 说明 |
|---|---|---|
| pendingInvoices | string（布尔含义） | 为 true 时仅含待上传发票及贷项通知单的货件，不含发票已成功上传的货件；覆盖过去 90 天下单的订单。为 false 或未提供时，内容取决于 all。官方类型页示例使用 `"reportOptions":{"pendingInvoices":"true"}`，但发票操作指南采用带 `ReportOption=` 的写法，不能推定可互换。 |
| all | string（布尔含义） | 为 true 时包含指定日期范围内下单、所有发票状态的货件；提供 dataStartTime 和 dataEndTime，范围最多 30 天。为 false 或未提供时，内容取决于 pendingInvoices。官方示例使用 `"reportOptions": {"ReportOption=All": "true"}`，键名确认限制同上。 |

官方类型页另有 `reportPeriod` 的首末日描述，例如 `WEEK` 为周日至周六，但未明确列出本报告的该选项定义；不能仅据此新增参数或给全部 VAT 请求强加周边界条件。需要该筛选时先核实所用请求约定。

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#xml-vat-invoice-data-report-vidr>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

日期范围写入以下字段；筛选范围仍由 `reportOptions` 决定，仅增加日期不会切换为 `all` 模式：

```json
{
  "reportType": "GET_XML_VAT_INVOICE_DATA_REPORT",
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
