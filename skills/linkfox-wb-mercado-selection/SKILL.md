---
name: linkfox-wb-mercado-selection
display_name: LinkFox 美客多选品
display_name_en: LinkFox Mercado Libre Product Selection
description: 面向 Mercado Libre（美客多）多站点的商品、关键词、类目、趋势、店铺、评论、汇率与套餐用量查询能力。
description_zh: 面向 Mercado Libre（美客多）墨西哥、巴西、阿根廷、智利及部分哥伦比亚数据场景，通过 Linkfox MCP 完成商品与官链查询、关键词热搜与流量词反查、类目定位、类目趋势、店铺、评论、汇率和套餐用量分析。当用户需要美客多选品、竞品研究、市场趋势或商品数据核验时触发；详细参数、响应和错误处理见 references/。
description_en: Mercado Libre product-selection and market-research capability for Mexico, Brazil, Argentina, Chile, and supported Colombia use cases. It queries products, catalog items, keywords, categories, trends, sellers, reviews, exchange rates, and plan usage through Linkfox MCP. Use it for Mercado Libre sourcing, product research, competitor checks, keyword demand, category analysis, or listing validation; detailed parameters and error handling are in references/.
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


# LinkFox 美客多选品（LinkFox Mercado Libre Product Selection）

为 Mercado Libre（美客多）选品与市场研究提供统一的数据查询能力：可从商品/官链、关键词、类目、趋势、店铺、评论、站点汇率和个人套餐用量等维度取得可审计的原始结果，并按用户目标给出数据对比。当前包含 1 个子能力标识 `linkfox-mercado-product-selection`、1 个精确 MCP `toolName` 和 24 个下游 operation；收费状态以返回的 `charged`/`costToken` 为准。

## 能力边界

### 能力范围

- **商品研究**：使用 `itemInfo` 查询商品基本信息，使用 `itemHistory` 查询销量历史，使用 `itemSearch` 按站点、关键词、类目、价格、销量、评分、评论、重量、上架时间、仓储、店铺类型和排序等条件筛选商品；统一通过 `LinkFox.proxy_call` 调用原 endpoint `/mercado/productSelection`，子能力标识为 `linkfox-mercado-product-selection`。
- **官链/目录研究**：使用 `catalogInfo`、`catalogHistory`、`catalogSearch` 查询官链或目录的基本信息、销量历史和筛选结果；`catalogSearch` 支持关键词、类目、品牌、价格、销量、评分、库存、重量、BSR、仓储、店铺类型、状态、月份和上架天数等条件。
- **关键词研究**：使用 `keywordDateSearch` 获取指定日期热搜词，使用 `keywordMonthSearch` 获取指定月份热搜词，使用 `keywordReverse` 对商品反查流量词；日期格式为 `YYYYMMDD`，月份格式为 `YYYYMM`。
- **类目定位**：使用免费的 `categorySearch` 搜索类目，使用免费的 `categorySmallSearch` 搜索最小子类目；当用户只有类目名称时，先解析 `categoryId`，再调用收费的商品、官链或趋势 operation。
- **类目趋势与机会**：使用 `trendBrandTopBrand`、`trendBrandTopItem`、`trendBrandTopSeller` 查询品牌/商品/店铺排行，使用 `trendNewItems` 分析新品机会，使用 `trendPrice` 查询价格分布，使用 `trendSale` 查询销量分布，使用 `trendSoldHis` 查询销售历史，使用 `trendStatistical` 查询类目汇总统计，使用 `trendStoreInventoryType` 查询仓储类型分布；这些 operation 均要求 `siteId` 与 `categoryId`。
- **店铺与用户反馈**：使用 `sellerSearch` 按站点、店铺类型、等级和优质卖家等级搜索店铺；使用免费的 `reviewSearch` 按 `itemId` 获取商品评论。
- **站点与额度信息**：使用免费的 `rateInfo` 查询站点货币对美元及人民币折算汇率，使用免费的 `myUsage` 查询当前套餐与用量；两个 operation 仍经同一 MCP endpoint 执行。
- **结果留痕**：保留实际 MCP `toolName`、下游 operation、业务参数、查询上下文和响应中的审计字段；旧脚本的本地缓存、自动落盘、会话元数据和 stdout 摘要不属于 MCP 能力。

### 边界与限制

- **调用边界**：只使用 `LinkFox.proxy_call`，精确 `toolName` 为 `mercado/productSelection`；不要直连旧网关或上游 XP-MCP。
- **认证边界**：WorkBuddy 自动注入授权上下文；禁止索取或传入 `headers`、Authorization、API Key、token、JWT、手机号或上游凭证。MCP、401/402 等异常按 `references/onboarding.md` 处理。
- **站点边界**：`MLM` 为墨西哥、`MLB` 为巴西、`MLA` 为阿根廷、`MLC` 为智利；`MCO` 为哥伦比亚，但只在各 operation 参考文档明确支持时使用。`reviewSearch` 只收 `itemId`，不传 `siteId`；`myUsage` 使用空对象参数。
- **收费边界**：`categorySearch`、`categorySmallSearch`、`reviewSearch`、`rateInfo`、`myUsage` 为免费 operation；其他 operation 当前后端通常按每次调用返回 `costToken = 16000`，即使业务结果为空也可能计费。同一任务内相同 MCP `toolName + arguments` 不得重复调用；失败或空结果不得自动换词、翻页或改参数连续试探。
- **参数边界**：原下游请求体必须是 `{"toolName":"<operation>","arguments":{...}}`，整体放入 `proxy_call.arguments`；其中业务 `arguments` 必须为对象，字段名严格使用参考文档的大小写。后端会移除 `uId`、`uid`、`memberId` 并裁剪空值，但不要依赖这些字段完成业务调用。
- **数据边界**：多数 operation 的 `data` 是格式化文本，不能强行假设所有结果都是统一数组；优先阅读 `data`，歧义时读取 `contentText`，只有用户要求诊断时才展示 `rawResponse`。
- **不适用范围**：不提供美客多店铺登录、Listing 发布、订单/库存变更、广告投放、物流履约、供应链采购、平台申诉或法律/财务结论；不把数据查询结果包装成确定的销量保证、盈利保证或平台规则结论。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “查这个美客多商品”“看商品详情” | `itemInfo` | 需要销量变化用 `itemHistory`；需要按条件找一批商品用 `itemSearch` |
| “搜墨西哥站耳机”“筛选竞品” | `itemSearch` | 只有类目名称时先用 `categorySearch`/`categorySmallSearch`；已有商品 ID 时用 `itemInfo` 或 `itemHistory` |
| “查官链/目录链接” | `catalogInfo` | 需要官链销量历史用 `catalogHistory`；需要批量筛选用 `catalogSearch` |
| “查热搜词”“看月度词” | `keywordDateSearch` 或 `keywordMonthSearch` | 有明确日期用按天，有明确月份用按月；要某商品带来的流量词用 `keywordReverse` |
| “看这个商品的流量词” | `keywordReverse` | 必须有 `itemId`；若研究全站需求，改用按天/按月热搜词 |
| “类目趋势”“品牌/商品/店铺排行” | 先 `categorySearch`，再按目标选 `trend*` | 需要新品选 `trendNewItems`，价格选 `trendPrice`，销量分布选 `trendSale`，历史选 `trendSoldHis`，汇总选 `trendStatistical`，仓储选 `trendStoreInventoryType` |
| “找机会类目/看类目规模” | `trendStatistical` 或 `trendNewItems` | 只有类目文本时先调用免费的类目搜索；要价格带或仓储结构时换用对应趋势 operation |
| “查店铺”“看评论” | `sellerSearch` 或免费的 `reviewSearch` | 店铺研究按 `sellerSearch`；已有商品 ID 且要买家反馈按 `reviewSearch` |
| “查汇率”“看套餐还剩多少” | 免费的 `rateInfo` 或 `myUsage` | 汇率必须给 `siteId`；套餐用量的 `arguments` 固定为 `{}` |

选择时先判断用户要单个对象、列表筛选、关键词、类目趋势还是辅助信息，再核对必填字段和站点支持范围。多个 operation 都能回答时，优先选择返回信息最贴合目标且调用次数最少的方案；先用免费类目解析减少付费调用的不确定性。付费调用前明确当前结果可能产生积分消耗，是否继续由用户决定。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 MCP `toolName` |
|---|---|---|---|---|
| `linkfox-mercado-product-selection` | `itemInfo` 商品基本信息（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `itemHistory` 商品销量历史（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `itemSearch` 商品搜索筛选（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `catalogInfo` 官链基本信息（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `catalogHistory` 官链销量历史（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `catalogSearch` 官链搜索筛选（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `keywordDateSearch` 按天热搜词（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `keywordMonthSearch` 月度热搜词（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `keywordReverse` 商品流量词反查（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `categorySearch` 类目搜索（免费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `categorySmallSearch` 最小子类目搜索（免费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendBrandTopBrand` 类目品牌排行（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendBrandTopItem` 类目商品排行（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendBrandTopSeller` 类目店铺排行（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendNewItems` 新品机会（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendPrice` 价格分布趋势（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendSale` 销量分布（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendSoldHis` 销售历史趋势（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendStatistical` 类目汇总统计（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `trendStoreInventoryType` 仓储类型分布（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `sellerSearch` 店铺搜索（收费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `reviewSearch` 商品评论（免费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `rateInfo` 站点汇率（免费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |
| `linkfox-mercado-product-selection` | `myUsage` 套餐与用量（免费） | `references/linkfox-mercado-product-selection.md` | `/mercado/productSelection` | `mercado/productSelection` |

详细必填/可选参数、站点和分页规则集中见 `references/mercado-tool-reference.md`；网关契约和错误码见 `references/api.md`；认证与套餐引导见 `references/onboarding.md`。子能力归档索引见 `references/linkfox-mercado-product-selection.md`。

## MCP 调用方式

- **MCP server**：`LinkFox`；唯一工具：`proxy_call`。
- **精确 endpoint toolName**：`mercado/productSelection`，即原 endpoint `/mercado/productSelection` 去掉前导 `/`；区分大小写，不得用 24 个 operation 名替代。
- **共享代理参数**：`proxy_call.arguments` 必须是原下游请求体，即 `{"toolName":"<operation>","arguments":{...}}`。第一层 `toolName` 是 MCP endpoint，内层 `arguments.toolName` 才是 24 个 operation 之一；业务字段保留在 `arguments.arguments`，不得扁平化或再包裹 `body`/`params`/`data`。
- **自动授权**：WorkBuddy 自动注入授权上下文；MCP 配置和调用参数中禁止增加 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- **返回解析**：先检查 MCP 连接、工具、schema 和 `isError`，再读取 text/structured content；text 是 JSON 字符串时只解析一次。之后检查下游 `errcode`/`errmsg`、`code`/`msg`，最后读取 `data`、`contentText`、`total`、`charged`、`costToken`、`costTime`。
- **去重与错误分层**：同一任务内相同 MCP `toolName + arguments` 只调用一次。收费调用失败、空结果或不理想时不自动重试、换词、翻页或改参数；需要追加调用时先说明潜在消耗并取得用户同意。MCP 不可用时禁止回退旧 HTTP 网关、脚本或其他工具。
- **本地能力变化**：旧脚本的 24 小时缓存、自动响应落盘、会话元数据和 stdout 摘要已移除；不要声称 MCP 自动提供这些能力。展示时直接基于本次 MCP 返回的可见数据，并记录查询上下文。
- **完整参数位置**：`references/api.md` 说明共享 MCP 请求、统一响应和错误码；`references/mercado-tool-reference.md` 记录 24 个 operation 的必填/可选字段、站点、分页、排序和上游协议码；`references/linkfox-mercado-product-selection.md` 为子能力索引；认证与积分异常见 `references/onboarding.md`。
- **反馈**：Feedback API 与工具 endpoint 独立；实际行为与用户意图不符或用户主动反馈时，可按 `references/api.md` 上报简洁且脱敏的内容，不中断业务调用，不上传凭证、隐私、完整大响应或敏感数据。

## 使用示例

以下均为完整 `proxy_call` 参数。执行收费 operation 前先说明可能产生积分消耗；`costToken`、`charged` 与返回业务结果以实际 MCP 下游响应为准。

### 1. 先定位类目（免费）

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}
}
```

用返回的类目 ID 继续调用趋势或商品筛选；需要最细层级时改用 `categorySmallSearch`，必填字段仍为 `siteId`、`searchText`。通常返回 `data` 文本和 `costToken: 0`。

### 2. 商品详情、历史与筛选（收费）

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"itemInfo","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}
}
```

商品历史只需 `itemId`：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"itemHistory","arguments":{"itemId":"MLM4979447466"}}
}
```

按条件筛选时保留 `siteId`，其余过滤字段按需增加：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"itemSearch","arguments":{"siteId":"MLM","title":"Auriculares","priceBegin":200,"priceEnd":1500,"sale30Start":10,"sortKey":"sale30d","sortOrder":"desc","pageNo":1,"pageSize":50}}
}
```

结果可能是格式化文本；不要假设 `data` 必然为统一数组。收费调用即使无匹配结果也可能计费。

### 3. 官链/目录查询（收费）

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"catalogInfo","arguments":{"siteId":"MLB","productId":"MLB21333"}}
}
```

需要批量筛选时使用：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"catalogSearch","arguments":{"siteId":"MLB","searchText":"fones bluetooth","priceVolStart":50,"priceVolEnd":500,"sales30VolStart":10,"sortKey":"sale30d","sortOrder":"desc","pageNo":1,"pageSize":50}}
}
```

`catalogHistory` 使用 `siteId` 与 `productId` 查询官链历史；官链 ID 与普通商品 `itemId` 不要混用。

### 4. 关键词需求与流量词（收费）

按日：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"keywordDateSearch","arguments":{"siteId":"MLM","runDate":"20260601","pageNo":1,"pageSize":50}}
}
```

按月：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"keywordMonthSearch","arguments":{"siteId":"MLB","runMonth":"202606"}}
}
```

已有商品 ID 时反查：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"keywordReverse","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}
}
```

按日/月查询支持筛选、排序和分页；部分关键词 operation 的最大分页深度为 10000，继续翻页前必须评估额外消耗。

### 5. 类目趋势与机会（收费）

先从免费类目查询取得 `categoryId`，再按问题选择一个趋势 operation。例如品牌排行：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"trendBrandTopBrand","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}
}
```

新品和月度销量分布示例：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"trendNewItems","arguments":{"siteId":"MLM","categoryId":"MLM458037"}}
}
```

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"trendSale","arguments":{"siteId":"MLM","categoryId":"MLM458037","month":"202606"}}
}
```

`trendBrandTopItem`、`trendBrandTopSeller`、`trendPrice`、`trendSoldHis`、`trendStatistical` 和 `trendStoreInventoryType` 同样至少需要 `siteId`、`categoryId`；后两者可按参考文档增加 `month`。

### 6. 店铺、评论、汇率与用量（免费/收费）

店铺筛选为收费 operation：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"sellerSearch","arguments":{"siteId":"MCO","sellerType":"LOCAL","levelId":"5_green","pageNo":1,"pageSize":50}}
}
```

商品评论不需要 `siteId`，为免费 operation：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"reviewSearch","arguments":{"itemId":"MLM4979447466","pageNo":1,"pageSize":50}}
}
```

汇率与套餐用量：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"rateInfo","arguments":{"siteId":"MLM"}}
}
```

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {"toolName":"myUsage","arguments":{}}
}
```

`MCO` 只能用于参考文档明确列出的 operation；套餐用量从认证信息识别用户，不要补造用户 ID。

## 展示规则

1. **客观呈现**：优先呈现网关返回的 `data`、`contentText`、`total`、`charged`、`costToken` 和 `costTime`，不要把查询结果扩写成未经支持的销量、盈利或市场结论。
2. **标注上下文**：展示列表或趋势时标注 `toolName`、站点、类目/商品 ID、日期或月份、筛选条件、分页范围及查询时间，便于用户复核。
3. **文本优先解析**：`data` 多数为文本；需要结构化时先判断 `textParsedAsJson`，再按真实返回抽取。大数组或时间序列只展示当前可见切片和必要统计，不虚构不可见的完整结果。
4. **错误与空结果区分**：`code: "200"` 且 `data` 表示“查询不到商品/评论”等，是上游业务无结果，不要称为系统故障；MCP 错误或非 200 `errcode` 才按错误处理。
5. **修正建议**：`errcode: 1002` 时核对内层 operation、业务参数对象、必填字段、字段大小写、站点和日期格式；`errcode: 500` 时记录脱敏信息，不自动重试收费调用。
6. **费用透明**：付费结果显示网关返回的 `charged` 和 `costToken`，提醒用户收费 operation 按调用计费，空结果不代表免扣；免费 operation 不应标成收费。
7. **敏感信息保护**：不展示 API Key、上游密钥、JWT、手机号、内部认证响应或完整敏感 raw payload；用户要原始诊断时也只提供必要且脱敏的字段。
8. **反馈上报**：发生明确的体验偏差、表扬、不满或可复现改进点时，按 `references/api.md` 的 Feedback API 使用 `skillName`、情绪、分类和简洁内容上报；不打断当前任务，不带隐私和凭证。

## 解决认证和积分问题

发生以下异常情况时，读取 `references/onboarding.md` 并按其中流程处理，不自行猜测或索要凭证。

### 异常情况

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提示检查 `LinkFox` 配置并重载 WorkBuddy；禁止 HTTP fallback。
- **401 / authorized error**：按 WorkBuddy 自动授权链路异常处理，提示重新登录或重载连接；不得索取或补传 Key。不要把 401 当成积分不足。
- **402 / 积分或余额不足**：消息含“积分余额不足”“计费不足”“余额不足”“quota exceeded”“insufficient balance”“套餐到期”“需充值”“请充值”等含义时，读取套餐清单并让用户选择，不自动购买。
- **403**：这是权限问题，不归入认证或 billing 引导；依据返回信息处理，不传认证字段。

### 引导规则

MCP 或授权异常只提示用户重新登录、重载连接或联系 WorkBuddy 管理员。积分不足时引导访问 `https://agent.linkfox.com/` 自助处理；不得自动查询套餐、选择套餐、创建支付订单、支付或轮询。处理完成后是否重新发起业务调用由用户决定。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
