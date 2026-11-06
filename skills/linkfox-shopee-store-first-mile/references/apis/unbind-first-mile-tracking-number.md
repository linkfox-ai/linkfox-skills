# 解绑指定订单的头程运单号 接口说明

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

## 接口：解绑指定订单的头程运单号（unbind_first_mile_tracking_number）

> 官方：[unbind_first_mile_tracking_number](https://open.shopee.com/documents/v2/v2.first_mile.unbind_first_mile_tracking_number?module=96&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 本接口的 Shopee 相对资源路径，见下表；辅助函数要求以 `api/v2` 开头。 |
| method | string | 是 | Shopee 上游 HTTP 方法，见下表；调用 LinkFox 网关本身始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐；服务端据此解析已授权令牌。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；两个标识都提供时均保留。 |
| queryString | string | GET 按需 | 无 `?` 的查询串；各业务值须 URL 编码。 |
| body | string | 否 | Shopee 请求体的 JSON 字符串，与外层网关 JSON 区分；业务必填条件由上游决定，脚本 POST 入口仍要求提供 body 或 requestBody。 |
| contentType | string | 否 | 提供 body 时使用，默认 `application/json`。 |

#### 上游操作

| 项目 | 值 |
|---|---|
| method | `POST` |
| path | `api/v2/first_mile/unbind_first_mile_tracking_number` |
| 对应脚本 | `scripts/unbind_first_mile_tracking_number.py`（相对于技能根目录） |
| 用途 | 解绑指定订单的头程运单号。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐；本头程封装要求至少一个店铺或商户标识，不适用其他 Public 接口可省略标识的规则。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID。 |
| body | object / string | POST 是（与 requestBody 二选一） | 对象会转为紧凑 JSON 字符串；字符串原样转发，优先于 requestBody。 |
| requestBody | object / string | POST 是（与 body 二选一） | body 未提供时使用；对象编码规则与 body 相同。 |
| contentType | string | 否 | 默认 application/json。 |

POST 只使用 `body`、`requestBody` 或注册表 `body_fields` 指定的字段。本接口注册表未配置 `body_fields`，不能仅在顶层放业务字段；缺少请求体会在请求前报错。字符串请求体必须是合法 JSON，以保证输出中的 requestBody 可以解析。
`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为保留键，不作为 GET 业务查询字段；店铺标识不自动注入 Shopee body。本操作的具体 Shopee 请求体/业务查询字段、枚举和默认值须依据已取得的官方要求确定；本文仅定义网关与脚本封装，不凭空补造业务参数。官方文档 URL 规则为 `https://open.shopee.com/documents/v2/v2.first_mile.{api}?module=96&type=1`。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；外部流程已检查依赖时可跳过本地安装检查，不绕过店铺授权。 |
| api | string | 通用入口必填 | `scripts/first_mile_api.py` 使用接口名选取操作；独立脚本不需要。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 本技能无响应缓存，所有业务调用始终传入该选项，不读写响应缓存。公共调用器仍可能创建空缓存目录。 |

依赖检测成功退出 0；缺失退出 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-shopee-store-auth`。依赖探测支持多种安装目录及环境变量。
请求地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，最后 `https://tool-gateway.linkfox.com`。接口密钥兼容两种环境变量。请求头保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 的透传，超时 150 秒。
完整结果只写当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`；请求前验证可写性，不回退家目录或临时目录。业务封装始终禁用响应缓存；同一任务应避免重复调用。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按基础规则判断；错误值不因上游成功而忽略。 |
| errmsg | string | 网关消息或错误说明，以实际返回为准。 |
| httpStatus | integer / string | Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态区分；兼容值为 200 的数字或去除首尾空白后的字符串 "200"。 |
| body | string | Shopee 返回的 JSON 字符串；上游状态成功后解析。 |
| contentType | string | 上游响应内容类型（返回时保留）。 |
| error | string | 连接或 HTTP 错误等调用器错误信息（如返回）。 |
| details | string | 非 JSON HTTP 错误原始正文（如返回）。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本操作名 `unbind_first_mile_tracking_number`。 |
| developerProxy | object | 网关完整响应，包含上游状态及原始 body。 |
| resolvedPath | string | `api/v2/first_mile/unbind_first_mile_tracking_number`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | GET 有查询参数时输出实际查询串。 |
| requestBody | object / array / scalar / null | POST 的请求体 JSON 解码结果。 |
| unbindFirstMileTrackingNumber | object / array / scalar / null | 网关正常且上游 httpStatus 为 200 时解析的 Shopee 完整 body；空正文或解析失败为 null，不只代表 response 子对象。 |
| unbindFirstMileTrackingNumberResponse | object / array / scalar | 上述解析对象的 response 非 null 时额外输出，内容与上游一致。 |

#### Shopee body 观察字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | Shopee 业务错误标识（如返回），解析成功后仍需检查。 |
| message | string | Shopee 消息或错误说明（如返回）。 |
| request_id | string | Shopee 请求标识（如返回）。 |
| response | object / array / scalar / null | Shopee 业务响应，非 null 时额外输出对应的 Response 字段。 |

以上为需观察的上游字段，不保证存在；更深层业务字段以实际响应为准，不补造缺失字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 认证和算力异常按 [账号与算力指引](../onboarding.md) 处理。
- Shopee 上游 `httpStatus` 不为 200 或类型、格式异常时不解析为成功结果；保留原始网关响应，结合上游错误说明处理。body 为空、不是可解码的 JSON 字符串或 JSON 解析失败时，对应解析字段为 null，完整原值仍在 developerProxy 中。
- 解析出 body 不代表业务成功；仍须查看 Shopee 的 error/message 和实际订单级处理结果。本封装不定义专用错误码、重试次数或冷却时间；按实际返回错误和上游要求处理，不套用其他平台的保护码规则。
- 此操作仅解绑指定订单；不得自动切换为 unbind_first_mile_tracking_number_all。

### curl 示例

以下仅为网关封装结构示例，空 body 不能替代实际业务必填字段，必须补齐上游所需条件后使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-${SHOPEE_API_BASE_URL:-https://tool-gateway.linkfox.com}}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/first_mile/unbind_first_mile_tracking_number",
  "method": "POST",
  "shopId": "67890",
  "body": "{}",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-first-mile",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
