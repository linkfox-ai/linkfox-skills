# Shopee 删除套装优惠 接口说明

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

## 接口：删除套装优惠（delete_bundle_deal）

> 官方：[delete_bundle_deal](https://open.shopee.com/documents/v2/v2.bundle_deal.delete_bundle_deal?module=110&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/bundle_deal/delete_bundle_deal`；必须以 api/v2 开头，本技能业务操作均使用 api/v2/bundle_deal/ 前缀。 |
| method | string | 是 | 固定 `POST`，这是上游方法；网关自身仍使用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐使用；脚本转换为字符串。本模块不适用 Public 无店铺接口的省略惯例。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供两者时均保留。 |
| queryString | string | 不使用 | 本 POST 操作的业务参数通过 body 提交；专用脚本不会从顶层字段构建查询串。 |
| body | string | POST 必填 | 上游完整 JSON 请求体的字符串，脚本支持对象自动序列化。 |
| contentType | string | 发送 body 时 | 默认 application/json；GET 无 body 时不发送。 |

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过已确认依赖的本地安装检测，不绕过授权。 |
| contentType | string | 否 | 默认 application/json；只在发送 body 时使用。 |
| api | string | 通用入口必填 | `delete_bundle_deal`；专用脚本 `scripts/delete_bundle_deal.py` 自动指定。 |
| body | JSON value / JSON 字符串 | 与 requestBody 二选一 | 优先采用此键；对象序列化为紧凑 JSON 字符串，字符串原样透传。须提供完整 Shopee 请求体。 |
| requestBody | JSON value / JSON 字符串 | body 不存在时使用 | body 的兼容别名；处理方式相同。 |

POST 优先采用 `body`，仅当该键不存在时才采用 `requestBody`。runner 支持从注册表 `body_fields` 提取顶层字段，但本模块各操作均未配置 `body_fields`，因此仅在顶层填写业务字段不能替代完整请求体。店铺选择等保留字段不会自动并入请求体；完整 body 不删改其内部字段。字符串须为有效 JSON，供脚本校验并解析 `requestBody`；非字符串值按 JSON 序列化。该透传兼容性不代表 Shopee 接受任意 JSON 类型，上游业务仍须提交完整请求对象。上游字段及其类型、必填和枚举按本接口官方文档准备；脚本不额外推断上游约定。

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
| api | string | `delete_bundle_deal`。 |
| developerProxy | object | 网关完整响应，保留错误及原始 body。 |
| resolvedPath | string | `api/v2/bundle_deal/delete_bundle_deal`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| developerProxy.error | string（本地异常时） | 公共调用器在连接失败、空正文 HTTP 错误或非 JSON HTTP 错误时生成的诊断摘要，不是网关保证字段。 |
| developerProxy.details | string（本地异常时） | 非 JSON HTTP 错误时由公共调用器保留的原始响应文本（若有），不是网关保证字段。 |
| requestBody | JSON value | 解析后的实际提交体，与发给 Shopee 的 JSON 内容一致。 |
| deleteBundleDeal | JSON value / null | 网关正常且上游 httpStatus 为 200 时解析完整 Shopee body；空或无效 JSON 为 null；其他失败时不生成。 |
| deleteBundleDealResponse | JSON value（若有） | 上述解析对象的 response 非 null 时提取；不替代完整解析对象。 |

Shopee body 的 `response` 是业务数据。嵌套结构以实际返回及对应官方文档为准，不补造活动、商品或错误字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，还需判断上游 `httpStatus`；本封装仅在上游为 200 时解析业务 body，其他状态保留原始响应并解释原因。
- 解析 body 或提取 response 不等于 Shopee 业务成功；依据上游实际错误和消息判断。写入结果不确定时，不自动重试。

### curl 示例

将本节网关 POST Body 字段保存为 UTF-8 文件 `delete-bundle-deal-request.json`，其中 path 为 `api/v2/bundle_deal/delete_bundle_deal`、method 为 `POST`，并填入已授权店铺和完整业务参数。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data-binary @delete-bundle-deal-request.json
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
