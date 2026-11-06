# Amazon Ads 授权与广告账户管理 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。授权接口也兼容旧版成功码整数 `0` 和字符串 `"0"`。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 不符合上述取值。布尔值 `false` 为无效业务码。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因
### 网关错误响应

成功对象与错误对象分别处理。错误模型仅含errcode（integer）与errmsg（string）；脚本记录的传输状态、计费头和本地错误见脚本参考。

接口仅管理当前API Key对应成员的授权。OAuth回调由系统内部保存授权并同步profile；业务操作通过profileId选择授权，原始Amazon凭证由服务端管理。

## 接口：生成授权链接（authorizeUrl）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/authorizeUrl`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE。 |
| accountName | string | 是 | 非空账户显示名，最长256字符，服务端去除首尾空白。 |

CLI选项和本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| authorizeUrl | string | 本次 OAuth URL，例如 https://sellercentral.amazon.com/ap/oa?...，必须完整保留。 |
| sourceType | string | 来源类型，示例值为 amazon_ads。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

OAuth 回调由系统处理，技能流程不手动调用。生成 URL 不证明授权成功；完成后以本次回调和只读授权记录核验。缺少账号名的错误示例：`{"errcode":1002,"errmsg":"缺少 accountName（账户显示名，必填非空）"}`。

错误时保留errmsg并按实际状态处理；不要补造未返回的业务结果。收到450 / 453 / 454 / 459时按[广告账号保护与重试](ads-protection.md)执行。

缺参数或身份异常返回1002；授权地址生成失败或配置异常返回1003。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazonAds/authorizeUrl \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region":"NA","accountName":"我的美国广告账号"}'
```

## 接口：列已授权账号（authorizedStores）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/authorizedStores`

### 请求参数

无业务参数，发送{}；成员身份来自API Key。

CLI选项和本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 已授权账号与站点条数，示例 3。 |
| stores | array<object> | 按 profileId 聚合去重，每个账号 × marketplace 一条；不能据此判断完整授权关系。 |
| stores[].profileId | integer（Long） | 下游广告业务操作使用的 profile 标识。 |
| stores[].accountInfoId | string | 广告主 entity 标识，跨 marketplace 稳定。 |
| stores[].accountInfoName | string | 广告账户名称，可能与紫鸟 storeName 不同。 |
| stores[].accountType | string | seller / vendor / agency。 |
| stores[].countryCode | string | 站点国家代码，例如 US。 |
| stores[].marketplaceStringId | string | marketplace 标识，例如 ATVPDKIKX0DER。 |
| stores[].region | string | NA / EU / FE。 |
| stores[].authRecordId | integer（Long） | OAuth 授权记录 ID，一次授权对应一条连接；不是 profileId。 |
| stores[].accountName | string | 发起授权时提供的账号显示名。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

列表用于选择账号与站点；按 profileId 聚合的去重结果不能证明某份连接已被完全移除。旧记录不能作为本次 OAuth 成功证据。

错误时保留errmsg并按实际状态处理；不要补造未返回的业务结果。收到450 / 453 / 454 / 459时按[广告账号保护与重试](ads-protection.md)执行。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazonAds/authorizedStores \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 接口：列广告 profile（profiles）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/profiles`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| refresh | boolean | 否 | 默认false读取DB快照；true时服务端尝试为当前成员绑定的授权重新同步profile。 |

CLI选项和本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | profile 条数，示例 3。 |
| refreshed | boolean | true表示本次执行了刷新尝试；同步失败也可能返回true，不能作为刷新成功证据。 |
| profiles | array<object> | 按绑定授权列出的profile快照；相同profile可能来自不同连接，不按profileId去重。 |
| profiles[].profileId | integer（Long） | 广告业务 profile 标识，例如 1111111111。 |
| profiles[].region | string | NA / EU / FE。 |
| profiles[].countryCode | string | 国家代码，例如 US。 |
| profiles[].currencyCode | string | 货币代码，例如 USD。 |
| profiles[].dailyBudget | string | 日预算，示例 "100.00"，保留字符串类型。 |
| profiles[].timezone | string | 时区，例如 America/Los_Angeles。 |
| profiles[].accountInfoId | string | 广告主 entity 标识，跨 marketplace 稳定。 |
| profiles[].accountInfoType | string | 广告账户类型，示例 seller。 |
| profiles[].accountInfoName | string | 广告账户名称，可能不同于授权显示名。 |
| profiles[].marketplaceStringId | string | marketplace 标识，例如 ATVPDKIKX0DER。 |
| profiles[].authRecordId | integer（Long） | OAuth 连接标识；用于确定整份连接的解绑范围。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

与 authorizedStores 相比，本接口用于连接范围和货币、时区、日预算等更细字段。解绑前读取快照，不使用 refresh=true；重新授权可能更新原记录，不能要求 profile 数量增加才能判成功。

错误时保留errmsg并按实际状态处理；不要补造未返回的业务结果。收到450 / 453 / 454 / 459时按[广告账号保护与重试](ads-protection.md)执行。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazonAds/profiles \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"refresh":true}'
```

## 接口：解绑广告连接（cancelAuthorization）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/cancelAuthorization`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| authRecordId | string | 是 | 授权记录ID的正整数文本，匹配^[1-9][0-9]{0,18}$，数值不超过9223372036854775807；解绑整份授权连接。 |

CLI选项和本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 本地解绑业务结果；只有 true 才表示已解除或原本不存在。 |
| authRecordId | integer（Long） | 本次解绑的授权记录 ID。 |
| removedBindings | integer | 移除绑定数；未绑定或重复解绑为 0，成功示例为 1。 |
| affectedProfileIds | array<integer（Long）> | 被移除连接覆盖的 profile 列表；未绑定或重复解绑为空数组。其他授权仍可能提供相同 profile 访问。 |
| localAuthorizationRevoked | boolean | 固定 false；保留 token 与 profile 快照。 |
| amazonRevoked | boolean | 固定 false；未撤销 Amazon 官方授权。 |
| message | string | 结果说明，例如“已解除当前用户的指定广告授权绑定；token 与其他用户绑定保留，未撤销 Amazon 授权”。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅解除 API Key 对应当前成员的整份连接及其全部 profile；共用成员身份的使用者都会受影响。保留 token、profile 快照与其他成员绑定。
- 未绑定或重复解绑仍返回 success=true、removedBindings=0、affectedProfileIds=[]；两个 revoked 字段始终为 false。
- 已发请求及未完成 OAuth 回调不受影响，后者可能恢复绑定。结果不确定先查询状态，不重放、不自动重新授权。
- Amazon 官方撤销需原授权人在广告后台的第三方应用管理中进入 Login with Amazon 移除应用；本接口不执行该操作。

错误时保留errmsg并按实际状态处理；不要补造未返回的业务结果。收到450 / 453 / 454 / 459时按[广告账号保护与重试](ads-protection.md)执行。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazonAds/cancelAuthorization \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"authRecordId":"1001"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-ads-auth",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
