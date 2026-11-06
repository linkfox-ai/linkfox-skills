# Shopee 直播：更新直播商品列表接口说明

[返回模块索引](../api.md) · [对应脚本](../../scripts/update_item_list.py)

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

## 接口：更新直播商品列表（update_item_list）

> 官方参考：[v2.livestream.update_item_list](https://open.shopee.com/documents/v2/v2.livestream.update_item_list?module=125&type=1)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| path | string | 是 | `api/v2/livestream/update_item_list`；本接口仅使用该 Livestream 相对路径。 |
| method | string | 是 | `POST`；为 Shopee 上游方法，LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐；脚本转为字符串。所有直播操作都需要店铺或商户标识，不能按 Public 接口免选店。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，脚本转为字符串；同时提供时两个标识均保留。 |
| queryString | string | 否 | GET 的业务查询串，无 `?` 前缀；是否需要业务查询参数按上游定义，脚本从顶层业务字段构建。 |
| body | string | 否 | 网关接收正文字符串；本技能的 POST CLI 必须显式提供 body 或 requestBody，按上游定义准备完整业务正文，非字符串 JSON 入参由脚本序列化。 |
| contentType | string | 否 | 有正文时可指定，默认 JSON；脚本默认 `application/json`，仅有正文时发送。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 同网关字段；所有直播操作都检查选店标识。 |
| merchantId | string | 与 shopId 至少一个 | 同网关字段。 |
| api | string | 通用入口必填 | 本接口为 `update_item_list`；专用入口按自身名称分派。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖检测。 |
| body | object / string / JSON 值 | POST 时与 requestBody 择一 | 优先于 requestBody；字符串原样转发，其他 JSON 值序列化。应提供上游要求的完整业务正文。 |
| requestBody | object / string / JSON 值 | POST 时与 body 择一 | body 未提供时使用的兼容别名。 |
| contentType | string | 否 | 默认 `application/json`。 |
| 顶层业务字段 | string / number / boolean | 依上游操作 | GET 时逐项写入 queryString；POST 时只读取注册表明确列出的 body_fields。 |
| --inline | CLI flag | 否 | 默认按 8 KB 阈值输出；指定后完整输出并落盘。 |
| --no-cache | CLI flag | 否 | 封装始终强制启用，不读取或保存响应缓存。 |

#### 参数映射与限制

- POST 优先读取 body，其次 requestBody；字符串正文原样转发，其他 JSON 值使用紧凑 JSON 序列化。两者均未提供时，只收集注册表 body_fields 中的非 null 字段。
- 本接口注册表没有声明 body_fields，必须显式提供 body 或 requestBody，不能只提供 shopId，也不能依靠任意顶层业务字段构建正文。
- `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为封装保留字段，不会自动进入业务正文；显式 body 内的内容由调用者负责。
- 业务正文及其嵌套字段、必填性、默认值和限制以本接口官方定义为准，需结合已有请求资料准备；封装不补齐未知字段。`contentType` 按上游要求指定。

依赖检查、环境变量兼容、无缓存和落盘约定见[脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，按基础规则判断；不得只看上游 httpStatus。 |
| errmsg | string | 网关消息或错误原因，原样保留。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态区分。 |
| contentType | string | 上游响应内容类型，按实际响应保留。 |
| body | string | Shopee 原始响应正文；仅通过下方规则后解析 JSON。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次操作 `update_item_list`。 |
| developerProxy | object / JSON 值 | 完整网关响应。 |
| developerProxy.error | string | 本地调用器在连接失败或 HTTP 错误时生成的消息（存在时）；不属于网关业务字段。 |
| developerProxy.details | string | 本地调用器保留的非 JSON HTTP 错误正文（存在时）；不属于网关业务字段。 |
| resolvedPath | string | 实际转发的 `api/v2/livestream/update_item_list`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | GET 时实际发送的非空查询串，未发送时不出现。 |
| requestBody | object / array / scalar / string / null | POST 正文；合法 JSON 解析后回显，非 JSON 字符串原样保留。 |
| updateItemList | object / array / scalar / null | 通过网关和上游状态检查后解析的完整 Shopee body；空白或无效 JSON 为 null，非成功时不生成。 |
| updateItemListResponse | JSON 值 | 仅当上述解析对象含非 null 的 response 时复制该值，原始对象仍保留。 |
| updateItemListRaw | string | 仅 JSON 解析失败时保留原始 body，便于解释错误。 |

`updateItemList` 是完整 Shopee body 的 JSON 解析结果；`updateItemListResponse` 是其中非 null 的 response 值。业务嵌套字段按真实响应展示，不补造缺失数据。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅当 LinkFox 网关正常响应且 Shopee `httpStatus=200` 时生成解析结果；否则保留网关响应解释原因。空白或无效 JSON 正文不视为已取得业务数据。
- Shopee JSON 内的业务错误需要结合实际错误消息处理，不能把网关成功、上游 HTTP 成功或存在解析字段直接等同于直播操作成功。
- 创建、开播、结束、商品维护和互动等写入结果不确定时，不自动重复提交；后续调用遵循调用约束。

### curl 示例

以下仅展示网关封装；替换店铺与业务参数后使用，不可原样提交占位值。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/livestream/update_item_list",
  "method": "POST",
  "shopId": "<已授权店铺 ID>",
  "body": "<按官方定义准备的完整业务正文字符串>",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-livestream",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
