---
name: linkfox-wb-kalodata-tiktok
display_name: LinkFox TikTok选品
display_name_en: LinkFox TikTok Product Selection
description: 面向 TikTok Shop 选品与竞品研究的 Kalodata 数据能力，发现并分析商品、店铺、达人、带货视频和直播榜单及详情。
description_zh: 面向 TikTok Shop 选品、竞品发现和带货表现研究的 Kalodata 数据能力。支持按地区、时间、语言和币种查看商品、店铺、达人、带货视频及直播榜单，并用榜单中的 ID 查询单个实体的销售额、销量、GMV、互动、佣金、渠道拆分和关联关系。当用户需要 TikTok 选品、爆品/热销排行、店铺或达人对比、带货视频分析、直播带货数据或指定实体详情时触发。完整参数、字段、错误码和 MCP 调用示例见 references/。
description_en: Kalodata data capability for TikTok Shop product selection, competitor discovery, and shoppable-performance research. It covers regional and time-windowed rankings plus single-entity details for products, shops, creators, shoppable videos, and livestreams, including sales, GMV, engagement, commission, channel splits, and related entities. Trigger it for TikTok product selection, bestseller discovery, shop or creator comparison, shoppable-video analysis, livestream commerce metrics, or a known entity ID lookup. Full parameters, fields, errors, and MCP examples are in references/.
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


# LinkFox TikTok选品（LinkFox TikTok Product Selection）

这是面向 TikTok Shop 经营决策的市场数据能力：先按市场和时间窗口发现高表现商品、店铺、达人、带货视频或直播，再沿榜单中的字符串 ID 深入查看单个对象的销售、流量、互动、佣金、渠道收入和关联关系。它适合做选品初筛、竞品拆解、达人合作线索发现、内容/直播表现对比和详情核验；返回可直接分析的原始业务数据和关键指标。

关联工具键为 `kalodata_tiktok`。当前能力覆盖 5 个业务模块、10 个 API operation：`linkfox-kalodata-tiktok-product`、`linkfox-kalodata-tiktok-shop`、`linkfox-kalodata-tiktok-creator`、`linkfox-kalodata-tiktok-video`、`linkfox-kalodata-tiktok-livestream`，每个模块均包含一个 rank operation 和一个 detail operation。

## 能力边界

### ✅ 能力范围

- **商品选品与商品核验**（`linkfox-kalodata-tiktok-product`）：用 `POST /kalodata/product/rank` 查看热销商品，比较价格、销量、GMV、视频/直播/橱窗收入、增长率、佣金率和上架日期；用 `POST /kalodata/product/detail` 查看价格区间、评论、类目、配送、所属店铺及关联视频/直播/达人。
- **店铺竞争研究**（`linkfox-kalodata-tiktok-shop`）：用 `POST /kalodata/shop/rank` 查看 TikTok Shop 店铺排行及自营、达人分销、商城收入拆分；用 `POST /kalodata/shop/detail` 查看店铺规模、商品、达人、视频和直播数量。
- **达人合作与带货表现**（`linkfox-kalodata-tiktok-creator`）：用 `POST /kalodata/creator/rank` 发现高表现达人，比较粉丝、内容观看、销量、视频/直播收入和增长率；用 `POST /kalodata/creator/detail` 查看地区、状态、简介、视频/直播 GPM、关联商品/店铺及已提供的联系方式。
- **带货视频研究**（`linkfox-kalodata-tiktok-video`）：用 `POST /kalodata/video/rank` 查看高表现视频，支持 `revenue_range` GMV 范围和 `sortField`；用 `POST /kalodata/video/detail` 查看播放、点赞、评论、分享、销量、视频 GPM、广告播放、ROAS、CPA、投放周期、时长和关联商品。
- **带货直播研究**（`linkfox-kalodata-tiktok-livestream`）：用 `POST /kalodata/livestream/rank` 查看按地区/时间窗口的直播榜；用 `POST /kalodata/livestream/detail` 查看指定直播的观看人数、GMV、GPM、时长和带货商品数。
- **发现到详情的链路**：rank 返回的 `product_id`、`shop_id`、`creator_id`、`video_id`、`livestream_id` 都必须作为字符串保留，并分别传给对应 detail 的 camelCase 参数；各模块的字段、示例和错误码详见同名 reference。
- **统一查询条件与结果处理**：rank 可按 `region`、`dateRange`、`language`、`currency` 查询，通常可用 `pageNumber` 1–5 与 `pageSize` 5–100 翻页；结果由 MCP 直接返回，按对应 reference 的响应字段解析。

### ❌ 边界与限制

- **榜单不是关键词搜索**：这些 rank operation 是按市场和时间窗口浏览榜单，不支持按商品名、店铺名、达人昵称、视频标题或直播标题检索；需要详情时必须先取得有效 ID。合法但无数据的查询可能返回 `errcode=200` 且没有 `data`，仍可能计费。
- **分页和数据时效**：响应通常不提供可信的 `total` 或总页数；以 `data.length` 判断当前页，返回条数小于 `pageSize` 或达到第 5 页时停止。数据可能存在 T+1 统计延迟，不等同于实时后台数据。
- **字段必须按 operation 区分**：所有销量字段都使用接口原样拼写 `sales_volumn`；直播 rank 用 `views`、字符串类型的 `revenue`/`unit_price`，detail 用 `viewers`、数字类型的 `revenue` 和 detail-only `gpm`；店铺 rank/detail 的渠道字段分别为 `self_promotion_revenue`/`shopping_mall_revenue` 与 `self_account_revenue`/`shoppingmall_revenue`。不得跨 operation 混用字段。
- **排序与过滤限制**：默认排序为 revenue（GMV）降序；`sortField` 的可接受结构由网关决定。收到不支持的排序字段时回退默认顺序并告知用户，不臆造字段或绕过校验；视频的 GMV 范围仅使用 `revenue_range`。
- **ID 和指标口径**：超长 ID 不能转为浮点数；收入是 GMV/销售额，不是利润、广告花费或净收益；`commission_rate`、`revenue_growth_rate` 为直接百分比数值。金额必须同时标明请求的 `currency`、`region` 与 `dateRange`。
- **认证、计费和重试**：WorkBuddy 通过 MCP 连接自动授权，调用参数中禁止加入 `headers`、`Authorization`、API key 或 token。每次业务调用都可能产生积分消耗；失败、空结果或参数不支持时不得自动重试、自动换参数、自动翻页探测或重复试探。需要再次调用时先说明原因并取得用户确认。
- **不提供的业务**：不负责 TikTok 广告投放或广告账户管理、内容创作/编辑/下载、店铺订单/库存/ERP、物流供应链、平台账号运营、关键词搜索、跨平台商品研究、法律/财务结论或与平台/卖家的直接沟通。

## 工具选择指南

按用户真正要观察的对象与指标选择 rank 或 detail；先用 rank 发现对象，再用对应 detail 深查。不同需求都能落到“商品/店铺/达人/视频/直播”时，优先按用户要做的决策对象选择，而不是仅按“销量”这个共同指标选择。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| TikTok 选品、爆品、热销商品、商品排行 | `linkfox-kalodata-tiktok-product` 的 `product/rank` | 要核验已知 `productId` 的价格区间、评论、渠道和关联对象时换 `product/detail` |
| 已知商品 ID 的销售与关联分析 | `linkfox-kalodata-tiktok-product` 的 `product/detail` | 只有商品名称、还没有 `productId` 时先回到 `product/rank`；它不支持按名称搜索 |
| TikTok 店铺排行、热销店铺、竞品店铺 | `linkfox-kalodata-tiktok-shop` 的 `shop/rank` | 要看单店铺达人合作、视频/直播数量和渠道拆分时换 `shop/detail` |
| 已知店铺 ID 的店铺资料 | `linkfox-kalodata-tiktok-shop` 的 `shop/detail` | 只有店铺名时先用 `shop/rank`，不能把店铺名直接当 `shopId` |
| TikTok 达人榜、网红合作线索、达人对比 | `linkfox-kalodata-tiktok-creator` 的 `creator/rank` | 要看单个达人的粉丝变化、视频/直播 GPM 或联系方式时换 `creator/detail` |
| 已知达人 ID 的带货资料 | `linkfox-kalodata-tiktok-creator` 的 `creator/detail` | 只有昵称或 handle 时先用 `creator/rank`；详情不按昵称搜索 |
| 热门带货视频、视频 GMV/播放排行 | `linkfox-kalodata-tiktok-video` 的 `video/rank` | 需要 GMV 范围用 `revenue_range`，需要单视频广告和互动明细时换 `video/detail` |
| 视频爆量、互动、广告指标或视频 GPM | `linkfox-kalodata-tiktok-video` 的 `video/detail` | 没有 `videoId` 时先用 `video/rank`；标题不能直接定位视频 |
| TikTok 带货直播榜、直播排行 | `linkfox-kalodata-tiktok-livestream` 的 `livestream/rank` | 要看单场直播观看人数、时长、GPM 和带货商品数时换 `livestream/detail` |
| 已知直播 ID 的直播数据 | `linkfox-kalodata-tiktok-livestream` 的 `livestream/detail` | 没有 `livestreamId` 时先用 `livestream/rank`；直播标题不能直接定位详情 |
| 跨对象做一轮选品判断 | 先调用 `product/rank`，再按榜单里的店铺/达人/视频/直播 ID 选择对应 detail | 若用户明确关注内容、主播或店铺，应直接选择对应 rank，避免为无关对象付费 |

选择思路：用户问“卖什么”时看商品；问“谁在卖”时看店铺或达人；问“怎么卖/内容表现”时看视频或直播。rank 只用于发现和比较，detail 只用于已有 ID 的单实体核验。若请求多个对象，先说明将产生多次接口消耗，并让用户决定是否继续。

## 业务需求路由速查

下表中的 reference 含该模块的参数、完整响应字段、错误码、MCP 示例、展示限制与反馈接口。`toolName` 必须使用去掉端点前导斜杠后的精确值。

| 子能力 | 业务能力 | reference | `toolName` |
|---|---|---|---|
| `linkfox-kalodata-tiktok-product` | 商品榜单发现 | `references/linkfox-kalodata-tiktok-product.md` | `kalodata/product/rank` |
| `linkfox-kalodata-tiktok-product` | 单商品详情 | `references/linkfox-kalodata-tiktok-product.md` | `kalodata/product/detail` |
| `linkfox-kalodata-tiktok-shop` | 店铺榜单发现 | `references/linkfox-kalodata-tiktok-shop.md` | `kalodata/shop/rank` |
| `linkfox-kalodata-tiktok-shop` | 单店铺详情 | `references/linkfox-kalodata-tiktok-shop.md` | `kalodata/shop/detail` |
| `linkfox-kalodata-tiktok-creator` | 达人榜单发现 | `references/linkfox-kalodata-tiktok-creator.md` | `kalodata/creator/rank` |
| `linkfox-kalodata-tiktok-creator` | 单达人详情 | `references/linkfox-kalodata-tiktok-creator.md` | `kalodata/creator/detail` |
| `linkfox-kalodata-tiktok-video` | 带货视频榜单发现 | `references/linkfox-kalodata-tiktok-video.md` | `kalodata/video/rank` |
| `linkfox-kalodata-tiktok-video` | 单视频详情 | `references/linkfox-kalodata-tiktok-video.md` | `kalodata/video/detail` |
| `linkfox-kalodata-tiktok-livestream` | 带货直播榜单发现 | `references/linkfox-kalodata-tiktok-livestream.md` | `kalodata/livestream/rank` |
| `linkfox-kalodata-tiktok-livestream` | 单直播详情 | `references/linkfox-kalodata-tiktok-livestream.md` | `kalodata/livestream/detail` |

## 调用方式

- **MCP Server**：`LinkFox`
- **MCP URL**：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **MCP 工具**：只调用 `proxy_call`。
- **参数封装**：外层始终包含 `toolName` 与 `arguments`；`arguments` 直接放原业务请求对象。例如 `POST /kalodata/product/rank` 对应 `toolName: "kalodata/product/rank"`。
- **自动授权**：WorkBuddy 自动注入授权信息；业务参数和示例中禁止出现 `headers`、`Authorization`、API key 或 token。
- **结果处理**：先检查 MCP 连接、工具 schema 和 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errmsg`，最后读取业务字段。不得把 MCP 外层对象当作下游响应，也不得循环解析字符串化 JSON。不承诺本地缓存、响应落盘或 stdout 摘要；完整 request/response/error/feedback 细节见对应 reference。
- **禁止回退**：不得使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 或 `proxy_call` 缺失、连接失败或返回错误时停止，不得静默 HTTP fallback，也不得猜测其他 `toolName`。
- **调用纪律**：同一会话同参数默认只调用一次。不要因空结果、失败或字段缺失自动重试、换区域、换时间、改 ID、改筛选或连续翻页。需要下一页或再次调用时，先说明额外积分消耗并取得用户确认；rank 最多第 5 页。
## 使用示例

以下示例均为接近可执行的 JSON 参数；缺省字段由网关处理。一次 rank 结果中的字符串 ID 可直接作为对应 detail 的 camelCase ID，但不要把示例 ID 当成用户未提供的真实对象。

### 1. 商品选品：榜单到详情

```json
{
  "toolName": "kalodata/product/rank",
  "arguments": {
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD",
    "language": "en-US",
    "pageSize": 20,
    "pageNumber": 1
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/product/rank"`），重点查看 `product_id`、`product_name`、`unit_price`、`sales_volumn`、`revenue`、`video_revenue`、`live_revenue`、`showcase_revenue`、`commission_rate` 和 `launch_date`。选定 `product_id` 后：

```json
{
  "toolName": "kalodata/product/detail",
  "arguments": {
    "productId": "1729508370969629931",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/product/detail"`），重点查看 `min_price`/`max_price`、`product_review_count`、`product_shop_id`、`delivery_type`、`creator_number`、`video_number`、`live_number` 和 detail 的 `shopping_mall_revenue`。渠道收入按接口定义相加，详情 GMV 可能因独立四舍五入存在微小差异。

### 2. 店铺竞争：排行到店铺画像

```json
{
  "toolName": "kalodata/shop/rank",
  "arguments": {
    "region": "US",
    "dateRange": "last30Day",
    "currency": "USD",
    "pageSize": 10,
    "pageNumber": 1,
    "sortField": {}
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/shop/rank"`），显示 `rank`、店铺、`revenue`、`sales_volumn`、`on_sell_product_count`、`unit_price` 和渠道拆分。选定榜单 `shop_id` 后：

```json
{
  "toolName": "kalodata/shop/detail",
  "arguments": {
    "shopId": "7495514739648989419",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/shop/detail"`），使用 detail 的 `seller_type`、`self_account_revenue`、`shoppingmall_revenue`、`creator_number`、`video_number`、`live_number`、`product_number`；不要把 rank 的 `shop_type`、`self_promotion_revenue`、`shopping_mall_revenue` 带入详情抽取。

### 3. 达人合作：榜单到达人详情

```json
{
  "toolName": "kalodata/creator/rank",
  "arguments": {
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD",
    "language": "en-US",
    "pageSize": 10,
    "pageNumber": 1,
    "sortField": {}
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/creator/rank"`），显示昵称、handle、`creator_id`、粉丝、内容观看、`sales_volumn`、总/视频/直播收入和增长率。选定 ID 后：

```json
{
  "toolName": "kalodata/creator/detail",
  "arguments": {
    "creatorId": "7153432386608251946",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/creator/detail"`），查看 `creator_followers`、`new_followers`、`video_gpm`、`live_gpm`、`product_number`、`shop_number` 和联系方式；空联系方式不虚构内容。

### 4. 带货视频：GMV 筛选到视频明细

```json
{
  "toolName": "kalodata/video/rank",
  "arguments": {
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD",
    "revenue_range": "1-1000",
    "sortField": {
      "field": "revenue",
      "type": "DESC"
    },
    "pageSize": 10,
    "pageNumber": 1
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/video/rank"`），这是榜单浏览而非标题关键词搜索；重点查看 `video_id`、播放/互动、`revenue`、广告占比和达人 handle。选定 ID 后：

```json
{
  "toolName": "kalodata/video/detail",
  "arguments": {
    "videoId": "7659161409279806734",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/video/detail"`），重点查看 `sales_volumn`、`video_gpm`、`ads_views`、`ads_roas`、`ad_cpa`、`ads_period`、`duration` 和 `product_number`；`video_gpm` 是每千次播放 GMV，不是百分比。

### 5. 带货直播：直播榜到单场详情

```json
{
  "toolName": "kalodata/livestream/rank",
  "arguments": {
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD",
    "language": "en-US",
    "pageSize": 10,
    "pageNumber": 1,
    "sortField": {}
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/livestream/rank"`），显示标题、creator handle、rank 隐含顺序、字符串 `revenue`/`unit_price`、`views`、时长和开始/结束时间。选定 `livestream_id` 后：

```json
{
  "toolName": "kalodata/livestream/detail",
  "arguments": {
    "livestreamId": "7661409374878878494",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }
}
```

调用 MCP `proxy_call`（`toolName: "kalodata/livestream/detail"`），显示单个直播的 `viewers`、数字 `revenue`、`gpm`、`product_number` 和时长。时间戳是 epoch 毫秒，时长是秒；不要将详情呈现成排行榜。

## 展示规则

1. **先标注查询口径**：任何金额、销量、观看或增长指标都标注 `region`、`dateRange`，金额同时标注 `currency`；说明数据来自 Kalodata TikTok Shop 数据接口及具体业务对象。
2. **榜单表格**：商品表至少展示商品名/ID、价格、`sales_volumn`、GMV、渠道收入、增长率、佣金率和上架日期；店铺表展示 rank、店铺、类型、GMV、销量、在售商品、件单价和增长率；达人表展示昵称、handle、粉丝、内容观看、销量、总/视频/直播 GMV 和增长率；视频表展示标题/ID、播放、互动、GMV、广告指标和达人；直播表展示标题、达人、GMV、`views`、时长、件单价和开始/结束时间。
3. **详情分组**：单实体 detail 不当作榜单展示。商品按身份/价格/销量/渠道/佣金/类目/店铺/关联对象分组；店铺按身份/规模/渠道/达人视频直播分组；达人按身份/受众/收入/视频/直播/商品店铺/联系方式分组；视频按身份/互动/变现/广告/达人/时长/关联商品分组；直播按身份/时间/观看/GMV/GPM/商品数分组。
4. **严格使用字段名和类型**：所有销量字段写 `sales_volumn`；达人 `creator_followers`、`content_views` 是字符串计数；视频 detail 的 `sales_volumn` 拼写保留；直播 rank 的 `views` 与 detail 的 `viewers` 不混用，rank 的 `revenue`/`unit_price` 先解析字符串，detail 的 `revenue` 是数字；店铺的 rank/detail 渠道字段按各自 reference 取值。
5. **百分比和 GPM**：`commission_rate`、`revenue_growth_rate`、广告占比带 `%`；佣金值 `25.0` 表示 25%，不是基点；`video_gpm`、`live_gpm`、`gpm` 是每千次展示/播放的 GMV，不是百分比。
6. **时间与顺序**：直播开始/结束时间从 epoch 毫秒格式化为可读本地时间，直播时长按秒；保留服务端默认 revenue 降序和返回顺序，只有用户明确请求且网关支持时才应用 `sortField`。rank 满页时提示可继续下一页，最多第 5 页；没有 `total` 时不要编造总数。
7. **不可用与空字段**：缺失、空字符串、0 或明确不可用值要标注 N/A 或省略，不补造数据；达人联系方式只有在字段有值时展示，否则注明未提供。渠道拆分受四舍五入影响时标注“约等于”。
8. **错误与建议**：展示 `errcode`/`errmsg` 的实际含义。501 若指向 Kalodata 522/554 上游错误，向用户说明后停止；只有用户明确同意时才可同参重试。若是页码、缺 ID 或不支持字段，指出具体修正。401/402 先区分 MCP 层与下游业务层，不把错误响应当正常数据。
9. **客观呈现**：默认只呈现指标、时间窗、字段含义和限制，不把 GMV 直接表述为利润或保证，不给未经用户要求的经营、法律或财务结论；多模块结果要按对象分组并保留来源和时间窗。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`，先判断错误发生在哪一层：

- **MCP 未安装、未连接或找不到 `proxy_call`**：这是 LinkFox MCP 配置问题；按 onboarding 中的固定 server、URL 和工具名检查连接。
- **MCP 层 401**：这是 WorkBuddy 到 MCP 的连接授权问题，检查或重新连接 MCP。不要把 token、API key 或 `Authorization` 放进 `arguments`。
- **下游业务 `errcode=401`**：MCP 已连通，但业务授权失败；保留实际 `errcode`/`errmsg` 并按 onboarding 指引处理。
- **下游业务 `errcode=402`**：积分或余额不足；说明业务调用可能扣费，按 onboarding 提供的充值入口引导用户。
- **下游业务 `errcode=403`**：权限不足，与 401/402 分开处理，不自动重试。
- **其他业务错误**：透传 `errmsg`，按对应 reference 修正参数；任何再次调用都先征得用户确认。
## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
