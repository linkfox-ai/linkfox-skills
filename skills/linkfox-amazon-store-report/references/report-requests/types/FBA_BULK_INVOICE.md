# `FBA_BULK_INVOICE`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：FBA bulk invoice  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#fba-bulk-invoice)（章节：**FBA Bulk Invoice**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **要点**：Provides the invoices for a seller within a given date range. These invoices include customer orders served by the seller. This report type supports the following report options: A single report option value is limited to 200 characters. The TRANSPORTER_COPY and CUSTOMER_COPY invoiceTypes are only available for the MCF_SHIPMENT transactionType. For any other transactionTypes, SELLER_COPY is the only valid invoiceType. MCF_SHIPMENT will also support SELLER_COPY as the valid invoiceType. orderIds and shipmentId are mutually exclusive fields. Only one should be provided in the request. If both fields are given the request will fail. If none of the fields are set or the report options field itself is absent, then the request will return all the relevant invoices (SHIPMENT and MCF_SHIPMENT transaction types) in the requested date range.
- **reportOptions（摘录）**：
  - orderIds: A single string consisting of a comma separated list of order ids to filter. Example: 406-8193317-8698708, 408-0804227-3381000.
  - shipmentIds: A single string consisting of a comma separated list of shipment ids to filter. Example: 64119752218302, 264552989124123.
  - transactionTypes: A single string consisting of a comma separated list of transaction types to filter. The possible transactionTypes are SHIPMENT, REFUND, CANCEL, EINVOICE_CANCEL, FC_TRANSFER, FC_TRANSFER_CANCEL, FC_REMOVAL, FC_REMOVAL_CANCEL, MCF_SHIPMENT, MCF_CANCEL, and MCF_REFUND.
  - invoiceTypes: A single string consisting of a comma separated list of invoice types to filter. Possible invoiceTypes include CUSTOMER_COPY, SELLER_COPY, and TRANSPORTER_COPY.

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
