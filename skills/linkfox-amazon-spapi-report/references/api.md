# SP-API Report API Reference

本文档描述 **报告获取** 相关的 API。授权与令牌相关接口（`/spApi/authorizeUrl`、`/spApi/storeTokens`、`/spApi/refreshToken` 等）属于 **依赖 skill** `linkfox-amazon-spapi-auth`，请参考该 skill 的 `references/api.md`。

> ⚠️ **依赖提示**：在调用本 skill 接口前，请先确认 `linkfox-amazon-spapi-auth` 已安装（参见本 skill 的 `SKILL.md` 顶部 Prerequisites）。

## Calling Conventions

- **Base URL**: `https://tool-gateway.linkfox.com`（默认；可用环境变量 `SPAPI_BASE_URL` 覆盖）
- **Request Method**: POST
- **Content-Type**: `application/json`
- **Authentication**: Header `Authorization: <api_key>`，读取环境变量 `LINKFOXAGENT_API_KEY`

## API Endpoints

### 1. Developer Proxy (Forward SP-API Calls)

**Endpoint**: `/spApi/developerProxy`

报告相关的所有 SP-API 调用（列表 / 请求 / 查状态 / 取下载链接）都通过这一个代理接口转发。

**Request Parameters** (JSON):

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| region | string | Yes | 区域代码：NA/EU/FE | "NA" |
| path | string | Yes | SP-API 路径（不含域名与 developer-proxy/{region}/ 前缀） | "reports/2021-06-30/reports" |
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
- 速率限制按上游 SP-API 端点执行

---

## 与依赖 skill 的接力关系

下面是典型调用序列（本 skill + `linkfox-amazon-spapi-auth`）：

```
linkfox-amazon-spapi-auth/scripts/store_tokens.py    # 取 accessToken
           │
           ▼
linkfox-amazon-spapi-report/scripts/get_report.py    # 用 accessToken 拉报告
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
  "skillName": "linkfox-amazon-spapi-report",
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

## 复用的报告报告类型

完整列表见 `references/report-types.md`（95+ 种）。精简摘要见 `references/report-types-basic.md`。
