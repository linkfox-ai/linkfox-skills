# ID 来源和跨版本规则

入库工作流中的 ID 不可互换。不要从显示名称、序号或另一个计划推导 ID。

| ID | 来源 | 用途 / 限制 |
|---|---|---|
| `inboundPlanId` | `createInboundPlan` | 整个 v2024 工作流的父级 ID；也对应 Send to Amazon workflow ID |
| `operationId` | 异步发起 operation | 只传给 `getInboundOperationStatus`；不是 plan/shipment/option ID |
| `packingOptionId` | `listPackingOptions` | 仅在同一 inbound plan 的当前 packing options 集合内使用 |
| `packingGroupId` | 已确认 packing option 的 packing groups | 已知箱规时用于 `setPackingInformation`；不是 shipmentId |
| `placementOptionId` | `listPlacementOptions` | 选择一个 placement；也用于 `generateTransportationOptions` |
| `shipmentId` | v2024 placement/shipment 响应 | v2024 plan 内 shipment 的 38 字符 ID；不应直接传给 v0 labels/BOL |
| `shipmentConfirmationId` | placement 确认后的 `getShipment` | 出现在 Amazon 标签上（例如 `FBA...`）；v0 `getLabels` / `getBillOfLading` 应使用此值 |
| `transportationOptionId` | `listTransportationOptions` | 与一个 `shipmentId` 绑定；每个 shipment 选一个 |
| `deliveryWindowOptionId` | `listDeliveryWindowOptions` | 与一个 shipment 绑定，且受 `validUntil` 限制 |
| `contentUpdatePreviewId` | `listShipmentContentUpdatePreviews` | 与指定 plan + shipment 绑定，受 `expiration` 限制 |
| `slotId` | `getSelfShipAppointmentSlots` | 与指定 plan + shipment 绑定，用于预约 self-ship slot |
| `boxId` | `listShipmentBoxes` | v0 `getLabels.packageLabelsToPrint`（wire: `PackageLabelsToPrint`）需要指定箱标签时使用 |
| `amazonReferenceId` | placement 确认后的 `getShipment` | 卡车/FC appointment 引用值；生成 self-ship slots 前要确认存在 |

## v2024 转 v0 标签与提单

```text
confirmPlacementOption
  → getInboundOperationStatus == SUCCESS
  → getShipment(inboundPlanId, shipmentId)
  → shipmentConfirmationId
  → getLabels / getBillOfLading v0 path {shipmentId}
```

v0 OpenAPI 使用路径名 `{shipmentId}`，但在 v2024 创建的 workflow 中，该路径值必须取自 `getShipment.shipmentConfirmationId`。脚本层参数应优先命名为 `shipmentConfirmationId`，避免与 v2024 `shipmentId` 混淆。

仅当用户明确操作原生 v0 shipment 时，才允许把 legacy `shipmentId` 作为兼容输入。如果同时传入两个不同的值，应拒绝而不是自动选择。

## 方案有效性

- 新一次 generate 可以使旧 option/preview/slot ID 失效。
- 必须在同一 `inboundPlanId`、`shipmentId` 和生成批次中使用 ID。
- 确认前检查费用、`validUntil`、`expiration` 和其他有效期字段。
- 不能在不同 plan/shipment 之间复用已缓存的 option ID。
