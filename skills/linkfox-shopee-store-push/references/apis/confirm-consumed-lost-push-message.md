# 确认消费丢失推送消息 接口说明

公共规则与 CLI 约定见 [模块参考](../api.md)。

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

## 接口：确认消费丢失推送消息（confirm_consumed_lost_push_message）

确认已经处理的补推消息；提交完整请求体。

官方文档：[confirm_consumed_lost_push_message](https://open.shopee.com/documents/v2/v2.push.confirm_consumed_lost_push_message?module=105&type=1)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/push/confirm_consumed_lost_push_message`，不得传主机名。 |
| method | string | 是 | 上游方法 `POST`；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺授权上下文；直接调用与业务脚本均需满足。网关读取后台授权令牌，并将此值作为上游查询参数 shop_id 转发。 |
| merchantId | string | 与 shopId 至少一个 | 商户授权上下文；网关将此值作为上游查询参数 merchant_id 转发。两者同时提供时均保留。 |
| queryString | string | 否 | 直接调用兼容字段，不含 `?`；本 POST 业务脚本不发送。 |
| body | string | 是 | 完整上游 JSON 字符串，由脚本 body 或 requestBody 构造。 |
| contentType | string | 有 body 时 | 默认 `application/json`。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 授权店铺 ID（推荐）；由网关解析授权并转发为上游 shop_id。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；两者同时提供时均转为字符串传入网关。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖安装检测。 |
| api | string | 通用入口必填 | 通用入口操作名：`confirm_consumed_lost_push_message`；独立脚本不需要。 |
| contentType | string | 否 | 默认 `application/json`；仅附带 body 时发送给网关。 |
| body | object / array / string / number / boolean / null | 与 requestBody 至少一个 | 完整上游请求体；非字符串值序列化为 JSON 字符串，字符串直接传入。兼容任意 JSON 值不代表上游接受该值，业务结构仍须符合官方定义。 |
| requestBody | object / array / string / number / boolean / null | 与 body 至少一个 | body 的兼容别名；两者同时出现时 body 优先，包括 body 为 null 或空字符串。 |
| 其他顶层字段 | JSON value | 否 | 本接口未声明 body_fields，忽略这些字段，不拼入查询串或请求体。 |

#### 参数约束与使用限制

POST 必须传完整 `body` / `requestBody`。runner 支持注册表 `body_fields` 顶层映射，但本接口没有声明 `body_fields`，不能把任意顶层字段当作请求体；缺少请求体时本地退出 1。非空字符串请求体必须是有效 JSON，在发送前验证；空字符串按兼容输入处理（发送空 body，输出 requestBody 为 null），不将其视为完整有效的业务配置。

保留字段用于网关选择或脚本控制，不自动注入显式 `body` 的业务内容；shopId / merchantId 由网关另行转发为上游 shop_id / merchant_id。上游业务字段、默认值、枚举、分页及限额以官方定义及实际返回为准；完整请求内容结合用户提供的信息确定，不补造参数或数值。Push 通常为 Partner/App 级，经本网关调用仍需至少一个授权上下文标识。选项 `--inline` 控制全量打印，`--no-cache` 可显式提供，封装始终禁用响应缓存。依赖、环境变量、追踪头与输出目录见模块参考。

### 响应结构

#### 网关原始响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；按公共规则判断，0 和 false 不视为空。 |
| errmsg | string | 网关错误或业务说明，按实际响应保留。 |
| httpStatus | integer / 数字字符串 | Shopee 上游 HTTP 状态，区别于 LinkFox 外层状态。 |
| contentType | string / null | Shopee 上游响应的 Content-Type。 |
| body | string | Shopee 原始 JSON 字符串；未声明的业务字段保持原样。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | `confirm_consumed_lost_push_message`。 |
| developerProxy | JSON value | 完整网关 JSON 响应，保留所有未列明字段；非对象 JSON 也原样保留。连接失败或非 JSON HTTP 错误时为公共调用器生成的本地诊断对象。 |
| resolvedPath | string | `api/v2/push/confirm_consumed_lost_push_message`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| developerProxy.error | string | 公共调用器在连接失败或非 JSON HTTP 错误时生成的本地错误说明（若有），不是网关保证返回的业务字段。 |
| developerProxy.details | string | 公共调用器在非 JSON HTTP 错误时保留的原始正文（若有）。 |
| requestBody | JSON value / null | POST 时返回解析后的提交体；空字符串为 null。 |
| confirmConsumedLostPushMessage | object / array / scalar / null | 网关正常响应且上游 httpStatus=200 时解析 body；空或无效 JSON 为 null，其他错误不生成此字段。业务子字段以实际返回为准。 |
| confirmConsumedLostPushMessageResponse | JSON value | 解析后的 Shopee 对象含非 null 的 response 时，原样提取。 |
| confirmConsumedLostPushMessage.response | JSON value | Shopee 业务 response；类型及子字段以实际返回为准。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层状态及 errcode，再看 `developerProxy.httpStatus`；上游非 200 不解析为业务结果（只接受数值 200 或去除空白后的字符串 "200"，不截断小数状态）。上游状态 200 时仍需阅读 Shopee 消息中的业务错误，不把存在解析对象当成操作成功。
- body 无法解析时返回对应解析字段 null，原始正文保留在 developerProxy.body；不补造成功结果。写入或消费确认结果不确定时，保留响应并核对状态，不自动重发。

### curl 示例

下例仅展示网关封装；调用前必须将 body 中的 `{}` 替换成符合官方定义的完整业务 JSON 字符串。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/push/confirm_consumed_lost_push_message","method":"POST","shopId":"67890","body":"{}","contentType":"application/json"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-push",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
