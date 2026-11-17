# Amazon 店铺授权 API Reference

本文档描述 **授权与店铺/令牌管理** 相关的 API。若需经网关代理拉取报告或 **Listing 单条查询** 等，请参考 `linkfox-amazon-store-report`、`linkfox-amazon-store-listings` skill。

## Calling Conventions

- **Base URL**: `${LINKFOX_TOOL_GATEWAY}`（默认 `https://tool-gateway.linkfox.com`；可用 `LINKFOX_TOOL_GATEWAY` 覆盖，兼容旧名 `STORE_API_BASE_URL` / `SPAPI_BASE_URL`）
- **Request Method**: 所有接口均为 POST
- **Content-Type**: `application/json`
- **Authentication**: Header `Authorization: <api_key>`，API key 优先读取环境变量 `LINKFOX_AGENT_API_KEY`，未设置时回退到兼容旧名 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和算力问题** 处理）

- **解绑脚本**: `LinkFox-Skill/2.0`；透传 `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME`，超时 150s，不缓存、不自动重试。

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
  "success": true,
  "message": "刷新成功并已更新数据库，token 已后台化管理"
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
  "status": "ACTIVE",
  "tokenExpiresAt": 3600,
  "message": "授权信息已后台化管理，token 不再经由 Agent 返回"
}
```

返回值只用于确认授权状态，不作为下游 token 来源。下游业务应通过 `developerProxy` 传入 `sellerId` + `region`。

---

### 5. Cancel Authorization

**Endpoint**: `/spApi/cancelAuthorization`

**Request Parameters** (JSON):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | Yes | 非空 Seller ID，最多 64 字符 |
| region | string | Yes | NA / EU / FE；必传，不支持单站点解绑 |

**Response**:

```json
{
  "success": true,
  "sellerId": "A1234567890",
  "region": "NA",
  "removedBindings": 1,
  "localAuthorizationRevoked": false,
  "amazonRevoked": false,
  "message": "已解除当前用户的店铺绑定；授权与 token 保留，其他用户不受影响；未撤销 Amazon 授权"
}
```

语义说明：

- 仅解除当前成员的 `sellerId + region` 绑定；授权主记录和 token 保留，其他成员不受影响。
- 未绑定或重复解绑仍返回 `success=true`、`removedBindings=0`；两个 revoked 字段固定为 `false`。
- 已发出的请求和未完成的授权回调不受影响，后者可能恢复绑定。Amazon 官方撤销需卖家在 Seller Central → Manage Your Apps → Disable authorization 操作。

---

## Error Codes

| errcode | 含义 | 建议动作 |
|---------|------|----------|
| 200 | 成功 | 正常解析 |
| 400 | 解绑参数格式错误 | 检查 sellerId 与 region |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和算力问题** 处理。|
| 402 | 算力不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和算力问题** 处理。|
| 1002 | 缺参数或认证失败 | 检查必填参数与认证 |
| 1003 | 第三方服务调用失败 | 稍后重试，检查网络与白名单 |
| 1004 | 授权记录不存在或不属于当前用户 | 核对 sellerId/region 或重新授权 |
| 1005 | 授权已取消或失效 | 重新授权 |

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

### Cancel Authorization

```bash
curl -X POST https://tool-gateway.linkfox.com/spApi/cancelAuthorization \
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
6. **取消授权语义**：`cancelAuthorization` 只做 LinkFox 当前成员解绑，不代表 Amazon 侧 OAuth 授权已撤销。

完整授权流程与实现细节：见 `authorization-flow.md`。
