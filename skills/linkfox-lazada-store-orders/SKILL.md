---
name: linkfox-lazada-store-orders
description: 查询和处理已授权 Lazada 店铺的订单、履约与售后，适用于核对订单和商品行、处理发货与取消、查询退货、管理评价和店铺会话。
---
# Lazada 店铺订单与售后

## 适用范围

### 适用

按时间或状态筛选店铺订单，核对订单详情及商品行，处理履约、取消、售后、评价和店铺会话。

| 用户表达 | 查询场景 |
|---|---|
| 查这个店铺最近创建或更新的订单 | 订单列表，按时间或状态筛选。 |
| 看这笔订单现在是什么状态 | 订单详情，查看订单状态、时间和可用金额字段。 |
| 核对这笔订单有哪些商品、SKU 和金额 | 订单商品明细，逐条查看商品行。 |
| 查看店铺收到的订单或售后通知 | 按店铺读取已接收通知，核对当前状态时回查订单或售后。 |
| 核对发货方式、打包、标记待揽收 | 按订单行和包裹处理履约。 |
| 看退货申请、处理售后或取消 | 查看申请和可用原因，核对具体订单行后处理。 |
| 回复商品评价或买家消息 | 先读取原评价或会话，再按已确认的目标回复。 |

### 边界

店铺绑定或授权失效时使用 `linkfox-lazada-store-auth`，商品档案查询使用 `linkfox-lazada-store-product`，对账使用 `linkfox-lazada-store-finance`。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 对应脚本 | 接口文档 | 性质 |
| --- | --- | --- | --- | --- |
| 订单列表 `listOrders` | `POST /lazada/developerProxy` → `GET /orders/get` | `scripts/list_orders.py` | [接口说明](references/api.md#订单列表) | 只读 |
| 订单详情 `getOrder` | `POST /lazada/developerProxy` → `GET /order/get` | `scripts/get_order.py` | [接口说明](references/api.md#订单详情) | 只读 |
| 订单商品明细 `getOrderItems` | `POST /lazada/developerProxy` → `GET /order/items/get` | `scripts/get_order_items.py` | [接口说明](references/api.md#订单商品明细) | 只读 |
| 已接收店铺通知 | `POST /lazada/events` | `scripts/list_store_events.py` | [接口说明](references/api.md#已接收店铺通知) | 只读 |
| 查询可用物流服务 `getShipmentProviders` | `POST /lazada/orders` → `POST /order/shipment/providers/get` | `scripts/orders_api.py getShipmentProviders` | [接口说明](references/order-operations.md#查询可用物流服务getshipmentproviders) | 只读 |
| 获取运单标签 `getShippingLabel` | `POST /lazada/orders` → `POST /order/package/document/get` | `scripts/orders_api.py getShippingLabel` | [接口说明](references/order-operations.md#获取运单标签getshippinglabel) | 只读 |
| 查询物流轨迹 `getOrderTrace` | `POST /lazada/orders` → `GET /logistic/order/trace` | `scripts/orders_api.py getOrderTrace` | [接口说明](references/order-operations.md#查询物流轨迹getordertrace) | 只读 |
| 查询可取消范围及原因 `validateOrderCancellation` | `POST /lazada/orders` → `GET /order/reverse/cancel/validate` | `scripts/orders_api.py validateOrderCancellation` | [接口说明](references/order-operations.md#查询可取消范围及原因validateordercancellation) | 只读 |
| 查询逆向单列表 `listReverseOrders` | `POST /lazada/orders` → `GET /reverse/getreverseordersforseller` | `scripts/orders_api.py listReverseOrders` | [接口说明](references/order-operations.md#查询逆向单列表listreverseorders) | 只读 |
| 查询逆向单详情 `getReverseOrder` | `POST /lazada/orders` → `GET /order/reverse/return/detail/list` | `scripts/orders_api.py getReverseOrder` | [接口说明](references/order-operations.md#查询逆向单详情getreverseorder) | 只读 |
| 查询售后原因 `listReverseOrderReasons` | `POST /lazada/orders` → `GET /order/reverse/reason/list` | `scripts/orders_api.py listReverseOrderReasons` | [接口说明](references/order-operations.md#查询售后原因listreverseorderreasons) | 只读 |
| 查询售后历史 `listReverseOrderHistory` | `POST /lazada/orders` → `GET /order/reverse/return/history/list` | `scripts/orders_api.py listReverseOrderHistory` | [接口说明](references/order-operations.md#查询售后历史listreverseorderhistory) | 只读 |
| 打包 `packOrder` | `POST /lazada/orders` → `POST /order/fulfill/pack` | `scripts/orders_api.py packOrder` | [接口说明](references/order-operations.md#打包packorder) | 写入 |
| 重新打包 `repackOrder` | `POST /lazada/orders` → `POST /order/package/repack` | `scripts/orders_api.py repackOrder` | [接口说明](references/order-operations.md#重新打包repackorder) | 写入 |
| 标记待揽收 `readyToShip` | `POST /lazada/orders` → `POST /order/package/rts` | `scripts/orders_api.py readyToShip` | [接口说明](references/order-operations.md#标记待揽收readytoship) | 写入 |
| 确认商家配送送达 `confirmDbsDelivery` | `POST /lazada/orders` → `POST /order/package/sof/delivered` | `scripts/orders_api.py confirmDbsDelivery` | [接口说明](references/order-operations.md#确认商家配送送达confirmdbsdelivery) | 写入 |
| 标记商家配送失败 `markDbsDeliveryFailed` | `POST /lazada/orders` → `POST /order/package/sof/failed_delivery` | `scripts/orders_api.py markDbsDeliveryFailed` | [接口说明](references/order-operations.md#标记商家配送失败markdbsdeliveryfailed) | 写入 |
| 标记数字订单交付 `deliverDigitalOrder` | `POST /lazada/orders` → `POST /order/digital/delivered` | `scripts/orders_api.py deliverDigitalOrder` | [接口说明](references/order-operations.md#标记数字订单交付deliverdigitalorder) | 写入 |
| 取消订单行 `cancelOrder` | `POST /lazada/orders` → `GET /order/reverse/cancel/create` | `scripts/orders_api.py cancelOrder` | [接口说明](references/order-operations.md#取消订单行cancelorder) | 写入 |
| 处理逆向单 `updateReverseOrder` | `POST /lazada/orders` → `GET /order/reverse/return/update` | `scripts/orders_api.py updateReverseOrder` | [接口说明](references/order-operations.md#处理逆向单updatereverseorder) | 写入 |
| 处理买家取消申请 `decideOrderCancellation` | `POST /lazada/orders` → `GET /order/reverse/cancel/seller/decide` | `scripts/orders_api.py decideOrderCancellation` | [接口说明](references/order-operations.md#处理买家取消申请decideordercancellation) | 写入 |
| 处理仅退款申请 `decideOnlyRefund` | `POST /lazada/orders` → `GET /order/reverse/onlyrefund/seller/decide` | `scripts/orders_api.py decideOnlyRefund` | [接口说明](references/order-operations.md#处理仅退款申请decideonlyrefund) | 写入 |
| 评价历史 `listReviewHistory` | `POST /lazada/orders` → `GET /review/seller/history/list` | `scripts/orders_api.py listReviewHistory` | [接口说明](references/communications.md#评价历史listreviewhistory) | 只读 |
| 按评价 ID 查询 `getReviews` | `POST /lazada/orders` → `GET /review/seller/list/v2` | `scripts/orders_api.py getReviews` | [接口说明](references/communications.md#按评价-id-查询getreviews) | 只读 |
| 提交卖家回复 `replyReview` | `POST /lazada/orders` → `GET /review/seller/reply/add` | `scripts/orders_api.py replyReview` | [接口说明](references/communications.md#提交卖家回复replyreview) | 写入 |
| 会话列表 `listChatSessions` | `POST /lazada/orders` → `GET /im/session/list` | `scripts/orders_api.py listChatSessions` | [接口说明](references/communications.md#会话列表listchatsessions) | 只读 |
| 会话详情 `getChatSession` | `POST /lazada/orders` → `GET /im/session/get` | `scripts/orders_api.py getChatSession` | [接口说明](references/communications.md#会话详情getchatsession) | 只读 |
| 会话消息 `listChatMessages` | `POST /lazada/orders` → `GET /im/message/list` | `scripts/orders_api.py listChatMessages` | [接口说明](references/communications.md#会话消息listchatmessages) | 只读 |
| 发送买家消息 `sendChatMessage` | `POST /lazada/orders` → `POST /im/message/send` | `scripts/orders_api.py sendChatMessage` | [接口说明](references/communications.md#发送买家消息sendchatmessage) | 写入 |
| 标记会话已读 `markChatRead` | `POST /lazada/orders` → `POST /im/session/read` | `scripts/orders_api.py markChatRead` | [接口说明](references/communications.md#标记会话已读markchatread) | 写入 |
| 创建订单会话 `openChatSession` | `POST /lazada/orders` → `POST /im/session/open` | `scripts/orders_api.py openChatSession` | [接口说明](references/communications.md#创建订单会话openchatsession) | 写入 |
| 撤回消息 `recallChatMessage` | `POST /lazada/orders` → `POST /im/message/recall` | `scripts/orders_api.py recallChatMessage` | [接口说明](references/communications.md#撤回消息recallchatmessage) | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | `scripts/orders_api.py operationStatus` | [写入与续查](references/order-operations.md#写入与续查) | 只读 |

## 前置条件

配置当前用户的 LinkFox Key，再通过 `linkfox-lazada-store-auth` 获取已授权的连接。只有一条符合条件的连接时直接使用，有多条候选时按店铺名称、站点和卖家 ID 确认目标。把目标记录的 `connectionId` 原样传入。

## 执行方式

- **脚本调用（推荐）**。使用 Python 3.9+ 运行 `python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **履约及沟通**。运行 `python scripts/orders_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **接口调用**。请求字段、成功结构和错误处理见 [接口参考](references/api.md)。
- **调用约束**。业务脚本通过预检后发起一次实时请求。列表只取一页，按用户任务范围继续分页。

### 输出策略

- 可保存的结果写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 成功结果不超过 8000 字节时，保存后打印完整 JSON。更大的结果打印摘要，主要列表最多展示前三项。`--inline` 可打印全部可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 运单标签仅在用户明确要求时查询。终端只显示回执和本地文件路径，该操作禁用 `--inline`。
- 以 `Saved full response:` 后的实际文件路径为准。需要更多字段时，从保存的 JSON 按需提取。

## 执行规则

- 按时间或状态筛选时查询订单列表，核对一笔订单时用原始订单 ID 查询详情或商品明细。需要下一页时按接口参考推进偏移量。
- 履约前读取真实订单行与当前状态。取消前先检查可取消范围及原因。售后按逆向单和逆向商品行处理。
- 提交打包、取消、售后或回复等动作前，向用户列明目标、范围与内容，取得明确授权。超时或结果不明时，用原 UUID 查询 `operationStatus`。

### 算力消耗

本 Skill 的订单查询、通知、履约、售后、评价、会话及写入状态查询均为 0 算力/次。算力消耗以网关实际计费配置为准。

### 解决认证和算力问题

LinkFox Key 未配置或已确认无效时，按 [认证和算力指引](references/onboarding.md) 检查。遇到 401、402 或 403 时，先按 [错误处理](references/api.md#错误处理) 区分网关问题、店铺授权失效与代理限制。

发送短信或使用验证码登录前先取得用户同意。创建算力订单前确认套餐、金额和支付方式。下单结果不明时先核对已有订单。安装了 qrcode 和 Pillow 时可生成二维码图片，也可使用支付链接。

### 约束与建议

- 展示时注明店铺、站点和返回范围。订单 ID 按字符串保留，查询同一笔订单的详情和商品行时沿用原店铺连接。
- 按实际字段解释订单行状态和金额，字段缺失时保留为未知。空列表或失败时说明实际结果。

## 使用示例

替换命令中的店铺连接和订单 ID。

```sh
python scripts/list_orders.py '{"connectionId":"11111111-1111-4111-8111-111111111111","queryParams":{"created_after":"2026-10-01T00:00:00+08:00","limit":20}}'
python scripts/get_order.py '{"connectionId":"11111111-1111-4111-8111-111111111111","queryParams":{"order_id":"123456789"}}'
python scripts/get_order_items.py '{"connectionId":"11111111-1111-4111-8111-111111111111","queryParams":{"order_id":"123456789"}}'
python scripts/orders_api.py listReverseOrders '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{"page_no":1,"page_size":20}}'
```

## 使用反馈

技能出现错误、指引不清或结果不符合预期时，可按 [Feedback](references/api.md#feedback) 整理脱敏摘要。用户授权发送后再提交。

---

更多跨境电商技能见 [LinkFox Skill](https://skill.linkfox.com/)。
