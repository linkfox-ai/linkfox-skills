# linkfox-amazon-store-orders — API 与网关调用说明

## 1. 调用链

1. **`POST ${LINKFOX_TOOL_GATEWAY}/spApi/storeTokens`**  
   Body: `{"sellerId":"<卖家ID>","region":"NA|EU|FE|..."}`  
   响应需含 **`accessToken`**。

2. **`POST ${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`**  
   Body 字段（与 listings / pricing 系列一致）：
   - **`region`**：与 storeTokens 相同。
   - **`path`**：Amazon SP-API 相对 path，**无**前导 `/`。
   - **`method`**：`GET` | `POST` | `PATCH`。
   - **`amzAccessToken`**：上一步的 access token。
   - **`queryString`**（可选）：URL 查询串，不含 `?`。
   - **`body`**（POST/PATCH）：JSON 字符串。
   - **`contentType`**：如 `application/json`。

环境变量：

- **`LINKFOX_AGENT_API_KEY`**（或 **`LINKFOXAGENT_API_KEY`**，必填）：网关鉴权。（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **`LINKFOX_TOOL_GATEWAY`**（或 `STORE_API_BASE_URL` / `SPAPI_BASE_URL`，可选）：默认 `https://tool-gateway.linkfox.com`。

---

## 2. 脚本与 path / method 对照

| 脚本 | method | path 模板 |
|------|--------|-----------|
| `search_orders.py` | GET | `orders/2026-01-01/orders` |
| `get_order.py` | GET | `orders/2026-01-01/orders/{orderId}` |
| `get_order_buyer_info.py` | GET | `orders/v0/orders/{orderId}/buyerInfo` |
| `get_order_address.py` | GET | `orders/v0/orders/{orderId}/address` |
| `get_order_items.py` | GET | `orders/v0/orders/{orderId}/orderItems` |
| `get_order_items_buyer_info.py` | GET | `orders/v0/orders/{orderId}/orderItems/buyerInfo` |
| `update_shipment_status.py` | POST | `orders/v0/orders/{orderId}/shipment` |
| `get_order_regulated_info.py` | GET | `orders/v0/orders/{orderId}/regulatedInfo` |
| `update_verification_status.py` | PATCH | `orders/v0/orders/{orderId}/regulatedInfo` |
| `confirm_shipment.py` | POST | `orders/v0/orders/{orderId}/shipmentConfirmation` |

`orderId` 在 path 中经 **percent-encoding**（与 listings SKU 处理一致）。

---

## 3. 各脚本 JSON 入参

### 3.1 公共字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家 ID |
| region | string | 是 | NA / EU / FE 等与 auth 一致 |
| skipDepCheck | boolean | 否 | 为 true 时跳过本地依赖探测 |

### 3.2 `search_orders.py`

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

### 3.3 `get_order.py`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | 亚马逊订单号 |
| includedData | string[] | 否 | 同官方 `includedData` |

解析字段：**`order`**。

### 3.4 `get_order_buyer_info.py` / `get_order_address.py`

| 字段 | 类型 | 必填 |
|------|------|------|
| orderId | string | 是 |

解析字段：**`buyerInfo`** / **`shippingAddress`**（以实际 JSON 为准）。

### 3.5 `get_order_items.py` / `get_order_items_buyer_info.py`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | |
| nextToken | string | 否 | 映射为查询参数 **`NextToken`** |

解析字段：**`orderItems`** / **`orderItemsBuyerInfo`**。

### 3.6 `update_shipment_status.py`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | string | 是 | |
| marketplaceId | string | 是 | |
| shipmentStatus | string | 是 | ReadyForPickup、PickedUp、RefusedPickup |
| orderItems | object[] | 否 | 部分更新时的行项目 |

成功时 Amazon 常返回 **HTTP 204**，stdout 中 **`developerProxy`** 含状态即可，未必有 JSON body。

### 3.7 `get_order_regulated_info.py`

仅需 **`orderId`**。解析字段：**`regulatedOrder`**。

### 3.8 `update_verification_status.py`

| 方式 | 说明 |
|------|------|
| `regulatedOrderVerificationStatus` | 对象，脚本包装为 `{ "regulatedOrderVerificationStatus": ... }` |
| `requestBody` | 整包 PATCH body 对象 |

成功可能为 **204**。

### 3.9 `confirm_shipment.py`

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
