---
name: linkfox-wb-sorftime-walmart
display_name: LinkFox Sorftime沃尔玛选品
display_name_en: LinkFox Sorftime Walmart Product Research
description: 面向 Walmart 美国站的 Sorftime 选品研究能力，支持类目、商品与关键词的发现、分析、趋势判断和关键词收藏管理。
description_zh: 面向 Walmart 美国站卖家提供可审计的 Sorftime 选品研究：定位类目并查看市场与 Best Seller，按名称发现商品并查看详情、趋势和销量，研究热词、商品关联词、扩展词及关键词收藏目录。通过 Linkfox MCP 按研究对象选择单个 operation；结果保留原始字段、消耗信息、时间窗口与数据限制。
description_en: Sorftime-powered Walmart US product research through Linkfox MCP for category, product, trend, sales, keyword, expansion, and explicitly confirmed saved-keyword management. Route each request to one operation and preserve source fields, windows, cost, and limitations.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Sorftime沃尔玛选品（LinkFox Sorftime Walmart Product Research）

这是面向 Walmart 美国站卖家的选品研究能力：当用户需要从类目、商品或关键词出发发现机会、核对市场信号、追踪商品变化或管理研究词库时，按研究对象和目标返回结构化 Sorftime 数据。它支持类目层级与市场概览、商品当前信息与历史销量、关键词市场与关联关系，以及经用户明确授权的关键词收藏操作。本能力登记 3 个子能力标识、16 个 operation 和 3 个精确 endpoint toolName，均通过 `LinkFox.proxy_call` 调用。

子能力标识为：`linkfox-sorftime-walmart-category-market`、`linkfox-sorftime-walmart-product-analysis`、`linkfox-sorftime-walmart-keyword-research`。它们共同使用 `tool_key=sorftime_walmart`，但每次请求仍必须只选择一个 operation。

## 能力边界

### 能力范围

- **类目定位与市场研究**（`linkfox-sorftime-walmart-category-market`）：用 `tree` 获取 Walmart US 类目层级，用 `searchByName` 将自然语言类目名匹配到最多 3 个相关类目，用 `marketReport` 按已确认的数字下划线 `nodePath` 查看类目市场指标和最多 Top 80 的 Best Seller。适用于类目树、类目节点、类目规模、市场报告和热销商品研究。
- **商品发现与商品分析**（`linkfox-sorftime-walmart-product-analysis`）：用 `searchByName` 按自然语言商品名发现相关商品，用 `detail` 查看单个 `productId` 的当前摘要，用 `trend` 查看商品历史变化，用 `salesVolume` 查看日期/变体销量行。适用于竞品发现、ProductId 核对、价格评分等当前字段、趋势和按日销量。
- **关键词市场与关系研究**（`linkfox-sorftime-walmart-keyword-research`）：用 `marketQuery` 按热度、排名或搜索量条件筛选当前热词，用 `searchByName` 反查商品/类目名称相关热词，用 `searchProducts` 查看热词对应商品，用 `detail` 查看关键词指标，用 `productKeywords` 反查商品关联词，用 `relatedKeywords` 扩展词；`favoriteAdd`、`favoriteChange`、`favoriteList` 用于已明确授权的关键词收藏目录管理。
- **Walmart US 数据调用**：三个业务端点均由后端固定使用 Sorftime `domain=21`；结果中的 `data.value` 保留对应 operation 的上游对象、数组、标量或 `null`，并返回 `operation`、`requestConsumed`、`costToken` 等审计字段（具体字段以各 reference 为准）。
- **可复核的 MCP 输出**：记录实际 `toolName`、`arguments`、operation、`requestConsumed`、`costToken` 和时间字段；收藏写操作不缓存、不自动重放。

### 边界与限制

- **市场范围固定**：只研究 Walmart 美国站；不能用本能力推断其他站点、Walmart 交易保证、实际利润或未来销量。
- **一次一个 operation**：一次请求只发送一个大小写严格匹配的 operation。不得为了“完整选品”自动串联类目、商品、关键词查询，也不得在空结果、失败或不确定时自动换词、换路径、换日期或翻页。
- **追加请求需说明成本**：第二个 operation、不同筛选条件、另一页或不同日期范围都可能产生新的 Sorftime 请求；先说明可能产生的积分消耗，再由用户决定是否继续。
- **类目路径不能猜**：`marketReport` 只接受数字 ID 以下划线连接的完整 `nodePath`；自然语言类目名应先用 `searchByName` 获取相关候选，不能把名称直接当路径。
- **数据窗口由 Sorftime 控制**：关键词热词为当前数据；`searchProducts` 使用最近 15 天搜索结果窗口；`productKeywords` 使用最近 30 天商品出现在搜索结果前三页的窗口；商品趋势的最早日期以实际响应为准。
- **收藏是外部状态变更**：`favoriteAdd` 与 `favoriteChange` 只有在用户明确要求时才可调用；删除时省略 `dict` 可能从所有目录删除，必须先确认范围。单个目录最多 2,000 个关键词，且 API 词库不与 Sorftime Professional 收藏夹同步。
- **认证与计费前置**：WorkBuddy 自动注入授权，禁止传入任何凭证。结果不是法律、财务或经营保证；积分不足、权限、上游限制和服务错误必须按返回信息处理。
- **不适用场景**：不提供非 Walmart US 站点数据、订单/库存/物流、广告投放、Listing 生成、店铺运营、跨平台选品、超出上述 operation 的 Sorftime Walmart“其他”接口，或脱离返回数据的主观投资/收益承诺。

## 工具选择指南

先判断用户的主要研究对象，再选择最小的一次调用；表中的 Sorftime Request 是文档标示的上游请求数，不等同于最终 `costToken`。如果用户的目标横跨多个 operation，应先推荐最匹配的一个，并说明另一个需要额外付费调用，由用户决定是否继续。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 想看 Walmart 完整类目层级或推导节点路径 | `linkfox-sorftime-walmart-category-market` → `tree`（5） | 只知道自然语言类目名时改用 `searchByName`（1）；已有完整 `nodePath` 要市场数据时改用 `marketReport`（5） |
| 想把自然语言类目名匹配到类目节点 | `linkfox-sorftime-walmart-category-market` → `searchByName`（1） | 不要把相关匹配当精确分类；需要完整层级时用 `tree` |
| 已有类目 `nodePath`，想看规模、指标和 Best Seller | `linkfox-sorftime-walmart-category-market` → `marketReport`（5） | 没有可信路径时先让用户从 `searchByName` 返回中选择，不能猜路径 |
| 想按商品名发现 Walmart 相关产品 | `linkfox-sorftime-walmart-product-analysis` → `searchByName`（2） | 已有 `productId` 时用 `detail`、`trend` 或 `salesVolume`，不要继续名称搜索 |
| 想看某个 ProductId 的当前详情、价格或评分 | `linkfox-sorftime-walmart-product-analysis` → `detail`（1） | 想看变化过程用 `trend`；只要日期销量行用 `salesVolume` |
| 想看商品历史变化或趋势 | `linkfox-sorftime-walmart-product-analysis` → `trend`（2） | 不要用当前 `detail` 代替历史数据；历史范围由 Sorftime 决定 |
| 想看昨日、按日或变体销量 | `linkfox-sorftime-walmart-product-analysis` → `salesVolume`（1） | 需要日期区间时补 `queryDate`/`queryEndDate`；不要为解释趋势自动再调 `trend` |
| 想筛选当前高热度/排名/搜索量关键词 | `linkfox-sorftime-walmart-keyword-research` → `marketQuery`（5） | 只知道商品/类目名称时用 `searchByName`；分页和条件变更都需重新授权 |
| 想从商品或类目名称反查热词 | `linkfox-sorftime-walmart-keyword-research` → `searchByName`（1） | 想看某个关键词的指标用 `detail`；想看热词商品用 `searchProducts` |
| 想查看某个热词带来的商品 | `linkfox-sorftime-walmart-keyword-research` → `searchProducts`（5） | 需要关键词本身指标用 `detail`；该结果受最近 15 天窗口限制 |
| 想看一个关键词的搜索量、排名等指标 | `linkfox-sorftime-walmart-keyword-research` → `detail`（1） | 想拓展同义/相关词用 `relatedKeywords`，不要把详情当拓词结果 |
| 想从商品反查关联关键词 | `linkfox-sorftime-walmart-keyword-research` → `productKeywords`（1） | 该结果是最近 30 天且限搜索结果前三页；仅有商品名时先走商品发现或名称反查 |
| 想扩展一个种子关键词 | `linkfox-sorftime-walmart-keyword-research` → `relatedKeywords`（5） | 只是想看关键词自身数据用 `detail`；高消耗扩展前要提醒用户 |
| 想收藏、删除、移动或列出关键词目录 | `linkfox-sorftime-walmart-keyword-research` → `favoriteAdd`/`favoriteChange`/`favoriteList` | 写操作必须有明确授权；删除省略目录的范围要单独确认，查询收藏不走缓存 |

选择思路：类目名称对应类目模块，商品名称或 `productId` 对应商品模块，热词/关联词/收藏目录对应关键词模块。`searchByName` 在类目、商品、关键词模块中含义不同，必须根据输入对象选择；不要因用户说“选品”就默认调用多个接口。满足程度相同时选择上表默认 operation，并在执行前说明它的返回形态和潜在消耗。

## 业务需求路由速查

按上表选择 operation 后，使用对应 reference 查完整参数、响应和错误码；脚本路径均相对于 skill 根目录。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-sorftime-walmart-category-market` | `tree`：完整类目树 | `references/linkfox-sorftime-walmart-category-market.md` | `/sorftime/walmart/categoryMarket` | `sorftime/walmart/categoryMarket` |
| `linkfox-sorftime-walmart-category-market` | `searchByName`：自然语言类目匹配 | `references/linkfox-sorftime-walmart-category-market.md` | `/sorftime/walmart/categoryMarket` | `sorftime/walmart/categoryMarket` |
| `linkfox-sorftime-walmart-category-market` | `marketReport`：类目市场与 Best Seller Top 80 | `references/linkfox-sorftime-walmart-category-market.md` | `/sorftime/walmart/categoryMarket` | `sorftime/walmart/categoryMarket` |
| `linkfox-sorftime-walmart-product-analysis` | `searchByName`：相关商品发现 | `references/linkfox-sorftime-walmart-product-analysis.md` | `/sorftime/walmart/productAnalysis` | `sorftime/walmart/productAnalysis` |
| `linkfox-sorftime-walmart-product-analysis` | `detail`：商品当前详情 | `references/linkfox-sorftime-walmart-product-analysis.md` | `/sorftime/walmart/productAnalysis` | `sorftime/walmart/productAnalysis` |
| `linkfox-sorftime-walmart-product-analysis` | `trend`：商品历史趋势 | `references/linkfox-sorftime-walmart-product-analysis.md` | `/sorftime/walmart/productAnalysis` | `sorftime/walmart/productAnalysis` |
| `linkfox-sorftime-walmart-product-analysis` | `salesVolume`：按日/变体销量 | `references/linkfox-sorftime-walmart-product-analysis.md` | `/sorftime/walmart/productAnalysis` | `sorftime/walmart/productAnalysis` |
| `linkfox-sorftime-walmart-keyword-research` | `marketQuery`：当前热词条件筛选 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `searchByName`：名称反查热词 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `searchProducts`：热词搜索结果商品 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `detail`：关键词指标详情 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `productKeywords`：商品关联关键词 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `relatedKeywords`：关联词扩展 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `favoriteAdd`：新增关键词收藏 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `favoriteChange`：删除/移动收藏 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |
| `linkfox-sorftime-walmart-keyword-research` | `favoriteList`：收藏词/目录列表 | `references/linkfox-sorftime-walmart-keyword-research.md` | `/sorftime/walmart/keywordResearch` | `sorftime/walmart/keywordResearch` |

认证与积分引导见 `references/onboarding.md`；本 skill 没有本地 helper。

## MCP 调用方式

- 只使用 `LinkFox.proxy_call`。根据研究对象选择路由表中的精确 `toolName`，区分大小写且不带前导 `/`。
- 原请求对象直接放入 `arguments`；必须保留大小写严格的 `operation`。除 `marketQuery.pattern` 外不增加业务嵌套，也不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入授权上下文；禁止传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- text JSON 只解析一次。先判断 MCP 连接、工具、schema 与 `isError`，再判断框架层 `errcode/errmsg`、业务层 `code/msg` 和 `data.value`。
- MCP 不可用时禁止回退旧 HTTP 网关、脚本或其他工具。失败、空结果、下一页和不同 operation 不得自动触发第二次调用。
- 类目、商品和关键词只读 operation 在同一任务内相同 `toolName + arguments` 不重复调用。旧脚本的 24 小时缓存、自动落盘、会话元数据和 stdout 摘要不属于 MCP 能力。
- `favoriteAdd`、`favoriteChange` 紧邻调用前必须复述关键词、目录和动作并取得明确确认；删除省略 `dict` 时须明确确认“从所有目录删除”。写结果不明确时禁止自动重放。
- 收藏幂等：`favoriteAdd.data.value=1` 按“已存在”处理，不再次新增；`favoriteChange.data.value=9` 按“不存在”处理，不自动换目录重试。需要核验时先说明额外消耗，由用户同意后调用 `favoriteList`。
- 每个追加 operation、筛选、分页、日期或核验调用都可能产生新消耗，执行前说明并由用户决定。
- 完整参数、响应与错误见三个对应 reference；认证和积分异常见 `references/onboarding.md`。
## 使用示例

以下示例只展示请求形态，不代表应自动执行整套流程。每个示例都只包含一个 operation；`requestConsumed`/`costToken` 以实际返回为准。

### 类目层

```json
{"operation":"searchByName","name":"patio furniture"}
```

返回 `data.value` 中最多 3 个相关类目，重点读取 `NodeId`、`CategoryName`；它们是相关匹配，不等于精确分类。用户选定节点并取得完整路径后，才可以单独调用：

```json
{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}
```

市场报告返回实际提供的指标与最多 Top 80 Best Seller。若确实需要全层级遍历才使用：

```json
{"operation":"tree"}
```

`tree` 约可能产生 10 MB 响应，属于 5 个 Sorftime Request 的高消耗操作；从 MCP 响应中按需提取必要节点，不要把完整类目树放入上下文。

### 商品层

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

该调用返回最多 100 个相关商品/页，应标注为 related products；从返回结果获得 `productId` 后，可按单一目标分别调用：

```json
{"operation":"detail","productId":"5169493923"}
```

```json
{"operation":"trend","productId":"5169493923"}
```

```json
{"operation":"salesVolume","productId":"5169493923","queryDate":"2026-07-01","queryEndDate":"2026-07-31","pageIndex":1}
```

`detail` 只呈现实际返回的 ProductSummeryObject 字段；`trend` 先确认响应中的时间字段和单位；`salesVolume` 行按 `[date, sales, type]` 解释，其中 `type=2` 表示昨日销量。日期范围和另一个 operation 都会产生额外付费调用，不能默认补调。

### 关键词层

按条件筛选当前热词：

```json
{"operation":"marketQuery","pattern":{"keyword":"wireless","searchVolumeCondition":[10000]},"pageIndex":1,"pageSize":20}
```

`[10000]` 表示大于 10000 的下界；`[0,10000]` 使用 Sorftime 文档中的小于 10000 语义。`pageSize` 为 20–200，筛选和分页属于新的付费调用。

研究单个关键词或商品关联词：

```json
{"operation":"detail","keyword":"wireless earbuds"}
```

```json
{"operation":"productKeywords","productId":"5169493923","pageIndex":1,"pageSize":20}
```

`productId` 和关键词都按字符串传递；商品关联词受最近 30 天、搜索结果前三页限制。查询收藏目录：

```json
{"operation":"favoriteList","command":"dict","pageIndex":1}
```

新增收藏或删除/移动属于外部状态变更，必须在用户明确授权后执行。例如移动一个已收藏词：

```json
{"operation":"favoriteChange","keyword":"wireless earbuds","dict":"Headphones","command":"move=Research"}
```

`command="del"` 且省略 `dict` 可能从所有目录删除，执行前必须确认删除范围；成功与否要检查 `data.value` 中的结果码，不能只看框架层成功状态。

## 展示规则

1. **先报调用事实**：说明实际选择的子能力和 `operation`，回显关键输入；有返回时展示 `requestConsumed`、`costToken`、`costTime`、`sourceType`，并区分缓存命中与真实上游调用。
2. **类目结果有限展示**：`tree` 只展示用户需要的类目名、`Id`/`ParentId`/`NodeId` 层级和推导出的 `nodePath`，绝不把约 10 MB 全树直接倾倒到对话；`searchByName` 最多列 3 个 `NodeId`/`CategoryName` 对，并标注“相关匹配”。
3. **类目市场客观呈现**：`marketReport` 只总结响应实际返回的指标，Best Seller 紧凑展示并标注“最多 Top 80 范围”，不能暗示覆盖整个类目目录。
4. **商品结果按对象展示**：名称搜索结果标注为相关商品并回显请求页；`detail` 只呈现 ProductSummeryObject 实际字段；`trend` 展示前先识别时间字段和单位；`salesVolume` 明确 `[date, sales, type]` 结构并标记 `type=2` 的昨日记录。
5. **关键词结果保留语义**：展示市场指标、排名、搜索量、相关词和商品关联词时保留 Sorftime 的观察窗口与估算属性；标明最近 15 天/30 天限制，不把估算需求或观察值改写为保证销量。
6. **收藏操作展示结果码**：`favoriteAdd`、`favoriteChange`、`favoriteList` 显示返回的 `data.value` 和 operation；新增的 `0/1/9`、变更的 `0/9` 按 reference 解释，框架层成功不代表收藏写入一定成功。
7. **数据来源与空值**：标注 Walmart US、Sorftime 和实际查询时间；保持 `data.value` 原始字段含义，不补造缺失的分类关系、指标、日期、单位或商品交易事实；不可用字段直接说明“响应未返回”。
8. **错误给出修正建议**：先展示 `errcode`/`errmsg`，再展示业务 `code`/`msg`；400/4000 补必填字段，4001 修正 operation/日期/分页/条件数组/command，401/402 走 onboarding，5109–5111 不连续请求，其他错误透传原文并建议稍后重试或反馈。
9. **控制后续调用**：空结果、失败、相关匹配或单页结果不能自动触发换词、换路径、换日期、相关词扩展、下一页或另一个 operation；如用户需要继续，先说明新调用可能产生的积分消耗并等待决定。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`：

- **MCP 工具不可用**：检查 `LinkFox` 配置并刷新会话；禁止回退旧 HTTP 网关。
- **401 / authorized error**：这是 WorkBuddy 自动授权上下文异常，提示刷新会话或检查连接；不在参数中补传凭证。
- **402 / 积分余额不足**：引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动查询套餐、创建订单、支付或轮询。处理完成后由用户决定是否重试。
- **403**：表示无权限，不归入 401 或 402；按原始错误说明处理。
- **业务错误**：MCP 成功后再检查下游 `errcode/code` 和消息字段；不因错误、空结果或无数据自动换参数、operation 或分页。
## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
