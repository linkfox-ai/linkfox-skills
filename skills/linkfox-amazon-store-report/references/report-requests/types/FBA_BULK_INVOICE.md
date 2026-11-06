# `FBA_BULK_INVOICE`

> **分类**：12. 监管合规报告  
> **说明**：FBA 批量发票  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [监管合规报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#fba-bulk-invoice)（章节：**FBA Bulk Invoice**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **角色** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **角色**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **可用范围**：卖家
- **按需/计划**：本报告仅可按需请求。
- **要点**：提供指定日期范围内卖家的发票，包含卖家履约的客户订单。单个 reportOptions 值最多 200 字符。TRANSPORTER_COPY 和 CUSTOMER_COPY 这两种 invoiceTypes 仅适用于 transactionType=MCF_SHIPMENT；其他 transactionTypes 仅允许 SELLER_COPY，MCF_SHIPMENT 也允许 SELLER_COPY。订单筛选与货件筛选互斥，只能提供其中一类，同时提供会失败。两者均未设置或未提供 reportOptions 时，返回日期范围内全部相关发票（SHIPMENT 和 MCF_SHIPMENT）。

货件筛选按官方选项清单列为 `shipmentIds`；官方互斥说明另写作 `shipmentId`，存在拼写差异。这里保留选项清单及二选一条件，不把两种拼写当成可互换参数；脚本原样透传 `reportOptions`，不自动补入或改写另一个键。该解释依据官方清单，不代表已通过实际请求验证差异。

#### reportOptions 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| orderIds | string | 单个字符串，以逗号分隔订单 ID 筛选，例如 406-8193317-8698708, 408-0804227-3381000。 |
| shipmentIds | string | 单个字符串，以逗号分隔货件 ID 筛选，例如 64119752218302, 264552989124123。 |
| transactionTypes | string | 单个字符串，以逗号分隔交易类型筛选。可选 SHIPMENT、REFUND、CANCEL、EINVOICE_CANCEL、FC_TRANSFER、FC_TRANSFER_CANCEL、FC_REMOVAL、FC_REMOVAL_CANCEL、MCF_SHIPMENT、MCF_CANCEL、MCF_REFUND。 |
| invoiceTypes | string | 单个字符串，以逗号分隔发票类型筛选。可选 CUSTOMER_COPY、SELLER_COPY、TRANSPORTER_COPY。 |

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#fba-bulk-invoice>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "FBA_BULK_INVOICE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "FBA_BULK_INVOICE",
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
