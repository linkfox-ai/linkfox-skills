# Amazon 店铺授权 API Reference

本文档描述 **授权与店铺/令牌管理** 相关的 API。若需经网关代理拉取报告或 **Listing 单条查询** 等，请参考 `linkfox-amazon-store-report`、`linkfox-amazon-store-listings` skill。

## Calling Conventions

- **Base URL**: `${LINKFOX_TOOL_GATEWAY}`（默认 `https://tool-gateway.linkfox.com`；可用 `LINKFOX_TOOL_GATEWAY` 覆盖，兼容旧名 `STORE_API_BASE_URL` / `SPAPI_BASE_URL`）
- **Request Method**: 所有接口均为 POST
- **Content-Type**: `application/json`
- **Authentication**: Header `Authorization: <api_key>`，API key 优先读取环境变量 `LINKFOX_AGENT_API_KEY`，未设置时回退到兼容旧名 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## API Endpoints

### 1. Get Authorization URL

**Endpoint**: `/spApi/authorizeUrl`

**Request Parameters** (JSON):

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| region | string | Yes | 区域代码：NA / EU / FE | "NA" |
| sellerName | string | **Yes** | 店铺展示名（店铺名）— **必填，非空**；用于在已授权店铺列表中识别账号 | "My Store" |

**Response**:

```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/apps/authorize/consent?..."
}
```

> 说明：授权完成后的回调由 Amazon 直接回调服务端内部接口处理，属于系统内部流程，不作为本 skill 的用户调用接口。

---

### 2. List Authorized Stores

**Endpoint**: `/spApi/authorizedStores`

**Request Parameters**: 无（使用当前用户上下文）

**Response**:

```json
{
  "stores": [
    {
      "sellerName": "My Store",
      "sellerId": "A1234567890",
      "region": "NA"
    }
  ],
  "total": 1
}
```

---

### 3. Refresh Token

**Endpoint**: `/spApi/refreshToken`

**Request Parameters** (JSON):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | Yes | Seller ID |
| region | string | No | 区域代码（精确匹配可选） |

**Response**:

```json
{
  "authRecordId": 123,
  "accessToken": "Atza|IwEBIA...",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600",
  "message": "Token refreshed and updated"
}
```

---

### 4. Query Store Tokens

**Endpoint**: `/spApi/storeTokens`

**Request Parameters** (JSON):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | Yes | Seller ID |
| region | string | Yes | 区域代码 |

**Response**:

```json
{
  "sellerId": "A1234567890",
  "region": "NA",
  "authRecordId": 123,
  "accessToken": "Atza|IwEBIA...",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600"
}
```

返回的 `accessToken` 可交给下游 skill（如 `linkfox-amazon-store-report`）用于调用亚马逊开放接口。

---

## Error Codes

| errcode | 含义 | 建议动作 |
|---------|------|----------|
| 200 | 成功 | 正常解析 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 1002 | 缺参数或认证失败 | 检查必填参数与认证 |
| 1003 | 第三方服务调用失败 | 稍后重试，检查网络与白名单 |
| 1004 | 授权记录不存在或不属于当前用户 | 核对 sellerId/region 或重新授权 |

**Error Response Example**:

```json
{
  "errcode": 1002,
  "errmsg": "Missing required parameter: region"
}
```

---

## curl Examples

### Get Authorization URL

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/authorizeUrl \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"region": "NA", "sellerName": "My Store"}'
```

### List Authorized Stores

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/authorizedStores \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json"
```

### Refresh Token

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/refreshToken \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sellerId": "A1234567890", "region": "NA"}'
```

### Query Store Tokens

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/storeTokens \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sellerId": "A1234567890", "region": "NA"}'
```

---

## Feedback API

> 本接口与上面的工具 API **是不同 base URL**，请勿混用。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**: `application/json`

```json
{
  "skillName": "linkfox-amazon-store-auth",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Authorization flow worked smoothly, user was satisfied."
}
```

**Field rules**:
- `skillName`: 使用本 skill 的 YAML frontmatter `name`
- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`: 用户说的话、实际发生了什么、为什么是问题或赞赏

---

## Important Notes

1. **Token 安全**：不要打印完整 accessToken/refreshToken，仅展示前 10 字符掩码。
2. **Token 生命周期**：accessToken 1 小时过期，使用前检查并按需刷新。
3. **区域专属**：同一卖家在不同区域需要分别授权。
4. **用户隔离**：所有 API 都强制用户级访问控制。
5. **回调白名单**：系统回调 URL 必须在授权提供方（紫鸟）处加白名单。

完整授权流程与实现细节：见 `authorization-flow.md`。
