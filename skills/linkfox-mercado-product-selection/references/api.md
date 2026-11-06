# 美客多选品 接口说明

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

## 接口：查询商品基本信息（itemInfo）

美客多平台，根据站点和商品ID查询基本信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `itemInfo`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.itemId | String | 是 | 商品ID，如：MLM178237632 |

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
  -d '{"toolName":"itemInfo","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}'
```


## 接口：查询商品销量历史（itemHistory）

美客多平台，根据商品ID查询商品销量历史信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `itemHistory`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.itemId | String | 是 | 商品ID，如：MLM178237632 |
| arguments.productId | String | 否 | 官链ID，如：MLM21333 |

字段名和类型须与上表一致。

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
  -d '{"toolName":"itemHistory","arguments":{"itemId":"MLM4979447466"}}'
```


## 接口：商品搜索（itemSearch）

美客多平台商品搜索工具。支持按站点、关键词、类目、价格、销量（总销量/30天销量）、评分、评论数、重量及上架时间等多维度筛选商品，并支持排序。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `itemSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 【必填】站点ID。可选值：MLM（墨西哥）、MLB（巴西）、MLC（智利）、MLA（阿根廷）、MCO（哥伦比亚） |
| arguments.title | String | 否 | 【选填】搜索关键词，匹配商品标题。例如：蓝牙耳机 |
| arguments.categoryId | String | 否 | 【选填】类目ID，用于限定搜索范围。例如：MLM458037 |
| arguments.sellerId | String | 否 | 【选填】店铺ID或店铺名称，指定查询特定店铺的商品 |
| arguments.itemUrl | String | 否 | 【选填】商品链接 |
| arguments.priceBegin | Integer | 否 | 【选填】最低价格（整数） |
| arguments.priceEnd | Integer | 否 | 【选填】最高价格（整数） |
| arguments.soldTotalBegin | Integer | 否 | 【选填】最低总销量（整数） |
| arguments.soldTotalEnd | Integer | 否 | 【选填】最高总销量（整数） |
| arguments.sale30Start | Integer | 否 | 【选填】最低30天销量（整数） |
| arguments.sale30End | Integer | 否 | 【选填】最高30天销量（整数） |
| arguments.scoreStart | BigDecimal | 否 | 【选填】最低商品评分（支持小数，如4.5） |
| arguments.scoreEnd | BigDecimal | 否 | 【选填】最高商品评分（支持小数，如5.0） |
| arguments.commentBegin | Integer | 否 | 【选填】最低评论数（整数） |
| arguments.commentEnd | Integer | 否 | 【选填】最高评论数（整数） |
| arguments.weightStart | Integer | 否 | 【选填】最低商品重量，单位：克(G) |
| arguments.weightEnd | Integer | 否 | 【选填】最高商品重量，单位：克(G) |
| arguments.startTimeAdded | Integer | 否 | 【选填】上架时间范围。可选值：15（最近15天）、30、60、90、180、365 |
| arguments.startTimeBegin | String | 否 | 【选填】自定义上架时间开始日期，格式：yyyy-MM-dd。例如：2026-03-01 |
| arguments.startTimeEnd | String | 否 | 【选填】自定义上架时间结束日期，格式：yyyy-MM-dd。例如：2026-03-24 |
| arguments.storageType | String | 否 | 【选填】仓储类型。可选值：None（全部）、FULL（官方仓）、CBT,LOCAL（自发货） |
| arguments.sellerType | String | 否 | 【选填】店铺类型。可选值：None（全部）、LOCAL（本土店）、CBT（跨境店） |
| arguments.follow | Integer | 否 | 【选填】是否跟卖。0：否，1：是 |
| arguments.isUsaFull | Boolean | 否 | 【选填】是否美国转运仓。true：是，false：否 |
| arguments.itemStatus | String | 否 | 【选填】商品状态。active：活跃，paused：暂停 |
| arguments.sortKey | String | 否 | 【选填】排序字段。可选值：title（商品名称）、price（价格）、sale7（7天销量）、sale30d（30天销量）、sold_quantity（总销量）、sales_amount30（30天销售额）、available_quantity（库存数）、start_time（上架时间）、brand_id（品牌）、bsr（最佳销售）。默认为综合排序 |
| arguments.sortOrder | String | 否 | 【选填】排序方式。asc：升序，desc：降序。默认为降序 |
| arguments.pageNo | Integer | 否 | 【选填】当前页码，默认为1 |
| arguments.pageSize | Integer | 否 | 【选填】每页条数，默认为50 |

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
  -d '{"toolName":"itemSearch","arguments":{"siteId":"MLM"}}'
```


## 接口：查询官链基本信息（catalogInfo）

美客多平台，根据站点和官链（或目录链接）ID查询基本信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `catalogInfo`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.productId | String | 是 | 官链（或目录链接）ID，如：MLM178237632 |

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
  -d '{"toolName":"catalogInfo","arguments":{"siteId":"MLM","productId":"MLM178237632"}}'
```


## 接口：查询官链销量历史（catalogHistory）

美客多平台，根据站点和官链（或目录链接）ID查询销量历史信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `catalogHistory`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.productId | String | 是 | 官链（或目录链接）ID，如：MLM178237632 |

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
  -d '{"toolName":"catalogHistory","arguments":{"siteId":"MLM","productId":"MLM178237632"}}'
```


## 接口：官链搜索（catalogSearch）

美客多平台官链（或目录链接）搜索工具，支持按站点、关键词、类目、价格、销量、评分、BSR排名等多维度筛选官链

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `catalogSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| arguments.searchText | String | 否 | 搜索关键词 |
| arguments.catalogId | String | 否 | 官链（或目录链接）ID |
| arguments.categoryId | String | 否 | 类目ID |
| arguments.bland | String | 否 | 品牌名称 |
| arguments.sellerId | String | 否 | 店铺ID |
| arguments.priceVolStart | Integer | 否 | 最低价格 |
| arguments.priceVolEnd | Integer | 否 | 最高价格 |
| arguments.sales30VolStart | Integer | 否 | 30天销量最小值 |
| arguments.sales30VolEnd | Integer | 否 | 30天销量最大值 |
| arguments.hisVolStart | Integer | 否 | 历史销量最小值 |
| arguments.hisVolEnd | Integer | 否 | 历史销量最大值 |
| arguments.scoreVolStart | String | 否 | 最低评分 |
| arguments.scoreVolEnd | String | 否 | 最高评分 |
| arguments.commentVolStart | Integer | 否 | 评论数最小值 |
| arguments.commentVolEnd | Integer | 否 | 评论数最大值 |
| arguments.stockVolStart | Integer | 否 | 库存最小值 |
| arguments.stockVolEnd | Integer | 否 | 库存最大值 |
| arguments.weightStart | Integer | 否 | 重量最小值（单位：克） |
| arguments.weightEnd | Integer | 否 | 重量最大值（单位：克） |
| arguments.bsrVolStart | Integer | 否 | BSR排名最小值 |
| arguments.bsrVolEnd | Integer | 否 | BSR排名最大值 |
| arguments.followVol | Integer | 否 | 是否跟卖，0：否，1：是 |
| arguments.isUsaFull | Boolean | 否 | 是否美国转运仓，true：是，false：否 |
| arguments.storageTypeVol | String | 否 | 仓储类型，FULL：官方仓，CBT：跨境店，LOCAL：本土店 |
| arguments.sellerTypeVol | String | 否 | 店铺类型，LOCAL：本土店，CBT：跨境店 |
| arguments.storeStatusVol | String | 否 | 商品状态，active：活跃，paused：暂停 |
| arguments.sortKey | String | 否 | 排序字段，sold_his：历史销量，price：价格，sale30d：30天销量，sale7：7天销量，bsr：BSR排名 |
| arguments.sortOrder | String | 否 | 排序方式，asc：升序，desc：降序，默认desc |
| arguments.pageNo | Integer | 否 | 页码，默认1 |
| arguments.pageSize | Integer | 否 | 每页条数，默认50，最大200 |
| arguments.month | String | 否 | 查询月份，格式：YYYYMM |
| arguments.addedVol | Integer | 否 | 上架时间天数，如：15、30、60、90、180、365 |

`pageNo` 从 1 开始；默认值及每页大小限制见上表。

字段名和类型须与上表一致。品牌字段为 `bland`，不得改为其他拼写。站点编号含义见 [站点对照](api.md#站点对照)，支持范围以本接口字段表为准。

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
  -d '{"toolName":"catalogSearch","arguments":{"siteId":"MLM"}}'
```


## 接口：按天搜索热搜词（keywordDateSearch）

美客多平台，根据站点和日期查询按天热搜词信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `keywordDateSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.runDate | String | 是 | 搜索日期，格式：YYYYMMDD |
| arguments.categoryId | String | 否 | 类目ID |
| arguments.searchText | String | 否 | 搜索词 |
| arguments.sort | Object | 否 | 排序规则对象，子字段见下表。 |
| arguments.sale30 | Object | 否 | 30天销量过滤范围对象，子字段见下表。 |
| arguments.visit30 | Object | 否 | 访问量过滤范围对象，子字段见下表。 |
| arguments.totalItem | Object | 否 | 商品数量过滤范围对象，子字段见下表。 |
| arguments.adCount | Object | 否 | 广告数量过滤范围对象，子字段见下表。 |
| arguments.pageNo | Integer | 否 | 页码，默认1 |
| arguments.pageSize | Integer | 否 | 每页条数，默认50 |

#### arguments 中的嵌套字段

以下列出对象内字段的含义和取值；子字段的具体类型与必填性未单独约定，不据此推定。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort.key | 未单独约定 | 未单独约定 | `sale30`（30天销量）、`item_total_count`（商品数量）、`visit30`（30天搜索量）、`view_count`（30天访问量）。 |
| sort.order | 未单独约定 | 未单独约定 | `ascending` / `descending`。 |
| sale30.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| sale30.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |
| visit30.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| visit30.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |
| totalItem.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| totalItem.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |
| adCount.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| adCount.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |

最大分页深度上限为 10000；不将此值误作每页大小。

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
  -d '{"toolName":"keywordDateSearch","arguments":{"siteId":"MLM","runDate":"20260601"}}'
```


## 接口：月度热搜词（keywordMonthSearch）

美客多平台，根据站点和月份查询月度热搜词信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `keywordMonthSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.runMonth | String | 是 | 搜索月份，格式：YYYYMM |
| arguments.categoryId | String | 否 | 类目ID |
| arguments.searchText | String | 否 | 搜索词 |
| arguments.sort | Object | 否 | 排序规则对象，子字段见下表。 |
| arguments.sale30 | Object | 否 | 30天销量过滤范围对象，子字段见下表。 |
| arguments.visit30 | Object | 否 | 访问量过滤范围对象，子字段见下表。 |
| arguments.totalItem | Object | 否 | 商品数量过滤范围对象，子字段见下表。 |
| arguments.pageNo | Integer | 否 | 页码，默认1 |
| arguments.pageSize | Integer | 否 | 每页条数，默认50 |

#### arguments 中的嵌套字段

以下列出对象内字段的含义和取值；子字段的具体类型与必填性未单独约定，不据此推定。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort.key | 未单独约定 | 未单独约定 | `sale30`（30天销量）、`item_total_count`（商品数量）、`visit30`（30天搜索量）、`view_count`（30天访问量）。 |
| sort.order | 未单独约定 | 未单独约定 | `ascending` / `descending`。 |
| sale30.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| sale30.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |
| visit30.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| visit30.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |
| totalItem.start | 未单独约定 | 未单独约定 | 过滤范围最小值。 |
| totalItem.end | 未单独约定 | 未单独约定 | 过滤范围最大值。 |

最大分页深度上限为 10000；不将此值误作每页大小。

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
  -d '{"toolName":"keywordMonthSearch","arguments":{"siteId":"MLB","runMonth":"202606"}}'
```


## 接口：流量词反查（keywordReverse）

美客多平台，流量词反查

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `keywordReverse`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.itemId | String | 是 | 商品ID，如：MLM178237632 |

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
  -d '{"toolName":"keywordReverse","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}'
```


## 接口：搜索类目（categorySearch）

免费 （限时）：搜索类目信息，根据站点和类目名称(西文或葡文)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `categorySearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.searchText | String | 是 | 类目名称，支持西文、中文 |

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
  -d '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'
```


## 接口：搜索最小子类目（categorySmallSearch）

免费 （限时）：搜索最小类目信息，根据站点和类目名称(西文或葡文)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mercado/productSelection`


### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| toolName | string | 是 | 固定为 `categorySmallSearch`，通过统一网关选择本操作；不额外构造 path 字段或上游端点。 |
| arguments | object | 是 | 下列字段均放入此对象；不能为数组、字符串或数字。后端移除 `uId`、`uid`、`memberId` 并裁剪空值。 |
| arguments.siteId | String | 是 | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| arguments.searchText | String | 是 | 类目名称，支持西文、中文 |

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
  -d '{"toolName":"categorySmallSearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'
```


## 脚本调用与兼容约定

业务入口：`python scripts/linkfox_mercado_product_selection.py '<JSON 参数>' [--inline] [--no-cache]`。JSON 参数是完整的 `{"toolName":"...","arguments":{...}}`，必须作为一个命令行参数传入，不能只传 arguments。

| 选项 / 约定 | 类型 | 说明 |
|------|------|------|
| --inline | CLI flag | 全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 跳过本地缓存的读取和写入，强制一次新调用；仍会保存完整响应。 |
| --help | CLI flag | 仅显示帮助，不发网络请求。 |
| 缓存 | 本地文件 | 缓存有效期为 24 小时，以完整请求 JSON 排序后的 SHA-256 前 16 位作为键，路径为 `linkfox/.cache/linkfox-mercado-product-selection/`。缓存文件直接保存响应对象，命中时标记 `_cache.hit=true` 并显示 `Cache hit`。响应对象含业务错误或空结果也可被保存；需刷新时显式指定 --no-cache，不自动重试。 |
| 公共调用器 | Python run | 业务包装调用 `call_api.run` 时始终添加 --no-cache，本地缓存统一由业务包装维护，公共调用器负责 HTTP 请求、响应输出与会话归档。 |
| 密钥优先级 | 环境变量 | 优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；未配置走 [认证引导](onboarding.md)。 |
| 网关地址 | 环境变量 | 优先 `LINKFOX_TOOL_GATEWAY`，缺省正式网关，移除末尾 `/`。不直连 XP-MCP，不索取上游 `secret-key` / `X-API-Key`，上游凭证由后端托管。 |
| 追踪信息 | 请求头 | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，缺省为空字符串。 |
| 输出目录 | 本地文件 | 业务包装在请求前检查当前目录可写，完整数据固定落到当前目录的 linkfox 会话目录；禁止回退到 /tmp、家目录或 ACPX_WORKSPACES。 |
| 会话归档 | 本地文件 | SESSION_ID 优先；缺省生成 HHMMSS-六位随机十六进制串，同一进程稳定。保留 `_meta.json` 和 `index.jsonl` 注册。归档文件采用微秒时间戳，已有同名文件时递增避让，连续调用各保存一份响应。 |

脚本在响应对象中添加本地元数据 `_http_status`，保存真实 HTTP 状态，缓存命中时保留该次请求的状态；此字段不是网关响应契约。连接失败未取得 HTTP 响应，或旧缓存未记录状态时，该值为 `null`，不能据此认定 HTTP 成功。旧缓存仍可复用，不会为补全状态自动发起新调用；需要重新查询时使用 `--no-cache`，并遵守成本约束。判断结果时结合该状态、`errcode` 和原始错误消息，不能将只有 `message` 等字段的 HTTP 错误视为成功。

小于等于 8000 UTF-8 字节时保存后全量打印，超出时仅打印摘要，含顶层字段、常见计数、最大列表长度及前三条样本。按需从保存文件提取字段。

PowerShell 可用单引号包裹 JSON；遇到引号问题时，先把 JSON 写入文件，再用 `Get-Content -Raw -Encoding UTF8` 读取成一个字符串参数。`--inline` 只控制输出，不读取输入文件。

## 站点对照

| 站点ID | 国家/地区 |
|------|------|
| MLM | 墨西哥 |
| MLB | 巴西 |
| MLA | 阿根廷 |
| MLC | 智利 |
| MCO | 哥伦比亚，仅显式列出该站点的操作支持。 |

## 上游诊断

上游 XP-MCP 文档版本为 1.0.0，协议为 STREAMABLE（SSE）。这些信息用于诊断，不能据此绕过网关直连上游。

| 上游协议错误码 | 含义 |
|------|------|
| -32000 | 系统错误 |
| -32001 | 已过期 |
| -32002 | 配额超出 |
| -32003 | 认证失败 |

这些是上游 MCP 协议层代码；网关统一转成 1002 / 500，以实际网关消息为准。



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
