# linkfox-amazon-ads-auth — 参数与字段参考

Amazon Ads 授权、已授权账号列表、profile 管理、令牌读取与刷新。

下游实体查询见 `linkfox-amazon-ads-entity`；SP 报告见 `linkfox-amazon-ads-report`。

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **Method**：POST，`Content-Type: application/json`
- **Auth**：Header `Authorization: <api_key>`（读环境变量 `LINKFOXAGENT_API_KEY`；未配置时引导用户到 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 关键 ID 关系

```
  一次 OAuth 授权
        ▼
  authRecordId (1 条)  ← 与 accessToken/refreshToken 绑定
        │
        ├──► profileId A (US)    ─┐
        ├──► profileId B (CA)    ├── 一次授权 → 多个 profile（每个 marketplace 一个）
        └──► profileId C (MX)    ─┘
```

- `authRecordId`：授权记录 ID，一次 LWA OAuth 对应一个
- `profileId`：业务操作单位；下游 skill 调用的核心参数
- `accountInfoId`：广告主 entity 级标识，跨 marketplace 稳定

## 接口

### 1. 生成授权 URL — `/amazonAds/authorizeUrl`

**Request**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `region` | string | 是 | `NA` / `EU` / `FE` |
| `accountName` | string | **是** | 非空字符串，用于在已授权列表识别 |

**Response**：
```json
{"authorizeUrl": "https://sellercentral.amazon.com/ap/oa?...", "sourceType": "amazon_ads"}
```

授权完成后 OAuth 回调由系统内部处理（存 token + 同步 profile），不作为公开接口。

---

### 2. 列已授权账号 — `/amazonAds/authorizedStores`

**Request**：无（用当前用户上下文）

**Response**：
```json
{
  "total": 3,
  "stores": [
    {
      "profileId": 1111111111,
      "accountInfoId": "ENTITY1ABC",
      "accountInfoName": "店铺 A",
      "accountType": "seller",
      "countryCode": "US",
      "marketplaceStringId": "ATVPDKIKX0DER",
      "region": "NA",
      "authRecordId": 1001,
      "accountName": "我的美国广告账号"
    }
  ]
}
```

按 profileId 聚合（每个账号 × marketplace 一条）。
`accountType` ∈ `seller` / `vendor` / `agency`。

---

### 3. 列 profile — `/amazonAds/profiles`

**Request**：
| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `refresh` | boolean | 否 | false | true=穿透上游重新拉取并落库；false=读本地快照 |

**Response**：
```json
{
  "total": 3, "refreshed": false,
  "profiles": [{
    "profileId": 1111111111, "region": "NA", "countryCode": "US",
    "currencyCode": "USD", "dailyBudget": "100.00",
    "timezone": "America/Los_Angeles",
    "accountInfoId": "ENTITY1ABC", "accountInfoType": "seller",
    "accountInfoName": "店铺 A",
    "marketplaceStringId": "ATVPDKIKX0DER",
    "authRecordId": 1001
  }]
}
```

与 `authorizedStores` 区别：前者面向"选账号 × 站点"粗粒度；本接口含货币、时区、日预算等业务字段。

---

### 4. 刷新令牌 — `/amazonAds/refreshToken`

`accessToken` 1 小时有效；过期后下游返回 HTTP 401 或错误体含 `expired` / `unauthorized` / `access token`。

**Request**（`authRecordId` 和 `profileId` 二选一）：
| 参数 | 类型 | 说明 |
|------|------|------|
| `authRecordId` | number | 授权主表 ID |
| `profileId` | number | 系统会反查到所属授权 |

**Response**：
```json
{
  "authRecordId": 1001,
  "accessToken": "Atza|IwEBI...", "refreshToken": "Atzr|IwEBI...",
  "tokenType": "bearer", "expiresIn": "3600",
  "message": "刷新成功"
}
```

---

### 5. 查询令牌 — `/amazonAds/storeTokens`

**Request**（二选一，同上）：`authRecordId` 或 `profileId`。

**Response**：同 §4，少了 `message` 字段。

本接口**不触发刷新**，仅读 DB。

---

## 错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 200 | 成功 | — |
| 1002 | 缺参数或认证失败 | 检查必填参数与 API Key |
| 1003 | 上游 Amazon Ads 调用失败 | 稍后重试 |
| 1004 | 授权记录不存在或不属于当前用户 | 核对 profileId / authRecordId |
| 1005 | profileId 权限校验失败 | 核对 profileId 归属 |

错误响应：
```json
{"errcode": 1002, "errmsg": "缺少 accountName（账户显示名，必填非空）"}
```

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

# 1. 生成授权 URL
curl -X POST $BASE/amazonAds/authorizeUrl -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"region":"NA","accountName":"我的美国广告账号"}'

# 2. 列已授权
curl -X POST $BASE/amazonAds/authorizedStores -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{}'

# 3. 列 profile（refresh=true 穿透刷新）
curl -X POST $BASE/amazonAds/profiles -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{"refresh":true}'

# 4. 刷新令牌
curl -X POST $BASE/amazonAds/refreshToken -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{"profileId":1111111111}'

# 5. 查令牌
curl -X POST $BASE/amazonAds/storeTokens -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{"profileId":1111111111}'
```

---

## Feedback API

与上面的工具 API **base URL 不同**：

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-amazon-ads-auth","sentiment":"POSITIVE",
       "category":"OTHER","content":"授权流程顺畅"}'
```

- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
