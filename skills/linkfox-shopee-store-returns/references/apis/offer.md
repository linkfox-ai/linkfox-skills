# 提出解决方案 接口说明

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

## 接口：提出解决方案（offer）

> 官方：[offer](https://open.shopee.com/documents/v2/v2.returns.offer?module=102&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/returns/offer`。 |
| method | string | 是 | 上游方法固定 `POST`；LinkFox 网关仍用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，支持兼容调用。 |
| queryString | string | 否 | 本操作的脚本不生成此项；业务内容通过 body 转发。 |
| body | string | 否（脚本 POST 必传） | 网关字段可选；本操作脚本必须通过 body / requestBody 提供完整业务请求的 JSON 字符串。 |
| contentType | string | 否 | 默认 application/json，脚本随 body 传入。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，店铺级操作推荐传入；封装不将此保留字段拼入业务 query/body，网关另注入上游 shop_id 查询参数。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；封装允许同时提供两者，网关另注入上游 merchant_id 查询参数。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地依赖探测，不绕过服务端店铺授权。 |
| api | string | 仅通用入口必填 | 通用入口取值 `offer`；独立脚本固定本操作，忽略传入的 api 值。不会传入上游。 |
| contentType | string | 否 | 默认 application/json，随 body 转发。 |
| body | JSON value / JSON string | 与 requestBody 至少一个 | 优先于 requestBody；非字符串值序列化为紧凑 JSON，字符串按原样转发，但内容须是合法 JSON。脚本接受 JSON 值不代表上游接受任意结构，完整业务内容仍须符合本操作要求。 |
| requestBody | JSON value / JSON string | body 不存在时使用 | body 的兼容别名；处理方式相同。 |
| body.* / requestBody.* | 依上游字段 | 依上游字段 | 嵌套字段、类型、默认值和枚举依本操作官方文档与任务所需准备，不补造字段定义。 |
| 顶层业务字段 | 依上游字段 | 不代替 body | 注册表支持 body_fields 提取，但本操作未配置 body_fields；必须传 body / requestBody，不能仅把业务字段放顶层。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 保存后强制全量打印。 |
| --no-cache | CLI flag | 否 | 兼容 CLI 选项；业务封装始终传此项，不读写响应缓存。 |
| --help | CLI flag | 否 | 显示本地帮助，不请求接口。 |

入口为 `scripts/offer.py`；也可用 `scripts/returns_api.py` 并传 `api: "offer"`。
依赖探测返回 42 时先安装并授权 `linkfox-shopee-store-auth`，不另写令牌逻辑。网关地址兼容 `SHOPEE_API_BASE_URL`；其他认证、保存与重试约定见 [运行约定](../api.md#运行约定)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | LinkFox 业务码，按公共基本规则判断。 |
| errmsg | string | 网关消息或错误原因。 |
| httpStatus | integer | Shopee 上游状态，区别于 LinkFox 外层 HTTP 状态。 |
| contentType | string | 上游响应内容类型，按实际返回展示。 |
| body | string | Shopee 原始响应 JSON 字符串；保留原始响应内容，不以存在 body 判定成功。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定 offer。 |
| developerProxy | object | 完整网关响应，保留错误与原始 body。 |
| resolvedPath | string | 实际转发路径 `api/v2/returns/offer`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| requestBody | JSON value / null | 回显解析后的请求体。 |
| offer | JSON value / null | 外层响应正常且上游 httpStatus 为 200 时解析的完整 Shopee body；空或不可解析时为 null。此字段不是 response 子对象。 |
| offerResponse | 依上游 response 类型 | 仅解析对象含非 null response 时，从 offer.response 提取。内部业务字段以实际响应及本操作官方文档为准。 |

#### 本地附加字段

`developerProxy.error` 和 `developerProxy.details` 可能由公共调用器在 HTTP 或连接异常时生成；`details` 保留无法解析为 JSON 的 HTTP 错误正文。这些诊断字段不是网关成功响应字段，外层状态以 `transportHttpStatus` 为准。

先判断状态，再读 `offer` 和可用的 `offerResponse`；上游完整字段以实际响应及本操作官方文档为准，不将未列明的业务字段当作固定契约。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `developerProxy.httpStatus` 是 Shopee 上游状态，只有 200 时解析业务 JSON；仍须检查解析结果中的 Shopee 错误，不把网关正常响应当作退货处理成功。
- 网关或上游失败时不提取为成功业务对象，保留原响应供核对；写入结果不确定时先核对退货状态，避免重复执行。

| 错误码 | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 核对 shopId / merchantId 与 API Key。 |
| 1003 | 代理或网络异常 | 保留错误；后续重试遵守调用约束，不自动连续试探。 |
| 1004 | 无授权记录 | 使用 `linkfox-shopee-store-auth` 完成目标店铺授权。 |
| 1005 | path 未加入白名单 | 核对 `api/v2/returns/...` 并确认服务端放行。 |

### curl 示例

以下为请求结构示意；占位符须替换，复杂 POST 的完整业务字段应按本操作准备，不能把示意 body 当成完整业务请求。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/returns/offer",
  "method": "POST",
  "shopId": "67890",
  "body": "{\"<官方业务字段>\":\"<业务值>\"}",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-returns",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
