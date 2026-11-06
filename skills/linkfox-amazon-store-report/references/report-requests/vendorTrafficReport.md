# `vendorTrafficReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **源文件**：[vendorTrafficReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorTrafficReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

提供 Vendor 全目录汇总和逐 ASIN 商品详情页流量，支持 DAY、WEEK、MONTH、QUARTER、YEAR，可跨多个周期。

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_TRAFFIC_REPORT`

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

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportType | string | 是 | 报告类型枚举。 |
| marketplaceIds | array[string] | 多数报告是 | 目标站点。 |
| dataStartTime / dataEndTime | string | 视报告 | ISO 8601；部分 Schema 仅使用 YYYY-MM-DD，忽略时间分量，以本页官方示例为准。 |
| reportOptions | object | 视报告 | 键名和枚举因报告而异；Brand Analytics 等必填，见下节。 |
| lastUpdatedDate | string | 视报告 | 部分 Vendor 报告使用，须按 Schema 要求与其他日期字段组合。 |

本仓库脚本 `scripts/get_report.py` 已支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_TRAFFIC_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK"
  },
  "lastUpdatedDate": "2021-06-20",
  "dataStartTime": "2021-06-06",
  "dataEndTime": "2021-06-19",
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
