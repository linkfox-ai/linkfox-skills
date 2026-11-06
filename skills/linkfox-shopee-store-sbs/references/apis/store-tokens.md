# Shopee 授权状态辅助查询 接口说明

[模块索引与运行约定](../api.md) · [认证与算力引导](../onboarding.md)

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

## 接口：查询店铺或商户授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID；共享函数对非空值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；两者都非空时均发送。 |
| appType | string | 否 | 直接请求网关时可选 `erp` / `ad`，默认 `erp`；SBS 的 Python 辅助函数只发送 shopId、merchantId，使用网关默认值。 |

#### 使用限制

- 本接口由 `_shopee_sbs_common.py` 的 `resolve_store_tokens(params)` 提供，属于 Python 授权状态辅助能力，没有独立 CLI，也不是 `sbs_api.py` 支持的 api 值。
- 接口返回后台授权记录的状态信息，不返回原始令牌。正常五个 SBS 查询通过 shopId 或 merchantId 由服务端解析令牌，不提前调用此接口。
- 缺少店铺和商户标识时退出 1，且不发起请求；本函数本身不额外执行依赖检测，调用流程仍需先确认已授权目标。
- 使用模块的密钥、网关环境变量、会话头及无缓存行为，统一经 `call_api.run` 调用并保存结果。

### 响应结构

| 字段 / 层次 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer（Long） | 授权主表 ID。 |
| shopId / merchantId | string（若返回） | 店铺或商户 ID。 |
| shopIdList / merchantIdList | string（若返回） | 店铺或商户 ID 列表的 JSON 字符串。 |
| appType | string | 授权应用类型：`erp` / `ad`。 |
| expireIn | integer（Long） | 网关定义的 access_token 有效期，单位秒；不能据此推算查询时的剩余有效期。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`；服务端按已存 accessToken 是否非空赋值，不能据此保证 SBS 查询成功。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null（若返回） | 按公共响应规则处理。 |
| errmsg | string（若返回） | 网关消息或错误说明。 |
| error / details | string（若返回） | 公共调用器保留的连接或 HTTP 错误信息。 |

#### 脚本本地附加字段

函数保留网关 JSON 对象的字段，另附加 `transportHttpStatus`（integer / null）：LinkFox 网关 HTTP 状态，连接失败为 null。此字段由本地封装产生；直接调用网关不保证返回，判断时需同时检查该状态与实际 errcode。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 该操作返回授权状态，不代表 SBS 库存查询已经成功；后续查询仍需单独判断结果。
- 展示授权状态时仅使用本次实际返回的字段，不将授权记录作为库存数据。

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
  "skillName": "linkfox-shopee-store-sbs",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
