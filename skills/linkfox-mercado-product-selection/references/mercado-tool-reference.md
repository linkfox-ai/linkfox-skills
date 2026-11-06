# 美客多选品 接口说明（趋势与辅助查询）

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

## 接口：热门品牌排行榜（trendBrandTopBrand）

美客多平台，查询指定类目下的热门品牌排行榜数据

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendBrandTopBrand`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendBrandTopBrand","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：热门商品排行榜（trendBrandTopItem）

美客多平台，查询指定类目下的热门商品排行榜数据

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendBrandTopItem`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendBrandTopItem","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：热门店铺排行榜（trendBrandTopSeller）

美客多平台，查询指定类目下的热门店铺排行榜数据

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendBrandTopSeller`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendBrandTopSeller","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：新品机会分析（trendNewItems）

美客多平台，查询指定类目的新品机会数据，包括新品销量、占比等信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendNewItems`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendNewItems","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：价格分布趋势（trendPrice）

美客多平台，查询指定类目的价格分布趋势数据

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendPrice`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendPrice","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：销量分布（trendSale）

美客多平台，查询指定类目的销量分布数据，支持按月查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendSale`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |
| arguments.month | String | 否 | 查询月份，格式：YYYYMM |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendSale","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：销售历史趋势（trendSoldHis）

美客多平台，查询指定类目的销售历史趋势数据

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendSoldHis`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendSoldHis","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：类目汇总统计（trendStatistical）

美客多平台，查询指定类目的汇总统计数据，包括总商品数、销量、销售额等

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendStatistical`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendStatistical","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：仓储类型分布（trendStoreInventoryType）

美客多平台，查询指定类目的仓储类型分布数据，包括FBM、FULL、CBT等仓储类型的销售情况

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `trendStoreInventoryType`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.categoryId | String | 是 | 类目ID |
| arguments.month | String | 否 | 查询月份，格式：YYYYMM |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"trendStoreInventoryType","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}'
```


## 接口：店铺搜索（sellerSearch）

美客多平台店铺搜索工具，支持按站点、店铺类型、店铺等级等条件筛选店铺

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `sellerSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.sellerType | String | 否 | 店铺类型，可选值：LOCAL（本土店）、CBT（跨境店）、CBT_OTHER（CBT的remote店）、CBT_FBM（CBT的full店铺） |
| arguments.levelId | String | 否 | 店铺等级，可选值：5_green（绿）、4_light_green（浅绿）、3_yellow（黄） |
| arguments.powerType | String | 否 | 优质卖家等级，可选值：platinum（铂金）、gold（黄金）、silver（白银） |
| arguments.pageNo | Integer | 否 | 页码，默认1 |
| arguments.pageSize | Integer | 否 | 每页条数，默认50 |

`pageNo` 从 1 开始；默认值及每页大小限制见上表。

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作收费，需要套餐额度；当前每次 `costToken=16000`，结果为空也不免扣。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"sellerSearch","arguments":{"siteId":"MLM"}}'
```


## 接口：查询商品评论（reviewSearch）

美客多平台，按商品ID获取评论列表详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `reviewSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.itemId | String | 是 | 商品ID，如：MLM178237632 |
| arguments.pageNo | Integer | 否 | 当前页码，默认为1 |
| arguments.pageSize | Integer | 否 | 每页条数，默认为50 |

评论查询使用 `itemId` 定位商品，不传 `siteId`；可选分页字段见上表。

`pageNo` 从 1 开始；默认值及每页大小限制见上表。

字段名和类型须与上表一致。

本操作免费 （限时），当前 `costToken=0`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"reviewSearch","arguments":{"itemId":"MLM4979447466"}}'
```


## 接口：汇率查询（rateInfo）

免费接口 （限时）：美客多平台，按站点，查询对应国家币种汇率(美元)，及折算人民币汇率信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `rateInfo`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |

字段名和类型须与上表一致。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

本操作免费 （限时），当前 `costToken=0`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"rateInfo","arguments":{"siteId":"MLM"}}'
```


## 接口：查询套餐使用量（myUsage）

免费接口 （限时）：购买的套餐及使用量

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `myUsage`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 传入空对象 `{}`，无业务参数；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |

本操作从认证信息获取用户 ID。

字段名和类型须与上表一致。

本操作免费 （限时），当前 `costToken=0`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | LinkFox 封装状态；成功示例为 `"200"`，与 `errcode` 并存；错误时可能省略。 |
| msg | string | 封装消息，成功示例为 `ok`。 |
| errcode | integer / string / null | 网关状态码，成功示例为 `200`；正常响应判断遵循下方基础规则。 |
| errmsg | string | 网关消息，成功示例为 `ok`；业务错误时为原因说明。 |
| type | string | 当前通常为 `rawMcpToolResult`。 |
| toolName | string | 实际调用的工具名。 |
| charged | boolean | 该工具是否收费。 |
| data | string / object / array | MCP `content.text` 解包后的业务数据，多数工具返回格式化文本。仅上游返回 JSON 对象或数组时才解析为相应结构，不假定统一业务字段。 |
| rawResponse | object | MCP `tools/call` 原始 result；当前网关返回 `{}`，不透出原始 result；原文读取 `contentText` 或 `data`。 |
| contentText | string | MCP text content 拼接后的原文。 |
| textParsedAsJson | boolean | 原文是否成功解析为 JSON；JSON 字符串也为 true，此时 `data` 仍是字符串。 |
| total | integer | 可推断时才返回的记录数；文本业务结果省略此字段，而非返回 null。 |
| costToken | integer | 本次 token 成本，当前收费工具为 16000，免费工具为 0 （限时），以实际响应为准。 |
| costTime | integer | 后端耗时，单位毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数校验失败时外层 HTTP 可能仍为 200，响应仅有 `errcode` / `errmsg`，不含 `code` / `data` 等字段。
- `errcode=1002`：必填字段缺失、`arguments` 非对象或不支持的 `toolName`；按本接口字段表补齐，保留名称大小写。未知工具消息形如「参数校验失败，请检查输入。不支持的 toolName: <name>」，脚本仍落盘该业务错误。
- `errcode=500`：上游 MCP 调用异常，例如 `LingdongMcpClient$TransientMcpException` 或 MCP 握手偶发 404。遵守成本约束，说明额外消耗后可重试 1–2 次；仍失败保存脱敏请求和响应交后端核查，脚本不会自动重试。
- HTTP 403 时检查是否使用 LinkFox 网关 Key，不能换成上游 Key；此情况不进入认证或充值引导。
- `data` 为文本不代表失败；「查询不到商品信息」「未查询到评论数据」等是上游业务空结果，结合封装状态解释，不直接判定系统故障。核对真实 ID 或关键词后，继续调用仍遵守成本约束。
- 上游 `-32000` 系列协议错误由网关转为 `1002` / `500`，不会直接透出；对照说明见 [上游诊断](api.md#上游诊断)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mercado/productSelection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"myUsage","arguments":{}}'
```


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mercado-product-selection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
