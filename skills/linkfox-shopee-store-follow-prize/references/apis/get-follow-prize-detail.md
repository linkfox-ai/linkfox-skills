# Shopee 查询关注有礼详情 接口说明

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

## 接口：查询关注有礼详情（get_follow_prize_detail）

> 官方：[v2.follow_prize.get_follow_prize_detail](https://open.shopee.com/documents/v2/v2.follow_prize.get_follow_prize_detail?module=113&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 固定为 `api/v2/follow_prize/get_follow_prize_detail`，不带主机名前缀；公共辅助函数校验以 `api/v2` 开头。 |
| method | string | 是 | 固定为 `GET`，为 Shopee 上游方法；LinkFox 网关请求始终使用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐；脚本转为字符串。若两者都传则都转发。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；脚本转为字符串。与 shopId 至少提供一个；两者都有值时均转发，不做互斥校验。 |
| queryString | string | GET 按需 | 不带 `?` 的查询串。 |
| body | string | 本操作不使用 | 活动 GET 脚本不发送 body。 |
| contentType | string | 本操作不使用 | 活动 GET 脚本不发送 contentType。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；Follow Prize 不是可省略店铺的 Public 接口。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID。 |
| api | string | 仅通用入口必填 | `follow_prize_api.py` 传 `get_follow_prize_detail`；单操作脚本固定选择该操作。 |
| contentType | string | 否 | 默认 `application/json`，仅对 POST body 生效。 |
| 其他业务字段 | string / number / boolean | 按操作 | 顶层非保留字段作为查询参数；标量编码后拼接（包括空字符串和 0）；boolean 转为小写 true/false，null 跳过，object/array 跳过。无默认分页值或状态枚举注入。 |
| campaign_id | 标量（具体类型按上游要求） | 按上游要求 | 按 campaign_id 指定活动并查询详情，脚本原样进行查询值编码。 |

GET 查询值使用百分号编码（`quote(..., safe="")`），无 `?` 前缀。当前 `LIST_QUERY_FIELDS` 为空，不应用通用 helper 的最多 50 项逗号列表规则。

网关选店和脚本控制字段 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为保留字段，不作为 Shopee GET query；POST 仅使用显式 body/requestBody，不混入这些顶层字段。令牌由服务端按已授权店铺解析，无需提供原始令牌；GET 顶层仅放该操作的业务查询字段。

#### 脚本选项与运行约定

依赖检查、认证兼容、CLI 选项、输出目录和无缓存约定见 [脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 业务码，按公共基本规则判断。 |
| errmsg | string | 网关消息或失败原因，实际返回为准。 |
| httpStatus | integer / 数字字符串 | Shopee 上游状态，与外层 HTTP 状态不同；脚本仅在转换为整数后等于 200 时解析 body。 |
| contentType | string | Shopee 上游响应的 Content-Type。 |
| body | string | Shopee 返回的 JSON 字符串；完整业务字段以实际返回为准。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | 固定为 `get_follow_prize_detail`。 |
| developerProxy | object | 网关原始完整响应，包括错误。 |
| resolvedPath | string | 实际上游 path：`api/v2/follow_prize/get_follow_prize_detail`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| developerProxy.error | string | 公共调用器在连接失败或非 JSON HTTP 错误时生成的本地诊断，非网关成功响应字段。 |
| developerProxy.details | string | 公共调用器保留的非 JSON HTTP 错误正文，存在时输出，非网关成功响应字段。 |
| queryString | string | 实际查询串；非空时输出。 |
| requestBody | JSON 值 / string / null | 发送了 body 时回显；可解析时输出解析值，否则保留原始字符串，空串为 null。 |
| getFollowPrizeDetail | JSON 值 / null | 网关正常且上游 httpStatus 为 200 时解析 Shopee body；空 body 或 JSON 解析失败为 null，其他失败不新增此字段。 |
| getFollowPrizeDetailResponse | JSON 值 | 当上述解析结果为 object 且 response 非 null 时，保留其 response 子对象；原始外壳仍保留在 getFollowPrizeDetail。 |

Shopee `response` 的内部字段以实际返回为准；保留真实嵌套对象，不预设未知字段的 schema。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层符合基础规则后，仅 `developerProxy.httpStatus` 转为整数等于 200 时解析活动业务结果。解析成功不代表活动变更已经成功，仍需阅读 Shopee body 中的业务消息。
- 上游非 200、空 body 或无法解析时保留原始响应，不将错误包装为活动成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path": "api/v2/follow_prize/get_follow_prize_detail", "method": "GET", "shopId": "67890", "queryString": "campaign_id=12345"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-follow-prize",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
