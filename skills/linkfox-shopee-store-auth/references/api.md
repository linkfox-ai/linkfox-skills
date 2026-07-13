# linkfox-shopee-store-auth — 参数与字段参考

Shopee 授权、已授权店铺列表、令牌读取。

业务 API 转发见 `/shopee/developerProxy`（path 须以 `api/v2` 开头）。

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST，`Content-Type: application/json`
- **Auth**：Header `Authorization: <api_key>`（读环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`；如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 关键 ID 关系

```
  一次 OAuth 授权
        ▼
  authRecordId (1 条)  ← 与 accessToken/refreshToken 绑定
        │
        ├──► shopId      ─┐
        └──► merchantId  ─┘  查询令牌时二选一即可
```

- `authRecordId`：授权记录 ID，一次 OAuth 对应一个
- `shopId`：店铺 ID，转发 Shopee API 时写为 `shop_id`
- `merchantId`：商户 ID，与 `shopId` 二选一；转发时写为 `merchant_id`
- `shopIdList` / `merchantIdList`：JSON 字符串，含本次授权绑定的全部 ID

## 接口

### 1. 生成授权 URL — `/shopee/authorizeUrl`

服务端自动组装 `state`、`callbackUrl`、`redirectUrl`。

**Request**：
| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `shopName` | string | 否 | - | 店铺展示名，便于在列表识别 |
| `region` | string | 否 | `cn` | `cn` / `global` / `br` |

**Response**：
```json
{"sourceType": "shopee", "authorizeUrl": "https://open.shopee.cn/auth?...&state=abc123"}
```

授权完成后 Token 由 Shopee POST 到 `/shopee/oauth/tokenCallback`（系统内部）；浏览器跳转 `/shopee/oauth/redirect`，不作为公开接口。

---

### 2. 列已授权店铺 — `/shopee/authorizedStores`

**Request**：无（用当前用户上下文）

**Response**：
```json
{
  "total": 1,
  "stores": [{
    "authRecordId": 1,
    "shopId": "67890",
    "merchantId": "12345",
    "shopIdList": "[67890]",
    "merchantIdList": "[12345]",
    "shopName": "Test Shopee Shop",
    "region": "cn"
  }]
}
```

---

### 3. 查询令牌 — `/shopee/storeTokens`

**Request**（`shopId` 与 `merchantId` 二选一）：
| 参数 | 类型 | 说明 |
|------|------|------|
| `shopId` | string | 店铺 ID |
| `merchantId` | string | 商户 ID |

**Response**：
```json
{
  "authRecordId": 1,
  "shopId": "67890",
  "merchantId": "12345",
  "shopIdList": "[67890]",
  "merchantIdList": "[12345]",
  "tokenType": "Bearer",
  "accessToken": "xxx",
  "expireIn": 14400,
  "refreshToken": "xxx"
}
```

本接口**不触发刷新**，仅读 DB。`expireIn` 为 access_token 剩余有效秒数（通常 14400）。

返回的 `accessToken` 可交给 `/shopee/developerProxy` 调用 Shopee 开放接口。

---

## 错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 200 | 成功 | — |
| 1002 | 参数错误或未登录 | 检查必填参数与 API Key |
| 1003 | 授权服务异常或网络失败 | 稍后重试 |
| 1004 | 授权记录不存在或不属于当前用户 | 核对 shopId / merchantId |
| 1005 | 转发路径未在白名单内（developerProxy） | path 须以 `api/v2` 开头 |

错误响应：
```json
{"errcode": 1004, "errmsg": "未找到授权记录"}
```

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

# 1. 生成授权 URL
curl -X POST $BASE/shopee/authorizeUrl -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"shopName":"我的虾皮店铺","region":"cn"}'

# 2. 列已授权
curl -X POST $BASE/shopee/authorizedStores -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{}'

# 3. 查令牌
curl -X POST $BASE/shopee/storeTokens -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{"shopId":"67890"}'
```

---

## Feedback API

与上面的工具 API **base URL 不同**：

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-auth","sentiment":"POSITIVE",
       "category":"OTHER","content":"授权流程顺畅"}'
```

- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
