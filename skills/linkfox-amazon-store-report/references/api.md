# Amazon 店铺报告 API Reference

本文档描述 **报告获取** 相关的 API。授权与令牌相关接口（`/spApi/authorizeUrl`、`/spApi/storeTokens`、`/spApi/refreshToken` 等）属于 **依赖 skill** `linkfox-amazon-store-auth`，请参考该 skill 的 `references/api.md`。

> ⚠️ **依赖提示**：在调用本 skill 接口前，请先确认 `linkfox-amazon-store-auth` 已安装（参见本 skill 的 `SKILL.md` 顶部 Prerequisites）。

## Calling Conventions

- **Base URL**: `${LINKFOX_TOOL_GATEWAY}`（默认 `https://tool-gateway.linkfox.com`；可用 `STORE_API_BASE_URL` 或兼容旧名 `SPAPI_BASE_URL` 覆盖）
- **Request Method**: POST
- **Content-Type**: `application/json`
- **Authentication**: Header `Authorization: <api_key>`，读取环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`

## API Endpoints

### 1. Developer Proxy（转发亚马逊开放接口）

**Endpoint**: `/spApi/developerProxy`

报告相关的上游调用（列表 / 请求 / 查状态 / 取下载链接）都通过该代理接口转发。

**Request Parameters** (JSON):

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| region | string | Yes | 区域代码：NA/EU/FE | "NA" |
| path | string | Yes | 上游 Reports 等 API 路径（不含域名与 developer-proxy/{region}/ 前缀） | "reports/2021-06-30/reports" |
| method | string | Yes | HTTP 方法：GET/POST/PUT/DELETE | "GET" |
| amzAccessToken | string | Yes | 访问令牌（来自 `/spApi/storeTokens`） | "Atza\|IwEBI..." |
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
- `amzAccessToken` 必须与 `region` 匹配的店铺令牌一致
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

**入口索引**：[report-requests/README.md](./report-requests/README.md)  
**按 `reportType` 全覆盖（109 个）**：[report-requests/types/README.md](./report-requests/types/README.md)

> 大量 **Flat File**（订单、库存等 TSV）报告在官方仓库中**无**独立 `schemas/reports/*.json` 时，请求体通常为 `reportType` + `marketplaceIds` + 可选 `dataStartTime`/`dataEndTime`，详见 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)。

### 脚本参数映射（`scripts/get_report.py`）

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

下面是典型调用序列（本 skill + `linkfox-amazon-store-auth`）：

```
linkfox-amazon-store-auth/scripts/store_tokens.py    # 取 accessToken
           │
           ▼
linkfox-amazon-store-report/scripts/get_report.py    # 用 accessToken 拉报告
  1. POST /spApi/developerProxy (method=POST,  path=reports/2021-06-30/reports)
  2. POST /spApi/developerProxy (method=GET,   path=reports/2021-06-30/reports/{reportId})  # 轮询
  3. POST /spApi/developerProxy (method=GET,   path=reports/2021-06-30/documents/{reportDocumentId})
  4. 直接下载返回的 url 并解压
```

## Error Codes

| errcode | 含义 | 建议动作 |
|---------|------|----------|
| 200 | 代理调用成功（还需看 `httpStatus`） | 继续解析 `body` |
| 1002 | 缺参数或认证失败 | 检查必填参数与 API key |
| 1003 | 第三方服务调用失败 | 稍后重试 |
| 1005 | path 不在白名单 | 联系后端加白名单 |

### Developer Proxy 上游状态码

调用成功（`errcode=200`）后必须再检查 `httpStatus`：

| httpStatus | 含义 | 建议动作 |
|------------|------|----------|
| 200 | 成功 | 正常解析 `body` |
| 202 | 已接受（创建报告后返回） | 拿到 reportId 进入轮询 |
| 400 | 参数错误 | 检查 reportType / marketplaceIds |
| 403 | 未授权 | 检查 accessToken、店铺权限、品牌备案 |
| 404 | 资源不存在 | 核对 reportId/reportDocumentId |
| 429 | 请求过快 | 指数退避重试 |
| 500 | 上游错误 | 延时重试 |

---

## curl Examples

### 列出现有报告

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "reports/2021-06-30/reports",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA&marketplaceIds=ATVPDKIKX0DER"
  }'
```

### 请求新报告

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "reports/2021-06-30/reports",
    "method": "POST",
    "amzAccessToken": "Atza|IwEBI...",
    "body": "{\"reportType\":\"GET_MERCHANT_LISTINGS_ALL_DATA\",\"marketplaceIds\":[\"ATVPDKIKX0DER\"]}",
    "contentType": "application/json"
  }'
```

### 查询报告状态

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "reports/2021-06-30/reports/<reportId>",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI..."
  }'
```

### 获取下载链接

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/developerProxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "reports/2021-06-30/documents/<reportDocumentId>",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI..."
  }'
```

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
