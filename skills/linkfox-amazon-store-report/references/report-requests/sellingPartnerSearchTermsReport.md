# `sellingPartnerSearchTermsReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellingPartnerSearchTermsReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchTermsReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Search Terms report shares data on the top-3 clicked ASINs by search keyword and department for a marketplace. Data is available at different date range aggregation levels: DAY, WEEK, MONTH, QUARTER. Requests cannot span multiple periods. For example, a request at WEEK level could not start on 2021-06-06 and end on 2021-06-19 as this would span two weeks.

## 对应 `reportType`（从 schema 中提取）

- `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT`

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
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK"
  },
  "dataStartTime": "2021-06-06",
  "dataEndTime": "2021-06-12",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
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
