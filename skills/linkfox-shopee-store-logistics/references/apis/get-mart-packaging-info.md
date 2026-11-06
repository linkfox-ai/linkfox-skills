# 查询 Mart 包装信息 接口说明

[模块导航](../api.md)；对应脚本：`scripts/get_mart_packaging_info.py`。官方：[v2.logistics.get_mart_packaging_info](https://open.shopee.com/documents/v2/v2.logistics.get_mart_packaging_info?module=95&type=1)。

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

## 接口：查询 Mart 包装信息（get_mart_packaging_info）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定为 `api/v2/logistics/get_mart_packaging_info`，不含主机名前缀。 |
| method | string | 是 | 固定为 `GET`，是 Shopee 上游方法；网关请求仍为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，通常推荐使用；物流脚本不存在可省略两个标识的 Public 操作。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID。两个标识都传时均保留。 |
| queryString | string | 按业务需要 | 业务查询串，无 ? 前缀，值使用百分号编码；脚本自动生成。 |
| body | string | 否 | 本接口脚本不发送 body。 |
| contentType | string | 否 | 通常省略。 |

#### 脚本 JSON 参数与选项

| 字段或选项 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 对应网关店铺标识。 |
| merchantId | string | 与 shopId 至少一个 | 对应网关商户标识。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过已由外部确认的本地依赖检查。 |
| api | string | 仅通用入口必填 | 固定 `get_mart_packaging_info`；独立脚本已确定操作。 |
| --inline | CLI flag | 否 | 强制全量输出，同时落盘。 |
| --no-cache | CLI flag | 否 | 封装始终传入，不缓存响应。 |
| 其他顶层业务字段 | string / number / boolean | 依上游要求 | 排除保留字段后生成 queryString；布尔值使用小写 true/false，null 忽略。除下行列表外，object/array 不自动发送。 |
| order_sn_list | string / string[] | 按业务需要 | 如本操作需要该字段，支持逗号串或数组，去空白及空项后逗号连接；1–50 项，其他类型、空列表或超过 50 项在本地报错。 |

GET 业务参数位于脚本 JSON 顶层；`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为保留字段，不进入 Shopee query。查询值统一 URL 编码，逗号也编码为 `%2C`。

本表未穷举本操作所有 Shopee 嵌套字段、枚举、默认值或站点限制；按本页官方文档与前置查询结果准备完整业务参数，不能将未列出的字段视为可省略。环境变量、依赖与无缓存约定见 [模块运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，依公共规则判断；不存在或为空的处理也依公共规则。 |
| errmsg | string | 网关错误或状态说明。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与外层 LinkFox HTTP 状态不同。 |
| contentType | string | 上游响应内容类型；下载面单时保留原值。 |
| body | string | 上游原始内容，可能为 JSON 或不可直接解析的面单数据。 |
| error | string | HTTP 或连接错误时的兼容错误信息。 |
| details | string | HTTP 错误的原始响应详情（如有）。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定 `get_mart_packaging_info`。 |
| developerProxy | object | 完整网关响应，保留错误。 |
| resolvedPath | string | 固定 `api/v2/logistics/get_mart_packaging_info`。 |
| transportHttpStatus | integer / null | 外层 LinkFox HTTP 状态；连接失败为 null。 |
| queryString | string | 仅实际存在查询参数时输出，无 ? 前缀。 |
| requestBody | any | 仅发送 body 时输出解析后的完整业务请求体。 |
| getMartPackagingInfo | any / null | 外层网关正常且上游 httpStatus 为 200 时解析 body；空内容或解析失败为 null，非 200 时不生成。 |
| getMartPackagingInfoResponse | any | 仅解析结果为对象且 response 不为 null 时提取该字段；0、false、空对象和空数组均保留。 |

上述操作响应键中的 Shopee 业务字段及嵌套结构以实际返回为准；按真实返回展示，不补造运单号、任务 ID 或成功状态。下载函数保留原始 body，不自动生成 PDF 文件。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 为 200 时才解析业务内容；先判断外层网关结果，不能以外层请求正常替代发货、任务或配置操作成功。
- 上游 JSON 的 `error`、`message`、`response` 依本操作实际含义解释。结果不明的写入不得盲目重试；非 JSON 下载响应保留在 developerProxy.body。
- 网关 1002–1005 的含义见 [网关业务错误](../api.md#网关业务错误)。

### curl 示例

示意请求；业务参数须按实际前置查询及上游定义补齐，不能直接用于店铺写入。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "path": "api/v2/logistics/get_mart_packaging_info",
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
  "skillName": "linkfox-shopee-store-logistics",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
