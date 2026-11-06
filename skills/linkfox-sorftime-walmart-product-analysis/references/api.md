# Walmart 产品分析 接口说明

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


## 运行约定

- 统一端点没有 `path` 转发字段，以 `operation` 区分四个操作，不构造其他路由。
- 市场仅限 Walmart 美国站，后端固定 Sorftime `domain=21`。每次仅接受一个商品名称或一个商品编号及一个操作；请求体必须为扁平 JSON，`operation` 大小写严格匹配 `searchByName`、`detail`、`trend`、`salesVolume`。
- 透传请求头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游普通 JSON 与 Base64/GZip 的识别、校验和解码由服务端完成。
- 不得批量或自动串行调用四个操作。翻页、更换日期范围或补调另一操作均是另一次付费请求，须先说明消耗并取得用户授权；失败或空结果不得自动变更参数连续试探。
- 入口脚本使用 24 小时单层缓存：键为排序后完整 JSON 的 SHA-256 前 16 位，文件位于 `<cwd>/linkfox/.cache/linkfox-sorftime-walmart-product-analysis/`，缓存文件直接保存响应体；默认复用未过期响应，包括已缓存的错误和空结果，不自动重试。`--no-cache` 跳过读取和写入，`--inline` 强制完整输出。公共 `call_api.run` 始终关闭自己的缓存，避免重复缓存。
- 脚本调用命令为 `python scripts/sorftime_walmart_product_analysis.py '<JSON 参数>' [--inline] [--no-cache]`；完整响应按 `SKILL.md` 输出策略保存于当前工作目录，不可写时在请求前报错，不回退到临时目录。认证兼容两种 API Key 变量，优先 `LINKFOX_AGENT_API_KEY`；网关优先 `LINKFOX_TOOL_GATEWAY`，默认地址见公共规则。

## 接口：名称搜索（searchByName）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/productAnalysis`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `operation` | string | 是 | 固定为 `searchByName`，区分大小写。 |
| `name` | string | 是 | 非空自然语言商品名称。 |
| `pageIndex` | integer | 否 | 从 1 开始，默认 1；每页最多 100 条。 |

本操作消耗 2 Sorftime Request；实际扣费及无数据特殊规则见本接口响应说明。

对应上游 `ProductSearchFromName`，按名称返回相关商品，不提供多条件商品库筛选或类目市场查询。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息 |
| `data` | object | 固定响应容器；`data.value` 保留本操作的 Sorftime 原始值，可能是对象、数组、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName`、`detail`、`trend` 或 `salesVolume` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `_cache` | object / absent | 入口脚本本地缓存标记，不属于网关业务响应。 |
| `_cache.hit` | boolean / absent | 命中缓存时为 `true`；计费字段来自原始请求，本次无新增扣费。 |
| `_http_status` | integer / null / absent | 入口脚本保存的实际 HTTP 状态；连接失败时为 `null`。缓存命中时是原请求的历史状态，旧缓存可能缺失，不能据缺失判断成功。此字段不是网关业务字段。 |
| `error` | string / absent | 入口脚本在连接失败、无法解析响应或无有效响应体的 HTTP 异常时给出的错误说明。 |
| `details` | string / absent | 无法解析时保留的原始响应内容。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。`data.value=null` 本身不等于 `Code=11`：生产实测某些 `Code=0` 空详情仍会正常消耗 Request，应结合 `msg` 与 `requestConsumed` 判断。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value` 结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> / null | 相关商品摘要数组；缺数据时可能为 `null` 或空数组，指标暂缺时字段可能为 `null` 或不出现。 |

#### 商品字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `Title` | string | 商品标题 |
| `Photo` | array<string> | 商品图片 URL 数组 |
| `ListingSalesVolumeOfMonth` | integer | Listing 维度近 30 天预估销量，不区分变体 |
| `ListingSalesOfMonth` | integer | Listing 维度近 30 天预估销售额；美国站单位为美分 |
| `ProductId` | string | Walmart ProductId |
| `ParentProductId` | string | 父商品 ProductId |
| `Price` | integer | 售价；美国站单位为美分，如 `1999` 表示 `$19.99` |
| `Brand` | string | 品牌 |
| `Seller` | string | 采集时的卖家名称 |
| `Shipedby` | string | 采集时的配送方式；字段名是上游原始拼写 |
| `WFSFee` | integer | WFS 费用；美国站单位为美分 |
| `Attribute` | array<string> / null | 商品属性，按 `[属性名, 属性值, ...]` 交错编码 |
| `FirstReviewsDate` | string / null | 首条评论日期，`yyyy-MM-dd` |
| `ReviewsCount` | integer | 评论数 |
| `Ratings` | number | 评分，如 `4.8` |
| `NodePath` | array<string\|null> | 类目及排名记录，按 `[类目名, NodeId, 排名日期, 排名, ...]` 分组编码；某日排名缺失时对应位置为 `null` |
| `Label` | array<string> | 商品标签，如 `pickup`、`savewith`、`bestsell` |
| `PopularPick` | integer | Popular Pick 标记；`1` 表示存在 |
| `Clearance` | integer | Clearance 标记；`1` 表示存在 |
| `ReducedPrice` | integer | Reduced Price 标记；`1` 表示存在 |
| `Rollback` | integer | Rollback 标记；`1` 表示存在 |
| `FlashDeal` | integer | Flash Deal 标记；`1` 表示存在 |
| `Size` | array<string> / null | 外包装尺寸 `[最长边, 次长边, 最短边]`，单位 cm |
| `Weight` | number | 商品重量，单位 g |
| `Variants` | array / null | 对象数组形式的变体数据，见下表 |
| `NumberOfStar` | array<number\|string> / null | 各星级评论数，按 `[星级, 评论数, ...]` 交错编码 |

#### `Variants` 对象数组

`Variants` 是对象数组，数组元素字段如下：

| 字段 | 类型 | 说明 |
|---|---|---|
| `VariantId` | string | 变体 ProductId |
| `Url` | string | 变体商品 URL |
| `Property` | array<string> | 变体属性，按 `[属性名, 属性值, ...]` 编码 |
| `PriceUpdate` | string / null | 价格更新时间，通常为 `yyyy-MM-dd` |
| `DetailUpdate` | string / null | 详情更新时间，通常为 `yyyy-MM-dd`；无有效日期时可能使用 `--` 等上游占位符 |


### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层状态正常后，若有业务 `code`，结合其成功值 `200` 与 `msg` 判断业务结果；参数或服务异常可能仅返回 `errcode` / `errmsg`。
- Sorftime `Code=11` 表示明确无数据并保持零 Request；单凭 `data.value=null` 不能推断免计费。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、日期格式及 `pageIndex>=1` |
| 4000 | operation 的条件必填参数缺失 | 补充 `searchByName.name`，或 `detail`、`trend`、`salesVolume` 的 `productId` |
| 4001 | 后端语义校验失败 | 检查无关参数、真实日历日期及开始/结束日期顺序 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动改变日期或操作重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl --max-time 150 -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}'
```

## 接口：商品详情（detail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/productAnalysis`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `operation` | string | 是 | 固定为 `detail`，区分大小写。 |
| `productId` | string | 是 | 非空 Walmart ProductId；即使仅含数字也必须使用字符串。 |

本操作消耗 1 Sorftime Request；实际扣费及无数据特殊规则见本接口响应说明。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息 |
| `data` | object | 固定响应容器；`data.value` 保留本操作的 Sorftime 原始值，可能是对象、数组、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName`、`detail`、`trend` 或 `salesVolume` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `_cache` | object / absent | 入口脚本本地缓存标记，不属于网关业务响应。 |
| `_cache.hit` | boolean / absent | 命中缓存时为 `true`；计费字段来自原始请求，本次无新增扣费。 |
| `_http_status` | integer / null / absent | 入口脚本保存的实际 HTTP 状态；连接失败时为 `null`。缓存命中时是原请求的历史状态，旧缓存可能缺失，不能据缺失判断成功。此字段不是网关业务字段。 |
| `error` | string / absent | 入口脚本在连接失败、无法解析响应或无有效响应体的 HTTP 异常时给出的错误说明。 |
| `details` | string / absent | 无法解析时保留的原始响应内容。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。`data.value=null` 本身不等于 `Code=11`：生产实测某些 `Code=0` 空详情仍会正常消耗 Request，应结合 `msg` 与 `requestConsumed` 判断。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value` 结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | object / array / null | 单个商品详情对象；缺数据时可能为 `null` 或空数组，指标暂缺时字段可能为 `null` 或不出现。 |

#### 商品字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `Title` | string | 商品标题 |
| `Photo` | array<string> | 商品图片 URL 数组 |
| `ListingSalesVolumeOfMonth` | integer | Listing 维度近 30 天预估销量，不区分变体 |
| `ListingSalesOfMonth` | integer | Listing 维度近 30 天预估销售额；美国站单位为美分 |
| `ProductId` | string | Walmart ProductId |
| `ParentProductId` | string | 父商品 ProductId |
| `Price` | integer | 售价；美国站单位为美分，如 `1999` 表示 `$19.99` |
| `Brand` | string | 品牌 |
| `Seller` | string | 采集时的卖家名称 |
| `Shipedby` | string | 采集时的配送方式；字段名是上游原始拼写 |
| `WFSFee` | integer | WFS 费用；美国站单位为美分 |
| `Attribute` | array<string> / null | 商品属性，按 `[属性名, 属性值, ...]` 交错编码 |
| `FirstReviewsDate` | string / null | 首条评论日期，`yyyy-MM-dd` |
| `ReviewsCount` | integer | 评论数 |
| `Ratings` | number | 评分，如 `4.8` |
| `NodePath` | array<string\|null> | 类目及排名记录，按 `[类目名, NodeId, 排名日期, 排名, ...]` 分组编码；某日排名缺失时对应位置为 `null` |
| `Label` | array<string> | 商品标签，如 `pickup`、`savewith`、`bestsell` |
| `PopularPick` | integer | Popular Pick 标记；`1` 表示存在 |
| `Clearance` | integer | Clearance 标记；`1` 表示存在 |
| `ReducedPrice` | integer | Reduced Price 标记；`1` 表示存在 |
| `Rollback` | integer | Rollback 标记；`1` 表示存在 |
| `FlashDeal` | integer | Flash Deal 标记；`1` 表示存在 |
| `Size` | array<string> / null | 外包装尺寸 `[最长边, 次长边, 最短边]`，单位 cm |
| `Weight` | number | 商品重量，单位 g |
| `Variants` | array / null | 扁平数组形式的变体数据，见下表 |
| `NumberOfStar` | array<number\|string> / null | 各星级评论数，按 `[星级, 评论数, ...]` 交错编码 |
| `Pickup` | integer | 详情扩展：Pickup 标签标记；`1` 表示存在 |
| `Savewith` | integer | 详情扩展：Save with 标签标记；`1` 表示存在 |
| `Bestseller` | integer | 详情扩展：Best Seller 标签标记；`1` 表示存在 |
| `UpdateDate` | string / null | 详情扩展：商品数据更新时间，通常为 `yyyy-MM-dd` |

#### `Variants` 扁平数组

`Variants` 在当前生产响应中是扁平数组，不是对象数组。每 3 项表示一个变体：

| 组内下标 | 类型 | 说明 |
|---:|---|---|
| `0` | string | 变体 ProductId |
| `1` | string | 变体商品 URL；上游值可能带前导空格，使用前宜 `trim` |
| `2` | array<string> | 变体属性，按 `[属性名, 属性值, ...]` 编码 |

例如两个变体的整体结构为 `[VariantId, Url, Property, VariantId, Url, Property]`。


### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层状态正常后，若有业务 `code`，结合其成功值 `200` 与 `msg` 判断业务结果；参数或服务异常可能仅返回 `errcode` / `errmsg`。
- Sorftime `Code=11` 表示明确无数据并保持零 Request；单凭 `data.value=null` 不能推断免计费。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、日期格式及 `pageIndex>=1` |
| 4000 | operation 的条件必填参数缺失 | 补充 `searchByName.name`，或 `detail`、`trend`、`salesVolume` 的 `productId` |
| 4001 | 后端语义校验失败 | 检查无关参数、真实日历日期及开始/结束日期顺序 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动改变日期或操作重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl --max-time 150 -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"detail","productId":"5169493923"}'
```

## 接口：商品趋势（trend）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/productAnalysis`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `operation` | string | 是 | 固定为 `trend`，区分大小写。 |
| `productId` | string | 是 | 非空 Walmart ProductId；即使仅含数字也必须使用字符串。 |

本操作消耗 2 Sorftime Request；实际扣费及无数据特殊规则见本接口响应说明。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息 |
| `data` | object | 固定响应容器；`data.value` 保留本操作的 Sorftime 原始值，可能是对象、数组、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName`、`detail`、`trend` 或 `salesVolume` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `_cache` | object / absent | 入口脚本本地缓存标记，不属于网关业务响应。 |
| `_cache.hit` | boolean / absent | 命中缓存时为 `true`；计费字段来自原始请求，本次无新增扣费。 |
| `_http_status` | integer / null / absent | 入口脚本保存的实际 HTTP 状态；连接失败时为 `null`。缓存命中时是原请求的历史状态，旧缓存可能缺失，不能据缺失判断成功。此字段不是网关业务字段。 |
| `error` | string / absent | 入口脚本在连接失败、无法解析响应或无有效响应体的 HTTP 异常时给出的错误说明。 |
| `details` | string / absent | 无法解析时保留的原始响应内容。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。`data.value=null` 本身不等于 `Code=11`：生产实测某些 `Code=0` 空详情仍会正常消耗 Request，应结合 `msg` 与 `requestConsumed` 判断。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value` 结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | object / array / null | 单个商品趋势对象；缺数据时可能为 `null` 或空数组，指标暂缺时字段可能为 `null` 或不出现。 |


趋势序列按 `[日期, 值, 日期, 值, ...]` 交错编码。真实响应中的日期和值当前均以字符串传输，调用方不要依赖 JSON 数字类型；需要计算时再显式转换。`RankTrend` 是二维数组，编码规则单独列出。

| 字段 | 类型 | 说明 |
|---|---|---|
| `ProductId` | string | Walmart ProductId |
| `ListingSalesVolumeOfMonth` | integer | 当前 Listing 维度近 30 天预估销量 |
| `ListingSalesOfMonth` | integer | 当前 Listing 维度近 30 天预估销售额；美国站单位为美分 |
| `ListingSalesVolumeOfMonthTrend` | array<string> | 月销量历史，按 `[yyyy-MM-dd, 销量, ...]` 编码 |
| `ListingSalesOfMonthTrend` | array<string> | 月销售额历史，按 `[yyyy-MM-dd, 销售额, ...]` 编码；金额单位为美分 |
| `PriceTrend` | array<string> | 价格历史，按 `[yyyy-MM-dd, 价格, ...]` 编码；金额单位为美分 |
| `ReviewsTrend` | array<string> | 评论数历史，按 `[yyyy-MM-dd, 评论数, ...]` 编码 |
| `StarTrend` | array<string> | 评分历史，按 `[yyyy-MM-dd, 评分, ...]` 编码；当前响应示例值为 `5.00` |
| `RankTrend` | array<array<string>> | 各类目排名历史；每行按 `[类目名, NodeId, 日期, 排名, 日期, 排名, ...]` 编码 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层状态正常后，若有业务 `code`，结合其成功值 `200` 与 `msg` 判断业务结果；参数或服务异常可能仅返回 `errcode` / `errmsg`。
- Sorftime `Code=11` 表示明确无数据并保持零 Request；单凭 `data.value=null` 不能推断免计费。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、日期格式及 `pageIndex>=1` |
| 4000 | operation 的条件必填参数缺失 | 补充 `searchByName.name`，或 `detail`、`trend`、`salesVolume` 的 `productId` |
| 4001 | 后端语义校验失败 | 检查无关参数、真实日历日期及开始/结束日期顺序 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动改变日期或操作重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl --max-time 150 -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"trend","productId":"5169493923"}'
```

## 接口：销量记录（salesVolume）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/productAnalysis`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `operation` | string | 是 | 固定为 `salesVolume`，区分大小写。 |
| `productId` | string | 是 | 非空 Walmart ProductId；即使仅含数字也必须使用字符串。 |
| `queryDate` | string | 否 | 开始日期，`yyyy-MM-dd`。 |
| `queryEndDate` | string | 否 | 截止日期，`yyyy-MM-dd`；仅给开始日期时默认当前日。 |
| `pageIndex` | integer | 否 | 从 1 开始，默认 1；每页最多 100 条。 |

本操作消耗 1 Sorftime Request；实际扣费及无数据特殊规则见本接口响应说明。

两日期均省略时默认最近 30 天；必须使用真实日历日期，开始日期不得晚于截止日期。最早可查日期及历史覆盖由 Sorftime 当前数据决定，不承诺固定最早日期。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息 |
| `data` | object | 固定响应容器；`data.value` 保留本操作的 Sorftime 原始值，可能是对象、数组、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName`、`detail`、`trend` 或 `salesVolume` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `_cache` | object / absent | 入口脚本本地缓存标记，不属于网关业务响应。 |
| `_cache.hit` | boolean / absent | 命中缓存时为 `true`；计费字段来自原始请求，本次无新增扣费。 |
| `_http_status` | integer / null / absent | 入口脚本保存的实际 HTTP 状态；连接失败时为 `null`。缓存命中时是原请求的历史状态，旧缓存可能缺失，不能据缺失判断成功。此字段不是网关业务字段。 |
| `error` | string / absent | 入口脚本在连接失败、无法解析响应或无有效响应体的 HTTP 异常时给出的错误说明。 |
| `details` | string / absent | 无法解析时保留的原始响应内容。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。`data.value=null` 本身不等于 `Code=11`：生产实测某些 `Code=0` 空详情仍会正常消耗 Request，应结合 `msg` 与 `requestConsumed` 判断。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value` 结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<array> / null | 销量记录行数组，每行为 `[date, sales, type]`；缺数据时可能为 `null` 或空数组，指标暂缺时字段可能为 `null` 或不出现。 |


`data.value` 是二维数组。真实响应当前把三个值都序列化为字符串，例如 `["2026-08-31","10000","2"]`；下表说明其业务类型。

| 下标 | 业务类型 | 说明 |
|---:|---|---|
| `0` | date | 记录日期，`yyyy-MM-dd` |
| `1` | integer | 销量值 |
| `2` | integer | 记录类型；`2` 表示昨日单日销量 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层状态正常后，若有业务 `code`，结合其成功值 `200` 与 `msg` 判断业务结果；参数或服务异常可能仅返回 `errcode` / `errmsg`。
- Sorftime `Code=11` 表示明确无数据并保持零 Request；单凭 `data.value=null` 不能推断免计费。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、日期格式及 `pageIndex>=1` |
| 4000 | operation 的条件必填参数缺失 | 补充 `searchByName.name`，或 `detail`、`trend`、`salesVolume` 的 `productId` |
| 4001 | 后端语义校验失败 | 检查无关参数、真实日历日期及开始/结束日期顺序 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动改变日期或操作重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl --max-time 150 -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"salesVolume","productId":"5169493923","queryDate":"2026-07-01","queryEndDate":"2026-07-31","pageIndex":1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sorftime-walmart-product-analysis",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
