# linkfox-sorftime-walmart-keyword-research reference

## 子能力概览

- **功能**：研究 Walmart US 当前热词、名称反查词、热词商品、关键词指标、商品关联词和扩展词，并在明确授权后管理关键词收藏目录。
- **边界**：每次只执行一个 operation；只有 `marketQuery` 使用可选 `pattern` 业务对象；`searchProducts` 受最近 15 天窗口限制，`productKeywords` 受最近 30 天/搜索结果前三页限制。
- **MCP**：使用 `LinkFox.proxy_call`，精确 `toolName=sorftime/walmart/keywordResearch`。
- **认证**：WorkBuddy 自动注入授权；通用异常流程见 `references/onboarding.md`。
- **成本与输出**：文档上游请求按 operation 为 5/1/5/1/1/5/1/0/1；收藏写操作不得缓存或自动重放。

## 收藏与展示护栏

- `favoriteAdd` 只有用户明确要求收藏时才能调用，省略 `dict` 使用“未分类”；单目录最多 2,000 个关键词。
- `favoriteChange` 仅允许 `del` 或 `move=<目标目录>`；删除时省略 `dict` 可能从所有目录删除，必须先确认范围；移动时省略 `dict` 表示“未分类”源目录。
- `favoriteList` 的 `command` 仅允许 `all`、`dict` 或 `dict=<目录>`；API 词库与 Sorftime Professional 收藏夹不互通。
- 写操作必须检查 `data.value` 的结果码，框架层成功不代表业务写入成功；空结果、失败和下一页不能自动触发后续调用。

以下 API 参考保留该业务能力的请求参数、完整响应、错误码、MCP 与 Feedback API 细节。

---

# Walmart 关键词研究 API 参考

## MCP 调用规范

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sorftime/walmart/keywordResearch`
- **响应字段来源**：`skills/linkfox-sorftime-walmart-keyword-research/references/api.md`；只从该文件的响应章节恢复字段。
- **arguments**：本 reference 的原请求对象直接作为 `arguments`；保留 `operation` 和业务嵌套对象，不包裹 `body`、`params` 或 `data`。
- **自动授权**：WorkBuddy 自动注入授权上下文；禁止传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **解析与失败**：text JSON 只解析一次；先处理 MCP/代理错误，再处理下游 `errcode`/`code` 和消息字段。禁止 HTTP fallback、自动切换 operation 或重复计费调用。
- **市场**：Walmart 美国站；后端固定使用 Sorftime `domain=21`。

## 操作矩阵

| operation | 用途 | 必填参数 | 可选参数 | 默认 | Sorftime Request |
|---|---|---|---|---|---:|
| `marketQuery` | 筛选当前热词 | 无 | `pattern`, `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `searchByName` | 商品/类目名称反查热词 | `name` | `pageIndex` | 第 1 页 | 1 |
| `searchProducts` | 热词搜索结果商品 | `keyword` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `detail` | 关键词详情 | `keyword` | 无 | - | 1 |
| `productKeywords` | 商品关联关键词 | `productId` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 1 |
| `relatedKeywords` | 关联词拓展 | `keyword` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `favoriteAdd` | 收藏关键词 | `keyword` | `dict` | 未分类 | 1 |
| `favoriteChange` | 删除/移动收藏关键词 | `keyword`, `command` | `dict` | 见下文 | 0 |
| `favoriteList` | 查询收藏词或目录 | `command` | `pageIndex` | 第 1 页 | 1 |

## 参数规则

### marketQuery

`pattern` 可含：`keyword`（非空字符串）、`rankCondition` 和 `searchVolumeCondition`。两个条件字段均为 1 或 2 个非负整数；下界不得大于上界。单元素 `[10000]` 表示大于 10000；双元素 `[0,10000]` 按官方语义表示小于 10000。`pageSize` 范围 20–200。

### 查询类操作

- `searchByName.name` 是商品或类目名称；`pageIndex` 从 1 开始，每页最多返回 200 条。
- `searchProducts` 仅支持当前热词，返回最近 15 天搜索结果出现的商品；`pageSize` 20–200。
- `detail.keyword` 为一个非空关键词。
- `productKeywords` 返回最近 30 天商品曾出现在搜索结果前三页的关键词；`productId` 为字符串，`pageSize` 20–200。
- `relatedKeywords` 使用一个种子关键词；`pageSize` 20–200。

### 收藏类操作与写入护栏

- `favoriteAdd`: `dict` 省略时使用“未分类”，目录不存在时 Sorftime 可创建；单个目录最多保存 2,000 个关键词。仅在用户明确要求收藏时调用。
- `favoriteChange`: `command` 仅允许 `del` 或 `move=<目标目录>`。`del` 省略 `dict` 会从所有目录删除，必须显式确认；移动省略 `dict` 时源目录是“未分类”。
- `favoriteList`: `command` 仅允许 `all`、`dict`、`dict=<目录>`；对外参数统一为 `pageIndex`，后端映射成上游 `Page`；每页最多 100 条。
- API 词库与 Sorftime 专业版收藏夹彼此独立，收藏数据不互通。
- `favoriteAdd` / `favoriteChange` 紧邻调用前必须复述关键词、源目录、目标目录或删除范围，并取得本次明确确认；历史“继续”不能代替确认。
- 写调用超时、MCP 错误或结果不明确时不得自动重放。需要核验时先说明额外消耗，并在用户同意后用 `favoriteList` 查询当前状态。
- `favoriteAdd` 返回 `1` 表示关键词已存在，应按幂等的“已收藏”处理，不再重复新增；`favoriteChange` 返回 `9` 表示关键词不存在，不自动改目录或再次删除/移动。
- 同一任务内相同收藏 `toolName + arguments` 只执行一次；任何分页、换目录、移动目标变化都视为新请求。

## 请求示例

```json
{"operation":"marketQuery","pattern":{"keyword":"wireless","searchVolumeCondition":[10000]},"pageIndex":1,"pageSize":20}
```

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

```json
{"operation":"favoriteList","command":"dict","pageIndex":1}
```

写操作格式示例（不得在未获授权时执行）：

```json
{"operation":"favoriteChange","keyword":"wireless earbuds","dict":"Headphones","command":"move=Research"}
```

## 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；实际业务结果位于 `data.value` |
| `data.value` | array / object / integer / null | 实际业务结果；具体类型和元素结构由 operation 决定，见下表 |
| `operation` | string | 本次实际执行的 operation |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11` 时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 来源契约记载该值来自生产网关响应头 `X-Cost-Token`，直接解析 JSON body 时可能缺失；MCP 是否将其呈现为该字段以实际响应为准 |
| `costCredit` | integer / absent | 来源契约记载该值来自生产网关响应头 `X-Cost-Credit`，表示实际扣除算力；MCP 是否将其呈现为该字段以实际响应为准 |
| `sourceType` | string | `sorftime` |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。MCP 返回中若没有 `costToken` / `costCredit`，不得补造。网关不会改名、扁平化或补造 `data.value` 内的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

### 各 operation 的 `data.value` 类型

| operation | 类型 | 元素类型 / 说明 |
|---|---|---|
| `marketQuery` | array<object> | 关键词摘要数组 |
| `searchByName` | array<object> | 与商品或类目名称相关的关键词摘要数组 |
| `searchProducts` | array<object> | 关键词近 15 天搜索结果中的商品摘要数组 |
| `detail` | object | 单个关键词摘要对象 |
| `productKeywords` | array<object> | 商品近 30 天在搜索结果前三页获得曝光的关键词记录 |
| `relatedKeywords` | array<object> | 相关关键词摘要数组 |
| `favoriteAdd` | integer | 收藏结果码 |
| `favoriteChange` | integer | 删除或移动结果码 |
| `favoriteList` | array<string> | 关键词或目录名称数组，具体内容由 `command` 决定 |

### 关键词摘要字段

此对象用于 `marketQuery`、`searchByName`、`detail`、`relatedKeywords`，也作为 `productKeywords[].Keyword` 的嵌套对象。`marketQuery`、`searchByName`、`relatedKeywords` 的数组元素与 `detail` 对象字段一致。

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

### `productKeywords`：商品关键词记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `ShowShare` | number | 该关键词为商品带来的曝光流量占比 |
| `RecentlyPosition` | string | 最近曝光位置，如 `1,2/18` 表示第 1 页第 2 位，共 18 个位置 |
| `OrganicPosition` | string | 最近自然曝光位置，编码同 `RecentlyPosition` |
| `AdPosition` | string | 最近广告曝光位置，编码同 `RecentlyPosition` |
| `Keyword` | object | 完整关键词摘要对象；字段见“关键词摘要字段” |

### `searchProducts`：商品摘要字段

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

### 收藏类 operation 的返回值

| operation | `data.value` | 说明 |
|---|---|---|
| `favoriteAdd` | `0` | 收藏成功 |
| `favoriteAdd` | `1` | 关键词已存在 |
| `favoriteAdd` | `9` | 收藏失败 |
| `favoriteChange` | `0` | 删除或移动成功 |
| `favoriteChange` | `9` | 关键词不存在 |
| `favoriteList` | array<string> | `dict` 返回目录名；`all` 或 `dict=<目录>` 返回关键词 |

## 错误码

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 200 | 成功 | 按 operation 解析 `data.value`；写操作再检查其中的结果码 |
| 400 / 4000 | 缺少必填参数；框架校验全局必填字段时返回 400，业务条件必填校验返回 4000 | 补充 operation 的条件必填字段 |
| 4001 | 参数格式错误 | 检查 operation 大小写、分页、条件数组和 command |
| 401 | 认证失败 | 按 SKILL.md 的认证引导处理 |
| 402 | 积分不足 | 按 SKILL.md 的积分引导处理 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

## MCP 示例

```json
{"toolName":"sorftime/walmart/keywordResearch","arguments":{"operation":"detail","keyword":"wireless earbuds"}}
```
## Feedback API

工具反馈使用独立端点 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，`Content-Type: application/json`。

```json
{"skillName":"linkfox-sorftime-walmart-keyword-research","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。
