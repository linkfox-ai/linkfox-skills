# `endUserDataReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[endUserDataReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/endUserDataReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

Provides end user (customer) data to IE, ES, FR, BE, NL, DE, IT, SE, and PL selling partners. The data contains customer personal data that includes contact information, page view (glance view), and order data for customers that elect to share this data with specific sellers. The customer data is accessible across various reporting periods (DAY, WEEK, and MONTH). Developers can choose start and end dates and the reporting period for data retrieval and aggregation. If the customer does not elect to share their data, the report does not generate data.

## 对应 `reportType`（从 schema 中提取）

- `END_USER_DATA_REPORT`

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

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "dataStartTime": "2023-09-10",
  "dataEndTime": "2023-09-16",
  "reportType": "END_USER_DATA_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK"
  },
  "marketplaceIds": [
    "A1PA6795UKMFR9",
    "APJ6JRA9NG5V4"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `reportPeriod` | `WEEK` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。
