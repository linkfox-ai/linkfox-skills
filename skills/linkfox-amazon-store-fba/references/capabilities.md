# FBA 操作与脚本索引

详细字段定义见 [api.md](api.md) 及其分模块接口文档。

## 入仓资格 v1（1）

| 操作 | Amazon 方法 | path | 脚本 |
|---|---|---|---|
| getItemEligibilityPreview | GET | `fba/inbound/v1/eligibility/itemPreview` | [get_item_eligibility_preview.py](../scripts/get_item_eligibility_preview.py) |

## FBA 库存 v1（4）

| 操作 | Amazon 方法 | path | 脚本 |
|---|---|---|---|
| getInventorySummaries | GET | `fba/inventory/v1/summaries` | [get_inventory_summaries.py](../scripts/get_inventory_summaries.py) |
| createInventoryItem | POST | `fba/inventory/v1/items` | [create_inventory_item.py](../scripts/create_inventory_item.py) |
| deleteInventoryItem | DELETE | `fba/inventory/v1/items/{sellerSku}` | [delete_inventory_item.py](../scripts/delete_inventory_item.py) |
| addInventory | POST | `fba/inventory/v1/items/inventory` | [add_inventory.py](../scripts/add_inventory.py) |

## 入仓 v0 保留查询（6）

| 操作 | Amazon 方法 | path | 脚本 |
|---|---|---|---|
| getPrepInstructions | GET | `fba/inbound/v0/prepInstructions` | [get_prep_instructions.py](../scripts/get_prep_instructions.py) |
| getLabels | GET | `fba/inbound/v0/shipments/{shipmentId}/labels` | [get_labels_v0.py](../scripts/get_labels_v0.py) |
| getBillOfLading | GET | `fba/inbound/v0/shipments/{shipmentId}/billOfLading` | [get_bill_of_lading.py](../scripts/get_bill_of_lading.py) |
| getShipmentsV0 | GET | `fba/inbound/v0/shipments` | [get_shipments_v0.py](../scripts/get_shipments_v0.py) |
| getShipmentItemsByShipmentId | GET | `fba/inbound/v0/shipments/{shipmentId}/items` | [get_shipment_items_by_shipment_id.py](../scripts/get_shipment_items_by_shipment_id.py) |
| getShipmentItems | GET | `fba/inbound/v0/shipmentItems` | [get_shipment_items.py](../scripts/get_shipment_items.py) |

## 入仓 v2024-03-20（45）

| 操作 | Amazon 方法 | path | 脚本 |
|---|---|---|---|
| listInboundPlans | GET | `inbound/fba/2024-03-20/inboundPlans` | [list_inbound_plans.py](../scripts/list_inbound_plans.py) |
| createInboundPlan | POST | `inbound/fba/2024-03-20/inboundPlans` | [create_inbound_plan.py](../scripts/create_inbound_plan.py) |
| getInboundPlan | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | [get_inbound_plan.py](../scripts/get_inbound_plan.py) |
| listInboundPlanBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | [list_inbound_plan_boxes.py](../scripts/list_inbound_plan_boxes.py) |
| cancelInboundPlan | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | [cancel_inbound_plan.py](../scripts/cancel_inbound_plan.py) |
| listInboundPlanItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | [list_inbound_plan_items.py](../scripts/list_inbound_plan_items.py) |
| updateInboundPlanName | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | [update_inbound_plan_name.py](../scripts/update_inbound_plan_name.py) |
| listPackingGroupBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | [list_packing_group_boxes.py](../scripts/list_packing_group_boxes.py) |
| listPackingGroupItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | [list_packing_group_items.py](../scripts/list_packing_group_items.py) |
| setPackingInformation | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | [set_packing_information.py](../scripts/set_packing_information.py) |
| listPackingOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | [list_packing_options.py](../scripts/list_packing_options.py) |
| generatePackingOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | [generate_packing_options.py](../scripts/generate_packing_options.py) |
| confirmPackingOption | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | [confirm_packing_option.py](../scripts/confirm_packing_option.py) |
| listInboundPlanPallets | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | [list_inbound_plan_pallets.py](../scripts/list_inbound_plan_pallets.py) |
| listPlacementOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | [list_placement_options.py](../scripts/list_placement_options.py) |
| generatePlacementOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | [generate_placement_options.py](../scripts/generate_placement_options.py) |
| confirmPlacementOption | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | [confirm_placement_option.py](../scripts/confirm_placement_option.py) |
| getShipment | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | [get_inbound_shipment.py](../scripts/get_inbound_shipment.py) |
| listShipmentBoxes | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | [list_shipment_boxes.py](../scripts/list_shipment_boxes.py) |
| listShipmentContentUpdatePreviews | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | [list_shipment_content_update_previews.py](../scripts/list_shipment_content_update_previews.py) |
| generateShipmentContentUpdatePreviews | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | [generate_shipment_content_update_previews.py](../scripts/generate_shipment_content_update_previews.py) |
| getShipmentContentUpdatePreview | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | [get_shipment_content_update_preview.py](../scripts/get_shipment_content_update_preview.py) |
| confirmShipmentContentUpdatePreview | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | [confirm_shipment_content_update_preview.py](../scripts/confirm_shipment_content_update_preview.py) |
| getDeliveryChallanDocument | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | [get_delivery_challan_document.py](../scripts/get_delivery_challan_document.py) |
| listDeliveryWindowOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | [list_delivery_window_options.py](../scripts/list_delivery_window_options.py) |
| generateDeliveryWindowOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | [generate_delivery_window_options.py](../scripts/generate_delivery_window_options.py) |
| confirmDeliveryWindowOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | [confirm_delivery_window_options.py](../scripts/confirm_delivery_window_options.py) |
| listShipmentItems | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | [list_shipment_items.py](../scripts/list_shipment_items.py) |
| updateShipmentName | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | [update_shipment_name.py](../scripts/update_shipment_name.py) |
| listShipmentPallets | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | [list_shipment_pallets.py](../scripts/list_shipment_pallets.py) |
| cancelSelfShipAppointment | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | [cancel_self_ship_appointment.py](../scripts/cancel_self_ship_appointment.py) |
| getSelfShipAppointmentSlots | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | [get_self_ship_appointment_slots.py](../scripts/get_self_ship_appointment_slots.py) |
| generateSelfShipAppointmentSlots | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | [generate_self_ship_appointment_slots.py](../scripts/generate_self_ship_appointment_slots.py) |
| scheduleSelfShipAppointment | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | [schedule_self_ship_appointment.py](../scripts/schedule_self_ship_appointment.py) |
| updateShipmentSourceAddress | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | [update_shipment_source_address.py](../scripts/update_shipment_source_address.py) |
| updateShipmentTrackingDetails | PUT | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | [update_shipment_tracking_details.py](../scripts/update_shipment_tracking_details.py) |
| listTransportationOptions | GET | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | [list_transportation_options.py](../scripts/list_transportation_options.py) |
| generateTransportationOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | [generate_transportation_options.py](../scripts/generate_transportation_options.py) |
| confirmTransportationOptions | POST | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | [confirm_transportation_options.py](../scripts/confirm_transportation_options.py) |
| listItemComplianceDetails | GET | `inbound/fba/2024-03-20/items/compliance` | [list_item_compliance_details.py](../scripts/list_item_compliance_details.py) |
| updateItemComplianceDetails | PUT | `inbound/fba/2024-03-20/items/compliance` | [update_item_compliance_details.py](../scripts/update_item_compliance_details.py) |
| createMarketplaceItemLabels | POST | `inbound/fba/2024-03-20/items/labels` | [create_marketplace_item_labels.py](../scripts/create_marketplace_item_labels.py) |
| listPrepDetails | GET | `inbound/fba/2024-03-20/items/prepDetails` | [list_prep_details.py](../scripts/list_prep_details.py) |
| setPrepDetails | POST | `inbound/fba/2024-03-20/items/prepDetails` | [set_prep_details.py](../scripts/set_prep_details.py) |
| getInboundOperationStatus | GET | `inbound/fba/2024-03-20/operations/{operationId}` | [get_inbound_operation_status.py](../scripts/get_inbound_operation_status.py) |

## MCF 履约 v2020-07-01（14）

| 操作 | Amazon 方法 | path | 脚本 |
|---|---|---|---|
| getFulfillmentPreview | POST | `fba/outbound/2020-07-01/fulfillmentOrders/preview` | [get_fulfillment_preview.py](../scripts/get_fulfillment_preview.py) |
| deliveryOffers | POST | `fba/outbound/2020-07-01/deliveryOffers` | [delivery_offers.py](../scripts/delivery_offers.py) |
| listAllFulfillmentOrders | GET | `fba/outbound/2020-07-01/fulfillmentOrders` | [list_all_fulfillment_orders.py](../scripts/list_all_fulfillment_orders.py) |
| createFulfillmentOrder | POST | `fba/outbound/2020-07-01/fulfillmentOrders` | [create_fulfillment_order.py](../scripts/create_fulfillment_order.py) |
| getPackageTrackingDetails | GET | `fba/outbound/2020-07-01/tracking` | [get_package_tracking_details.py](../scripts/get_package_tracking_details.py) |
| listReturnReasonCodes | GET | `fba/outbound/2020-07-01/returnReasonCodes` | [list_return_reason_codes.py](../scripts/list_return_reason_codes.py) |
| createFulfillmentReturn | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return` | [create_fulfillment_return.py](../scripts/create_fulfillment_return.py) |
| getFulfillmentOrder | GET | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | [get_fulfillment_order.py](../scripts/get_fulfillment_order.py) |
| updateFulfillmentOrder | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}` | [update_fulfillment_order.py](../scripts/update_fulfillment_order.py) |
| cancelFulfillmentOrder | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel` | [cancel_fulfillment_order.py](../scripts/cancel_fulfillment_order.py) |
| submitFulfillmentOrderStatusUpdate | PUT | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status` | [submit_fulfillment_order_status_update.py](../scripts/submit_fulfillment_order_status_update.py) |
| getFeatures | GET | `fba/outbound/2020-07-01/features` | [get_features.py](../scripts/get_features.py) |
| getFeatureInventory | GET | `fba/outbound/2020-07-01/features/inventory/{featureName}` | [get_feature_inventory.py](../scripts/get_feature_inventory.py) |
| getFeatureSKU | GET | `fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}` | [get_feature_sku.py](../scripts/get_feature_sku.py) |
