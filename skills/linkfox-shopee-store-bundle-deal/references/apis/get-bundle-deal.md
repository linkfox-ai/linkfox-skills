# Shopee 查询套装优惠详情 接口说明

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

## 接口：查询套装优惠详情（get_bundle_deal）

> 官方：[get_bundle_deal](https://open.shopee.com/documents/v2/v2.bundle_deal.get_bundle_deal?module=110&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/bundle_deal/get_bundle_deal`；必须以 api/v2 开头，本技能业务操作均使用 api/v2/bundle_deal/ 前缀。 |
| method | string | 是 | 固定 `GET`，这是上游方法；网关自身仍使用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐使用；脚本转换为字符串。本模块不适用 Public 无店铺接口的省略惯例。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供两者时均保留。 |
| queryString | string | GET 按操作 | 不带 ? 的查询串；专用脚本从顶层业务字段构建。 |
| body | string | 不使用 | 本 GET 操作不发送上游请求体；脚本中的 body / requestBody 为保留键，会被忽略。 |
| contentType | string | 不使用 | 本 GET 操作不发送此字段；网关请求自身的 Content-Type 仍按公共规则设置。 |

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过已确认依赖的本地安装检测，不绕过授权。 |
| contentType | string | 否 | 兼容保留键，本 GET 操作忽略。 |
| api | string | 通用入口必填 | `get_bundle_deal`；专用脚本 `scripts/get_bundle_deal.py` 自动指定。 |
| bundle_deal_id | 脚本接受标量；上游类型见官方文档 | 详情定位 | 通过此字段查询活动详情；放 JSON 顶层并编码进 queryString。脚本不额外校验其上游类型和必填性。 |
| 顶层业务字段 | string / number / boolean | 按上游操作 | 除保留键外且不为 null 的标量进入 queryString；空字符串、0、false 仍保留；布尔值转为小写 true/false。对象和数组跳过；本模块 LIST_QUERY_FIELDS 为空，不启用列表拼接。 |

GET 业务字段放 JSON 顶层。键和值分别做百分号编码，queryString 不带 `?`。保留键为 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType`，不会自动进入上游查询。详情通过 `bundle_deal_id` 定位，列表的分页和状态筛选按对应官方文档准备；完整上游字段及其类型、必填和枚举以对应官方文档为准；脚本不额外推断上游约定。

脚本的 CLI、认证兼容、依赖退出码、缓存与落盘限制见 [脚本运行约定](../api.md#脚本运行约定)；认证与算力引导见 [onboarding.md](../onboarding.md)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，不等同于 LinkFox 外层 HTTP 状态。 |
| contentType | string（若返回） | 上游响应内容类型。 |
| body | string | 上游原始 JSON 字符串；完整保留在 developerProxy 中。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | `get_bundle_deal`。 |
| developerProxy | object | 网关完整响应，保留错误及原始 body。 |
| resolvedPath | string | `api/v2/bundle_deal/get_bundle_deal`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| developerProxy.error | string（本地异常时） | 公共调用器在连接失败、空正文 HTTP 错误或非 JSON HTTP 错误时生成的诊断摘要，不是网关保证字段。 |
| developerProxy.details | string（本地异常时） | 非 JSON HTTP 错误时由公共调用器保留的原始响应文本（若有），不是网关保证字段。 |
| queryString | string（若有） | 实际使用的已编码查询串。 |
| getBundleDeal | JSON value / null | 网关正常且上游 httpStatus 为 200 时解析完整 Shopee body；空或无效 JSON 为 null；其他失败时不生成。 |
| getBundleDealResponse | JSON value（若有） | 上述解析对象的 response 非 null 时提取；不替代完整解析对象。 |

Shopee body 的 `response` 是业务数据。嵌套结构以实际返回及对应官方文档为准，不补造活动、商品或错误字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，还需判断上游 `httpStatus`；本封装仅在上游为 200 时解析业务 body，其他状态保留原始响应并解释原因。
- 解析 body 或提取 response 不等于 Shopee 业务成功；依据上游实际错误和消息判断。写入结果不确定时，不自动重试。

### curl 示例

将本节网关 POST Body 字段保存为 UTF-8 文件 `get-bundle-deal-request.json`，其中 path 为 `api/v2/bundle_deal/get_bundle_deal`、method 为 `GET`，并填入已授权店铺和完整业务参数。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data-binary @get-bundle-deal-request.json
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-bundle-deal",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
