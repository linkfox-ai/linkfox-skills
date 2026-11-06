# Shopee 店铺授权状态查询辅助接口说明

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

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 二选一 | 店铺 ID，最长 64 字符；辅助函数将传入值转为字符串。 |
| merchantId | string | 与 shopId 二选一 | 商户 ID，最长 64 字符；两者都提供时辅助函数均发送，两者均无则本地退出 1，不发请求。 |
| appType | string | 否 | 直接网关请求可选 `erp` / `ad`，默认 `erp`。辅助函数只发送两个标识，不转发此参数，因此使用网关默认值。 |

公共脚本的 `resolve_store_tokens(params)` 提供此调用，分类 CLI 流程不自动调用；店铺授权与选店仍交由 `linkfox-shopee-store-auth`。该函数无独立 CLI；认证、兼容网关变量与无缓存约定见 [脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 / 返回值 | 类型 | 说明 |
|---|---|---|
| authRecordId | Long | 授权记录 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | Long | 授权有效期，单位秒；不是剩余时长保证。 |
| status | string | `ACTIVE` / `EXPIRED`；服务端按已存令牌是否非空生成，不单独证明下一次分类操作会成功。 |
| message | string | 授权状态说明。 |

接口返回授权状态，不返回原始令牌。辅助函数返回上述网关 JSON，不额外解析业务字段。

#### 本地附加字段

以下是公共调用器生成的诊断字段，不是网关业务字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 连接失败，或 HTTP 错误正文为空或不是有效 JSON 时的错误信息。 |
| details | string | HTTP 错误正文不是有效 JSON 时保留错误正文文本。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

查询仅限当前用户拥有的授权记录；未找到记录或记录不属于当前用户时返回错误。此辅助函数只返回原始授权状态数据，不替代授权技能，也不触发自动续期或重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
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
  "skillName": "linkfox-shopee-store-shop-category",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
