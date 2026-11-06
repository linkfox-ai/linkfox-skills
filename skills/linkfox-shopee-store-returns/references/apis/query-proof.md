# 查询退货凭证 接口说明

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

## 接口：查询退货凭证（query_proof）

> 官方：[query_proof](https://open.shopee.com/documents/v2/v2.returns.query_proof?module=102&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/returns/query_proof`。 |
| method | string | 是 | 上游方法固定 `GET`；LinkFox 网关仍用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，支持兼容调用。 |
| queryString | string | 否 | 上游查询串，不含 ?；业务所需条件见下表。脚本从顶层业务标量字段生成，不接收预拼接查询串。 |
| body | string | 否 | 本操作为 GET，不传。 |
| contentType | string | 否 | 本操作不传 body，脚本不发送此项；网关请求头仍为 application/json。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，店铺级操作推荐传入；封装不将此保留字段拼入业务 query/body，网关另注入上游 shop_id 查询参数。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；封装允许同时提供两者，网关另注入上游 merchant_id 查询参数。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地依赖探测，不绕过服务端店铺授权。 |
| api | string | 仅通用入口必填 | 通用入口取值 `query_proof`；独立脚本固定本操作，忽略传入的 api 值。不会传入上游。 |
| contentType | string | 否 | 保留字段；GET 脚本忽略，不进入 queryString。 |
| body / requestBody | 任意 JSON 值 | 否 | 保留字段；GET 脚本忽略，不进入 queryString，也不生成上游 body。 |
| 其他业务标量字段 | string / number / boolean | 依上游字段 | 放 JSON 顶层；排除保留字段和 null；布尔值变为小写 true/false，值进行百分号编码；dict/list 跳过。不自动添加默认值。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 保存后强制全量打印。 |
| --no-cache | CLI flag | 否 | 兼容 CLI 选项；业务封装始终传此项，不读写响应缓存。 |
| --help | CLI flag | 否 | 显示本地帮助，不请求接口。 |

入口为 `scripts/query_proof.py`；也可用 `scripts/returns_api.py` 并传 `api: "query_proof"`。
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
| api | string | 固定 query_proof。 |
| developerProxy | object | 完整网关响应，保留错误与原始 body。 |
| resolvedPath | string | 实际转发路径 `api/v2/returns/query_proof`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | 仅实际存在查询串时返回；不带问号。 |
| queryProof | JSON value / null | 外层响应正常且上游 httpStatus 为 200 时解析的完整 Shopee body；空或不可解析时为 null。此字段不是 response 子对象。 |
| queryProofResponse | 依上游 response 类型 | 仅解析对象含非 null response 时，从 queryProof.response 提取。内部业务字段以实际响应及本操作官方文档为准。 |

#### 本地附加字段

`developerProxy.error` 和 `developerProxy.details` 可能由公共调用器在 HTTP 或连接异常时生成；`details` 保留无法解析为 JSON 的 HTTP 错误正文。这些诊断字段不是网关成功响应字段，外层状态以 `transportHttpStatus` 为准。

先判断状态，再读 `queryProof` 和可用的 `queryProofResponse`；上游完整字段以实际响应及本操作官方文档为准，不将未列明的业务字段当作固定契约。

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
  "path": "api/v2/returns/query_proof",
  "method": "GET",
  "shopId": "67890"
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
