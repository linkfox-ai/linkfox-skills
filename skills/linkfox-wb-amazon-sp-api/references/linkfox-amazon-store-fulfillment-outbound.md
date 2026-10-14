# Reference archive: linkfox-amazon-store-fulfillment-outbound

本文件归档该子能力的执行说明、API 契约、参数约束、错误处理和工作流；按需阅读相关章节。

## Capability instructions


## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `spApi/developerProxy` |
| `arguments` | 直接使用本 reference 对应的网关请求对象 |

```json
{
  "toolName": "spApi/developerProxy",
  "arguments": {
    "sellerId": "A1234567890",
    "region": "NA",
    "path": "fulfillment/outbound/2026-07-04/previews",
    "method": "POST",
    "body": "<按本 reference 构造的 JSON 字符串；无请求体时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-fulfillment-outbound/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `operationId` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `method` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `resolvedPath` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `queryString` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `requestBody` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.errcode` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.httpStatus` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.contentType` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `nextAction` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-fulfillment-outbound
description: 亚马逊 Multi-Channel Fulfillment（MCF）新版出仓履约管理。用于获取配送报价和订单预览，创建、查询、列出、更新或取消履约订单，查看包裹与跟踪、签收证明、投递照片、收件人及 locker/drop-off 信息，并查询相关发票头。用户提到 Fulfillment Outbound、MCF、多渠道配送、亚马逊库存配送到站外客户、配送报价、getOffers、getOrderPreview、createOrder、getInvoiceHeaders、receivedBy、unitIdentifiers、v2026-07-04 时触发。即使未明确说“MCF API”，只要希望用亚马逊库存履约非亚马逊渠道订单，也应触发此技能；External Fulfillment、普通 Orders API 和旧版 v2020-07-01 不属于此技能。
---

# Amazon 店铺 Fulfillment Outbound

Use this Skill for Amazon Multi-Channel Fulfillment workflows on Fulfillment Outbound `v2026-07-04`. It exposes all nine operations in Amazon's current Outbound model plus the overview page's associated `getInvoiceHeaders` 操作 from Invoices `v2026-06-25`, while keeping the existing production `linkfox-amazon-store-fba` and `linkfox-amazon-store-external-fulfillment` implementations untouched.

## Prerequisites

2. Select one authorized store and obtain its `sellerId` and `region`. Accept only `NA`, `EU`, or `FE`.
4. Read `references/api.md`（见本文对应归档章节） for operation contracts and `references/workflows.md`（见本文对应归档章节） before a create, update, or cancel action.
5. After explicit user confirmation, pass boolean `confirmWrite: true` to `createOrder`, `updateOrder`, `cancelOrder`, `updateOrderStatus`, or `updatePackage`; the wrappers reject writes without it.
6. When Amazon assigned a multi-tenant service identifier, pass it only as top-level `fulfillmentServiceId` (1–40 characters). The proxy maps it to `x-amzn-fulfillment-service-id`; never put the raw header name in query or body.

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## Operation Guide

| Stage | Operation | Script | Availability |
|---|---|---|---|
| Quote | `getOffers` | `get_offers` 操作 | Production |
| Preview | `getOrderPreview` | `get_order_preview` 操作 | Production |
| Create | `createOrder` | `create_order` 操作 | Production |
| Read | `getOrder` | `amazon_store_fulfillment_outbound__get_order` 操作 | Production |
| List | `listOrders` | `list_orders` 操作 | Production |
| Release hold / update | `updateOrder` | `update_order` 操作 | Production |
| Cancel | `cancelOrder` | `cancel_order` 操作 | Production |
| Simulate order status | `updateOrderStatus` | `update_order_status` 操作 | Amazon dynamic sandbox only |
| Simulate package status | `updatePackage` | `amazon_store_fulfillment_outbound__update_package` 操作 | Amazon dynamic sandbox only |
| List invoice headers | `getInvoiceHeaders` | `get_invoice_headers` 操作 | Production, Invoices v2026-06-25 |

## Workflow Rules

1. Use `getOffers` for multi-SKU delivery options and expiration times; use `getOrderPreview` for planned shipments, fees, constraints, and fulfillability.
2. Show the chosen store, destination, line items, service tier, fees, hold/ship action, and `orderId` before `createOrder`.
3. Treat `orderId` and every `lineItemId` as seller-controlled idempotency identifiers. Never invent a replacement ID after an uncertain timeout.
4. A `createOrder` response can be HTTP 200 or 202. On 202, use the returned/requested `orderId` with `getOrder`; do not automatically poll.
5. Use `updateOrder` only to update the supported fulfillment configuration, currently the HOLD/SHIP action. Confirm before releasing a held order.
6. Confirm before `cancelOrder`. Amazon only stops fulfillment where cancellation is still possible; do not present 202 as completed cancellation.
7. Add `shipments: "INCLUDE"` to `getOrder` or `listOrders` when package and tracking details are needed.
8. Never automatically replay POST/PUT after 429, 500, 503, or a timeout. Recover with `getOrder` where possible.
9. Use `getInvoiceHeaders` only for header-level invoice discovery. Require `marketplaceId`; provide both issue-date bounds or neither, keep the range within 90 days, and page with `nextToken` only after user approval.

## Important Limitations

- `updateOrderStatus` and `updatePackage` are marked `x-amzn-api-sandbox-only: true` by Amazon. Consistent with the existing FBA skill, their wrappers use the same `spApi/developerProxy` request shape as every other operation and do not accept or send a separate `sandbox` control field. Use them only with sandbox test data; availability depends on the unified gateway/upstream route.
- The optional `x-amzn-fulfillment-service-id` multi-tenant header is exposed only through the typed top-level `fulfillmentServiceId` parameter. Raw header names, nested aliases, blank values, values over 40 characters, and newline characters are rejected before calling the gateway.
- Amazon's Outbound overview role list mentions `getInvoiceHeaders`, but its Reference path is `/finances/invoices/2026-06-25/invoices`. This Skill exposes it as an explicitly labeled related Invoices operation; it is not counted among the nine Outbound OpenAPI operations and does not accept `fulfillmentServiceId`.
- Legacy v2020-07-01 returns, features, and package-tracking operations remain in the production FBA Skill and are not copied into this current-version Skill. Read `references/migration.md`（见本文对应归档章节） when migrating.

## Display Rules

- Present Amazon data and identifiers without exposing internal tool names or access tokens.
- Separate operation success from business completion: show gateway `errcode`, Amazon `httpStatus`, order `status`, constraints, and next action.
- For offers and previews, show expiration, service tier, delivery interval, currency, price, and item constraints together.
- For orders, show `orderId`, status, line items, shipments, packages, tracking, proof of delivery, drop-off/locker details, unit identifiers, and pagination token only when present.

## User Expression

**Ask**: “Check MCF delivery options for these Amazon SKUs to this postal code.”

**Do**: use `getOffers`; do not create an order.

**Ask**: “Preview and then create this MCF order.”

**Do**: run `getOrderPreview`, present constraints and fees, obtain confirmation, then run `createOrder` once.

**Ask**: “Track my MCF order.”

**Do**: run `getOrder` with `shipments: "INCLUDE"`; do not call the legacy tracking operation.

## Feedback

Report issues with `skillName: linkfox-amazon-store-fulfillment-outbound`, operation, masked IDs, resolved path, gateway status, and Amazon response summary. Never include credentials.

## Amazon SP-API 接口保护与重试指引

同一店铺连续收到 Amazon SP-API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大店铺风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查必填字段、marketplace、ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 店铺全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该店铺调用，检查授权、权限、店铺归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属店铺/站点、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 店铺+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该店铺全部 SP-API。
- 保留已有 `reportId`、`feedId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 积分消耗规则

不消耗积分（以网关实际计费为准）。

---
*更多跨境 Skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# Fulfillment Outbound API v2026-07-04 参考

## 调用规范

- 超时：150 秒。
- 对 LinkFox 网关固定使用 POST；payload 中的 `method` 才是 Amazon GET/POST/PUT。
- 公共 CLI 参数：`sellerId`、`region`；有 body 的 operation 使用 `requestBody`。Amazon 分配多租户服务标识时，可额外传顶层 `fulfillmentServiceId`（1–40 字符），服务端仅将它映射为 `x-amzn-fulfillment-service-id`。
- `createOrder` / `updateOrder` / `cancelOrder` 需用户明确确认后传布尔值 `confirmWrite: true`。
- 禁止传入 token、原始 `path`、`method`、`queryString` 或 `body` 覆盖固定契约；禁止直接传原始 `x-amzn-fulfillment-service-id` 或把服务标识放入 query/body。


官方基线：

- [Fulfillment Outbound API](https://developer-docs.amazon.com/sp-api/docs/fulfillment-outbound-api)
- [v2026-07-04 Reference](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)
- [v2026-07-04 OpenAPI Model](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)

## Operation 契约

| Operation | Amazon method/path | 输入 | 成功状态 |
|---|---|---|---|
| `getOrderPreview` | POST `/fulfillment/outbound/2026-07-04/previews` | body | 200 |
| `getOffers` | POST `/fulfillment/outbound/2026-07-04/offers` | body | 200 |
| `createOrder` | POST `/fulfillment/outbound/2026-07-04/orders` | body | 200/202 |
| `listOrders` | GET `/fulfillment/outbound/2026-07-04/orders` | query | 200 |
| `getOrder` | GET `/fulfillment/outbound/2026-07-04/orders/{orderId}` | path/query | 200 |
| `updateOrder` | PUT `/fulfillment/outbound/2026-07-04/orders/{orderId}` | path/body | 202 |
| `cancelOrder` | PUT `/fulfillment/outbound/2026-07-04/orders/{orderId}/cancel` | path | 202 |
| `updateOrderStatus` | PUT `/fulfillment/outbound/2026-07-04/orders/{orderId}/status` | path/body | 204，沙箱专用 |
| `updatePackage` | PUT `/fulfillment/outbound/2026-07-04/orders/{orderId}/packages/{packageId}` | path/body | 204，沙箱专用 |
| `getInvoiceHeaders` | GET `/finances/invoices/2026-06-25/invoices` | query | 200，关联的 Invoices API operation |

### getOrderPreview

必填 body：

- `destination.deliveryAddress`：地址至少包含 `name`、`addressLine1`、`postalCode`、两位大写 `countryCode`。
- `lineItems[]`：每项包含 `product.productIdentifier.amazonSku` 和 `amount.value`；`amount.unit` 如提供应为 `EACHES`。

可选：`channel`、`fulfillmentConfiguration`、`origin`、`excludeEstimatedFees`、`includePaymentOnDelivery`。响应关键字段：`plannedShipments[]`、`constraints[]`。

### getOffers

必填 body：

- `origin.countryCode`
- `items[].productIdentifier.amazonSku`

Amazon 当前 schema 没有将 `OfferItem.productIdentifier` 标为 required，但空 item 无法定位 SKU；本 Skill 为避免消耗一次无效付费调用，在本地要求每个 item 提供 `productIdentifier.amazonSku`。预览、创建和报价的数组也要求至少一项。

可选 `destination` 和 `fulfillmentConfiguration`。响应关键字段为 `offerResults[]`，每项包含输入 item、`offers[]`、可能的 `constraints[]`。

### createOrder

必填 body：

- `orderId`：卖家生成的唯一订单标识。
- `destination.deliveryAddress`
- `lineItems[]`：每项包含唯一 `lineItemId`、`product.productIdentifier.amazonSku`、`amount.value`。

可选：`channel`、`origin`、`fulfillmentConfiguration`、`paymentInformation`。`fulfillmentConfiguration.action` 常见为 `SHIP` 或 `HOLD`；policy 可为 `FILL_OR_KILL`、`FILL_ALL`、`FILL_ALL_AVAILABLE`。

HTTP 200 返回 `order`；HTTP 202 返回至少 `orderId` 和 `status`。202 后通过 `getOrder` 恢复状态。

### listOrders

query 参数：

- `updatedAfter`：ISO 8601 date-time。
- `pageToken`：从上一页 `pagination.nextToken` 获取。
- `shipments`：`INCLUDE` / `EXCLUDE`。

响应关键字段：`orders[]`、`pagination.nextToken`。脚本不自动翻页。

### getOrder

- path：`orderId`，1–40 字符。
- query：可选 `shipments=INCLUDE|EXCLUDE`。
- 响应：`order`；包含状态、配置、地址、line items，选择 INCLUDE 时可包含 shipments、packages 与 tracking。

`getOrder` 的当前响应模型已承载多个旧版独立查询场景，不需要在 v2026 路径上虚构额外 operation：

- `shipments[].packages[].tracking.carrier|amazon`：承运商/Amazon 跟踪号和 URL；
- `tracking.proofOfDelivery.deliveryPhotoUrl|receivedBy`：投递照片或签收人；
- `tracking.dropOffLocation`：包括日本 locker/delivery box 等投放位置；
- `shipments[].items[].unitIdentifiers`：商品实例/序列号标识；
- 多个 `shipments` / `packages` 以及 line item 的 `cancelledAmount` / `unfulfillableAmount`：用于拆包和部分履约状态。

这些字段均由 wrapper 保留在完整响应中；仅在用户需要包裹/跟踪明细时传 `shipments: "INCLUDE"`。

### updateOrder

- path：`orderId`。
- body：`fulfillmentConfiguration`；当前模型只允许更新 action。通常用 `{"fulfillmentConfiguration":{"action":"SHIP"}}` 释放 HOLD。
- HTTP 202 表示已接受，不代表更新完成；后续用 `getOrder` 核实。

### cancelOrder

- path：`orderId`。
- 无 request body。
- HTTP 202 表示取消请求已接受；后续用 `getOrder` 核实最终状态。

### 动态沙箱操作

- `updateOrderStatus` body：`status`，允许 `PROCESSING`、`COMPLETE`、`COMPLETE_PARTIAL`、`CANCELLED`、`UNFULFILLABLE`、`INVALID`。
- `updatePackage` body：必填 `status`，可选 `deliveryTime`、`tracking`。路径直接结束于 `{packageId}`，没有额外 `/status` 段。

Amazon OpenAPI 对这两个路径显式设置 `x-amzn-api-sandbox-only: true`。按照现有 FBA Skill 的统一调用方式，wrapper 仍使用标准 `spApi/developerProxy` 请求结构，不接收也不发送单独的 `sandbox` 控制字段，不需要 Skill 专属 sandbox 配置。只能用于 sandbox 测试数据，路径是否可用由统一网关及其上游路由决定。两项写操作同样要求 `confirmWrite: true`。

### 关联的 `getInvoiceHeaders`

Amazon Outbound 概述页的“Roles for v2026-07-04”列表展示 `getInvoiceHeaders`，实际 Reference 路径为 `GET /finances/invoices/2026-06-25/invoices`，属于 **Invoices API v2026-06-25**，且不在 `fulfillmentOutbound_2026-07-04.json` 的 9 个 operation 中。本 Skill 仍按概述页提供 `get_invoice_headers` 操作，但保留真实 API 归属和路径，不把它拼接到 Outbound 路径。

query：

- `marketplaceId`：必填。
- `nextToken`：分页 token；脚本不自动翻页，Amazon 可能返回空页。
- `fromIssueDate` / `toIssueDate`：必须同时提供或同时省略，ISO 8601 date-time，范围不得超过 90 天。
- `invoicesModifiedAfter`：可选 ISO 8601 date-time。

响应关键字段为 `invoices[]`、`numOfRecords`、`nextToken`。该 operation 不定义 `x-amzn-fulfillment-service-id`，因此禁止传 `fulfillmentServiceId`。

## 响应与错误

公开脚本保留以下外层结构：

- `operationId`、`method`、`resolvedPath`
- `queryString` / `requestBody`（存在时）
- `developerProxy.errcode`、`developerProxy.httpStatus`、`developerProxy.contentType`、`developerProxy.body`
- 解析后的 operation 结果字段
- 202 时可能有 `nextAction`，但不会自动轮询

判定顺序：先检查 `errcode == 200`，再检查 Amazon `httpStatus`，最后读取解析结果。400/403/404/413/415 修正请求；429/500/503 或超时不自动重放写操作。

## MCP 示例见本文开头



面向用户应调用固定 operation 脚本，不应直接允许其覆盖上述 method/path。

## Feedback

问题反馈地址：`https://skill-api.linkfox.com/api/v1/public/feedback`。附 `skillName: linkfox-amazon-store-fulfillment-outbound`、operation、脱敏 ID、resolved path、HTTP 状态与响应摘要。

## Archived reference: migration.md

# 从 Fulfillment Outbound v2020-07-01 迁移

| v2020-07-01 | v2026-07-04 |
|---|---|
| `getFulfillmentPreview` | `getOrderPreview` |
| `deliveryOffers` | `getOffers` |
| `createFulfillmentOrder` | `createOrder` |
| `listAllFulfillmentOrders` | `listOrders` |
| `getFulfillmentOrder` | `getOrder` |
| `updateFulfillmentOrder` | `updateOrder` |
| `cancelFulfillmentOrder` | `cancelOrder` |
| `submitFulfillmentOrderStatusUpdate` | `updateOrderStatus`（沙箱专用） |

基础路径从 `/fba/outbound/2020-07-01` 改为 `/fulfillment/outbound/2026-07-04`。请求和响应字段也发生重构，例如 `sellerFulfillmentOrderId` 改为 `orderId`，商品标识使用 `amazonSku`，items/quantity 结构改为 lineItems/amount。

以下旧操作没有当前版本的一一替代：`getFeatures`、`getFeatureSKU`、`getFeatureInventory`、`createFulfillmentReturn`、`listReturnReasonCodes`。`getPackageTrackingDetails` 已迁移到 Amazon Shipment Tracking API。不要为了兼容旧调用而把这些 operation 注册到新路径。

官方迁移指南：[Fulfillment Outbound migration guide](https://developer-docs.amazon.com/sp-api/docs/fulfillment-outbound-migration-guide)。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。

## Archived reference: workflows.md

# Fulfillment Outbound 工作流

## 报价与可履约性

1. 选择 `sellerId + region`。
2. 用 `getOffers` 比较多个 SKU 的服务等级与到期时间，或用 `getOrderPreview` 获取 planned shipments、费用和 constraints。
3. 发现 constraints 时停止创建，向用户展示受影响 SKU 和 Amazon 原因。

## 创建订单

1. 固定唯一 `orderId` 和每行唯一 `lineItemId`。
2. 展示目的地址、SKU、数量、service tier、费用和 `SHIP`/`HOLD`。
3. 获得明确确认后只调用一次 `createOrder`。
4. HTTP 200 读取 `order`；HTTP 202 用 `getOrder` 后续查询，禁止自动轮询。

## HOLD 后发货

1. `getOrder` 确认订单仍可更新。
2. 展示将从 HOLD 改为 SHIP 的订单并确认。
3. 调用 `updateOrder`，body 为 `{"fulfillmentConfiguration":{"action":"SHIP"}}`。
4. 用 `getOrder` 核实状态。

## 查询、分页和跟踪

- `listOrders` 使用 `updatedAfter` 或 `pageToken`；不自动遍历全部页。
- 需要 shipments、packages、tracking 或 proof-of-delivery 数据时传 `shipments: "INCLUDE"`。
- v2026 返回的 tracking 已嵌入 order shipments；不要调用旧版 `getPackageTrackingDetails`。

`getOrder(shipments="INCLUDE")` 已覆盖当前文档中的多个用例，不是额外 operation：

- 配送跟踪：`shipments[].packages[].tracking.carrier/amazon` 的 `trackingNumber` 和 `trackingUrl`。
- 签收凭证：`tracking.proofOfDelivery.deliveryPhotoUrl` 和 `receivedBy`；这些字段只在 Amazon 实际返回时展示，不伪造图片或收件人。
- 收件/投递位置：`tracking.dropOffLocation.type/attributes`，可表示 locker、delivery box、neighbor 等。
- 分包与部分履约：按 `shipmentItemIds` 将 package 与 shipment item 对应，并分别展示 shipment/package status。
- 单件标识：`shipment.items[].unitIdentifiers` 保留 Amazon 返回的制造批号/单位标识；不将其误当成 `lineItemId`。

POD 图片 URL 和收件人信息可能涉及收件人隐私；只在用户确实请求签收凭证时展示，不记录到问题反馈中。

## 发票头查询

1. 使用 `getInvoiceHeaders`，必传 `marketplaceId`。
2. 需要按开票时间过滤时同时传 `fromIssueDate` 和 `toIssueDate`，范围不超过 90 天；需要增量同步时使用 `invoicesModifiedAfter`。
3. 展示 `invoices[]`、`numOfRecords` 和 `nextToken`；不得自动翻页。
4. 该 operation 属于 Invoices v2026-06-25，不传 `fulfillmentServiceId`，也不把路径改写到 Outbound 前缀。

## 动态沙箱

1. `updateOrderStatus` 和 `updatePackage` 只用于测试订单，先展示 sandbox 目标、order/package ID 和状态变化。
2. 用户确认后传 `confirmWrite: true`。
3. 与现有 FBA Skill 一致，wrapper 使用统一 `spApi/developerProxy`，不传额外 `sandbox` 字段；测试环境沿用 Amazon Store Skill 的网关配置。

## 区域和特殊履约配置

- Japan 预约配送/时段：先用 `getOrderPreview` 确认 `fulfillmentConfiguration.serviceLevel.deliveryInterval`，再将 Amazon 接受的配置传给 `createOrder`。
- Japan 投递偏好：`destination.dropOffLocation` 可表达 neighbor、delivery box、locker 等类型；只传用户明确提供且当地支持的 attributes。
- India：`paymentInformation` 及 line-item payment-on-delivery 字段仅在 Amazon India 当前支持的业务中使用。
- Cross-border：同时展示并确认 `origin.countryCode`、destination country 和 `perUnitDeclaredValue`；以 preview constraints 为准。
- Unbranded / SIPP / Block AMZL：先通过 preview/offers 获取当前可用的 service 配置，然后把用户确认的 `fulfillmentConfiguration.services.packaging/additional` 原样传入 `createOrder`；不自行猜测区域可用值。
- 订单状态通知属于 Notifications API 的 `FULFILLMENT_ORDER_STATUS` 订阅，不是 Outbound 的第 10 个 operation。

## 取消

1. `getOrder` 恢复最新状态。
2. 展示可能无法取消已进入拣货/发运的部分，并取得确认。
3. 调用 `cancelOrder` 一次。
4. HTTP 202 后通过 `getOrder` 核实；不把接受请求等同于取消完成。
