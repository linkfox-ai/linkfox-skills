# Reference archive: linkfox-amazon-store-fba

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
    "path": "fba/inbound/v1/eligibility/itemPreview",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-fba/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-fba
description: 亚马逊 FBA 综合管理技能。用于查询商品入仓资格与 FBA 库存，调整库存，并处理 FBA 入仓计划、装箱、放置、运输、货件、标签、提单以及旧版 MCF 多渠道履约订单、退货和跟踪等跨域流程。用户提到亚马逊 FBA、入仓资格、Inbound Eligibility、FBA 库存摘要、Send to Amazon、Inbound Plan、FBA 货件、旧版 MCF、getItemEligibilityPreview、getInventorySummaries、createInboundPlan、createFulfillmentOrder 时触发。若需求专门涉及 Fulfillment Inbound v2024-03-20 入仓流程，优先使用 linkfox-amazon-store-fulfillment-inbound；涉及 Fulfillment Outbound v2026-07-04 新版 MCF，使用 linkfox-amazon-store-fulfillment-outbound；External Fulfillment 和普通卖家订单不属于此技能。
---

# Amazon 店铺 Fulfillment by Amazon (FBA)


覆盖 **方案 A** 模块：

1. **Inbound Eligibility v1**（入仓/混装资格预览）
2. **FBA Inventory v1**（仓内库存）
3. **Fulfillment Inbound v2024-03-20**（现行入仓工作流）+ **v0** 保留查询
4. **Fulfillment Outbound 2020-07-01**（MCF 多渠道履约）

不包含：FBA Small and Light（已弃用）、External Fulfillment（见 `linkfox-amazon-store-external-fulfillment`）、Merchant Fulfillment（MFN）。

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## Prerequisites

2. 应用需具备 **Amazon Fulfillment** 等相关角色（以 Amazon 控制台为准）
3. 网关需放行路径前缀：`fba/`、`inbound/fba/`（遇 **1005** 找后端加白）

## Current Capabilities

共 **70** 个 operation。模块表：

| 模块 | 数量 | 说明 |
|------|------|------|
| eligibility | 1 | getItemEligibilityPreview |
| inventory | 4 | summaries / create / delete / add |
| inbound_v0 | 6 | prep / labels / BOL / shipments / items |
| inbound (2024-03-20) | 45 | InboundPlan 全流程 |
| outbound (2020-07-01) | 14 | MCF 履约 |

**完整 Operation ↔ path ↔ 脚本表**：见 `references/capabilities.md`（见本文对应归档章节）  

## Quick Parameters

### getItemEligibilityPreview

- 必填：`asin`、`program`（`INBOUND`|`COMMINGLING`）
- `program=INBOUND` 时必填 `marketplaceIds`（或 `marketplaceId`，最多 1 个）



### getInventorySummaries

- 必填：`granularityType`（通常 `Marketplace`）、`granularityId`（marketplaceId）、`marketplaceIds`
- 可选：`details`、`sellerSkus`、`startDateTime`、`nextToken`

### Inbound / Outbound 写操作

复杂 schema 请用 **`requestBody`** 按官方模型传完整 JSON；path 参数（如 `inboundPlanId`、`shipmentId`、`sellerFulfillmentOrderId`）与 query 字段并列在入参中。

异步步骤（generate*Options 等）返回后用 **`getInboundOperationStatus`** 轮询（勿擅自高频轮询，先征得用户同意）。

## Scripts



共享模块：`_spapi_fba_common` 操作、`_fba_endpoints` 操作、`_fba_runner` 操作（非独立 CLI）。

## Display Rules

1. 先看 `developerProxy.errcode` / `httpStatus`，再看解析字段 **`payload`**
2. 202/204 可能无 body；以状态码判断成功
3. Inbound 2024 与 v0 的 `getShipments`/`getShipment` 勿混淆：v0 脚本为 `get_shipments_v0` 操作；2024 货件为 `get_inbound_shipment` 操作
4. 与 **`linkfox-amazon-store-orders`**、**`linkfox-amazon-store-external-fulfillment`** 边界清晰，勿混用

## Important Limitations

- Outbound **2026-07-04** 未纳入本 skill（方案 A）
- Small and Light 已弃用，不实现
- Inbound 状态机复杂，需按官方工作流顺序调用；冲突常见 **409/422**
- 限速因接口而异（Eligibility 约 1 rps），注意 **429**

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

**Feedback：** `skillName`：`linkfox-amazon-store-fba`

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-fba — API 与网关说明

## 1. 调用链


| 字段 | 说明 |
|------|------|
| region | NA / EU / FE |
| path | SP-API 相对路径，无前导 `/` |
| method | GET / POST / PUT / DELETE / PATCH |
| sellerId | 店铺 ID（网关解析 token） |
| queryString | 可选 |
| body + contentType | 写操作 |


## 2. 通用 JSON 入参

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId / region | 是 | |
| api / operation | 用 `fba_api` 操作 时必填 | Amazon operationId |
| requestBody | 写操作推荐 | 官方 body |
| query | 否 | 额外 query 对象 |
| queryString | 否 | 原始查询串（覆盖） |
| skipDepCheck | 否 | 跳过 auth skill 探测 |
| marketplaceId | 否 | 自动提升为 marketplaceIds |

路径模板参数（如 `inboundPlanId`、`shipmentId`、`sellerSku`）直接写在同级 JSON。

## 3. 模块索引

完整表见 `capabilities.md`（见本文对应归档章节），机器可读说明见 `operations.json`（见本文对应归档章节）。

### 3.1 Eligibility

- `getItemEligibilityPreview`：`asin` + `program`；INBOUND 需 marketplaceIds

### 3.2 Inventory

- `getInventorySummaries`：granularityType + granularityId + marketplaceIds
- `createInventoryItem` / `addInventory`：marketplaceId + requestBody
- `deleteInventoryItem`：sellerSku + marketplaceId

### 3.3 Inbound v0

- prepInstructions / labels / billOfLading / shipments / shipmentItems

### 3.4 Inbound 2024-03-20

- InboundPlan CRUD 与状态机：packing → placement → transportation → shipment
- 异步：`getInboundOperationStatus`
- items：compliance / labels / prepDetails

### 3.5 Outbound 2020-07-01

- preview / deliveryOffers / fulfillmentOrders CRUD / return / tracking / features

## 4. 官方入口

- [getItemEligibilityPreview](https://developer-docs.amazon.com/sp-api/reference/getitemeligibilitypreview)
- [FBA Inventory v1](https://developer-docs.amazon.com/sp-api/reference/fba-inventory-v1)
- [Fulfillment Inbound v2024-03-20](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v2024-03-20)
- [Fulfillment Inbound v0](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v0)
- [Fulfillment Outbound 2020-07-01](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-2020-07-01)

## 5. 错误处理

| 现象 | 处理 |
|------|------|
| 401/402 / 积分 | onboarding.md |
| 1005 | 放行 `fba/`、`inbound/fba/` |
| 403 | 角色/权限 |
| 409/422 | 状态机或参数问题 |
| 429 | 降速，先征得用户同意 |

## 6. Feedback

`skillName`：`linkfox-amazon-store-fba`

## Archived reference: capabilities.md

### eligibility (1)

| Operation | Method | path | 脚本 |
|-----------|--------|------|------|
| getItemEligibilityPreview | GET | `fba/inbound/v1/eligibility/itemPreview` | `get_item_eligibility_preview` 操作 |

### inventory (4)

| Operation | Method | path | 脚本 |
|-----------|--------|------|------|
| getInventorySummaries | GET | `fba/inventory/v1/summaries` | `get_inventory_summaries` 操作 |
| createInventoryItem | POST | `fba/inventory/v1/items` | `create_inventory_item` 操作 |
| deleteInventoryItem | DELETE | `fba/inventory/v1/items/{sellerSku}` | `delete_inventory_item` 操作 |
| addInventory | POST | `fba/inventory/v1/items/inventory` | `add_inventory` 操作 |

### inbound_v0 (6)

| Operation | Method | path | 脚本 |
|-----------|--------|------|------|
| getPrepInstructions | GET | `fba/inbound/v0/prepInstructions` | `amazon_store_fba__get_prep_instructions` 操作 |
| getLabels | GET | `fba/inbound/v0/shipments/{shipmentId}/labels` | `get_labels_v0` 操作 |
| getBillOfLading | GET | `fba/inbound/v0/shipments/{shipmentId}/billOfLading` | `amazon_store_fba__get_bill_of_lading` 操作 |
| getShipments | GET | `fba/inbound/v0/shipments` | `get_shipments_v0` 操作 |
| getShipmentItemsByShipmentId | GET | `fba/inbound/v0/shipments/{shipmentId}/items` | `amazon_store_fba__get_shipment_items_by_shipment_id` 操作 |
| getShipmentItems | GET | `fba/inbound/v0/shipmentItems` | `amazon_store_fba__get_shipment_items` 操作 |

### inbound (45)

| Operation | Method | path | 脚本 |
|-----------|--------|------|------|
| listInboundPlans | GET | `inbound/fba/2024-03-20/inboundPlans` | `amazon_store_fba__list_inbound_plans` 操作 |
| createInboundPlan | POST | `inbound/fba/2024-03-20/inboundPlans` | `amazon_store_fba__create_inbound_plan` 操作 |
| getInboundPlan | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | `amazon_store_fba__get_inbound_plan` 操作 |
| listInboundPlanBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | `amazon_store_fba__list_inbound_plan_boxes` 操作 |
| cancelInboundPlan | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | `amazon_store_fba__cancel_inbound_plan` 操作 |
| listInboundPlanItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | `amazon_store_fba__list_inbound_plan_items` 操作 |
| updateInboundPlanName | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | `amazon_store_fba__update_inbound_plan_name` 操作 |
| listPackingGroupBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | `amazon_store_fba__list_packing_group_boxes` 操作 |
| listPackingGroupItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | `amazon_store_fba__list_packing_group_items` 操作 |
| setPackingInformation | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | `amazon_store_fba__set_packing_information` 操作 |
| listPackingOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | `amazon_store_fba__list_packing_options` 操作 |
| generatePackingOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | `amazon_store_fba__generate_packing_options` 操作 |
| confirmPackingOption | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | `amazon_store_fba__confirm_packing_option` 操作 |
| listInboundPlanPallets | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | `amazon_store_fba__list_inbound_plan_pallets` 操作 |
| listPlacementOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | `amazon_store_fba__list_placement_options` 操作 |
| generatePlacementOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | `amazon_store_fba__generate_placement_options` 操作 |
| confirmPlacementOption | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | `amazon_store_fba__confirm_placement_option` 操作 |
| getShipment | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | `get_inbound_shipment` 操作 |
| listShipmentBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | `amazon_store_fba__list_shipment_boxes` 操作 |
| listShipmentContentUpdatePreviews | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | `amazon_store_fba__list_shipment_content_update_previews` 操作 |
| generateShipmentContentUpdatePreviews | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | `amazon_store_fba__generate_shipment_content_update_previews` 操作 |
| getShipmentContentUpdatePreview | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | `amazon_store_fba__get_shipment_content_update_preview` 操作 |
| confirmShipmentContentUpdatePreview | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | `amazon_store_fba__confirm_shipment_content_update_preview` 操作 |
| getDeliveryChallanDocument | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | `amazon_store_fba__get_delivery_challan_document` 操作 |
| listDeliveryWindowOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | `amazon_store_fba__list_delivery_window_options` 操作 |
| generateDeliveryWindowOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | `amazon_store_fba__generate_delivery_window_options` 操作 |
| confirmDeliveryWindowOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | `amazon_store_fba__confirm_delivery_window_options` 操作 |
| listShipmentItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | `amazon_store_fba__list_shipment_items` 操作 |
| updateShipmentName | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | `amazon_store_fba__update_shipment_name` 操作 |
| listShipmentPallets | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | `amazon_store_fba__list_shipment_pallets` 操作 |
| cancelSelfShipAppointment | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | `amazon_store_fba__cancel_self_ship_appointment` 操作 |
| getSelfShipAppointmentSlots | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | `amazon_store_fba__get_self_ship_appointment_slots` 操作 |
| generateSelfShipAppointmentSlots | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | `amazon_store_fba__generate_self_ship_appointment_slots` 操作 |
| scheduleSelfShipAppointment | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | `amazon_store_fba__schedule_self_ship_appointment` 操作 |
| updateShipmentSourceAddress | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | `amazon_store_fba__update_shipment_source_address` 操作 |
| updateShipmentTrackingDetails | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | `amazon_store_fba__update_shipment_tracking_details` 操作 |
| listTransportationOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | `amazon_store_fba__list_transportation_options` 操作 |
| generateTransportationOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | `amazon_store_fba__generate_transportation_options` 操作 |
| confirmTransportationOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | `amazon_store_fba__confirm_transportation_options` 操作 |
| listItemComplianceDetails | GET | `inbound/fba/2024-03-20/items/compliance` | `amazon_store_fba__list_item_compliance_details` 操作 |
| updateItemComplianceDetails | PUT | `inbound/fba/2024-03-20/items/compliance` | `amazon_store_fba__update_item_compliance_details` 操作 |
| createMarketplaceItemLabels | POST | `inbound/fba/2024-03-20/items/labels` | `amazon_store_fba__create_marketplace_item_labels` 操作 |
| listPrepDetails | GET | `inbound/fba/2024-03-20/items/prepDetails` | `amazon_store_fba__list_prep_details` 操作 |
| setPrepDetails | POST | `inbound/fba/2024-03-20/items/prepDetails` | `amazon_store_fba__set_prep_details` 操作 |
| getInboundOperationStatus | GET | `inbound/fba/2024-03-20/operations/{operationId}` | `amazon_store_fba__get_inbound_operation_status` 操作 |

### outbound (14)

| Operation | Method | path | 脚本 |
|-----------|--------|------|------|
| getFulfillmentPreview | POST | `fba/outbound/2020-07-01/fulfillmentOrders/preview` | `get_fulfillment_preview` 操作 |
| deliveryOffers | POST | `fba/outbound/2020-07-01/deliveryOffers` | `delivery_offers` 操作 |
| listAllFulfillmentOrders | GET | `fba/outbound/2020-07-01/fulfillmentOrders` | `list_all_fulfillment_orders` 操作 |
| createFulfillmentOrder | POST | `fba/outbound/2020-07-01/fulfillmentOrders` | `create_fulfillment_order` 操作 |
| getPackageTrackingDetails | GET | `fba/outbound/2020-07-01/tracking` | `get_package_tracking_details` 操作 |
| listReturnReasonCodes | GET | `fba/outbound/2020-07-01/returnReasonCodes` | `list_return_reason_codes` 操作 |
| createFulfillmentReturn | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return` | `create_fulfillment_return` 操作 |
| getFulfillmentOrder | GET | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | `get_fulfillment_order` 操作 |
| updateFulfillmentOrder | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | `update_fulfillment_order` 操作 |
| cancelFulfillmentOrder | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel` | `cancel_fulfillment_order` 操作 |
| submitFulfillmentOrderStatusUpdate | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status` | `submit_fulfillment_order_status_update` 操作 |
| getFeatures | GET | `fba/outbound/2020-07-01/features` | `get_features` 操作 |
| getFeatureInventory | GET | `fba/outbound/2020-07-01/features/inventory/{featureName}` | `get_feature_inventory` 操作 |
| getFeatureSKU | GET | `fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}` | `get_feature_sku` 操作 |

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。

## Archived reference: operations.json

```json
[
  {
    "id": "getItemEligibilityPreview",
    "method": "GET",
    "path": "fba/inbound/v1/eligibility/itemPreview",
    "module": "eligibility",
    "query": [
      "asin",
      "program",
      "marketplaceIds"
    ],
    "required": [
      "asin",
      "program"
    ],
    "script": "get_item_eligibility_preview operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getitemeligibilitypreview"
  },
  {
    "id": "getInventorySummaries",
    "method": "GET",
    "path": "fba/inventory/v1/summaries",
    "module": "inventory",
    "query": [
      "details",
      "granularityType",
      "granularityId",
      "startDateTime",
      "sellerSkus",
      "sellerSku",
      "nextToken",
      "marketplaceIds"
    ],
    "required": [
      "granularityType",
      "granularityId",
      "marketplaceIds"
    ],
    "script": "get_inventory_summaries operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getinventorysummaries"
  },
  {
    "id": "createInventoryItem",
    "method": "POST",
    "path": "fba/inventory/v1/items",
    "module": "inventory",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "marketplaceId"
    ],
    "body": true,
    "script": "create_inventory_item operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/createinventoryitem"
  },
  {
    "id": "deleteInventoryItem",
    "method": "DELETE",
    "path": "fba/inventory/v1/items/{sellerSku}",
    "module": "inventory",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "sellerSku",
      "marketplaceId"
    ],
    "script": "delete_inventory_item operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/deleteinventoryitem"
  },
  {
    "id": "addInventory",
    "method": "POST",
    "path": "fba/inventory/v1/items/inventory",
    "module": "inventory",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "marketplaceId"
    ],
    "body": true,
    "script": "add_inventory operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/addinventory"
  },
  {
    "id": "getPrepInstructions",
    "method": "GET",
    "path": "fba/inbound/v0/prepInstructions",
    "module": "inbound_v0",
    "query": [
      "ShipToCountryCode",
      "SellerSKUList",
      "ASINList"
    ],
    "required": [
      "ShipToCountryCode"
    ],
    "script": "get_prep_instructions operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getprepinstructions"
  },
  {
    "id": "getLabels",
    "method": "GET",
    "path": "fba/inbound/v0/shipments/{shipmentId}/labels",
    "module": "inbound_v0",
    "query": [
      "PageType",
      "LabelType",
      "NumberOfPackages",
      "PackageLabelsToPrint",
      "NumberOfPallets",
      "PageSize",
      "PageStartIndex"
    ],
    "required": [
      "shipmentId",
      "PageType",
      "LabelType"
    ],
    "script": "get_labels_v0 operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getlabels"
  },
  {
    "id": "getBillOfLading",
    "method": "GET",
    "path": "fba/inbound/v0/shipments/{shipmentId}/billOfLading",
    "module": "inbound_v0",
    "required": [
      "shipmentId"
    ],
    "script": "get_bill_of_lading operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getbilloflading"
  },
  {
    "id": "getShipmentsV0",
    "method": "GET",
    "path": "fba/inbound/v0/shipments",
    "module": "inbound_v0",
    "query": [
      "QueryType",
      "MarketplaceId",
      "ShipmentStatusList",
      "ShipmentIdList",
      "LastUpdatedAfter",
      "LastUpdatedBefore",
      "NextToken"
    ],
    "required": [
      "QueryType",
      "MarketplaceId"
    ],
    "script": "get_shipments_v0 operation",
    "amazonOp": "getShipments",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getshipments"
  },
  {
    "id": "getShipmentItemsByShipmentId",
    "method": "GET",
    "path": "fba/inbound/v0/shipments/{shipmentId}/items",
    "module": "inbound_v0",
    "query": [
      "MarketplaceId"
    ],
    "required": [
      "shipmentId"
    ],
    "script": "get_shipment_items_by_shipment_id operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getshipmentitemsbyshipmentid"
  },
  {
    "id": "getShipmentItems",
    "method": "GET",
    "path": "fba/inbound/v0/shipmentItems",
    "module": "inbound_v0",
    "query": [
      "QueryType",
      "MarketplaceId",
      "LastUpdatedAfter",
      "LastUpdatedBefore",
      "NextToken"
    ],
    "required": [
      "QueryType",
      "MarketplaceId"
    ],
    "script": "get_shipment_items operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getshipmentitems"
  },
  {
    "id": "listInboundPlans",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken",
      "status",
      "sortBy",
      "sortOrder"
    ],
    "required": [],
    "body": false,
    "script": "list_inbound_plans operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listinboundplans"
  },
  {
    "id": "createInboundPlan",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans",
    "module": "inbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "create_inbound_plan operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/createinboundplan"
  },
  {
    "id": "getInboundPlan",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "get_inbound_plan operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getinboundplan"
  },
  {
    "id": "listInboundPlanBoxes",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_inbound_plan_boxes operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listinboundplanboxes"
  },
  {
    "id": "cancelInboundPlan",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "cancel_inbound_plan operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/cancelinboundplan"
  },
  {
    "id": "listInboundPlanItems",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_inbound_plan_items operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listinboundplanitems"
  },
  {
    "id": "updateInboundPlanName",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "update_inbound_plan_name operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updateinboundplanname"
  },
  {
    "id": "listPackingGroupBoxes",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "packingGroupId"
    ],
    "body": false,
    "script": "list_packing_group_boxes operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listpackinggroupboxes"
  },
  {
    "id": "listPackingGroupItems",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "packingGroupId"
    ],
    "body": false,
    "script": "list_packing_group_items operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listpackinggroupitems"
  },
  {
    "id": "setPackingInformation",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "set_packing_information operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/setpackinginformation"
  },
  {
    "id": "listPackingOptions",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_packing_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listpackingoptions"
  },
  {
    "id": "generatePackingOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "generate_packing_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generatepackingoptions"
  },
  {
    "id": "confirmPackingOption",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "packingOptionId"
    ],
    "body": true,
    "script": "confirm_packing_option operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/confirmpackingoption"
  },
  {
    "id": "listInboundPlanPallets",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_inbound_plan_pallets operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listinboundplanpallets"
  },
  {
    "id": "listPlacementOptions",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_placement_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listplacementoptions"
  },
  {
    "id": "generatePlacementOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "generate_placement_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generateplacementoptions"
  },
  {
    "id": "confirmPlacementOption",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "placementOptionId"
    ],
    "body": true,
    "script": "confirm_placement_option operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/confirmplacementoption"
  },
  {
    "id": "getShipment",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "get_inbound_shipment operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getshipment"
  },
  {
    "id": "listShipmentBoxes",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "list_shipment_boxes operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listshipmentboxes"
  },
  {
    "id": "listShipmentContentUpdatePreviews",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "list_shipment_content_update_previews operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listshipmentcontentupdatepreviews"
  },
  {
    "id": "generateShipmentContentUpdatePreviews",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "generate_shipment_content_update_previews operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generateshipmentcontentupdatepreviews"
  },
  {
    "id": "getShipmentContentUpdatePreview",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId",
      "contentUpdatePreviewId"
    ],
    "body": false,
    "script": "get_shipment_content_update_preview operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getshipmentcontentupdatepreview"
  },
  {
    "id": "confirmShipmentContentUpdatePreview",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId",
      "contentUpdatePreviewId"
    ],
    "body": true,
    "script": "confirm_shipment_content_update_preview operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/confirmshipmentcontentupdatepreview"
  },
  {
    "id": "getDeliveryChallanDocument",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "get_delivery_challan_document operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getdeliverychallandocument"
  },
  {
    "id": "listDeliveryWindowOptions",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "list_delivery_window_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listdeliverywindowoptions"
  },
  {
    "id": "generateDeliveryWindowOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "generate_delivery_window_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generatedeliverywindowoptions"
  },
  {
    "id": "confirmDeliveryWindowOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId",
      "deliveryWindowOptionId"
    ],
    "body": true,
    "script": "confirm_delivery_window_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/confirmdeliverywindowoptions"
  },
  {
    "id": "listShipmentItems",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "list_shipment_items operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listshipmentitems"
  },
  {
    "id": "updateShipmentName",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "update_shipment_name operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updateshipmentname"
  },
  {
    "id": "listShipmentPallets",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "list_shipment_pallets operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listshipmentpallets"
  },
  {
    "id": "cancelSelfShipAppointment",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "cancel_self_ship_appointment operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/cancelselfshipappointment"
  },
  {
    "id": "getSelfShipAppointmentSlots",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken"
    ],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": false,
    "script": "get_self_ship_appointment_slots operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getselfshipappointmentslots"
  },
  {
    "id": "generateSelfShipAppointmentSlots",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "generate_self_ship_appointment_slots operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generateselfshipappointmentslots"
  },
  {
    "id": "scheduleSelfShipAppointment",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId",
      "slotId"
    ],
    "body": true,
    "script": "schedule_self_ship_appointment operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/scheduleselfshipappointment"
  },
  {
    "id": "updateShipmentSourceAddress",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "update_shipment_source_address operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updateshipmentsourceaddress"
  },
  {
    "id": "updateShipmentTrackingDetails",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId",
      "shipmentId"
    ],
    "body": true,
    "script": "update_shipment_tracking_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updateshipmenttrackingdetails"
  },
  {
    "id": "listTransportationOptions",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions",
    "module": "inbound",
    "query": [
      "pageSize",
      "paginationToken",
      "placementOptionId",
      "shipmentId"
    ],
    "required": [
      "inboundPlanId"
    ],
    "body": false,
    "script": "list_transportation_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listtransportationoptions"
  },
  {
    "id": "generateTransportationOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "generate_transportation_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/generatetransportationoptions"
  },
  {
    "id": "confirmTransportationOptions",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation",
    "module": "inbound",
    "query": [],
    "required": [
      "inboundPlanId"
    ],
    "body": true,
    "script": "confirm_transportation_options operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/confirmtransportationoptions"
  },
  {
    "id": "listItemComplianceDetails",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/items/compliance",
    "module": "inbound",
    "query": [
      "marketplaceId",
      "mskus"
    ],
    "required": [
      "marketplaceId"
    ],
    "body": false,
    "script": "list_item_compliance_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listitemcompliancedetails"
  },
  {
    "id": "updateItemComplianceDetails",
    "method": "PUT",
    "path": "inbound/fba/2024-03-20/items/compliance",
    "module": "inbound",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "marketplaceId"
    ],
    "body": true,
    "script": "update_item_compliance_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updateitemcompliancedetails"
  },
  {
    "id": "createMarketplaceItemLabels",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/items/labels",
    "module": "inbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "create_marketplace_item_labels operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/createmarketplaceitemlabels"
  },
  {
    "id": "listPrepDetails",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/items/prepDetails",
    "module": "inbound",
    "query": [
      "marketplaceId",
      "mskus"
    ],
    "required": [
      "marketplaceId",
      "mskus"
    ],
    "body": false,
    "script": "list_prep_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listprepdetails"
  },
  {
    "id": "setPrepDetails",
    "method": "POST",
    "path": "inbound/fba/2024-03-20/items/prepDetails",
    "module": "inbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "set_prep_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/setprepdetails"
  },
  {
    "id": "getInboundOperationStatus",
    "method": "GET",
    "path": "inbound/fba/2024-03-20/operations/{operationId}",
    "module": "inbound",
    "query": [],
    "required": [
      "operationId"
    ],
    "body": false,
    "script": "get_inbound_operation_status operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getinboundoperationstatus"
  },
  {
    "id": "getFulfillmentPreview",
    "method": "POST",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/preview",
    "module": "outbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "get_fulfillment_preview operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getfulfillmentpreview"
  },
  {
    "id": "deliveryOffers",
    "method": "POST",
    "path": "fba/outbound/2020-07-01/deliveryOffers",
    "module": "outbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "delivery_offers operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/deliveryoffers"
  },
  {
    "id": "listAllFulfillmentOrders",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders",
    "module": "outbound",
    "query": [
      "queryStartDate",
      "nextToken"
    ],
    "required": [],
    "body": false,
    "script": "list_all_fulfillment_orders operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listallfulfillmentorders"
  },
  {
    "id": "createFulfillmentOrder",
    "method": "POST",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders",
    "module": "outbound",
    "query": [],
    "required": [],
    "body": true,
    "script": "create_fulfillment_order operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/createfulfillmentorder"
  },
  {
    "id": "getPackageTrackingDetails",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/tracking",
    "module": "outbound",
    "query": [
      "packageNumber"
    ],
    "required": [
      "packageNumber"
    ],
    "body": false,
    "script": "get_package_tracking_details operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getpackagetrackingdetails"
  },
  {
    "id": "listReturnReasonCodes",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/returnReasonCodes",
    "module": "outbound",
    "query": [
      "sellerSku",
      "marketplaceId",
      "sellerFulfillmentOrderId",
      "language"
    ],
    "required": [],
    "body": false,
    "script": "list_return_reason_codes operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/listreturnreasoncodes"
  },
  {
    "id": "createFulfillmentReturn",
    "method": "PUT",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return",
    "module": "outbound",
    "query": [],
    "required": [
      "sellerFulfillmentOrderId"
    ],
    "body": true,
    "script": "create_fulfillment_return operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/createfulfillmentreturn"
  },
  {
    "id": "getFulfillmentOrder",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}",
    "module": "outbound",
    "query": [],
    "required": [
      "sellerFulfillmentOrderId"
    ],
    "body": false,
    "script": "get_fulfillment_order operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getfulfillmentorder"
  },
  {
    "id": "updateFulfillmentOrder",
    "method": "PUT",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}",
    "module": "outbound",
    "query": [],
    "required": [
      "sellerFulfillmentOrderId"
    ],
    "body": true,
    "script": "update_fulfillment_order operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/updatefulfillmentorder"
  },
  {
    "id": "cancelFulfillmentOrder",
    "method": "PUT",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel",
    "module": "outbound",
    "query": [],
    "required": [
      "sellerFulfillmentOrderId"
    ],
    "body": true,
    "script": "cancel_fulfillment_order operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/cancelfulfillmentorder"
  },
  {
    "id": "submitFulfillmentOrderStatusUpdate",
    "method": "PUT",
    "path": "fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status",
    "module": "outbound",
    "query": [],
    "required": [
      "sellerFulfillmentOrderId"
    ],
    "body": true,
    "script": "submit_fulfillment_order_status_update operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/submitfulfillmentorderstatusupdate"
  },
  {
    "id": "getFeatures",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/features",
    "module": "outbound",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "marketplaceId"
    ],
    "body": false,
    "script": "get_features operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getfeatures"
  },
  {
    "id": "getFeatureInventory",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/features/inventory/{featureName}",
    "module": "outbound",
    "query": [
      "marketplaceId",
      "nextToken"
    ],
    "required": [
      "featureName",
      "marketplaceId"
    ],
    "body": false,
    "script": "get_feature_inventory operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getfeatureinventory"
  },
  {
    "id": "getFeatureSKU",
    "method": "GET",
    "path": "fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}",
    "module": "outbound",
    "query": [
      "marketplaceId"
    ],
    "required": [
      "featureName",
      "sellerSku",
      "marketplaceId"
    ],
    "body": false,
    "script": "get_feature_sku operation",
    "doc": "https://developer-docs.amazon.com/sp-api/reference/getfeaturesku"
  }
]
```
