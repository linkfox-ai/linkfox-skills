# `GET_MERCHANT_LISTINGS_DATA`

> **分类**：7. 库存报告  
> **说明**：有效刊登（标准）  
> **可用范围**：仅卖家

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [库存报告](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **按需/计划**：本报告仅可按需请求。
- **输出格式**：制表符分隔的平面文件
- **角色**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：全部刊登的详细报告。每份仅支持一个站点；传多个 marketplaceIds 时只接受第一个。接受下列 reportOptions。

#### reportOptions 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| preferredReportDocumentLocale | string | 指定列标题首选语言的字符串，接受 POSIX 风格 locale，例如 "reportOptions":{"preferredReportDocumentLocale":"en_US"}。报告不会按 locale 单独缓存；在缓存周期内重复请求（按记录数约 1–6 小时）可能返回与所请求语言不同的列标题。此为 Amazon 上游行为，不是本技能响应缓存。 |

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA",
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
