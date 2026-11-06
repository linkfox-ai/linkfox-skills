# `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX`

> **分类**：9. 订单报告  
> **说明**：订单税务（平面文件）  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [订单报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-tax)（章节：**Requested or Scheduled Flat File Order Report (Tax)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **角色**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Order Fulfillment Channel**：MFN
- **可用范围**：Seller Central 卖家
- **站点范围**：NA
- **按需/计划**：Requested or scheduled
- **输出格式**：制表符分隔的平面文件
- **要点**：仅面向 NA，包含过去 60 天的订单。Seller Central 卖家同时仅可计划一份 GET_ORDER_REPORT_DATA_TAX 或 GET_FLAT_FILE_ORDER_REPORT_DATA_TAX；新增计划会取消已有计划。按需请求与计划生成的文件格式略有不同；接受下列 reportOptions。

#### reportOptions 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| ShowSalesChannel | boolean / string | 布尔值，控制是否增加销售渠道列。默认 false；示例："reportOptions":{"ShowSalesChannel":"true"}。 |

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-tax>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_TAX",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_TAX",
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
