# 刷新 access token 接口说明

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

## 接口：刷新 access token（refresh_access_token）

> 官方：[refresh_access_token](https://open.shopee.com/documents/v2/v2.public.refresh_access_token?module=104&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/public/refresh_access_token`；不含主机名。脚本自动填充。 |
| method | string | 是 | 固定 `POST`；这是 Shopee 上游方法，外层始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 网关选店标识，脚本转换为字符串；runner 不将其写入业务查询串或正文，网关另以 shop_id 加入上游查询串。 |
| merchantId | string | 与 shopId 至少一个 | 网关选商户标识，脚本转换为字符串；runner 不将其写入业务查询串或正文，网关另以 merchant_id 加入上游查询串。 |
| accessToken | string | 否 | 脚本兼容传给网关，但网关忽略此值；实际 access_token 由后台按 shopId/merchantId 解析，不能用此字段替代选店。 |
| queryString | string | 否 | 本 POST 脚本不构建查询串；直接调用网关或共享转发函数时，按上游要求编码且不含 `?` 前缀。 |
| body | string | POST 必填 | 上游完整请求正文；脚本可接收对象并序列化，也接受原始字符串。GET 通常不传。 |
| contentType | string | 否 | 有 body 时默认 `application/json`；脚本仅在传 body 时发送。 |

上游 Public 操作多为 Partner 或 OAuth 级，本身通常不要求 shopId/merchantId；本技能的网关脚本仍要求两者至少一个，用于授权目标校验，不能同时省略两者。

#### 脚本业务参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| body | object / array / scalar / string / null | 与 requestBody 至少一个 | 完整上游正文；优先于 requestBody；非字符串值用 UTF-8 JSON 序列化，字符串保持原值；是否为有效业务正文由上游规则决定。 |
| requestBody | object / array / scalar / string / null | body 未传时必填 | body 的兼容别名，不直接进入网关请求。 |
| body_fields | 注册表配置（非 CLI 字段） | 否 | runner 支持从注册表指定的顶层字段构造正文，但本模块三个 POST 操作均未配置 body_fields；不能仅传顶层字段代替完整 body/requestBody。 |

授权码、refresh token、resend code 等上游正文的子字段、必填集合和默认值按所选操作官方要求提供；脚本透传完整正文，不补充上游子字段或默认值，不把示意对象当作完整业务请求。网关选店字段不会自动注入正文，若上游也需要店铺或商户标识，须在正文中单独提供。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口必填 | 通用入口选择本操作时填 `refresh_access_token`；独立脚本固定操作，不转发此字段。全部可选操作见 [模块总览](../api.md)。 |
| skipDepCheck | boolean | 否 | 默认 false；仅在外部已检查依赖时跳过本地安装检测，不绕过网关授权。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 本技能不使用响应缓存；业务封装调用 `call_api.run` 始终传此选项，不读取或保存响应缓存。 |

公共认证兼容、依赖探测、无缓存及落盘约定见 [脚本运行约定](../api.md#脚本运行约定)。

#### 脚本调用

`python scripts/refresh_access_token.py '{"shopId":"67890","body":{"<上游字段>":"<值>"}}' [--inline] [--no-cache]`

通用入口为 `python scripts/public_api.py '<同一 JSON，增加 api 字段>'`，其中 api 为 `refresh_access_token`。示意正文中的占位字段须替换为用户提供的完整业务资料。

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
| api | string | 操作名 `refresh_access_token`。 |
| developerProxy | object | 上述网关完整响应，错误响应也保留。 |
| resolvedPath | string | 固定 `api/v2/public/refresh_access_token`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | object / array / scalar / string / null | POST 时保留实际正文；可解析 JSON 时返回解析值，否则保留原字符串。 |
| refreshAccessToken | object / array / scalar / null | 网关正常且上游 httpStatus=200 时解析 Shopee body；空或无法解析时为 null。此字段为完整上游 JSON，不等同于其中 response。 |
| refreshAccessTokenResponse | 任意 JSON | 仅当上游解析对象中的 response 非 null 时提取该值。子字段和嵌套结构以实际响应和所选操作官方文档为准。 |

#### Shopee body 解析对象

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string（如返回） | Shopee 业务错误；有错误时不得将 token 或列表操作认定为成功。 |
| message | string（如返回） | 上游业务说明，按实际响应解释。 |
| response | 任意 JSON（如返回） | 可用业务结果，映射为 `refreshAccessTokenResponse`；内部结构以实际响应为准，不补造字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先检查外层响应，再检查 `developerProxy.httpStatus`；上游不为 200 时不解析为成功结果。网关错误或无效 JSON 均保留原响应供诊断。
- 上游 body 的 error/message 与 response 分开判断；token 操作不能仅凭 HTTP 200 认定业务完成。
- 客户端不自动翻页、重试或更换参数；网关检测到 token 过期或无效时，会在内部刷新并重试一次。因此一次脚本请求不代表上游只被调用一次。日常授权流程优先使用 `linkfox-shopee-store-auth`。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/public/refresh_access_token","method":"POST","shopId":"67890","body":"<按官方要求提供的完整 JSON 正文>","contentType":"application/json"}'
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
