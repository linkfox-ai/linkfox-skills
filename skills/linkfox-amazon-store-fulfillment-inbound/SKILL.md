---
name: linkfox-amazon-store-fulfillment-inbound
description: 管理已授权亚马逊店铺的 FBA 入仓全流程，支持入库计划、装箱、分仓、货件内容更新、运输方案、送达窗口、自配送预约、商品合规与预处理，以及箱唛、商品标签、交货单、提单和异步状态查询。适用于 Send to Amazon 入仓准备、执行与状态恢复；不适用于前台竞品研究、店铺刊登维护或已废弃的旧版建仓与运输写入。
---
# Amazon 店铺 FBA 入仓管理

## 适用范围

### 适用

将库存发往亚马逊运营中心，或恢复已有入库计划和货件的执行进度。覆盖 v2024-03-20 的 45 个操作及配合新流程使用的 6 个 v0 查询和文档操作。

**场景速查**

| 用户表达 | 处理场景 |
|---|---|
| 按这批 SKU 创建 FBA 入库计划 | 建立计划并推进装箱、分仓和运输。 |
| 比较这些分仓和运输方案 | 展示货件划分、运费、折扣、有效期及前置条件。 |
| 改一下货件内容、地址或追踪信息 | 核对当前阶段，准备相应变更或内容预览。 |
| 安排送仓或印度自配送预约 | 读取送达窗口、预约槽与现有预约。 |
| 下载箱唛、商品标签或提单 | 核对货件标识并及时获取文档。 |
| 入库操作超时，查一下是否完成 | 查询异步状态或只读恢复计划和货件。 |

## 接口清单

LinkFox 外层统一为 POST；下表端点中的方法表示转发给 Amazon 的方法。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 列出入库计划（`listInboundPlans`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/list_inbound_plans.py` | 同步读取或处理结果。 |
| 创建入库计划（`createInboundPlan`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/create_inbound_plan.py` | 发起异步操作，需续查状态。 |
| 获取入库计划（`getInboundPlan`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/get_inbound_plan.py` | 同步读取或处理结果。 |
| 列出计划箱信息（`listInboundPlanBoxes`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/list_inbound_plan_boxes.py` | 同步读取或处理结果。 |
| 取消入库计划（`cancelInboundPlan`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/cancel_inbound_plan.py` | 发起异步操作，需续查状态。 |
| 列出计划商品（`listInboundPlanItems`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/list_inbound_plan_items.py` | 同步读取或处理结果。 |
| 修改计划名称（`updateInboundPlanName`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name` | [references/apis/inbound-plans.md](references/apis/inbound-plans.md) | `scripts/update_inbound_plan_name.py` | 同步读取或处理结果。 |
| 列出装箱组箱信息（`listPackingGroupBoxes`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | [references/apis/packing.md](references/apis/packing.md) | `scripts/list_packing_group_boxes.py` | 同步读取或处理结果。 |
| 列出装箱组商品（`listPackingGroupItems`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | [references/apis/packing.md](references/apis/packing.md) | `scripts/list_packing_group_items.py` | 同步读取或处理结果。 |
| 提交装箱信息（`setPackingInformation`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation` | [references/apis/packing.md](references/apis/packing.md) | `scripts/set_packing_information.py` | 发起异步操作，需续查状态。 |
| 列出装箱方案（`listPackingOptions`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | [references/apis/packing.md](references/apis/packing.md) | `scripts/list_packing_options.py` | 同步读取或处理结果。 |
| 生成装箱方案（`generatePackingOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions` | [references/apis/packing.md](references/apis/packing.md) | `scripts/generate_packing_options.py` | 发起异步操作，需续查状态。 |
| 确认装箱方案（`confirmPackingOption`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | [references/apis/packing.md](references/apis/packing.md) | `scripts/confirm_packing_option.py` | 发起异步操作，需续查状态。 |
| 列出计划托盘（`listInboundPlanPallets`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets` | [references/apis/packing.md](references/apis/packing.md) | `scripts/list_inbound_plan_pallets.py` | 同步读取或处理结果。 |
| 列出分仓方案（`listPlacementOptions`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | [references/apis/placement.md](references/apis/placement.md) | `scripts/list_placement_options.py` | 同步读取或处理结果。 |
| 生成分仓方案（`generatePlacementOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions` | [references/apis/placement.md](references/apis/placement.md) | `scripts/generate_placement_options.py` | 发起异步操作，需续查状态。 |
| 确认分仓方案（`confirmPlacementOption`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | [references/apis/placement.md](references/apis/placement.md) | `scripts/confirm_placement_option.py` | 发起异步操作，需续查状态。 |
| 获取货件（`getShipment`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/get_shipment.py` | 同步读取或处理结果。 |
| 列出货件箱信息（`listShipmentBoxes`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/list_shipment_boxes.py` | 同步读取或处理结果。 |
| 列出内容更新预览（`listShipmentContentUpdatePreviews`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | [references/apis/shipment-content-updates.md](references/apis/shipment-content-updates.md) | `scripts/list_shipment_content_update_previews.py` | 同步读取或处理结果。 |
| 生成内容更新预览（`generateShipmentContentUpdatePreviews`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | [references/apis/shipment-content-updates.md](references/apis/shipment-content-updates.md) | `scripts/generate_shipment_content_update_previews.py` | 发起异步操作，需续查状态。 |
| 获取内容更新预览（`getShipmentContentUpdatePreview`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | [references/apis/shipment-content-updates.md](references/apis/shipment-content-updates.md) | `scripts/get_shipment_content_update_preview.py` | 同步读取或处理结果。 |
| 确认内容更新预览（`confirmShipmentContentUpdatePreview`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | [references/apis/shipment-content-updates.md](references/apis/shipment-content-updates.md) | `scripts/confirm_shipment_content_update_preview.py` | 发起异步操作，需续查状态。 |
| 获取交货单（`getDeliveryChallanDocument`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | [references/apis/delivery-windows-and-documents.md](references/apis/delivery-windows-and-documents.md) | `scripts/get_delivery_challan_document.py` | 同步读取或处理结果。 |
| 列出送达窗口（`listDeliveryWindowOptions`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | [references/apis/delivery-windows-and-documents.md](references/apis/delivery-windows-and-documents.md) | `scripts/list_delivery_window_options.py` | 同步读取或处理结果。 |
| 生成送达窗口（`generateDeliveryWindowOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | [references/apis/delivery-windows-and-documents.md](references/apis/delivery-windows-and-documents.md) | `scripts/generate_delivery_window_options.py` | 发起异步操作，需续查状态。 |
| 确认送达窗口（`confirmDeliveryWindowOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | [references/apis/delivery-windows-and-documents.md](references/apis/delivery-windows-and-documents.md) | `scripts/confirm_delivery_window_options.py` | 发起异步操作，需续查状态。 |
| 列出货件商品（`listShipmentItems`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/list_shipment_items.py` | 同步读取或处理结果。 |
| 修改货件名称（`updateShipmentName`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/update_shipment_name.py` | 同步读取或处理结果。 |
| 列出货件托盘（`listShipmentPallets`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/list_shipment_pallets.py` | 同步读取或处理结果。 |
| 取消自配送预约（`cancelSelfShipAppointment`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | [references/apis/self-ship-appointments.md](references/apis/self-ship-appointments.md) | `scripts/cancel_self_ship_appointment.py` | 发起异步操作，需续查状态。 |
| 获取自配送预约槽（`getSelfShipAppointmentSlots`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | [references/apis/self-ship-appointments.md](references/apis/self-ship-appointments.md) | `scripts/get_self_ship_appointment_slots.py` | 同步读取或处理结果。 |
| 生成自配送预约槽（`generateSelfShipAppointmentSlots`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | [references/apis/self-ship-appointments.md](references/apis/self-ship-appointments.md) | `scripts/generate_self_ship_appointment_slots.py` | 发起异步操作，需续查状态。 |
| 预约或改期自配送（`scheduleSelfShipAppointment`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | [references/apis/self-ship-appointments.md](references/apis/self-ship-appointments.md) | `scripts/schedule_self_ship_appointment.py` | 同步读取或处理结果。 |
| 修改货件发货地址（`updateShipmentSourceAddress`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/update_shipment_source_address.py` | 发起异步操作，需续查状态。 |
| 更新货件追踪信息（`updateShipmentTrackingDetails`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | [references/apis/shipments.md](references/apis/shipments.md) | `scripts/update_shipment_tracking_details.py` | 发起异步操作，需续查状态。 |
| 列出运输方案（`listTransportationOptions`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | [references/apis/transportation.md](references/apis/transportation.md) | `scripts/list_transportation_options.py` | 同步读取或处理结果。 |
| 生成运输方案（`generateTransportationOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions` | [references/apis/transportation.md](references/apis/transportation.md) | `scripts/generate_transportation_options.py` | 发起异步操作，需续查状态。 |
| 确认运输方案（`confirmTransportationOptions`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | [references/apis/transportation.md](references/apis/transportation.md) | `scripts/confirm_transportation_options.py` | 发起异步操作，需续查状态。 |
| 列出商品合规信息（`listItemComplianceDetails`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/items/compliance` | [references/apis/prep-compliance-labels.md](references/apis/prep-compliance-labels.md) | `scripts/list_item_compliance_details.py` | 同步读取或处理结果。 |
| 更新商品合规信息（`updateItemComplianceDetails`） | PUT `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/items/compliance` | [references/apis/prep-compliance-labels.md](references/apis/prep-compliance-labels.md) | `scripts/update_item_compliance_details.py` | 发起异步操作，需续查状态。 |
| 生成商品标签（`createMarketplaceItemLabels`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/items/labels` | [references/apis/prep-compliance-labels.md](references/apis/prep-compliance-labels.md) | `scripts/create_marketplace_item_labels.py` | 同步读取或处理结果。 |
| 列出预处理信息（`listPrepDetails`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/items/prepDetails` | [references/apis/prep-compliance-labels.md](references/apis/prep-compliance-labels.md) | `scripts/list_prep_details.py` | 同步读取或处理结果。 |
| 设置预处理信息（`setPrepDetails`） | POST `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/items/prepDetails` | [references/apis/prep-compliance-labels.md](references/apis/prep-compliance-labels.md) | `scripts/set_prep_details.py` | 发起异步操作，需续查状态。 |
| 获取异步操作状态（`getInboundOperationStatus`） | GET `/spApi/developerProxy` -> path：`inbound/fba/2024-03-20/operations/{operationId}` | [references/apis/asynchronous-operations.md](references/apis/asynchronous-operations.md) | `scripts/get_inbound_operation_status.py` | 同步读取或处理结果。 |
| 获取旧版预处理说明（`getPrepInstructions`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/prepInstructions` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_prep_instructions.py` | 同步读取或处理结果。 |
| 获取箱唛标签（`getLabels`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/shipments/{shipmentId}/labels` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_labels.py` | 同步读取或处理结果。 |
| 获取提单（`getBillOfLading`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/shipments/{shipmentId}/billOfLading` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_bill_of_lading.py` | 同步读取或处理结果。 |
| 查询旧版货件（`getShipments`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/shipments` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_shipments.py` | 同步读取或处理结果。 |
| 按旧版货件查询商品（`getShipmentItemsByShipmentId`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/shipments/{shipmentId}/items` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_shipment_items_by_shipment_id.py` | 同步读取或处理结果。 |
| 查询旧版货件商品（`getShipmentItems`） | GET `/spApi/developerProxy` -> path：`fba/inbound/v0/shipmentItems` | [references/apis/legacy-v0.md](references/apis/legacy-v0.md) | `scripts/get_shipment_items.py` | 同步读取或处理结果。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查本地依赖；缺失时先安装依赖，不在本技能实现授权或令牌逻辑。按 [接口参考](references/api.md#业务前置条件) 核对授权角色与商品入库资格。

先阅读 [接口参考](references/api.md) 及任务对应的分组文档。依赖检测、认证兼容与字段要求均在接口参考中说明。

## 入仓执行流程

1. 确认目标店铺、工作流阶段及已有标识。已有计划或货件时先只读恢复，避免重复创建；根据 [工作流](references/workflows.md) 选择已知箱规、Pack Later、India 或内容更新路径。
2. 写操作前核对用户意图和目标。取消计划、确认装箱、确认分仓、确认内容预览、确认送达窗口、取消或安排预约、确认运输这八类提交操作，须先展示关键选择并取得明确确认；确认运输前展示各货件方案、费用、币种、时效及有效期，不默认选择收费项。
3. 已知箱规按“创建计划 → 装箱 → 分仓 → 运输”推进；Pack Later 与 India 的装箱和分仓顺序不同，按工作流执行。每步异步操作只在状态成功后进入下游。
4. 异步发起后保留任务标识并显式查询状态。进行中则停止本轮推进，失败则展示问题并停止下游写入；本技能不自动轮询、翻页、换参数试探或重放写请求。响应不确定时先查状态或只读恢复。
5. 取得货件确认标识后获取标签或提单，用户需要文件时立即下载当次响应中的文档链接。下载与跨版本要求见 [接口参考](references/api.md)。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时成功读取/生成缓存，写入与提交不缓存。失败或空结果时，不得自动换参数、翻页或连续试探；需要继续调用时先征得用户同意。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-fulfillment-inbound-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、结果中已有的常见计数字段（如 `total`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力（以网关实际计费为准） （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **清晰展示状态**：注明店铺、区域、市场、工作流阶段和关联标识，用表格展示方案、货件划分、费用、币种、有效期及执行结果。区分请求被接受、异步执行成功和货件后续状态。
- **区分标识**：计划、异步任务、装箱组、方案、货件和标签标识不可混用；来源与跨版本关系见 [标识参考](references/identifiers.md)。
- **展示关键选择**：装箱确认展示组别、支持配置和激励；分仓确认展示全部货件、费用或折扣；预约展示 FC、货件、日期时间、预约槽与当前预约；内容更新展示新旧差异、运输影响和有效期。
- **保留执行进度**：逐步保留计划、货件及异步任务标识；方案重新生成后重新核对选择，不按列表序号默认确认。
- **保护店铺**：错误处理按 [接口参考](references/api.md) 和 [店铺保护与重试](references/spapi-protection.md) 执行。先向用户说明店铺保护，再给出原因、处理动作和等待时间，保留已取得的数据。
- **说明结果边界**：仅展示实际返回字段；空箱或托盘结果可能与当前流程阶段有关。市场与流程差异见 [市场限制](references/marketplace-constraints.md)，详细执行路径见 [工作流](references/workflows.md)。

## 使用示例

### 新建入仓计划

用户：按这批 SKU 和箱规安排发往亚马逊仓库。

核对已授权店铺与商品准备状态，创建计划并逐步查询异步结果，展示装箱、分仓和运输方案，按用户确认推进提交。

### 恢复已有货件

用户：刚才确认运输超时了，看看是否已经成功。

使用已保留的任务标识查询状态，必要时读取计划和货件，说明当前结果后再判断下一步。

### 获取标签与提单

用户：下载这个入库货件的箱唛和提单。

从货件读取正确的标签标识，取得当次文档链接并及时下载，返回文件及其关联货件。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
