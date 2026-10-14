# Reference archive: linkfox-amazon-store-fulfillment-inbound

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
    "path": "inbound/fba/2024-03-20/inboundPlans",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-fulfillment-inbound/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `contentType` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-fulfillment-inbound
description: 亚马逊 FBA 入仓与 Fulfillment Inbound 全流程管理。用于创建和管理 inbound plan，处理装箱、placement、shipment、货件内容更新、送达窗口、自配送预约、运输方案、商品合规、预处理、箱唛标签、提单及异步操作状态。用户提到 FBA 入库计划、Send to Amazon、创建入仓计划、packing option、placement option、transportation option、货件箱唛、入仓标签、送仓预约、shipmentConfirmationId、createInboundPlan、Fulfillment Inbound API、v2024-03-20 或 v0 入仓接口时触发。即使未明确说“Fulfillment Inbound”，只要希望把库存发往亚马逊运营中心并完成建仓、装箱、分仓、运输或交仓步骤，也应触发此技能。
---

# Amazon 店铺 Fulfillment Inbound

本 Skill 覆盖 Amazon Fulfillment Inbound `v2024-03-20` 的 45 个 operation，以及仍需配合新流程使用的 6 个 `v0` 查询/文档 operation。所有请求继续使用 Amazon Store 系列的生产链路：`proxy_call` 的 `spApi/developerProxy`，由服务端通过 `sellerId + region` 解析授权。

## Prerequisites（必须先读）

2. 通过 auth Skill 选定店铺，取得 `sellerId` 与 `region`。`region` 仅允许 `NA`、`EU`、`FE`。
4. 先读与任务匹配的分组文档；完整契约入口见 `references/api.md`（见本文对应归档章节）。

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 工作方式

每个公开脚本只代表一个固定 operation，并且一次执行最多调用一次网关。统一执行器负责：

- 校验公共字段、path/query/body、枚举、分页上限和关键嵌套约束；
- 对 path segment 与 query 参数进行百分号编码；
- 将 v0 CLI 的 lowerCamelCase 参数映射为 Amazon 要求的 PascalCase wire 名称；
- 识别 200/201/202/204 成功响应并解析 JSON；
- 对异步响应返回显式 `nextAction`，但不自动轮询；
- 保存完整响应，大响应只在 stdout 展示摘要。

调用格式：



公共参数：

| 参数 | 必填 | 说明 |
|---|---|---|
| `sellerId` | 是 | 已授权 Seller ID |
| `region` | 是 | `NA` / `EU` / `FE` |
| path/query 参数 | 条件 | 使用各 operation 文档中的 lowerCamelCase 名称 |
| `requestBody` | 条件 | Amazon JSON body；推荐显式传此对象，也兼容将 body 字段放在顶层 |
| `confirmWrite` | 提交类操作必填 | 用户明确确认目标和选择后传布尔值 `true`；8 个确定性提交操作缺少该值时脚本会在网关调用前拒绝 |
| `skipDepCheck` | 否 | 仅本地调试使用 |

示例：



## 选择 operation

| 分组 | 用途 | 详细参数与脚本 |
|---|---|---|
| Inbound Plans | 创建、读取、取消、改名、查看 plan 内容 | `inbound-plans.md`（见本文对应归档章节） |
| Packing | 生成/确认装箱方案、提交箱规、查看 packing group | `packing.md`（见本文对应归档章节） |
| Placement | 生成、列出、确认分仓方案 | `placement.md`（见本文对应归档章节） |
| Shipments | 读取货件、箱/件/托盘、名称和地址、tracking | `shipments.md`（见本文对应归档章节） |
| Content Updates | 预览并确认已建货件内容变更 | `shipment-content-updates.md`（见本文对应归档章节） |
| Delivery | delivery window 与 delivery challan | `delivery-windows-and-documents.md`（见本文对应归档章节） |
| Self-Ship | India 自配送预约槽与预约 | `self-ship-appointments.md`（见本文对应归档章节） |
| Transportation | 生成、比较、确认运输方案 | `transportation.md`（见本文对应归档章节） |
| Prep / Compliance / Labels | 预处理、合规和商品标签 | `prep-compliance-labels.md`（见本文对应归档章节） |
| Async Status | 查询 `operationId` 的执行状态 | `asynchronous-operations.md`（见本文对应归档章节） |
| Retained v0 | prep instructions、箱唛、BOL、旧货件查询 | `legacy-v0.md`（见本文对应归档章节） |

## 执行规则

1. 先确认当前工作流阶段及已有 ID；ID 的来源和跨版本映射见 `references/identifiers.md`（见本文对应归档章节）。已有 plan/shipment 时优先只读恢复，不重复创建。
2. 写操作前确认用户意图和目标店铺。以下 8 个确定性提交操作必须在执行前向用户展示关键选择并取得明确确认：`cancelInboundPlan`、`confirmPackingOption`、`confirmPlacementOption`、`confirmShipmentContentUpdatePreview`、`confirmDeliveryWindowOptions`、`cancelSelfShipAppointment`、`scheduleSelfShipAppointment`、`confirmTransportationOptions`。
3. `confirmTransportationOptions` 可能接受运输费用；确认前展示每个 shipment 的 option、费用、币种、时效与 expiration。不得替用户默认选择收费项。
4. 19 个异步发起 operation 返回 `operationId` 后，只调用 `amazon_store_fulfillment_inbound__get_inbound_operation_status` 操作 查询。`IN_PROGRESS` 时停止并告知稍后再查；`FAILED` 时展示 `operationProblems`，不得进入下游写步骤；仅 `SUCCESS` 可继续。
5. 脚本层不自动翻页、轮询、换参数试探或重放 POST/PUT。服务端按 `sellerId + region` 解析授权上下文；Agent 不读取或传递 raw access token，也不假设服务端会透明重试。授权失败或 429/500/503、超时造成结果不确定时停止，优先通过用户确认后的 status/read operation 恢复状态。
6. `updateInboundPlanName`、`updateShipmentName` 的 204 空 body 是成功，不当作解析失败。
7. `getLabels` / `getBillOfLading` 必须使用 `getShipment` 返回的 `shipmentConfirmationId`；脚本同时接受该别名。下载 URL 可能很快过期，应在取得后立即下载，不要长期保存 URL。

完整标准路径、Pack Later、India、自有承运人和 shipment content update 流程见 `references/workflows.md`（见本文对应归档章节）。市场限制见 `references/marketplace-constraints.md`（见本文对应归档章节）。

## 输出与错误处理

- 完整响应保存到 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-fulfillment-inbound-<timestamp>.json`；stdout 会打印实际路径。
- 响应不超过 8 KB 时打印完整 JSON；更大时打印摘要；`--inline` 强制打印完整 JSON。
- 始终先判断 `developerProxy.errcode`，再判断 `httpStatus`，最后读取 operation 结果字段。
- 401/402、API Key、授权、积分或余额问题按 `references/onboarding.md`（见本文对应归档章节） 处理。
- Amazon 返回 400/403/404/409/413/415/422 时，修正输入或流程状态后由用户决定是否再次调用。

## 参考路由

- 字段、响应、分页、错误语义：读 `references/api.md`（见本文对应归档章节）。
- 业务流程选择：读 `references/workflows.md`（见本文对应归档章节）。
- ID 产生和 v2024/v0 映射：读 `references/identifiers.md`（见本文对应归档章节）。
- 国家/市场差异：读 `references/marketplace-constraints.md`（见本文对应归档章节）。
- 某个 operation 的 method/path/body/script：只读对应的 `references/apis/*.md` 分组文档。

问题反馈使用 `skillName: linkfox-amazon-store-fulfillment-inbound`，并附脱敏后的 operation、关联 ID 与 `developerProxy` 响应。

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

# Fulfillment Inbound API 参考

本 Skill 通过 LinkFox `proxy_call` 的 `spApi/developerProxy` 调用 Amazon Fulfillment Inbound API，覆盖：

- Fulfillment Inbound `v2024-03-20`：45 个 operation。
- Fulfillment Inbound `v0`：6 个 Amazon 仍保留的查询和文档 operation。
- 总计 51 个 operation：28 GET、16 POST、7 PUT。

官方基线：

- [Fulfillment Inbound API 概述](https://developer-docs.amazon.com/sp-api/docs/fulfillment-inbound-api)
- [v2024-03-20 Reference](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v2024-03-20)
- [v2024-03-20 OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-inbound-api-model/fulfillmentInbound_2024-03-20.json)
- [v0 OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-inbound-api-model/fulfillmentInboundV0.json)

## 调用契约

调用规范：

- HTTP 方法：对 LinkFox 网关固定使用 POST；网关 payload 中的 `method` 才是 Amazon operation 的 GET/POST/PUT。
- 超时：150 秒。

所有入口脚本接收一个 JSON 字符串。公共字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `sellerId` | 是 | 已授权的 Amazon Seller ID |
| `region` | 是 | `NA` / `EU` / `FE` |
| `requestBody` | 条件 | Amazon operation 的 JSON request body；不将本地控制字段混入其中 |
| `confirmWrite` | 提交类操作 | 用户明确确认后传布尔值 `true` |
| `skipDepCheck` | 否 | 仅调试时跳过本地 auth skill 探测 |

脚本根据 operation 固定 Amazon `method` 和 `path`；调用方不应传原始 `method`、`path`、`queryString` 或 token。`developerProxy` 使用 `sellerId + region` 在服务端解析授权。


网关原始响应保留在 `developerProxy`，常见字段为 `errcode`、`httpStatus`、`contentType`、`body`。脚本同时将成功 JSON body 解析为 operation 结果字段。

## operation 索引

| 分组 | 数量 | 参考 |
|---|---:|---|
| Inbound Plans | 7 | `inbound-plans.md`（见本文对应归档章节） |
| Packing | 7 | `packing.md`（见本文对应归档章节） |
| Placement | 3 | `placement.md`（见本文对应归档章节） |
| Shipments | 7 | `shipments.md`（见本文对应归档章节） |
| Shipment Content Updates | 4 | `shipment-content-updates.md`（见本文对应归档章节） |
| Delivery Windows / Documents | 4 | `delivery-windows-and-documents.md`（见本文对应归档章节） |
| Self-Ship Appointments | 4 | `self-ship-appointments.md`（见本文对应归档章节） |
| Transportation | 3 | `transportation.md`（见本文对应归档章节） |
| Prep / Compliance / Labels | 5 | `prep-compliance-labels.md`（见本文对应归档章节） |
| Asynchronous Operations | 1 | `asynchronous-operations.md`（见本文对应归档章节） |
| 保留 v0 | 6 | `legacy-v0.md`（见本文对应归档章节） |

## 异步操作

19 个 operation 会发起异步处理：18 个返回 HTTP 202，`generateSelfShipAppointmentSlots` 返回 HTTP 201。响应中的 `operationId` 只用于：

```text
getInboundOperationStatus(operationId)
  ├─ IN_PROGRESS → 稍后由调用方再查
  ├─ SUCCESS     → 再进入下一个工作流步骤
  └─ FAILED      → 输出 operationProblems，停止下游写操作
```

HTTP 201/202 不代表业务已完成。脚本单次运行不隐式轮询、不自动执行下一步。

## request body 语义

- 有必填字段的 body：传 `requestBody` 对象并在本地校验必填键。
- OpenAPI 要求 body 但没有必填属性：允许 `requestBody: {}`，例如 `generatePlacementOptions`。
- OpenAPI 无 body：不向上游发送 body，例如 `generatePackingOptions`。
- HTTP 204：`updateInboundPlanName` 和 `updateShipmentName` 成功时 body 为空，不当作 JSON 解析错误。

## 分页

v2024 的分页接口从响应 `pagination.nextToken` 取值，下一次请求传 `paginationToken`。必须保留首页的所有过滤字段；不自动拉取全部页。

v0 的 Amazon wire 使用 `NextToken` 等 PascalCase 名称；脚本 CLI 统一接收 `nextToken` 等 lowerCamelCase 名称并自动映射。

## 错误处理

- `errcode != 200`：保留网关错误，不尝试解析为 Amazon 成功响应。
- Amazon HTTP 400/403/404/409/413/415/422：修正请求或工作流状态后再调用。
- HTTP 429/500/503：停止并向用户报告；确认、取消、预约以及其他 POST/PUT 在响应不确定时不得由脚本或 Agent 自动重放。服务端按 `sellerId + region` 解析授权上下文；Agent 不读取或传递 raw access token，也不假设服务端会透明刷新或重试。
- auth / billing 错误：按 [onboarding.md](onboarding.md) 处理。
- 上报问题时使用 `skillName: linkfox-amazon-store-fulfillment-inbound`，保留脱敏后的 `developerProxy`、operation 和关联 ID。

## MCP 示例见本文开头



公开脚本会固定并校验 `method`、`path`、query 和 body；面向用户调用时应使用对应 operation 脚本，而不是自行拼接上述网关 payload。

## Feedback

问题反馈地址：`https://skill-api.linkfox.com/api/v1/public/feedback`。自动检测到持续的授权错误、白名单拒绝、契约不一致或 Amazon 响应结构变化时，附带 `skillName`、operation、脱敏后的关联 ID 与响应摘要。

## Archived reference: apis/asynchronous-operations.md

# Asynchronous Operations（1 operation）

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `getInboundOperationStatus`<br>`amazon_store_fulfillment_inbound__get_inbound_operation_status` 操作 | GET / 200 | `/inbound/fba/2024-03-20/operations/{operationId}` | 必填 `operationId`；返回 `operation`、`operationId`、`operationStatus`、`operationProblems` |

`operationStatus` 只有：

| 状态 | 处理 |
|---|---|
| `IN_PROGRESS` | 记录 operation ID，稍后由调用方再次查询；不进入下游步骤 |
| `SUCCESS` | 只表示该一个 operation 完成；可通过下一个 list/get operation 读取结果 |
| `FAILED` | 展示 `operationProblems`，停止下游写操作；修正输入或工作流后由用户决定是否重新发起 |

## 异步发起 operation 清单（19）

- Plans：`createInboundPlan`、`cancelInboundPlan`
- Packing：`generatePackingOptions`、`confirmPackingOption`、`setPackingInformation`
- Placement：`generatePlacementOptions`、`confirmPlacementOption`
- Content updates：`generateShipmentContentUpdatePreviews`、`confirmShipmentContentUpdatePreview`
- Delivery windows：`generateDeliveryWindowOptions`、`confirmDeliveryWindowOptions`
- Self-ship：`cancelSelfShipAppointment`、`generateSelfShipAppointmentSlots`
- Shipment updates：`updateShipmentSourceAddress`、`updateShipmentTrackingDetails`
- Transportation：`generateTransportationOptions`、`confirmTransportationOptions`
- Item data：`updateItemComplianceDetails`、`setPrepDetails`

其中 `generateSelfShipAppointmentSlots` 返回 HTTP 201，其余 18 个返回 HTTP 202。两种 HTTP 状态都必须继续查 `operationStatus`。

本 Skill 不隐式轮询。只有用户或上层工作流显式请求查状态时，才再运行本脚本。

## Archived reference: apis/delivery-windows-and-documents.md

# Delivery Windows 与 Documents（4 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `getDeliveryChallanDocument`<br>`amazon_store_fulfillment_inbound__get_delivery_challan_document` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument` | 必填 plan/shipment ID；返回 `documentDownload`；仅 India PCP shipment |
| `listDeliveryWindowOptions`<br>`amazon_store_fulfillment_inbound__list_delivery_window_options` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | 必填 plan/shipment ID；可选 `pageSize` 1–100、`paginationToken`；返回 window IDs、dates、availability/validity |
| `generateDeliveryWindowOptions`<br>`amazon_store_fulfillment_inbound__generate_delivery_window_options` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions` | 必填 plan/shipment ID；无 body；返回 `operationId` |
| `confirmDeliveryWindowOptions`<br>`amazon_store_fulfillment_inbound__confirm_delivery_window_options` 操作 | POST / 202<br>异步・确认 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation` | 必填 plan/shipment/window ID；无 body；返回 `operationId` |

## Delivery window 规则

- 自有承运人选项通常需要为 placement 中的每个 shipment 生成和确认 delivery window，以 transportation option `preconditions` 为准。
- 确认前展示 `startDate`、`endDate`、`availabilityType` 和 `validUntil`。
- 过期后重新 generate/list，不确认旧 ID。
- `confirmDeliveryWindowOptions` 是高影响操作，应取得用户明确确认。

## Challan 文档

`getDeliveryChallanDocument` 返回的 URI 可能有过期时间。如用户要下载，应使用当次 Amazon 响应的 HTTPS URI 立即下载；不接受用户传入的任意 URL。

## Archived reference: apis/inbound-plans.md

# Inbound Plans（7 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listInboundPlans`<br>`amazon_store_fulfillment_inbound__list_inbound_plans` 操作 | GET / 200 | `/inboundPlans` | 可选 `pageSize` 1–30、`paginationToken`、`status` (`ACTIVE/VOIDED/SHIPPED`)、`sortBy` (`LAST_UPDATED_TIME/CREATION_TIME`)、`sortOrder` (`ASC/DESC`)；返回 `inboundPlans` + `pagination` |
| `createInboundPlan`<br>`amazon_store_fulfillment_inbound__create_inbound_plan` 操作 | POST / 202<br>异步 | `/inboundPlans` | body 必填 `destinationMarketplaces`、`items`、`sourceAddress`，可选 `name`；返回 `inboundPlanId` + `operationId` |
| `getInboundPlan`<br>`amazon_store_fulfillment_inbound__get_inbound_plan` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}` | 必填 `inboundPlanId`；返回 plan 状态、marketplaces、packing/placement options 和 shipments 摘要 |
| `listInboundPlanBoxes`<br>`amazon_store_fulfillment_inbound__list_inbound_plan_boxes` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/boxes` | 必填 `inboundPlanId`；可选 `pageSize` 1–1000、`paginationToken` |
| `cancelInboundPlan`<br>`amazon_store_fulfillment_inbound__cancel_inbound_plan` 操作 | PUT / 202<br>异步・取消 | `/inboundPlans/{inboundPlanId}/cancellation` | 必填 `inboundPlanId`；无 body；返回 `operationId` |
| `listInboundPlanItems`<br>`amazon_store_fulfillment_inbound__list_inbound_plan_items` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/items` | 必填 `inboundPlanId`；可选 `pageSize` 1–1000、`paginationToken` |
| `updateInboundPlanName`<br>`amazon_store_fulfillment_inbound__update_inbound_plan_name` 操作 | PUT / 204 | `/inboundPlans/{inboundPlanId}/name` | 必填 `inboundPlanId`；body 必填 `name`；成功响应无 body |

## Create 要点

- `destinationMarketplaces` 当前每个 plan 只传一个 marketplace ID。
- `items` 中每项的关键字段是 `msku`、`quantity`、`prepOwner`、`labelOwner`；按商品需要增加 `expiration` 或 `manufacturingLotCode`。
- `sourceAddress` 至少包含 `name`、`addressLine1`、`city`、两位大写 `countryCode`、`phoneNumber`、`postalCode`。创建后如需修改单个 shipment 的发货地址，使用 `updateShipmentSourceAddress`。
- 保留 `createInboundPlan` 返回的两个 ID：`operationId` 用于查状态，`inboundPlanId` 用于后续全部 plan operation。

`cancelInboundPlan` 是不可隐式执行的高影响操作；执行前展示 plan ID 和当前状态并取得用户明确确认。

## Archived reference: apis/legacy-v0.md

# 保留的 Fulfillment Inbound v0（6 operations）

Amazon 官方仍保留以下 6 个 v0 operation。本 Skill 不包含已废弃的 v0 创建、修改、运输估算或确认 operation。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `getPrepInstructions`<br>`amazon_store_fulfillment_inbound__get_prep_instructions` 操作 | GET / 200 | `/fba/inbound/v0/prepInstructions` | CLI 必填 `shipToCountryCode`；通常传 `sellerSKUList` / `asinList` 至少一组，各最多 50；返回 prep instructions 和 invalid SKU/ASIN |
| `getLabels`<br>`get_labels` 操作 | GET / 200 | `/fba/inbound/v0/shipments/{shipmentId}/labels` | path 使用 `shipmentConfirmationId`；CLI 必填 `pageType`、`labelType`；按模式可传 packages/pallets/page 参数；返回 `payload.DownloadURL` |
| `getBillOfLading`<br>`amazon_store_fulfillment_inbound__get_bill_of_lading` 操作 | GET / 200 | `/fba/inbound/v0/shipments/{shipmentId}/billOfLading` | path 使用 `shipmentConfirmationId`；返回 `payload.DownloadURL` |
| `getShipments`<br>`amazon_store_fulfillment_inbound__get_shipments` 操作 | GET / 200 | `/fba/inbound/v0/shipments` | CLI 必填 `queryType`、`marketplaceId`；其他参数受 QueryType 约束；返回 `ShipmentData`、`NextToken` |
| `getShipmentItemsByShipmentId`<br>`amazon_store_fulfillment_inbound__get_shipment_items_by_shipment_id` 操作 | GET / 200 | `/fba/inbound/v0/shipments/{shipmentId}/items` | 必填 legacy `shipmentId`；`marketplaceId` 已废弃，不传；返回 `ItemData`、`NextToken` |
| `getShipmentItems`<br>`amazon_store_fulfillment_inbound__get_shipment_items` 操作 | GET / 200 | `/fba/inbound/v0/shipmentItems` | CLI 必填 `queryType`、`marketplaceId`；其他参数受 QueryType 约束；返回 `ItemData`、`NextToken` |

## v0 query 规则

v0 参数大小写是 Amazon wire 契约的一部分。脚本 CLI 只需传项目统一的 lowerCamelCase 名称，执行器自动映射：`marketplaceId → MarketplaceId`、`queryType → QueryType`、`nextToken → NextToken`。

`getShipments.queryType`：

- `SHIPMENT`：传 `shipmentStatusList` 和/或 `shipmentIdList`（最多 999）。
- `DATE_RANGE`：传 `lastUpdatedAfter` / `lastUpdatedBefore`。
- `NEXT_TOKEN`：传上一页的 `nextToken`，不混用新筛选条件。

`getShipmentItems.queryType`：

- `DATE_RANGE`：传 `lastUpdatedAfter` / `lastUpdatedBefore`。
- `NEXT_TOKEN`：传 `nextToken`，只继续上一页查询。

v0 数组 query 使用该 API 的 CSV wire 格式，不复用 v2024 `mskus` 的重复 key 规则。

## Labels 和 BOL

v2024 工作流中，先：

```text
getShipment(inboundPlanId, shipmentId)
  → shipmentConfirmationId
  → getLabels / getBillOfLading 的 v0 {shipmentId} path
```

- 不要将 v2024 38 字符 `shipmentId` 直接作为 label/BOL 路径值。
- CLI `packageLabelsToPrint` 要与 v2024 `listShipmentBoxes` 返回的 `boxId` 一致，否则 Amazon 可返回 `IncorrectPackageIdentifier`。
- CLI `labelType` 允许 `BARCODE_2D`、`UNIQUE`、`PALLET`；`pageType` 是 marketplace 相关枚举。
- Non-Partnered LTL labels 需要 `pageSize` 和 `pageStartIndex`，`pageSize` 最大 1000。
- `numberOfPallets` 为每个 pallet 返回四张相同标签。
- labels 和 BOL 的 `DownloadURL` 仅有效约 15 秒；如用户要文件，调用者应在同一任务中取得 URL 后立即下载。

下载时只使用 Amazon 当次响应的 HTTPS URL，不接受用户提供的任意 URL。

## Archived reference: apis/packing.md

# Packing（7 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listPackingGroupBoxes`<br>`amazon_store_fulfillment_inbound__list_packing_group_boxes` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes` | 必填 `inboundPlanId`、`packingGroupId`；可选 `pageSize` 1–100、`paginationToken` |
| `listPackingGroupItems`<br>`amazon_store_fulfillment_inbound__list_packing_group_items` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items` | 必填 `inboundPlanId`、`packingGroupId`；可选 `pageSize` 1–100、`paginationToken` |
| `setPackingInformation`<br>`amazon_store_fulfillment_inbound__set_packing_information` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/packingInformation` | body 必填 `packageGroupings`；每项必填 `boxes`，并在 `packingGroupId` / `shipmentId` 中二选一；返回 `operationId` |
| `listPackingOptions`<br>`amazon_store_fulfillment_inbound__list_packing_options` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/packingOptions` | 必填 `inboundPlanId`；可选 `pageSize` 1–20、`paginationToken`；返回 `packingOptions` |
| `generatePackingOptions`<br>`amazon_store_fulfillment_inbound__generate_packing_options` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/packingOptions` | 必填 `inboundPlanId`；无 body；返回 `operationId` |
| `confirmPackingOption`<br>`amazon_store_fulfillment_inbound__confirm_packing_option` 操作 | POST / 202<br>异步・确认 | `/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation` | 必填 `inboundPlanId`、`packingOptionId`；无 body；返回 `operationId` |
| `listInboundPlanPallets`<br>`amazon_store_fulfillment_inbound__list_inbound_plan_pallets` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/pallets` | 必填 `inboundPlanId`；可选 `pageSize` 1–1000、`paginationToken` |

## `setPackingInformation` 规则

- 已知箱规且 placement 尚未确认：每个 grouping 传已确认 packing option 中的 `packingGroupId`，省略 `shipmentId`。
- Pack Later 且 placement 已确认：每个 grouping 传已确认 placement 中的 `shipmentId`，省略 `packingGroupId`。
- India custom-placement 是特例：官方 India 用例要求先为选定 placement 的所有 `shipmentId` 设置 packing information，然后才 `confirmPlacementOption`。
- `boxes` 每个 grouping 1–5000。一般包含 `contentInformationSource`、dimensions、weight、quantity 和 items。
- `contentInformationSource` 为 `BARCODE_2D` 或 `MANUAL_PROCESS` 时，`items` 应保留为 `null`，不能在清理 JSON 时擅自删除。
- 重新设置箱规后，之前生成的 placement options 失效，要重新 generate/list。

`confirmPackingOption` 前先展示 packing groups、supported configurations 和可能的 incentive；不按列表序号隐式确认。

## Archived reference: apis/placement.md

# Placement（3 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listPlacementOptions`<br>`amazon_store_fulfillment_inbound__list_placement_options` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/placementOptions` | 必填 `inboundPlanId`；可选 `pageSize` 1–20、`paginationToken`；返回 `placementOptions` |
| `generatePlacementOptions`<br>`amazon_store_fulfillment_inbound__generate_placement_options` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/placementOptions` | body 必须存在但允许 `{}`；India 可传 `customPlacement`；返回 `operationId` |
| `confirmPlacementOption`<br>`amazon_store_fulfillment_inbound__confirm_placement_option` 操作 | POST / 202<br>异步・确认 | `/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation` | 必填 `inboundPlanId`、`placementOptionId`；无 body；返回 `operationId` |

## 选择规则

- 一个 inbound plan 只确认一个 placement option。
- 每个 option 可能产生一个或多个 `shipmentId`，并包含 placement fee 或 discount。
- 确认前展示 `placementOptionId`、所有 shipment 划分、费用/折扣和有效期。
- 修改 packing information 后必须重新生成 placement options。
- India `customPlacement` 是数组，每项必填 `warehouseId` 和 `items`；不用于其他 marketplace。

`confirmPlacementOption` 是高影响操作。其成功后通过 `getShipment` 取得 `shipmentConfirmationId`，该值才是 v0 labels/BOL 应使用的标签 shipment ID。

## Archived reference: apis/prep-compliance-labels.md

# Prep、Compliance 与 Marketplace Labels（5 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listItemComplianceDetails`<br>`amazon_store_fulfillment_inbound__list_item_compliance_details` 操作 | GET / 200 | `/items/compliance` | query 必填 `mskus` 1–100 和 `marketplaceId`；返回 `complianceDetails`；India 专用 |
| `updateItemComplianceDetails`<br>`amazon_store_fulfillment_inbound__update_item_compliance_details` 操作 | PUT / 202<br>异步 | `/items/compliance` | query 必填 `marketplaceId`；body 必填 `msku`、`taxDetails`；返回 `operationId`；India 专用 |
| `createMarketplaceItemLabels`<br>`amazon_store_fulfillment_inbound__create_marketplace_item_labels` 操作 | POST / 200<br>文档 | `/items/labels` | body 必填 `labelType`、`marketplaceId`、`mskuQuantities` 1–100；可选 `pageType`、`localeCode`、width/height；返回 `documentDownloads` |
| `listPrepDetails`<br>`amazon_store_fulfillment_inbound__list_prep_details` 操作 | GET / 200 | `/items/prepDetails` | query 必填 `marketplaceId`、`mskus` 1–100；返回 `mskuPrepDetails` |
| `setPrepDetails`<br>`amazon_store_fulfillment_inbound__set_prep_details` 操作 | POST / 202<br>异步 | `/items/prepDetails` | body 必填 `marketplaceId`、`mskuPrepDetails`；返回 `operationId` |

## MSKU query 编码

`listItemComplianceDetails` 和 `listPrepDetails` 使用重复 key，不使用 CSV：

```text
mskus=SKU-1&mskus=SKU-2&marketplaceId=...
```

Amazon 要求 MSKU 中的下列字符在最终 URL 中双重 percent encode：

```text
% → %2525
+ → %252B
, → %252C
```

不能将过长 MSKU 列表静默截断。如 LinkFox `queryString` 超过限制，应报错并让调用方显式分批。

## Prep details 一致性

- 先 `setPrepDetails` 并等待异步成功，再 `listPrepDetails`。
- Seller Central 中设置的 prep details 不会由该 operation 返回。
- US marketplace 要求卖家在入库前完成商品 prep 和 label。

## Marketplace item label 文档

`documentDownloads[]` 包含 `downloadType`、`uri` 和可选 `expiration`。如用户需要文件，只使用当次响应的 HTTPS URI 立即下载，不接受任意 URL 作为输入。

## Archived reference: apis/self-ship-appointments.md

# Self-Ship Appointments（4 operations）

路径版本：`/inbound/fba/2024-03-20`。仅适用于 `MX`、`BR`、`EG`、`SA`、`AE`、`IN` marketplaces。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `cancelSelfShipAppointment`<br>`amazon_store_fulfillment_inbound__cancel_self_ship_appointment` 操作 | PUT / 202<br>异步・取消 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation` | 必填 plan/shipment ID；body 必须存在，可为 `{}` 或包含 `reasonComment`；返回 `operationId` |
| `getSelfShipAppointmentSlots`<br>`amazon_store_fulfillment_inbound__get_self_ship_appointment_slots` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | 必填 plan/shipment ID；可选 `pageSize` 1–100、`paginationToken`；返回 `selfShipAppointmentSlotsAvailability` |
| `generateSelfShipAppointmentSlots`<br>`amazon_store_fulfillment_inbound__generate_self_ship_appointment_slots` 操作 | POST / 201<br>异步 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots` | body 必须存在，可为 `{}`；可选 `desiredStartDate`、`desiredEndDate`；返回 `operationId` |
| `scheduleSelfShipAppointment`<br>`amazon_store_fulfillment_inbound__schedule_self_ship_appointment` 操作 | POST / 200<br>预约/改期 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule` | 必填 plan/shipment/slot ID；body 必须存在，可为 `{}`；改期时必填 `reasonComment`；同步返回 `selfShipAppointmentDetails` |

## 执行顺序

```text
getShipment → 确认 amazonReferenceId 存在
generateSelfShipAppointmentSlots → getInboundOperationStatus == SUCCESS
getSelfShipAppointmentSlots → 展示 slot/date/expiration
用户明确确认
scheduleSelfShipAppointment
```

不传期望日期时，Amazon 默认提供未来 42 天的可用 slot。`slotId` 与当前 plan + shipment 绑定；生成新 slots 后不复用旧 ID。

`scheduleSelfShipAppointment` 和 `cancelSelfShipAppointment` 均是高影响操作。执行前显示 FC、shipment、日期时间、slot ID 和当前 appointment，并取得用户明确确认。

## Archived reference: apis/shipment-content-updates.md

# Shipment Content Updates（4 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listShipmentContentUpdatePreviews`<br>`amazon_store_fulfillment_inbound__list_shipment_content_update_previews` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | 必填 plan/shipment ID；可选 `pageSize` 1–20、`paginationToken` |
| `generateShipmentContentUpdatePreviews`<br>`amazon_store_fulfillment_inbound__generate_shipment_content_update_previews` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews` | body 必填 `boxes`、`items`；返回 `operationId` |
| `getShipmentContentUpdatePreview`<br>`amazon_store_fulfillment_inbound__get_shipment_content_update_preview` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}` | 必填 plan/shipment/preview ID；返回 `requestedUpdates`、`transportationOption`、`expiration` |
| `confirmShipmentContentUpdatePreview`<br>`amazon_store_fulfillment_inbound__confirm_shipment_content_update_preview` 操作 | POST / 202<br>异步・确认 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation` | 必填 plan/shipment/preview ID；无 body；返回 `operationId` |

这一组操作用于 transportation 已确认后的 shipment 内容调整。不要直接确认 list 中的第一项；先 get preview，向用户展示内容变更、新 transportation option/费用和 `expiration`。

只能在同一 plan + shipment 中使用 preview ID。已过期或重新生成后的旧 preview 不得确认。

## Archived reference: apis/shipments.md

# Shipments（7 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `getShipment`<br>`amazon_store_fulfillment_inbound__get_shipment` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}` | 必填 `inboundPlanId`、`shipmentId`；返回 placement、destination、status，以及可用时的 `shipmentConfirmationId`、`amazonReferenceId`、transport/tracking |
| `listShipmentBoxes`<br>`amazon_store_fulfillment_inbound__list_shipment_boxes` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes` | 必填 plan/shipment ID；可选 `pageSize` 1–1000、`paginationToken` |
| `listShipmentItems`<br>`amazon_store_fulfillment_inbound__list_shipment_items` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items` | 必填 plan/shipment ID；可选 `pageSize` 1–1000、`paginationToken` |
| `listShipmentPallets`<br>`amazon_store_fulfillment_inbound__list_shipment_pallets` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets` | 必填 plan/shipment ID；可选 `pageSize` 1–1000、`paginationToken` |
| `updateShipmentName`<br>`amazon_store_fulfillment_inbound__update_shipment_name` 操作 | PUT / 204 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name` | 必填 plan/shipment ID；body 必填 `name`；成功响应无 body |
| `updateShipmentSourceAddress`<br>`amazon_store_fulfillment_inbound__update_shipment_source_address` 操作 | PUT / 202<br>异步 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress` | 必填 plan/shipment ID；body 必填 `address`，地址至少含 name/addressLine1/city/countryCode/phoneNumber/postalCode；返回 `operationId` |
| `updateShipmentTrackingDetails`<br>`amazon_store_fulfillment_inbound__update_shipment_tracking_details` 操作 | PUT / 202<br>异步 | `/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails` | 必填 plan/shipment ID；body 必填 `trackingDetails`；返回 `operationId` |

## Tracking 输入

`trackingDetails` 按 shipment mode 二选一：

- SPD：`spdTrackingDetail` 中提供每个 `boxId` 对应的 `trackingId`。
- LTL/FTL：`ltlTrackingDetail` 中提供承运人给出的 freight bill/BOL 信息。

不在同一请求中同时提交 SPD 和 LTL tracking。更新前可以使用 `listShipmentBoxes` 取回真实 `boxId`。

## 跨版本提醒

`getShipment.shipmentId` 是 v2024 工作流 ID；`getShipment.shipmentConfirmationId` 是标签上的 ID。v0 `getLabels` 和 `getBillOfLading` 使用后者，见 `../identifiers.md`（见本文对应归档章节）。

## Archived reference: apis/transportation.md

# Transportation（3 operations）

路径版本：`/inbound/fba/2024-03-20`。

| Operation / 脚本 | HTTP / 成功 | Amazon path | 必要输入与语义 |
|---|---|---|---|
| `listTransportationOptions`<br>`amazon_store_fulfillment_inbound__list_transportation_options` 操作 | GET / 200 | `/inboundPlans/{inboundPlanId}/transportationOptions` | 必填 `inboundPlanId`；可选 `pageSize` 1–20、`paginationToken`、`placementOptionId`、`shipmentId`；返回 `transportationOptions` |
| `generateTransportationOptions`<br>`amazon_store_fulfillment_inbound__generate_transportation_options` 操作 | POST / 202<br>异步 | `/inboundPlans/{inboundPlanId}/transportationOptions` | body 必填 `placementOptionId`、`shipmentTransportationConfigurations`；返回 `operationId` |
| `confirmTransportationOptions`<br>`amazon_store_fulfillment_inbound__confirm_transportation_options` 操作 | POST / 202<br>异步・确认 | `/inboundPlans/{inboundPlanId}/transportationOptions/confirmation` | body 必填 `transportationSelections`，每项至少绑定 `shipmentId` + `transportationOptionId`；返回 `operationId` |

## Generate/list

- `shipmentTransportationConfigurations` 覆盖候选 placement 中的所有 shipments，按 mode 提供 ready-to-ship window、freight 和 pallet 信息。
- 不同 placement option 的 transportation 费用可能不同。在 placement 确认前，可按候选 `placementOptionId` 生成/列出 transportation options 供用户比较。
- 分页时保留 `placementOptionId` 和 `shipmentId` 过滤条件。
- 展示每个 option 的 shipment、carrier、`shippingMode`、`shippingSolution`、cost、void window、expiration 和 preconditions。

## Confirm

- 必须先确认 placement option。
- 每个 shipment 选择一个与之匹配的 transportation option。
- 自有承运人在 preconditions 要求时，先确认对应 delivery window。
- Amazon Partnered 确认意味着同意运费估算和 Amazon 扣费。
- 确认后不能再为该 plan 生成或确认新 transportation options。

`confirmTransportationOptions` 是高影响操作，不能从“列出方案”或“推荐便宜方案”自动进入确认。

## Archived reference: identifiers.md

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

## v2024 转 v0 labels/BOL

```text
confirmPlacementOption
  → getInboundOperationStatus == SUCCESS
  → getShipment(inboundPlanId, shipmentId)
  → shipmentConfirmationId
  → getLabels / getBillOfLading v0 path {shipmentId}
```

v0 OpenAPI 使用路径名 `{shipmentId}`，但在 v2024 创建的 workflow 中，该路径值必须取自 `getShipment.shipmentConfirmationId`。脚本层参数应优先命名为 `shipmentConfirmationId`，避免与 v2024 `shipmentId` 混淆。

仅当用户明确操作原生 v0 shipment 时，才允许把 legacy `shipmentId` 作为兼容输入。如果同时传入两个不同的值，应拒绝而不是自动选择。

## option 有效性

- 新一次 generate 可以使旧 option/preview/slot ID 失效。
- 必须在同一 `inboundPlanId`、`shipmentId` 和生成批次中使用 ID。
- 确认前检查费用、`validUntil`、`expiration` 和其他有效期字段。
- 不能在不同 plan/shipment 之间复用已缓存的 option ID。

## Archived reference: marketplace-constraints.md

# Marketplace 与业务限制

这些条件来自 Amazon Fulfillment Inbound 官方概述、operation 描述和 India 工作流。能否调用最终仍受卖家资格、目标 FC、商品可入库性和 Amazon 实时返回影响。

| 能力 | 限制 |
|---|---|
| v2024 创建入库 shipment | Amazon 当前概述声明支持除 Brazil 外的 Amazon stores |
| Self-ship appointment | `MX`、`BR`、`EG`、`SA`、`AE`、`IN` |
| Item compliance | `listItemComplianceDetails` / `updateItemComplianceDetails` 仅用于 India compliance，IN marketplace ID 为 `A21TJRUUN4KGV` |
| Custom placement | India 工作流可在 `generatePlacementOptions.requestBody.customPlacement` 中指定商品/数量与 FC |
| Delivery challan | 仅 India marketplace 的 Partnered Carrier Program（PCP）shipment |
| Pack Later | 仅 pallet delivery（LTL/FTL）；可用 Amazon Partnered 或自有承运人 |
| Amazon-recommended packing | ES、UK、FR、DE、IT；适用于单件 parcel 小于 15kg 的 SPD，不支持 LTL/FTL |
| US prep/label | 卖家必须在发往 Amazon 履约网络前完成商品预处理和贴标 |

## Prep details

- 必须先调用 `setPrepDetails`，才能通过 `listPrepDetails` 取回该 Skill 设置的 prep details。
- 在 Seller Central 中填写的 prep details 不会由 `listPrepDetails` 返回。
- `listPrepDetails` 和 `listItemComplianceDetails` 的 `mskus` 是重复 query key，最多 100 个。MSKU 中 `%`、`+`、`,` 要按 Amazon 要求双重 percent encode。
- `listPrepDetails` 返回的 `prepOwnerConstraint` 和 `labelOwnersConstraint` 决定 `createInboundPlan` 可用的 owner；两者为空时可选 `AMAZON` 或 `SELLER`。`allOwnersConstraint=MUST_MATCH` 时 prep/label owner 必须一致。
- `prepCategory=FC_PROVIDED` 表示 Amazon 已固定该类别，不可修改。如果在创建 plan 后又用 `setPrepDetails` 改了 category，当前 plan 仍使用 `listInboundPlanItems` / `listInboundPlanBoxes` 返回的原 prep/label owner；新设置仅影响后续 plan。
- `ITEM_NO_PREP` 不代表可以省略 prep/label owner；`prepCategory=NONE` 也可能仍需 label owner，应以 `listPrepDetails` 返回的 owner 约束为准。

## Listing 前置条件

- 入库 MSKU 必须已建立 Amazon listing 并设为 FBA fulfillment channel；不在本 Skill 内自动创建 listing 或将 FBM 转换为 FBA。
- 电池、含电池或可能属于危险品的商品，必须先在 listing 中补齐 battery/dangerous-goods 信息，否则转为 FBA 会失败。
- 官方 listing channel code 按区域使用 `AMAZON_NA`、`AMAZON_EU`、`AMAZON_IN` 或 `AMAZON_JP`；这属于 Listings Items / Feeds API，不应拼到 Fulfillment Inbound 请求中。

## Self-ship 和 India

- Self-ship 四个 operation 的 endpoint 虽列出 BR，不能将此推导为 `createInboundPlan` 在 BR 可用；两项能力限制应独立校验。
- 生成 self-ship slots 前，先用 `getShipment` 确认已存在 `amazonReferenceId`。
- 不传 `desiredStartDate` / `desiredEndDate` 时，Amazon 默认生成未来 42 天的可用 slot。
- `scheduleSelfShipAppointment` 用于重新预约时，`reasonComment` 必须填写。
- India 店铺业务除 Amazon Fulfillment role 外，官方流程还要求 Product Listing role 以及已建立的 listing。

## 时效性

- Packing、placement、transportation、delivery window、content-update preview 和 appointment slot 均可能带有 `validUntil`、`expiration` 或类似字段。确认前必须重新检查。
- 重新生成 option 后，之前的 option ID 不再可信。
- 在 placement / transportation 尚未确认时切换到 Send to Amazon，STA 会重新生成 options，API 中之前的 options 会被丢弃。

## 官方来源

- [Fulfillment Inbound API](https://developer-docs.amazon.com/sp-api/docs/fulfillment-inbound-api)
- [Ship Inventory to Amazon Fulfillment Centers in India](https://developer-docs.amazon.com/sp-api/docs/ship-inventory-to-india-fc)
- [Prep details 发布说明](https://developer-docs.amazon.com/sp-api/changelog/update-fulfillment-inbound-api-v2024-03-20-now-supports-preparation-details)

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。

## Archived reference: workflows.md

# Fulfillment Inbound 工作流

每个 operation 脚本只执行一次 Amazon 请求。本文中的 `poll`表示调用方显式运行 `amazon_store_fulfillment_inbound__get_inbound_operation_status` 操作，只在 `SUCCESS` 后继续。

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

## 3. Partnered Carrier 和自有承运人

- Amazon Partnered Carrier：在 `listTransportationOptions` 中选择 `shippingSolution=AMAZON_PARTNERED_CARRIER`。确认代表接受运费估算和 Amazon 扣费。
- 自有承运人：选择 `shippingSolution=USE_YOUR_OWN_CARRIER`，按 `preconditions` 为每个 shipment 生成、列出并确认 delivery window。
- 多 shipment placement 要为每个 `shipmentId` 选择一个 `transportationOptionId`。
- 所有 shipment 类型都必须确认 transportation option。
- `confirmTransportationOptions` 之前必须已确认 placement；确认 transportation 后不能再为该 plan 生成或确认新 transportation options。

## 4. Shipment content update

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

## 7. 标签和 BOL

placement 确认完成后，调用 `getShipment` 获取 `shipmentConfirmationId`，再传给 v0 `getLabels` / `getBillOfLading`。不要直接使用 v2024 `shipmentId`。完整 ID 规则见 `identifiers.md`（见本文对应归档章节）。

## 8. 取消与运费 void window

`cancelInboundPlan` 会取消 plan 及关联 shipments，但已确认 transportation 的运费只在 Amazon 的 void window 内可取消：SPD 为确认后 24 小时，LTL/FTL 为确认后 1 小时。超过时限可能仍收取运费。执行前展示 shipment 类型、transportation 确认时间和可能费用；完成后用 `getInboundOperationStatus` 或 `getInboundPlan` 确认 `VOIDED`。
