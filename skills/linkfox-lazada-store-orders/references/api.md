# Lazada 店铺订单查询接口参考

## 公共规则

### 调用规范

- 基础地址读取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`。直接调用使用 `POST /lazada/developerProxy`，超时 150 秒。
- 请求头为 `Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <LinkFox Key>`。Key 优先取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID` 和 `APP_NAME`，缺省为空。
- 命名脚本接收一个 JSON 对象，自动填入 `operation`。每次调用均实时请求，`--no-cache` 保留为兼容选项。`--inline` 打印完整脱敏 JSON 并继续保存。

| 网关请求字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 是 | 原样传入当前用户已授权的店铺连接 ID。后端据此选择店铺和站点。 |
| `operation` | 字符串 | 是 | `listOrders`、`getOrder` 或 `getOrderItems`。 |
| `queryParams` | 对象 | 是 | 按各操作的表格传入 Lazada 查询参数。 |

### 响应结构

网关成功响应为 `{"data": <业务数据>, "requestId": <Lazada 请求标识>}`，或由外层 `data` 包裹此对象。CLI 去除外层包裹并移除敏感字段，保存 `{"data": <业务数据>, "requestId": <Lazada 请求标识或 null>, "success": true}`。下方响应字段按保存文件中的路径标注。

## 订单列表

`listOrders` → `GET /orders/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `created_after` | 字符串 | 与 `update_after` 至少提供一个 | 创建时间下界 |
| `created_before` | 字符串 | 否 | 创建时间上界 |
| `update_after` | 字符串 | 与 `created_after` 至少提供一个 | 更新时间下界 |
| `update_before` | 字符串 | 否 | 更新时间上界 |
| `status` | 字符串 | 否 | 按订单行状态筛选，`all` 表示所有状态 |
| `sort_by` | 字符串 | 否 | Lazada 排序字段 |
| `sort_direction` | 字符串 | 否 | Lazada 排序方向 |
| `offset` | 0–5000 的整数或数字字符串 | 否 | 结果偏移量，默认 0 |
| `limit` | 1–100 的整数或数字字符串 | 否 | 每页条数，默认 20 |

时间使用含时区的 ISO 8601，优先采用官方示例的 `+08:00` 偏移格式，例如 `2026-11-01T00:00:00+08:00`。LinkFox 也接受 `+0800` 并原样转发。需要继续翻页时保持查询条件，递增 `offset`。达到上限后调整时间范围，从 `offset=0` 开始并按当前店铺内的 `order_id` 去重。 [Lazada 订单查询指南](https://open.lazada.com/apps/doc/doc?docId=121327&nodeId=29616)

### 响应字段

| 保存文件路径 | 类型 | 说明 |
| --- | --- | --- |
| `data.orders` | 对象数组 | 本页订单，字段同[订单详情](#订单详情)。空数组是成功结果。 |
| `data.count` | 数值或数字字符串 | 上游返回的本页数量，可能缺失。 |
| `data.countTotal` | 数值或数字字符串 | 查询条件下的订单总量，可能缺失。 |

## 订单详情

`getOrder` → `GET /order/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `order_id` | 1 至 20 位的正整数文本 | 是 | 当前店铺的真实订单 ID |

### 响应字段

详情对象保存在 `data`。字段由后端按下表保留，缺失或 null 的字段可能省略。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `order_id` | 字符串 | 订单 ID，在当前店铺内使用。 |
| `statuses`、`status` | 字符串数组、字符串 | `statuses` 汇总订单行状态，同一订单可能含多种状态。 |
| `created_at`、`updated_at` | 字符串 | 创建及更新时间。 |
| `items_count` | 数值或数字字符串 | 商品行数量，按实际字段展示。 |
| `price`、`shipping_fee`、`voucher` | 数值或数字字符串 | 价格、运费与优惠。价格字段需结合优惠及运费解释买家实付。 |
| `currency` | 字符串 | 金额币种。 |

[Lazada 订单字段说明](https://open.lazada.com/apps/doc/doc?docId=121327&nodeId=29616)

## 订单商品明细

`getOrderItems` → `GET /order/items/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `order_id` | 1 至 20 位的正整数文本 | 是 | 当前店铺的真实订单 ID |

### 响应字段

商品行保存在 `data` 数组，空数组是成功结果。同款商品可有多个 `order_item_id`，核对时分别保留。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `order_item_id`、`order_id` | 字符串 | 订单行 ID 和所属订单 ID。 |
| `item_id`、`product_id` | 字符串 | 上游返回的商品标识，按实际字段区分。 |
| `sku`、`shop_sku`、`name`、`status` | 字符串 | SKU、商品名称和行状态。 |
| `created_at`、`updated_at` | 字符串 | 商品行创建及更新时间。 |
| `item_price`、`paid_price`、`shipping_amount`、`voucher_amount` | 数值或数字字符串 | 行价格、实付、运费与优惠。 |
| `currency`、`quantity` | 字符串、数值或数字字符串 | 金额币种及数量，按实际字段展示。 |

订单数据以服务端保留的业务字段为准。输出前额外移除地址、买家姓名和联系方式。 [Lazada 订单商品响应示例](https://open.lazada.com/apps/doc/doc?docId=121784&nodeId=45697)

## 履约、售后、评价与会话

发货及逆向单使用 [履约与售后接口](order-operations.md)。评价和买家会话使用 [评价与店铺会话接口](communications.md)。订单列表、详情和商品行继续使用本页的原查询入口。

## 已接收店铺通知

`POST /lazada/events` 读取该连接已接收的通知。使用 `python scripts/list_store_events.py '<JSON 参数>'`。

| 请求字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 是 | 当前用户的真实店铺连接 ID。 |
| `limit` | 整数 | 否 | 单页 1–100 条，默认 20。 |
| `beforeId` | 字符串 | 否 | 下一页读取原样使用上页的 `nextBeforeId`。 |

| 保存文件字段 | 类型 | 含义 |
| --- | --- | --- |
| `events` | 对象数组 | 按接收记录倒序返回。本页无记录时为空数组。 |
| `events[].eventId`、`events[].notifyId` | 字符串 | LinkFox 事件记录及通知标识。 |
| `events[].type` | 字符串 | 事件类型。 |
| `events[].occurredAt` | 整数 | 事件时间，Unix 毫秒。 |
| `events[].status` | 字符串 | 事件携带的状态，可缺失。 |
| `events[].orderId`、`orderItemId`、`productId`、`skuId`、`reverseOrderId`、`reverseOrderLineId`、`packageId` | 字符串 | 事件关联的业务标识，按类型提供。 |
| `nextBeforeId` | 字符串或 null | 下一页游标。网关省略此字段时，CLI 文件中为 null，表示无下一页。 |

通知来自已配置且通过可信入口接收的推送。空列表只表示当前连接在本次查询范围内无记录。核对实际业务状态时查询原订单、商品或售后接口。

## 错误处理

- HTTP 2xx 且 JSON `errcode` 缺失、为 null、为空字符串或纯空白，或者是 200–299 的整数或数字字符串，才继续检查业务数据。`0`、`false` 与 XML `ToolErrorResponse` 属于失败。失败时保存可用诊断并以非零状态退出。
- 输出可用的 `httpStatus`、`errcode`、`requestId`、`traceId` 以及服务端提供的 `upstreamCode`、`upstreamRequestId`，省略原始错误正文。
- `error=REAUTHORIZATION_REQUIRED` 时通过授权 Skill 核对该店铺连接。单凭 401 无法区分店铺授权和 LinkFox Key，应结合诊断定位。已确认 LinkFox Key 故障时按 [认证和算力指引](onboarding.md) 处理。
- `error=LAZADA_PROXY_FORBIDDEN` 时将代理出口白名单问题交给接入维护方核查。其他 403 时核对店铺或应用权限。出现 402 时先按实际调用的接口核对网关账户或计费诊断。
- `upstreamCode=SellerNotVerified` 表示 Lazada 尚未验证该卖家。请用户在对应站点的卖家中心确认验证状态，完成后再查询。
- 超时或 5xx 保留请求标识，脚本不会自动重发。

## Feedback

用户明确同意发送反馈后，使用单独的反馈接口。仅提交获准发送的简要内容，省略店铺、订单、买家标识、凭据和原始响应。

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- 请求头 `Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-orders",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "用户同意发送的简要反馈"
}
```

`sentiment` 可选 `POSITIVE`、`NEUTRAL`、`NEGATIVE`。`category` 可选 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。
