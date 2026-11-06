---
name: linkfox-amazon-store-fba
description: 管理亚马逊店铺的 FBA 商品入仓资格、仓内库存、入仓计划、装箱、放置、运输、货件、标签和提单，以及旧版 MCF 多渠道履约订单、退货和跟踪。适用于 FBA 综合管理及跨模块履约流程；专门的现行入仓流程和新版 MCF 使用对应技能，不适用于 External Fulfillment、普通卖家订单或自配送履约。
---
# Amazon 店铺 FBA 综合管理

## 适用范围

### 适用

管理已授权亚马逊卖家店铺的 FBA 库存及入仓、旧版 MCF 履约流程。
用户希望核对商品入仓或混装资格、查看或调整仓内库存、处理入仓计划与货件，或管理旧版 MCF 订单、退货和包裹跟踪时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 这个商品能否入仓或混装 | 入仓资格：展示资格预览与限制原因。 |
| 查看 FBA 库存，或按我提供的信息调整库存 | 库存管理：核对目标店铺、站点与库存商品。 |
| 帮我处理 Send to Amazon 入仓计划和货件 | 入仓流程：计划、装箱、放置、运输与货件管理。 |
| 获取旧版货件的标签、提单和商品清单 | 保留查询：使用入仓 v0 对应能力。 |
| 查看或处理旧版 MCF 订单、退货及跟踪 | 旧版 MCF：履约预览、订单维护、退货与包裹查询。 |

### 边界

专门涉及 Fulfillment Inbound v2024-03-20 入仓流程时，优先使用 `linkfox-amazon-store-fulfillment-inbound`；Fulfillment Outbound v2026-07-04 新版 MCF 使用 `linkfox-amazon-store-fulfillment-outbound`。External Fulfillment 使用 `linkfox-amazon-store-external-fulfillment`，普通卖家订单使用 `linkfox-amazon-store-orders`。本技能不包含已弃用的 FBA Small and Light，也不处理 Merchant Fulfillment（MFN）。

## 接口清单

外层统一为 POST `/spApi/developerProxy`；下表同时列出转发方法和 path，以区分 70 个操作。模块数量为资格 1、库存 4、旧版入仓 6、现行入仓 45、旧版 MCF 14。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 预览商品入仓与混装资格（`getItemEligibilityPreview`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v1/eligibility/itemPreview` | `references/apis/eligibility.md` | `scripts/get_item_eligibility_preview.py` | 入仓资格 v1。 |
| 查询 FBA 库存摘要（`getInventorySummaries`） | POST `/spApi/developerProxy` -> GET path：`fba/inventory/v1/summaries` | `references/apis/inventory.md` | `scripts/get_inventory_summaries.py` | FBA 库存 v1。 |
| 创建库存商品（`createInventoryItem`） | POST `/spApi/developerProxy` -> POST path：`fba/inventory/v1/items` | `references/apis/inventory.md` | `scripts/create_inventory_item.py` | FBA 库存 v1。 |
| 删除库存商品（`deleteInventoryItem`） | POST `/spApi/developerProxy` -> DELETE path：`fba/inventory/v1/items/{sellerSku}` | `references/apis/inventory.md` | `scripts/delete_inventory_item.py` | FBA 库存 v1。 |
| 增加库存（`addInventory`） | POST `/spApi/developerProxy` -> POST path：`fba/inventory/v1/items/inventory` | `references/apis/inventory.md` | `scripts/add_inventory.py` | FBA 库存 v1。 |
| 查询旧版预处理说明（`getPrepInstructions`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/prepInstructions` | `references/apis/inbound_v0.md` | `scripts/get_prep_instructions.py` | 入仓 v0 保留查询。 |
| 获取旧版货件标签（`getLabels`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/shipments/{shipmentId}/labels` | `references/apis/inbound_v0.md` | `scripts/get_labels_v0.py` | 入仓 v0 保留查询。 |
| 获取旧版提单（`getBillOfLading`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/shipments/{shipmentId}/billOfLading` | `references/apis/inbound_v0.md` | `scripts/get_bill_of_lading.py` | 入仓 v0 保留查询。 |
| 查询旧版入仓货件（`getShipmentsV0`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/shipments` | `references/apis/inbound_v0.md` | `scripts/get_shipments_v0.py` | 入仓 v0 保留查询。 |
| 按旧版货件查询商品（`getShipmentItemsByShipmentId`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/shipments/{shipmentId}/items` | `references/apis/inbound_v0.md` | `scripts/get_shipment_items_by_shipment_id.py` | 入仓 v0 保留查询。 |
| 查询旧版货件商品（`getShipmentItems`） | POST `/spApi/developerProxy` -> GET path：`fba/inbound/v0/shipmentItems` | `references/apis/inbound_v0.md` | `scripts/get_shipment_items.py` | 入仓 v0 保留查询。 |
| 列出入仓计划（`listInboundPlans`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans` | `references/apis/inbound.md` | `scripts/list_inbound_plans.py` | 入仓 v2024-03-20。 |
| 创建入仓计划（`createInboundPlan`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans` | `references/apis/inbound.md` | `scripts/create_inbound_plan.py` | 入仓 v2024-03-20。 |
| 获取入仓计划（`getInboundPlan`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | `references/apis/inbound.md` | `scripts/get_inbound_plan.py` | 入仓 v2024-03-20。 |
| 列出计划箱件（`listInboundPlanBoxes`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | `references/apis/inbound.md` | `scripts/list_inbound_plan_boxes.py` | 入仓 v2024-03-20。 |
| 取消入仓计划（`cancelInboundPlan`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | `references/apis/inbound.md` | `scripts/cancel_inbound_plan.py` | 入仓 v2024-03-20。 |
| 列出计划商品（`listInboundPlanItems`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | `references/apis/inbound.md` | `scripts/list_inbound_plan_items.py` | 入仓 v2024-03-20。 |
| 更新计划名称（`updateInboundPlanName`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | `references/apis/inbound.md` | `scripts/update_inbound_plan_name.py` | 入仓 v2024-03-20。 |
| 列出装箱组箱件（`listPackingGroupBoxes`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | `references/apis/inbound.md` | `scripts/list_packing_group_boxes.py` | 入仓 v2024-03-20。 |
| 列出装箱组商品（`listPackingGroupItems`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | `references/apis/inbound.md` | `scripts/list_packing_group_items.py` | 入仓 v2024-03-20。 |
| 设置装箱信息（`setPackingInformation`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | `references/apis/inbound.md` | `scripts/set_packing_information.py` | 入仓 v2024-03-20。 |
| 列出装箱选项（`listPackingOptions`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | `references/apis/inbound.md` | `scripts/list_packing_options.py` | 入仓 v2024-03-20。 |
| 生成装箱选项（`generatePackingOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | `references/apis/inbound.md` | `scripts/generate_packing_options.py` | 入仓 v2024-03-20。 |
| 确认装箱选项（`confirmPackingOption`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | `references/apis/inbound.md` | `scripts/confirm_packing_option.py` | 入仓 v2024-03-20。 |
| 列出计划托盘（`listInboundPlanPallets`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | `references/apis/inbound.md` | `scripts/list_inbound_plan_pallets.py` | 入仓 v2024-03-20。 |
| 列出放置选项（`listPlacementOptions`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | `references/apis/inbound.md` | `scripts/list_placement_options.py` | 入仓 v2024-03-20。 |
| 生成放置选项（`generatePlacementOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | `references/apis/inbound.md` | `scripts/generate_placement_options.py` | 入仓 v2024-03-20。 |
| 确认放置选项（`confirmPlacementOption`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | `references/apis/inbound.md` | `scripts/confirm_placement_option.py` | 入仓 v2024-03-20。 |
| 获取现行入仓货件（`getShipment`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | `references/apis/inbound.md` | `scripts/get_inbound_shipment.py` | 入仓 v2024-03-20。 |
| 列出货件箱件（`listShipmentBoxes`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | `references/apis/inbound.md` | `scripts/list_shipment_boxes.py` | 入仓 v2024-03-20。 |
| 列出货件内容更新预览（`listShipmentContentUpdatePreviews`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | `references/apis/inbound.md` | `scripts/list_shipment_content_update_previews.py` | 入仓 v2024-03-20。 |
| 生成货件内容更新预览（`generateShipmentContentUpdatePreviews`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | `references/apis/inbound.md` | `scripts/generate_shipment_content_update_previews.py` | 入仓 v2024-03-20。 |
| 获取货件内容更新预览（`getShipmentContentUpdatePreview`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | `references/apis/inbound.md` | `scripts/get_shipment_content_update_preview.py` | 入仓 v2024-03-20。 |
| 确认货件内容更新预览（`confirmShipmentContentUpdatePreview`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | `references/apis/inbound.md` | `scripts/confirm_shipment_content_update_preview.py` | 入仓 v2024-03-20。 |
| 获取交货单文档（`getDeliveryChallanDocument`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | `references/apis/inbound.md` | `scripts/get_delivery_challan_document.py` | 入仓 v2024-03-20。 |
| 列出送达窗口选项（`listDeliveryWindowOptions`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | `references/apis/inbound.md` | `scripts/list_delivery_window_options.py` | 入仓 v2024-03-20。 |
| 生成送达窗口选项（`generateDeliveryWindowOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | `references/apis/inbound.md` | `scripts/generate_delivery_window_options.py` | 入仓 v2024-03-20。 |
| 确认送达窗口选项（`confirmDeliveryWindowOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | `references/apis/inbound.md` | `scripts/confirm_delivery_window_options.py` | 入仓 v2024-03-20。 |
| 列出现行货件商品（`listShipmentItems`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | `references/apis/inbound.md` | `scripts/list_shipment_items.py` | 入仓 v2024-03-20。 |
| 更新货件名称（`updateShipmentName`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | `references/apis/inbound.md` | `scripts/update_shipment_name.py` | 入仓 v2024-03-20。 |
| 列出货件托盘（`listShipmentPallets`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | `references/apis/inbound.md` | `scripts/list_shipment_pallets.py` | 入仓 v2024-03-20。 |
| 取消自配送预约（`cancelSelfShipAppointment`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | `references/apis/inbound.md` | `scripts/cancel_self_ship_appointment.py` | 入仓 v2024-03-20。 |
| 获取自配送预约时段（`getSelfShipAppointmentSlots`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | `references/apis/inbound.md` | `scripts/get_self_ship_appointment_slots.py` | 入仓 v2024-03-20。 |
| 生成自配送预约时段（`generateSelfShipAppointmentSlots`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | `references/apis/inbound.md` | `scripts/generate_self_ship_appointment_slots.py` | 入仓 v2024-03-20。 |
| 安排自配送预约（`scheduleSelfShipAppointment`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | `references/apis/inbound.md` | `scripts/schedule_self_ship_appointment.py` | 入仓 v2024-03-20。 |
| 更新货件发货地址（`updateShipmentSourceAddress`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | `references/apis/inbound.md` | `scripts/update_shipment_source_address.py` | 入仓 v2024-03-20。 |
| 更新货件跟踪信息（`updateShipmentTrackingDetails`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | `references/apis/inbound.md` | `scripts/update_shipment_tracking_details.py` | 入仓 v2024-03-20。 |
| 列出运输选项（`listTransportationOptions`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | `references/apis/inbound.md` | `scripts/list_transportation_options.py` | 入仓 v2024-03-20。 |
| 生成运输选项（`generateTransportationOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | `references/apis/inbound.md` | `scripts/generate_transportation_options.py` | 入仓 v2024-03-20。 |
| 确认运输选项（`confirmTransportationOptions`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | `references/apis/inbound.md` | `scripts/confirm_transportation_options.py` | 入仓 v2024-03-20。 |
| 列出商品合规信息（`listItemComplianceDetails`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/items/compliance` | `references/apis/inbound.md` | `scripts/list_item_compliance_details.py` | 入仓 v2024-03-20。 |
| 更新商品合规信息（`updateItemComplianceDetails`） | POST `/spApi/developerProxy` -> PUT path：`inbound/fba/2024-03-20/items/compliance` | `references/apis/inbound.md` | `scripts/update_item_compliance_details.py` | 入仓 v2024-03-20。 |
| 创建站点商品标签（`createMarketplaceItemLabels`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/items/labels` | `references/apis/inbound.md` | `scripts/create_marketplace_item_labels.py` | 入仓 v2024-03-20。 |
| 列出商品预处理信息（`listPrepDetails`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/items/prepDetails` | `references/apis/inbound.md` | `scripts/list_prep_details.py` | 入仓 v2024-03-20。 |
| 设置商品预处理信息（`setPrepDetails`） | POST `/spApi/developerProxy` -> POST path：`inbound/fba/2024-03-20/items/prepDetails` | `references/apis/inbound.md` | `scripts/set_prep_details.py` | 入仓 v2024-03-20。 |
| 查询入仓异步操作状态（`getInboundOperationStatus`） | POST `/spApi/developerProxy` -> GET path：`inbound/fba/2024-03-20/operations/{operationId}` | `references/apis/inbound.md` | `scripts/get_inbound_operation_status.py` | 入仓 v2024-03-20。 |
| 预览旧版 MCF 履约（`getFulfillmentPreview`） | POST `/spApi/developerProxy` -> POST path：`fba/outbound/2020-07-01/fulfillmentOrders/preview` | `references/apis/outbound.md` | `scripts/get_fulfillment_preview.py` | MCF 履约 v2020-07-01。 |
| 查询旧版 MCF 配送报价（`deliveryOffers`） | POST `/spApi/developerProxy` -> POST path：`fba/outbound/2020-07-01/deliveryOffers` | `references/apis/outbound.md` | `scripts/delivery_offers.py` | MCF 履约 v2020-07-01。 |
| 列出旧版 MCF 履约订单（`listAllFulfillmentOrders`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/fulfillmentOrders` | `references/apis/outbound.md` | `scripts/list_all_fulfillment_orders.py` | MCF 履约 v2020-07-01。 |
| 创建旧版 MCF 履约订单（`createFulfillmentOrder`） | POST `/spApi/developerProxy` -> POST path：`fba/outbound/2020-07-01/fulfillmentOrders` | `references/apis/outbound.md` | `scripts/create_fulfillment_order.py` | MCF 履约 v2020-07-01。 |
| 获取旧版 MCF 包裹跟踪（`getPackageTrackingDetails`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/tracking` | `references/apis/outbound.md` | `scripts/get_package_tracking_details.py` | MCF 履约 v2020-07-01。 |
| 列出旧版 MCF 退货原因（`listReturnReasonCodes`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/returnReasonCodes` | `references/apis/outbound.md` | `scripts/list_return_reason_codes.py` | MCF 履约 v2020-07-01。 |
| 创建旧版 MCF 退货（`createFulfillmentReturn`） | POST `/spApi/developerProxy` -> PUT path：`fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return` | `references/apis/outbound.md` | `scripts/create_fulfillment_return.py` | MCF 履约 v2020-07-01。 |
| 获取旧版 MCF 履约订单（`getFulfillmentOrder`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | `references/apis/outbound.md` | `scripts/get_fulfillment_order.py` | MCF 履约 v2020-07-01。 |
| 更新旧版 MCF 履约订单（`updateFulfillmentOrder`） | POST `/spApi/developerProxy` -> PUT path：`fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | `references/apis/outbound.md` | `scripts/update_fulfillment_order.py` | MCF 履约 v2020-07-01。 |
| 取消旧版 MCF 履约订单（`cancelFulfillmentOrder`） | POST `/spApi/developerProxy` -> PUT path：`fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel` | `references/apis/outbound.md` | `scripts/cancel_fulfillment_order.py` | MCF 履约 v2020-07-01。 |
| 提交旧版 MCF 订单状态更新（`submitFulfillmentOrderStatusUpdate`） | POST `/spApi/developerProxy` -> PUT path：`fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status` | `references/apis/outbound.md` | `scripts/submit_fulfillment_order_status_update.py` | MCF 履约 v2020-07-01。 |
| 获取旧版 MCF 功能（`getFeatures`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/features` | `references/apis/outbound.md` | `scripts/get_features.py` | MCF 履约 v2020-07-01。 |
| 获取旧版 MCF 功能库存（`getFeatureInventory`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/features/inventory/{featureName}` | `references/apis/outbound.md` | `scripts/get_feature_inventory.py` | MCF 履约 v2020-07-01。 |
| 获取旧版 MCF 功能 SKU（`getFeatureSKU`） | POST `/spApi/developerProxy` -> GET path：`fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}` | `references/apis/outbound.md` | `scripts/get_feature_sku.py` | MCF 履约 v2020-07-01。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。确认目标店铺、站点及操作对象；应用需具备 Amazon Fulfillment 等相关角色。依赖检测及网关配置见 `references/api.md`，各操作所需信息见对应接口文档。

## 执行流程

1. 确认店铺授权、目标站点与业务目标，按接口清单选择资格、库存、入仓或旧版 MCF 操作，并读取对应定义。
2. 核对业务输入；写入时明确用户要求的目标和变更内容，按对应模型准备业务数据。统一入口和单操作脚本均可用，具体参数映射见接口定义。
3. 入仓按计划 → 装箱 → 放置 → 运输 → 货件的状态机顺序执行；异步生成步骤返回后，保留操作标识，通过状态查询确认结果，再推进后续步骤。不得擅自高频轮询，先征得用户同意。
4. 查询完整响应并解释业务结果；写操作结果不确定时先查询状态，不直接重放。失败或空结果不得自动翻页或连续试探，继续前先说明原因与后续调用范围；限流及店铺保护按接口参考处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/fba_api.py '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，业务脚本禁用响应缓存。失败或空结果时，不得自动翻页或修改参数连续试探；需要继续查询时，先向用户说明原因和调用范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-fba-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、存在的顶层常见标量（如 `total`、`success`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分模块和版本**：本技能覆盖 Inbound Eligibility v1、FBA Inventory v1、Fulfillment Inbound v2024-03-20 及 v0 保留查询、Fulfillment Outbound v2020-07-01。旧版货件查询使用 `scripts/get_shipments_v0.py`，现行单货件查询使用 `scripts/get_inbound_shipment.py`，不要混淆。
- **清晰展示结果**：注明店铺、站点和业务模块，用表格展示库存、资格原因、计划或货件状态、履约订单及跟踪数据。区分请求完成、异步操作被接受和最终业务完成。
- **保留原始证据**：保留网关完整响应、已取得的任务标识和数据文件；通过摘要判断数据是否足够，再从文件提取具体字段。
- **解释状态与保护**：先按接口参考判断网关和上游状态，再解释业务数据。遇店铺保护时先说明保护原因、处理动作和等待时间，不仅以“服务器繁忙”解释；冷却及重试规则见 `references/spapi-protection.md`。
- **缓存约定**：本技能业务脚本禁用响应缓存；具体 CLI 及缓存约定见 `references/api.md`。

## 使用示例

### 核对入仓资格与仓内库存

用户：看看这个商品是否能入仓，再核对对应站点的 FBA 库存。

确认店铺和站点，先做资格预览，再按目标范围查看库存，分别说明资格原因及可用库存数据。

### 处理现行入仓计划

用户：按这些商品和装箱信息处理入仓计划。

确认计划和写入范围，依状态机推进装箱、放置、运输与货件步骤；保留异步操作标识，确认状态后再继续。

### 获取旧版货件文档

用户：查一下旧版货件的标签和提单。

选择入仓 v0 对应操作，展示文档及所属货件，不与现行货件查询混用。

### 查询旧版 MCF 订单与退货

用户：查看这个旧版 MCF 订单的履约和跟踪，按我提供的资料处理退货。

先查询订单及跟踪，再在用户指定的退货范围内准备数据，说明提交结果与后续可查状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
