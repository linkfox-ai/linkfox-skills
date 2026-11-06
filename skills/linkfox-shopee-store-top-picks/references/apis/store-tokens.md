# Shopee 店铺授权状态兼容查询 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：查询店铺授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 默认与说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，兼容函数将传入值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；两个标识都提供时都发送。 |
| appType | string | 否 | 网关默认 `erp`，枚举 `erp` / `ad`；Top Picks 使用 ERP 授权。兼容函数仅发送 shopId / merchantId，不转发 appType，使用网关默认值。 |

`scripts/_shopee_top_picks_common.py` 的 `resolve_store_tokens(params)` 供兼容调用方使用，不提供独立 CLI。该接口查询当前用户的店铺授权状态，不返回原始令牌。正常精选操作由服务端解析令牌，不额外调用该接口。API Key、网关别名、无缓存和敏感副本约定见 [运行约定](../api.md#运行约定)。授权由 `linkfox-shopee-store-auth` 负责。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按基础规则判断（若返回）。 |
| errmsg | string | 原始消息（若返回）。 |
| authRecordId | integer (Long) | 授权记录 ID。 |
| shopId / merchantId | string | 授权记录中的店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表的 JSON 字符串。 |
| appType | string | 授权应用类型：`erp` / `ad`。 |
| expireIn | integer (Long) | 授权记录中的 access_token 有效期秒数，不代表本次调用时的剩余有效期。 |
| status | string | `ACTIVE` / `EXPIRED`；服务端按授权记录中是否存在令牌判断，不等于 Top Picks 权限校验或实时可用性检测。 |
| message | string | 授权信息说明。 |
| error / details | string | 公共调用器遇到非 JSON HTTP 错误或连接错误时可能返回的详情。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 兼容函数原样返回内存 JSON 对象；保存副本仅保留白名单中的数值、布尔或 null 状态值，其余值隐藏，且不打印到 stdout。上表业务字段用于直接网关响应或内存消费，不能从隐藏副本恢复。
- 该响应是授权状态，不能当作精选集合列表或写入结果；不自动跨店重试。未找到当前用户所属授权记录时，网关返回 `1004`，使用 `linkfox-shopee-store-auth` 核对授权与选店。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-top-picks",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
