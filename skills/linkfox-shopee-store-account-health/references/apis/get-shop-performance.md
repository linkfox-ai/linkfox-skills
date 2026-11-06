# Shopee 店铺绩效总览 接口说明

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

## 接口：店铺绩效总览（get_shop_performance）

> 官方：[v2.account_health.get_shop_performance](https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1)

查询履约、商品刊登、客服等账户健康指标。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/account_health/get_shop_performance`，必须以 `api/v2` 开头；账户健康路径须属于 `api/v2/account_health/`。 |
| method | string | 是 | 固定 `GET`；网关外层仍使用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；由服务端解析已授权令牌。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；支持同时传入两个标识，不自动更换目标。 |
| queryString | string | 否（网关层） | 不带 `?` 的上游查询串；本操作所需业务字段与条件见脚本 JSON 参数。 |
| body | string | 否 | 共享代理封装保留的上游请求体；六个 GET 操作不传。 |
| contentType | string | 否 | 共享代理封装默认 `application/json`；仅有 body 时发送。 |

本接口无额外 Shopee 业务 query 参数。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 至少一个 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 至少一个 | 商户 ID |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口必填 | `scripts/account_health_api.py` 的操作名，允许六个账户健康操作；专用入口已固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI；本技能始终向 `call_api.run` 传入此选项，不读取或写入响应缓存。 |

业务参数放在 JSON 顶层，由脚本组成不含 `?` 的 `queryString`。`shopId`、`merchantId`、`skipDepCheck`、`api`、`body`、`requestBody`、`contentType` 为保留字段，不进入上游 query。普通标量按值百分号编码，布尔值转为小写，null 和对象、数组不进入 query；当前六个操作没有列表 query 字段。分页默认值由上游采用，脚本未显式传入时不主动补值。

`body` / `requestBody` / `contentType` 为共享调用器的兼容选项，六个 GET 操作不发送请求体；不要用它们代替顶层业务参数。通用入口不接受原始代理 path，只允许已登记的六个操作。

依赖检测、网关环境变量、认证与当前工作目录输出约定见 [公共运行约定](../api.md#运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断。 |
| errmsg | string | 网关消息，错误时用于解释原因。 |
| httpStatus | integer | Shopee 上游状态码，与外层 LinkFox HTTP 状态不同。 |
| contentType | string | 上游响应内容类型。 |
| body | string | Shopee 原始 JSON 字符串，业务字段完整保留于此。 |

#### 本地错误附加字段

公共调用器在 HTTP 错误正文为空、无法解析为 JSON 或连接失败时，可能在脚本输出的 `developerProxy` 中构造下列字段；它们不是网关成功响应的固定字段。HTTP 错误若带有有效 JSON，则保留该 JSON；外层状态另见 `transportHttpStatus`。

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 本地构造的 HTTP 错误或连接失败说明。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留的原始正文；并非必返。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次账户健康操作名。 |
| developerProxy | object | 上述完整网关响应；错误时也保留。 |
| resolvedPath | string | 实际转发的相对路径。 |
| queryString | string | 非空时输出实际发送的无问号查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| getShopPerformance | JSON 值 / null | 外层正常且上游状态为 200 时解析的完整 Shopee body，并非只取其中 response；body 为空或 JSON 无效时为 null。异常网关或上游状态时不生成。 |
| getShopPerformanceResponse | object / array / 以实际返回为准 | 仅在解析对象的 response 非 null 时输出该值；实际类型由上游决定。 |

下列业务字段位于 `getShopPerformance.response`（同时映射为 `getShopPerformanceResponse`）。以下仅列出常见业务字段，不构成完整上游 schema；标注“以实际返回为准”的字段不预设类型或必返性，不补造字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| overall_performance | object | 店铺健康总览。 |
| overall_performance.rating | 以实际返回为准 | 总体评级。 |
| overall_performance 中各类 failed 计数 | 以实际返回为准 | 各维度未达标数量；具体字段名以实际返回为准。 |
| metric_list | array | 绩效指标列表。 |
| metric_list[].metric_id | int | 指标 ID，可交给指标来源明细查询。 |
| metric_list[].metric_name | 以实际返回为准 | 指标名称。 |
| metric_list[].current_period | 以实际返回为准 | 当前周期指标。 |
| metric_list[].last_period | 以实际返回为准 | 上一周期指标。 |
| metric_list[].target | 以实际返回为准 | 目标值。 |
| metric_list[].unit | 以实际返回为准 | 指标单位。 |

#### 常用 `metric_id`（节选）

| ID | 含义 |
|----|------|
| `1` | 延迟发货率（Late Shipment Rate） |
| `3` | 未履约率（Non-Fulfilment Rate） |
| `12` | 预售商品刊登占比（Pre-order Listing %） |
| `25` | 快速交接率（Fast Handover Rate） |
| `42` | 取消率（Cancellation Rate） |
| `43` | 退货退款率（Return-refund Rate） |
| `52` | 严重商品刊登违规（Severe Listing Violations） |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层响应正常后，再检查 `developerProxy.httpStatus`；上游状态为 200 才解析 Shopee body，不把网关转发完成直接视为业务成功。
- Shopee 业务错误按 body 中的实际错误码与消息解释；保留 body 的完整内容，不将 JSON 可解析直接视为健康或无处罚。
- 上游 body 为空或非有效 JSON 时，解析字段为 null，原始 body 保留在 `developerProxy`；上游非 200 或网关失败时不生成解析字段。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "path": "api/v2/account_health/get_shop_performance",
    "method": "GET",
    "shopId": "67890"
  }'
```

更多公共运行约定、接口索引与 [Feedback](../api.md#Feedback) 见 [模块参考](../api.md)。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-account-health",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
