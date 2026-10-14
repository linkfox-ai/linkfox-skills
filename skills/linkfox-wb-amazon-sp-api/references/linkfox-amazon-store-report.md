# Reference archive: linkfox-amazon-store-report

本文件归档该子能力的执行说明、API 契约、参数约束、错误处理和工作流；按需阅读相关章节。

## Capability instructions


## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `spApi/developerProxy` |
| `arguments` | 直接使用本 reference 对应的网关请求对象 |

```json
{
  "toolName": "spApi/developerProxy",
  "arguments": {
    "sellerId": "A1234567890",
    "region": "NA",
    "path": "reports/2021-06-30/reports",
    "method": "POST",
    "body": "<按本 reference 构造的 JSON 字符串；无请求体时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-report/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `errmsg` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `contentType` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-report
description: 亚马逊卖家店铺报告获取与下载。支持库存、订单、销量与流量、FBA、财务结算、退货、Brand Analytics 等 95+ 种报告的请求、状态轮询、下载和解压，并生成可下载的已解压文件地址。用户提到拉取或下载亚马逊报告、库存报告、订单报告、销售与流量报告、Business Report、FBA 报告、结算报告、退货报告、Brand Analytics、ABA 搜索词、Amazon store report、pull or download Amazon report 时触发。即使未明确说“报告”，只要希望从 Amazon Seller Central 批量导出某一时间段的结构化经营数据，也应触发此技能；查询少量实时订单、商品或价格优先使用对应专用技能。本技能依赖 linkfox-amazon-store-auth。
---

# Amazon 店铺报告获取

## 工作流

先通过授权 reference 选择 `sellerId` 与 `region`。报告生命周期中的创建、查询状态和获取文档信息均调用 `proxy_call`，精确 `toolName` 为 `spApi/developerProxy`，请求对象直接放入 `arguments`：

1. `POST reports/2021-06-30/reports` 创建报告并记录 `reportId`。
2. `GET reports/2021-06-30/reports/{reportId}` 查询状态；只有用户明确要求继续时才再次查询，不自动或高频轮询。
3. 状态为 `DONE` 后，`GET reports/2021-06-30/documents/{reportDocumentId}` 获取预签名下载 URL。
4. 将最终 `url`、输出路径及可选 `compressionAlgorithm` 传给 `scripts/get_report.py` 下载并按 GZIP 解压。该 helper 不调用工具网关，也不读取 LinkFox 或 Amazon 凭证。

写操作在调用前需用户明确确认。失败、空结果或不理想结果均停止并展示，不自动重试；同一 `toolName + arguments` 不重复调用。

## 请求要点

CreateReport 请求体使用 `reportType`、`marketplaceIds`，并按具体报告类型提供可选 `dataStartTime`、`dataEndTime`、`lastUpdatedDate`、`reportOptions`。完整报告类型参数与结果字段保留在下方来源归档；来源未说明的字段属性不推测。

## 错误处理

按 `references/onboarding.md` 区分 MCP 缺失、MCP 401、下游 401、402、403 和其他业务错误。WorkBuddy 自动注入 Authorization，禁止在 `arguments` 中传 headers、API Key、access/refresh token、JWT 或手机号。

## Archived reference: api.md

# Amazon 店铺报告 API Reference

本文档描述 **报告获取** 相关的 API。报告调用只传已选店铺的 `sellerId + region`，授权上下文由服务端解析；不得先调用 `spApi/storeTokens` 读取或传递 raw access token。授权建立与状态处理见本 skill 的 `linkfox-amazon-store-auth` reference。

> **依赖提示**：调用报告接口前先确认用户已选择授权店铺及其 `sellerId + region`；授权缺失时按主 `SKILL.md` 和 onboarding 停止处理，不自动重试。

## Calling Conventions

- **Request Method**: POST
- **Content-Type**: `application/json`

## API Endpoints

### 1. Developer Proxy（转发亚马逊开放接口）

**Endpoint**: `spApi/developerProxy`

报告相关的上游调用（列表 / 请求 / 查状态 / 取下载链接）都通过该代理接口转发。

**Request Parameters** (JSON):

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| region | string | Yes | 区域代码：NA/EU/FE | "NA" |
| path | string | Yes | 上游 Reports 等 API 路径（不含域名与 developer-proxy/{region}/ 前缀） | "reports/2021-06-30/reports" |
| method | string | Yes | HTTP 方法：GET/POST/PUT/DELETE | "GET" |
| queryString | string | No | Query 参数（无 `?`） | "marketplaceIds=ATVPDKIKX0DER" |
| body | string | No | POST/PUT 请求体（JSON 字符串） | `"{\"reportType\":\"...\"}"` |
| contentType | string | No | Content-Type 头（默认 application/json） | "application/json" |

**Response**:

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "httpStatus": 200,
  "contentType": "application/json",
  "body": "{\"reports\":[...]}"
}
```

**Important Notes**:
- `path` 必须在白名单内（后端 `sp-api.developer-proxy.allowed-path-prefixes`）
- 默认白名单含 `reports/2021-06-30/reports`
- 速率限制按上游亚马逊接口端点执行

---

## createReport 请求体（`POST reports/2021-06-30/reports`）

`developerProxy` 的 `body` 为 **JSON 字符串**，反序列化后与 Amazon **CreateReport** 请求体一致。

### 通用字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reportType | string | 是 | 报告类型枚举，见 `references/report-types.md` |
| marketplaceIds | array[string] | 是 | 站点 ID 列表（多数报告至少一个） |
| dataStartTime | string | 视报告 | ISO 8601；部分 schema 仅使用日期部分 `YYYY-MM-DD` |
| dataEndTime | string | 视报告 | 同上 |
| lastUpdatedDate | string | 视报告 | 部分 Vendor 报告要求，与日期字段组合以官方 schema 为准 |
| reportOptions | object | 视报告 | **Brand Analytics、销售流量、促销/优惠券、部分 Vendor** 等必填；键与枚举见各报告专页 |

### 与官方 JSON Schema 的对应关系

Amazon 在仓库 [amzn/selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中为 **带 JSON 结果包裹** 的报告提供了 Schema（含 `reportSpecification` 示例与结果字段定义）。

本 skill 在 `references/report-requests/` 下为 **每个 `*.json` 维护一份同名 `*.md`**，内容包括：

- 上游 Raw 链接与摘要说明  
- 从 schema 提取的 **`reportType`** 与 **`reportSpecification` 官方示例**（可直接作为 `body` 模板）  
- **`reportOptions`** 键表（若有）  
- 结果文档结构说明要点  

**入口索引**：`report-requests/README.md`（见本文对应归档章节）  
**按 `reportType` 全覆盖（109 个）**：`report-requests/types/README.md`（见本文对应归档章节）

> 大量 **Flat File**（订单、库存等 TSV）报告在官方仓库中**无**独立 `schemas/reports/*.json` 时，请求体通常为 `reportType` + `marketplaceIds` + 可选 `dataStartTime`/`dataEndTime`，详见 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)。

### CreateReport 请求参数映射

| JSON 参数 | 写入 createReport 体 |
|-----------|------------------------|
| reportType | reportType |
| marketplaceIds | marketplaceIds |
| dataStartTime | dataStartTime |
| dataEndTime | dataEndTime |
| lastUpdatedDate | lastUpdatedDate |
| reportOptions | reportOptions（对象原样合并） |

---

## 与依赖 skill 的接力关系

授权 skill 只负责选店。报告的创建、状态查询与文档查询按本文 MCP 工作流执行；最终预签名 URL 才交给 `scripts/get_report.py`。

## Error Codes

| errcode | 含义 | 建议动作 |
|---------|------|----------|
| 200 | 代理调用成功（还需看 `httpStatus`） | 继续解析 `body` |
| 1002 | 缺参数或认证失败 | 检查必填参数并按 onboarding 区分认证层级 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 1003 | 第三方服务调用失败 | 向用户报告，不自动重试 |
| 1005 | path 不在白名单 | 联系后端加白名单 |

### Developer Proxy 上游状态码

调用成功（`errcode=200`）后必须再检查 `httpStatus`：

| httpStatus | 含义 | 建议动作 |
|------------|------|----------|
| 200 | 成功 | 正常解析 `body` |
| 202 | 已接受（创建报告后返回） | 拿到 reportId 进入轮询 |
| 400 | 参数错误 | 检查 reportType / marketplaceIds |
| 403 | 未授权 | 检查店铺授权、权限与品牌备案 |
| 404 | 资源不存在 | 核对 reportId/reportDocumentId |
| 429 | 请求过快 | 向用户报告，不自动重试 |
| 500 | 上游错误 | 向用户报告，不自动重试 |

---

## MCP Examples 见本文开头

### 列出现有报告



### 请求新报告



### 查询报告状态



### 获取下载链接



---

## Feedback API

> 本接口与上面工具 API **不同 base URL**，不要混用。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**: `application/json`

```json
{
  "skillName": "linkfox-amazon-store-report",
  "sentiment": "NEGATIVE",
  "category": "BUG",
  "content": "Report FATAL for Brand Analytics, but store lacks brand registry — error not surfaced clearly."
}
```

**Field rules**:
- `skillName`: 使用本 skill frontmatter 的 `name`
- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`: 用户说了什么、实际发生了什么、为什么是问题

---

## 报告类型索引

完整列表见 `references/report-types.md`（95+ 种）。精简摘要见 `references/report-types-basic.md`。

**带 schema 的请求/结果格式**：`references/report-requests/README.md`（与 [GitHub schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 一一对应）。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。

## Archived reference: report-requests/accountHealthReport-2020-11-18.md

# `accountHealthReport-2020-11-18.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[accountHealthReport-2020-11-18.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/accountHealthReport-2020-11-18.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The root schema comprises the entire JSON document.

## 对应 `reportType`（SP-API）

- （文档结构对应账户状况类报告；`reportType` 以 [Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准，常见为账户状况/绩效相关枚举）

本 JSON 主要为**报告结果文档**字段定义，文件中未嵌入 `reportSpecification` 示例。创建报告时的 `reportType`、是否需 `reportOptions` 请查阅官方 Report Type Values。

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 无内嵌 `reportSpecification` 示例

创建请求请以 [Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准；可先用最小字段试请求，再根据 400 错误补充 `reportOptions`。

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 无内嵌 `reportSpecification` 示例

创建请求请以 [Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准；可先用最小字段试请求，再根据 400 错误补充 `reportOptions`。

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md

# `b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

Provides B2B product recommendations based on predicted incremental units sold, unmet buyer demand, low offer count, and other factors for products already offered on Amazon. The recommendations are personalized to the Seller based on past sales activity.

## 对应 `reportType`（SP-API）

- `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU`

同上，输出为推荐列表结构。

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 无内嵌 `reportSpecification` 示例

创建请求请以 [Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准；可先用最小字段试请求，再根据 400 错误补充 `reportOptions`。

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/endUserDataReport.md

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

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

## Archived reference: report-requests/marketplaceAsinPageViewMetrics.md

# `marketplaceAsinPageViewMetrics.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[marketplaceAsinPageViewMetrics.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/marketplaceAsinPageViewMetrics.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

Provides information on the ASIN page view (glance view) metrics for the DE, FR, IT, ES, NL, PL, SE, BE (EU-8) and UK marketplaces, with data available up to the last seven days. A page view is a customer view of the product's detail page for a given ASIN. Developers have the option to specify a start and end date to retrieve data within that range. If no dates are specified, the report will provide the data for the latest available day. For marketplaces and product categories where the seller does not have a meaningful presence (40 units sold), the report will not return any data.

## 对应 `reportType`（从 schema 中提取）

- `MARKETPLACE_ASIN_PAGE_VIEW_METRICS`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "dataStartTime": "2023-04-27",
  "dataEndTime": "2023-05-03",
  "reportType": "MARKETPLACE_ASIN_PAGE_VIEW_METRICS",
  "reportOptions": {
    "productType": "AUTO_BATTERY"
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
| `productType` | `AUTO_BATTERY` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/promotionReport.md

# `promotionReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[promotionReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/promotionReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Promotion Performance report contains data to help vendors optimize their promotions and adjust their advertising strategies. Currently three promotion types are supported: Best Deal, Lightning Deal, and Price Discount. This report supports start dates up to two years before the current date.

## 对应 `reportType`（从 schema 中提取）

- `GET_PROMOTION_PERFORMANCE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_PROMOTION_PERFORMANCE_REPORT",
  "reportOptions": {
    "promotionStartDateFrom": "2020-11-23T15:33:26Z",
    "promotionStartDateTo": "2020-12-06T15:33:26Z"
  },
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `promotionStartDateFrom` | `2020-11-23T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `promotionStartDateTo` | `2020-12-06T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/README.md

# 报告请求与文档格式（按 GitHub schema 分文件）

> 与 [amzn/selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中的 JSON Schema **一一对应**。

## `reportType` 全覆盖（含无 JSON 的 Flat File）

`references/report-types.md` 表格中的 **每一个** `reportType` 均有专页 → **`types/README.md`（见本文对应归档章节）**（109 个：`types/<REPORT_TYPE>.md`）。  
有 GitHub JSON 的条目会链回下表中的 `*.md`；其余条目给出最小 CreateReport 模板并指向 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)。

## 索引（仅含官方 `schemas/reports/*.json`）

| 文档 | 上游 Schema | 涉及 `reportType` |
|------|-------------|-------------------|
| `accountHealthReport-2020-11-18.md`（见本文对应归档章节） | [`accountHealthReport-2020-11-18.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/accountHealthReport-2020-11-18.json) | 见专页（账户状况结果 JSON；`reportType` 以官方 Report Type Values 为准） |
| `b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md`（见本文对应归档章节） | [`b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json) | `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` |
| `b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md`（见本文对应归档章节） | [`b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json) | `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` |
| `endUserDataReport.md`（见本文对应归档章节） | [`endUserDataReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/endUserDataReport.json) | `END_USER_DATA_REPORT` |
| `marketplaceAsinPageViewMetrics.md`（见本文对应归档章节） | [`marketplaceAsinPageViewMetrics.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/marketplaceAsinPageViewMetrics.json) | `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` |
| `promotionReport.md`（见本文对应归档章节） | [`promotionReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/promotionReport.json) | `GET_PROMOTION_PERFORMANCE_REPORT` |
| `sellerCouponReport.md`（见本文对应归档章节） | [`sellerCouponReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerCouponReport.json) | `GET_COUPON_PERFORMANCE_REPORT` |
| `sellerSalesAndTrafficReport.md`（见本文对应归档章节） | [`sellerSalesAndTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerSalesAndTrafficReport.json) | `GET_SALES_AND_TRAFFIC_REPORT` |
| `sellingPartnerMarketBasketAnalysisReport.md`（见本文对应归档章节） | [`sellingPartnerMarketBasketAnalysisReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerMarketBasketAnalysisReport.json) | `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT`（搜索词见 `sellingPartnerSearchTermsReport`） |
| `sellingPartnerRepeatPurchaseReport.md`（见本文对应归档章节） | [`sellingPartnerRepeatPurchaseReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerRepeatPurchaseReport.json) | `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` |
| `sellingPartnerSearchCatalogPerformanceReport.md`（见本文对应归档章节） | [`sellingPartnerSearchCatalogPerformanceReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchCatalogPerformanceReport.json) | `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` |
| `sellingPartnerSearchQueryPerformanceReport.md`（见本文对应归档章节） | [`sellingPartnerSearchQueryPerformanceReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchQueryPerformanceReport.json) | `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` |
| `sellingPartnerSearchTermsReport.md`（见本文对应归档章节） | [`sellingPartnerSearchTermsReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchTermsReport.json) | `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` |
| `vendorCouponReport.md`（见本文对应归档章节） | [`vendorCouponReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorCouponReport.json) | `GET_COUPON_PERFORMANCE_REPORT` |
| `vendorForecastingReport.md`（见本文对应归档章节） | [`vendorForecastingReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorForecastingReport.json) | `GET_VENDOR_FORECASTING_REPORT` |
| `vendorInventoryReport.md`（见本文对应归档章节） | [`vendorInventoryReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorInventoryReport.json) | `GET_VENDOR_INVENTORY_REPORT` |
| `vendorNetPureProductMarginReport.md`（见本文对应归档章节） | [`vendorNetPureProductMarginReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorNetPureProductMarginReport.json) | `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` |
| `vendorRealTimeInventoryReport.md`（见本文对应归档章节） | [`vendorRealTimeInventoryReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeInventoryReport.json) | `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` |
| `vendorRealTimeSalesReport.md`（见本文对应归档章节） | [`vendorRealTimeSalesReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeSalesReport.json) | `GET_VENDOR_REAL_TIME_SALES_REPORT` |
| `vendorRealTimeTrafficReport.md`（见本文对应归档章节） | [`vendorRealTimeTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeTrafficReport.json) | `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` |
| `vendorSalesReport.md`（见本文对应归档章节） | [`vendorSalesReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorSalesReport.json) | `GET_VENDOR_SALES_REPORT` |
| `vendorTrafficReport.md`（见本文对应归档章节） | [`vendorTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorTrafficReport.json) | `GET_VENDOR_TRAFFIC_REPORT` |

## 通用说明

- **创建报告**：`references/api.md` 中的 `developerProxy` + `path=reports/2021-06-30/reports` + `method=POST`。
- **本目录**：每个 `*.md` 对应一个 `*.json`，给出 `createReport` 请求体要点及 schema 摘要。
- **未出现在上表中的 reportType**：见 **`types/`（见本文对应归档章节）** 目录下按枚举命名的专页（全覆盖 `report-types.md`）。

## Archived reference: report-requests/sellerCouponReport.md

# `sellerCouponReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellerCouponReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerCouponReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report contains data to help sellers optimize their coupons and adjust their advertising strategies. This report supports start dates up to two years before the current date.

## 对应 `reportType`（从 schema 中提取）

- `GET_COUPON_PERFORMANCE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_COUPON_PERFORMANCE_REPORT",
  "reportOptions": {
    "couponStartDateFrom": "2021-11-01T15:33:26Z",
    "couponStartDateTo": "2021-11-30T15:33:26Z"
  },
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `couponStartDateFrom` | `2021-11-01T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `couponStartDateTo` | `2021-11-30T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/sellerSalesAndTrafficReport.md

# `sellerSalesAndTrafficReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellerSalesAndTrafficReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerSalesAndTrafficReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares data on the sales performance and page traffic of the seller's items aggregated by date (across the seller's entire catalog of items) and aggregated by ASIN. Aggregated data is available at different date range aggregation levels: DAY, WEEK, MONTH. Per-ASIN data is available at different ASIN aggregation levels: PARENT, CHILD, SKU. Requests can span multiple date range periods.

## 对应 `reportType`（从 schema 中提取）

- `GET_SALES_AND_TRAFFIC_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
  "reportOptions": {
    "dateGranularity": "DAY",
    "asinGranularity": "SKU"
  },
  "dataStartTime": "2021-06-11",
  "dataEndTime": "2021-06-14",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `dateGranularity` | `DAY` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `asinGranularity` | `SKU` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/sellingPartnerMarketBasketAnalysisReport.md

# `sellingPartnerMarketBasketAnalysisReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellingPartnerMarketBasketAnalysisReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerMarketBasketAnalysisReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Market Basket report contains data on the items that are most commonly purchased in combination with the items in the customer's basket (cart) at checkout. The data is available across different reporting periods: DAY, WEEK, MONTH, and QUARTER. Requests can span multiple reporting periods. In this report, "asin" is an ASIN in the selling partner's catalog and "purchasedWithAsin" might or might not be an ASIN in the selling partner's catalog.

## 对应 `reportType`

- 本文件根级 `reportSpecification.properties.reportType.enum` 为 **`GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT`**。
- `reportSpecification.examples` 中曾出现 `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` 示例，与 **Search Terms** 专用 schema [`sellingPartnerSearchTermsReport.json`](https://github.com/amzn/selling-partner-api-models/blob/main/schemas/reports/sellingPartnerSearchTermsReport.json) 对应；拉 **搜索词** 报告请以该文件及 `sellingPartnerSearchTermsReport.md`（见本文对应归档章节） 为准。

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK"
  },
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

## Archived reference: report-requests/sellingPartnerRepeatPurchaseReport.md

# `sellingPartnerRepeatPurchaseReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellingPartnerRepeatPurchaseReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerRepeatPurchaseReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Repeat Purchase report shares data on the quantity of repeated purchases of the selling partner's items. Data is available at different date range aggregation levels: WEEK, MONTH, QUARTER. Requests can span multiple reporting periods. In this report, "asin" is an ASIN in the selling partner's catalog.

## 对应 `reportType`（从 schema 中提取）

- `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK"
  },
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

## Archived reference: report-requests/sellingPartnerSearchCatalogPerformanceReport.md

# `sellingPartnerSearchCatalogPerformanceReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellingPartnerSearchCatalogPerformanceReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchCatalogPerformanceReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Search Catalog Performance report provides search engagement metrics, such as impressions, clicks, cart adds, and purchases for a date range that you specify. The data is available at different reporting periods: WEEK, MONTH, and QUARTER. Requests cannot span multiple periods. For example, a request at the WEEK level cannot start on 2025-01-05 and end on 2025-01-18 as this request spans two weeks.

## 对应 `reportType`（从 schema 中提取）

- `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK",
    "asins": "B123456789 B987654321"
  },
  "dataStartTime": "2025-01-05",
  "dataEndTime": "2025-01-11",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `reportPeriod` | `WEEK` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `asins` | `B123456789 B987654321` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/sellingPartnerSearchQueryPerformanceReport.md

# `sellingPartnerSearchQueryPerformanceReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[sellingPartnerSearchQueryPerformanceReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchQueryPerformanceReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Search Query Performance Report provides overall query performance, such as impressions, clicks, cart adds, and purchases for a list of Amazon Standard Identification Numbers (ASINs) and date range that you specify. Data is available at different reporting periods: WEEK, MONTH, and QUARTER. Requests cannot span multiple periods. For example, a request at the WEEK level cannot start on 2025-01-05 and end on 2025-01-18 as this request spans two weeks.

## 对应 `reportType`（从 schema 中提取）

- `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK",
    "asin": "B123456789 B987654321"
  },
  "dataStartTime": "2025-01-05",
  "dataEndTime": "2025-01-11",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `reportPeriod` | `WEEK` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `asin` | `B123456789 B987654321` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/sellingPartnerSearchTermsReport.md

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

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

## Archived reference: report-requests/types/END_USER_DATA_REPORT.md

# `END_USER_DATA_REPORT`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：End user data report  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`endUserDataReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#end-user-data-report)（章节：**End User Data Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Buyer Communication](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#buyer-communication)
- **Availability**：Sellers
- **Marketplace availability**：IE, ES, FR, BE, NL, DE, IT, SE, and PL.
- **Requested/scheduled**：This report can be requested or scheduled.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#end-user-data-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "END_USER_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/FBA_BULK_INVOICE.md

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

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/FEE_DISCOUNTS_REPORT.md

# `FEE_DISCOUNTS_REPORT`

> **分类**：1. Amazon Business Reports  
> **说明**：Amazon Business fee discounts  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Amazon Business Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-amazon-business#referral-fee-discounts-report)（章节：**Referral Fee Discounts Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Availability**：Amazon Business sellers
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Microsoft Excel Workbook file (.xlsx)
- **要点**：Contains a summary of the seller's fee discounts. 📘NoteInformation in this report can be up to 24 hours old. Do not request a report more than once within a 24-hour period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-amazon-business#referral-fee-discounts-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "FEE_DISCOUNTS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "FEE_DISCOUNTS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_AFN_INVENTORY_DATA.md

# `GET_AFN_INVENTORY_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Amazon Fulfilled Network inventory  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-inventory-report)（章节：**FBA Amazon Fulfilled Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_AFN_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_AFN_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_AFN_INVENTORY_DATA_BY_COUNTRY.md

# `GET_AFN_INVENTORY_DATA_BY_COUNTRY`

> **分类**：6.2 FBA Inventory  
> **说明**：AFN inventory by country  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-multi-country-inventory-report)（章节：**FBA Multi-Country Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：Seller Central sellers
- **Marketplace availability**：Europe (EU)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains quantity available for local fulfillment by country, helping Multi-Country Inventory sellers in Europe track their FBA inventory. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-multi-country-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_AFN_INVENTORY_DATA_BY_COUNTRY",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_AFN_INVENTORY_DATA_BY_COUNTRY",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL.md

# `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA fulfilled shipments (general)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report)（章节：**FBA Amazon Fulfilled Shipments Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking)
- **要点**：Contains detailed order/shipment/item information including price, courier, and tracking data. You can request up to one month of data in a single report. Content updated in near real-time in Europe (EU), Japan, and North America (NA). 📘NoteIn Japan, EU, and NA, in most cases, there will be a delay of approximately one to three hours from the time a fulfillment order ships and the time the items in the fulfillment order appear in the report. In some rare cases there could be a delay of up to 24 hours.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING.md

# `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA shipments for invoicing  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report-invoicing)（章节：**FBA Amazon Fulfilled Shipments Report (Invoicing)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：This report should be used to generate tax invoices in the EU region. You can request up to one month of data in a single report. Content updated in near real-time in Europe (EU), Japan, and North America (NA). 📘Note:In most cases, there will be a delay of approximately one to three hours from the time a fulfillment order ships and the time the items in the fulfillment order appear in the report. In some rare cases there could be a delay of up to 24 hours.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report-invoicing>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX.md

# `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA shipments tax data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report-tax)（章节：**FBA Amazon Fulfilled Shipments Report (Tax)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：This report is for calculating and remitting taxes in the NA region. You can request up to one month of data in a single report. Content updated in near real-time in Europe (EU), Japan, and North America (NA). 📘Note:In most cases, there will be a delay of approximately one to three hours from the time a fulfillment order ships and the time the items in the fulfillment order appear in the report. In some rare cases there could be a delay of up to 24 hours.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-amazon-fulfilled-shipments-report-tax>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON.md

# `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON`

> **分类**：3. B2B Product Opportunities  
> **说明**：B2B opportunities not yet on Amazon  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[B2B Product Opportunities Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---not-yet-on-amazon)（章节：**B2B Product Opportunities - Not yet on Amazon**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Marketplace availability**：This report is only available in the following marketplaces:
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---not-yet-on-amazon>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU.md

# `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU`

> **分类**：3. B2B Product Opportunities  
> **说明**：Personalized B2B product recommendations  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[B2B Product Opportunities Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---recommended-for-you-report)（章节：**B2B Product Opportunities - Recommended for You Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Marketplace availability**：This report is only available in the following marketplaces:
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---recommended-for-you-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT.md

# `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Products frequently purchased together  
> **可用范围**：Both

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellingPartnerMarketBasketAnalysisReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#market-basket-analysis-report)（章节：**Market Basket Analysis Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers and vendors who have the Brand Analytics Selling Partner API role and are registered in [Amazon Brand Registry](https://brandservices.amazon.com).
- **Marketplace availability**：NA (all marketplaces), EU (Spain, United Kingdom, France, Netherlands, Germany, Italy, Sweden, Turkey, Saudi Arabia, United Arab Emirates, India), FE (all marketplaces).
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#market-basket-analysis-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT.md

# `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Repeat purchase behavior analysis  
> **可用范围**：Both

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellingPartnerRepeatPurchaseReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#repeat-purchase)（章节：**Repeat Purchase**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers and vendors who have the Brand Analytics Selling Partner API role and are registered in [Amazon Brand Registry](https://brandservices.amazon.com/).
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#repeat-purchase>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT.md

# `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Search catalog performance metrics  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellingPartnerSearchCatalogPerformanceReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#search-catalog-performance-report)（章节：**Search Catalog Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers who have the Brand Analytics Selling Partner API role and are registered in [Amazon Brand Registry](https://brandservices.amazon.com).
- **Marketplace availability**：NA (all marketplaces), EU (Spain, United Kingdom, France, Netherlands, Germany, Italy, Sweden, Turkey, Saudi Arabia, United Arab Emirates, India), FE (all marketplaces).
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#search-catalog-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT.md

# `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Search query performance data  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellingPartnerSearchQueryPerformanceReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#search-query-performance-report)（章节：**Search Query Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers who have the Brand Analytics Selling Partner API role and are registered in [Amazon Brand Registry](https://brandservices.amazon.com).
- **Marketplace availability**：NA (all marketplaces), EU (Spain, United Kingdom, France, Netherlands, Germany, Italy, Sweden, Turkey, Saudi Arabia, United Arab Emirates, India), FE (all marketplaces).
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#search-query-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT.md

# `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Top search terms for products  
> **可用范围**：Both

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellingPartnerSearchTermsReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#amazon-search-terms-report)（章节：**Amazon Search Terms Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers and vendors who have the Brand Analytics Selling Partner API role, are registered in [Amazon Brand Registry](https://brandservices.amazon.com/), and are a brand representative.
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#amazon-search-terms-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA.md

# `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA`

> **分类**：9. Order Reports  
> **说明**：Converged pending orders  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#converged-flat-file-pending-orders-report)（章节：**Converged Flat File Pending Orders Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Order Fulfillment Channel**：MFN
- **Availability**：Marketplace sellers
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Flat file
- **要点**：Contains all pending orders.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#converged-flat-file-pending-orders-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_COUPON_PERFORMANCE_REPORT.md

# `GET_COUPON_PERFORMANCE_REPORT`

> **分类**：11. Performance Reports  
> **说明**：Coupon performance  
> **可用范围**：Both

> **说明**：Seller 与 Vendor 共用同一 `reportType` 字符串时，请按账号类型阅读 **Seller** 或 **Vendor** 专页。

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellerCouponReport.md`（见本文对应归档章节）、`vendorCouponReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#coupons-performance-report)（章节：**Coupons Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers and Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#coupons-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_COUPON_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_CSV_MFN_PRIME_RETURNS_REPORT.md

# `GET_CSV_MFN_PRIME_RETURNS_REPORT`

> **分类**：13. Returns Reports  
> **说明**：MFN Prime returns (CSV)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#csv-prime-returns-report-by-return-date)（章节：**CSV Prime Returns Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Comma-separated flat file
- **要点**：Contains detailed Seller Fulfilled Prime returns information, including return request date, RMA ID, label details, ASIN, and return reason code. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#csv-prime-returns-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_CSV_MFN_PRIME_RETURNS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_CSV_MFN_PRIME_RETURNS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_DATE_RANGE_FINANCIAL_HOLDS_DATA.md

# `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA`

> **分类**：10. Payment Reports  
> **说明**：Financial holds by date range  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Payment Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-payment#deferred-transaction-report)（章节：**Deferred Transaction Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：Seller Central sellers
- **Report output type**：Comma-separated flat file
- **Roles**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **要点**：A point-in-time report that contains a list of deferred transactions. A single report can provide up to 10 years of data. 🚧ImportantYou must request the Deferred Transaction Report through the Payments Reports Repository on [Seller Central](https://developer-docs.amazon.com/sp-api/docs/seller-central-urls) before you can use the [Reports v2021-06-30](https://developer-docs.amazon.com/sp-api/reference/reports-v2021-06-30) API to retrieve the Deferred Transaction Report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-payment#deferred-transaction-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_DATE_RANGE_FINANCIAL_HOLDS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_DATE_RANGE_FINANCIAL_HOLDS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EASYSHIP_DOCUMENTS.md

# `GET_EASYSHIP_DOCUMENTS`

> **分类**：5. Easy Ship Reports  
> **说明**：Easy Ship shipping documents  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Easy Ship Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-report)（章节：**EasyShip Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Report output type**：PDF
- **要点**：Contains the invoice, shipping label, and warranty (if available) documents for an Amazon EasyShip order.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EASYSHIP_DOCUMENTS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EASYSHIP_DOCUMENTS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EASYSHIP_PICKEDUP.md

# `GET_EASYSHIP_PICKEDUP`

> **分类**：5. Easy Ship Reports  
> **说明**：Easy Ship picked up orders  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Easy Ship Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-picked-up-report)（章节：**EasyShip Picked Up Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Report output type**：Tab-delimited file
- **要点**：Contains all the seller-fulfilled orders that were picked up on the specified dates.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-picked-up-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EASYSHIP_PICKEDUP",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EASYSHIP_PICKEDUP",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EASYSHIP_WAITING_FOR_PICKUP.md

# `GET_EASYSHIP_WAITING_FOR_PICKUP`

> **分类**：5. Easy Ship Reports  
> **说明**：Orders waiting for Easy Ship pickup  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Easy Ship Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-waiting-for-pick-up-report)（章节：**EasyShip Waiting for Pick Up Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Report output type**：Tab-delimited file
- **要点**：Contains all of a seller's orders that are in the following status in Seller Central: "Waiting for pick up"

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-easy-ship#easyship-waiting-for-pick-up-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EASYSHIP_WAITING_FOR_PICKUP",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EASYSHIP_WAITING_FOR_PICKUP",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EPR_ANNUAL_REPORTS.md

# `GET_EPR_ANNUAL_REPORTS`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：EPR annual reports  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-annual-report)（章节：**EPR Annual Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file
- **要点**：Contains data used to declare EPR compliance to regulatory bodies and pay EPR fees, aggregated by year. Amazon Extended Producer Responsibility Reports (Amazon EPR Reports) allow sellers to programmatically retrieve all the necessary data required for EPR reporting to regulatory bodies and pay EPR fees. Amazon EPR Reports offer a significant time savings to sellers by generating reports without requiring manual data compilation across several data sources and manual product classification.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-annual-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EPR_ANNUAL_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EPR_ANNUAL_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EPR_MONTHLY_REPORTS.md

# `GET_EPR_MONTHLY_REPORTS`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：Extended Producer Responsibility (monthly)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-monthly-report)（章节：**EPR Monthly Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file
- **要点**：Contains data used to declare EPR compliance to regulatory bodies and pay EPR fees, aggregated by month. Amazon Extended Producer Responsibility Reports (Amazon EPR Reports) allow sellers to programmatically retrieve all the necessary data required for EPR reporting to regulatory bodies and pay EPR fees. Amazon EPR Reports offer a significant time savings to sellers by generating reports without requiring manual data compilation across several data sources and manual product classification.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-monthly-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EPR_MONTHLY_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EPR_MONTHLY_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_EPR_QUARTERLY_REPORTS.md

# `GET_EPR_QUARTERLY_REPORTS`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：EPR quarterly reports  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-quarterly-report)（章节：**EPR Quarterly Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file
- **要点**：Contains data used to declare EPR compliance to regulatory bodies and pay EPR fees, aggregated by quarter. Amazon Extended Producer Responsibility Reports (Amazon EPR Reports) allow sellers to programmatically retrieve all the necessary data required for EPR reporting to regulatory bodies and pay EPR fees. Amazon EPR Reports offer a significant time savings to sellers by generating reports without requiring manual data compilation across several data sources and manual product classification.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#epr-quarterly-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_EPR_QUARTERLY_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_EPR_QUARTERLY_REPORTS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA.md

# `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA`

> **分类**：6.3 FBA Fees & Charges  
> **说明**：Estimated FBA fees  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-fee-preview-report)（章节：**FBA Fee Preview Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains the estimated Amazon Selling and Fulfillment Fees for the seller's FBA inventory with active offers. The content is updated at least once every 72 hours. To successfully generate a report, specify the dataStartTime parameter for a minimum 72 hours prior to NOW and dataEndTime to NOW. 🚧CautionThis report can only be requested once per day per seller.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-fee-preview-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA.md

# `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA`

> **分类**：6.4 FBA Returns & Reimbursements  
> **说明**：FBA customer returns  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-returns-report)（章节：**FBA Returns Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains customer returned items received at an Amazon fulfillment center, including Return Reason and Disposition. Content updated daily.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-returns-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA.md

# `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA shipment promotion data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-promotions-report)（章节：**FBA Promotions Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Marketplace availability**：North America (NA)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains promotions applied to FBA customer orders sold through Amazon, such as Super Saver Shipping. Content updated daily.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-promotions-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA.md

# `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA`

> **分类**：6.4 FBA Returns & Reimbursements  
> **说明**：FBA shipment replacements  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-replacements-report)（章节：**FBA Replacements Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：FBA sellers.
- **Marketplace availability**：NA and IN marketplaces.
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains replacements that have been issued to customers for completed orders. Content updated daily. For FBA sellers only.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-replacements-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA.md

# `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA customer shipment sales  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-customer-shipment-sales-report)（章节：**FBA Customer Shipment Sales Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains condensed item level data on shipped FBA customer orders including price, quantity, and ship-to location. Content updated in near real-time in Europe (EU), Japan, and North America (NA). 📘Note:In Japan, EU, and NA, in most cases, there will be a delay of approximately one to three hours from the time a fulfillment order ships and the time the items in the fulfillment order appear in the report. In some rare cases there could be a delay of up to 24 hours.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-customer-shipment-sales-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA.md

# `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA`

> **分类**：6.1 FBA Shipments  
> **说明**：FBA customer taxes  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-customer-taxes)（章节：**FBA Customer Taxes**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **要点**：Tab-delimited flat file report for tax-enabled US sellers. This report contains data through February 28, 2013. All new transaction data can be found in the Sales Tax Report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-customer-taxes>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA.md

# `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA`

> **分类**：6.6 FBA Compliance  
> **说明**：Inbound non-compliance issues  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inbound-performance-report)（章节：**FBA Inbound Performance Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains inbound shipment problems by product and shipment. Content updated daily.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inbound-performance-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA.md

# `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA`

> **分类**：6.3 FBA Fees & Charges  
> **说明**：Long-term storage fees  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-long-term-storage-fee-charges-report)（章节：**FBA Long Term Storage Fee Charges Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains the charge data for long-term storage. 📘Note:To ensure the correctness of the report generated, the time between the dataStartTime and the dateEndTime attributes of the CreateReportSpecification should be equal to one month.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-long-term-storage-fee-charges-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA.md

# `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA`

> **分类**：6.5 FBA Removals  
> **说明**：Removal order details  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removal-order-detail-report)（章节：**FBA Removal Order Detail Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains all the removal orders, including the items in each removal order, placed during any given time period. This can be used to help reconcile the total number of items requested to be removed from an Amazon fulfillment center with the actual number of items removed, along with the status of each item in the removal order. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removal-order-detail-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA.md

# `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA`

> **分类**：6.5 FBA Removals  
> **说明**：Removal shipment details  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removal-shipment-detail-report)（章节：**FBA Removal Shipment Detail Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Provides shipment tracking information for all removal orders and includes the items that have been removed from an Amazon fulfillment center for either a single removal order or for a date range. This report will not include canceled returns or disposed items; it is only for shipment information. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removal-shipment-detail-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_INVENTORY_PLANNING_DATA.md

# `GET_FBA_INVENTORY_PLANNING_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：FBA inventory planning  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory-health-report)（章节：**FBA Manage Inventory Health Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Provides a consolidated view across your sales (7, 30, 60, and 90 days), shipment statuses (working, received, and shipped), estimated storage and long-term storage fees, and aged and excess units. It includes metrics across sales, inbound, estimated fees, and recommended actions. Not available in the NL, PL, SE, or BE marketplaces.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory-health-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_INVENTORY_PLANNING_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_INVENTORY_PLANNING_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_MYI_ALL_INVENTORY_DATA.md

# `GET_FBA_MYI_ALL_INVENTORY_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：FBA all inventory status  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory---archived)（章节：**FBA Manage Inventory - Archived**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains current details of all (including archived) inventory including condition, quantity, and volume. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory---archived>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_MYI_ALL_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_MYI_ALL_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA.md

# `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：FBA Manage Your Inventory (active)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory)（章节：**FBA Manage Inventory**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains current details of active (not archived) inventory including condition, quantity, and volume. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-manage-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_OVERAGE_FEE_CHARGES_DATA.md

# `GET_FBA_OVERAGE_FEE_CHARGES_DATA`

> **分类**：6.3 FBA Fees & Charges  
> **说明**：FBA overage fee charges  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-storage-overage-fees-report)（章节：**FBA Inventory Storage Overage Fees Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Estimated inventory storage overage fees for each storage type of your inventory in Amazon fulfillment centers that exceeds your storage limits.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-storage-overage-fees-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_OVERAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_OVERAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_RECOMMENDED_REMOVAL_DATA.md

# `GET_FBA_RECOMMENDED_REMOVAL_DATA`

> **分类**：6.5 FBA Removals  
> **说明**：Recommended removal inventory  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-recommended-removal-report)（章节：**FBA Recommended Removal Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Identifies sellable items that will be 365 days old or older during the next Long-Term Storage cleanup event, if the report is generated within six weeks of the cleanup event date. This report includes both sellable and unsellable items. Content updated daily.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-recommended-removal-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_RECOMMENDED_REMOVAL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_RECOMMENDED_REMOVAL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_REIMBURSEMENTS_DATA.md

# `GET_FBA_REIMBURSEMENTS_DATA`

> **分类**：6.4 FBA Returns & Reimbursements  
> **说明**：FBA reimbursements  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-reimbursements-report)（章节：**FBA Reimbursements Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains itemized details of a seller's inventory reimbursements, including the reason for the reimbursement. Content updated daily.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-reimbursements-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_REIMBURSEMENTS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_REIMBURSEMENTS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FBA_STORAGE_FEE_CHARGES_DATA.md

# `GET_FBA_STORAGE_FEE_CHARGES_DATA`

> **分类**：6.3 FBA Fees & Charges  
> **说明**：FBA storage fee charges  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-storage-fees-report)（章节：**FBA Storage Fees Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains estimated monthly inventory storage fees for each ASIN of a seller's inventory in Amazon fulfillment centers.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-storage-fees-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FBA_STORAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FBA_STORAGE_FEE_CHARGES_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING.md

# `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING`

> **分类**：9. Order Reports  
> **说明**：Actionable orders for shipping  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#unshipped-orders-report)（章节：**Unshipped Orders Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Order Fulfillment Channel**：MFN
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：Contains only orders that are not confirmed as shipped. This report covers a 38-day lookback period. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - ShowSalesChannel: A Boolean value that indicates whether an additional column is added to the report that shows the sales channel. Default: false. Example: "reportOptions":{"ShowSalesChannel":"true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#unshipped-orders-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL.md

# `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL`

> **分类**：9. Order Reports  
> **说明**：All orders by last update  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-orders-by-last-update-report)（章节：**Flat File Orders By Last Update Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Order Fulfillment Channel**：MFN and FBA
- **Availability**：Sellers
- **Requested/scheduled**：Requested
- **Report output type**：Tab-delimited flat file
- **Roles**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **要点**：Contains all orders updated in the specified period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-orders-by-last-update-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL.md

# `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`

> **分类**：9. Order Reports  
> **说明**：All orders by order date  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-orders-by-order-date-report)（章节：**Flat File Orders By Order Date Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Order Fulfillment Channel**：MFN and FBA
- **Availability**：Sellers
- **Requested/scheduled**：Requested
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **要点**：Contains all orders that were placed in the specified period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-orders-by-order-date-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE.md

# `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE`

> **分类**：9. Order Reports  
> **说明**：Archived orders  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-archived-orders-report)（章节：**Flat File Archived Orders Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Order Fulfillment Channel**：MFN and FBA
- **Availability**：Sellers
- **Requested/scheduled**：Requested
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **要点**：Contains all archived orders that were placed in the specified period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-archived-orders-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT.md

# `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT`

> **分类**：13. Returns Reports  
> **说明**：MFN SKU return attributes (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#flat-file-return-attributes-report-by-return-date)（章节：**Flat File Return Attributes Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains detailed return attribute information by SKU, including prepaid label eligibility and returnless refund eligibility. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#flat-file-return-attributes-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_OPEN_LISTINGS_DATA.md

# `GET_FLAT_FILE_OPEN_LISTINGS_DATA`

> **分类**：7. Inventory Reports  
> **说明**：Open listings (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_FLAT_FILE_OPEN_LISTINGS_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：Seller Central sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：Contains a summary of the seller's product listings with the price and quantity for each SKU. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - Custom: A Boolean value that indicates whether a custom report is returned. Default: false. Example: "reportOptions":{"custom":"true"}.
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING.md

# `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING`

> **分类**：9. Order Reports  
> **说明**：Order invoicing (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-invoicing)（章节：**Requested or Scheduled Flat File Order Report (Invoicing)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Marketplace availability**：EU
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：This report can be used to generate tax invoices in the EU region. This report shows orders from the previous 60 days. Seller Central sellers can only schedule one GET_ORDER_REPORT_DATA_INVOICING or GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled. 📘NoteThe format of this report will differ slightly depending on whether it is scheduled or requested.
- **reportOptions（摘录）**：
  - ShowSalesChannel: A Boolean value that indicates whether an additional column is added to the report that shows the sales channel. Default: false. Example: "reportOptions":{"ShowSalesChannel":"true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-invoicing>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING.md

# `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING`

> **分类**：9. Order Reports  
> **说明**：Order shipping (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-shipping)（章节：**Requested or Scheduled Flat File Order Report (Shipping)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：Contains orders from the previous 60 days. This report can be used to ship Amazon orders. Seller Central sellers can only schedule one GET_ORDER_REPORT_DATA_SHIPPING or GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled. 📘NoteThe format of this report will differ slightly depending on whether it is scheduled or requested. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - ShowSalesChannel: A Boolean value that indicates whether an additional column is added to the report that shows the sales channel. Default: false. Example: "reportOptions":{"ShowSalesChannel":"true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-shipping>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_ORDER_REPORT_DATA_TAX.md

# `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX`

> **分类**：9. Order Reports  
> **说明**：Order tax (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#requested-or-scheduled-flat-file-order-report-tax)（章节：**Requested or Scheduled Flat File Order Report (Tax)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Marketplace availability**：NA
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：Contains orders from the previous 60 days for NA region only. Seller Central sellers can only schedule one GET_ORDER_REPORT_DATA_TAX or GET_FLAT_FILE_ORDER_REPORT_DATA_TAX report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled. 📘NoteThe format of this report will differ slightly depending on whether it is scheduled or requested. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - ShowSalesChannel: A Boolean value that indicates whether an additional column is added to the report that shows the sales channel. Default: false. Example: "reportOptions":{"ShowSalesChannel":"true"}

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

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_PENDING_ORDERS_DATA.md

# `GET_FLAT_FILE_PENDING_ORDERS_DATA`

> **分类**：9. Order Reports  
> **说明**：Pending orders (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-pending-orders-report)（章节：**Flat File Pending Orders Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking)
- **Order Fulfillment Channel**：MFN
- **Availability**：Sellers
- **Requested/scheduled**：Requested or scheduled
- **Report output type**：Tab-delimited flat file
- **要点**：Contains all pending orders.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#flat-file-pending-orders-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE.md

# `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE`

> **分类**：13. Returns Reports  
> **说明**：Returns by date (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#flat-file-returns-report-by-return-date)（章节：**Flat File Returns Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains detailed returns information, including return request date, RMA ID, label details, ASIN, and return reason code. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#flat-file-returns-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_SALES_TAX_DATA.md

# `GET_FLAT_FILE_SALES_TAX_DATA`

> **分类**：15. Tax Reports  
> **说明**：Sales tax collection data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#sales-tax-report)（章节：**Sales Tax Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Report output type**：Tab-delimited flat file
- **Store availability**：US
- **User type**：Sellers
- **要点**：Tab-delimited flat file for tax-enabled US sellers. Content updated daily. This report cannot be requested or scheduled. The seller must generate the report from the Tax Document Library in Seller Central. After the report has been generated, you can search for it using the getReports operation.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#sales-tax-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_SALES_TAX_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_SALES_TAX_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT.md

# `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT`

> **分类**：8. Invoice Reports  
> **说明**：VAT invoice data (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Invoice Data Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#flat-file-vat-invoice-data-report-vidr)（章节：**Flat File VAT Invoice Data Report (VIDR)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Availability**：Sellers who have enrolled in Amazon's VAT Calculation Service and have opted to upload their own invoices. This report is for both Fulfillment by Amazon and seller-fulfilled orders.
- **Report output type**：Tab-delimited flat file
- **Default**："pendingInvoices" : "true"
- **要点**：Provides all the information required to generate a VAT invoice for each shipment, return, or refund for a seller's order. A shipment is included in this report immediately after it is dispatched. Amazon recommends scheduling this report at least twice a day. This report accepts the following reportOptions values: For information on how to use this report, refer to [VAT Calculation Service](https://developer-docs.amazon.com/sp-api/docs/vat-calculation-service-guide).
- **reportOptions（摘录）**：
  - pendingInvoices – A Boolean value. When true, the report contains only shipments for which invoices and credit notes are pending. This report does not contain shipments for which invoices have already been uploaded successfully. Includes shipments for orders that were placed within the previous 90 days. When false, or if pendingInvoices is not included in reportOptions, the content of the report depends on the value of all. Example: "reportOptions": {"ReportOption=pendingInvoices": "true"}
  - all – A Boolean value. When true, the report contains shipments for orders that were placed within the date range that you specify. Includes shipments of all possible invoice statuses. You must specify the startDate and endDate parameters of the [createReport](https://developer-docs.amazon.com/sp-api/reference/createreport) operation. The dataStartTime and dataEndTime values must correspond to valid first and last days in the specified reportPeriod. For example, dataStartTime must be a Sunday and dataEndTime must be a Saturday when reportPeriod=WEEK. The maximum allowed date range is 30 days. When false, or if all is not included in reportOptions, the content of the report depends on the value of pendingInvoices. Example: "reportOptions": {"ReportOption=All": "true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#flat-file-vat-invoice-data-report-vidr>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_GST_MTR_B2B_CUSTOM.md

# `GET_GST_MTR_B2B_CUSTOM`

> **分类**：15. Tax Reports  
> **说明**：Custom GST MTR B2B  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-gst-merchant-tax-report-b2b)（章节：**On Demand GST Merchant Tax Report B2B**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Store availability**：IN
- **要点**：Provides detailed information about sales, refunds, and cancellations from Amazon Business invoices issued within a date range that you specify.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-gst-merchant-tax-report-b2b>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_GST_MTR_B2B_CUSTOM",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_GST_MTR_B2B_CUSTOM",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_GST_MTR_B2C_CUSTOM.md

# `GET_GST_MTR_B2C_CUSTOM`

> **分类**：15. Tax Reports  
> **说明**：Custom GST MTR B2C  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-gst-merchant-tax-report-b2c)（章节：**On Demand GST Merchant Tax Report B2C**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Store availability**：IN
- **要点**：Provides detailed information about sales, refunds, and cancellations from consumer invoices issued. The report only provides data for the last 45 days.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-gst-merchant-tax-report-b2c>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_GST_MTR_B2C_CUSTOM",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_GST_MTR_B2C_CUSTOM",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_GST_STR_ADHOC.md

# `GET_GST_STR_ADHOC`

> **分类**：15. Tax Reports  
> **说明**：GST Adhoc report  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-stock-transfer-report)（章节：**On Demand Stock Transfer Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file
- **Store availability**：IN
- **User type**：FBA sellers who use Amazon systems to make inventory movements from Amazon Fulfillment Centers (FC removals or FC to FC transfers). Required for filing tax returns by sellers and vendors.
- **要点**：Provides transaction level information like invoice value, invoice number, tax rate, and Goods and Services Tax Identification Numbers (GSTINs). All supplies that go through interstate movement transactions are considered taxable supplies. These supplies are liable for a Goods and Services Tax (GST) at the origin location and GST credit at the destination location.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#on-demand-stock-transfer-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_GST_STR_ADHOC",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_GST_STR_ADHOC",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_LEDGER_DETAIL_VIEW_DATA.md

# `GET_LEDGER_DETAIL_VIEW_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Inventory ledger detail  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---detailed-view)（章节：**Inventory Ledger Report - Detailed View**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Use the Inventory Ledger Report - Detailed View to analyze your inventory movements to and from Amazon fulfillment centers, including products that are sold, returned, removed/disposed, damaged, lost, and found. You can view all historical movements of your inventory for 18 months in this report. This report accepts the following reportOptions values: You can pass multiple parameters to ReportOptions as shown in the following example: "reportOptions":{"eventType":"Adjustments", "FNSKU" : "X00001", "MSKU" : "Test"}
- **reportOptions（摘录）**：
  - eventType: Filters report data for a particular warehouse event. Default is the empty string, which returns all events. Other possible values are as follows: Adjustments CustomerReturns Receipts Shipments VendorReturns WhseTransfers Examples: "reportOptions":{"eventType":""} "reportOptions":{"eventType":"Adjustments"}
  - FNSKU: Include FNSKU value to view report data for that particular FNSKU.
  - MSKU: Include MSKU value to view report data for all active FNSKU mappings of that MSKU.
  - ASIN: Include ASIN value to view report data for all active FNSKU mappings of that ASIN.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---detailed-view>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_LEDGER_DETAIL_VIEW_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_LEDGER_DETAIL_VIEW_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_LEDGER_SUMMARY_VIEW_DATA.md

# `GET_LEDGER_SUMMARY_VIEW_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Inventory ledger summary  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#inventory-ledger-report---summary-view)（章节：**Inventory Ledger Report - Summary View**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：The Inventory Ledger Report is like a bank statement of your inventory. It provides end-to-end inventory reconciliation capability by showing starting inventory balance, received inventory, customer orders, customer returns, adjustments, removals and ending balance. This report accepts the following reportOptions values: Report behaviors:
- **reportOptions（摘录）**：
  - aggregateByLocation: Include Country to aggregate Summary View data by country. Include FC to aggregate Summary View data by fulfillment center. Default: COUNTRY. Example: "reportOptions":{"aggregateByLocation":"COUNTRY"}
  - aggregatedByTimePeriod: Specify the time period to aggregate Summary View data accordingly (for example, MONTHLY, WEEKLY, DAILY, etc.). Default: MONTHLY. Example: "reportOptions":{"aggregatedByTimePeriod":"MONTHLY"}
  - FNSKU: Include FNSKU value to view report data for that particular FNSKU.
  - MSKU: Include MSKU value to view report data for all active FNSKU mappings of that MSKU.
  - ASIN: Include ASIN value to view report data for all active FNSKU mappings of that ASIN.

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

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_CANCELLED_LISTINGS_DATA.md

# `GET_MERCHANT_CANCELLED_LISTINGS_DATA`

> **分类**：7. Inventory Reports  
> **说明**：Cancelled listings  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_CANCELLED_LISTINGS_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：A canceled listings report. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - Custom: A Boolean value that indicates whether a custom report is returned. Default: false. Example: "reportOptions":{"custom":"true"}.
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_CANCELLED_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_CANCELLED_LISTINGS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_ALL_DATA.md

# `GET_MERCHANT_LISTINGS_ALL_DATA`

> **分类**：7. Inventory Reports  
> **说明**：All active listings  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_ALL_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：A detailed all listings report. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - Custom: A Boolean value that indicates whether a custom report is returned. Default: false. Example: "reportOptions":{"custom":"true"}.
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_DATA.md

# `GET_MERCHANT_LISTINGS_DATA`

> **分类**：7. Inventory Reports  
> **说明**：Active listings (standard)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：A detailed all listings report. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

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

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT.md

# `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT`

> **分类**：7. Inventory Reports  
> **说明**：Listings (backwards compatible)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：An open listings report. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - Custom: A Boolean value that indicates whether a custom report is returned. Default: false. Example: "reportOptions":{"custom":"true"}.
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_DATA_LITE.md

# `GET_MERCHANT_LISTINGS_DATA_LITE`

> **分类**：7. Inventory Reports  
> **说明**：Listings (lite version)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_DATA_LITE**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：Contains only the SKU, ASIN, Price, and Quantity fields for items that have a quantity greater than zero. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_LITE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_LITE",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_DATA_LITER.md

# `GET_MERCHANT_LISTINGS_DATA_LITER`

> **分类**：7. Inventory Reports  
> **说明**：Listings (lighter version)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_DATA_LITER**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：An active listings report that contains only the SKU and Quantity fields for items that have a quantity greater than zero. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_LITER",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_DATA_LITER",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANT_LISTINGS_INACTIVE_DATA.md

# `GET_MERCHANT_LISTINGS_INACTIVE_DATA`

> **分类**：7. Inventory Reports  
> **说明**：Inactive listings  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANT_LISTINGS_INACTIVE_DATA**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：A detailed inactive listings report. 📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_INACTIVE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_INACTIVE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MERCHANTS_LISTINGS_FYP_REPORT.md

# `GET_MERCHANTS_LISTINGS_FYP_REPORT`

> **分类**：7. Inventory Reports  
> **说明**：Fix Your Products report  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MERCHANTS_LISTINGS_FYP_REPORT**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：Tab-delimited flat file
- **要点**：📘NoteYou can only specify one marketplace per report. When requesting a report with multiple marketplaceIds, only the first marketplaceId in the list will be accepted. Contains suppressed listings, the reason each listing is suppressed, and instructions for removing each suppression. This report accepts the following reportOptions values:
- **reportOptions（摘录）**：
  - preferredReportDocumentLocale: A string value that specifies the preferred locale for report column headers. Accepts standard locale codes in the POSIX-style locale format. Example: "reportOptions":{"preferredReportDocumentLocale":"en_US"}. 📘NoteReports are not cached by locale. Requesting the same report within the cache period (between one and six hours depending on the number of entries) may return headers in a different locale than requested.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MERCHANTS_LISTINGS_FYP_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MERCHANTS_LISTINGS_FYP_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_MFN_PANEU_OFFER_STATUS.md

# `GET_MFN_PANEU_OFFER_STATUS`

> **分类**：7. Inventory Reports  
> **说明**：MFN Pan-EU offer status  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_MFN_PANEU_OFFER_STATUS**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Marketplace availability**：Spain, UK, France, Germany, and Italy marketplaces.
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains eligibility information for the Pan-European FBA Program for each of the seller's self-fulfilled listings. Self-fulfilled listings are not allowed in the Pan-European FBA program, and this report can help sellers determine whether to convert any of their self-fulfilled listings to Amazon-fulfilled listings in order to enroll them in the program. For more information, refer to Seller Central Help.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_MFN_PANEU_OFFER_STATUS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_MFN_PANEU_OFFER_STATUS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_ORDER_REPORT_DATA_INVOICING.md

# `GET_ORDER_REPORT_DATA_INVOICING`

> **分类**：9. Order Reports  
> **说明**：Order data for invoicing  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-invoicing)（章节：**Scheduled XML Order Report (Invoicing)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Marketplace availability**：EU
- **Requested/scheduled**：Scheduled
- **Report output type**：XML
- **要点**：This report can be used to generate tax invoices in the EU region. The report includes all new orders since the last report. For new reports, it contains order reports from the past 38 days. You can only schedule one GET_ORDER_REPORT_DATA_INVOICING or GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-invoicing>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_INVOICING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_ORDER_REPORT_DATA_SHIPPING.md

# `GET_ORDER_REPORT_DATA_SHIPPING`

> **分类**：9. Order Reports  
> **说明**：Order shipping data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-shipping)（章节：**Scheduled XML Order Report (Shipping)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Requested/scheduled**：Scheduled
- **Report output type**：XML
- **要点**：This report is for shipping seller fulfilled orders to customers. The report includes all new orders since the last report. For new reports, it contains order reports from the past 38 days. You can only schedule one GET_ORDER_REPORT_DATA_SHIPPING or GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-shipping>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_SHIPPING",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_ORDER_REPORT_DATA_TAX.md

# `GET_ORDER_REPORT_DATA_TAX`

> **分类**：9. Order Reports  
> **说明**：Order tax data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-tax)（章节：**Scheduled XML Order Report (Tax)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Order Fulfillment Channel**：MFN
- **Availability**：Seller Central sellers
- **Marketplace availability**：NA
- **Requested/scheduled**：Scheduled
- **Report output type**：XML
- **要点**：This report is for calculating and remitting taxes in the NA region. The report includes all new orders since the last report. For new reports, it contains order reports from the past 38 days. You can only schedule one GET_ORDER_REPORT_DATA_TAX or GET_FLAT_FILE_ORDER_REPORT_DATA_TAX report at a time. If you have one of these reports scheduled and you schedule a new report, the existing report is canceled.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#scheduled-xml-order-report-tax>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_TAX",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_ORDER_REPORT_DATA_TAX",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_PAN_EU_OFFER_STATUS.md

# `GET_PAN_EU_OFFER_STATUS`

> **分类**：7. Inventory Reports  
> **说明**：Pan-European offer status  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_PAN_EU_OFFER_STATUS**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Marketplace availability**：Spain, UK, France, Germany, and Italy marketplaces.
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted), [Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **要点**：Contains enrollment status and eligibility information for the Pan-European FBA program for each of the seller's Amazon-fulfilled listings. For more information, refer to Seller Central Help.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_PAN_EU_OFFER_STATUS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_PAN_EU_OFFER_STATUS",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_PENDING_ORDERS_DATA.md

# `GET_PENDING_ORDERS_DATA`

> **分类**：9. Order Reports  
> **说明**：Pending orders  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-pending-orders-report)（章节：**XML Pending Orders Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：Scheduled
- **Report output type**：XML
- **要点**：Contains all pending orders.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-pending-orders-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_PENDING_ORDERS_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_PROMOTION_PERFORMANCE_REPORT.md

# `GET_PROMOTION_PERFORMANCE_REPORT`

> **分类**：11. Performance Reports  
> **说明**：Promotion performance  
> **可用范围**：Both

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`promotionReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#promotions-performance-report)（章节：**Promotions Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights), [Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers who have the Selling Partner Insights Selling Partner API role and vendors who have the Brand Analytics Selling Partner API role who are also registered in Amazon's Brand Registry.
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#promotions-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_PROMOTION_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_REFERRAL_FEE_PREVIEW_REPORT.md

# `GET_REFERRAL_FEE_PREVIEW_REPORT`

> **分类**：7. Inventory Reports  
> **说明**：Referral fee preview  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Inventory Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory)（章节：**GET_REFERRAL_FEE_PREVIEW_REPORT**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains the seller's open listings as well as the price and estimated referral fees for each SKU. 📘NoteThe information in this report may be up to 24 hours old. Do not request a report more than once per 24-hour period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_REFERRAL_FEE_PREVIEW_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_REFERRAL_FEE_PREVIEW_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_REMOTE_FULFILLMENT_ELIGIBILITY.md

# `GET_REMOTE_FULFILLMENT_ELIGIBILITY`

> **分类**：6.2 FBA Inventory  
> **说明**：Remote fulfillment eligibility  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#remote-fulfillment-eligibility)（章节：**Remote Fulfillment Eligibility**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking)
- **要点**：Contains all of a seller's US Fulfillment by Amazon offers, including whether they qualify for the North America Remote Fulfillment (NARF) program. 📘Note:Recheck this report regularly, since ASIN eligibility can change. This report can take up to 24 hours to generate.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#remote-fulfillment-eligibility>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_REMOTE_FULFILLMENT_ELIGIBILITY",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_REMOTE_FULFILLMENT_ELIGIBILITY",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_RESERVED_INVENTORY_DATA.md

# `GET_RESERVED_INVENTORY_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Reserved inventory data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-reserved-inventory-report)（章节：**FBA Reserved Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Provides data about the number of reserved units in a seller's inventory. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-reserved-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_RESERVED_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_RESERVED_INVENTORY_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT.md

# `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT`

> **分类**：6.2 FBA Inventory  
> **说明**：FBA restock recommendations  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#restock-inventory-report)（章节：**Restock Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Provides recommendations on products to restock, suggested order quantities, and reorder dates. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#restock-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_SALES_AND_TRAFFIC_REPORT.md

# `GET_SALES_AND_TRAFFIC_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Sales and traffic by date  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`sellerSalesAndTrafficReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#sales-and-traffic-business-report)（章节：**Sales and Traffic Business Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#sales-and-traffic-business-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_SELLER_FEEDBACK_DATA.md

# `GET_SELLER_FEEDBACK_DATA`

> **分类**：11. Performance Reports  
> **说明**：Customer feedback  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#flat-file-feedback-report)（章节：**Flat File Feedback Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **要点**：Contains negative and neutral feedback (one to three stars) from buyers who rated the seller's performance.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#flat-file-feedback-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_SELLER_FEEDBACK_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_SELLER_FEEDBACK_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_STRANDED_INVENTORY_LOADER_DATA.md

# `GET_STRANDED_INVENTORY_LOADER_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Stranded inventory (bulk format)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-bulk-fix-stranded-inventory-report)（章节：**FBA Bulk Fix Stranded Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains a list of stranded inventory. Update the listing information in this report file and then submit the file using the Flat File Inventory Loader Feed (POST_FLAT_FILE_INVLOADER_DATA) of the Feeds API. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-bulk-fix-stranded-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_STRANDED_INVENTORY_LOADER_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_STRANDED_INVENTORY_LOADER_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_STRANDED_INVENTORY_UI_DATA.md

# `GET_STRANDED_INVENTORY_UI_DATA`

> **分类**：6.2 FBA Inventory  
> **说明**：Stranded inventory (UI format)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Fulfillment by Amazon (FBA) Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-stranded-inventory-report)（章节：**FBA Stranded Inventory Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Availability**：FBA sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Tab-delimited flat file
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **要点**：Contains a breakdown of inventory in stranded status, including recommended actions. Content updated in near real-time.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-stranded-inventory-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_STRANDED_INVENTORY_UI_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_STRANDED_INVENTORY_UI_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_V1_SELLER_PERFORMANCE_REPORT.md

# `GET_V1_SELLER_PERFORMANCE_REPORT`

> **分类**：11. Performance Reports  
> **说明**：Seller performance v1  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#xml-customer-metrics-report)（章节：**XML Customer Metrics Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：XML
- **要点**：Contains select, individual performance metrics data from the Seller Central dashboard.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#xml-customer-metrics-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_V1_SELLER_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_V1_SELLER_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_V2_SELLER_PERFORMANCE_REPORT.md

# `GET_V2_SELLER_PERFORMANCE_REPORT`

> **分类**：11. Performance Reports  
> **说明**：Seller performance v2  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#seller-performance-report)（章节：**Seller Performance Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights)
- **Availability**：Sellers
- **Requested/scheduled**：This report can only be requested.
- **要点**：Contains the individual performance metrics data from the Seller Central Account Health dashboard.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#seller-performance-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_V2_SELLER_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_V2_SELLER_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE.md

# `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`

> **分类**：14. Settlement/Payments Reports  
> **说明**：Settlement report v2 (flat file)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Settlement Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#flat-file-settlement-report)（章节：**Flat File Settlement Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment)
- **Availability**：Sellers
- **Report output type**：Tab-delimited flat file
- **要点**：This report is deprecated.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#flat-file-settlement-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2.md

# `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2`

> **分类**：14. Settlement/Payments Reports  
> **说明**：Enhanced settlement report  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Settlement Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#flat-file-v2-settlement-report)（章节：**Flat File V2 Settlement Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **Availability**：Seller Central sellers
- **Report output type**：Tab-delimited flat file
- **要点**：A settlement report. This report replaces the Flat File Settlement Report and XML Settlement Report. Price columns are condensed into three general-purpose columns: The amount-type and amount-description columns contain the type of charge or fee you have incurred, and indicates whether different fees are related to a common type. Amount values always populate in a single amount column, so there's no need to parse the rows to find a number, even if new fees or transaction types are introduced in the future. Additionally, amounts are displayed in local currency formats (for example, 95,00 for EU instead of 95.00). For Seller Central sellers only.

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

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_V2_SETTLEMENT_REPORT_DATA_XML.md

# `GET_V2_SETTLEMENT_REPORT_DATA_XML`

> **分类**：14. Settlement/Payments Reports  
> **说明**：Settlement report v2 (XML)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Settlement Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#xml-settlement-report)（章节：**XML Settlement Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Finance and Accounting](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#finance-and-accounting)
- **Availability**：Seller Central sellers
- **Report output type**：XML
- **要点**：This report is deprecated.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement#xml-settlement-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_XML",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_XML",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_VAT_TRANSACTION_DATA.md

# `GET_VAT_TRANSACTION_DATA`

> **分类**：15. Tax Reports  
> **说明**：VAT transaction data  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-transactions-report)（章节：**Amazon VAT Transactions Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Requested/scheduled**：This report can only be requested and is available from the third of each month. If you request the report before the third of the month, then Amazon returns a status of FATAL.
- **Report output type**：Tab-delimited flat file
- **Store availability**：Germany, Spain, Italy, France, and UK.
- **要点**：📘NoteThis reports ignores the marketplaceId parameter and will return data for all available stores. Provides detailed information for sales, returns, refunds, cross border inbound, and cross border fulfillment center transfers.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-transactions-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_VAT_TRANSACTION_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_VAT_TRANSACTION_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_VENDOR_FORECASTING_REPORT.md

# `GET_VENDOR_FORECASTING_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Vendor forecasting data  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorForecastingReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-forecasting-report)（章节：**Vendor Forecasting Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-forecasting-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_FORECASTING_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_INVENTORY_REPORT.md

# `GET_VENDOR_INVENTORY_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Vendor inventory report  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorInventoryReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-inventory-report)（章节：**Vendor Inventory Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-inventory-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_INVENTORY_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT.md

# `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Vendor product margins  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorNetPureProductMarginReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#net-pure-product-margin-report)（章节：**Net Pure Product Margin Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#net-pure-product-margin-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_REAL_TIME_INVENTORY_REPORT.md

# `GET_VENDOR_REAL_TIME_INVENTORY_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Real-time vendor inventory  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorRealTimeInventoryReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-inventory-report)（章节：**Rapid Retail Analytics Inventory Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-inventory-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_INVENTORY_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_REAL_TIME_SALES_REPORT.md

# `GET_VENDOR_REAL_TIME_SALES_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Real-time vendor sales  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorRealTimeSalesReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-sales-report)（章节：**Rapid Retail Analytics Sales Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-sales-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_SALES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_REAL_TIME_TRAFFIC_REPORT.md

# `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Real-time vendor traffic  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorRealTimeTrafficReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-traffic-report)（章节：**Rapid Retail Analytics Traffic Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#rapid-retail-analytics-traffic-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_TRAFFIC_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_SALES_REPORT.md

# `GET_VENDOR_SALES_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Vendor sales report  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorSalesReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-sales-report)（章节：**Vendor Sales Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-sales-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_SALES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_VENDOR_TRAFFIC_REPORT.md

# `GET_VENDOR_TRAFFIC_REPORT`

> **分类**：2. Analytics Reports  
> **说明**：Vendor traffic report  
> **可用范围**：Vendor only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`vendorTrafficReport.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Analytics Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-traffic-report)（章节：**Vendor Traffic Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-traffic-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_VENDOR_TRAFFIC_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL.md

# `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL`

> **分类**：9. Order Reports  
> **说明**：All orders (XML, by update)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-orders-by-last-update-report)（章节：**XML Orders By Last Update Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Order Fulfillment Channel**：MFN and FBA
- **Availability**：Sellers
- **Requested/scheduled**：Requested
- **Report output type**：XML
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **要点**：Contains all orders updated in the specified period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-orders-by-last-update-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL.md

# `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`

> **分类**：9. Order Reports  
> **说明**：All orders (XML, by date)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Order Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-orders-by-order-date-report)（章节：**XML Orders By Order Date Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Order Fulfillment Channel**：MFN and FBA
- **Availability**：Sellers
- **Requested/scheduled**：Requested
- **Report output type**：XML
- **Roles**：[Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Amazon Fulfillment](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#amazon-fulfillment), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **要点**：Contains all orders that were placed in the specified period.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#xml-orders-by-order-date-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_BROWSE_TREE_DATA.md

# `GET_XML_BROWSE_TREE_DATA`

> **分类**：4. Browse Tree Reports  
> **说明**：Browse tree hierarchy (XML format)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Browse Tree Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree#browse-tree-report)（章节：**Browse Tree Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Availability**：Sellers
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：XML
- **Schema**：[BrowseTreeReport.xsd](https://images-na.ssl-images-amazon.com/images/G/01/mwsportal/doc/en_US/Reports/XSDs/BrowseTreeReport.xsd)
- **要点**：Contains browse tree hierarchy information and node refinement information for the Amazon retail website in any marketplace. This report accepts the following reportOptions values: 📘Note:The seller must be registered in any marketplace that you specify using the MarketplaceId value. Also, your request must be sent to an endpoint that corresponds to the MarketplaceId that you specify. Otherwise, the service returns an error. 📘Note:If RootNodesOnly and BrowseNodeId are both included in the reportOptions parameter, RootNodesOnly takes precedence. 📘Note:Amazon recommends that you do not include the MarketplaceIds parameter with calls to the createReport operation that request the Browse Tree Report. If there is ever a conflict between a MarketplaceIds parameter value and the MarketplaceId value of the reportOptions parameter, the MarketplaceId value takes precedence.
- **reportOptions（摘录）**：
  - MarketplaceId – Specifies the marketplace from which you want browse tree information. If MarketplaceId is not included in the reportOptions parameter, the report contains browse tree information from the seller's default marketplace.
  - RootNodesOnly - A string value that must be either true or false. When you set RootNodesOnly to true, the report contains only the root nodes from the marketplace that you specify using MarketplaceId (or from your default marketplace if you do not specify MarketplaceId). When you set RootNodesOnly to false, or if you do not include RootNodesOnly in the ReportOptions parameter, the value of BrowseNodeId determines the content of the report.
  - BrowseNodeId – Specifies the top node of the browse tree hierarchy in the report. If BrowseNodeId is not included in the ReportOptions parameter, and if RootNodesOnly is false or is not included in the ReportOptions parameter, then the report contains the entire browse node hierarchy from the marketplace specified using MarketplaceId (or from the seller's default marketplace, if MarketplaceId is not specified). Note that if you include an invalid BrowseNodeId in your request, the service returns a report that contains no data.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree#browse-tree-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_BROWSE_TREE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_BROWSE_TREE_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_MFN_PRIME_RETURNS_REPORT.md

# `GET_XML_MFN_PRIME_RETURNS_REPORT`

> **分类**：13. Returns Reports  
> **说明**：MFN Prime returns (XML)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-prime-returns-report-by-return-date)（章节：**XML Prime Returns Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Pricing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#pricing), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：XML
- **要点**：Contains detailed Seller Fulfilled Prime returns information, including return request date, RMA ID, label details, ASIN, and return reason code. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-prime-returns-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_MFN_PRIME_RETURNS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_MFN_PRIME_RETURNS_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT.md

# `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT`

> **分类**：13. Returns Reports  
> **说明**：MFN SKU return attributes (XML)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-return-attributes-report-by-return-date)（章节：**XML Return Attributes Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：XML
- **要点**：Contains detailed return attribute information by SKU, including prepaid label eligibility and returnless refund eligibility. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-return-attributes-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_RETURNS_DATA_BY_RETURN_DATE.md

# `GET_XML_RETURNS_DATA_BY_RETURN_DATE`

> **分类**：13. Returns Reports  
> **说明**：Returns by date (XML)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Returns Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-returns-report-by-return-date)（章节：**XML Returns Report by Return Date**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Inventory and Order Tracking](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#inventory-and-order-tracking), [Direct to Consumer Shipping (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#direct-to-consumer-shipping-restricted)
- **Requested/scheduled**：This report can be requested or scheduled.
- **Report output type**：XML
- **要点**：Contains detailed returns information, including return request date, RMA ID, label details, ASIN, and return reason code. You can request up to 60 days of data in a single report.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns#xml-returns-report-by-return-date>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_RETURNS_DATA_BY_RETURN_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_RETURNS_DATA_BY_RETURN_DATE",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GET_XML_VAT_INVOICE_DATA_REPORT.md

# `GET_XML_VAT_INVOICE_DATA_REPORT`

> **分类**：8. Invoice Reports  
> **说明**：VAT invoice data (XML)  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Invoice Data Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#xml-vat-invoice-data-report-vidr)（章节：**XML VAT Invoice Data Report (VIDR)**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Availability**：Sellers who have enrolled in Amazon's VAT Calculation Service and have opted to upload their own invoices. This report is for both Fulfillment by Amazon and seller-fulfilled orders.
- **Report output type**：XML
- **Default**："pendingInvoices" : "true".
- **要点**：Provides all the information required to generate a VAT invoice for each shipment, return, or refund for a seller's order. A shipment is included in this report immediately after it is dispatched. Amazon recommends scheduling this report at least twice a day. This report accepts the following reportOptions values: For information on how to use this report, refer to [VAT Calculation Service](https://developer-docs.amazon.com/sp-api/docs/vat-calculation-service-guide).
- **reportOptions（摘录）**：
  - pendingInvoices – A Boolean value. When true, the report contains only shipments for which invoices and credit notes are pending. This report does not contain shipments for which invoices have already been uploaded successfully. Includes shipments for orders that were placed within the previous 90 days. When false, or if pendingInvoices is not included in reportOptions, the content of the report depends on the value of all. Example: "reportOptions":{"pendingInvoices":"true"}
  - all – A Boolean value. When true, the report contains shipments for orders that were placed within the date range that you specify. Includes shipments of all possible invoice statuses. You must specify the startDate and endDate parameters of the [createReport](https://developer-docs.amazon.com/sp-api/reference/createreport) operation. The dataStartTime and dataEndTime values must correspond to valid first and last days in the specified reportPeriod. For example, dataStartTime must be a Sunday and dataEndTime must be a Saturday when reportPeriod=WEEK. The maximum allowed date range is 30 days. When false, or if all is not included in reportOptions, the content of the report depends on the value of pendingInvoices. Example: "reportOptions": {"ReportOption=All": "true"}

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-invoice-data#xml-vat-invoice-data-report-vidr>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GET_XML_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GET_XML_VAT_INVOICE_DATA_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GST_MTR_B2B.md

# `GST_MTR_B2B`

> **分类**：15. Tax Reports  
> **说明**：GST Monthly Tax Report B2B  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-business)（章节：**GST Merchant Tax Report - Business to Business**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Requested/scheduled**：This report can only be scheduled.
- **Report output type**：Comma-separated flat file
- **Store availability**：IN
- **要点**：Provides detailed information about sales, refunds, and cancellations from Amazon Business invoices issued within a date range that you specify.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-business>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GST_MTR_B2B",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GST_MTR_B2B",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GST_MTR_B2C.md

# `GST_MTR_B2C`

> **分类**：15. Tax Reports  
> **说明**：GST Monthly Tax Report B2C  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-customer)（章节：**GST Merchant Tax Report - Business to Customer**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Requested/scheduled**：This report can only be scheduled.
- **Report output type**：Comma-separated flat file
- **Store availability**：IN
- **要点**：Provides detailed information about sales, refunds, and cancellations from consumer invoices issued within a date range that you specify.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-tax-report---business-to-customer>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GST_MTR_B2C",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GST_MTR_B2C",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/GST_MTR_STOCK_TRANSFER_REPORT.md

# `GST_MTR_STOCK_TRANSFER_REPORT`

> **分类**：15. Tax Reports  
> **说明**：GST stock transfer report  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-stock-transfer-report)（章节：**GST Merchant Stock Transfer Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准
- **Role**：[Tax Remittance (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-remittance-restricted)
- **Report output type**：Comma-separated flat file
- **Store availability**：IN
- **要点**：Provides details on inventory movements from Amazon Fulfillment Centers (FC removals or FC to FC transfers). The report contains transaction level details required for accounting and GST tax filing.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#gst-merchant-stock-transfer-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "GST_MTR_STOCK_TRANSFER_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "GST_MTR_STOCK_TRANSFER_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/types/MARKETPLACE_ASIN_PAGE_VIEW_METRICS.md

# `MARKETPLACE_ASIN_PAGE_VIEW_METRICS`

> **分类**：12. Regulatory Compliance Reports  
> **说明**：ASIN page view metrics  
> **可用范围**：Seller only

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：`marketplaceAsinPageViewMetrics.md`（见本文对应归档章节）
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Regulatory Compliance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#marketplace-asin-page-view-metrics)（章节：**Marketplace ASIN Page View Metrics**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Selling Partner Insights](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#selling-partner-insights)
- **Availability**：Sellers
- **Marketplace availability**：DE, FR, IT, ES, NL, PL, SE, BE (EU-8), UK, and IE.
- **Requested/scheduled**：This report can be requested or scheduled.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-regulatory-compliance#marketplace-asin-page-view-metrics>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "MARKETPLACE_ASIN_PAGE_VIEW_METRICS",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

本 reference 的 CreateReport 参数说明。

## 另见

- `references/report-types.md`

## Archived reference: report-requests/types/README.md

# 按 `reportType` 全覆盖 — 请求说明专页

本目录为 `references/report-types.md` 中**每一个**报告枚举提供一页说明：

- 标注是否在 Amazon [`schemas/reports`](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 有 JSON 结果 Schema，并链到 `references/report-requests/` 下对应专页。
- 无独立 JSON 的类型：给出 **CreateReport 最小请求体** 与官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 入口。
- 每页顶部另有 **「官方说明」或「官方索引（Report type values）」**：从亚马逊各子类文档自动摘录；其中在 `report-requests/` 下**已有 GitHub Schema 专页**（`*.md` 与 `schemas/reports/*.json` 对应）的类型，仅保留 **Schema 链、Amazon 锚点、权限/站点类字段**，避免与专页中的 Schema 摘要、`reportOptions` 表重复。其余 Flat File 类型仍为完整「官方说明」。  
  更新摘录：将 15 个子页 HTML 放入 `references/_spapi_docs_cache/`，运行 `merge_report_type_values_from_cache` 操作（依赖见该脚本注释）。

**共计**：109 个 `reportType`。

## 索引

| reportType | 分类（report-types.md） | 类型 | 专页 |
|------------|-------------------------|------|------|
| `FEE_DISCOUNTS_REPORT` | 1. Amazon Business Reports | Flat/XML（文档） | `FEE_DISCOUNTS_REPORT.md`（见本文对应归档章节） |
| `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT.md`（见本文对应归档章节） |
| `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT.md`（见本文对应归档章节） |
| `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_REAL_TIME_INVENTORY_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_REAL_TIME_SALES_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_REAL_TIME_SALES_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_SALES_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_SALES_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_TRAFFIC_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_TRAFFIC_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_FORECASTING_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_FORECASTING_REPORT.md`（见本文对应归档章节） |
| `GET_VENDOR_INVENTORY_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_VENDOR_INVENTORY_REPORT.md`（见本文对应归档章节） |
| `GET_SALES_AND_TRAFFIC_REPORT` | 2. Analytics Reports | JSON Schema 专页 | `GET_SALES_AND_TRAFFIC_REPORT.md`（见本文对应归档章节） |
| `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` | 3. B2B Product Opportunities | JSON Schema 专页 | `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU.md`（见本文对应归档章节） |
| `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` | 3. B2B Product Opportunities | JSON Schema 专页 | `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON.md`（见本文对应归档章节） |
| `GET_XML_BROWSE_TREE_DATA` | 4. Browse Tree Reports | Flat/XML（文档） | `GET_XML_BROWSE_TREE_DATA.md`（见本文对应归档章节） |
| `GET_EASYSHIP_DOCUMENTS` | 5. Easy Ship Reports | Flat/XML（文档） | `GET_EASYSHIP_DOCUMENTS.md`（见本文对应归档章节） |
| `GET_EASYSHIP_PICKEDUP` | 5. Easy Ship Reports | Flat/XML（文档） | `GET_EASYSHIP_PICKEDUP.md`（见本文对应归档章节） |
| `GET_EASYSHIP_WAITING_FOR_PICKUP` | 5. Easy Ship Reports | Flat/XML（文档） | `GET_EASYSHIP_WAITING_FOR_PICKUP.md`（见本文对应归档章节） |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL.md`（见本文对应归档章节） |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING.md`（见本文对应归档章节） |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA` | 6.1 FBA Shipments | Flat/XML（文档） | `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA.md`（见本文对应归档章节） |
| `GET_AFN_INVENTORY_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_AFN_INVENTORY_DATA.md`（见本文对应归档章节） |
| `GET_AFN_INVENTORY_DATA_BY_COUNTRY` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_AFN_INVENTORY_DATA_BY_COUNTRY.md`（见本文对应归档章节） |
| `GET_LEDGER_SUMMARY_VIEW_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_LEDGER_SUMMARY_VIEW_DATA.md`（见本文对应归档章节） |
| `GET_LEDGER_DETAIL_VIEW_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_LEDGER_DETAIL_VIEW_DATA.md`（见本文对应归档章节） |
| `GET_RESERVED_INVENTORY_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_RESERVED_INVENTORY_DATA.md`（见本文对应归档章节） |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA.md`（见本文对应归档章节） |
| `GET_FBA_MYI_ALL_INVENTORY_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_FBA_MYI_ALL_INVENTORY_DATA.md`（见本文对应归档章节） |
| `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT.md`（见本文对应归档章节） |
| `GET_STRANDED_INVENTORY_UI_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_STRANDED_INVENTORY_UI_DATA.md`（见本文对应归档章节） |
| `GET_STRANDED_INVENTORY_LOADER_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_STRANDED_INVENTORY_LOADER_DATA.md`（见本文对应归档章节） |
| `GET_FBA_INVENTORY_PLANNING_DATA` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_FBA_INVENTORY_PLANNING_DATA.md`（见本文对应归档章节） |
| `GET_REMOTE_FULFILLMENT_ELIGIBILITY` | 6.2 FBA Inventory | Flat/XML（文档） | `GET_REMOTE_FULFILLMENT_ELIGIBILITY.md`（见本文对应归档章节） |
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | 6.3 FBA Fees & Charges | Flat/XML（文档） | `GET_FBA_STORAGE_FEE_CHARGES_DATA.md`（见本文对应归档章节） |
| `GET_FBA_OVERAGE_FEE_CHARGES_DATA` | 6.3 FBA Fees & Charges | Flat/XML（文档） | `GET_FBA_OVERAGE_FEE_CHARGES_DATA.md`（见本文对应归档章节） |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | 6.3 FBA Fees & Charges | Flat/XML（文档） | `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA` | 6.3 FBA Fees & Charges | Flat/XML（文档） | `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | 6.4 FBA Returns & Reimbursements | Flat/XML（文档） | `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA` | 6.4 FBA Returns & Reimbursements | Flat/XML（文档） | `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA.md`（见本文对应归档章节） |
| `GET_FBA_REIMBURSEMENTS_DATA` | 6.4 FBA Returns & Reimbursements | Flat/XML（文档） | `GET_FBA_REIMBURSEMENTS_DATA.md`（见本文对应归档章节） |
| `GET_FBA_RECOMMENDED_REMOVAL_DATA` | 6.5 FBA Removals | Flat/XML（文档） | `GET_FBA_RECOMMENDED_REMOVAL_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | 6.5 FBA Removals | Flat/XML（文档） | `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | 6.5 FBA Removals | Flat/XML（文档） | `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA.md`（见本文对应归档章节） |
| `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA` | 6.6 FBA Compliance | Flat/XML（文档） | `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | 7. Inventory Reports | Flat/XML（文档） | `GET_FLAT_FILE_OPEN_LISTINGS_DATA.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_ALL_DATA` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_ALL_DATA.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_DATA` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_DATA.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_INACTIVE_DATA.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_DATA_LITE` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_DATA_LITE.md`（见本文对应归档章节） |
| `GET_MERCHANT_LISTINGS_DATA_LITER` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_LISTINGS_DATA_LITER.md`（见本文对应归档章节） |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANT_CANCELLED_LISTINGS_DATA.md`（见本文对应归档章节） |
| `GET_MERCHANTS_LISTINGS_FYP_REPORT` | 7. Inventory Reports | Flat/XML（文档） | `GET_MERCHANTS_LISTINGS_FYP_REPORT.md`（见本文对应归档章节） |
| `GET_PAN_EU_OFFER_STATUS` | 7. Inventory Reports | Flat/XML（文档） | `GET_PAN_EU_OFFER_STATUS.md`（见本文对应归档章节） |
| `GET_MFN_PANEU_OFFER_STATUS` | 7. Inventory Reports | Flat/XML（文档） | `GET_MFN_PANEU_OFFER_STATUS.md`（见本文对应归档章节） |
| `GET_REFERRAL_FEE_PREVIEW_REPORT` | 7. Inventory Reports | Flat/XML（文档） | `GET_REFERRAL_FEE_PREVIEW_REPORT.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT` | 8. Invoice Reports | Flat/XML（文档） | `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT.md`（见本文对应归档章节） |
| `GET_XML_VAT_INVOICE_DATA_REPORT` | 8. Invoice Reports | Flat/XML（文档） | `GET_XML_VAT_INVOICE_DATA_REPORT.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING.md`（见本文对应归档章节） |
| `GET_ORDER_REPORT_DATA_INVOICING` | 9. Order Reports | Flat/XML（文档） | `GET_ORDER_REPORT_DATA_INVOICING.md`（见本文对应归档章节） |
| `GET_ORDER_REPORT_DATA_TAX` | 9. Order Reports | Flat/XML（文档） | `GET_ORDER_REPORT_DATA_TAX.md`（见本文对应归档章节） |
| `GET_ORDER_REPORT_DATA_SHIPPING` | 9. Order Reports | Flat/XML（文档） | `GET_ORDER_REPORT_DATA_SHIPPING.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE.md`（见本文对应归档章节） |
| `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | 9. Order Reports | Flat/XML（文档） | `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL.md`（见本文对应归档章节） |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | 9. Order Reports | Flat/XML（文档） | `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_PENDING_ORDERS_DATA` | 9. Order Reports | Flat/XML（文档） | `GET_FLAT_FILE_PENDING_ORDERS_DATA.md`（见本文对应归档章节） |
| `GET_PENDING_ORDERS_DATA` | 9. Order Reports | Flat/XML（文档） | `GET_PENDING_ORDERS_DATA.md`（见本文对应归档章节） |
| `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA` | 9. Order Reports | Flat/XML（文档） | `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA.md`（见本文对应归档章节） |
| `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA` | 10. Payment Reports | Flat/XML（文档） | `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA.md`（见本文对应归档章节） |
| `GET_SELLER_FEEDBACK_DATA` | 11. Performance Reports | Flat/XML（文档） | `GET_SELLER_FEEDBACK_DATA.md`（见本文对应归档章节） |
| `GET_V1_SELLER_PERFORMANCE_REPORT` | 11. Performance Reports | Flat/XML（文档） | `GET_V1_SELLER_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `GET_V2_SELLER_PERFORMANCE_REPORT` | 11. Performance Reports | Flat/XML（文档） | `GET_V2_SELLER_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `GET_PROMOTION_PERFORMANCE_REPORT` | 11. Performance Reports | JSON Schema 专页 | `GET_PROMOTION_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `GET_COUPON_PERFORMANCE_REPORT` | 11. Performance Reports | JSON Schema 专页 | `GET_COUPON_PERFORMANCE_REPORT.md`（见本文对应归档章节） |
| `END_USER_DATA_REPORT` | 12. Regulatory Compliance Reports | JSON Schema 专页 | `END_USER_DATA_REPORT.md`（见本文对应归档章节） |
| `FBA_BULK_INVOICE` | 12. Regulatory Compliance Reports | Flat/XML（文档） | `FBA_BULK_INVOICE.md`（见本文对应归档章节） |
| `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` | 12. Regulatory Compliance Reports | JSON Schema 专页 | `MARKETPLACE_ASIN_PAGE_VIEW_METRICS.md`（见本文对应归档章节） |
| `GET_EPR_MONTHLY_REPORTS` | 12. Regulatory Compliance Reports | Flat/XML（文档） | `GET_EPR_MONTHLY_REPORTS.md`（见本文对应归档章节） |
| `GET_EPR_QUARTERLY_REPORTS` | 12. Regulatory Compliance Reports | Flat/XML（文档） | `GET_EPR_QUARTERLY_REPORTS.md`（见本文对应归档章节） |
| `GET_EPR_ANNUAL_REPORTS` | 12. Regulatory Compliance Reports | Flat/XML（文档） | `GET_EPR_ANNUAL_REPORTS.md`（见本文对应归档章节） |
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | 13. Returns Reports | Flat/XML（文档） | `GET_XML_RETURNS_DATA_BY_RETURN_DATE.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | 13. Returns Reports | Flat/XML（文档） | `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE.md`（见本文对应归档章节） |
| `GET_XML_MFN_PRIME_RETURNS_REPORT` | 13. Returns Reports | Flat/XML（文档） | `GET_XML_MFN_PRIME_RETURNS_REPORT.md`（见本文对应归档章节） |
| `GET_CSV_MFN_PRIME_RETURNS_REPORT` | 13. Returns Reports | Flat/XML（文档） | `GET_CSV_MFN_PRIME_RETURNS_REPORT.md`（见本文对应归档章节） |
| `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | 13. Returns Reports | Flat/XML（文档） | `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | 13. Returns Reports | Flat/XML（文档） | `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT.md`（见本文对应归档章节） |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | 14. Settlement/Payments Reports | Flat/XML（文档） | `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE.md`（见本文对应归档章节） |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | 14. Settlement/Payments Reports | Flat/XML（文档） | `GET_V2_SETTLEMENT_REPORT_DATA_XML.md`（见本文对应归档章节） |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | 14. Settlement/Payments Reports | Flat/XML（文档） | `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2.md`（见本文对应归档章节） |
| `GST_MTR_STOCK_TRANSFER_REPORT` | 15. Tax Reports | Flat/XML（文档） | `GST_MTR_STOCK_TRANSFER_REPORT.md`（见本文对应归档章节） |
| `GST_MTR_B2B` | 15. Tax Reports | Flat/XML（文档） | `GST_MTR_B2B.md`（见本文对应归档章节） |
| `GST_MTR_B2C` | 15. Tax Reports | Flat/XML（文档） | `GST_MTR_B2C.md`（见本文对应归档章节） |
| `GET_FLAT_FILE_SALES_TAX_DATA` | 15. Tax Reports | Flat/XML（文档） | `GET_FLAT_FILE_SALES_TAX_DATA.md`（见本文对应归档章节） |
| `SC_VAT_TAX_REPORT` | 15. Tax Reports | Flat/XML（文档） | `SC_VAT_TAX_REPORT.md`（见本文对应归档章节） |
| `GET_VAT_TRANSACTION_DATA` | 15. Tax Reports | Flat/XML（文档） | `GET_VAT_TRANSACTION_DATA.md`（见本文对应归档章节） |
| `GET_GST_MTR_B2B_CUSTOM` | 15. Tax Reports | Flat/XML（文档） | `GET_GST_MTR_B2B_CUSTOM.md`（见本文对应归档章节） |
| `GET_GST_MTR_B2C_CUSTOM` | 15. Tax Reports | Flat/XML（文档） | `GET_GST_MTR_B2C_CUSTOM.md`（见本文对应归档章节） |
| `GET_GST_STR_ADHOC` | 15. Tax Reports | Flat/XML（文档） | `GET_GST_STR_ADHOC.md`（见本文对应归档章节） |

## Archived reference: report-requests/types/SC_VAT_TAX_REPORT.md

# `SC_VAT_TAX_REPORT`

> **分类**：15. Tax Reports  
> **说明**：Seller Central VAT tax report  
> **可用范围**：Seller only

## 官方说明（Report type values）

以下内容整理自官方 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 子页 [Tax Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-calculation-report)（章节：**Amazon VAT Calculation Report**）。**与专页其它段落冲突时以官方英文文档为准。**

- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）
- **Role**：[Tax Invoicing (Restricted)](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#tax-invoicing-restricted)
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：Comma-separated flat file
- **Store availability**：Ireland, Spain, United Kingdom, France, Belgium, Netherlands, Germany, Italy, Sweden, and Poland
- **要点**：Provides detailed value-added tax (VAT) calculation information for buyer shipments, returns, and refunds.

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-tax#amazon-vat-calculation-report>


## 官方 `schemas/reports` JSON Schema

本 `reportType` 在 Amazon 仓库 [https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中**无**与结果格式一一对应的独立 JSON 文件（多为 **Flat File / TSV / XML** 等）。**请求参数、可选日期、`reportOptions`、列定义**以官方为准：

- [https://developer-docs.amazon.com/sp-api/docs/report-type-values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)

## CreateReport 请求体（最小常用）

多数此类报告可按下述最小结构创建（是否支持 `dataStartTime`/`dataEndTime` 及格式以官方文档为准）：

```json
{
  "reportType": "SC_VAT_TAX_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

支持日期范围时，可补充例如：

```json
{
  "reportType": "SC_VAT_TAX_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}
```

若官方要求 **`reportOptions`** 或其它字段，必须一并传入（见 Report type values）。

## LinkFox

- `get_report` 操作：JSON 参数与 CreateReport 体字段同名；支持 `reportOptions`、`lastUpdatedDate`。  
- 网关与代理：`references/api.md`。

## 另见

- 全类型总表：`references/report-types.md`  
- 带 JSON 结果 Schema 的报告：`references/report-requests/README.md`

## Archived reference: report-requests/vendorCouponReport.md

# `vendorCouponReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorCouponReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorCouponReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report contains data to help vendors optimize their coupons and adjust their advertising strategies. This report supports start dates up to two years before the current date.

## 对应 `reportType`（从 schema 中提取）

- `GET_COUPON_PERFORMANCE_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_COUPON_PERFORMANCE_REPORT",
  "reportOptions": {
    "campaignStartDateFrom": "2021-11-01T15:33:26Z",
    "campaignStartDateTo": "2021-11-30T15:33:26Z"
  },
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `campaignStartDateFrom` | `2021-11-01T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `campaignStartDateTo` | `2021-11-30T15:33:26Z` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorForecastingReport.md

# `vendorForecastingReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorForecastingReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorForecastingReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

Forecast customer demand of your products for production and inventory planning purposes.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_FORECASTING_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_FORECASTING_REPORT",
  "reportOptions": {
    "sellingProgram": "RETAIL"
  },
  "lastUpdatedDate": "2021-06-20",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `sellingProgram` | `RETAIL` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorInventoryReport.md

# `vendorInventoryReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorInventoryReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorInventoryReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares inventory data of a vendor's items both at an aggregated level (across the vendor's entire catalog of items) and at a per-ASIN level. Data is available at different date range aggregation levels: DAY, WEEK, MONTH, QUARTER, YEAR. Requests can span multiple date range periods. For example, if the customer specified reportPeriod=WEEK and a dataStartTime and dataEndTime that are 3 weeks apart, the report would contain data for each of those 3 contiguous weeks.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_INVENTORY_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_INVENTORY_REPORT",
  "reportOptions": {
    "reportPeriod": "WEEK",
    "sellingProgram": "RETAIL",
    "distributorView": "MANUFACTURING"
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
| `sellingProgram` | `RETAIL` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `distributorView` | `MANUFACTURING` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorNetPureProductMarginReport.md

# `vendorNetPureProductMarginReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorNetPureProductMarginReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorNetPureProductMarginReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

The Net Pure Product Margin report shares data with vendors on Amazon's profit margin selling the vendor's items both at an aggregated level (across the vendor's entire catalog of items) and at a per-ASIN level. Data is available at different date range aggregation levels: DAY, WEEK, MONTH, QUARTER, YEAR. Requests can span multiple date range periods.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT",
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

## Archived reference: report-requests/vendorRealTimeInventoryReport.md

# `vendorRealTimeInventoryReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorRealTimeInventoryReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeInventoryReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares inventory data at an ASIN level, aggregated to an hourly granularity. Requests can span multiple date range periods, including the current day.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_REAL_TIME_INVENTORY_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_INVENTORY_REPORT",
  "dataStartTime": "2022-10-01T00:00:00Z",
  "dataEndTime": "2022-10-01T02:00:00Z",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorRealTimeSalesReport.md

# `vendorRealTimeSalesReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorRealTimeSalesReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeSalesReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares sales data at an ASIN level, aggregated to an hourly granularity. Requests can span multiple date range periods. For example, if the customer specified dataStartTime and dataEndTime span three hours, the report would contain data for each complete hour within the time span.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_REAL_TIME_SALES_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_SALES_REPORT",
  "dataStartTime": "2022-04-20T20:00:00Z",
  "dataEndTime": "2022-04-20T21:00:00Z",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ],
  "reportOptions": {
    "currencyCode": "USD"
  }
}
```

### `reportOptions` 键说明（来自示例）

| 键 | 示例值 | 说明 |
|----|--------|------|
| `currencyCode` | `USD` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorRealTimeTrafficReport.md

# `vendorRealTimeTrafficReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorRealTimeTrafficReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeTrafficReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares data on the customer traffic to the detail pages of the vendor's items with an hourly granularity. Requests can span multiple date range periods. For example, if the customer specified dataStartTime and dataEndTime span three hours, the report would contain data for each complete hour within the time span.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_REAL_TIME_TRAFFIC_REPORT",
  "dataStartTime": "2022-04-20T20:00:00Z",
  "dataEndTime": "2022-04-20T21:00:00Z",
  "marketplaceIds": [
    "ATVPDKIKX0DER"
  ]
}
```

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorSalesReport.md

# `vendorSalesReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorSalesReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorSalesReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares data on the sales performance of vendor's items both at an aggregated level (across the vendor's entire catalog of items) and at a per-ASIN level. Data is available at different date range aggregation levels: DAY, WEEK, MONTH, QUARTER, YEAR. Requests can span multiple date range periods.

## 对应 `reportType`（从 schema 中提取）

- `GET_VENDOR_SALES_REPORT`

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

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

### 官方 `reportSpecification` 示例（摘自 schema `examples`）

```json
{
  "reportType": "GET_VENDOR_SALES_REPORT",
  "reportOptions": {
    "distributorView": "MANUFACTURING",
    "reportPeriod": "WEEK",
    "sellingProgram": "RETAIL"
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
| `distributorView` | `MANUFACTURING` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `reportPeriod` | `WEEK` | 详见上游 schema `reportSpecification.properties.reportOptions` |
| `sellingProgram` | `RETAIL` | 详见上游 schema `reportSpecification.properties.reportOptions` |

## 报告结果文档（下载/解压后的 JSON）

- 顶层字段以本 schema 的 `properties` / `definitions` 为准（多为业务数据数组或对象）。
- 若 schema 内含 `reportSpecification` + 数据数组（如 `dataByAsin`），下载文件常为 **带元数据包裹** 的结构，与 TSV 类平面报告不同。

## Archived reference: report-requests/vendorTrafficReport.md

# `vendorTrafficReport.json` — 报告格式说明

> 上游 JSON Schema 来自 Amazon [selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports)。

- **Raw**：[vendorTrafficReport.json](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorTrafficReport.json)
- **目录浏览**：https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports

## Schema 摘要

This report shares data on the customer traffic to the detail pages of the vendor's items both at an aggregated level (across the vendor's entire catalog of items) and at a per-ASIN level. Data is available for different date range aggregation levels: DAY, WEEK, MONTH, QUARTER, YEAR. Requests can span multiple date range periods.

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

- **`reportType`** / **`marketplaceIds`**：必填（多数报告）。
- **`dataStartTime`** / **`dataEndTime`**：ISO 8601；部分报告 schema 使用 **仅日期** `YYYY-MM-DD`（Amazon 忽略时间分量），以本文件「官方示例」为准。
- **`reportOptions`**：对象，键名/枚举因报告而异；Brand Analytics 等 **必填**，见下节。
- **`lastUpdatedDate`**：部分 Vendor 报告使用（见 schema `reportSpecification`），需与 `dataStartTime`/`dataEndTime` 按官方要求组合。

CreateReport 请求体支持：在 JSON 参数中传入 **`reportOptions`**（对象）以及 **`lastUpdatedDate`**（字符串），会合并进创建请求体。

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

## Archived reference: report-types.md

# Amazon Store Complete Report Types Reference

This document lists ALL report types available in Amazon Selling Partner API, organized by category.

**Total**：本页表格共 **109** 个 `reportType` 枚举（与 `report-requests/types/` 专页一一对应）；Amazon 文档中可能另有增减，以 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准。

**全覆盖请求说明**：下表每一个 `Report Type` 在仓库中均有独立专页（CreateReport 要点、是否有官方 JSON Schema、链到 GitHub `schemas/reports` 专页等）→ `report-requests/types/README.md`（见本文对应归档章节）（按 `reportType` 字母/索引表浏览），或直接打开 `report-requests/types/<REPORT_TYPE>.md`（见本文对应归档章节）。

---

## 1. Amazon Business Reports

Business-related fee and discount reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `FEE_DISCOUNTS_REPORT` | Amazon Business fee discounts | Seller only |

---

## 2. Analytics Reports

Sales, traffic, and business intelligence reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` | Search catalog performance metrics | Seller only |
| `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` | Search query performance data | Seller only |
| `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT` | Products frequently purchased together | Both |
| `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` | Top search terms for products | Both |
| `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` | Repeat purchase behavior analysis | Both |
| `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` | Real-time vendor inventory | Vendor only |
| `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` | Real-time vendor traffic | Vendor only |
| `GET_VENDOR_REAL_TIME_SALES_REPORT` | Real-time vendor sales | Vendor only |
| `GET_VENDOR_SALES_REPORT` | Vendor sales report | Vendor only |
| `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` | Vendor product margins | Vendor only |
| `GET_VENDOR_TRAFFIC_REPORT` | Vendor traffic report | Vendor only |
| `GET_VENDOR_FORECASTING_REPORT` | Vendor forecasting data | Vendor only |
| `GET_VENDOR_INVENTORY_REPORT` | Vendor inventory report | Vendor only |
| `GET_SALES_AND_TRAFFIC_REPORT` | Sales and traffic by date | Seller only |

---

## 3. B2B Product Opportunities

Business-to-business product opportunity insights.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` | Personalized B2B product recommendations | Seller only |
| `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` | B2B opportunities not yet on Amazon | Seller only |

---

## 4. Browse Tree Reports

Product category and browse node data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_XML_BROWSE_TREE_DATA` | Browse tree hierarchy (XML format) | Seller only |

---

## 5. Easy Ship Reports

Amazon Easy Ship program reports (India marketplace).

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_EASYSHIP_DOCUMENTS` | Easy Ship shipping documents | Seller only |
| `GET_EASYSHIP_PICKEDUP` | Easy Ship picked up orders | Seller only |
| `GET_EASYSHIP_WAITING_FOR_PICKUP` | Orders waiting for Easy Ship pickup | Seller only |

---

## 6. FBA (Fulfillment by Amazon) Reports

Comprehensive FBA inventory, shipment, fees, and fulfillment data.

### 6.1 FBA Shipments

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA fulfilled shipments (general) | Seller only |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING` | FBA shipments for invoicing | Seller only |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX` | FBA shipments tax data | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA customer shipment sales | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA` | FBA shipment promotion data | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA` | FBA customer taxes | Seller only |

### 6.2 FBA Inventory

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_AFN_INVENTORY_DATA` | Amazon Fulfilled Network inventory | Seller only |
| `GET_AFN_INVENTORY_DATA_BY_COUNTRY` | AFN inventory by country | Seller only |
| `GET_LEDGER_SUMMARY_VIEW_DATA` | Inventory ledger summary | Seller only |
| `GET_LEDGER_DETAIL_VIEW_DATA` | Inventory ledger detail | Seller only |
| `GET_RESERVED_INVENTORY_DATA` | Reserved inventory data | Seller only |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA Manage Your Inventory (active) | Seller only |
| `GET_FBA_MYI_ALL_INVENTORY_DATA` | FBA all inventory status | Seller only |
| `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT` | FBA restock recommendations | Seller only |
| `GET_STRANDED_INVENTORY_UI_DATA` | Stranded inventory (UI format) | Seller only |
| `GET_STRANDED_INVENTORY_LOADER_DATA` | Stranded inventory (bulk format) | Seller only |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA inventory planning | Seller only |
| `GET_REMOTE_FULFILLMENT_ELIGIBILITY` | Remote fulfillment eligibility | Seller only |

### 6.3 FBA Fees & Charges

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA storage fee charges | Seller only |
| `GET_FBA_OVERAGE_FEE_CHARGES_DATA` | FBA overage fee charges | Seller only |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | Estimated FBA fees | Seller only |
| `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA` | Long-term storage fees | Seller only |

### 6.4 FBA Returns & Reimbursements

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA customer returns | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA` | FBA shipment replacements | Seller only |
| `GET_FBA_REIMBURSEMENTS_DATA` | FBA reimbursements | Seller only |

### 6.5 FBA Removals

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_RECOMMENDED_REMOVAL_DATA` | Recommended removal inventory | Seller only |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | Removal order details | Seller only |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | Removal shipment details | Seller only |

### 6.6 FBA Compliance

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA` | Inbound non-compliance issues | Seller only |

---

## 7. Inventory Reports

Listing and inventory management reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | Open listings (flat file) | Seller only |
| `GET_MERCHANT_LISTINGS_ALL_DATA` | All active listings | Seller only |
| `GET_MERCHANT_LISTINGS_DATA` | Active listings (standard) | Seller only |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | Inactive listings | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT` | Listings (backwards compatible) | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_LITE` | Listings (lite version) | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_LITER` | Listings (lighter version) | Seller only |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | Cancelled listings | Seller only |
| `GET_MERCHANTS_LISTINGS_FYP_REPORT` | Fix Your Products report | Seller only |
| `GET_PAN_EU_OFFER_STATUS` | Pan-European offer status | Seller only |
| `GET_MFN_PANEU_OFFER_STATUS` | MFN Pan-EU offer status | Seller only |
| `GET_REFERRAL_FEE_PREVIEW_REPORT` | Referral fee preview | Seller only |

---

## 8. Invoice Reports

VAT invoice data for tax compliance.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT` | VAT invoice data (flat file) | Seller only |
| `GET_XML_VAT_INVOICE_DATA_REPORT` | VAT invoice data (XML) | Seller only |

---

## 9. Order Reports

Order processing and fulfillment data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING` | Actionable orders for shipping | Seller only |
| `GET_ORDER_REPORT_DATA_INVOICING` | Order data for invoicing | Seller only |
| `GET_ORDER_REPORT_DATA_TAX` | Order tax data | Seller only |
| `GET_ORDER_REPORT_DATA_SHIPPING` | Order shipping data | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING` | Order invoicing (flat file) | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING` | Order shipping (flat file) | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX` | Order tax (flat file) | Seller only |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders by last update | Seller only |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders by order date | Seller only |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | Archived orders | Seller only |
| `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders (XML, by update) | Seller only |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders (XML, by date) | Seller only |
| `GET_FLAT_FILE_PENDING_ORDERS_DATA` | Pending orders (flat file) | Seller only |
| `GET_PENDING_ORDERS_DATA` | Pending orders | Seller only |
| `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA` | Converged pending orders | Seller only |

---

## 10. Payment Reports

Financial holds and payment data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA` | Financial holds by date range | Seller only |

---

## 11. Performance Reports

Seller performance metrics and feedback.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_SELLER_FEEDBACK_DATA` | Customer feedback | Seller only |
| `GET_V1_SELLER_PERFORMANCE_REPORT` | Seller performance v1 | Seller only |
| `GET_V2_SELLER_PERFORMANCE_REPORT` | Seller performance v2 | Seller only |
| `GET_PROMOTION_PERFORMANCE_REPORT` | Promotion performance | Both |
| `GET_COUPON_PERFORMANCE_REPORT` | Coupon performance | Both |

---

## 12. Regulatory Compliance Reports

Compliance and regulatory reporting.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `END_USER_DATA_REPORT` | End user data report | Seller only |
| `FBA_BULK_INVOICE` | FBA bulk invoice | Seller only |
| `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` | ASIN page view metrics | Seller only |
| `GET_EPR_MONTHLY_REPORTS` | Extended Producer Responsibility (monthly) | Seller only |
| `GET_EPR_QUARTERLY_REPORTS` | EPR quarterly reports | Seller only |
| `GET_EPR_ANNUAL_REPORTS` | EPR annual reports | Seller only |

---

## 13. Returns Reports

Return and replacement order data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | Returns by date (XML) | Seller only |
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | Returns by date (flat file) | Seller only |
| `GET_XML_MFN_PRIME_RETURNS_REPORT` | MFN Prime returns (XML) | Seller only |
| `GET_CSV_MFN_PRIME_RETURNS_REPORT` | MFN Prime returns (CSV) | Seller only |
| `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU return attributes (XML) | Seller only |
| `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU return attributes (flat file) | Seller only |

---

## 14. Settlement/Payments Reports

Financial settlement and transaction data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | Settlement report v2 (flat file) | Seller only |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | Settlement report v2 (XML) | Seller only |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | Enhanced settlement report | Seller only |

---

## 15. Tax Reports

Tax compliance and transaction data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GST_MTR_STOCK_TRANSFER_REPORT` | GST stock transfer report | Seller only |
| `GST_MTR_B2B` | GST Monthly Tax Report B2B | Seller only |
| `GST_MTR_B2C` | GST Monthly Tax Report B2C | Seller only |
| `GET_FLAT_FILE_SALES_TAX_DATA` | Sales tax collection data | Seller only |
| `SC_VAT_TAX_REPORT` | Seller Central VAT tax report | Seller only |
| `GET_VAT_TRANSACTION_DATA` | VAT transaction data | Seller only |
| `GET_GST_MTR_B2B_CUSTOM` | Custom GST MTR B2B | Seller only |
| `GET_GST_MTR_B2C_CUSTOM` | Custom GST MTR B2C | Seller only |
| `GET_GST_STR_ADHOC` | GST Adhoc report | Seller only |

---

## Report Request Best Practices

1. **Schedule Frequency**: Most reports can be requested on-demand, but some have rate limits
2. **Date Ranges**: Use reasonable date ranges (typically 1-90 days)
3. **Retention**: Reports are retained for 90 days unless specified otherwise
4. **Rate Limits**: Respect API rate limits (typically 0.0222 requests/second)
5. **Marketplace-Specific**: Some reports are only available in certain marketplaces

## Common Marketplace IDs

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | United States | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| NA | Brazil | A2Q3Y263D00KWC |
| EU | United Kingdom | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| EU | France | A13V1IB3VIYZZH |
| EU | Italy | APJ6JRA9NG5V4 |
| EU | Spain | A1RKKUPIHCS9HS |
| EU | Netherlands | A1805IZSGTT6HS |
| EU | Poland | A1C3SOZRARQ6R3 |
| EU | Sweden | A2NODRKZP88ZB9 |
| EU | Turkey | A33AVAJ2PDY3EV |
| FE | Japan | A1VC38T7YXB528 |
| FE | Australia | A39IBJ37TRP1C6 |
| FE | Singapore | A19VAU5U5O7RUS |
| FE | India | A21TJRUUN4KGV |
| FE | UAE | A2VIGQ35RCS4UG |

## Quick Reference by Use Case

**Inventory Management**:
- `GET_MERCHANT_LISTINGS_ALL_DATA`
- `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA`
- `GET_STRANDED_INVENTORY_UI_DATA`

**Order Processing**:
- `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`
- `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING`

**Financial Analysis**:
- `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`
- `GET_SALES_AND_TRAFFIC_REPORT`
- `GET_FBA_STORAGE_FEE_CHARGES_DATA`

**Performance Monitoring**:
- `GET_V2_SELLER_PERFORMANCE_REPORT`
- `GET_SELLER_FEEDBACK_DATA`
- `GET_SALES_AND_TRAFFIC_REPORT`

**Returns Management**:
- `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE`
- `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA`

**Tax Compliance**:
- `GET_FLAT_FILE_SALES_TAX_DATA`
- `GET_VAT_TRANSACTION_DATA`
- `GET_GST_MTR_B2B_CUSTOM`

---

**Official Documentation**: https://developer-docs.amazon.com/sp-api/docs/report-type-values

**Last Updated**: Based on Amazon Selling Partner API documentation as of April 2026

## Archived reference: report-types-basic.md

# Amazon Store Report Types Reference

This document describes the common report types available in Amazon Selling Partner API.

## Report Categories

Amazon Store reports are organized into the following main categories:

### 1. Inventory Reports (库存报告)

Track your inventory status, listings, and stock levels.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_MERCHANT_LISTINGS_ALL_DATA` | Active listings report including SKU, ASIN, price, quantity | Near real-time |
| `GET_MERCHANT_LISTINGS_DATA` | Active listings in tab-delimited flat file format | Near real-time |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | Inactive listings report | Near real-time |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | Cancelled listings | Near real-time |
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | Open listings report (SKU, price, quantity) | Near real-time |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA Manage Inventory Report | Near real-time |
| `GET_FBA_INVENTORY_AGED_DATA` | FBA Inventory Age Report | Daily |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA Inventory Planning Report | Daily |

**Common Use Cases:**
- Monitor current inventory levels
- Identify inactive or stranded inventory
- Plan inventory replenishment
- Audit listing accuracy

### 2. Order Reports (订单报告)

Retrieve order data for processing and analysis.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders by order date (general format) | Near real-time |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders by last update date | Near real-time |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE` | All orders in XML format | Near real-time |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | Archived orders data | Historical |
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA` | Actionable orders requiring processing | Near real-time |
| `GET_ORDER_REPORT_DATA_SHIPPING` | Orders with shipping information | Near real-time |

**Common Use Cases:**
- Export orders for ERP/WMS systems
- Track order fulfillment status
- Analyze order patterns
- Generate shipping labels

### 3. Financial Reports (财务报告)

Access settlement and financial transaction data.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | Settlement report v2 (flat file) | Every 14 days |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | Settlement report v2 (XML format) | Every 14 days |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | Enhanced settlement report | Every 14 days |

**Common Use Cases:**
- Reconcile Amazon payments
- Track fees and refunds
- Generate financial statements
- Accounting integration

### 4. Sales Reports (销售报告)

Analyze sales performance and traffic metrics.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_SALES_AND_TRAFFIC_REPORT` | Sales and traffic by date | Daily |
| `GET_FLAT_FILE_SALES_TAX_DATA` | Sales tax collection data | Near real-time |

**Common Use Cases:**
- Track daily sales metrics
- Monitor traffic and conversion rates
- Analyze sales trends
- Tax reporting

### 5. FBA (Fulfillment by Amazon) Reports

Manage FBA inventory and shipments.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA fulfilled shipments | Near real-time |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA customer shipment sales | Daily |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | FBA removal order details | Daily |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | FBA removal shipment details | Daily |
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA storage fee charges | Monthly |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | Estimated FBA fees | On-demand |

**Common Use Cases:**
- Track FBA shipments
- Monitor storage fees
- Process removal orders
- Analyze fulfillment costs

### 6. Returns Reports (退货报告)

Track customer returns and refunds.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | Returns data by return date | Daily |
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | Returns data in XML format | Daily |
| `GET_FLAT_FILE_ALL_RETURNS_DATA_BY_RETURN_DATE` | All returns data | Daily |
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA customer returns | Daily |

**Common Use Cases:**
- Process return requests
- Track return rates
- Analyze return reasons
- Manage refunds

### 7. Performance Reports (绩效报告)

Monitor seller performance metrics.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_V1_SELLER_PERFORMANCE_REPORT` | Seller performance metrics | Daily |
| `GET_FLAT_FILE_FEEDBACK_DATA` | Customer feedback | Daily |

**Common Use Cases:**
- Monitor account health
- Track customer satisfaction
- Identify performance issues
- Respond to feedback

## Report Request Workflow

### Creating a Report

1. **Request a Report**
   - Endpoint: `POST /reports/2021-06-30/reports`
   - Specify `reportType`, `marketplaceIds`, and optional date range
   - Receive a `reportId` in response

2. **Check Report Status**
   - Endpoint: `GET /reports/2021-06-30/reports/{reportId}`
   - Status values: `IN_QUEUE`, `IN_PROGRESS`, `DONE`, `CANCELLED`, `FATAL`

3. **Download Report Document**
   - When status is `DONE`, get `reportDocumentId`
   - Endpoint: `GET /reports/2021-06-30/documents/{reportDocumentId}`
   - Get download URL and decrypt if needed

### Getting Existing Reports

- Endpoint: `GET /reports/2021-06-30/reports`
- Filter by `reportTypes`, `processingStatuses`, `marketplaceIds`
- Filter by date range: `createdSince`, `createdUntil`

## Common Parameters

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| `reportType` | Type of report to generate | Yes | `GET_MERCHANT_LISTINGS_ALL_DATA` |
| `marketplaceIds` | Target marketplace(s) | Yes | `["ATVPDKIKX0DER"]` (US) |
| `dataStartTime` | Start date for data range | No | `2024-01-01T00:00:00Z` |
| `dataEndTime` | End date for data range | No | `2024-01-31T23:59:59Z` |

## Marketplace IDs

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | United States | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| EU | United Kingdom | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| EU | France | A13V1IB3VIYZZH |
| EU | Italy | APJ6JRA9NG5V4 |
| EU | Spain | A1RKKUPIHCS9HS |
| FE | Japan | A1VC38T7YXB528 |
| FE | Australia | A39IBJ37TRP1C6 |
| FE | Singapore | A19VAU5U5O7RUS |
| FE | India | A21TJRUUN4KGV |

## Best Practices

1. **Request Frequency**
   - Respect rate limits: typically 0.0222 requests/second (1 request per 45 seconds)
   - Use burst capacity wisely
   - Schedule recurring reports during off-peak hours

2. **Date Ranges**
   - Keep date ranges reasonable (typically 1-90 days)
   - Some reports may have maximum date range restrictions
   - Use `dataStartTime` and `dataEndTime` to narrow results

3. **Error Handling**
   - Check report status before downloading
   - Handle `FATAL` status reports gracefully
   - Retry failed requests with exponential backoff

4. **Data Processing**
   - Reports are typically in TSV (tab-separated values) format
   - Handle large files efficiently (streaming)
   - Validate data before processing

## Example: Request Inventory Report

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## Example: Get Reports List

```
GET /reports/2021-06-30/reports?reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA&marketplaceIds=ATVPDKIKX0DER
```

## Additional Resources

- Official Documentation: https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference
- Report Type Values: https://developer-docs.amazon.com/sp-api/docs/report-type-values
- Reports API Use Case Guide: https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-use-case-guide

---

**Note**: Report availability and update frequency may vary by marketplace and seller account type. Always check the official Amazon Selling Partner API documentation for the most current information.
