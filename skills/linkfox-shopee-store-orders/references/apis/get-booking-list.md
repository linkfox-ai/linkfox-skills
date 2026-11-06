# Shopee 查询预约列表接口说明

[模块导航](../api.md) · [技能入口](../../SKILL.md) · [认证与算力引导](../onboarding.md)

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

## 接口：查询预约列表（get_booking_list）

> 上游文档：[ get_booking_list ](https://open.shopee.com/documents/v2/v2.order.get_booking_list?module=94&type=1)。类型列中的“—”表示类型未明确限定，不据此推测类型。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 本接口的 api/v2/order/... 路径，不含域名，见下方。 |
| `method` | string | 是 | 本接口上游 GET / POST，见下方；网关自身始终 POST。 |
| `shopId` | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐使用；两者均提供时，兼容函数均转发。 |
| `merchantId` | string | 与 shopId 至少一个 | 已授权商户 ID；本模块不属于可省略选店的 Public 接口。 |
| `queryString` | string | GET 时 | 业务查询串，不含 ?；值须百分号编码。 |
| `body` | string | POST 时 | 上游请求体字符串。通常是 JSON；multipart 例外见对应接口限制。 |
| `contentType` | string | 否 | 默认 application/json；POST 存在 body 时脚本传入。 |

#### 上游方法与路径

- **Method**：`GET`
- **path**：`api/v2/order/get_booking_list`

紫鸟代理自动追加 `partner_id`、`timestamp`、`sign`；网关根据选店标识写入 `access_token`、`shop_id` 或 `merchant_id`，不在业务参数中重复拼装。

#### 脚本业务参数（GET Query）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `time_range_field` | string | 是 | create_time / update_time。 |
| `time_from` | integer | 是 | 起始 Unix 秒时间戳，与 time_to 的跨度不超过 15 天。 |
| `time_to` | integer | 是 | 结束 Unix 秒时间戳，与 time_from 的跨度不超过 15 天。 |
| `page_size` | integer | 是 | 每页条数。 |
| `cursor` | string | 否 | 分页游标；续页使用上次返回的游标。 |
| `booking_status` | string | 否 | READY_TO_SHIP / PROCESSED / SHIPPED / CANCELLED / MATCHED；page_size 的数值上限未明确限定。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `api` | string | 仅通用入口必需 | order_api.py 选择当前接口操作；专用脚本不需要。 |
| `skipDepCheck` | boolean | 否 | 默认 false，仅跳过本地安装检测，不绕过店铺授权。 |
| `--inline` | CLI flag | 否 | 强制完整打印，仍保存响应。 |
| `--no-cache` | CLI flag | 否 | 业务封装始终向公共 run 加入此项，不读写响应缓存；可能创建空缓存目录。 |

调用专用脚本 `scripts/get_booking_list.py` 或通用入口 `scripts/order_api.py`。GET 业务字段放脚本 JSON 顶层，布尔值编码为小写 true/false；除已定义的编号列表会用逗号连接外，字典和数组不会加入 queryString。网关选店及控制字段不进入上游 query。

依赖检测、兼容环境变量、无缓存与落盘约定见 [模块运行约定](../api.md#运行约定)。

#### 使用限制

time_from / time_to 时间跨度不超过 15 天。

### 响应结构

#### 网关响应

| 字段 | 类型 | 出现条件 | 说明 |
|---|---|---|---|
| `errcode` | integer / string / null | — | 网关业务状态码；按公共规则判断。 |
| `errmsg` | string | — | 网关消息或错误原因。 |
| `httpStatus` | integer | — | Shopee/紫鸟上游状态码，与 LinkFox 外层 HTTP 状态不同。 |
| `contentType` | string | — | 上游内容类型，例如 application/json。 |
| `body` | string | — | 上游原始响应；JSON 字符串通常包含 error、response。 |

#### 脚本输出字段

| 字段 | 类型 | 出现条件 | 说明 |
|---|---|---|---|
| `api` | string | — | 当前操作名：get_booking_list。 |
| `developerProxy` | object | — | 网关完整响应，见上表。 |
| `resolvedPath` | string | — | 实际转发路径。 |
| `transportHttpStatus` | integer / null | — | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| `queryString` | string | GET 有值时 | 实际编码查询串。 |
| `requestBody` | object / string / null | POST 时 | 实际请求体；JSON 可解析时为对象，否则保留字符串。 |
| `getBookingList` | object / array / scalar / null | 满足解析条件时 | Shopee body 的完整 JSON 解析值，不是 response 子对象。空或解析失败为 null。 |
| `getBookingListResponse` | — | response 存在且非 null 时 | 上游 JSON 的 response 子对象，保持上游实际类型。 |
| `getBookingListRaw` | string | JSON 解析失败时 | 保留无法解析的原始 body。 |

#### Shopee body 结构

| 字段 | 类型 | 出现条件 | 说明 |
|---|---|---|---|
| `error` | — | — | Shopee 业务错误标识；非空时不能视为操作成功。 |
| `response` | — | — | Shopee 业务数据；以实际返回结构为准，未明确列出的字段不补造。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层网关正常响应后，上游 `httpStatus` 为 200（兼容字符串 "200"）时才解析 body；解析出字段仅表示可读取，还须检查 Shopee `error`。上游非 200 时保留原始 developerProxy，不产生业务解析字段。请求完成不等于订单写入成功。

| 值 | 含义 | 处理 |
|---|---|---|
| errcode=1002 | 参数错误或未登录 | 检查选店标识及 API Key。 |
| 外层 HTTP 400 / errcode=400 | path、method 等请求校验失败 | 根据 errmsg 修正请求，不与上游 httpStatus=400 混淆。 |
| 外层 HTTP 503 / errcode=503 | 代理连接失败 | 保留错误，遵守调用约束，不自动重试写操作。 |
| errcode=1004 | 无授权记录 | 返回授权技能处理。 |
| errcode=1005 | path 未放行或授权已失效 | 依据 errmsg 区分；路径问题核对 api/v2/order/... 及白名单，授权失效则返回认证技能重新授权。 |
| 上游 400 | 路径错误 | 核对资源路径。 |
| 上游 403 | IP 白名单问题 | 核查代理白名单。 |
| 上游 408 | 超时 | 结果可能不确定，避免自动重复写入。 |
| 上游 5xx | 上游错误透传 | 保留原始错误，按任务范围处理。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/order/get_booking_list",
  "method": "GET",
  "shopId": "67890",
  "queryString": "time_range_field=update_time&time_from=1700000000&time_to=1700086400&page_size=20"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-orders",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
