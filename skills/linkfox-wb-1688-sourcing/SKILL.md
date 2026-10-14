---
name: linkfox-wb-1688-sourcing
display_name: LinkFox 1688找货源
display_name_en: LinkFox 1688 Sourcing
description: 1688货源搜索、以图找货、热销榜单与商品详情核验的一体化采购发现能力。
description_zh: 面向1688采购与选品的货源发现能力：按中文关键词筛选商品和供应商、按图片寻找相似货源、查看周/月热销榜单，并对已知商品的SKU价格、库存、起批量、物流和供应商信息进行核验。当用户说1688找货源、批发采购、工厂货源、一件代发、以图找同款、1688热销榜或查询1688商品详情时触发；仅提供数据检索与事实整理，不代替下单、付款、质量认证或法律判断。
description_en: Unified 1688 sourcing discovery for keyword-based product and supplier search, image-based lookalike sourcing, weekly or monthly bestseller browsing, and known-offer detail verification covering SKU prices, inventory, MOQ, logistics, and supplier facts. Use when users ask to find 1688 wholesale sources, factory suppliers, dropship products, visual matches, trending products, or details for a known 1688 offer or URL. It provides factual retrieval and comparison only, not ordering, payment, quality certification, or legal advice.
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


# LinkFox 1688找货源（LinkFox 1688 Sourcing）

这是面向1688采购决策的统一货源发现与核验能力：从关键词、图片、榜单或已知商品链接出发，返回可比较的商品、供应商、价格、销量、履约与采购条款。能力范围覆盖 4 个子能力、4 个业务 API operation、1 个图片上传辅助端点和 1 个本地 OSS PUT helper。子能力标识为 `linkfox-1688-search-by-image`、`linkfox-1688-product-detail`、`linkfox-dld-product-billboard`、`linkfox-dld-product-search`；全部参数与响应字段见 `references/`。

## 能力边界

### 能力范围

- **关键词货源发现**：用中文关键词、价格、销量、供应商类型、发货时效、代发权益、平台面单和保障条件筛选1688商品；通过 MCP `proxy_call` 的 `dld/productSearch` 路由调用，详见 `references/linkfox-dld-product-search.md`。
- **图片找相似货源**：用公开图片 URL、原始 Base64 或已返回的 `imageId` 找1688同款/相似商品，并按支持的货盘、工厂、体验分、退款率、发货、代发、区域专线等条件筛选；通过 MCP `proxy_call` 的 `alibaba1688/imageSearch` 路由调用。
- **热销与趋势发现**：按中文关键词查看1688周榜或月榜，并按销售笔数、销售件数、预估销售额、上架时间、批发价或代发价排序；通过 MCP `proxy_call` 的 `dld/productBillboard` 路由调用。
- **已知商品核验**：根据一个 `offerId` 或标准1688商品 URL 查询标题、属性、SKU、1件零售价、2件及以上批发阶梯价、库存、MOQ、物流包装、供应商指标、混批、发票和证书；通过 MCP `proxy_call` 的 `alibaba1688/productDetail` 路由调用。
- **本地图片准备**：本地图片先用 `proxy_call` 的 `oss/file/presignedPut` 获取预签名 PUT URL，再由 `scripts/upload_image.py` 仅向该 URL 上传，公开 URL 随后作为 `imageUrl`。

### 边界与限制

- 只检索1688国内批发市场；不处理 Amazon 或其他平台的商品研究、店铺级经营分析、广告、评价分析、运费核算、跨境货代、谈价、下单、付款、物流跟踪或开票履约。
- 图片搜索必须提供 `imageUrl`、`imageBase64`、`imageId` 三者之一；图片 URL/文件只支持 png、jpg、jpeg，Base64 必须是纯编码内容且不能带 `data:image/...;base64,` 前缀。未支持的筛选或排序不可用其他逻辑绕过。
- 关键词搜索和榜单的 `keyWord` 必须是中文；周榜日期必须是周日且只支持近90天，月榜日期必须是当月1日且只支持近12个月。关键词最多50字符，榜单每页最多100条。
- 商品详情是单个 `offerId` 的核验，不是关键词或图片发现；价格、库存、物流和供应商数据会变化，涉及采购成本时应重新取得用户确认后发起实时查询，最终成交价仍需实时订单预览确认。详情接口不会授权账户或改变采购状态。
- 搜索数据是实时返回，不提供基于结果的二次 SQL/数据库查询。字段缺失必须保持未知，不得推断为零、否或已通过认证；销售额是估算值，不能当作实际回款。
- WorkBuddy 自动为 MCP 连接注入授权，业务 `arguments` 中禁止放 `headers`、Authorization、API key 或 token。业务调用可能消耗积分；失败、空结果或分页不得自动改参数连续试探，应先说明再次调用的成本并由用户决定。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找某类1688货源/供应商”“按价格、销量、工厂或代发筛选” | `linkfox-dld-product-search` | 只看历史热销排名用 `linkfox-dld-product-billboard`；已有商品 ID/URL 要核验详情用 `linkfox-1688-product-detail` |
| “用这张图找1688同款/相似货源” | `linkfox-1688-search-by-image` | 只有文字关键词时用 `linkfox-dld-product-search`；只想看热销趋势时用榜单 |
| “1688热销榜/爆款/周榜/月榜/趋势商品” | `linkfox-dld-product-billboard` | 需要近7/30天实时筛选或更偏供应商条件时用 `linkfox-dld-product-search` |
| “查这个1688链接/offerId的SKU、价格、库存、MOQ、包装或供应商” | `linkfox-1688-product-detail` | 还没有确定商品时先用关键词、图片或榜单发现；一次只查一个 offerId |
| “查一批商品 ID 的价格或销量对比” | `linkfox-dld-product-search` 的 `productIds` | 需要每个商品的 SKU、阶梯价、件重尺或证书时逐个使用商品详情；详情每个 offerId 单独调用 |
| “我有本地图片” | 先调用 `oss/file/presignedPut`，再运行 `scripts/upload_image.py`，最后调用图片找货 | 已有公开 png/jpg/jpeg URL 时直接调用；不把本地路径直接传给 imageSearch |
| “需要采购价/利润判断” | 商品详情，分开呈现 CNY 与请求币种 | 搜索或榜单价格只能用于初筛；缺失 `retailPrice` 不得用其他字段补齐 |

选择时先判断输入形态（图片、中文关键词、榜单时间、已知 ID/URL），再判断目标是发现、排名还是核验；同样满足时优先使用请求更窄、返回字段更贴合且调用次数更少的方式。需要同时看图片相似度与关键词结果时，先用图片搜索，再用返回的 `offerId` 做详情核验，不要把不同结果臆造为同一商品。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 精确 `toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-1688-search-by-image` | 以图找1688同款/相似货源 | `references/linkfox-1688-search-by-image.md` | `alibaba1688/imageSearch` | 无 |
| `linkfox-1688-search-by-image` | 本地图片上传为公开 URL | `references/linkfox-1688-search-by-image.md` | `oss/file/presignedPut` | `scripts/upload_image.py` 仅 PUT 预签名 URL |
| `linkfox-1688-product-detail` | 已知 offerId/URL 的商品详情与采购条款 | `references/linkfox-1688-product-detail.md` | `alibaba1688/productDetail` | 无 |
| `linkfox-dld-product-billboard` | 1688周榜/月榜与热销商品发现 | `references/linkfox-dld-product-billboard.md` | `dld/productBillboard` | 无 |
| `linkfox-dld-product-search` | 1688关键词、商品 ID/URL 与供应商条件搜索 | `references/linkfox-dld-product-search.md` | `dld/productSearch` | 无 |
## MCP 调用方式

- **固定连接**：MCP server 为 `LinkFox`，URL 为 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，唯一工具为 `proxy_call`。
- **调用结构**：外层同时传精确 `toolName` 与 `arguments`；原业务请求对象直接作为 `arguments`，不得额外包裹 `body`、`params`、`data` 或另一层 `arguments`。
- **严格 allowlist**：仅允许 `alibaba1688/imageSearch`、`oss/file/presignedPut`、`alibaba1688/productDetail`、`dld/productBillboard`、`dld/productSearch`。值区分大小写，不得用展示名、snake_case 或 skill slug 替代。
- **自动授权**：Authorization 由 WorkBuddy 自动注入；MCP 配置和 `arguments` 禁止增加 `headers`、API key、token、JWT、手机号或其他凭证。
- **禁止直连与回退**：不得用 curl、`urllib`、`requests`、`httpx` 或其他客户端直连工具网关。MCP 或 `proxy_call` 缺失时停止，不静默回退旧脚本。
- **响应与错误**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 为 JSON 时只解析一次，再检查下游 `errcode`/`errorCode` 与 `errmsg`。
- **收费去重**：同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想均不得自动重试、自动翻页、改关键词、换图片或扩大筛选；再次调用前说明可能的积分消耗并由用户决定。
- **本地图片两阶段流程**：先以 `{"contentType":"<MIME>","fileExtension":"<ext>"}` 调用 `oss/file/presignedPut`，再把返回的预签名 URL 和本地路径传给 `scripts/upload_image.py --presigned-url`。helper 只访问预签名 OSS URL，不访问工具网关。
- **结果追溯**：保留本次 `toolName`、`arguments`、代理错误和下游响应中的状态、数量、`costToken` 等字段；不声称 MCP 自动提供旧脚本的24小时缓存、响应落盘或 stdout 摘要。
- **完整契约**：四个业务 reference 保存参数、枚举、完整响应字段、错误、成本、展示和独立 Feedback API；连接、401/402/403 分层见 `references/onboarding.md`。
## 使用示例

### 1. 按关键词找工厂货源

调用 MCP `proxy_call`（`toolName: "dld/productSearch"`）：

```json
{
  "toolName": "dld/productSearch",
  "arguments": {
    "keyWord": "蓝牙耳机",
    "cycle": "30",
    "companyType": 2,
    "beginPrice": 10,
    "endPrice": 50,
    "sortField": "saleCount30d",
    "sortType": "desc",
    "pageIndex": 1,
    "pageSize": 20
  }
}
```

重点出参是 `products[]` 中的 `offerId`、`title`、`price`、`consignPrice`、`quantityBegin`、`salesOrderCount`、`salesQuantity`、`estimatedSalesAmount`、`company`、`shopUrl` 和 `asinUrl`；按 `cycle` 标注7日或30日数据。英文关键词先翻译为中文并告知用户，`pageSize` 为10–100。

### 2. 按图片找相似货源

调用 MCP `proxy_call`（`toolName: "alibaba1688/imageSearch"`）：

```json
{
  "toolName": "alibaba1688/imageSearch",
  "arguments": {
    "imageUrl": "https://example.com/product.jpg",
    "page": 1,
    "pageSize": 20,
    "filter": "certifiedFactory,isOnePsale,shipIn24Hours",
    "sort": "{\"price\":\"asc\"}",
    "keyword": "收纳盒"
  }
}
```

重点出参是 `imageId`、`total`、`totalPage`、`products[]` 及商品图片、价格、月销量、复购率、交易分、卖家身份、发货地和代发标识。仅支持公开 png/jpg/jpeg URL；翻页优先复用首轮返回的 `imageId`，不支持的 filter/sort 不得改用其他工具绕过。

### 3. 查看热销榜单

调用 MCP `proxy_call`（`toolName: "dld/productBillboard"`）查询月榜：

```json
{
  "toolName": "dld/productBillboard",
  "arguments": {
    "keyWord": "手机壳",
    "pageType": 3,
    "date": "2026-08-01",
    "sortField": "orderCount",
    "sortType": "desc",
    "pageIndex": 1,
    "pageSize": 20,
    "companyType": 2,
    "offerType": 4
  }
}
```

重点出参是 `total`、`products[]` 的商品标题、批发/代发价、订单数、销售件数、预估销售额、上架时间、店铺链接和商品链接；按返回 `dataType` 区分 `weeklyData` 与 `monthlyData`。周榜日期必须为周日，月榜日期必须为1日，并受数据窗口限制。

### 4. 核验已知商品的采购细节

调用 MCP `proxy_call`（`toolName: "alibaba1688/productDetail"`）：

```json
{
  "toolName": "alibaba1688/productDetail",
  "arguments": {
    "offerId": "1040473674152",
    "currency": "USD"
  }
}
```

展示 `subject`、SKU 属性/库存、`retailPrice`（1件零售价）、`price` 与 `saleInfo.priceRanges`（2件及以上批发语义）、外币对应字段、MOQ、混批、发货地、件重尺、供应商服务分、发票和证书。涉及价格或利润时说明数据时点并取得用户确认后查询；`retailPrice` 缺失必须原样标为未知，不能用 `price`、`consignPrice` 或促销字段替代。

### 5. 本地图片到以图找货

先确认用户同意上传图片，根据扩展名确定 MIME，然后取得预签名 URL：

```json
{
  "toolName": "oss/file/presignedPut",
  "arguments": {
    "contentType": "image/jpeg",
    "fileExtension": "jpg"
  }
}
```

确认下游 `errcode=200` 且存在 `url` 后，仅对该预签名 URL 执行本地上传：

```bash
python scripts/upload_image.py "C:\素材\product.jpg" --presigned-url "<proxy_call 返回的 url>"
```

helper 输出不带查询参数的公开 `url`。再把该 URL 作为 `alibaba1688/imageSearch` 的 `arguments.imageUrl`；任一步失败都停止，不自动重复上传或搜索。
## 展示规则

1. **先交代检索上下文**：说明使用的关键词（如发生翻译，写出原词和中文词）、图片 URL/页码、榜单类型与日期、商品 ID/币种，以及数据是实时搜索还是周/月统计。
2. **搜索与榜单用表格**：至少展示商品图（有则显示）、标题、`offerId`、批发价、代发价、起批量、销量/订单/预估销售额、发货时间、供应商/店铺、商品链接和店铺链接；价格始终标注 CNY/RMB 及批发或代发语义。
3. **以图结果要展示识别信息**：有 `imageUrl` 时内联图片，显示 `total`、当前页/总页数、卖家身份、商品标签、复购率、体验分、发货地和一件代发标识；有下一页时提示用户可继续，但不自行翻页。
4. **销量要注明周期**：关键词搜索按 `cycle` 标明近7日或近30日；榜单按 `dataType` 标明周数据/月数据。预估销售额必须标为估算值，不能表述为实际收入。
5. **详情用 SKU 表格**：先显示标题和 `offerId`，再按规格显示库存、1件零售价、2件及以上批发价、请求币种价格和代发价；人民币与外币分列。补充 MOQ、单位、混批、包邮/代发、发货地、发货保障、包装尺寸重量、服务指标、促销、发票和证书。
6. **保留缺失与原始事实**：上游未返回字段显示“未提供/未知”，不把缺失解释为否、0、无库存或无证书；不把卖家评分推导为质量承诺，不渲染详情 HTML。
7. **分页与错误可行动**：总数超过当前页时告知总量并提示可请求下一页；错误时展示 `errcode/errorCode` 和 `errmsg` 的可理解摘要，建议检查中文关键词、日期、ID、图片格式或筛选范围，不静默改参数重试。
8. **禁止越界结论**：不把搜索排名当作质量认证、销量当作保证，不给出物流成本、成交价、侵权或合规结论；商品链接只作为导航，不代表平台已授权购买。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`，严格区分错误层级：

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提供固定 MCP 配置并提示重启或重载客户端；禁止 HTTP fallback。
- **MCP 连接 401**：检查 WorkBuddy 登录与自动授权连接，重新登录/重载，仍失败时联系 WorkBuddy 管理员；不得要求用户填写 Authorization。
- **代理成功但下游 401**：保留下游 `errcode/errorCode` 与 `errmsg`，按自动授权或业务认证异常处理；不得把 key 放进 `arguments`。
- **下游 402 或积分不足**：引导用户访问 `https://agent.linkfox.com/` 查看余额、套餐与充值；不得代用户选套餐、下单、支付或轮询。
- **下游 403**：按权限不足单独处理，不归类为认证或充值问题。
- **其他错误**：透传下游状态和消息，按对应 reference 核对参数；任何再次收费调用都先取得用户确认。
## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
