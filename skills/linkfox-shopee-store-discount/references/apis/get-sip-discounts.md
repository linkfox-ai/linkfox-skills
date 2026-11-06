# 查询 SIP 跨境折扣 接口说明

公共规则中的 onboarding.md 指 [账号引导](../onboarding.md)。

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


## 接口：查询 SIP 跨境折扣（get_sip_discounts）

> 官方：[get_sip_discounts](https://open.shopee.com/documents/v2/v2.discount.get_sip_discounts?module=99&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐；脚本按真值选取并转成字符串。Discount 不适用免选店的 Public 接口约定。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；两者同时提供则均转发。 |
| path | string | 是（脚本自动） | 固定为 `api/v2/discount/get_sip_discounts`；必须以 `api/v2/discount/` 开头。 |
| method | string | 是（脚本自动） | 固定为 `GET`；外层 LinkFox HTTP 请求始终为 POST。 |
| queryString | string | GET 视业务需要 | 网关接收不含 `?` 的查询串；脚本按下方规则从顶层业务字段生成，不能将整个查询串当作脚本顶层 queryString 输入。 |
| body | string | 本操作不使用 | GET runner 不发送 body；底层兼容函数的 body 参数不属于本操作 CLI。 |
| contentType | string | 本操作不使用 | GET runner 将其视为保留字段，不传入查询串或网关请求体。 |

#### 脚本 JSON 补充参数

专用入口 `scripts/get_sip_discounts.py`；通用入口 `scripts/discount_api.py`。选店标识与 contentType 直接使用上表同名参数。路径和上游方法由注册表固定，不接受调用方替换。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口是 | 本接口值为 `get_sip_discounts`；专用脚本固定，无需传入。 |
| skipDepCheck | boolean | 否 | 默认 false；保留安装依赖检测开关，不作为授权依据。 |
| requestBody | JSON 值 | 本操作不使用 | GET runner 忽略此保留字段。 |
| 其他顶层业务字段 | string / number / boolean / null / object / array | 按上游操作 | 非保留字段的标量参与查询；null、对象和数组跳过。布尔值转小写，标量值按百分号 URL 编码。 |

业务参数放脚本 JSON 顶层，排除 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 后生成 `queryString`。null 跳过；布尔转为小写 true / false；对象和数组跳过；标量值逐个使用百分号 URL 编码（空格为 `%20`）。当前列表字段集合为空，不会把任意数组自动拼成字符串。`path`、`method`、`queryString` 不是 runner 的覆盖参数；若放在顶层也会成为同名上游查询参数，不应借此替换固定路径、方法或选店认证。

#### 已知上游业务字段与定义范围

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 其他 SIP 查询字段 | 标量，具体类型按 Shopee | 按上游操作 | 用于查询 SIP 折扣列表；具体字段、类型、默认值和枚举按官方文档准备，不臆造字段。 |

本节说明网关封装和脚本参数；Shopee 内部字段的类型、必填性、枚举、默认值及业务限制按本接口官方文档核对，响应内部结构按实际返回解释。运行参数、依赖退出码、环境变量兼容与无缓存约定见 [模块运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 存在时按公共规则判断；0 和 false 不代表空值或成功。 |
| errmsg | string | 网关消息，保留实际内容。 |
| httpStatus | integer | Shopee 上游状态码，与 LinkFox 外层 HTTP 状态不同。 |
| body | string | Shopee 原始 JSON 响应字符串；按下方业务规则解析。 |
| contentType | string / null | 上游响应 Content-Type。 |

#### 脚本加工响应

`developerProxy.error` / `developerProxy.details` 是公共调用器在连接失败或 HTTP 非 JSON 错误时生成的本地诊断信息，存在时原样保留；不属于网关保证的业务响应字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定为 `get_sip_discounts`。 |
| developerProxy | object | 完整网关响应，包括错误信息。 |
| resolvedPath | string | 固定为 `api/v2/discount/get_sip_discounts`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| queryString | string | 实际发送的非空查询串，仅 GET 有值时提供。 |
| getSipDiscounts | JSON 值 / null | Shopee body 整体解析结果，并非仅 response 子对象；空白、无效 JSON 或非字符串 JSON 值时为 null，未解析内容仍保存在 developerProxy.body。网关未正常响应或上游非 200 时不生成此字段。 |
| getSipDiscountsResponse | JSON 值 | 解析结果为对象且其 response 不为 null 时，提取 response；否则省略。 |
| getSipDiscounts.response | JSON 值 | 上游实际业务响应，内部字段按实际返回解释；不补造列表、计数或成功标记。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，仍须确认 `developerProxy.httpStatus` 为 200，再读取 `getSipDiscounts` / `getSipDiscountsResponse`。外层 2xx 不等于上游操作成功。
- 上游 body 中若含业务错误，按实际内容解释，不因 JSON 可解析或 response 存在就宣称写入完成；业务错误码按实际返回解释。
- 空白或无效 body 保留未解析内容，不自动重试、翻页或重复提交。写入结果不确定时先查询活动状态。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data-binary '{"path": "api/v2/discount/get_sip_discounts", "method": "GET", "shopId": "67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-discount",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
