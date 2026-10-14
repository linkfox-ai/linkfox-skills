# TikTok Shop ERP 授权 API Reference

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/authorizeUrl`、`tiktokShop/authorizedStores`、`tiktokShop/storeTokens`、`tiktokShop/refreshToken`（按本页子能力选择） |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-auth/references/api.md`；只按其响应契约核对字段表 |

```json
{"toolName":"tiktokShop/authorizedStores","arguments":{"appType":"erp","region":"global"}}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

本文档描述 **TikTok Shop ERP（小店，`appType=erp`）** 授权与店铺/令牌管理 API（`/tiktokShop`）。本 skill **仅支持 erp**；不处理 `affiliate` / `creator`。

业务数据（商品/订单/履约/财务等）由按功能拆分的 `linkfox-tiktok-shop-*` skill 经 `tiktokShop/developerProxy`（`appType=erp`）调用，不在本 skill 范围。

> ⚠️ **达人/视频号授权**请用 **`linkfox-tiktok-video-auth`**（`/tiktokVideo`）。本 skill 仅允许 `appType=erp`，非 `erp` 请求必须停止。

## Calling Conventions

- **调用入口**: 仅使用 `LinkFox` 的 `proxy_call`；不得通过环境变量覆盖或回退到 HTTP
- **Request Method**: 全部 POST
- **Content-Type**: `application/json`
- **Authentication**: WorkBuddy 自动注入 MCP Authorization
- **User-Agent**: `LinkFox-Skill/2.0`
- **超时**: 150s
- **appType**: 本 skill **固定 `erp`**

## API Endpoints

### 1. Get Authorization URL

**Endpoint**: `tiktokShop/authorizeUrl`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| shopName | string | No | - | 店铺名称（展示用，最长 256） |
| region | string | No | `global` | `global` / `us` |
| appType | string | No | **`erp`（强制）** | 本 skill 始终传 `erp`；勿传 affiliate/creator |

**Response**:

```json
{
  "authorizeUrl": "https://services.tiktokshop.com/open/authorize?service_id=xxx&state=abc123"
}
```

> 授权 URL 约 1 小时有效；完成后 Token 由系统回调落库。

---

### 2. List Authorized Stores

**Endpoint**: `tiktokShop/authorizedStores`

**Request**: 无（当前用户上下文）。

网关可能返回多种 `appType`；**本 skill 脚本只保留 `appType=erp`** 并重算 `total`。

**Response（脚本过滤后）**:

```json
{
  "stores": [
    {
      "openId": "7010736057180325637",
      "sellerName": "Test Shop",
      "sellerBaseRegion": "ID",
      "appType": "erp",
      "region": "global"
    }
  ],
  "total": 1
}
```

---

### 3. Query Store Tokens（可选 / 调试）

**Endpoint**: `tiktokShop/storeTokens`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| openId | string | **Yes** | - | 卖家 open_id |
| appType | string | No | **`erp`（强制）** | 本 skill 始终传 `erp` |

**Response**:

| 字段 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 来源未说明 |
| openId | string | 卖家 open_id |
| appType | string | ERP 应用类型 |
| accessToken | string | 调用 TikTok Shop ERP 开放接口的凭证；仅记录响应契约，不得读取后展示、保存或转发 |
| refreshToken | string | 续签凭证；仅记录响应契约，不得读取后展示、保存或转发 |
| accessTokenExpireIn | integer | accessToken 过期 Unix 时间戳 |
| refreshTokenExpireIn | integer | refreshToken 过期 Unix 时间戳 |

> 只读库中令牌，**不**校验 `accessTokenExpireIn`，也**不**触发刷新。  
> ERP 业务 skill 调用 `tiktokShop/developerProxy` 时只需传 `openId`，**不必**先调本接口。

---

### 4. Refresh Token（可选手动）

**Endpoint**: `tiktokShop/refreshToken`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| openId | string | **Yes** | - | 卖家 open_id |
| appType | string | No | **`erp`（强制）** | 本 skill 始终传 `erp` |

**Response**:

| 字段 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 来源未说明 |
| accessToken | string | 调用 TikTok Shop ERP 开放接口的凭证；仅记录响应契约，不得读取后展示、保存或转发 |
| refreshToken | string | 续签凭证；仅记录响应契约，不得读取后展示、保存或转发 |
| accessTokenExpireIn | integer | accessToken 过期 Unix 时间戳 |
| refreshTokenExpireIn | integer | refreshToken 过期 Unix 时间戳 |
| message | string | 刷新结果消息 |

> **日常业务不要先手动刷新**。`developerProxy` 在上游 HTTP 401 或 token expired/invalid 时会自动调用刷新逻辑、回写数据库并重试一次。  
> 无按过期时间提前刷新、无定时任务。本接口仅供排查或用户明确要求。  
> `refresh_token` 过期后须重新走 authorizeUrl。

---

## ACCESS_TOKEN 后台化（业务 Agent 必读）

```
业务 skill  →  POST tiktokShop/developerProxy { openId, appType=erp, path, method, ... }
网关        →  按 openId+appType 从库取 accessToken（忽略 ttsAccessToken）
           →  转发上游；若 401 / token expired|invalid → refresh 一次并重试
           →  刷新成功则更新库中 accessToken / refreshToken / 过期时间
```

业务 skill **禁止**在每次调用前执行：`storeTokens` → 判断过期 → `refreshToken`。

---

## Error Codes

| errcode | 含义 | 建议动作 |
|---------|------|----------|
| 1002 | 参数校验失败 / 未登录 | 检查必填参数与认证 |
| 1003 | 上游异常 | 稍后重试 |
| 1004 | 授权记录不存在 / 无 refresh_token | 核对 openId 或重新授权 |
| 1005 | developerProxy path 未白名单 | 联系运维放行（业务 skill） |

脚本本地拒绝非 erp 的 `appType` 时直接 stderr 报错并 exit 1（不发网关请求）。

---

## MCP Examples

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`

```json
{
  "skillName": "linkfox-tiktok-shop-auth",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "ERP authorization flow worked smoothly."
}
```

---

## Important Notes

1. **仅 ERP**：`appType` 固定 `erp`。
2. **凭证隔离**：响应表中的凭证字段仅用于契约记录，不得读取后展示、保存或转发。
3. **过期字段**：`*ExpireIn` 为绝对 Unix 时间戳；业务侧不据此主动刷新。
4. **下游**：业务走 `linkfox-tiktok-shop-*` + `developerProxy(openId)`；token 后台化 + 401 自动刷新。
5. **达人分流**：creator → `linkfox-tiktok-video-auth`。
6. **手动 refresh**：仅排查或用户明确要求；勿作为业务前置步骤。
