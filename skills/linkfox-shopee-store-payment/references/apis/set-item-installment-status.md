# 设置商品分期状态 接口说明

模块导航与运行约定见 [../api.md](../api.md)。

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

## 接口：设置商品分期状态（set_item_installment_status）

> 官方：[set_item_installment_status](https://open.shopee.com/documents/v2/v2.payment.set_item_installment_status?module=97&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/payment/set_item_installment_status`，脚本按注册表填入；必须以 `api/v2` 开头，最长 2048 字符。 |
| method | string | 是 | 固定 `POST`，仅表示 Shopee 上游方法；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐使用；最长 64 字符，脚本转成字符串。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID，可与 shopId 同时传入；最长 64 字符。 |
| queryString | string | 否 | 其他查询字符串，无 `?` 前缀，最长 4096 字符；本操作为 POST，脚本不发送此字段。 |
| body | string | 否 | 网关可省略的上游请求正文，最长 1048576 字符；本操作脚本要求提供合法 JSON 的 body 或 requestBody。 |
| contentType | string | 否 | 默认 `application/json`，最长 128 字符；仅 body 不为 None 时发往网关。 |

#### 脚本 JSON 参数与 CLI

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 店铺 ID；Payment 脚本必须提供 shopId 或 merchantId，不适用 Public 无店铺操作的 ID 省略规则。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID。 |
| api | string | 仅通用入口是 | `payment_api.py` 取 `set_item_installment_status`；专用入口固定操作，不据此切换。 |
| skipDepCheck | boolean | 否 | 默认 false，仅外部流程已经确认依赖时跳过安装检测，不绕过授权。 |
| body | JSON value / string | POST 是，与 requestBody 二选一 | 上游 JSON 请求体，优先于 requestBody；字符串须为合法 JSON。保留对象、数组、标量及 null 的序列化能力，业务结构以官方文档为准。 |
| requestBody | JSON value / string | POST 是，与 body 二选一 | body 的兼容别名；不自动加入选店保留字段。 |
| contentType | string | 否 | 默认 `application/json`；GET 不使用。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘。 |
| --no-cache | CLI flag | 否 | 所有入口始终向公共 run 添加此选项，不读取或写入响应缓存。 |

#### 参数映射与使用限制

POST 先取 `body`，否则取 `requestBody`。注册表未配置 `body_fields`，顶层业务字段不会自动组装成 body；不能只传店铺 ID。

保留字段 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 不进入 GET query，也不自动混入 POST body。URL 编码、列表辅助函数、依赖返回码、网关地址兼容、认证及无缓存约定见 [运行约定](../api.md#运行约定)。本接口脚本为 `scripts/set_item_installment_status.py`，通用入口为 `scripts/payment_api.py`。

本参考定义网关封装、脚本实际处理及已知业务字段，不构成完整 Shopee 上游 schema；未列明的业务字段、必填、枚举、默认值或使用上限须按对应官方文档确认，不作推断。设置商品分期状态所需的具体业务请求和返回以该操作官方文档及实际响应为准。

### 响应结构

#### 网关原始响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断；与上游 httpStatus 独立。 |
| errmsg | string | 网关消息，错误时保留原文。 |
| httpStatus | integer | 网关 DTO 定义的 Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态独立；脚本另外兼容可转换的数字字符串，详见运行约定。 |
| contentType | string | 上游响应内容类型，按实际响应保留。 |
| body | string | Shopee 原始响应正文，通常为 JSON 字符串；完整业务结构以对应官方文档及实际响应为准，不补造字段。 |

#### 本地附加字段

以下字段由公共调用器在异常时生成，位于脚本输出的 `developerProxy` 内，不属于网关响应 DTO。

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 连接失败或无法取得 JSON 错误体时提供的说明。 |
| details | string | HTTP 错误响应无法解析为 JSON 时保留原文。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | `set_item_installment_status`。 |
| developerProxy | object | 完整网关响应，包括错误原文。 |
| resolvedPath | string | `api/v2/payment/set_item_installment_status`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | 仅实际发送非空查询串时返回，无 `?` 前缀。 |
| requestBody | JSON value / null | 仅 POST 返回，等于解析后的实际请求体。 |
| setItemInstallmentStatus | JSON value / null | 网关正常且上游 httpStatus 为 200 时解析 body；空体或无法解析为 null。 |
| setItemInstallmentStatusResponse | JSON value | 解析结果为对象且 response 非 null 时提取；不丢弃 false、0 或空列表。 |

先检查 `transportHttpStatus` 与 `developerProxy.errcode`，再检查 `developerProxy.httpStatus`，最后读取 `setItemInstallmentStatus` 和 `setItemInstallmentStatusResponse`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析业务成功；保留原始网关响应。Shopee `body` 内部业务错误仍需根据实际返回判断，不能只凭外层 HTTP 成功认定操作完成。 本操作修改分期设置，需核对用户指定的店铺或商品及目标状态；不自动重复提交状态不明的设置。
- `errcode=1002`：参数或未登录，核对店铺标识和 API Key；`1003`：代理或网络异常，后续请求遵守调用约束；`1004`：无授权记录，交由 `linkfox-shopee-store-auth`；`1005`：按错误原文区分；路径未白名单时核对 `api/v2/payment/...` 并由服务端确认放行，授权信息失效时交由认证技能重新授权。

### curl 示例

仅展示网关封装；必需业务条件须先按官方文档补齐，POST 的空对象不是可直接执行的完整请求。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "path": "api/v2/payment/set_item_installment_status",
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
  "skillName": "linkfox-shopee-store-payment",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
