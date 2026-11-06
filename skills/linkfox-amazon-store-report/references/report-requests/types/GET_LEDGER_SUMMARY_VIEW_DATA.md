# `GET_LEDGER_SUMMARY_VIEW_DATA`

> **分类**：6.2 FBA 库存  
> **说明**：库存分类账汇总  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---summary-view)（章节：**Inventory Ledger Report - Summary View**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **角色**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **按需/计划**：本报告仅可按需请求。
- **输出格式**：制表符分隔的平面文件
- **要点**：库存分类账类似库存银行流水，展示期初库存、收货、客户订单、客户退货、调整、移除和期末余额，实现全流程对账。接受下列 reportOptions。

#### reportOptions 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| aggregateByLocation | string | 按国家汇总使用 Country，按仓库汇总使用 FC。默认 COUNTRY；示例："reportOptions":{"aggregateByLocation":"COUNTRY"}。Country 与默认值及示例中的 COUNTRY 存在大小写差异，请按接口要求核对，不自行统一大小写。 |
| aggregatedByTimePeriod | string | 指定汇总周期，例如 MONTHLY、WEEKLY、DAILY。默认 MONTHLY；示例："reportOptions":{"aggregatedByTimePeriod":"MONTHLY"}。 |
| FNSKU | string | 提供 FNSKU 可查看该 FNSKU 的报告数据。 |
| MSKU | string | 提供 MSKU 可查看映射到该 MSKU 的全部有效 FNSKU 数据。 |
| ASIN | string | 提供 ASIN 可查看映射到该 ASIN 的全部有效 FNSKU 数据。 |

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---summary-view>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_LEDGER_SUMMARY_VIEW_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_LEDGER_SUMMARY_VIEW_DATA",
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
