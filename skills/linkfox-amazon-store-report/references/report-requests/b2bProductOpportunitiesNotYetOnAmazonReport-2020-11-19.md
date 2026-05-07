# `b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

Provides B2B product recommendations based on predicted incremental units sold, unmet buyer demand, and other factors for products not yet listed on Amazon. The recommendations are personalized to the seller based on past sales activity.

## 对应 `reportType`（SP-API）

- `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON`

Schema 描述输出 `recommendations` 结构。创建报告通常：`reportType` + `marketplaceIds`，日期字段以官方为准。

## `createReport` 请求体（`POST .../reports/2021-06-30/reports`）

LinkFox 网关通过 `developerProxy` 转发时，`body` 为 JSON 字符串，对象字段与 SP-API **CreateReport** 一致，常用结构如下：

```json
{
  "reportType": "<REPORT_TYPE>",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ],
  "dataStartTime": "2025-01-01T00:00:00Z",
  "dataEndTime": "2025-01-31T23:59:59Z",
  "reportOptions": {
    "...": "..."
  }
}
```

- **`reportType`** / **`marketplaceIds`**：必填（多数报告）。
- **`dataStartTime`** / **`dataEndTime`**：ISO 8601；部分报告 schema 使用 **仅日期** `YYYY-MM-DD`（Amazon 忽略时间分量），以本文件「官方示例」为准。
- **`reportOptions`**：对象，键名/枚举因报告而异；Brand Analytics 等 **必填**，见下节。
- **`lastUpdatedDate`**：部分 Vendor 报告使用（见 schema `reportSpecification`），需与 `dataStartTime`/`dataEndTime` 按官方要求组合。

本仓库脚本 `scripts/get_report.py` 已支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 无内嵌 `reportSpecification` 示例

创建请求请以 [Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准；可先用最小字段试请求，再根据 400 错误补充 `reportOptions`。

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。
