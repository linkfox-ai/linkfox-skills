---
name: linkfox-wb-amazon-front-data
display_name: LinkFox 亚马逊前台数据
display_name_en: LinkFox Amazon Front Data
description: 面向亚马逊前台的实时商品、搜索、评论、视觉相似和 Alexa 导购数据能力。
description_zh: 面向亚马逊前台实时数据获取与分析，支持按关键词查看搜索结果与排位、按 ASIN 获取商品详情、按星级与条件读取评论、按公开图片查找视觉相似商品，以及通过 Alexa 购物助手进行自然语言导购问答。当用户需要亚马逊前台快照、竞品研究、Listing 数据、买家反馈、图片找同款或对话式商品推荐时触发；输出结构化结果、链接、图片和可追溯的原始响应。该能力不提供历史搜索量、广告投放、库存管理或法律结论。
description_en: Real-time Amazon storefront data retrieval and analysis for search SERPs, ASIN product details, filtered customer reviews, visual product discovery from public image URLs, and Alexa conversational shopping answers. Use it for Amazon storefront snapshots, competitor research, listing data, customer feedback, image-based lookalike discovery, or conversational product recommendations. It returns structured results, links, images, and traceable raw responses, but does not provide historical search analytics, advertising management, inventory operations, or legal conclusions.
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


# LinkFox 亚马逊前台数据（LinkFox Amazon Front Data）

本能力用于完成亚马逊前台的实时数据工作：从搜索结果页发现商品和排位，从 ASIN 页面读取 Listing 详情，从评论中提取买家反馈，从公开图片发现视觉相似商品，或让 Alexa 购物助手回答自然语言购物问题。结果可包含商品标题、ASIN、价格、币种、评分、评论数、图片、链接、配送、赞助标记、评论文本、变体、Keepa 补充字段、Alexa 回答和追问建议。

本能力覆盖 5 个子能力和 5 个下游工具路由。所有业务查询都通过 Linkfox MCP 唯一工具 `proxy_call` 调用；本地脚本只保留预签名 URL 的 OSS 文件 PUT 辅助。每个子能力的完整参数、响应字段、错误码、成本和特殊规则见 `references/`。

## 能力边界

### 能力范围

- **关键词搜索与前台排位**：使用 `proxy_call` 路由到 `amazon/search` 模拟指定站点的前台搜索，返回关键词、页码、位置、ASIN、标题、价格、评分、评论数、品牌、配送、FBA、赞助标记和上架信息。适用于竞品发现、SERP 快照、价格比较、赞助商品识别和指定 ASIN 排位核对。
- **ASIN 商品详情**：使用 `proxy_call` 路由到 `amazon/product/detail` 获取最多 40 个 ASIN 的当前商品页数据，包括标题、图片、五点、规格、描述、A+ 内容、价格、优惠、评分分布、Prime、库存、配送、变体，以及按需返回的经常一起购买、相关商品和作者评论。
- **评论读取与反馈分析**：使用 `proxy_call` 路由到 `amazon/reviews/list` 按单个 ASIN、星级、排序、关键词、认证购买和媒体条件读取评论，支持按 1—5 星分别设定数量，并据此整理常见痛点和受好评特征。
- **图片找相似商品**：使用 `proxy_call` 路由到 `amazon/searchByImage` 对可公开访问的图片 URL 进行视觉商品搜索，支持 8 个站点、价格/评分/评论数排序、站内或跨境配送，以及可选的 Keepa 销售排名、月销量、FBA 费用和规格字段。本地图片先用 `proxy_call` 路由到 `oss/file/presignedPut` 取得预签名 URL，再使用 `scripts/upload_image.py` 上传。
- **Alexa 对话式导购**：使用 `proxy_call` 路由到 `amazon/alexaSearch` 发送一条自然语言购物问题，获得 Alexa 回答、分组商品推荐、ASIN、商品链接、价格、评分和可继续追问的问题；可用具体的分类页、搜索结果页或商品详情页 URL 提供页面上下文。
- **可追溯与去重**：保留本次 `toolName`、`arguments`、MCP 返回和下游响应中的 `taskId`/`costToken` 等追踪字段。不声称 MCP 会自动落盘或提供 24 小时本地缓存；同一任务内不得以完全相同的 `toolName + arguments` 重复发起收费调用。

### 边界与限制

- **实时快照而非历史分析**：搜索、商品详情和评论反映调用时的前台数据；不等同于历史搜索量、关键词趋势、历史排名、历史价格或销量预测。
- **站点与输入限制**：搜索和详情使用 `amazonDomain`，评论使用 `domainCode`；各自支持范围见对应 reference。图片搜索必须使用可公开访问的图片 URL，印度站不支持 `countryOrAreaCode`；不可用本地路径直接查询。
- **单请求限制**：评论接口一次只支持一个 ASIN，多个 ASIN 必须分开调用；Alexa 每次只能传一个 `prompts` 元素，跨轮追问必须由 Agent 总结上一轮后重新发起调用；详情一次最多 40 个 ASIN；评论每个星级最多 100 条。
- **参数约束**：图片搜索的 `deliveryZip` 与 `countryOrAreaCode` 不能同时传；图片搜索的排序值仅限其 reference 列出的 7 种；搜索排序值仅限其 reference 列出的 6 种；Alexa 的 `url` 只用于具体页面，不要传普通亚马逊首页。
- **图片与评论语义**：图片搜索是视觉相似商品发现，不是文字关键词搜索；评论返回原始发布语言，评论分析应标注这是从返回文本归纳的主题，不应伪装成供应商字段。
- **数据能力边界**：不提供 ABA 历史搜索词分析、广告创建或竞价、店铺订单/库存、FBA 财务核算、Listing 文案创作、图片编辑、销售额预测、数据库 SQL 二次处理或侵权法律结论。
- **认证与消耗**：Authorization 由 WorkBuddy 自动注入，不放入 MCP 配置或业务参数。业务调用可能消耗积分；失败或空结果不得自动重试，也不得自动换词、换图、翻页、换邮编或改参数连续试探；需要继续调用时先说明额外消耗并由用户决定。
- **数据缺失**：字段为空、`0` 或 `-1` 可能表示供应商没有提供该值；不得把不可用字段当成真实价格、尺寸、销量或排名。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “搜这个关键词现在在亚马逊显示什么”“我的 ASIN 排第几” | `linkfox-amazon-search` | 只知道 ASIN 且要完整 Listing 用 `linkfox-amazon-product-detail`；要历史词量或趋势不在本能力范围 |
| “查这个 ASIN 的标题、五点、价格、变体、A+” | `linkfox-amazon-product-detail` | 只要买家反馈或星级筛选用 `linkfox-amazon-reviews-list`；只要搜索页排位用 `linkfox-amazon-search` |
| “看看差评在抱怨什么”“只要已验证购买的 1 星评论” | `linkfox-amazon-reviews-list` | 需要当前评分分布、详情页五点或变体时换用 `linkfox-amazon-product-detail` |
| “用图片找同款/相似商品”“找更便宜的视觉替代品” | `linkfox-amazon-search-by-image` | 没有图片而有关键词用 `linkfox-amazon-search`；需要已知 ASIN 的完整页面用 `linkfox-amazon-product-detail` |
| “让亚马逊帮我推荐”“在这个页面继续问 Alexa” | `linkfox-amazon-alexa-search` | 需要扁平 SERP、位置、赞助标记或可批量比较时用 `linkfox-amazon-search`；需要确定 ASIN 页面字段时用 `linkfox-amazon-product-detail` |
| 用户给出本地图片路径 | 先用 `proxy_call` + `oss/file/presignedPut` 取预签名 URL，再运行 `scripts/upload_image.py`，最后用 `amazon/searchByImage` | 若用户仅要编辑图片、生成图片或做非亚马逊图片处理，不适用本能力 |
| 需要视觉结果的 Keepa 补充数据 | `linkfox-amazon-search-by-image`，设置 `aggregateByKeepaData: true` | 只需要前台价格/排位时关闭 Keepa；需要评论或 Listing 内容时分别选择评论或详情接口 |

选择时先判断用户要的是“搜索页列表”“已知 ASIN 页面”“评论文本”“图片相似结果”还是“自然语言回答”，再核对站点、输入形态、分页/批量限制和预计消耗。相近需求同时满足时，默认推荐上表工具，并把需要改用其他工具的原因和额外调用成本讲清楚，由用户决定是否继续。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | `proxy_call.toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-amazon-search` | 关键词前台搜索、排位与 SERP 商品数据 | `references/linkfox-amazon-search.md` | `amazon/search` | 无 |
| `linkfox-amazon-product-detail` | ASIN 商品详情、Listing、变体及可选关联商品 | `references/linkfox-amazon-product-detail.md` | `amazon/product/detail` | 无 |
| `linkfox-amazon-reviews-list` | 按星级/关键词/认证/媒体筛选评论 | `references/linkfox-amazon-reviews-list.md` | `amazon/reviews/list` | 无 |
| `linkfox-amazon-search-by-image` | 公开图片视觉搜索、配送和可选 Keepa 补充 | `references/linkfox-amazon-search-by-image.md` | `amazon/searchByImage` | 无 |
| `linkfox-amazon-search-by-image` | 本地图片上传为公开图片 URL（前置辅助） | `references/linkfox-amazon-search-by-image.md` | `oss/file/presignedPut` | `scripts/upload_image.py` 仅 PUT 预签名 URL |
| `linkfox-amazon-alexa-search` | Alexa 自然语言导购、商品分组和追问 | `references/linkfox-amazon-alexa-search.md` | `amazon/alexaSearch` | 无 |

## MCP 调用方式

- **唯一调用入口**：MCP server 名为 `LinkFox`，地址为 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，唯一工具为 `proxy_call`。外层必须同时传当前 allowlist 中的精确 `toolName` 与 `arguments`；`arguments` 始终是 JSON 对象，即使下游工具无业务参数也必须传 `{}`。不要再包裹 `body`、`params` 或 `data`。
- **严格 allowlist**：`toolName` 只允许 `amazon/search`、`amazon/product/detail`、`amazon/reviews/list`、`amazon/searchByImage`、`amazon/alexaSearch`、`oss/file/presignedPut`。值为原网关 endpoint 去掉前导 `/` 后的精确字符串，区分大小写；不得猜测、转换为 snake_case 或用 skill slug 代替。
- **禁止直连和回退**：不得使用 curl、`urllib`、`requests` 或其他 HTTP 客户端直连 `tool-gateway.linkfox.com`，不得静默回退到旧 API 或查询脚本。MCP 或 `proxy_call` 不存在时，立即停止业务调用并读取 `references/onboarding.md`。
- **错误分层**：先检查 MCP 传输/工具层是否失败（包括 `isError=true`、工具不存在、参数 schema 错误和代理调用失败）；只有代理层成功后才解析下游 JSON 的 `errcode`/`errorCode`/`code`、`errmsg`/`msg`。`proxy_call` 若返回 text 形式的 JSON，只解析一次；不循环解码字符串化 JSON。
- **不自动重试**：所有业务路由都可能收费。MCP 错误、下游错误或空结果都不得触发自动重试；同一任务内对完全相同的 `toolName + arguments` 只调用一次。若需改参数或再试，先说明可能的额外消耗并由用户决定。
- **本地图片两阶段流程**：本地路径不可直接作为 `imageUrl`。先调用 `proxy_call`，传 `{"toolName":"oss/file/presignedPut","arguments":{"contentType":"<MIME>","fileExtension":"<ext>"}}`；再将下游返回的预签名 URL 与本地路径交给 `scripts/upload_image.py` 执行 OSS PUT。检查其输出的公开 `url` 后作为 `amazon/searchByImage` 的 `imageUrl`。公开 URL 有效期为 24 小时，支持 jpg、jpeg、png、gif、webp、heic。
- **响应追溯**：保留当次 `toolName`、完整 `arguments`、代理错误与下游返回中的总数、失败明细、`costToken`、`taskId` 等字段。不声称会自动保存原始响应或命中 24 小时本地缓存；向用户输出结论和必要证据，不直接倾倒大段原始 JSON。
- **完整参数位置**：参数、默认值、站点/排序枚举、响应字段、错误码、成本和反馈接口分别见 `references/linkfox-amazon-product-detail.md`、`references/linkfox-amazon-reviews-list.md`、`references/linkfox-amazon-search.md`、`references/linkfox-amazon-search-by-image.md`、`references/linkfox-amazon-alexa-search.md`。MCP 安装、WorkBuddy 自动授权异常和 402 分流见 `references/onboarding.md`。
- **反馈**：当能力与用户意图不匹配、结果错误、用户明确表扬/不满或提出改进意见时，按相应 reference 中的 Feedback API 规则上报；反馈接口 `https://skill-api.linkfox.com/api/v1/public/feedback` 与 MCP 业务路由分离，不要混用，且不要中断用户当前流程。

## 使用示例

以下示例均是传入 `proxy_call.arguments` 的业务参数对象；应与路由表中的 `toolName` 组合调用。真实调用前确认目标站点、输入约束和积分消耗；不要因结果为空自动扩大范围。

### 1. 关键词前台搜索

```json
{
  "keyword": "wireless earbuds",
  "amazonDomain": "amazon.com",
  "language": "en_US",
  "sort": "review-rank",
  "page": 1,
  "deliveryZip": "10001",
  "device": "desktop"
}
```

读取 `products[]` 的 `position`、`asin`、`title`、`price`、`currency`、`rating`、`ratings`、`brand`、`sponsored` 和 `asinUrl`，并报告 `total`、`keyword`、`costToken`。`page` 从 1 开始，每页约 20 条；这是调用时的前台排位，不是历史排名。排序只能使用 reference 中的支持值。

### 2. ASIN 商品详情

```json
{
  "asins": "B072MQ5BRX,B08N5WRWNW",
  "amazonDomain": "amazon.co.jp",
  "language": "ja_JP",
  "deliveryZip": "100-0001",
  "device": "mobile",
  "returnBoughtTogether": true,
  "returnRelatedProducts": true,
  "returnAuthorsReviews": true
}
```

读取 `products[]` 中的标题、图片、`aboutItem`、`productDescription`、价格/原价/币种、`rating`/`ratings`、`variants`、`itemSpecifications`、Prime、库存和配送；按需读取 `boughtTogether`、`relatedProducts` 和 `authorsReviews`。一次最多 40 个 ASIN，按 ASIN 分隔展示；这是当前商品页快照，按成功返回商品数计费，批量前应先确认范围。

### 3. 按条件读取评论

```json
{
  "asin": "B08N5WRWNW",
  "domainCode": "com",
  "star1Num": 30,
  "star2Num": 30,
  "star3Num": 0,
  "star4Num": 0,
  "star5Num": 0,
  "sortBy": "recent",
  "reviewerType": "avp_only_reviews",
  "mediaType": "all_contents",
  "formatType": "all_formats",
  "filterByKeyword": "battery"
}
```

按 `rating` 分组展示 `title`、`text`、`date`、`verified`、`vine`、`numberOfHelpful`、图片/视频链接，并先给出重复痛点或受好评特征。一次只查一个 ASIN；若传入任意星级数量，未传的星级按 0 处理，每个星级最多 100 条。按计划抓取页数计费，调用前说明预计范围。

### 4. 图片视觉搜索与 Keepa 补充

```json
{
  "imageUrl": "https://example.com/product-image.jpg",
  "amazonDomain": "amazon.de",
  "sort": "price-asc-rank",
  "deliveryZip": "10115",
  "aggregateByKeepaData": true
}
```

读取 `products[]` 的 `asin`、`title`、`asinUrl`、`price`、`oldPrice`、`currency`、`rating`、`ratings`、`brand`，以及启用后存在的 `salesRank`、`monthlySalesUnits`、`fbaFees`、`fulfillment`、`sellerNum`、`variationNum`、尺寸和 `lastUpdate`；报告 `total`/`totalCount` 与 `costToken`。`imageUrl` 必须公开可访问；`deliveryZip` 与 `countryOrAreaCode` 互斥；Keepa 补充会增加消耗，应按用户要求启用。

### 5. Alexa 自然语言导购

```json
{
  "prompts": ["best wireless earbuds for running on Amazon US under $100"],
  "format": "json",
  "url": "https://www.amazon.com/s?k=wireless+earbuds"
}
```

成功时读取 `data[]` 的 `content`、`products[].title`、商品 `asin`/`title`/`url`/`cover`/`price`/`originalPrice`/`score`/`ratingsCount`/`describe`、`followUpQuestions` 和 `screenshot`，并报告 `resultsNum`、`costToken`。每次 `prompts` 只能有 1 个元素且长度不超过 255 字符；后续问题须把上一轮要点和新问题拼成新的 `prompts[0]`。需要用户可读报告时省略 `format` 或使用 `markdown`；只在有具体页面上下文时传 `url`。

## 展示规则

1. **按结果类型呈现**：关键词搜索用表格展示位置、ASIN、标题、价格、评分、评论数、品牌和赞助状态；商品详情按 ASIN 分块，五点用列表、规格和价格用表格、变体按维度展示；评论按星级分组并先总结主题；图片搜索用商品对比表；Alexa 的 `markdown` 结果直接保留其问答、商品分组和追问结构。
2. **标注实时性和来源**：说明数据来自亚马逊前台以及对应的搜索、详情、评论、图片或 Alexa 数据路径，并在用户关心时间时指出这是调用时快照；不要把 Alexa 推荐或视觉相似度描述为确定性结论。
3. **处理价格和站点**：价格必须带币种代码或符号；同时展示原价时明确折扣；明确 `amazonDomain` 或 `domainCode`，不要跨站点混淆价格、评论和配送。
4. **展示图片与链接**：详情和图片搜索中的图片 URL 可作为内嵌图片或可点击链接；搜索结果默认展示链接，不主动渲染图片；Alexa 展示商品详情 URL，截图 URL 作为补充链接。
5. **展示扩展字段**：详情有 `customerReviews` 时展示 5—1 星分布；详情存在变体、关联商品或作者评论时分别标注其返回条件；图片搜索启用 Keepa 且字段存在时补充销售排名、月销量、FBA 费用、配送方式和更新时间；评论明确标注 Vine、认证购买、媒体和有用票数。
6. **保持字段客观**：`0`、`-1`、空字符串或缺失字段按 N/A/不可用展示或省略，不将它们解释为零销量、零费用或已确认的属性；rating、价格、币种和评论数按原始响应归一化展示。
7. **报告数量和错误**：始终报告 `total`/`totalCount`、`resultsNum` 或可用的结果数量；若 `resultsNum=0` 或列表为空，说明没有可用结果并建议改写 Alexa 问题或检查输入；非 200 业务状态展示 `errmsg`/`msg`，根据错误建议检查 ASIN、站点、图片 URL、排序值、邮编或参数范围。
8. **尊重不支持的操作**：用户要求不支持的排序、站点、批量方式或 SQL 二次处理时，直接说明可用选项和限制，不用其他工具绕过；评论多 ASIN 分开调用，Alexa 追问遵守单 prompt 规则。
9. **说明分析性质**：评论痛点、竞品比较和推荐排序是基于返回数据的整理；视觉结果是相似商品列表；不把这些结果扩展为销售预测、广告效果、历史趋势或法律判断。

## 解决认证和积分问题

发生以下异常情况时，读取 `references/onboarding.md`，按其中的 MCP 安装、WorkBuddy 自动授权异常或充值分流处理。不得把“MCP 未安装”误判为下游 401，也不得在 skill 内自行安装或热加载 MCP。

### 异常情况

- **MCP 或 `proxy_call` 缺失**：这是客户端配置问题。读取 onboarding，给出配置示例并停止业务调用；不尝试 HTTP 回退。
- **MCP/代理层失败**：`isError=true`、连接中断、工具不存在或 `toolName` 不可路由时，展示 MCP 层错误并停止。不将其当作下游业务错误，不猜测新 `toolName`。
- **下游响应 401**：代理成功后的业务 `errcode/errorCode/code=401`，或消息包含 `authorized error`、`鉴权失败`、`未授权`、`unauthorized`。按 onboarding 检查 WorkBuddy 登录与自动授权状态，重启或重载连接；不得要求用户配置 MCP header，也不把凭证放入 `arguments`。
- **下游响应 402**：代理成功后的业务状态为 402，或消息含“积分余额不足”“计费不足”“余额不足”“quota exceeded”“insufficient balance”“套餐到期”“需充值”“请充值”等同义表达时，引导用户访问 `https://agent.linkfox.com/` 查看余额和充值。不得自动下单、自动选套餐或轮询支付结果，也不要把 402 当成参数错误。
- **其他下游错误**：`403` 等非认证/计费错误不归入上述两类；透传业务错误信息，并按对应 reference 的参数和站点建议修正，不自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
