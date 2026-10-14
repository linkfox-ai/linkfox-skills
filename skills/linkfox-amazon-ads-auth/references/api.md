# linkfox-amazon-ads-auth — 参数与字段参考

Amazon Ads 授权、已授权账号列表、profile 管理与授权连接解绑。

下游实体查询见 `linkfox-amazon-ads-manager`；SP 报告见 `linkfox-amazon-ads-report`。

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST，`Content-Type: application/json`
- **Auth**：Header `Authorization: <api_key>`（读环境变量 `LINKFOX_AGENT_API_KEY`（优先）或 `LINKFOXAGENT_API_KEY`；如未配置 按 SKILL.md 的 **## 解决认证和算力问题** 处理）

- **解绑脚本**：`LinkFox-Skill/2.0`；透传 `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME`，超时 150s，不缓存、不自动重试。

## 关键 ID 关系

```
  一次 OAuth 授权
        ▼
  authRecordId (1 条 OAuth 授权连接)
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

### 4. 解绑广告连接 — `/amazonAds/cancelAuthorization`

**Request**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `authRecordId` | integer | 是 | 授权记录 ID，范围 1–9223372036854775807；不接受 profileId 替代 |

后端兼容纯数字字符串；脚本要求 JSON 整数。

**Response**：

```json
{
  "success": true,
  "authRecordId": 1001,
  "removedBindings": 1,
  "affectedProfileIds": [1111111111, 2222222222, 3333333333],
  "localAuthorizationRevoked": false,
  "amazonRevoked": false,
  "message": "已解除当前用户的指定广告授权绑定；token 与其他用户绑定保留，未撤销 Amazon 授权"
}
```

- 仅解除当前成员的整份连接（全部 profile），保留 token、profile 快照和其他成员绑定。
- 未绑定或重复解绑仍返回 `success=true`、`removedBindings=0`、`affectedProfileIds=[]`；两个 revoked 字段固定为 `false`。
- `affectedProfileIds` 表示被移除连接的范围；其他授权仍可能提供相同 profile 的访问。
- 已发出的请求和未完成的授权回调不受影响，后者可能恢复绑定。Amazon 官方撤销需原授权人通过广告后台的第三方应用管理进入 Login with Amazon 移除应用。

---

## 错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 200 | 成功 | — |
| 400 | 解绑参数格式错误 | 检查 authRecordId；整数溢出返回 1002 |
| 402 | 计费/算力不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和算力问题** 处理。 |
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

# 4. 解绑广告连接
curl -X POST $BASE/amazonAds/cancelAuthorization -H "Authorization: $KEY" \
  -H "Content-Type: application/json" -d '{"authRecordId":1001}'
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
