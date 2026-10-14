# linkfox-sorftime-walmart-category-market reference

## 子能力概览

- **功能**：研究 Walmart US 类目层级、自然语言类目匹配、类目市场指标和 Best Seller Top 80。
- **边界**：`tree`、`searchByName`、`marketReport` 每次只执行一个 operation；`marketReport` 必须使用数字下划线 `nodePath`，不能把自然语言名称直接作为路径；`searchByName` 最多返回 3 个相关类目，不代表精确分类。
- **MCP**：使用 `LinkFox.proxy_call`，精确 `toolName=sorftime/walmart/categoryMarket`。
- **认证**：WorkBuddy 自动注入授权；通用异常流程见 `references/onboarding.md`。
- **成本与输出**：文档上游请求分别为 5、1、5；追加 operation 或重试前必须说明成本并获得决定。

以下 API 参考保留该业务能力的请求参数、完整响应、错误码、MCP 与 Feedback API 细节。

## 业务能力与特殊规则

- `tree` 适用于需要完整层级遍历的场景，整体响应可能约 10 MB，应从 MCP 响应中按需提取，避免整棵树进入上下文。
- `searchByName` 的 `name` 是自然语言类目名称，结果最多 3 个相关匹配。
- `marketReport` 的 `nodePath` 应来自已确认的类目层级；Best Seller 只代表最多 Top 80 范围。
- 后端固定使用 Sorftime `domain=21`，数据只面向 Walmart US；空结果或失败不得自动换参数、改路径或翻页。

---

# Walmart 类目市场 API 参考

## MCP 调用规范

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sorftime/walmart/categoryMarket`
- **响应字段来源**：`skills/linkfox-sorftime-walmart-category-market/references/api.md`；只从该文件的响应章节恢复字段。
- **arguments**：本 reference 的原请求对象直接作为 `arguments`；保留 `operation` 和业务嵌套对象，不包裹 `body`、`params` 或 `data`。
- **自动授权**：WorkBuddy 自动注入授权上下文；禁止传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **解析与失败**：text JSON 只解析一次；先处理 MCP/代理错误，再处理下游 `errcode`/`code` 和消息字段。禁止 HTTP fallback、自动切换 operation 或重复计费调用。
- **市场**：Walmart 美国站；后端固定使用 Sorftime `domain=21`。

## 操作与请求参数

| operation | 用途 | 其他参数 | 必填规则 | Sorftime Request |
|---|---|---|---|---:|
| `tree` | 完整类目树 | 无 | 只需 `operation` | 5 |
| `searchByName` | 按自然语言类目名称搜索相关类目 | `name`: string | `name` 必填且非空 | 1 |
| `marketReport` | 类目市场报告与 Best Seller Top 80 | `nodePath`: string | `nodePath` 必填 | 5 |

`name` 是自然语言类目名称，例如 `patio furniture`。该操作对应 Sorftime `CategorySearchFromName`，最多返回 3 个相关类目；匹配结果不代表精确分类。

`nodePath` 是由数字类目 ID 组成、以下划线分隔的完整路径，例如 `4044_623679_1032619_5842891_9823303`。应从类目树获得，不要凭名称猜测。

请求示例：

```json
{"operation":"tree"}
```

```json
{"operation":"searchByName","name":"patio furniture"}
```

```json
{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}
```

## 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；`data.value` 按 operation 保留 Sorftime 原始数组、对象、标量或 `null` |
| `data.value` | array / object / scalar / null | 实际业务结果；具体类型和元素结构由 operation 决定，见下表 |
| `operation` | string | 本次实际执行的 `tree`、`searchByName` 或 `marketReport` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 来源契约记载该值来自生产网关响应头 `X-Cost-Token`，直接解析 JSON body 时可能缺失；MCP 是否将其呈现为该字段以实际响应为准 |
| `costCredit` | integer / absent | 来源契约记载该值来自生产网关响应头 `X-Cost-Credit`，表示实际扣除算力；MCP 是否将其呈现为该字段以实际响应为准 |
| `sourceType` | string | `sorftime` |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。MCP 返回中若没有 `costToken` / `costCredit`，不得补造。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

### 各 operation 的 `data.value` 类型

| operation | 类型 | 元素类型 / 说明 |
|---|---|---|
| `tree` | array<object> | 完整类目树；数组元素为类目节点 |
| `searchByName` | array<object> | 相关类目；最多 3 项 |
| `marketReport` | array<object> | 类目商品摘要数组；直接返回数组，不再套 `Products` 层 |

### `tree`：类目节点字段

类目树响应通常超过 10 MB，应按需提取必要节点，避免完整内容进入上下文。

| 字段 | 类型 | 说明 |
|---|---|---|
| `Id` | integer | 类目 ID |
| `ParentId` | integer | 父类目 ID；`0` 表示顶层 |
| `NodeId` | string | Walmart 类目节点 ID |
| `Name` | string | 英文类目名称 |
| `CNName` | string | 中文类目名称 |
| `URL` | string | 类目 URL |

### `searchByName`：类目匹配字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `NodeId` | string | 下划线分隔的完整类目路径，可直接作为 `marketReport.nodePath` |
| `CategoryName` | string | 类目展示名称 |

### `marketReport`：商品摘要字段

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

## 错误码

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 200 | 成功 | 按所选 operation 解析 `data.value` |
| 400 / 4000 | 缺少必填参数；框架校验全局必填字段时返回 400，业务条件必填校验返回 4000 | 补充 `operation`、`searchByName` 的 `name` 或 `marketReport` 的 `nodePath` |
| 4001 | 参数格式错误 | 检查 operation 大小写、name 是否非空及 nodePath 格式 |
| 401 | 认证失败 | 按 SKILL.md 的认证引导处理 |
| 402 | 积分不足 | 按 SKILL.md 的积分引导处理 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换参数连续重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

## MCP 示例

```json
{"toolName":"sorftime/walmart/categoryMarket","arguments":{"operation":"searchByName","name":"patio furniture"}}
```
## Feedback API

此端点与工具 API 独立：`POST https://skill-api.linkfox.com/api/v1/public/feedback`，`Content-Type: application/json`。

```json
{"skillName":"linkfox-sorftime-walmart-category-market","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。
