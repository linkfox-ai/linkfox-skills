# Shopee 查询加购优惠详情接口说明

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

## 接口：查询加购优惠详情（get_add_on_deal）

> 官方：[get_add_on_deal](https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal?module=111&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| path | string | 是 | 固定为 `api/v2/add_on_deal/get_add_on_deal`，须使用 `api/v2/add_on_deal/...` 前缀。 |
| method | string | 是 | 上游方法固定为 `GET`；外层始终为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；本模块不能省略选店标识，服务端按选店标识解析授权令牌。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供时脚本保留两者并转为字符串。 |
| queryString | string | GET 时按业务需要 | 无 `?` 前缀的 Shopee 查询串；见脚本映射。 |
| body | string | 通常不传 | Shopee 业务 JSON 字符串；内部字段按本接口官方定义准备，不臆造必填项或默认值。 |
| contentType | string | 随 body | 默认 `application/json`；无 body 时不发送。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐；不会进入 Shopee query/body。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；不会进入 Shopee query/body。 |
| api | string | 仅通用入口必填 | 固定为 `get_add_on_deal`；独立入口为 `scripts/get_add_on_deal.py`。 |
| skipDepCheck | boolean | 否 | 默认 false；只跳过本地依赖检查，不进入 query/body。 |
| contentType | string | 否 | 默认 `application/json`，作为网关保留字段，不进入业务 query/body。 |
| add_on_deal_id | 按 Shopee 业务定义 | 按业务需要 | 目标活动标识，用于详情查询；放在 JSON 顶层。封装不新增本地类型或范围限制。 |
| 顶层业务字段 | string / number / boolean / null | 按业务需要 | 除保留字段外逐项拼入 queryString；布尔值写为小写 true/false，值经 URL 百分号编码；null 被忽略，dict/list 被跳过。 |
| body / requestBody | object / string | 否 | 保留字段，GET 不使用，也不进入 queryString。 |

业务字段必须放 JSON 顶层，不要传已经拼好的顶层 `queryString`；该名称会被当作普通业务字段再次编码。注册表的 `LIST_QUERY_FIELDS` 为空，不自动把任何数组转成逗号列表。分页、状态筛选等业务字段的名称、类型、默认值和枚举按本接口官方定义准备；本地封装不补充这些定义，不能推测。

CLI 选项、依赖退出码、认证兼容、落盘和无缓存约定见 [脚本运行约定](../api.md#脚本运行约定)；公共规则中的 onboarding.md 对应 [认证与算力指引](../onboarding.md)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；依公共规则判断，0 和 false 不表示成功。 |
| errmsg | string | 网关消息；用于解释具体错误。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分开判断。 |
| contentType | string | 上游返回的内容类型（若提供）。 |
| body | string | Shopee 原始 JSON 字符串；具体业务字段以本接口官方定义及实际返回为准。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定为 `get_add_on_deal`。 |
| developerProxy | object | 网关响应原文的解析结果；连接失败或 HTTP 错误正文无法解析为 JSON 时，保存本地调用器生成的诊断对象。 |
| developerProxy.error / developerProxy.details | string | 本地诊断字段；error 说明连接或 HTTP 错误，details（若有）保留无法解析的 HTTP 错误正文，不是网关保证返回的字段。 |
| resolvedPath | string | 固定为 `api/v2/add_on_deal/get_add_on_deal`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| queryString | string | 有查询串时返回实际编码后的内容，无问号。 |
| requestBody | object / array / scalar / null | POST 时回显解析后的请求 JSON，GET 不提供。 |
| getAddOnDeal | object / array / scalar / null | 网关正常且上游 httpStatus=200 时解析的完整 Shopee body；空 body 或解析失败为 null；其他错误时不生成此字段。 |
| getAddOnDealResponse | 以实际返回为准 | 仅在解析对象的 response 非 null 时提取该字段；不是完整 Shopee body 的替代。 |

Shopee 内部业务字段以实际返回为准；上述解析字段包含完整 Shopee body，不能把 `getAddOnDeal` 误认为仅含 `response`。读取其中实际返回的业务错误和结果，不补造不存在的商品或活动字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后再检查 Shopee `httpStatus`；仅上游 200 时解析业务 body。上游 HTTP 成功仍需查看 Shopee body 内的实际业务结果与错误信息。
- 本接口仅用于查询加购优惠详情；不能把活动操作与主商品、加购商品操作混用。错误或结果不确定时保留完整响应，按用户任务范围处理，避免重复写入或无目的翻页。

### curl 示例

查询字段按本接口所需补充；示例仅用于说明网关封装。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/add_on_deal/get_add_on_deal",
  "method": "GET",
  "shopId": "67890",
  "queryString": "add_on_deal_id=12345"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-add-on-deal",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
