---
name: linkfox-wb-amazon-sp-api
display_name: LinkFox 亚马逊SP-API
display_name_en: LinkFox Amazon SP-API
description: 面向亚马逊卖家后台的统一 SP-API 能力，支持店铺授权、商品与目录、定价、订单、报告、Feeds、客户反馈、A+ 内容以及 FBA、入库、出库和外部履约管理。
description_zh: 当用户需要授权或选择亚马逊店铺、查询或维护 Listings、目录、价格、订单、报告、客户反馈、A+ 内容，或执行库存、Feeds、FBA、入库、出库、面单、发票、退货及外部履约操作时使用。通过 sellerId 与 region 调用对应 Amazon SP-API；支持只读查询、异步任务跟踪和经过明确确认的写操作。完整参数、响应、限制和错误处理见 references/，通过 LinkFox MCP 执行。
description_en: Unified Amazon seller-backend SP-API operations for store authorization, catalog and listings, pricing, orders, reports, feeds, customer feedback, A+ content, FBA, inbound, outbound, and external fulfillment. Use when the user asks to authorize or select a seller store, inspect or change marketplace data, retrieve reports, or run fulfillment workflows. Calls use sellerId and region, support read and asynchronous workflows, and require explicit confirmation for destructive or committing writes. See references/ for full contracts and MCP routing.
icon: icons/logo.png
version: 1.2.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox 亚马逊SP-API（LinkFox Amazon SP-API）

为亚马逊卖家提供统一的店铺后台操作入口：先确定已授权店铺与站点，再按业务目标选择查询、报告、内容管理、订单处理或履约 operation，最后通过 LinkFox MCP 执行并审计结果。当前覆盖 14 个业务子能力、205 个路由；完整契约按子能力归档在 `references/`。

## 能力边界

### 能力范围

- **店铺授权与选择**：生成 Amazon 授权链接、列出已授权店铺、刷新授权状态、检查令牌状态和本地解绑；使用 `linkfox-amazon-store-auth` 的 `spApi/authorizeUrl`、`spApi/authorizedStores`、`spApi/refreshToken`、`spApi/storeTokens`、`spApi/cancelAuthorization`。
- **报告与运营数据**：按 Seller、区域、站点和报告类型创建报告、轮询、下载、解压并返回本地文件信息；使用 `linkfox-amazon-store-report` 的 MCP 报告流程；最终预签名 URL 由 `scripts/get_report.py` 下载和解压。
- **Listings 与商品目录**：读取、搜索、部分更新、全量更新或删除刊登，读取刊登限制和 product type 定义；使用 `linkfox-amazon-store-listings` 的 Listings/Definitions API。目录检索、类目和 ASIN 详情使用 `linkfox-amazon-store-catalog`。
- **价格与竞争报价**：获取商品价格、竞争价格、Listing/Item offers、批量 offers、Featured Offer 预期价格和竞争摘要；使用 `linkfox-amazon-store-pricing`，批量请求遵守各 operation 的条数上限。
- **订单与受限信息**：搜索订单、读取订单聚合信息、买家/地址/行项目兼容接口、受监管订单信息、确认发货、更新发货状态和验证状态；使用 `linkfox-amazon-store-orders`，PII/RDT 与弃用接口按 reference 处理。
- **Feeds 与文件上传**：创建上传目的地或 Feed 文档、上传文件、创建/查询/取消 Feed、下载处理结果；使用 `linkfox-amazon-store-feeds` 与 `linkfox-amazon-store-uploads`。预签名 URL 上传/下载不经过 `developerProxy`。
- **客户反馈洞察**：读取商品或 Browse Node 的评论主题、评论趋势、退货主题与退货趋势，以及商品 Browse Node；使用 `linkfox-amazon-store-customer-feedback`。
- **外部履约**：同步库存、查询/确认发货、创建和更新包裹、查询运输选项、生成或读取发票与面单、查询退货；使用 `linkfox-amazon-store-external-fulfillment`。库存更新是绝对值，不是增量。
- **FBA 与入库/出库**：覆盖 FBA eligibility、库存、旧版入库/出库、Fulfillment Inbound v2024-03-20 全流程，以及 Fulfillment Outbound v2026-07-04 的报价、预览、下单、更新、取消和包裹状态；分别使用 `linkfox-amazon-store-fba`、`linkfox-amazon-store-fulfillment-inbound`、`linkfox-amazon-store-fulfillment-outbound`。
- **A+ 内容**：搜索、创建、读取、更新 A+ 文档，校验或替换 ASIN 关联，查询发布记录，提交审核或暂停展示；使用 `linkfox-amazon-store-aplus-content`。

### 边界与限制

- 所有卖家后台 operation 都必须以已授权的 `sellerId` 和 `region`（`NA`、`EU`、`FE`）为上下文；没有明确店铺时先列出授权店铺并让用户选择，不猜测店铺或站点。
- 不读取、展示、传递或让用户填写 Amazon raw `accessToken` / `refreshToken`；`storeTokens` 只用于状态确认，下游统一由服务端按 `sellerId + region` 解析授权。
- 写入、删除、取消、提交审核、确认运输/装箱/发货等可能改变店铺或履约状态的操作，执行前必须取得用户对目标店铺、资源和动作的明确确认；Inbound/Outbound 文档规定的提交操作还必须传 `confirmWrite: true`。
- 只读查询不能替代 Amazon Seller Central 的人工审核、税务/法律判断、库存盘点或订单履约承诺；受限 PII 只按 Amazon 权限和 RDT 规则展示。
- 不提供 Amazon 账号注册、授权申请审核、Listing 文案策略、广告投放、价格策略、法律意见、物流承运商谈判或与 Amazon/买家的直接沟通；不绕过接口白名单、权限、沙箱限制或数据保护政策。
- 不擅自自动翻页、重试、改参数、重复提交 POST/PUT/PATCH/DELETE 或高频轮询。异步 operation 返回 `operationId` 时，按对应 reference 查询状态；`IN_PROGRESS` 停止并告知用户稍后再查，`FAILED` 先展示问题，不进入后续写步骤。
- 报告、Feed、面单、发票和 A+ 内容可能返回预签名 URL、压缩文件、Base64 或临时本机链接；必须标注有效期和可用范围，不把大字段反复贴入上下文。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 授权、列出店铺、刷新或查看授权状态 | `linkfox-amazon-store-auth` | 没有授权上下文时先完成店铺选择；不要用 `storeTokens` 获取 raw token |
| 查报告、下载订单/销售/库存/财务文件 | `linkfox-amazon-store-report` | 需要实时订单对象用 Orders；需要库存绝对值同步用 External Fulfillment 或写入 Feed |
| 查或改 Listing、查限制、查 product type | `linkfox-amazon-store-listings` | 只查 ASIN 目录资料用 Catalog；只查报价/竞争价用 Pricing |
| 查 ASIN、目录属性或 Browse Node 类目 | `linkfox-amazon-store-catalog` | 需要 Listing 级 SKU 数据用 Listings；需要评论主题/趋势用 Customer Feedback |
| 查当前价格、报价、竞争价格或 Featured Offer | `linkfox-amazon-store-pricing` | 需要修改刊登价格/属性时使用 Listings 的写操作，并先确认 |
| 搜索订单、查履约信息、确认发货或受监管订单 | `linkfox-amazon-store-orders` | Amazon MCF 新版出库流程用 Fulfillment Outbound；FBA 旧版出库用 FBA |
| 批量提交库存/Listing/其他 Feed 文件 | `linkfox-amazon-store-feeds` | 只需为任意资源创建上传目的地用 Uploads；不要把 Feed 结果当实时订单数据 |
| 创建上传目的地或直接上传资源文件 | `linkfox-amazon-store-uploads` | Feed 文件仍需按 Feeds 的 create/upload/create 流程提交 |
| 评论/退货主题、趋势或商品 Browse Node | `linkfox-amazon-store-customer-feedback` | 需要原始订单或退货对象用 Orders/FBA/履约能力 |
| MFN/外部履约库存、发货、包裹、发票、面单、退货 | `linkfox-amazon-store-external-fulfillment` | 普通 Seller Orders 用 Orders；Amazon FBA 货件入库用 FBA 或 Inbound |
| FBA eligibility、FBA 库存、旧版 FBA inbound/outbound | `linkfox-amazon-store-fba` | 新建 Inbound Plan 用 Fulfillment Inbound；新版 MCF 用 Fulfillment Outbound |
| Inbound Plan、装箱、分仓、运输、货件内容、预约 | `linkfox-amazon-store-fulfillment-inbound` | 只查旧版 v0 货件/标签/BOL 可在该 reference 的 Retained v0 operation；不要混用 FBA 的同名脚本 |
| MCF 出库报价、预览、下单、订单或包裹状态 | `linkfox-amazon-store-fulfillment-outbound` | `updateOrderStatus`/`updatePackage` 仅 Amazon dynamic sandbox；旧版出库读取迁移到 FBA |
| A+ 文档、ASIN 关联、审核、暂停和发布记录 | `linkfox-amazon-store-aplus-content` | 需要普通 Listing 属性用 Listings；需要上传 A+ 资源文件先用 Uploads |

选择时先区分“资源对象”（Listing/ASIN/订单/报告/Feed/货件/包裹/A+）和“动作性质”（读取、生成预览、提交、确认、取消），再查看路由表中的 method、path、脚本和 reference。多个能力都能满足时优先选择默认推荐；涉及费用、写入或异步链路时先说明影响，让用户决定是否继续。

## 业务需求路由速查

路由表中的 `reference` 是本目录的单文件归档。除授权管理与两项预签名 PUT 外，其余 operation 均通过 `proxy_call` 的 `spApi/developerProxy` 转发；完整 query/body、响应字段、版本差异和错误码见对应 reference。

| 子能力 | 业务能力 | reference | `toolName` / 上游 operation | 本地 helper |
|---|---|---|---|---|
| `linkfox-amazon-store-auth` | authorizeUrl operation | `references/linkfox-amazon-store-auth.md` | `spApi/authorizeUrl` | — |
| `linkfox-amazon-store-auth` | authorizedStores operation | `references/linkfox-amazon-store-auth.md` | `spApi/authorizedStores` | — |
| `linkfox-amazon-store-auth` | refreshToken operation | `references/linkfox-amazon-store-auth.md` | `spApi/refreshToken` | — |
| `linkfox-amazon-store-auth` | storeTokens operation | `references/linkfox-amazon-store-auth.md` | `spApi/storeTokens` | — |
| `linkfox-amazon-store-auth` | cancelAuthorization operation | `references/linkfox-amazon-store-auth.md` | `spApi/cancelAuthorization` | — |
| `linkfox-amazon-store-report` | getReport operation | `references/linkfox-amazon-store-report.md` | `spApi/developerProxy` → POST `reports/2021-06-30/reports`; GET `reports/2021-06-30/reports/{reportId}`; GET `reports/2021-06-30/documents/{reportDocumentId}` | `scripts/get_report.py`（仅下载/解压最终 URL） |
| `linkfox-amazon-store-listings` | getListingsItem operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → GET `listings/2021-08-01/items/{sellerId}/{sku}` | — |
| `linkfox-amazon-store-listings` | searchListingsItems operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → GET `listings/2021-08-01/items/{sellerId}` | — |
| `linkfox-amazon-store-listings` | patchListingsItem operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → PATCH `listings/2021-08-01/items/{sellerId}/{sku}` | — |
| `linkfox-amazon-store-listings` | putListingsItem operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → PUT `listings/2021-08-01/items/{sellerId}/{sku}` | — |
| `linkfox-amazon-store-listings` | deleteListingsItem operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → DELETE `listings/2021-08-01/items/{sellerId}/{sku}` | — |
| `linkfox-amazon-store-listings` | getListingsRestrictions operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → GET `listings/2021-08-01/restrictions` | — |
| `linkfox-amazon-store-listings` | searchDefinitionsProductTypes operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → GET `definitions/2020-09-01/productTypes` | — |
| `linkfox-amazon-store-listings` | getDefinitionsProductType operation | `references/linkfox-amazon-store-listings.md` | `spApi/developerProxy` → GET `definitions/2020-09-01/productTypes/{productType}` | — |
| `linkfox-amazon-store-pricing` | getPricing operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → GET `products/pricing/v0/price` | — |
| `linkfox-amazon-store-pricing` | getCompetitivePricing operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → GET `products/pricing/v0/competitivePrice` | — |
| `linkfox-amazon-store-pricing` | getListingOffers operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → GET `products/pricing/v0/listings/{SellerSKU}/offers` | — |
| `linkfox-amazon-store-pricing` | getItemOffers operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → GET `products/pricing/v0/items/{ASIN}/offers` | — |
| `linkfox-amazon-store-pricing` | getItemOffersBatch operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → POST `batches/products/pricing/v0/itemOffers` | — |
| `linkfox-amazon-store-pricing` | getListingOffersBatch operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → POST `batches/products/pricing/v0/listingOffers` | — |
| `linkfox-amazon-store-pricing` | getFeaturedOfferExpectedPriceBatch operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → POST `batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice` | — |
| `linkfox-amazon-store-pricing` | getCompetitiveSummary operation | `references/linkfox-amazon-store-pricing.md` | `spApi/developerProxy` → POST `batches/products/pricing/2022-05-01/items/competitiveSummary` | — |
| `linkfox-amazon-store-orders` | searchOrders operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/2026-01-01/orders` | — |
| `linkfox-amazon-store-orders` | getOrder operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/2026-01-01/orders/{orderId}` | — |
| `linkfox-amazon-store-orders` | getOrderBuyerInfo operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/v0/orders/{orderId}/buyerInfo` | — |
| `linkfox-amazon-store-orders` | getOrderAddress operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/v0/orders/{orderId}/address` | — |
| `linkfox-amazon-store-orders` | getOrderItems operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/v0/orders/{orderId}/orderItems` | — |
| `linkfox-amazon-store-orders` | getOrderItemsBuyerInfo operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/v0/orders/{orderId}/orderItems/buyerInfo` | — |
| `linkfox-amazon-store-orders` | updateShipmentStatus operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → POST `orders/v0/orders/{orderId}/shipment` | — |
| `linkfox-amazon-store-orders` | getOrderRegulatedInfo operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → GET `orders/v0/orders/{orderId}/regulatedInfo` | — |
| `linkfox-amazon-store-orders` | updateVerificationStatus operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → PATCH `orders/v0/orders/{orderId}/regulatedInfo` | — |
| `linkfox-amazon-store-orders` | confirmShipment operation | `references/linkfox-amazon-store-orders.md` | `spApi/developerProxy` → POST `orders/v0/orders/{orderId}/shipmentConfirmation` | — |
| `linkfox-amazon-store-feeds` | createFeedDocument operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → POST `feeds/2021-06-30/documents` | — |
| `linkfox-amazon-store-feeds` | getFeedDocument operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → GET `feeds/2021-06-30/documents/{feedDocumentId}` | — |
| `linkfox-amazon-store-feeds` | createFeed operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → POST `feeds/2021-06-30/feeds` | — |
| `linkfox-amazon-store-feeds` | getFeed operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → GET `feeds/2021-06-30/feeds/{feedId}` | — |
| `linkfox-amazon-store-feeds` | getFeeds operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → GET `feeds/2021-06-30/feeds` | — |
| `linkfox-amazon-store-feeds` | cancelFeed operation | `references/linkfox-amazon-store-feeds.md` | `spApi/developerProxy` → DELETE `feeds/2021-06-30/feeds/{feedId}` | — |
| `linkfox-amazon-store-feeds` | uploadFeedDocument operation | `references/linkfox-amazon-store-feeds.md` | 预签名 URL PUT（非 MCP） | `scripts/upload_feed_document.py` |
| `linkfox-amazon-store-catalog` | listCatalogCategories operation | `references/linkfox-amazon-store-catalog.md` | `spApi/developerProxy` → GET `catalog/v0/categories` | — |
| `linkfox-amazon-store-catalog` | searchCatalogItems operation | `references/linkfox-amazon-store-catalog.md` | `spApi/developerProxy` → GET `catalog/{2022-04-01\|2020-12-01}/items` | — |
| `linkfox-amazon-store-catalog` | getCatalogItem operation | `references/linkfox-amazon-store-catalog.md` | `spApi/developerProxy` → GET `catalog/{2022-04-01\|2020-12-01}/items/{asin}` | — |
| `linkfox-amazon-store-customer-feedback` | getItemReviewTopics operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/items/{asin}/reviews/topics` | — |
| `linkfox-amazon-store-customer-feedback` | getItemBrowseNode operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/items/{asin}/browseNode` | — |
| `linkfox-amazon-store-customer-feedback` | getItemReviewTrends operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/items/{asin}/reviews/trends` | — |
| `linkfox-amazon-store-customer-feedback` | getBrowseNodeReviewTopics operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics` | — |
| `linkfox-amazon-store-customer-feedback` | getBrowseNodeReviewTrends operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends` | — |
| `linkfox-amazon-store-customer-feedback` | getBrowseNodeReturnTopics operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics` | — |
| `linkfox-amazon-store-customer-feedback` | getBrowseNodeReturnTrends operation | `references/linkfox-amazon-store-customer-feedback.md` | `spApi/developerProxy` → GET `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends` | — |
| `linkfox-amazon-store-uploads` | createUploadDestinationForResource operation | `references/linkfox-amazon-store-uploads.md` | `spApi/developerProxy` → POST `uploads/2020-11-01/uploadDestinations/{resource}` | — |
| `linkfox-amazon-store-uploads` | uploadToDestination operation | `references/linkfox-amazon-store-uploads.md` | 预签名 URL PUT（非 MCP） | `scripts/upload_to_destination.py` |
| `linkfox-amazon-store-external-fulfillment` | batchInventory operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → POST `externalFulfillment/inventory/2024-09-11/inventories` | — |
| `linkfox-amazon-store-external-fulfillment` | getShipments operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/shipments` | — |
| `linkfox-amazon-store-external-fulfillment` | getShipment operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/shipments/{shipmentId}` | — |
| `linkfox-amazon-store-external-fulfillment` | processShipment operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → POST `externalFulfillment/2024-09-11/shipments/{shipmentId}?operation={operation}` | — |
| `linkfox-amazon-store-external-fulfillment` | createPackages operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → POST `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages` | — |
| `linkfox-amazon-store-external-fulfillment` | updatePackage operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → PUT `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}` | — |
| `linkfox-amazon-store-external-fulfillment` | updatePackageStatus operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → PATCH `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}` | — |
| `linkfox-amazon-store-external-fulfillment` | retrieveShippingOptions operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/shipments/{shipmentId}/shippingOptions` | — |
| `linkfox-amazon-store-external-fulfillment` | generateInvoice operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → POST `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice` | — |
| `linkfox-amazon-store-external-fulfillment` | retrieveInvoice operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice` | — |
| `linkfox-amazon-store-external-fulfillment` | generateShipLabels operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → PUT `externalFulfillment/2024-09-11/shipments/{shipmentId}/shipLabels?operation={operation}` | — |
| `linkfox-amazon-store-external-fulfillment` | listReturns operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/returns` | — |
| `linkfox-amazon-store-external-fulfillment` | getReturn operation | `references/linkfox-amazon-store-external-fulfillment.md` | `spApi/developerProxy` → GET `externalFulfillment/2024-09-11/returns/{returnId}` | — |
| `linkfox-amazon-store-fba` | getItemEligibilityPreview operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v1/eligibility/itemPreview` | — |
| `linkfox-amazon-store-fba` | getInventorySummaries operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inventory/v1/summaries` | — |
| `linkfox-amazon-store-fba` | createInventoryItem operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `fba/inventory/v1/items` | — |
| `linkfox-amazon-store-fba` | deleteInventoryItem operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → DELETE `fba/inventory/v1/items/{sellerSku}` | — |
| `linkfox-amazon-store-fba` | addInventory operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `fba/inventory/v1/items/inventory` | — |
| `linkfox-amazon-store-fba` | getPrepInstructions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/prepInstructions` | — |
| `linkfox-amazon-store-fba` | getLabels operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/labels` | — |
| `linkfox-amazon-store-fba` | getBillOfLading operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/billOfLading` | — |
| `linkfox-amazon-store-fba` | getShipmentsV0 operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments` | — |
| `linkfox-amazon-store-fba` | getShipmentItemsByShipmentId operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/items` | — |
| `linkfox-amazon-store-fba` | getShipmentItems operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipmentItems` | — |
| `linkfox-amazon-store-fba` | listInboundPlans operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans` | — |
| `linkfox-amazon-store-fba` | createInboundPlan operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans` | — |
| `linkfox-amazon-store-fba` | getInboundPlan operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | — |
| `linkfox-amazon-store-fba` | listInboundPlanBoxes operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | — |
| `linkfox-amazon-store-fba` | cancelInboundPlan operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | — |
| `linkfox-amazon-store-fba` | listInboundPlanItems operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | — |
| `linkfox-amazon-store-fba` | updateInboundPlanName operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | — |
| `linkfox-amazon-store-fba` | listPackingGroupBoxes operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | — |
| `linkfox-amazon-store-fba` | listPackingGroupItems operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | — |
| `linkfox-amazon-store-fba` | setPackingInformation operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | — |
| `linkfox-amazon-store-fba` | listPackingOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | — |
| `linkfox-amazon-store-fba` | generatePackingOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | — |
| `linkfox-amazon-store-fba` | confirmPackingOption operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | — |
| `linkfox-amazon-store-fba` | listInboundPlanPallets operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | — |
| `linkfox-amazon-store-fba` | listPlacementOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | — |
| `linkfox-amazon-store-fba` | generatePlacementOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | — |
| `linkfox-amazon-store-fba` | confirmPlacementOption operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | — |
| `linkfox-amazon-store-fba` | getShipment operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | — |
| `linkfox-amazon-store-fba` | listShipmentBoxes operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | — |
| `linkfox-amazon-store-fba` | listShipmentContentUpdatePreviews operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | — |
| `linkfox-amazon-store-fba` | generateShipmentContentUpdatePreviews operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | — |
| `linkfox-amazon-store-fba` | getShipmentContentUpdatePreview operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | — |
| `linkfox-amazon-store-fba` | confirmShipmentContentUpdatePreview operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | — |
| `linkfox-amazon-store-fba` | getDeliveryChallanDocument operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | — |
| `linkfox-amazon-store-fba` | listDeliveryWindowOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | — |
| `linkfox-amazon-store-fba` | generateDeliveryWindowOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | — |
| `linkfox-amazon-store-fba` | confirmDeliveryWindowOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | — |
| `linkfox-amazon-store-fba` | listShipmentItems operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | — |
| `linkfox-amazon-store-fba` | updateShipmentName operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | — |
| `linkfox-amazon-store-fba` | listShipmentPallets operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | — |
| `linkfox-amazon-store-fba` | cancelSelfShipAppointment operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | — |
| `linkfox-amazon-store-fba` | getSelfShipAppointmentSlots operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | — |
| `linkfox-amazon-store-fba` | generateSelfShipAppointmentSlots operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | — |
| `linkfox-amazon-store-fba` | scheduleSelfShipAppointment operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | — |
| `linkfox-amazon-store-fba` | updateShipmentSourceAddress operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | — |
| `linkfox-amazon-store-fba` | updateShipmentTrackingDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | — |
| `linkfox-amazon-store-fba` | listTransportationOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | — |
| `linkfox-amazon-store-fba` | generateTransportationOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | — |
| `linkfox-amazon-store-fba` | confirmTransportationOptions operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | — |
| `linkfox-amazon-store-fba` | listItemComplianceDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/items/compliance` | — |
| `linkfox-amazon-store-fba` | updateItemComplianceDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/items/compliance` | — |
| `linkfox-amazon-store-fba` | createMarketplaceItemLabels operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/items/labels` | — |
| `linkfox-amazon-store-fba` | listPrepDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/items/prepDetails` | — |
| `linkfox-amazon-store-fba` | setPrepDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/items/prepDetails` | — |
| `linkfox-amazon-store-fba` | getInboundOperationStatus operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/operations/{operationId}` | — |
| `linkfox-amazon-store-fba` | getFulfillmentPreview operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `fba/outbound/2020-07-01/fulfillmentOrders/preview` | — |
| `linkfox-amazon-store-fba` | deliveryOffers operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `fba/outbound/2020-07-01/deliveryOffers` | — |
| `linkfox-amazon-store-fba` | listAllFulfillmentOrders operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/fulfillmentOrders` | — |
| `linkfox-amazon-store-fba` | createFulfillmentOrder operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → POST `fba/outbound/2020-07-01/fulfillmentOrders` | — |
| `linkfox-amazon-store-fba` | getPackageTrackingDetails operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/tracking` | — |
| `linkfox-amazon-store-fba` | listReturnReasonCodes operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/returnReasonCodes` | — |
| `linkfox-amazon-store-fba` | createFulfillmentReturn operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return` | — |
| `linkfox-amazon-store-fba` | getFulfillmentOrder operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | — |
| `linkfox-amazon-store-fba` | updateFulfillmentOrder operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | — |
| `linkfox-amazon-store-fba` | cancelFulfillmentOrder operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel` | — |
| `linkfox-amazon-store-fba` | submitFulfillmentOrderStatusUpdate operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → PUT `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status` | — |
| `linkfox-amazon-store-fba` | getFeatures operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/features` | — |
| `linkfox-amazon-store-fba` | getFeatureInventory operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/features/inventory/{featureName}` | — |
| `linkfox-amazon-store-fba` | getFeatureSKU operation | `references/linkfox-amazon-store-fba.md` | `spApi/developerProxy` → GET `fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listInboundPlans operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans` | — |
| `linkfox-amazon-store-fulfillment-inbound` | createInboundPlan operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getInboundPlan operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listInboundPlanBoxes operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | — |
| `linkfox-amazon-store-fulfillment-inbound` | cancelInboundPlan operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listInboundPlanItems operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | — |
| `linkfox-amazon-store-fulfillment-inbound` | updateInboundPlanName operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listPackingGroupBoxes operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listPackingGroupItems operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | — |
| `linkfox-amazon-store-fulfillment-inbound` | setPackingInformation operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listPackingOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generatePackingOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | confirmPackingOption operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listInboundPlanPallets operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listPlacementOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generatePlacementOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | confirmPlacementOption operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getShipment operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listShipmentBoxes operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listShipmentContentUpdatePreviews operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generateShipmentContentUpdatePreviews operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getShipmentContentUpdatePreview operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | — |
| `linkfox-amazon-store-fulfillment-inbound` | confirmShipmentContentUpdatePreview operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getDeliveryChallanDocument operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listDeliveryWindowOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generateDeliveryWindowOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | confirmDeliveryWindowOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listShipmentItems operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | — |
| `linkfox-amazon-store-fulfillment-inbound` | updateShipmentName operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listShipmentPallets operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | — |
| `linkfox-amazon-store-fulfillment-inbound` | cancelSelfShipAppointment operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getSelfShipAppointmentSlots operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generateSelfShipAppointmentSlots operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | — |
| `linkfox-amazon-store-fulfillment-inbound` | scheduleSelfShipAppointment operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | — |
| `linkfox-amazon-store-fulfillment-inbound` | updateShipmentSourceAddress operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | — |
| `linkfox-amazon-store-fulfillment-inbound` | updateShipmentTrackingDetails operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listTransportationOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | generateTransportationOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | confirmTransportationOptions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listItemComplianceDetails operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/items/compliance` | — |
| `linkfox-amazon-store-fulfillment-inbound` | updateItemComplianceDetails operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → PUT `inbound/fba/2024-03-20/items/compliance` | — |
| `linkfox-amazon-store-fulfillment-inbound` | createMarketplaceItemLabels operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/items/labels` | — |
| `linkfox-amazon-store-fulfillment-inbound` | listPrepDetails operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/items/prepDetails` | — |
| `linkfox-amazon-store-fulfillment-inbound` | setPrepDetails operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → POST `inbound/fba/2024-03-20/items/prepDetails` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getInboundOperationStatus operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `inbound/fba/2024-03-20/operations/{operationId}` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getPrepInstructions operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/prepInstructions` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getLabels operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/labels` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getBillOfLading operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/billOfLading` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getShipments operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getShipmentItemsByShipmentId operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipments/{shipmentId}/items` | — |
| `linkfox-amazon-store-fulfillment-inbound` | getShipmentItems operation | `references/linkfox-amazon-store-fulfillment-inbound.md` | `spApi/developerProxy` → GET `fba/inbound/v0/shipmentItems` | — |
| `linkfox-amazon-store-fulfillment-outbound` | getOrderPreview operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → POST `fulfillment/outbound/2026-07-04/previews` | — |
| `linkfox-amazon-store-fulfillment-outbound` | getOffers operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → POST `fulfillment/outbound/2026-07-04/offers` | — |
| `linkfox-amazon-store-fulfillment-outbound` | createOrder operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → POST `fulfillment/outbound/2026-07-04/orders` | — |
| `linkfox-amazon-store-fulfillment-outbound` | listOrders operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → GET `fulfillment/outbound/2026-07-04/orders` | — |
| `linkfox-amazon-store-fulfillment-outbound` | getOrder operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → GET `fulfillment/outbound/2026-07-04/orders/{orderId}` | — |
| `linkfox-amazon-store-fulfillment-outbound` | updateOrder operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → PUT `fulfillment/outbound/2026-07-04/orders/{orderId}` | — |
| `linkfox-amazon-store-fulfillment-outbound` | cancelOrder operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → PUT `fulfillment/outbound/2026-07-04/orders/{orderId}/cancel` | — |
| `linkfox-amazon-store-fulfillment-outbound` | updateOrderStatus operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → PUT `fulfillment/outbound/2026-07-04/orders/{orderId}/status` | — |
| `linkfox-amazon-store-fulfillment-outbound` | updatePackage operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → PUT `fulfillment/outbound/2026-07-04/orders/{orderId}/packages/{packageId}` | — |
| `linkfox-amazon-store-fulfillment-outbound` | getInvoiceHeaders operation | `references/linkfox-amazon-store-fulfillment-outbound.md` | `spApi/developerProxy` → GET `finances/invoices/2026-06-25/invoices` | — |
| `linkfox-amazon-store-aplus-content` | searchContentDocuments operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → GET `aplus/2020-11-01/contentDocuments` | — |
| `linkfox-amazon-store-aplus-content` | createContentDocument operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentDocuments` | — |
| `linkfox-amazon-store-aplus-content` | getContentDocument operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → GET `aplus/2020-11-01/contentDocuments/{contentReferenceKey}` | — |
| `linkfox-amazon-store-aplus-content` | updateContentDocument operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentDocuments/{contentReferenceKey}` | — |
| `linkfox-amazon-store-aplus-content` | listContentDocumentAsinRelations operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → GET `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` | — |
| `linkfox-amazon-store-aplus-content` | postContentDocumentAsinRelations operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` | — |
| `linkfox-amazon-store-aplus-content` | validateContentDocumentAsinRelations operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentAsinValidations` | — |
| `linkfox-amazon-store-aplus-content` | searchContentPublishRecords operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → GET `aplus/2020-11-01/contentPublishRecords` | — |
| `linkfox-amazon-store-aplus-content` | postContentDocumentApprovalSubmission operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions` | — |
| `linkfox-amazon-store-aplus-content` | postContentDocumentSuspendSubmission operation | `references/linkfox-amazon-store-aplus-content.md` | `spApi/developerProxy` → POST `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions` | — |

## MCP 调用方式

MCP server 为 `LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`），唯一工具为 `proxy_call`。允许的精确 `toolName`：

- `spApi/authorizeUrl`
- `spApi/authorizedStores`
- `spApi/refreshToken`
- `spApi/storeTokens`
- `spApi/cancelAuthorization`
- `spApi/developerProxy`

```json
{"toolName":"spApi/developerProxy","arguments":{"sellerId":"A1234567890","region":"NA","path":"listings/2021-08-01/items/A1234567890/SKU-001","method":"GET","queryString":"marketplaceIds=ATVPDKIKX0DER"}}
```

WorkBuddy 自动注入 Authorization。`toolName` 精确匹配并区分大小写；原 developerProxy 请求对象直接作为 `arguments`，不额外包裹。禁止传网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。禁止 curl、`urllib`、`requests`、`httpx` 直连网关；MCP 缺失时不 HTTP fallback。失败、空结果或不理想时不自动重试，相同 `toolName + arguments` 不重复调用。按 MCP/schema/`isError`、代理 content、下游业务错误、业务结果顺序处理；text JSON 只解析一次。

Feed 与 Uploads 的预签名 URL PUT 不是工具网关调用，分别使用保留的本地上传 helper。报告返回的预签名下载 URL 可使用 `scripts/get_report.py` 本地下载/解压；这些 helper 不读取 LinkFox 凭证。

## 使用示例

具体 operation 的 `path`、method、query/body 和完整响应字段见对应 reference。任何写入、删除、取消、审核提交、发货、运输或装箱确认都必须先取得用户明确确认；异步状态按 reference 查询且不高频轮询。

## 展示规则

1. **先展示调用状态**：先显示网关 `errcode`、`errmsg`、`httpStatus`、request ID，再解析 `body`、operation result 或脚本附加字段；HTTP 成功不等于业务完成。
2. **标注业务状态**：报告展示 `processingStatus` 与文件路径；Feed 展示 `feedId`、`processingStatus` 和结果文档；Inbound/FBA/Outbound 展示 `operationId`、Amazon status、下一步；订单/包裹/货件展示当前状态与是否仍需确认。
3. **文件结果可用性**：报告下载 helper 只返回 `outputPath`、`bytes` 和 `httpStatus`；预签名 URL、面单和发票下载地址均需标注过期风险，不得展示预签名查询参数。
4. **大字段与敏感字段**：不要直接输出完整 Base64、原始买家地址、PII、raw token 或整份大 JSON；摘要中展示计数和前 3 条样本，需要时从落盘文件抽取脱敏字段。
5. **分页与异步**：显示是否存在 `nextToken`/`paginationToken` 和 `operationId`，不把第一页当全量，不把 `IN_PROGRESS` 当失败或完成；继续分页/轮询前说明额外调用影响并遵守 reference。
6. **写操作结果**：分别展示“网关已接受”“Amazon 已完成”“业务资源当前状态”；对 202/204/207 等无完整 body 的响应，用 `success`、status 和下一查询建议解释，不臆造已完成。
7. **Amazon 保护状态**：连续收到 Amazon 400、403、404、429 时，网关可能返回自定义 450、453、454、459。立即停止自动/并发重试，优先展示 `retryAfter`/`blockedUntil`；450 检查参数，453 检查授权，454 检查资源，459 降低频率。说明这是店铺保护冷却，不是封号或积分限制。
8. **错误可行动**：1005 指向路径白名单，401/403 检查授权和权限，400 检查必填字段/枚举/body，404 检查资源所属店铺和站点，429 遵循退避；不要通过换脚本、重复任务或改参数绕过保护。
9. **来源与不可用字段**：说明数据来自对应 Amazon SP-API operation 和调用时间；Amazon 未返回的字段标记为不可用，不用其他接口臆测补全。

## 解决认证和积分问题

- MCP/`proxy_call` 缺失：停止并提示配置后重载 WorkBuddy，不自行安装或 HTTP fallback。
- MCP 401：提示重新登录、重载连接或联系 WorkBuddy 管理员，不要求填写 Authorization。
- 代理成功但下游 401：按自动授权或下游认证失败处理，不把 Key/token 放进 `arguments`。
- 下游 402 或积分不足：引导访问 `https://agent.linkfox.com/`，不自动选套餐、下单、支付或轮询。
- 403 与其他错误按业务 reference 处理。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
