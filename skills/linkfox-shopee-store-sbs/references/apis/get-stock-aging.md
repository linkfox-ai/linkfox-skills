# Shopee SBS 库龄报表 接口说明

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

## 接口：库龄报表（get_stock_aging）

> 官方：[get_stock_aging](https://open.shopee.com/documents/v2/v2.sbs.get_stock_aging?module=124&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/sbs/get_stock_aging`；相对路径必须以 `api/v2` 开头，SBS 使用 `api/v2/sbs/...`。 |
| method | string | 是 | 固定 `GET`，是 Shopee 上游方法；网关请求仍为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐；非空值在封装内转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；允许二者同时传入，均发送。 |
| queryString | string | 否 | 不含 `?` 的 URL 查询字符串；脚本由顶层业务字段构造，为空则不发送。 |
| body | string | 否 | 共享代理函数支持；本 GET 操作的业务入口不发送。 |
| contentType | string | 否 | 共享代理函数默认 `application/json`，仅发送 body 时带给网关；本 GET 操作省略。 |

#### 脚本 JSON 参数与 CLI 选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 同上。本 SBS 入口必须有店铺或商户标识，不支持省略二者的无店铺调用。 |
| merchantId | string | 与 shopId 至少一个 | 同上。 |
| api | string | 通用入口必填 | `sbs_api.py` 使用 `get_stock_aging`；专用入口已固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；已由外部确认依赖时可跳过本地安装检查，不绕过店铺授权。 |
| body / requestBody | string / object | 否 | 共享 runner 的 POST 请求体参数，本 GET 操作不读取，且不放进 queryString。 |
| contentType | string | 否 | 默认 `application/json`，GET 不发送。 |
| 其他顶层业务字段 | string / number / boolean / null / object / array | 否 | 标量逐项编码进入 queryString；布尔值为小写 true/false，null 跳过，object/array 跳过。业务字段按官方文档或已有用户数据提供，不能臆造必填项、默认值、分页或枚举。 |
| --inline | CLI flag | 否 | 强制完整打印加工后响应，同时落盘。 |
| --no-cache | CLI flag | 否 | 兼容公共选项；本入口始终禁用响应缓存。 |

#### 参数约束与使用限制

- 依赖已授权的目标店铺或商户，具体依赖检查、认证和缓存行为见 [模块运行约定](../api.md#脚本运行约定)。
- 服务端按 `shopId` 或 `merchantId` 解析并管理令牌；查询只需提供目标标识和业务字段。
- GET 业务字段放脚本 JSON 顶层；保留字段 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 不进入 Shopee query/body。
- 查询值使用百分号编码（空格为 `%20`，逗号、`&`、`/` 等均编码），键名按原值保留；本模块未注册列表查询字段，不把数组自动改成逗号列表。
- `queryString` 不是脚本保留键；若要手工提供完整查询串，应直接请求网关，不把完整串放入脚本顶层，否则它会被当成名为 queryString 的业务参数再次编码。
- 本操作为只读 GET；上游速率、分页上限及完整字段 schema 以官方文档和实际返回为准，不假定未经确认的限制或响应结构。

### 响应结构

#### 网关原始响应（脚本 developerProxy 内）

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 存在时按公共响应规则判断，不以单一成功枚举判断。 |
| errmsg | string（若返回） | 网关错误或业务消息。 |
| httpStatus | integer / string（若返回） | Shopee 上游 HTTP 状态；与 LinkFox HTTP 状态分开判断，解析层仅对 200 解析 body。 |
| contentType | string（若返回） | 上游响应的 Content-Type，与请求的 contentType 分开解释。 |
| body | string（若返回） | Shopee 原始 JSON 响应字符串；空白、缺失或无法解析时不产生有效业务数据。 |
| error | string（错误时可能返回） | 连接失败或非 JSON HTTP 错误信息，公共调用器保留。 |
| details | string（错误时可能返回） | 无法解析为 JSON 的 HTTP 错误响应体。 |
| 其他字段 | 原始类型 | 网关返回的其他字段按实际类型原样保留。 |

#### 脚本加工结果

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定 `get_stock_aging`。 |
| developerProxy | object | 原始网关响应，不丢失错误字段。 |
| resolvedPath | string | 固定 `api/v2/sbs/get_stock_aging`。 |
| transportHttpStatus | integer / null | LinkFox 网关 HTTP 状态；连接失败为 null，便于区分外层与上游状态。 |
| queryString | string（可选） | 非空时回显已编码查询串，无 `?`。 |
| requestBody | object / array / scalar / null（可选） | 共享 runner 的请求体回显；本 GET 操作不产生。 |
| getStockAging | object / array / scalar / null（可选） | Shopee body 的完整解析结果；仅网关正常且上游 httpStatus=200 时解析，空或非法 JSON 为 null。 |
| getStockAgingResponse | 原始 JSON 类型（可选） | 当完整解析结果为 object 且 response 非 null 时，保留其中 response。 |
| getStockAging.response | 原始 JSON 类型（若返回） | 内部业务字段、类型、必填、默认值或枚举以实际返回和官方文档为准，不补造字段。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共规则通过后，再检查 `developerProxy.httpStatus` 及 Shopee body 内实际错误；外层成功不代表上游或业务成功。
- 解析层仅在上游 httpStatus=200 时生成 `getStockAging`；它保留完整 body，不能把存在解析字段当成业务成功证据。
- 解析结果中的 response 非 null 时另给 `getStockAgingResponse`；空结果与零库存不能直接等同于网关故障，需结合实际字段解释。
- Shopee 返回 403 时按店铺或仓库权限问题处理。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/sbs/get_stock_aging","method":"GET","shopId":"67890"}'
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
