# Reference archive: linkfox-amazon-store-external-fulfillment

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
    "path": "externalFulfillment/inventory/2024-09-11/inventories",
    "method": "POST",
    "body": "<按本 reference 构造的 JSON 字符串；无请求体时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-external-fulfillment/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-external-fulfillment
description: 亚马逊 External Fulfillment 外部履约管理。用于 Seller Flex、FBA Onsite、Easy Ship、Self Ship、MFN Self Delivery 等项目中的按 location 库存查询或更新、履约货件处理、包裹与状态更新、配送选项、面单、发票和退货查询。用户提到 External Fulfillment、SmartConnect、Seller Flex、FBA Onsite、Easy Ship、Self Ship、batchInventory、location 库存、外部履约 shipment、EF 面单、EF 发票或 EF 退货时触发。即使未明确说“External Fulfillment API”，只要需求围绕这些外部履约项目的库存、货件、包裹或退货，也应触发此技能；普通卖家订单使用 linkfox-amazon-store-orders，FBA/MCF 使用对应 fulfillment 技能。
---

# Amazon 店铺 External Fulfillment


适用渠道：Seller Flex / FBA Onsite、Multi Seller Flex、Easy Ship、Self Ship、MFN Self Delivery、Amazon Pharmacy 等（以商家 allowlist 与角色为准）。

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考索引

| 模块 | 能力 | 文档 |
|------|------|------|
| Inventory | batchInventory | [batchInventory](https://developer-docs.amazon.com/sp-api/reference/batchinventory) |
| Shipping | getShipments | [getShipments](https://developer-docs.amazon.com/sp-api/reference/getshipments-1) |
| Shipping | getShipment | [getShipment](https://developer-docs.amazon.com/sp-api/reference/getshipment-1) |
| Shipping | processShipment | [processShipment](https://developer-docs.amazon.com/sp-api/reference/processshipment) |
| Shipping | createPackages | [createPackages](https://developer-docs.amazon.com/sp-api/reference/createpackages) |
| Shipping | updatePackage | [updatePackage](https://developer-docs.amazon.com/sp-api/reference/updatepackage) |
| Shipping | updatePackageStatus | [updatePackageStatus](https://developer-docs.amazon.com/sp-api/reference/updatepackagestatus) |
| Shipping | retrieveShippingOptions | [retrieveShippingOptions](https://developer-docs.amazon.com/sp-api/reference/retrieveshippingoptions) |
| Shipping | generateInvoice | [generateInvoice](https://developer-docs.amazon.com/sp-api/reference/generateinvoice) |
| Shipping | retrieveInvoice | [retrieveInvoice](https://developer-docs.amazon.com/sp-api/reference/retrieveinvoice) |
| Shipping | generateShipLabels | [generateShipLabels](https://developer-docs.amazon.com/sp-api/reference/generateshiplabels) |
| Returns | listReturns | [listReturns](https://developer-docs.amazon.com/sp-api/reference/listreturns) |
| Returns | getReturn | [getReturn](https://developer-docs.amazon.com/sp-api/reference/getreturn) |

---

## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。

2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。
3. 商家需 **External Fulfillment allowlist**，应用需 **Direct-to-Consumer Shipping (Restricted)** 角色。

---

## Current Capabilities（脚本一览）

| 能力 | developerProxy `path`（要点） | 脚本 |
|------|------------------------------|------|
| batchInventory | `externalFulfillment/inventory/2024-09-11/inventories`，POST | `post_batch_inventory` 操作 |
| getShipments | `externalFulfillment/2024-09-11/shipments` + Query | `amazon_store_external_fulfillment__get_shipments` 操作 |
| getShipment | `.../shipments/{shipmentId}` | `amazon_store_external_fulfillment__get_shipment` 操作 |
| processShipment | `.../shipments/{shipmentId}?operation=`，POST | `process_shipment` 操作 |
| createPackages | `.../shipments/{shipmentId}/packages`，POST | `create_packages` 操作 |
| updatePackage | `.../shipments/{shipmentId}/packages/{packageId}`，PUT | `amazon_store_external_fulfillment__update_package` 操作 |
| updatePackageStatus | 同上 path，PATCH | `update_package_status` 操作 |
| retrieveShippingOptions | `.../shipments/{shipmentId}/shippingOptions` + packageId | `retrieve_shipping_options` 操作 |
| generateInvoice | `.../shipments/{shipmentId}/invoice`，POST | `generate_invoice` 操作 |
| retrieveInvoice | 同上 path，GET | `retrieve_invoice` 操作 |
| generateShipLabels | `.../shipments/{shipmentId}/shipLabels?operation=`，PUT | `generate_ship_labels` 操作 |
| listReturns | `externalFulfillment/2024-09-11/returns` + Query | `list_returns` 操作 |
| getReturn | `.../returns/{returnId}` | `get_return` 操作 |


---

## Quick Parameters（摘要）

- **batchInventory**：`requests` 1～10 条。简化项：`action`=`fetch`|`update`、`locationId`、`skuId`；update 必填 `quantity`。MFN 单仓常用 `locationId=DEFAULT`；Seller Flex 用 4 位仓码。高级：`useAmazonRequestShape:true` 直传官方 `requests`。
- **getShipments**：必填 `status`（如 `ACCEPTED`/`CREATED`）；可选 `locationId`、`marketplaceId`、`channelName`、`lastUpdatedAfter/Before`、`maxResults`、`paginationToken`。
- **processShipment**：`operation`=`CONFIRM`|`REJECT`；REJECT 时可传 `referenceId`/`lineItems` 或 `requestBody`。
- **createPackages / updatePackage**：包裹尺寸重量与 `packageLineItems` 按官方 schema 放在 `packages` 或 `requestBody`。
- **updatePackageStatus**：主要用于 Self Delivery；传 `status`/`subStatus`/`reason`。
- **generateShipLabels**：`operation`=`GENERATE`|`REGENERATE`；可选 `shippingOptionId`、`packageIds`。
- **listReturns**：可选 `status`（新退货常用 `CREATED`）、`returnLocationId`、时间窗、`nextToken`。

典型履约流程：`getShipments` → `processShipment(CONFIRM)` → `createPackages` → `retrieveShippingOptions` → `generateInvoice` → `generateShipLabels` →（Self Delivery）`updatePackageStatus`。

---

## Scripts



---

## Display Rules

1. 先看网关 **`developerProxy.errcode` / `httpStatus`**，再解析脚本附加字段（如 **`batchInventory`**、**`shipments`**、**`invoice`**）。
2. **batchInventory** 成功时常为 **207** Multi-Status；逐条看 `responses[].status`。
3. 多数写操作成功可能为 **204**（无 body）；stdout 会标 `success: true`。
4. 发票/面单文档多为 Base64 或预签名 URL，勿把整段大 base64 反复贴进上下文。
5. **路径白名单**：若返回 **1005**，需后端放行 **`externalFulfillment/`** 前缀。

---

## Important Limitations

- 权限：**Direct-to-Consumer Shipping (Restricted)**；商家需 allowlist。
- **写库存为绝对值发布**，非增量；只同步有变化的 SKU；SKU 特殊字符需 URL 编码（脚本已处理简化入参）。
- 与 **`linkfox-amazon-store-orders`**（普通 Orders）、**`linkfox-amazon-store-feeds`**（Feed 改库存）、**`linkfox-amazon-store-report`**（库存报告）边界不同，勿混用。
- Seller Flex 上 `retrieveShippingOptions` 常返回空；Easy Ship 全球多数站点可能不支持 `generateInvoice`（印度除外）。
- 返回结构以 Amazon schema 为准；详见 **`references/api.md`**。

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

不消耗积分（以网关实际计费为准；若网关计费则按积分规则处理）。

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-external-fulfillment`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-external-fulfillment — API 与网关调用说明

## 1. 调用链

1. 依赖 **`linkfox-amazon-store-auth`** 完成店铺授权（`sellerId` + `region`）。
   Body 字段：
   - **`region`**
   - **`path`**：Amazon SP-API 相对 path，**无**前导 `/`
   - **`method`**：`GET` | `POST` | `PUT` | `PATCH`
   - **`queryString`**（可选）：不含 `?`
   - **`body`**（写操作）：JSON 字符串
   - **`contentType`**：`application/json`

环境变量：


---

## 2. 脚本与 path / method 对照

| 脚本 | method | path 模板 |
|------|--------|-----------|
| `post_batch_inventory` 操作 | POST | `externalFulfillment/inventory/2024-09-11/inventories` |
| `amazon_store_external_fulfillment__get_shipments` 操作 | GET | `externalFulfillment/2024-09-11/shipments` |
| `amazon_store_external_fulfillment__get_shipment` 操作 | GET | `externalFulfillment/2024-09-11/shipments/{shipmentId}` |
| `process_shipment` 操作 | POST | `externalFulfillment/2024-09-11/shipments/{shipmentId}` + `operation` |
| `create_packages` 操作 | POST | `.../shipments/{shipmentId}/packages` |
| `amazon_store_external_fulfillment__update_package` 操作 | PUT | `.../shipments/{shipmentId}/packages/{packageId}` |
| `update_package_status` 操作 | PATCH | `.../shipments/{shipmentId}/packages/{packageId}` |
| `retrieve_shipping_options` 操作 | GET | `.../shipments/{shipmentId}/shippingOptions` + `packageId` |
| `generate_invoice` 操作 | POST | `.../shipments/{shipmentId}/invoice` |
| `retrieve_invoice` 操作 | GET | `.../shipments/{shipmentId}/invoice` |
| `generate_ship_labels` 操作 | PUT | `.../shipments/{shipmentId}/shipLabels` + `operation` |
| `list_returns` 操作 | GET | `externalFulfillment/2024-09-11/returns` |
| `get_return` 操作 | GET | `externalFulfillment/2024-09-11/returns/{returnId}` |

路径段经 percent-encoding。

---

## 3. 公共入参

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家 ID |
| region | string | 是 | NA / EU / FE |
| skipDepCheck | boolean | 否 | true 时跳过本地依赖探测 |

---

## 4. Inventory — `post_batch_inventory` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests | object[] | 是 | 1～10 条 |
| useAmazonRequestShape | boolean | 否 | true 时 `requests` 为官方原始数组 |

简化项字段：

| 字段 | 说明 |
|------|------|
| action | `fetch` 或 `update` |
| locationId | MFN 单仓常用 `DEFAULT`；Seller Flex 为 4 位仓码 |
| skuId | 卖家 SKU |
| quantity | update 必填；绝对库存 |
| clientSequenceNumber | 可选 |
| marketplaceAttributes | 可选；多站点时常需 `{marketplaceId, channelName}` |

脚本会组装为：

```json
{
  "requests": [
    {
      "method": "POST",
      "uri": "/inventory/fetch?locationId=DEFAULT&skuId=SKU-1",
      "body": { "marketplaceAttributes": { "marketplaceId": "...", "channelName": "MFN" } }
    }
  ]
}
```

解析字段：**`batchInventory`**（上游常为 HTTP **207**）。

官方：

- [Publish location-level inventory](https://developer-docs.amazon.com/sp-api/docs/publish-location-level-inventory)
- [Retrieve location-level inventory](https://developer-docs.amazon.com/sp-api/docs/retrieve-location-level-inventory)

---

## 5. Shipping

### 5.1 `amazon_store_external_fulfillment__get_shipments` 操作

| 字段 | 必填 | 说明 |
|------|------|------|
| status | 是 | 如 ACCEPTED、CREATED、CONFIRMED、SHIPPED… |
| locationId | 否 | 渠道 location |
| marketplaceId / channelName | 否 | |
| lastUpdatedAfter / lastUpdatedBefore | 否 | ISO 8601 |
| maxResults | 否 | 1～100 |
| paginationToken | 否 | 上一页 nextToken |

解析字段：**`shipments`**。

### 5.2 `amazon_store_external_fulfillment__get_shipment` 操作

| 字段 | 必填 |
|------|------|
| shipmentId | 是 |

解析字段：**`shipment`**。

### 5.3 `process_shipment` 操作

| 字段 | 必填 | 说明 |
|------|------|------|
| shipmentId | 是 | |
| operation | 是 | CONFIRM / REJECT |
| requestBody | 否 | 官方 body |
| referenceId / lineItems | 否 | 简化字段，合成 body |

### 5.4 `create_packages` 操作

| 字段 | 必填 |
|------|------|
| shipmentId | 是 |
| packages 或 requestBody | 是 |

### 5.5 `amazon_store_external_fulfillment__update_package` 操作

| 字段 | 必填 |
|------|------|
| shipmentId / packageId / requestBody | 是 |

### 5.6 `update_package_status` 操作

| 字段 | 必填 | 说明 |
|------|------|------|
| shipmentId / packageId | 是 | |
| status 或 requestBody | 是 | 可附带 subStatus、reason |

### 5.7 `retrieve_shipping_options` 操作

| 字段 | 必填 |
|------|------|
| shipmentId / packageId | 是 |

解析字段：**`shippingOptions`**。

### 5.8 `generate_invoice` 操作 / `retrieve_invoice` 操作

| 字段 | 必填 |
|------|------|
| shipmentId | 是 |

解析字段：**`invoice`**（含 `document.format` / `document.content` Base64）。

### 5.9 `generate_ship_labels` 操作

| 字段 | 必填 | 说明 |
|------|------|------|
| shipmentId | 是 | |
| operation | 是 | GENERATE / REGENERATE |
| shippingOptionId | 否 | 需 URL 编码（脚本处理） |
| packageIds / requestBody | 否 | 三方承运等场景 |

解析字段：**`shipLabels`**。

---

## 6. Returns

### 6.1 `list_returns` 操作

可选：`returnLocationId`、`rmaId`、`status`、`reverseTrackingId`、`createdSince`、`createdUntil`、`lastUpdatedSince`、`lastUpdatedUntil`、`maxResults`、`nextToken`。

解析字段：**`returns`**。

### 6.2 `get_return` 操作

| 字段 | 必填 |
|------|------|
| returnId | 是 |

解析字段：**`returnItem`**。

---

## 7. 错误与白名单

| 现象 | 处理 |
|------|------|
| 401/402 / 积分不足 | 见 `references/onboarding.md` |
| 403 | 角色/allowlist/签名问题，非 onboarding 范围 |
| 1005 路径拒绝 | 后端放行 `externalFulfillment/` |
| 409 / 422 | 履约状态机冲突或参数不可处理，检查当前 shipment status |
| 429 | 降速重试（先征得用户同意） |

---

## 8. Feedback

`skillName`：`linkfox-amazon-store-external-fulfillment`

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
