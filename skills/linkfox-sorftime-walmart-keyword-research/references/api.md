# Walmart 关键词研究 接口说明

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

## 接口：筛选当前热词（marketQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `marketQuery`，大小写严格匹配。 |
| pattern | object | 否 | 唯一可选业务嵌套对象，筛选条件见下方字段。 |
| pattern.keyword | string | 否 | 非空关键词字符串。 |
| pattern.rankCondition | array<integer> | 否 | 周搜索排名条件。1 或 2 个非负整数，下界不得大于上界；单元素 `[10000]` 表示大于 10000，双元素 `[0,10000]` 按官方语义表示小于 10000。 |
| pattern.searchVolumeCondition | array<integer> | 否 | 近 30 天搜索量条件。1 或 2 个非负整数，下界不得大于上界；单元素 `[10000]` 表示大于 10000，双元素 `[0,10000]` 按官方语义表示小于 10000。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。 |
| pageSize | integer | 否 | 默认 20，范围 20–200。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 仅筛选当前热词；`pattern` 字段及条件数组的边界语义见上方参数表。
- 本操作文档消耗为 5 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> | 筛选当前热词结果；无数据时可能为 null 或空数组。 |

#### 关键词摘要字段（`data.value[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `Keyword` | string | 关键词 |
| `KeywordCNName` | string | 关键词中文名 |
| `Images` | array<string> | 关键词搜索结果 Top 10 商品图片 URL |
| `Update` | string | 关键词最近更新时间，通常为 `yyyyMMdd` |
| `Rank` | integer | 周搜索排名 |
| `SearchVolume` | number | 近 30 天搜索量；上游可能以带小数的 JSON 数字传输 |
| `ProductCount` | integer | Walmart 搜索页展示的竞品数量 |
| `SearchFirstPageAvgPrice` | integer | 搜索结果第一页自然位商品均价；美国站单位为美分 |
| `SearchFirstPageAvgReviews` | number | 搜索结果第一页自然位商品平均评论数 |
| `SearchFirstPageAvgStar` | number | 搜索结果第一页自然位商品平均评分 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketQuery","pattern":{"keyword":"wireless","searchVolumeCondition":[10000]},"pageIndex":1,"pageSize":20}'
```

## 接口：名称反查热词（searchByName）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `searchByName`，大小写严格匹配。 |
| name | string | 是 | 非空商品或类目名称。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 每页最多返回 200 条，不提供 `pageSize`。
- 本操作文档消耗为 1 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> | 名称反查热词结果；无数据时可能为 null 或空数组。 |

#### 关键词摘要字段（`data.value[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `Keyword` | string | 关键词 |
| `KeywordCNName` | string | 关键词中文名 |
| `Images` | array<string> | 关键词搜索结果 Top 10 商品图片 URL |
| `Update` | string | 关键词最近更新时间，通常为 `yyyyMMdd` |
| `Rank` | integer | 周搜索排名 |
| `SearchVolume` | number | 近 30 天搜索量；上游可能以带小数的 JSON 数字传输 |
| `ProductCount` | integer | Walmart 搜索页展示的竞品数量 |
| `SearchFirstPageAvgPrice` | integer | 搜索结果第一页自然位商品均价；美国站单位为美分 |
| `SearchFirstPageAvgReviews` | number | 搜索结果第一页自然位商品平均评论数 |
| `SearchFirstPageAvgStar` | number | 搜索结果第一页自然位商品平均评分 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}'
```

## 接口：热词搜索结果商品（searchProducts）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `searchProducts`，大小写严格匹配。 |
| keyword | string | 是 | 一个非空关键词，按字符串传递。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。 |
| pageSize | integer | 否 | 默认 20，范围 20–200。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 仅支持当前热词，返回最近 15 天搜索结果出现的商品。
- 本操作文档消耗为 5 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> | 热词搜索结果商品结果；无数据时可能为 null 或空数组。 |

#### 商品摘要字段（`data.value[]`）

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
| `Variants` | array<object> / null | 变体列表，字段见下表 |
| `NumberOfStar` | array<number\|string> / null | 各星级评论数，按 `[星级, 评论数, ...]` 交错编码 |

`Variants` 数组元素：

| 字段 | 类型 | 说明 |
|---|---|---|
| `VariantId` | string | 变体 ProductId |
| `Url` | string | 变体商品 URL |
| `Property` | array<string> | 变体属性，按 `[属性名, 属性值, ...]` 编码 |
| `PriceUpdate` | string / null | 价格更新时间，通常为 `yyyy-MM-dd` |
| `DetailUpdate` | string / null | 详情更新时间，通常为 `yyyy-MM-dd`；无有效日期时可能使用 `--` 等上游占位符 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchProducts","keyword":"wireless earbuds","pageIndex":1,"pageSize":20}'
```

## 接口：关键词详情（detail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `detail`，大小写严格匹配。 |
| keyword | string | 是 | 一个非空关键词，按字符串传递。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 本操作文档消耗为 1 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | object | 关键词详情结果；无数据时可能为 null 或空数组。 |

#### 关键词摘要字段（`data.value`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `Keyword` | string | 关键词 |
| `KeywordCNName` | string | 关键词中文名 |
| `Images` | array<string> | 关键词搜索结果 Top 10 商品图片 URL |
| `Update` | string | 关键词最近更新时间，通常为 `yyyyMMdd` |
| `Rank` | integer | 周搜索排名 |
| `SearchVolume` | number | 近 30 天搜索量；上游可能以带小数的 JSON 数字传输 |
| `ProductCount` | integer | Walmart 搜索页展示的竞品数量 |
| `SearchFirstPageAvgPrice` | integer | 搜索结果第一页自然位商品均价；美国站单位为美分 |
| `SearchFirstPageAvgReviews` | number | 搜索结果第一页自然位商品平均评论数 |
| `SearchFirstPageAvgStar` | number | 搜索结果第一页自然位商品平均评分 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"detail","keyword":"wireless earbuds"}'
```

## 接口：商品关联关键词（productKeywords）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `productKeywords`，大小写严格匹配。 |
| productId | string | 是 | Walmart 商品编号，按字符串传递。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。 |
| pageSize | integer | 否 | 默认 20，范围 20–200。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 返回近 30 天商品曾出现在搜索结果前三页的关键词。
- 本操作文档消耗为 1 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> | 商品关联关键词结果；无数据时可能为 null 或空数组。 |

#### 商品关键词记录字段（`data.value[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `ShowShare` | number | 该关键词为商品带来的曝光流量占比 |
| `RecentlyPosition` | string | 最近曝光位置，如 `1,2/18` 表示第 1 页第 2 位，共 18 个位置 |
| `OrganicPosition` | string | 最近自然曝光位置，编码同 `RecentlyPosition` |
| `AdPosition` | string | 最近广告曝光位置，编码同 `RecentlyPosition` |
| `Keyword` | object | 完整关键词摘要对象；字段见本接口下方关键词摘要字段表 |

#### 关键词摘要字段（`data.value[].Keyword`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `Keyword` | string | 关键词 |
| `KeywordCNName` | string | 关键词中文名 |
| `Images` | array<string> | 关键词搜索结果 Top 10 商品图片 URL |
| `Update` | string | 关键词最近更新时间，通常为 `yyyyMMdd` |
| `Rank` | integer | 周搜索排名 |
| `SearchVolume` | number | 近 30 天搜索量；上游可能以带小数的 JSON 数字传输 |
| `ProductCount` | integer | Walmart 搜索页展示的竞品数量 |
| `SearchFirstPageAvgPrice` | integer | 搜索结果第一页自然位商品均价；美国站单位为美分 |
| `SearchFirstPageAvgReviews` | number | 搜索结果第一页自然位商品平均评论数 |
| `SearchFirstPageAvgStar` | number | 搜索结果第一页自然位商品平均评分 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"productKeywords","productId":"5169493923","pageIndex":1,"pageSize":20}'
```

## 接口：关联词拓展（relatedKeywords）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `relatedKeywords`，大小写严格匹配。 |
| keyword | string | 是 | 一个非空关键词，按字符串传递。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。 |
| pageSize | integer | 否 | 默认 20，范围 20–200。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 以一个种子关键词拓展相关词，不自动串行调用其他操作。
- 本操作文档消耗为 5 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<object> | 关联词拓展结果；无数据时可能为 null 或空数组。 |

#### 关键词摘要字段（`data.value[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `Keyword` | string | 关键词 |
| `KeywordCNName` | string | 关键词中文名 |
| `Images` | array<string> | 关键词搜索结果 Top 10 商品图片 URL |
| `Update` | string | 关键词最近更新时间，通常为 `yyyyMMdd` |
| `Rank` | integer | 周搜索排名 |
| `SearchVolume` | number | 近 30 天搜索量；上游可能以带小数的 JSON 数字传输 |
| `ProductCount` | integer | Walmart 搜索页展示的竞品数量 |
| `SearchFirstPageAvgPrice` | integer | 搜索结果第一页自然位商品均价；美国站单位为美分 |
| `SearchFirstPageAvgReviews` | number | 搜索结果第一页自然位商品平均评论数 |
| `SearchFirstPageAvgStar` | number | 搜索结果第一页自然位商品平均评分 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"relatedKeywords","keyword":"wireless earbuds","pageIndex":1,"pageSize":20}'
```

## 接口：收藏关键词（favoriteAdd）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `favoriteAdd`，大小写严格匹配。 |
| keyword | string | 是 | 一个非空关键词，按字符串传递。 |
| dict | string | 否 | 省略时使用“未分类”；传入时为目录名称。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 仅在用户明确要求收藏时执行；提供的目录不存在时 Sorftime 可创建。单个目录最多 2,000 个关键词。
- API 词库与 Sorftime 专业版收藏夹独立、不互通；收藏操作及列表始终绕过本地缓存。
- 本操作文档消耗为 1 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | integer | 收藏结果码：`0` 成功，`1` 关键词已存在，`9` 失败。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- `data.value=0` 表示收藏成功，`1` 表示已存在，`9` 表示收藏失败；保留并展示原值。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

以下写入示例仅在已有用户明确授权时执行。

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"favoriteAdd","keyword":"wireless earbuds","dict":"Headphones"}'
```

## 接口：删除或移动收藏关键词（favoriteChange）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `favoriteChange`，大小写严格匹配。 |
| keyword | string | 是 | 一个非空关键词，按字符串传递。 |
| command | string | 是 | 仅允许 `del` 或 `move=<目标目录>`；移动时目标目录非空。 |
| dict | string | 否 | 源目录，省略时仅操作“未分类”；其他源目录必须显式传入。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 仅在用户明确要求删除或移动时执行；不提供删除目录操作，删除最后一个词可能保留空目录。
- API 词库与 Sorftime 专业版收藏夹独立、不互通；收藏操作及列表始终绕过本地缓存。
- 本操作的上游消耗为 0 个 Sorftime Request；该计数不等同于实际扣除算力，实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | integer | 删除或移动结果码：`0` 成功，`9` 关键词不存在。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- `data.value=0` 表示删除或移动成功，`9` 表示关键词不存在；保留并展示原值。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

以下写入示例仅在已有用户明确授权时执行。

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"favoriteChange","keyword":"wireless earbuds","dict":"Headphones","command":"move=Research"}'
```

## 接口：查询收藏词或目录（favoriteList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/keywordResearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operation | string | 是 | 固定为 `favoriteList`，大小写严格匹配。 |
| command | string | 是 | 仅允许 `all`、`dict` 或 `dict=<目录>`；指定目录时目录非空。 |
| pageIndex | integer | 否 | 从 1 开始，默认 1。后端映射到上游 `Page`。 |

#### 参数与使用限制

- 仅 Walmart 美国站，后端固定 Sorftime `domain=21`。请求使用扁平 lowerCamel JSON，不外套 `params`；一次只选一个操作，不传该操作无关参数。
- 每页最多 100 条；不提供 `pageSize`。
- API 词库与 Sorftime 专业版收藏夹独立、不互通；收藏操作及列表始终绕过本地缓存。
- 本操作文档消耗为 1 个 Sorftime Request；实际扣费读取响应头及业务封装的 `costCredit`，不自行按倍数补算。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。

### 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |

#### 本地附加字段

- `_http_status`（integer）：入口脚本记录的实际 HTTP 状态，不是网关业务字段；先按此状态再结合 `errcode`、业务 `code` 判断结果，HTTP 401/402 按认证及算力引导处理。
- `_cache.hit=true` 时，`_http_status` 与费用字段均属于原请求，本次未调用网关。旧缓存未记录 HTTP 状态时该字段缺失，不将其补作 200；摘要未显示时从完整响应文件读取。

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.value` | array<string> | `dict` 返回目录名称；`all` 或 `dict=<目录>` 返回关键词。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架响应正常后再判断业务 `code` / `msg`；业务 `code=200` 表示成功，不能以外层 HTTP 200 代替业务结果。
- Sorftime 明确返回 `Code=11` 表示无数据，`requestConsumed=0`、`X-Cost-Token=0`；`X-Cost-Credit` 可能缺失，不据此推算其他收费字段。
- 失败或空结果不自动换词、翻页或切换操作；继续调用前先说明额外消耗。

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`、operation 枚举、`pageIndex>=1` 及 `pageSize` 范围 |
| 4000 | operation 的条件必填参数缺失 | 补充该 operation 对应的 `name`、`keyword`、`productId` 或 `command` |
| 4001 | 后端语义校验失败 | 检查无关参数、条件数组边界和收藏 `command` 格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4001,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl -i --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/keywordResearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"favoriteList","command":"dict","pageIndex":1}'
```

## 脚本运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 第一个位置参数；完整请求体，操作定义见上方对应接口。 |
| --inline | CLI flag | 否 | 强制完整输出，同时仍落盘。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存的读取和写入；不能替代收藏写入授权。 |
| --help / -h | CLI flag | 否 | 仅展示帮助，不请求接口。 |

基础地址优先使用 `LINKFOX_TOOL_GATEWAY`，缺省使用正式网关；认证使用 `LINKFOX_AGENT_API_KEY` 优先、回退 `LINKFOXAGENT_API_KEY` 的顺序。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。

只读研究使用 24 小时缓存：参数以 `json.dumps(..., ensure_ascii=False, sort_keys=True)` 序列化后取 SHA-256 前 16 位，保存到 `<cwd>/linkfox/.cache/linkfox-sorftime-walmart-keyword-research/`，缓存直接保存未包装的 JSON 响应，命中时使用 `_cache.hit` 标记。同一参数缓存可包含错误或空结果；不要为试探绕过缓存。`favoriteAdd`、`favoriteChange`、`favoriteList` 始终不读写响应缓存。

业务脚本通过公共 `call_api.run` 执行，并始终向它传入 `--no-cache`，由业务层单独负责缓存；公共调用器仍可能创建空缓存目录，不形成第二份响应缓存。业务封装解析公共传输层收到的 XML `ToolErrorResponse`，保留解析后的错误码与消息；不能解析的响应保留错误原文。新请求的实际 HTTP 状态记录到本地 `_http_status`，缓存读取沿用原状态，未记录状态的旧缓存不补造 HTTP 200。用 `X-Cost-Token` / `X-Cost-Credit` 覆盖响应体内同名字段。费用头缺失时不补造，非整数值按返回值展示。

完整响应按 SKILL.md 输出策略保存并登记会话元数据；业务封装在请求前于当前工作目录的会话 `data/` 下排他创建响应文件，文件名使用纳秒时间戳，避免同秒连续调用覆盖历史结果。不能创建文件时立即报错，不发起请求，也不回退到 `/tmp` 或家目录。认证或落盘失败时清理本次预留的空文件。收藏写入授权由执行流程核对，CLI 没有额外确认参数。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sorftime-walmart-keyword-research",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
