# Fulfillment Inbound 工作流

每个 operation 脚本只执行一次 Amazon 请求。本文中的 `poll`表示调用方显式运行 `get_inbound_operation_status.py`，只在 `SUCCESS` 后继续。

## 1. 已知箱规

```text
createInboundPlan → poll
generatePackingOptions → poll
listPackingOptions → 展示 packing options
confirmPackingOption → poll
listPackingGroupBoxes / listPackingGroupItems（按需）
setPackingInformation（使用 packingGroupId）→ poll
generatePlacementOptions → poll
listPlacementOptions → 展示 shipment 划分、费用/折扣
generateTransportationOptions（对候选 placement）→ poll
listTransportationOptions → 展示每个 shipment 的费用、时效和 expiration
confirmPlacementOption → poll
[自有承运人] generate/list/confirmDeliveryWindowOptions → 各步 poll
confirmTransportationOptions → poll
getShipment → shipmentConfirmationId
getLabels / getBillOfLading（v0）
[非合作承运人] updateShipmentTrackingDetails → poll
```

如果在 `setPackingInformation` 后修改箱规，必须重新 `generatePlacementOptions`，不能确认旧 placement option。Amazon 目前不支持完全丢弃已提交的 packing information；要完全重置时建立新 plan。

## 2. Pack Later（未知箱规）

只用于 pallet delivery（LTL/FTL）：

```text
createInboundPlan → poll
generatePlacementOptions({}) → poll
listPlacementOptions
confirmPlacementOption → poll
setPackingInformation（使用 shipmentId，不传 packingGroupId）→ poll
generateTransportationOptions → poll
listTransportationOptions
[自有承运人] generate/list/confirmDeliveryWindowOptions
confirmTransportationOptions → poll
getShipment → labels/BOL/tracking
```

每个 `packageGrouping` 必须按工作流二选一：已知箱规传 `packingGroupId`，Pack Later 传 `shipmentId`。

## 3. 合作承运人与自有承运人

- Amazon Partnered Carrier：在 `listTransportationOptions` 中选择 `shippingSolution=AMAZON_PARTNERED_CARRIER`。确认代表接受运费估算和 Amazon 扣费。
- 自有承运人：选择 `shippingSolution=USE_YOUR_OWN_CARRIER`，按 `preconditions` 为每个 shipment 生成、列出并确认 delivery window。
- 多 shipment placement 要为每个 `shipmentId` 选择一个 `transportationOptionId`。
- 所有 shipment 类型都必须确认 transportation option。
- `confirmTransportationOptions` 之前必须已确认 placement；确认 transportation 后不能再为该 plan 生成或确认新 transportation options。

## 4. 货件内容更新

仅在 transportation 已确认且 shipment 尚未进入 `RECEIVING` 之前使用：

```text
generateShipmentContentUpdatePreviews(boxes, items) → poll
listShipmentContentUpdatePreviews
getShipmentContentUpdatePreview → 展示 requestedUpdates、transportationOption、expiration
用户明确确认
confirmShipmentContentUpdatePreview → poll
getShipment / listShipmentBoxes / listShipmentItems 验证结果
```

不能确认已过期 preview，也不能把一个 shipment 的 preview ID 用于另一个 shipment。

Amazon 当前限制：在每个 shipment 内，每个 SKU 的数量只能在原数量基础上调整“5% 或 6 件，取较大值”；只有原数量不超过 6 时才能移除整个 SKU，且不能移除所有 SKU 或使 shipment 变空。超出该范围时取消 inbound plan 并重新创建；脚本无法仅根据新 body 得知原数量，所以确认前必须先读取当前 shipment items 并做差分。

## 5. India 工作流

```text
list/updateItemComplianceDetails（每个 MSKU 通常只需维护一次）
createInboundPlan → poll
generatePlacementOptions(customPlacement) → poll
listPlacementOptions → 选定 placement，保留其所有 shipmentId
setPackingInformation（覆盖所有选定 shipmentId）→ poll
confirmPlacementOption → poll
generate/list/confirmTransportationOptions → poll
getShipment → 确认 amazonReferenceId
[自配送] generateSelfShipAppointmentSlots → poll
              → getSelfShipAppointmentSlots
              → scheduleSelfShipAppointment
[合作承运人] getDeliveryChallanDocument
```

Appointment booking 仅用于 self-ship；delivery challan 仅用于 India PCP shipment。

Amazon 当前 India 用例指定：确认 placement 前，必须先为该 placement 的全部 shipment IDs 提交 packing information。这是 India custom-placement 的特定顺序，不要套用 Pack Later 的“确认 placement 后再 packing”顺序。

## 6. 只读恢复

已有 `inboundPlanId` / `shipmentId` 时，先查询状态而不是重新创建：

```text
getInboundPlan
  → listPackingOptions / listPlacementOptions（按当前阶段）
  → getShipment
  → listShipmentBoxes / listShipmentItems / listShipmentPallets
```

如果手头是 `operationId`，先 `getInboundOperationStatus`。写请求遇到超时或不确定响应时，通过状态查询和只读 operation 恢复，不直接重放写请求。

- `listInboundPlanItems` / `listInboundPlanPallets` 的 package grouping 标识在确认 placement 前可能是 `packingGroupId`，确认后则是 `shipmentId`；不要混用。
- `listShipmentBoxes` 只在 `setPackingInformation` 生成箱信息后有数据；`listShipmentPallets` 只在 LTL/FTL transportation 流程提供托盘信息后有数据。

## 7. 标签和提单

placement 确认完成后，调用 `getShipment` 获取 `shipmentConfirmationId`，再传给 v0 `getLabels` / `getBillOfLading`。不要直接使用 v2024 `shipmentId`。完整 ID 规则见 [identifiers.md](identifiers.md)。

## 8. 取消与运费撤销窗口

`cancelInboundPlan` 会取消 plan 及关联 shipments，但已确认 transportation 的运费只在 Amazon 的 void window 内可取消：SPD 为确认后 24 小时，LTL/FTL 为确认后 1 小时。超过时限可能仍收取运费。执行前展示 shipment 类型、transportation 确认时间和可能费用；完成后用 `getInboundOperationStatus` 确认操作为 `SUCCESS`；需要核对计划最终状态时，用 `getInboundPlan` 确认 `VOIDED`。
