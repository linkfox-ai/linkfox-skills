# 查询 Partner 下已授权店铺 接口说明

本文 scripts/ 路径以技能目录为基准；公共规则中的 onboarding.md 指 [认证与算力引导](../onboarding.md)。

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

## 接口：查询 Partner 下已授权店铺（get_shops_by_partner）

> 官方：[get_shops_by_partner](https://open.shopee.com/documents/v2/v2.public.get_shops_by_partner?module=104&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/public/get_shops_by_partner`；不含主机名。脚本自动填充。 |
| method | string | 是 | 固定 `GET`；这是 Shopee 上游方法，外层始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 网关选店标识，脚本转换为字符串；runner 不将其写入业务查询串或正文，网关另以 shop_id 加入上游查询串。 |
| merchantId | string | 与 shopId 至少一个 | 网关选商户标识，脚本转换为字符串；runner 不将其写入业务查询串或正文，网关另以 merchant_id 加入上游查询串。 |
| accessToken | string | 否 | 脚本兼容传给网关，但网关忽略此值；实际 access_token 由后台按 shopId/merchantId 解析，不能用此字段替代选店。 |
| queryString | string | GET 按需 | 无 `?` 前缀；GET 脚本从顶层业务字段构建，直接调用网关时自行编码。 |
| body | string | 否 | 本 GET 脚本不发送；共享转发函数兼容原始正文字符串。 |
| contentType | string | 否 | 有 body 时共享转发函数默认 `application/json`；本 GET 脚本不发送。 |

上游 Public 操作多为 Partner 或 OAuth 级，本身通常不要求 shopId/merchantId；本技能的网关脚本仍要求两者至少一个，用于授权目标校验，不能同时省略两者。

#### 脚本业务参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 顶层业务字段 | string / number / boolean | 按上游要求 | 除保留字段外的非 null 标量转为查询参数；布尔值为小写 true/false，值使用百分号编码。对象、数组被跳过。具体查询字段、分页默认值和枚举按所选上游操作要求提供，脚本不为这些字段补充默认值或校验枚举。 |

保留字段为 `shopId`、`merchantId`、`accessToken`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType`，不会由 runner 拼入业务 query/body；网关仍将选店标识加入上游查询串，并注入后台 access_token。当前 `LIST_QUERY_FIELDS` 为空，没有额外列表字段转换。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口必填 | 通用入口选择本操作时填 `get_shops_by_partner`；独立脚本固定操作，不转发此字段。全部可选操作见 [模块总览](../api.md)。 |
| skipDepCheck | boolean | 否 | 默认 false；仅在外部已检查依赖时跳过本地安装检测，不绕过网关授权。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 本技能不使用响应缓存；业务封装调用 `call_api.run` 始终传此选项，不读取或保存响应缓存。 |

公共认证兼容、依赖探测、无缓存及落盘约定见 [脚本运行约定](../api.md#脚本运行约定)。

#### 脚本调用

`python scripts/get_shops_by_partner.py '{"shopId":"67890"}' [--inline] [--no-cache]`

通用入口为 `python scripts/public_api.py '<同一 JSON，增加 api 字段>'`，其中 api 为 `get_shops_by_partner`。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态；按公共响应码规则判断，不能把 0 或 false 当作成功。 |
| errmsg | string | 网关说明；失败时按实际返回解释。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与外层 LinkFox HTTP 状态区分。 |
| contentType | string | 上游响应内容类型。 |
| body | string | Shopee 原始响应，通常为 JSON 字符串，始终保留在 developerProxy。 |
| error | string | 连接失败或非 JSON HTTP 错误时公共调用器保留的错误说明。 |
| details | string | 非 JSON HTTP 错误时保留原始文本。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 操作名 `get_shops_by_partner`。 |
| developerProxy | object | 上述网关完整响应，错误响应也保留。 |
| resolvedPath | string | 固定 `api/v2/public/get_shops_by_partner`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| queryString | string | 仅有查询串时返回，值为实际编码后的查询串。 |
| getShopsByPartner | object / array / scalar / null | 网关正常且上游 httpStatus=200 时解析 Shopee body；空或无法解析时为 null。此字段为完整上游 JSON，不等同于其中 response。 |
| getShopsByPartnerResponse | 任意 JSON | 仅当上游解析对象中的 response 非 null 时提取该值。子字段和嵌套结构以实际响应和所选操作官方文档为准。 |

#### Shopee body 解析对象

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string（如返回） | Shopee 业务错误；有错误时不得将 token 或列表操作认定为成功。 |
| message | string（如返回） | 上游业务说明，按实际响应解释。 |
| response | 任意 JSON（如返回） | 可用业务结果，映射为 `getShopsByPartnerResponse`；内部结构以实际响应为准，不补造字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先检查外层响应，再检查 `developerProxy.httpStatus`；上游不为 200 时不解析为成功结果。网关错误或无效 JSON 均保留原响应供诊断。
- 上游 body 的 error/message 与 response 分开判断；不能仅凭 HTTP 200 认定店铺、商户或 IP 段查询成功。
- 客户端不自动翻页、重试或更换参数；网关检测到 token 过期或无效时，会在内部刷新并重试一次。因此一次脚本请求不代表上游只被调用一次。日常授权流程优先使用 `linkfox-shopee-store-auth`。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/public/get_shops_by_partner","method":"GET","shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-public",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
