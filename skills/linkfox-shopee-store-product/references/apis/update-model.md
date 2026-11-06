# Shopee 更新SKU 接口说明

对应脚本：`scripts/update_model.py`；通用入口为 `scripts/product_api.py`。

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

## 接口：更新SKU（update_model）

> 官方：[update_model](https://open.shopee.com/documents/v2/v2.product.update_model?module=89&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

上游方法：`POST`；转发 `path`：`api/v2/product/update_model`。用途：更新SKU。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 本接口上游相对路径，见本节说明；以 `api/v2/product/` 开头，不带主机名。 |
| method | string | 是 | 本接口上游方法，见本节说明；外层网关始终POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺ID；脚本将非空值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户ID；两者都提供时均传递。 |
| queryString | string | GET时按需 | 无 `?` 前缀，业务参数编码后组成；无参数时省略。 |
| body | string | POST时 | Shopee请求体的JSON字符串；脚本可接受对象并序列化。 |
| contentType | string | 否 | 有body时可指定，默认 `application/json`；脚本无body时省略。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺ID；Product操作不得省略选店。 |
| merchantId | string | 与 shopId 至少一个 | 商户ID。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖检测，不绕过授权。 |
| api | string | 通用入口必填 | `product_api.py` 的注册操作名，独立入口已固定操作。 |
| contentType | string | 否 | 默认 `application/json`。 |
| body | object / array / number / boolean / null / string | POST时与requestBody择一 | 优先级最高；非字符串值序列化为JSON，字符串须是有效JSON文本并原样转发。 |
| requestBody | object / array / number / boolean / null / string | POST时与body择一 | 仅未提供body时使用；编码与校验规则同body。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 兼容选项；业务封装始终关闭响应缓存。 |

`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 是保留字段，不进入Shopee query或自动组装的body。详细CLI、依赖、输出与认证兼容见 [运行约定](../api.md#脚本运行约定)。

#### Shopee业务字段

本接口须使用完整 `body` 或 `requestBody`，不从顶层自动收集业务字段；不得仅传店铺信息就执行POST。字符串请求体必须是有效JSON，格式错误或空字符串会在请求前退出。复杂body的内部字段按本接口官方定义准备，不凭空补齐类型、默认值或嵌套结构。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断。 |
| errmsg | string | 网关消息；原始错误完整保留。 |
| httpStatus | integer | Shopee上游HTTP状态，与LinkFox外层HTTP状态不同。 |
| contentType | string | 上游返回内容类型，如返回则保留。 |
| body | string | Shopee原始JSON字符串，成功时按下方字段解析。 |
| error / details | string | HTTP或连接错误时公共调用器可能返回的信息。 |

#### 脚本输出与Shopee对象

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定 `update_model`。 |
| developerProxy | object | 网关完整响应，不删除错误字段。 |
| transportHttpStatus | integer / null | LinkFox外层HTTP状态；连接失败为null。 |
| resolvedPath | string | 固定 `api/v2/product/update_model`。 |
| queryString | string | 仅非空GET查询时返回，编码后无问号。 |
| requestBody | object / array / scalar / null | 仅POST返回；由提交的JSON请求体解析得到。 |
| updateModel | object / array / scalar / null | 上游body解析结果；成功状态但空body或非JSON时为null。 |
| updateModelResponse | object / array / scalar | 仅解析对象中response存在且非null时，从response提取。 |
| updateModel.response | 未限定 | Shopee业务对象；内部字段不作固定约定，按实际响应与本接口官方定义读取。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅网关正常响应且上游 `httpStatus=200` 时解析Shopee body；非200时保留原始响应，不将其认定为商品业务成功。
- 解析后如Shopee返回业务错误，按实际错误说明处理；存在解析字段并不保证业务成功。成功body中没有response时，不生成提取字段。
- 网关错误及依赖缺失的处理见 [运行约定](../api.md#脚本运行约定)；`errcode=1005` 须结合errmsg区分白名单拒绝与授权失效。

### curl 示例

以下仅演示网关包装与字段位置；示例ID、空列表及占位body须按实际业务与官方定义补齐，写操作不可直接照发。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/product/update_model",
  "method": "POST",
  "shopId": "67890",
  "body": "{\"待补齐\":\"按本接口官方定义填写完整业务字段\"}",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
