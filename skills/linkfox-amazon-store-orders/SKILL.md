---
name: linkfox-amazon-store-orders
description: 亚马逊店铺订单（与 linkfox-amazon-store-auth / report / listings / pricing 同系列），经 /spApi/developerProxy 调用 SP-API Orders：v2026-01-01 的 searchOrders、getOrder；v0 的 getOrderBuyerInfo、getOrderAddress、getOrderItems、getOrderItemsBuyerInfo、updateShipmentStatus、getOrderRegulatedInfo、updateVerificationStatus、confirmShipment。当用户提到亚马逊订单、searchOrders、getOrder、订单列表、订单详情、买家信息、收货地址、订单行、发货确认、管制订单、核验状态、Orders API、SP-API 订单 时触发。
---

# Amazon 店铺 Orders

本 skill 与 **`linkfox-amazon-store-auth`**、**`linkfox-amazon-store-report`**、**`linkfox-amazon-store-listings`**、**`linkfox-amazon-store-pricing`** 同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`** 取 **`accessToken`**，再 **`POST /spApi/developerProxy`** 转发上游 **`GET` / `POST` / `PATCH`**。

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

1. 运行 `python scripts/check_auth_dependency.py`；若 exit code **42** 且 stderr 含 `DEPENDENCY_MISSING:`，请先安装 **`linkfox-amazon-store-auth`**。
2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities（脚本一览）

| 能力 | developerProxy `path`（要点） | 脚本 |
|------|------------------------------|------|
| searchOrders | `orders/2026-01-01/orders` + Query | `search_orders.py` |
| getOrder | `orders/2026-01-01/orders/{orderId}` + Query | `get_order.py` |
| getOrderBuyerInfo | `orders/v0/orders/{orderId}/buyerInfo` | `get_order_buyer_info.py` |
| getOrderAddress | `orders/v0/orders/{orderId}/address` | `get_order_address.py` |
| getOrderItems | `orders/v0/orders/{orderId}/orderItems` + NextToken | `get_order_items.py` |
| getOrderItemsBuyerInfo | `orders/v0/orders/{orderId}/orderItems/buyerInfo` | `get_order_items_buyer_info.py` |
| updateShipmentStatus | `orders/v0/orders/{orderId}/shipment`，POST JSON | `update_shipment_status.py` |
| getOrderRegulatedInfo | `orders/v0/orders/{orderId}/regulatedInfo` | `get_order_regulated_info.py` |
| updateVerificationStatus | `orders/v0/orders/{orderId}/regulatedInfo`，PATCH JSON | `update_verification_status.py` |
| confirmShipment | `orders/v0/orders/{orderId}/shipmentConfirmation`，POST JSON | `confirm_shipment.py` |

共享逻辑见 **`scripts/_spapi_orders_common.py`**（仅供同目录脚本 import，非独立 CLI）。

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

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/search_orders.py '{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"lastUpdatedAfter":"2026-05-01T00:00:00Z"}'

python scripts/get_order.py '{"sellerId":"A1...","region":"NA","orderId":"123-1234567-1234567","includedData":["FULFILLMENT","PACKAGES"]}'
```

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

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-orders`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
