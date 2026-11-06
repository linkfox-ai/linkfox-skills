# `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2`

> **分类**：14. 结算与支付报告  
> **说明**：增强结算报告  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Settlement Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#flat-file-v2-settlement-report)（章节：**Flat File V2 Settlement Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **角色**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **可用范围**：Seller Central 卖家
- **输出格式**：制表符分隔的平面文件
- **要点**：结算报告，替代 Flat File Settlement Report 和 XML Settlement Report。价格列合并为三个通用列：amount-type 与 amount-description 描述收费类型并关联同类费用，所有金额统一放在 amount 列，即使新增费用或交易类型也无需扫描其他列找金额。金额按本地格式展示，例如 EU 用 95,00 而不是 95.00；仅限 Seller Central 卖家。

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#flat-file-v2-settlement-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2",
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
