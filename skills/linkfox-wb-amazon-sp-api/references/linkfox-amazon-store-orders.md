# Reference archive: linkfox-amazon-store-orders

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
    "path": "orders/2026-01-01/orders",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-orders/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `resolvedPath` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `queryString` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `requestBody` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.errcode` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.httpStatus` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `developerProxy.body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-orders
description: 亚马逊卖家订单查询与履约状态管理。用于搜索订单、获取订单详情、订单商品、买家信息和收货地址，处理发货确认、配送状态、管制商品订单及买家核验状态。用户提到亚马逊订单、卖家订单列表、订单详情、Amazon order ID、买家信息、收货地址、订单行、确认发货、更新 shipment 状态、管制订单、核验状态、searchOrders、getOrder、Orders API 时触发。即使未明确说“Orders API”，只要希望查询或处理亚马逊商城中产生的卖家订单，也应触发此技能；MCF、FBA 入仓和 External Fulfillment 货件使用对应履约技能。
---

# Amazon 店铺 Orders


## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考索引

| 能力 | 文档 |
|------|------|
| searchOrders | [searchOrders](https://developer-docs.amazon.com/sp-api/reference/searchorders) |
| getOrder (v2026-01-01) | [getOrder](https://developer-docs.amazon.com/sp-api/reference/getorder-3) |
| getOrderBuyerInfo (deprecated) | [getOrderBuyerInfo](https://developer-docs.amazon.com/sp-api/reference/getorderbuyerinfo) |
| getOrderAddress (deprecated) | [getOrderAddress](https://developer-docs.amazon.com/sp-api/reference/getorderaddress) |
| getOrderItems (deprecated) | [getOrderItems](https://developer-docs.amazon.com/sp-api/reference/getorderitems) |
| getOrderItemsBuyerInfo (deprecated) | [getOrderItemsBuyerInfo](https://developer-docs.amazon.com/sp-api/reference/getorderitemsbuyerinfo) |
| updateShipmentStatus | [updateShipmentStatus](https://developer-docs.amazon.com/sp-api/reference/updateshipmentstatus) |
| getOrderRegulatedInfo | [getOrderRegulatedInfo](https://developer-docs.amazon.com/sp-api/reference/getorderregulatedinfo) |
| updateVerificationStatus | [updateVerificationStatus](https://developer-docs.amazon.com/sp-api/reference/updateverificationstatus) |
| confirmShipment | [confirmShipment](https://developer-docs.amazon.com/sp-api/reference/confirmshipment) |

---

## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。

2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities（脚本一览）

| 能力 | developerProxy `path`（要点） | 脚本 |
|------|------------------------------|------|
| searchOrders | `orders/2026-01-01/orders` + Query | `search_orders` 操作 |
| getOrder | `orders/2026-01-01/orders/{orderId}` + Query | `amazon_store_orders__get_order` 操作 |
| getOrderBuyerInfo | `orders/v0/orders/{orderId}/buyerInfo` | `get_order_buyer_info` 操作 |
| getOrderAddress | `orders/v0/orders/{orderId}/address` | `get_order_address` 操作 |
| getOrderItems | `orders/v0/orders/{orderId}/orderItems` + NextToken | `get_order_items` 操作 |
| getOrderItemsBuyerInfo | `orders/v0/orders/{orderId}/orderItems/buyerInfo` | `get_order_items_buyer_info` 操作 |
| updateShipmentStatus | `orders/v0/orders/{orderId}/shipment`，POST JSON | `update_shipment_status` 操作 |
| getOrderRegulatedInfo | `orders/v0/orders/{orderId}/regulatedInfo` | `get_order_regulated_info` 操作 |
| updateVerificationStatus | `orders/v0/orders/{orderId}/regulatedInfo`，PATCH JSON | `update_verification_status` 操作 |
| confirmShipment | `orders/v0/orders/{orderId}/shipmentConfirmation`，POST JSON | `confirm_shipment` 操作 |


---

## Quick Parameters（摘要）

- **searchOrders**：`createdAfter` **或** `lastUpdatedAfter`（二选一）；`marketplaceIds`；可选 `fulfillmentStatuses`、`fulfilledBy`、`maxResultsPerPage`、`paginationToken`（上一页 **`nextToken`**）、`includedData`。
- **getOrder**：`orderId`；可选 **`includedData`**（如 BUYER、FULFILLMENT、PACKAGES）。
- **getOrderItems / getOrderItemsBuyerInfo**：可选 **`nextToken`** → 查询参数 `NextToken`。
- **updateShipmentStatus**：`marketplaceId`、`shipmentStatus`（ReadyForPickup / PickedUp / RefusedPickup）；可选 **`orderItems`**。
- **updateVerificationStatus**：传 **`regulatedOrderVerificationStatus`** 对象，或整包 **`requestBody`**。
- **confirmShipment**：**`requestBody`** 为官方要求的完整对象（通常含 **`packageDetail`** 等）。

---

## Scripts



---

## Display Rules

1. 先看网关 **`developerProxy.errcode` / `httpStatus`**，再解析各脚本附加字段（如 **`searchOrders`**、**`order`**）。
2. **POST/PATCH** 脚本：`stdout` 中含 **`requestBody`**（组装后的 Amazon 请求体），便于排查。
3. **v0 买家/地址/行项目** 接口在官方文档中为 **deprecated**；新集成优先用 **v2026-01-01** 的 **searchOrders / getOrder** 与 **`includedData`** 拉齐业务字段。
4. **searchOrders** 默认速率较低（官方约 **0.0056 req/s**），注意 **429**。
5. 受限 PII / RDT 以 Amazon 数据保护政策为准；详见 **`references/api.md`**。

---

## Important Limitations

- 权限：**Orders** 及相关角色；部分读取可能需 **Restricted Data Token**，不在本 skill 内实现。
- **路径白名单**：若网关返回 **1005** 等拒绝转发，需后端放行 **`orders/v0/...`** 与 **`orders/2026-01-01/...`** 前缀。
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

不消耗积分。

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-orders`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-orders — API 与网关调用说明

## 1. 调用链

   Body: `{"sellerId":"<卖家ID>","region":"NA|EU|FE|..."}`  

   Body 字段（与 listings / pricing 系列一致）：
   - **`region`**：与 storeTokens 相同。
   - **`path`**：Amazon SP-API 相对 path，**无**前导 `/`。
   - **`method`**：`GET` | `POST` | `PATCH`。
   - **`queryString`**（可选）：URL 查询串，不含 `?`。
   - **`body`**（POST/PATCH）：JSON 字符串。
   - **`contentType`**：如 `application/json`。

环境变量：


---

## 2. 脚本与 path / method 对照

| 脚本 | method | path 模板 |
|------|--------|-----------|
| `search_orders` 操作 | GET | `orders/2026-01-01/orders` |
| `amazon_store_orders__get_order` 操作 | GET | `orders/2026-01-01/orders/{orderId}` |
| `get_order_buyer_info` 操作 | GET | `orders/v0/orders/{orderId}/buyerInfo` |
| `get_order_address` 操作 | GET | `orders/v0/orders/{orderId}/address` |
| `get_order_items` 操作 | GET | `orders/v0/orders/{orderId}/orderItems` |
| `get_order_items_buyer_info` 操作 | GET | `orders/v0/orders/{orderId}/orderItems/buyerInfo` |
| `update_shipment_status` 操作 | POST | `orders/v0/orders/{orderId}/shipment` |
| `get_order_regulated_info` 操作 | GET | `orders/v0/orders/{orderId}/regulatedInfo` |
| `update_verification_status` 操作 | PATCH | `orders/v0/orders/{orderId}/regulatedInfo` |
| `confirm_shipment` 操作 | POST | `orders/v0/orders/{orderId}/shipmentConfirmation` |

`orderId` 在 path 中经 **percent-encoding**（与 listings SKU 处理一致）。

---

## 3. 各脚本 JSON 入参

### 3.1 公共字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家 ID |
| region | string | 是 | NA / EU / FE 等与 auth 一致 |
| skipDepCheck | boolean | 否 | 为 true 时跳过本地依赖探测 |

### 3.2 `search_orders` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplaceIds | string[] | 是 | 站点 ID 列表，长度 ≤ 50（以 Amazon 为准） |
| createdAfter | string | 条件 | ISO 8601；与 `lastUpdatedAfter` **二选一** |
| createdBefore | string | 否 | 与 `createdAfter` 同组使用 |
| lastUpdatedAfter | string | 条件 | ISO 8601；与 `createdAfter` **二选一** |
| lastUpdatedBefore | string | 否 | 与 `lastUpdatedAfter` 同组使用 |
| fulfillmentStatuses | string[] | 否 | 如 PENDING、UNSHIPPED、SHIPPED、CANCELLED 等 |
| fulfilledBy | string[] | 否 | MERCHANT、AMAZON |
| maxResultsPerPage | number | 否 | 1～100，默认 100 |
| paginationToken | string | 否 | 上一页响应 **`nextToken`** |
| includedData | string[] | 否 | BUYER、RECIPIENT、PROCEEDS、FULFILLMENT、PACKAGES 等（见 [searchOrders](https://developer-docs.amazon.com/sp-api/reference/searchorders)） |

脚本会在 stdout 的 JSON 中解析 **`searchOrders`**（当 `developerProxy.errcode==200` 且 `httpStatus==200` 时由 `body` JSON 解析）。

### 3.3 `amazon_store_orders__get_order` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | 亚马逊订单号 |
| includedData | string[] | 否 | 同官方 `includedData` |

解析字段：**`order`**。

### 3.4 `get_order_buyer_info` 操作 / `get_order_address` 操作

| 字段 | 类型 | 必填 |
|------|------|------|
| orderId | string | 是 |

解析字段：**`buyerInfo`** / **`shippingAddress`**（以实际 JSON 为准）。

### 3.5 `get_order_items` 操作 / `get_order_items_buyer_info` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | |
| nextToken | string | 否 | 映射为查询参数 **`NextToken`** |

解析字段：**`orderItems`** / **`orderItemsBuyerInfo`**。

### 3.6 `update_shipment_status` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | |
| marketplaceId | string | 是 | |
| shipmentStatus | string | 是 | ReadyForPickup、PickedUp、RefusedPickup |
| orderItems | object[] | 否 | 部分更新时的行项目 |

成功时 Amazon 常返回 **HTTP 204**，stdout 中 **`developerProxy`** 含状态即可，未必有 JSON body。

### 3.7 `get_order_regulated_info` 操作

仅需 **`orderId`**。解析字段：**`regulatedOrder`**。

### 3.8 `update_verification_status` 操作

| 方式 | 说明 |
|------|------|
| `regulatedOrderVerificationStatus` | 对象，脚本包装为 `{ "regulatedOrderVerificationStatus": ... }` |
| `requestBody` | 整包 PATCH body 对象 |

成功可能为 **204**。

### 3.9 `confirm_shipment` 操作

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requestBody | object | 是 | 与官方 **confirmShipment** schema 一致 |

成功可能为 **204**。

---

## 4. 响应与错误

- 脚本统一输出 JSON：`developerProxy` 为网关原样；部分脚本增加 **`resolvedPath`**、**`queryString`**、**`requestBody`**。
- 优先阅读 **`developerProxy.errcode`**、**`developerProxy.httpStatus`**，再读 **`developerProxy.body`**（常为 Amazon 错误 JSON）。
- **429**：需降频重试；searchOrders 默认速率较低。
- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。

---

## 5. 受限数据与 deprecated

- **getOrderBuyerInfo / getOrderAddress / getOrderItems / getOrderItemsBuyerInfo** 在官方文档中标记为 **deprecated**；敏感数据需 **RDT** 与数据保护策略，见 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken) 与 Orders 文档说明。
- **getOrderRegulatedInfo** 的 `Accept` 等头若需特化，取决于网关是否支持透传；当前脚本未附加额外 Amazon 请求头。

---

## 6. Feedback

若需反馈本 skill 问题，请在工单或内部渠道注明 **`skillName`: `linkfox-amazon-store-orders`**，并附上 `developerProxy` 完整 JSON（注意脱敏）。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
