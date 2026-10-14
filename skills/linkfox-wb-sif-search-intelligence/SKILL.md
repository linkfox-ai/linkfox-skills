---
name: linkfox-wb-sif-search-intelligence
display_name: LinkFox SIF亚马逊情报分析
display_name_en: LinkFox SIF Amazon Intelligence Analysis
description: 面向亚马逊商品与关键词的 SIF 搜索情报分析能力，识别市场竞争、流量来源、曝光结构、关键词排名与转化表现。
description_zh: 面向亚马逊选品、竞品研究和运营诊断的统一 SIF 搜索情报分析能力。当用户需要评估关键词竞争度与供需关系、拆解关键词下竞品 ASIN 的自然/广告/推荐流量、分析一个或多个 ASIN 的全渠道曝光结构，或反查 ASIN 的流量关键词、排名、搜索量、点击集中度与点击购买转化时触发。支持 US、UK、DE、CA、JP、FR、ES、IT、MX、AU、AE、BR、SA 站点；完整参数、响应字段及 MCP 契约见 references/。
description_en: Unified SIF search-intelligence analysis for Amazon product research, competitor research, and operations diagnosis through Linkfox MCP. Supports keyword competition, traffic-source breakdowns, ASIN exposure structure, and reverse-ASIN keyword analysis across 13 marketplaces. Full parameters, response fields, and MCP contracts are in references/.
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


# LinkFox SIF亚马逊情报分析（LinkFox SIF Amazon Intelligence Analysis）

面向亚马逊选品、竞品研究与运营诊断，使用 SIF 数据回答“这个词有多难”“这个词下谁在获取流量”“这个 ASIN 的曝光来自哪里”“这个 ASIN 依靠哪些关键词排名”等问题。能力覆盖 4 个子能力和 4 个精确 endpoint toolName，均通过 `LinkFox.proxy_call` 调用。

## 能力边界

### 能力范围

- **关键词市场概览**（`linkfox-sif-keyword-overview`）：调用 `POST /sif/keywordOverview`，在单个关键词、指定站点和数据周期下返回搜索热度排名、预估周搜索量、供需比、自然/广告/推荐商品数量、SIF 跟踪 ASIN 数量及数据更新时间；适合先做市场竞争度和供需快照。
- **关键词下的竞品流量结构**（`linkfox-sif-keyword-summary`）：调用 `POST /sif/keywordSummary`，返回某个关键词下 ASIN 的关键词级与商品级曝光得分/占比，覆盖自然搜索、SP、品牌广告、视频广告、AC、ER、TR 和推荐位广告/非广告；支持 ASIN 过滤、单条件筛选、排序、分页和自定义日期区间。
- **ASIN 全局流量与曝光结构**（`linkfox-sif-asin-summary`）：调用 `POST /sif/asinSummary`，针对 1–10 个 ASIN 返回全关键词范围的商品元数据、各流量渠道曝光分数/占比、关键词数量、上期值以及本期新进/退出数量；适合单品诊断和批量竞品横向比较。
- **ASIN 反查流量关键词**（`linkfox-sif-asin-keywords`）：调用 `POST /sif/asinKeywords`，针对单个 ASIN 返回带来自然排名、SP 广告排名、周搜索量、关键词热度、流量份额、自然/付费得分、TOP3 点击集中度、点击购买转化率和标记的关键词明细；支持最近 7/30 天、月、周、条件筛选、排序和分页。
- **站点与周期分析**：四类查询均支持 13 个站点代码 `US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA`，未指定时默认 `US`；关键词应尽量使用目标站点语言。关键词概览、关键词流量来源和 ASIN 汇总默认最近 7 天/最新整周，ASIN 关键词另支持 `latelyDay`、`month`、`week`。
- **可审计执行**：记录实际 `toolName`、`arguments`、站点、周期及响应中的成本/时间字段；相同调用不重复执行。

### 边界与限制

- **输入粒度不同**：`keywordOverview` 与 `keywordSummary` 每次处理一个关键词；`asinKeywords` 每次只能处理一个 ASIN；`asinSummary` 一次最多 10 个 ASIN。多关键词或多 ASIN 需求应拆分调用并在结果中标注各自站点和周期。
- **筛选限制**：`keywordSummary.condition` 每次只能传一个值；`asinSummary.conditions` 可传逗号分隔的渠道条件；ASIN 关键词的 `conditions` 才支持多个标志/周期计数条件。不要把三者的筛选名混用。
- **分页与窗口限制**：`keywordSummary` 与 `asinKeywords` 每页最多 100 条；`asinSummary` 每页最多 10000 条；`asinKeywords.timePieceType=latelyDay` 仅支持 `7` 或 `30`，月值为 `YYYY-MM`，周值为周起始日期；关键词概览不提供分页。
- **数据口径限制**：曝光 score 是相对可见度指标，不是销量、订单、销售额或真实流量；关键词流量来源中无前缀字段是 ASIN 全局指标，`keyword*` 字段只表示当前关键词。`clickConcentrationShare` 是 ABA TOP3 点击集中度，不是转化率；转化率使用 `clickToPurchaseConversionRate`。
- **时间与新进/退出口径**：`*Prev`、`*In`、`*Out` 只在有对应周期字段的 API 中表示当前窗口与上一窗口的关系；展示时必须写明默认周期或用户指定的 `startDate ~ endDate`、月/周窗口，不能脱离周期比较数字。
- **认证和计费**：WorkBuddy 自动注入授权，禁止传入任何凭证。查询会消耗积分；同一任务相同 `toolName + arguments` 只调用一次。失败或空结果不得自动改关键词、换站点、改参数或连续翻页试探。
- **不适用范围**：不提供长期历史曲线、销售/收入估算、评论分析、Listing 文案优化、广告竞价/预算管理、订单库存管理、物流供应链或平台操作。需要多周趋势、点击/转化份额等超出当前窗口的指标时，应明确说明当前数据不足，不把快照推断为趋势。

### 指标口径速查

- `keywordOverview` 的 `supplyDemandRatio` 按搜索结果商品数/月搜索量计算，数值越低代表相对竞争越小；`keywordPopularityRank` 数值越小代表搜索热度越高。两个指标都要和返回的 ABA 周期一起展示。
- `keywordSummary` 既有 ASIN 跨所有关键词的商品级 exposure 字段，也有仅针对查询词的 `keyword*` exposure 字段；用户问“这个词”时优先使用后者，不要把全局值当成词内值。
- `asinSummary` 的 `totalExposureScore`、各渠道 exposure score 和 ratio 描述 ASIN 全关键词可见度；`*Prev` 是上一周期，`*In`/`*Out` 是本周期相对上一周期新进/退出的关键词数量。
- `asinKeywords` 的 `trafficShare` 是该词对 ASIN 总关键词流量的份额；`naturalTrafficShare` 与 `paidTrafficShare` 是得分占比；`clickConcentrationShare` 观察关键词下头部 ASIN 点击集中度，不能替代 `clickToPurchaseConversionRate`。
- 所有 exposure score 都是可见度综合评分，不可直接换算成曝光次数、点击数、订单数或销售额；缺少字段时应保留 N/A，不用其他端点的近似字段填充。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “这个关键词竞争大吗”“供需比、商品数、搜索热度是多少” | `linkfox-sif-keyword-overview` | 想知道具体哪些 ASIN 获取自然/广告/推荐流量时换 `linkfox-sif-keyword-summary`；想研究某 ASIN 的关键词时换 `linkfox-sif-asin-keywords` |
| “这个词下面哪些竞品在抢 SP/品牌/视频流量”“看这个词的流量结构” | `linkfox-sif-keyword-summary` | 只要市场级数量和供需快照用 `linkfox-sif-keyword-overview`；要某 ASIN 跨全部关键词的总结构用 `linkfox-sif-asin-summary` |
| “这个 ASIN 的自然和付费流量占比”“和几个竞品比较曝光结构” | `linkfox-sif-asin-summary` | 只查一个关键词下的对比用 `linkfox-sif-keyword-summary`；要逐关键词排名、搜索量、转化表现用 `linkfox-sif-asin-keywords` |
| “这个 ASIN 排了哪些词”“自然排名/广告排名/高转化词/搜索量上涨词” | `linkfox-sif-asin-keywords` | 要渠道汇总、上期值、新进/退出数量或最多 10 个 ASIN 批量比较用 `linkfox-sif-asin-summary` |
| “在不同站点/日期区间比较” | 选择与指标粒度匹配的上述端点，分别调用 | 不要用一个端点替代另一端点；关键词概览和关键词流量来源都按单关键词调用，ASIN 关键词按单 ASIN 调用；追加调用前提示积分消耗 |

选择思路：先判断问题的主键是“关键词”还是“ASIN”，再判断要“市场总量”“某关键词下的 ASIN 分布”“ASIN 全局渠道汇总”还是“ASIN 的逐关键词明细”。需要同时回答多个层次时，先调用最能直接回答主问题的端点，再由用户决定是否追加其他层次；满足程度相同则使用上表默认推荐。字段级差异、完整条件值与响应结构以 reference 为准。

### 参数决策

- 未指定站点时使用 `US`；已指定站点时保留用户意图并把关键词尽量转换为当地语言。可比较多个站点，但每个站点必须单独记录请求和更新时间。
- 未指定时间时，关键词概览、关键词流量来源和 ASIN 汇总使用默认最近 7 天；需要完整 ABA 周时按端点使用 `last7d=false` 加 `startDate`/`endDate`。ASIN 关键词的最近窗口使用 `latelyDay=7`，查询月或周时改用 `month`/`week` 及对应格式。
- 需要筛选“自然/广告/转化/新进”关键词时，只有 `asinKeywords.conditions` 支持并列条件；`keywordSummary.condition` 必须单选；`asinSummary.conditions` 才使用其渠道值 `nf`、`sp`、`sb`、`sbv`、`ad`、`acAd` 或 `totalPeriod.in`。
- 需要查市场总量时不要为了获取 ASIN 明细而重复调用概览；需要具体竞品时直接使用 `keywordSummary`。需要跨关键词的单品结构时直接使用 `asinSummary`，不要从单个关键词的若干行外推全局结构。
- 结果超过一页时先展示第一页摘要和 `total`，得到用户确认后再调整 `pageNum`；`keywordSummary`/`asinKeywords` 的 `pageSize` 上限是 100，`asinSummary` 的上限是 10000。

## 业务需求路由速查

表头固定为：`子能力 / 业务能力 / reference / 原 endpoint / toolName`。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-sif-keyword-overview` | 单关键词竞争度、供需比、搜索结果和广告/推荐数量概览 | [references/linkfox-sif-keyword-overview.md](references/linkfox-sif-keyword-overview.md) | `/sif/keywordOverview` | `sif/keywordOverview` |
| `linkfox-sif-keyword-summary` | 单关键词下 ASIN 的关键词级/商品级流量来源与曝光结构 | [references/linkfox-sif-keyword-summary.md](references/linkfox-sif-keyword-summary.md) | `/sif/keywordSummary` | `sif/keywordSummary` |
| `linkfox-sif-asin-summary` | 1–10 个 ASIN 的全关键词渠道曝光、关键词数量及周期对比 | [references/linkfox-sif-asin-summary.md](references/linkfox-sif-asin-summary.md) | `/sif/asinSummary` | `sif/asinSummary` |
| `linkfox-sif-asin-keywords` | 单 ASIN 反查流量关键词、排名、搜索量、份额、点击集中度和转化 | [references/linkfox-sif-asin-keywords.md](references/linkfox-sif-asin-keywords.md) | `/sif/asinKeywords` | `sif/asinKeywords` |

认证与积分引导统一使用 [references/onboarding.md](references/onboarding.md)。本 skill 没有本地 helper。

### Reference 定位

- `references/linkfox-sif-keyword-overview.md` 归档关键词概览的完整请求字段、竞争指标、单条响应字段、错误码和 MCP 示例。
- `references/linkfox-sif-keyword-summary.md` 归档关键词下 ASIN 流量来源的条件值、排序值、两类 exposure 字段、缺失字段说明和分页示例。
- `references/linkfox-sif-asin-summary.md` 归档 ASIN 批量汇总的渠道字段、周期字段、最多 10 个 ASIN 的请求限制和比较示例。
- `references/linkfox-sif-asin-keywords.md` 归档 ASIN 反查的完整条件 marker、时间片段、排名/转化字段、分页与多 ASIN拆分规则。
- 每个 reference 同时保留对应业务的功能说明、边界、调用方式、展示规则、错误处理、完整 API 和认证引导；遇到字段歧义时以该文件的 API 表为准。

## MCP 调用方式

- 只使用 `LinkFox.proxy_call`；`toolName` 必须是路由表中的精确值，区分大小写且不带前导 `/`。
- 对应 reference 的原请求对象直接放入 `arguments`，不增加 `body`、`params`、`data` 或第二层 `arguments`。
- WorkBuddy 自动注入授权上下文；禁止在参数中传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- text JSON 只解析一次。先检查 MCP 连接、工具、schema 和 `isError`，再检查下游 `code`/`errcode` 与 `msg`/`errmsg`。
- MCP 不可用时禁止回退旧 HTTP 网关、脚本或其他工具。失败或空结果不得自动更换参数；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先固定站点、语言、时间窗口和必要筛选，再选择排序与分页；追加站点、关键词、ASIN 或分页前提示额外积分消耗并取得同意。
- 旧脚本的 24 小时缓存、自动落盘、会话索引和 stdout 摘要不属于 MCP 能力，迁移后不再承诺。

## 使用示例

### 1. 关键词竞争度快照

请求“分析 Amazon US 的 wireless charger 竞争度、供需关系与广告数量”时，使用 `keywordOverview`：

```json
{"keyword":"wireless charger","country":"US","last7d":true}
```

调用 `proxy_call`，使用 `toolName="sif/keywordOverview"` 和上面的业务参数。

重点展示 `supplyDemandRatio`、`keywordPopularityRank`、`estimatedWeeklySearchVolume`、`totalSearchResultProductCount`、SP/品牌/视频广告数量和 `dataPeriodStartDate ~ dataPeriodEndDate`；热度排名数值越小代表越热门。该端点通常每个关键词只返回一条记录，不直接列出竞品 ASIN；需要竞品明细时另行调用关键词流量来源端点。

### 2. 单关键词下的竞品流量结构

请求“查看 wireless charger 下哪些 ASIN 有 SP 广告，并按整体 SP 曝光排序”时，使用 `keywordSummary`：

```json
{"searchKeyword":"wireless charger","country":"US","condition":"isSpAd","sortBy":"totalSpSocre","desc":true,"pageNum":1,"pageSize":100}
```

重点展示 ASIN、标题、`keywordNaturalExposureScore`、`keywordSponsoredProductsExposureScore`、`keywordRecommendAdExposureScore`、各占比和 `dataPeriodStartDate`。`condition` 每次只能有一个值；无前缀的 exposure 字段是该 ASIN 跨关键词的商品级指标，`keyword*` 字段才是当前关键词指标。结果超过一页时报告 `total` 并建议用户决定是否继续翻页。

### 3. 多 ASIN 全局曝光比较

请求“比较两个竞品在 US 的自然、SP、品牌、视频及推荐位流量，并看上期变化”时，使用 `asinSummary`：

```json
{"searchValue":"B09V3KXJPB,B0BN1K7WJP","country":"US","last7d":true,"sortBy":"totalSpSocre","desc":true,"pageNum":1,"pageSize":10000}
```

重点展示 `totalExposureScore`、各渠道 exposure ratio、各类关键词数量，以及 `*Prev`、`*In`、`*Out` 字段；横向表格中明确写出当前窗口与上一窗口的含义。单次最多 10 个 ASIN，曝光分数适合相对比较，不应解释成销量或收入。

### 4. 单 ASIN 反查关键词

请求“找出 B0XXXXXXXX 在 US 的自然流量词和高转化长尾词，并按自然排名升序”时，使用 `asinKeywords`：

```json
{"asin":"B0XXXXXXXX","country":"US","conditions":"nfPosition,isAccurateTailKw,isPurchaseKw","sortBy":"lastRank","desc":false,"timePieceType":"latelyDay","timePieceValue":"7","pageNum":1,"pageSize":100}
```

重点展示 `keyword`、`productNaturalRank`、`productAdRank`、`weeklySearchVolume`、`trafficShare`、`naturalTrafficShare`、`paidTrafficShare`、`clickConcentrationShare` 和 `clickToPurchaseConversionRate`，并翻译标记数组和展示位置数组。排名数字越小位置越好；`clickConcentrationShare` 不能当作转化率。单次只能查一个 ASIN，每页最多 100 条。

### 5. 指定周期与站点的拆分调用

请求“比较 bluetooth speaker 在 US、UK、DE 的竞争”时，对每个站点分别调用 `keywordOverview`，并将关键词翻译为站点语言：

```json
[
  {"keyword":"bluetooth speaker","country":"US","last7d":true},
  {"keyword":"bluetooth speaker","country":"UK","last7d":true},
  {"keyword":"Bluetooth Lautsprecher","country":"DE","last7d":true}
]
```

多个调用会分别产生查询消耗，结果必须逐站点标注数据周期和更新时间。若用户只要某个关键词下的竞品 ASIN 流量分布，应改用 `keywordSummary`；若要单个 ASIN 的跨关键词结构，应改用 `asinSummary`。

## 展示规则

1. **先说明查询口径**：每次结果开头标注站点、请求关键词或 ASIN、请求时间窗口、实际 `dataPeriodStartDate`/`dataPeriodEndDate`（或 `periodEndDate`/`abaCreateDateWeek`）和数据更新时间。
2. **按问题组织表格**：关键词概览按市场指标展示；关键词流量来源按 ASIN 行、自然/付费/推荐渠道分组；ASIN 汇总分开商品元数据、当前周期 exposure、关键词数量和周期对比；ASIN 关键词按关键词行展示排名、搜索量、份额、得分和标记。
3. **区分字段范围**：关键词流量来源中的无前缀字段表示 ASIN 所有关键词的商品级指标，`keyword*` 字段表示当前查询关键词；用户问当前关键词时优先展示 `keyword*`，禁止用同名不同口径字段替代。
4. **格式化比例**：将 `trafficShare`、`naturalTrafficShare`、`paidTrafficShare`、各种 `ExposureRatio`、`recommend*Ratio` 和 `clickConcentrationShare` 从小数格式化为百分比，并在表头保留指标名称；曝光 score 保留原始数值并注明它是相对得分。
5. **解释排名与点击指标**：自然排名/广告排名及关键词热度排名均应提醒数值越小表示位置更高或热度更高；明确写出 `clickConcentrationShare` 是 ABA TOP3 点击集中度，`clickToPurchaseConversionRate` 才是点击到购买转化率。
6. **翻译枚举标记**：将 `displayPositionTypes` 的 `natural/ac/sp/top/bottom/er/vedio/tr/trfob` 翻译为自然位/Amazon's Choice/SP 广告/顶部品牌广告/底部品牌广告/编辑推荐/视频广告/Top Rated/Top Rated Frequently Bought；将流量和转化 marker 翻译为用户可读标签。
7. **突出但不臆测关键指标**：关键词概览突出供需比、热度排名、总商品数；关键词流量来源突出自然与付费占比及单 ASIN 渠道结构；ASIN 汇总突出全局渠道占比和 In/Out/Prev；ASIN 关键词突出排名、搜索量、份额及转化字段。不要基于这些快照擅自给出销量、收入或法律结论。
8. **处理空值和分页**：接口以 `0`、`-1` 或空值表示不可用时标注 N/A 或省略，不能把不可用当作真实零值；有更多页时说明 `total`/当前页并建议下一页，不能自动连续翻页。
9. **客观呈现来源**：标注数据来自 SIF 的关键词概览、关键词流量来源、ASIN 汇总或 ASIN 关键词端点；多个端点并用时逐项注明端点、参数和周期。用户未要求建议时只呈现数据与口径。
10. **错误与修正建议**：失败时同时检查 HTTP/网关 `errcode`、业务 `code` 和 `msg`/`errmsg`；根据错误建议检查 API Key、ASIN/关键词格式、站点代码、日期格式、条件单选、分页上限或关键词语言。遇到空结果先说明可能是站点无数据或关键词未被跟踪，不要自动改参数。
11. **多对象布局**：多个 ASIN 使用并列对比表，多个站点或关键词使用相同字段的分组表；`asinSummary` 允许一次最多 10 个，`asinKeywords` 多 ASIN 必须分开调用并汇总时保持每个 ASIN 的边界。

## 解决认证和积分问题

发生以下异常情况时读取 `references/onboarding.md`：

### 异常情况

- **MCP 工具不可用**：检查 `LinkFox` 配置并刷新会话，禁止 HTTP fallback。
- **响应 401**：包括 `errcode=401`、`authorized error`、鉴权失败或未授权；提示刷新会话或检查 Linkfox 连接，不补传凭证。
- **响应 402 或余额不足**：包括 `errcode=402`、消息中的积分余额不足、计费不足、余额不足、`quota exceeded`、`insufficient balance`、套餐到期或需充值；引导用户自助处理。

### 引导动作

- WorkBuddy 自动授权，不索取、展示或配置 API Key、token、JWT 或手机号。
- 余额不足时引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动查询套餐、下单、支付或轮询。
- **其他状态**：`errcode=403` 属于无权限，不归入认证或余额问题；原样说明错误并停止无授权的重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
