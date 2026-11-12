---
name: linkfox-lazada-store-orders
description: 查询和处理已授权 Lazada 店铺的订单、履约与售后，适用于核对订单和商品行、处理发货与取消、查询退货、管理评价。
---
# Lazada 店铺订单与售后

## 适用范围

### 适用

按时间或状态筛选店铺订单，核对订单详情及商品行，处理履约、取消、售后和评价。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查这个店铺最近创建或更新的订单 | 订单列表，按时间或状态筛选。 |
| 看这笔订单现在是什么状态 | 订单详情，查看订单状态、时间和可用金额字段。 |
| 核对这笔订单有哪些商品、SKU 和金额 | 订单商品明细，逐条查看商品行。 |
| 查看店铺收到的订单或售后通知 | 按店铺读取已接收通知，核对当前状态时回查订单或售后。 |
| 核对发货方式、打包、标记待揽收 | 按订单行和包裹处理履约。 |
| 看退货申请、处理售后或取消 | 查看申请和可用原因，核对具体订单行后处理。 |
| 回复商品评价 | 先读取原评价，再按已确认的目标回复。 |

### 边界

店铺绑定或授权失效时使用 `linkfox-lazada-store-auth`，商品档案查询使用 `linkfox-lazada-store-product`，对账使用 `linkfox-lazada-store-finance`。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 接口文档 | 对应脚本 | 性质 |
| --- | --- | --- | --- | --- |
| 订单列表 `listOrders` | `POST /lazada/developerProxy` → `GET /orders/get` | [接口说明](references/api.md#接口订单列表listorders) | `scripts/list_orders.py` | 只读 |
| 订单详情 `getOrder` | `POST /lazada/developerProxy` → `GET /order/get` | [接口说明](references/api.md#接口订单详情getorder) | `scripts/get_order.py` | 只读 |
| 订单商品明细 `getOrderItems` | `POST /lazada/developerProxy` → `GET /order/items/get` | [接口说明](references/api.md#接口订单商品明细getorderitems) | `scripts/get_order_items.py` | 只读 |
| 已接收店铺通知 | `POST /lazada/events` | [接口说明](references/api.md#接口已接收店铺通知liststoreevents) | `scripts/list_store_events.py` | 只读 |
| 查询可用物流服务 `getShipmentProviders` | `POST /lazada/orders` → `POST /order/shipment/providers/get` | [接口说明](references/order-operations.md#接口查询可用物流服务getshipmentproviders) | `scripts/orders_api.py getShipmentProviders` | 只读 |
| 获取运单标签 `getShippingLabel` | `POST /lazada/orders` → `POST /order/package/document/get` | [接口说明](references/order-operations.md#接口获取运单标签getshippinglabel) | `scripts/orders_api.py getShippingLabel` | 只读 |
| 查询物流轨迹 `getOrderTrace` | `POST /lazada/orders` → `GET /logistic/order/trace` | [接口说明](references/order-operations.md#接口查询物流轨迹getordertrace) | `scripts/orders_api.py getOrderTrace` | 只读 |
| 查询可取消范围及原因 `validateOrderCancellation` | `POST /lazada/orders` → `GET /order/reverse/cancel/validate` | [接口说明](references/order-operations.md#接口查询可取消范围及原因validateordercancellation) | `scripts/orders_api.py validateOrderCancellation` | 只读 |
| 查询逆向单列表 `listReverseOrders` | `POST /lazada/orders` → `GET /reverse/getreverseordersforseller` | [接口说明](references/order-operations.md#接口查询逆向单列表listreverseorders) | `scripts/orders_api.py listReverseOrders` | 只读 |
| 查询逆向单详情 `getReverseOrder` | `POST /lazada/orders` → `GET /order/reverse/return/detail/list` | [接口说明](references/order-operations.md#接口查询逆向单详情getreverseorder) | `scripts/orders_api.py getReverseOrder` | 只读 |
| 查询售后原因 `listReverseOrderReasons` | `POST /lazada/orders` → `GET /order/reverse/reason/list` | [接口说明](references/order-operations.md#接口查询售后原因listreverseorderreasons) | `scripts/orders_api.py listReverseOrderReasons` | 只读 |
| 查询售后历史 `listReverseOrderHistory` | `POST /lazada/orders` → `GET /order/reverse/return/history/list` | [接口说明](references/order-operations.md#接口查询售后历史listreverseorderhistory) | `scripts/orders_api.py listReverseOrderHistory` | 只读 |
| 打包 `packOrder` | `POST /lazada/orders` → `POST /order/fulfill/pack` | [接口说明](references/order-operations.md#接口打包packorder) | `scripts/orders_api.py packOrder` | 写入 |
| 重新打包 `repackOrder` | `POST /lazada/orders` → `POST /order/package/repack` | [接口说明](references/order-operations.md#接口重新打包repackorder) | `scripts/orders_api.py repackOrder` | 写入 |
| 标记待揽收 `readyToShip` | `POST /lazada/orders` → `POST /order/package/rts` | [接口说明](references/order-operations.md#接口标记待揽收readytoship) | `scripts/orders_api.py readyToShip` | 写入 |
| 确认商家配送送达 `confirmDbsDelivery` | `POST /lazada/orders` → `POST /order/package/sof/delivered` | [接口说明](references/order-operations.md#接口确认商家配送送达confirmdbsdelivery) | `scripts/orders_api.py confirmDbsDelivery` | 写入 |
| 标记商家配送失败 `markDbsDeliveryFailed` | `POST /lazada/orders` → `POST /order/package/sof/failed_delivery` | [接口说明](references/order-operations.md#接口标记商家配送失败markdbsdeliveryfailed) | `scripts/orders_api.py markDbsDeliveryFailed` | 写入 |
| 标记数字订单交付 `deliverDigitalOrder` | `POST /lazada/orders` → `POST /order/digital/delivered` | [接口说明](references/order-operations.md#接口标记数字订单交付deliverdigitalorder) | `scripts/orders_api.py deliverDigitalOrder` | 写入 |
| 取消订单行 `cancelOrder` | `POST /lazada/orders` → `GET /order/reverse/cancel/create` | [接口说明](references/order-operations.md#接口取消订单行cancelorder) | `scripts/orders_api.py cancelOrder` | 写入 |
| 处理逆向单 `updateReverseOrder` | `POST /lazada/orders` → `GET /order/reverse/return/update` | [接口说明](references/order-operations.md#接口处理逆向单updatereverseorder) | `scripts/orders_api.py updateReverseOrder` | 写入 |
| 处理买家取消申请 `decideOrderCancellation` | `POST /lazada/orders` → `GET /order/reverse/cancel/seller/decide` | [接口说明](references/order-operations.md#接口处理买家取消申请decideordercancellation) | `scripts/orders_api.py decideOrderCancellation` | 写入 |
| 处理仅退款申请 `decideOnlyRefund` | `POST /lazada/orders` → `GET /order/reverse/onlyrefund/seller/decide` | [接口说明](references/order-operations.md#接口处理仅退款申请decideonlyrefund) | `scripts/orders_api.py decideOnlyRefund` | 写入 |
| 评价历史 `listReviewHistory` | `POST /lazada/orders` → `GET /review/seller/history/list` | [接口说明](references/communications.md#接口评价历史listreviewhistory) | `scripts/orders_api.py listReviewHistory` | 只读 |
| 按评价 ID 查询 `getReviews` | `POST /lazada/orders` → `GET /review/seller/list/v2` | [接口说明](references/communications.md#接口按评价-id-查询getreviews) | `scripts/orders_api.py getReviews` | 只读 |
| 提交卖家回复 `replyReview` | `POST /lazada/orders` → `GET /review/seller/reply/add` | [接口说明](references/communications.md#接口提交卖家回复replyreview) | `scripts/orders_api.py replyReview` | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | [写入与续查](references/order-operations.md#接口查询写入状态operationstatus) | `scripts/orders_api.py operationStatus` | 只读 |

## 前置条件

配置当前用户的 LinkFox Key，再通过 `linkfox-lazada-store-auth` 获取已授权的连接。只有一条符合条件的连接时直接使用，有多条候选时按店铺名称、站点和卖家 ID 确认目标。把目标记录的 `connectionId` 原样传入。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md` 及接口清单中的对应文档。
- **脚本调用（推荐）**：使用 Python 3.9+，`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **业务操作入口**：`python scripts/orders_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **成本约束**：本技能不消耗算力，业务调用通过输出预检后实时请求一次，不启用 24 小时响应缓存。按用户任务范围分页或查询原申请／写记录，不因失败或空结果自动扩大范围或重放写入。

本地输入、默认值、构参映射及保存结果见 [脚本使用说明](references/script-usage.md)。

### 输出策略

- 始终保存可保存的完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 响应体不超过 8000 字节：保存后，将完整脱敏 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用诊断、最大列表字段的长度和最多前三项样本。
- 添加 `--inline` 可强制全量打印可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 运单标签仅在用户明确要求时查询。终端只显示回执和本地文件路径，该操作禁用 `--inline`。

先通过摘要判断数据是否足够。以 `Saved full response:` 后的实际文件路径为准；需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

- 按时间或状态筛选时查询订单列表，核对一笔订单时用原始订单 ID 查询详情或商品明细。需要下一页时按接口参考推进偏移量。
- 履约前读取真实订单行与当前状态。取消前先检查可取消范围及原因。售后按逆向单和逆向商品行处理。
- 提交打包、取消、售后或回复等动作前，向用户列明目标、范围与内容，取得明确授权。超时或结果不明时，用原 UUID 查询 `operationStatus`。

### 算力消耗

本 Skill 的订单查询、通知、履约、售后、评价及写入状态查询均为 0 算力/次。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`；先结合接口诊断确认是 LinkFox 用户认证或计费问题。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

Lazada 店铺授权失效、卖家未验证、应用权限或代理限制按接口参考处理。短信、登录和算力订单按用户已授权范围执行；订单结果不明先核对原订单。可选二维码依赖为 qrcode 和 Pillow，未安装时使用支付链接，不静默安装。

### 约束与建议

- 多名用户绑定同店时，通知按店铺共享，但查询始终使用当前用户的连接。切换 LinkFox 用户后重新列店。
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

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引整理脱敏反馈，不要打断用户当前流程。仅在用户授权发送后提交。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
