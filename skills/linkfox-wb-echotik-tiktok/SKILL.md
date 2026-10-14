---
name: linkfox-wb-echotik-tiktok
display_name: LinkFox EchoTik TikTok选品
display_name_en: LinkFox EchoTik TikTok Product Selection
description: 面向 TikTok Shop 的商品、店铺与带货视频数据选品分析能力，支持发现、筛选、对比和追踪重点对象。
description_zh: 面向 TikTok Shop 选品与竞品研究，按市场、销量、GMV、价格、佣金、店铺、达人带货视频和时间榜单发现机会，并对已知商品、店铺或视频做批量详情对比、关联内容分析和视频地址解析。覆盖 16 个 TikTok Shop 市场；需要发现对象时使用搜索/榜单，需要已知 ID 或 URL 时使用详情查询。触发词包括 TikTok 选品、商品搜索、爆品/新品排行、店铺分析、带货视频、视频排行、商品或视频详情、TikTok 视频下载、EchoTik 数据等。完整参数与 MCP 调用见 references/。
description_en: TikTok Shop product-selection and competitive-research capability for discovering and comparing products, stores, and shoppable videos by marketplace, sales, GMV, price, commission, creator activity, and time-based rankings. It also retrieves batch details for known product/store/video IDs or URLs, analyzes product-linked videos, and resolves playable or downloadable TikTok video addresses. Covers 16 TikTok Shop markets; use search and ranking operations for discovery and detail operations for known IDs or URLs. Triggered by TikTok product research, product/store/video rankings, shoppable-video analysis, product or video detail lookup, TikTok video download, and EchoTik data requests. Full parameters and MCP calls are in references/.
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


# LinkFox EchoTik TikTok选品（LinkFox EchoTik TikTok Product Selection）

面向 TikTok Shop 选品、竞品拆解与带货内容研究：先按市场和指标发现商品、新品、店铺或视频，再用已知 ID/URL 获取详情并进行可核验的横向对比。结果包括销量、GMV、价格、评分、佣金、达人/视频/直播覆盖，以及视频播放与转化指标；必要时还可解析指定 TikTok 视频的播放、封面和下载地址。

本能力覆盖 11 个子能力、11 个 API operation，支持 US、ID、TH、PH、MY、VN、GB、MX、SG、SA、BR、ES、JP、DE、IT、FR 共 16 个市场。每个子能力的完整参数、响应字段、错误码和特殊规则归档在对应 `references/<子能力标识>.md`；`scripts/response_io.py` 只负责可选的本地响应保存与读取。

## 能力边界

### 能力范围

- **商品发现与选品筛选**：使用 `linkfox-echotik-list-product` 按关键词、市场、销量/GMV、价格、评分、佣金、达人数、视频数、上架时间等条件搜索商品；使用 `linkfox-echotik-list-new-product-rank` 查询指定日期的新品榜，识别正在增长的商品。
- **已知商品详情对比**：使用 `linkfox-echotik-batch-product-detail` 按 `productIds` 或 TikTok Shop `productUrls` 批量获取多周期销量、GMV、直播、视频、达人、价格、评分、佣金、趋势与上下架/全托管状态。
- **店铺发现与画像**：使用 `linkfox-echotik-list-seller` 按市场、类目、30 日 GMV、销售趋势、本土/跨境和视频/直播带货方式筛选店铺；使用 `linkfox-echotik-seller-detail` 获取单店完整经营画像。
- **店铺商品盘点**：使用 `linkfox-echotik-list-seller-product` 根据 `sellerId` 查看单店商品目录，并按销量、GMV、价格或近 7 日表现排序。
- **视频发现与榜单研究**：使用 `linkfox-echotik-list-video` 按区域、达人、商品、类目、播放量、时长、发布时间、带货/投流/AI 标识筛选视频；使用 `linkfox-echotik-list-video-rank` 按日/周/月和播放量或视频销量查询带日期的排行榜。
- **商品关联视频分析**：使用 `linkfox-echotik-product-video` 根据 `productId` 查看关联带货视频，比较播放、互动、销量和 GMV，并支持达人和时间范围过滤。
- **已知视频详情与素材地址**：使用 `linkfox-echotik-batch-video-detail` 按视频 ID/URL 批量获取表现详情；使用 `linkfox-echotik-get-video-download-url` 将一个 TikTok 视频链接解析为无水印/含水印下载地址、播放地址和封面地址。
- **数据交付与审计**：MCP 不会自动提供旧脚本的响应落盘、摘要或 24 小时缓存。需要长期复核时，将单次解析后的业务 JSON 交给 `scripts/response_io.py save` 保存，再用 `read` 按字段读取。

### 边界与限制

- 所有数据来自 EchoTik 查询结果，销量、GMV、视频归因等属于估算或平台抓取指标；不能据此作出确定的利润、法律、平台合规或投资结论。
- 商品、店铺和视频的搜索/榜单用于发现与筛选；批量商品/视频详情与店铺商品列表需要已有合法的 ID 或 URL，不能把详情接口当作关键词搜索接口。
- `region`、`date`、`rankType`、`videoRankField`、`sellerId`、`productId`、`videoIds`/`videoUrls` 和视频 `url` 的必填条件因 operation 不同；调用前必须按对应 reference 传参。
- 多数列表接口的 `pageSize` 必须是 10 的倍数且最大为 100；视频排行数据可能滞后 1–2 天，日期过近可能无数据。
- 非英语市场的商品关键词应尽量使用目标市场语言；类目 ID、商品 ID、店铺 ID、达人 ID 通常是内部标识，不能自行翻译或猜测。
- 下载/播放地址可能受区域、隐私和源站限制，且可能过期；没有返回的下载字段不得补造链接。视频销量和 GMV 仅作估算展示。
- 不适用于 TikTok 店铺订单、库存、广告投放、物流履约、达人私信、内容创作/剪辑、商品上架、跨平台数据、评论文本分析或供应链采购；也不提供法律意见、利润测算或自动运营动作。
- MCP 可用性、WorkBuddy 自动授权、积分余额和数据源覆盖会影响结果。失败或空结果不得自动换参数、无限翻页或重复试探；需要再次查询前说明可能产生额外消耗。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找 TikTok 上正在卖的商品”“按关键词筛高销量/高佣金商品” | `linkfox-echotik-list-product` | 只关心某个日期的新品榜用 `linkfox-echotik-list-new-product-rank`；已有商品 ID/URL 的多品对比用 `linkfox-echotik-batch-product-detail` |
| “TikTok 新品排行”“今天/某天的热门新品” | `linkfox-echotik-list-new-product-rank` | 需要自由组合销量、价格、佣金等筛选用 `linkfox-echotik-list-product`；需要已知商品完整指标用 `linkfox-echotik-batch-product-detail` |
| “比较这些 TikTok 商品的销量、GMV、直播和达人数据” | `linkfox-echotik-batch-product-detail` | 没有 ID/URL、需要先发现商品时用 `linkfox-echotik-list-product` 或新品榜 |
| “找 TikTok 店铺/店铺排行/本土跨境店铺” | `linkfox-echotik-list-seller` | 已知 `sellerId` 查单店画像用 `linkfox-echotik-seller-detail`；查看该店在卖什么用 `linkfox-echotik-list-seller-product` |
| “看这家店的商品和爆款” | `linkfox-echotik-list-seller-product` | 需要店铺总 GMV、粉丝、评分和带货覆盖用 `linkfox-echotik-seller-detail`；尚无 `sellerId` 时先用店铺搜索 |
| “找热门/带货/投流/AI TikTok 视频” | `linkfox-echotik-list-video` | 要日/周/月榜单用 `linkfox-echotik-list-video-rank`；已有视频 ID/URL 查详情用 `linkfox-echotik-batch-video-detail` |
| “本周最火视频”“按视频销量排榜” | `linkfox-echotik-list-video-rank` | 想按达人、商品、播放量、投流或 AI 条件自由筛选用 `linkfox-echotik-list-video`；只分析某商品的关联视频用 `linkfox-echotik-product-video` |
| “这个商品有哪些带货视频/哪个视频转化高” | `linkfox-echotik-product-video` | 用户提供的是一批视频 ID/URL 时用 `linkfox-echotik-batch-video-detail`；只有区域和筛选条件时用视频列表 |
| “分析这些视频的播放和销量” | `linkfox-echotik-batch-video-detail` | 未提供具体 ID/URL、想发现视频时用视频列表或视频榜；想下载单条视频时用 `linkfox-echotik-get-video-download-url` |
| “下载这个 TikTok 视频/去水印链接” | `linkfox-echotik-get-video-download-url` | 只要播放和营销表现详情用批量视频详情；要发现某商品的带货视频用商品视频 |

选择时先判断用户是否提供了“已知对象”：没有 ID/URL 时优先发现型接口；有商品/店铺/视频 ID 或 URL 时优先详情型接口。再根据是否需要自由筛选、固定日期榜单、单店/单品范围和输出成本选择；多个 operation 都能满足时，向用户说明差异、默认推荐最贴合者，并让用户决定是否继续产生额外调用。

## 业务需求路由速查

| 子能力 | reference | 原 endpoint | 精确 `toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-echotik-list-new-product-rank` | `references/linkfox-echotik-list-new-product-rank.md` | `/echotik/listNewProductRank` | `echotik/listNewProductRank` | `response_io.py` |
| `linkfox-echotik-list-product` | `references/linkfox-echotik-list-product.md` | `/echotik/listProduct` | `echotik/listProduct` | `response_io.py` |
| `linkfox-echotik-list-seller` | `references/linkfox-echotik-list-seller.md` | `/echotik/listSeller` | `echotik/listSeller` | `response_io.py` |
| `linkfox-echotik-list-seller-product` | `references/linkfox-echotik-list-seller-product.md` | `/echotik/listSellerProduct` | `echotik/listSellerProduct` | `response_io.py` |
| `linkfox-echotik-seller-detail` | `references/linkfox-echotik-seller-detail.md` | `/echotik/sellerDetail` | `echotik/sellerDetail` | `response_io.py` |
| `linkfox-echotik-list-video` | `references/linkfox-echotik-list-video.md` | `/echotik/listVideo` | `echotik/listVideo` | `response_io.py` |
| `linkfox-echotik-list-video-rank` | `references/linkfox-echotik-list-video-rank.md` | `/echotik/listVideoRank` | `echotik/listVideoRank` | `response_io.py` |
| `linkfox-echotik-batch-video-detail` | `references/linkfox-echotik-batch-video-detail.md` | `/echotik/batchVideoDetail` | `echotik/batchVideoDetail` | `response_io.py` |
| `linkfox-echotik-product-video` | `references/linkfox-echotik-product-video.md` | `/echotik/listProductVideo` | `echotik/listProductVideo` | `response_io.py` |
| `linkfox-echotik-batch-product-detail` | `references/linkfox-echotik-batch-product-detail.md` | `/echotik/batchProductDetail` | `echotik/batchProductDetail` | `response_io.py` |
| `linkfox-echotik-get-video-download-url` | `references/linkfox-echotik-get-video-download-url.md` | `/echotik/getVideoDownloadUrl` | `echotik/getVideoDownloadUrl` | `response_io.py` |

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 调用参数：`toolName` 使用上表 endpoint 去掉前导 `/` 的精确值；`arguments` 直接使用对应 reference 的请求参数对象。
- `toolName` 区分大小写；禁止额外包裹 `body`、`params`、`data` 或另一层 `arguments`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、API Key、token、JWT、手机号或其他凭证。
- 禁止通过旧脚本、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 缺失时不得 HTTP fallback。
- 同一任务相同 `toolName + arguments` 只调用一次。收费调用失败、空结果或结果不理想时不得自动换参数、翻页或重试。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与 `errmsg` / `msg`。
- MCP 不提供旧脚本的 24 小时缓存、自动响应落盘或 stdout 摘要。需要保存时使用 `response_io.py save`，但仍以同一任务调用记录防止重复收费。
- 完整参数、响应、成本和展示限制见对应 reference；`pageNum` 从 1 开始，`pageSize` 规则以具体 operation 为准。

配置：

```json
{"mcpServers":{"LinkFox":{"type":"streamableHttp","url":"https://mcp-tool-gateway.linkfox.com/mcp/any-tool"}}}
```

## 使用示例

以下示例使用真实参数名，执行时将 JSON 作为对应 `toolName` 的 `arguments`。示例中的 ID 仅用于展示格式；返回结果应以接口实时数据为准。

### 1. 关键词商品搜索

```json
{
  "keyword": "phone case",
  "region": "US",
  "minTotalSale30dCnt": 1000,
  "minProductCommissionRate": 0.1,
  "productSortField": 5,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

调用 `echotik/listProduct`。重点读取 `products` 的商品名、价格/货币、总销量、30 日销量/GMV、评分、佣金和达人/视频数量；佣金小数需展示为百分比，非英语市场要注意关键词本地化。

### 2. 指定日期新品榜

```json
{
  "date": "2026-08-20",
  "region": "GB",
  "pageNum": 1,
  "pageSize": 20
}
```

调用 `echotik/listNewProductRank`。读取 `products`、`total`、`costToken` 和销售趋势；`date` 必填且是日快照，不等于跨月历史趋势，结果较多时分页。新品榜字段中的 `asin` 是商品标识。

### 3. 批量商品详情

```json
{
  "productIds": ["1729382310407603945", "1729382310407603946"],
  "productUrls": ["https://shop.tiktok.com/us/pdp/phone-case/1729382310407603947"]
}
```

调用 `echotik/batchProductDetail`。`productIds` 与 `productUrls` 至少传一个，服务端合并后单次最多 1000 个；读取 `products` 的 1d/7d/15d/30d/60d/90d/累计销量与 GMV、直播/视频/达人指标、`salesTrendFlag`、`isSShop`、`offMark` 和 `freeShipping`。价格字段按 reference 标注为 USD，缺失记录要列出原始 ID/URL。

### 4. 店铺发现、画像与商品盘点

店铺搜索：

```json
{
  "region": "US",
  "fromFlag": 2,
  "salesTrendFlag": 1,
  "minTotalSaleGmv30dAmt": 50000,
  "sellerSortField": 2,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

调用 `echotik/listSeller` 取得 `sellerId`；随后可用以下参数查单店详情：

```json
{
  "sellerId": "7495514739648989419"
}
```

分别调用 `echotik/sellerDetail` 与 `echotik/listSellerProduct`。详情接口返回扁平店铺对象，不要期待 `sellers` 列表；店铺商品接口仅接受 `sellerId` 与排序/分页，不支持关键词或区域筛选。店铺列表和店铺商品的 `pageSize` 必须遵守 10 的倍数/最大 100 规则。

### 5. 视频发现与视频榜

条件搜索：

```json
{
  "region": "US",
  "salesFlag": 1,
  "minTotalViewsCnt": 100000,
  "videoSortField": 3,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

日期榜单：

```json
{
  "date": "2026-08-10",
  "rankType": 2,
  "region": "US",
  "videoRankField": 2,
  "createdByAi": "true",
  "pageSize": 20,
  "pageNum": 1
}
```

分别调用 `echotik/listVideo` 与 `echotik/listVideoRank`。前者 `region` 必填，可按达人/商品/播放量/时长/时间/带货/投流/AI 筛选；后者 `date`、`rankType`、`region`、`videoRankField` 均必填，`rankType` 为 1/2/3，`videoRankField` 为 1/2。榜单要保留返回顺序；按某指标排序时其他指标可能为 0，销量和 GMV 要标注为估算。

### 6. 商品关联视频与已知视频详情

商品关联视频：

```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 4,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

批量视频详情：

```json
{
  "videoIds": ["7030893014180531462", "6768504823336815877"],
  "videoUrls": ["https://www.tiktok.com/@creator/video/7425631540178160939"]
}
```

分别调用 `echotik/listProductVideo` 与 `echotik/batchVideoDetail`。商品视频排序字段 1–6 依次为播放、点赞、分享、视频销量、视频 GMV、发布时间；批量视频详情的 ID/URL 可混传，合计最多 1000 个。展示时提供官方 URL、描述、播放/互动、销售/GMV、达人和带货/投流/AI 标识，并列出没有返回数据的 ID/URL。

### 7. 解析 TikTok 视频播放与下载地址

```json
{
  "url": "https://www.tiktok.com/@creator/video/1234567890"
}
```

调用 `echotik/getVideoDownloadUrl`。优先展示 `noWatermarkDownloadUrl`，其次是 `downloadUrl`；两者均缺失时只能提供 `playUrl` 预览，并展示 `coverUrl`/`dynamicCoverUrl`。地址可能过期，应提示及时使用；不要把视频地址解析当成视频发现或视频表现分析。

## 展示规则

1. **先说明查询上下文**：展示 operation 对应的市场、日期/榜单周期、筛选条件、当前页与 `total`；市场未指定时，适用接口可使用 US，`region` 必填接口不能省略。
2. **使用结构化表格**：商品表至少呈现名称/ID、价格和货币、总销量、近 30 日销量或 GMV、评分、评论、佣金；店铺表呈现店铺、地区、总销量、30 日 GMV、粉丝、评分、评价、达人数和店铺链接。
3. **视频结果保留可核验信息**：视频表呈现描述（过长截断）、视频 ID、播放/点赞/评论/分享/收藏、视频销量、GMV、发布时间、达人 ID；有 `officialUrl` 时提供原始 TikTok 链接，有 `coverUrl` 时标记封面可用。
4. **正确解释单位和枚举**：佣金小数转换为百分比；价格与 GMV 带货币；`duration` 秒转换为可读时长；`YYYYMMDD` 和 Unix 秒级时间戳按各自字段解释；销售趋势 0/1/2 显示为稳定/上升/下降。
5. **区分累计与周期值**：详情结果同时出现累计与 1d/7d/15d/30d/60d/90d 时，标明统计窗口；视频列表的 1d/7d/30d 播放/点赞增量不要与累计值混淆。
6. **明确估算和缺失**：视频销量、视频 GMV、商品归因等估算值必须标注“估算”；API 未返回的下载地址、字段或视频/商品记录显示为不可用，不得补造。
7. **处理榜单和大结果集**：榜单保留接口排名顺序；结果多时先展示当前页和前若干项，并提示可分页或收紧筛选，不要自动连续翻页。
8. **展示状态与风险提示**：商品详情标记趋势、全托管、下架、包邮等状态；店铺标记本土/跨境、视频/直播带货和趋势；视频下载结果提示地址可能过期及区域/隐私限制。
9. **按错误信息给出修正建议**：400 检查必填字段、枚举、日期、时间戳、ID/URL 格式和 pageSize；10000 检查无匹配对象或过近榜单日期；401/402 按下方认证与积分流程处理；其他错误原样依据 `errmsg` 说明。
10. **保留审计出处**：说明数据来自 EchoTik operation，并保留 `toolName`、`arguments` 和必要的本地 JSON 路径；不要把实时查询结果描述成数据库统计或确定性的经营结论。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`：MCP 缺失时停止并提示配置；MCP 连接 401 按 WorkBuddy 自动授权链路异常处理；代理成功后的下游 401、402、403 与其他业务错误分别处理。不得要求或接收用户手工提供 Authorization、API Key、token、JWT 或手机号，不得自动购买套餐、支付或轮询订单。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
