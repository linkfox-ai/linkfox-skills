# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件说明本地 CLI 输入、构参和保存结果；CLI 补充字段不是网关 DTO。业务字段以各接口参考为准。

## 共享脚本约定

### 脚本输入与构参

使用 Python 3.9+，普通业务入口和公共调用器仅用标准库。具名脚本接受一个 JSON 对象；带操作名的入口接受 `<操作> '<JSON 参数>'` 或 `<操作> --params-file <UTF-8 JSON 文件>`，两种参数来源互斥。各操作名大小写固定，无额外别名。

| 参数／选项 | 类型 | 默认／说明 |
|---|---|---|
| `connectionId` | 字符串 | 从当前用户店铺列表原样取值，不复用其他用户连接。 |
| `params` | 对象 | 业务操作默认 `{}`，有必填业务参数时仍须提供；原生对象／数组不转换为字符串，明确要求 JSON／XML 文本的字段除外。 |
| `queryParams` | 对象 | 商品／订单只读脚本默认 `{}`，按操作校验必填查询条件；不接受 `params` 别名。 |
| `requestId` | 字符串 | 写入或续查须提供带连字符 UUID，脚本转成小写；不自动生成，不用于只读业务查询。 |
| `--params-file` | CLI 选项 | 仅带操作名的入口支持，读取 UTF-8／UTF-8 BOM JSON；不上传参数文件本身。 |
| `--inline` | CLI 开关 | 默认关闭，开启时打印全部可保存数据，同时仍保存文件；运单标签例外见对应操作。 |
| `--no-cache` | CLI 开关 | 所有业务调用均实时执行，无缓存读写；保留此兼容选项，不允许重试或跳过保存。 |

网关与双 Key 的优先级、请求头及超时见 [公共规则](api.md#公共规则)。未知顶层字段会在请求前拒绝；业务层只构参、检查业务结果，公共 `call_api.run` 统一传输和保存。ID 保持原类型和精度，不把字符串 ID 转成浮点数。

### 脚本输出与业务结果

输出先经过预检，再发起一次请求，不自动重试。结果保存到当前工作目录 `linkfox/<YYYY-MM-DD>/<session>/data/`，优先使用 `SESSION_ID`，缺省使用时间和随机标识；文件名包含技能、操作、时间及随机后缀。输出或元数据不可写时在请求前失败，不回退到临时目录。

| 本地字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作允许的标量／null | 去除可选网关外层包装后的业务结果，保留内层层次和类型；凭据与不应展示的敏感字段被移除。事件命令使用下方单独的输出结构。 |
| `requestId` | 字符串或 null | 上游请求标识。 |
| `clientRequestId` | 字符串 | 写入／续查使用的原 UUID，异常时仍尽可能保留。 |
| `status` | 字符串 | 原写记录或授权申请状态，不与 HTTP 状态混用。 |
| `success` | 布尔值 | CLI 调用结果。写入仅 `SUCCEEDED` 为 true；成功查询状态时仍须检查原 `status`。 |
| `httpStatus`、`errcode`、`errorCode`、`code` | 整数或字符串，可缺省 | 失败时可保留的网关传输诊断；不等于上游 HTTP。 |
| `error` | 字符串，可缺省 | 本地错误分类。 |
| `traceId`、`upstreamCode`、`upstreamRequestId` | 字符串，可缺省 | 经过格式校验的跟踪标识或从服务端安全消息提取的上游诊断。 |

响应不超过 8000 字节时打印完整脱敏 JSON；较大响应打印顶层字段、诊断和最大列表的长度及最多前三项样本。以 `Saved full response:` 后的实际路径为准。`--inline` 不解除脱敏。业务失败、HTTP／网关／结构异常为非零退出；本地参数／输出预检失败通常为 2，远程失败为 1，成功为 0。原始错误正文、Key 和店铺令牌不保存。

`REAUTHORIZATION_REQUIRED` 先核对店铺授权，`LAZADA_PROXY_FORBIDDEN` 核对代理出口；`SellerNotVerified` 表示卖家未验证；范围和权限问题不当作 LinkFox 登录或计费故障。写入结果不明时仅用原 UUID 查询状态，核对目标实际状态后再决定下一步。

## 接口：订单列表（listOrders）

### 脚本输入与构参

`python scripts/list_orders.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `queryParams` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口订单列表listorders)；不展开为顶层字段。 |

脚本固定填入 `operation=listOrders`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/developerProxy` → `GET /orders/get`。参数约束与业务字段见 [接口说明](api.md#接口订单列表listorders)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口订单列表listorders) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：订单详情（getOrder）

### 脚本输入与构参

`python scripts/get_order.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `queryParams` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口订单详情getorder)；不展开为顶层字段。 |

脚本固定填入 `operation=getOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/developerProxy` → `GET /order/get`。参数约束与业务字段见 [接口说明](api.md#接口订单详情getorder)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口订单详情getorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：订单商品明细（getOrderItems）

### 脚本输入与构参

`python scripts/get_order_items.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `queryParams` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口订单商品明细getorderitems)；不展开为顶层字段。 |

脚本固定填入 `operation=getOrderItems`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/developerProxy` → `GET /order/items/get`。参数约束与业务字段见 [接口说明](api.md#接口订单商品明细getorderitems)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口订单商品明细getorderitems) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：已接收店铺通知（listStoreEvents）

### 脚本输入与构参

`python scripts/list_store_events.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `limit` | 整数 | 否，默认 20，范围 1–100。 |
| `beforeId` | 字符串 | 否，使用上页 `nextBeforeId`；正整数文本，须在有符号 64 位范围内。 |

输入对象原样发送，不增加 `operation`。

网关及上游映射为 `POST /lazada/events`。参数约束与业务字段见 [接口说明](api.md#接口已接收店铺通知liststoreevents)。

### 脚本输出与业务结果

保存 `events`、`nextBeforeId` 和 `success`；网关未提供游标时归一为 null。事件仅保留已定义标识、类型、整数时间和字符串状态，不把缺失状态补为空字符串。

## 接口：查询可用物流服务（getShipmentProviders）

### 脚本输入与构参

`python scripts/orders_api.py getShipmentProviders '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询可用物流服务getshipmentproviders)；不展开为顶层字段。 |

脚本固定填入 `operation=getShipmentProviders`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/shipment/providers/get`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询可用物流服务getshipmentproviders)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询可用物流服务getshipmentproviders) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：获取运单标签（getShippingLabel）

### 脚本输入与构参

`python scripts/orders_api.py getShippingLabel '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口获取运单标签getshippinglabel)；不展开为顶层字段。 |

脚本固定填入 `operation=getShippingLabel`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/package/document/get`。参数约束与业务字段见 [接口说明](order-operations.md#接口获取运单标签getshippinglabel)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口获取运单标签getshippinglabel) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。 运单结果可能含收件信息，仅保存本地文件并输出诊断，拒绝 `--inline`；POSIX 创建权限为 0600。响应必须包含实际 `file` 或 `pdf_url` 才成功。

## 接口：查询物流轨迹（getOrderTrace）

### 脚本输入与构参

`python scripts/orders_api.py getOrderTrace '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询物流轨迹getordertrace)；不展开为顶层字段。 |

脚本固定填入 `operation=getOrderTrace`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /logistic/order/trace`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询物流轨迹getordertrace)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询物流轨迹getordertrace) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：查询可取消范围及原因（validateOrderCancellation）

### 脚本输入与构参

`python scripts/orders_api.py validateOrderCancellation '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询可取消范围及原因validateordercancellation)；不展开为顶层字段。 |

脚本固定填入 `operation=validateOrderCancellation`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/cancel/validate`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询可取消范围及原因validateordercancellation)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询可取消范围及原因validateordercancellation) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：查询逆向单列表（listReverseOrders）

### 脚本输入与构参

`python scripts/orders_api.py listReverseOrders '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询逆向单列表listreverseorders)；不展开为顶层字段。 |

脚本固定填入 `operation=listReverseOrders`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /reverse/getreverseordersforseller`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询逆向单列表listreverseorders)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询逆向单列表listreverseorders) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：查询逆向单详情（getReverseOrder）

### 脚本输入与构参

`python scripts/orders_api.py getReverseOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询逆向单详情getreverseorder)；不展开为顶层字段。 |

脚本固定填入 `operation=getReverseOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/return/detail/list`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询逆向单详情getreverseorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询逆向单详情getreverseorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：查询售后原因（listReverseOrderReasons）

### 脚本输入与构参

`python scripts/orders_api.py listReverseOrderReasons '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询售后原因listreverseorderreasons)；不展开为顶层字段。 |

脚本固定填入 `operation=listReverseOrderReasons`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/reason/list`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询售后原因listreverseorderreasons)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询售后原因listreverseorderreasons) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：查询售后历史（listReverseOrderHistory）

### 脚本输入与构参

`python scripts/orders_api.py listReverseOrderHistory '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口查询售后历史listreverseorderhistory)；不展开为顶层字段。 |

脚本固定填入 `operation=listReverseOrderHistory`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/return/history/list`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询售后历史listreverseorderhistory)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口查询售后历史listreverseorderhistory) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：打包（packOrder）

### 脚本输入与构参

`python scripts/orders_api.py packOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口打包packorder)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=packOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/fulfill/pack`。参数约束与业务字段见 [接口说明](order-operations.md#接口打包packorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口打包packorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：重新打包（repackOrder）

### 脚本输入与构参

`python scripts/orders_api.py repackOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口重新打包repackorder)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=repackOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/package/repack`。参数约束与业务字段见 [接口说明](order-operations.md#接口重新打包repackorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口重新打包repackorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：标记待揽收（readyToShip）

### 脚本输入与构参

`python scripts/orders_api.py readyToShip '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口标记待揽收readytoship)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=readyToShip`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/package/rts`。参数约束与业务字段见 [接口说明](order-operations.md#接口标记待揽收readytoship)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口标记待揽收readytoship) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：确认商家配送送达（confirmDbsDelivery）

### 脚本输入与构参

`python scripts/orders_api.py confirmDbsDelivery '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口确认商家配送送达confirmdbsdelivery)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=confirmDbsDelivery`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/package/sof/delivered`。参数约束与业务字段见 [接口说明](order-operations.md#接口确认商家配送送达confirmdbsdelivery)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口确认商家配送送达confirmdbsdelivery) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：标记商家配送失败（markDbsDeliveryFailed）

### 脚本输入与构参

`python scripts/orders_api.py markDbsDeliveryFailed '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口标记商家配送失败markdbsdeliveryfailed)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=markDbsDeliveryFailed`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/package/sof/failed_delivery`。参数约束与业务字段见 [接口说明](order-operations.md#接口标记商家配送失败markdbsdeliveryfailed)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口标记商家配送失败markdbsdeliveryfailed) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：标记数字订单交付（deliverDigitalOrder）

### 脚本输入与构参

`python scripts/orders_api.py deliverDigitalOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口标记数字订单交付deliverdigitalorder)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=deliverDigitalOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `POST /order/digital/delivered`。参数约束与业务字段见 [接口说明](order-operations.md#接口标记数字订单交付deliverdigitalorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口标记数字订单交付deliverdigitalorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：取消订单行（cancelOrder）

### 脚本输入与构参

`python scripts/orders_api.py cancelOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口取消订单行cancelorder)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=cancelOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/cancel/create`。参数约束与业务字段见 [接口说明](order-operations.md#接口取消订单行cancelorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口取消订单行cancelorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：处理逆向单（updateReverseOrder）

### 脚本输入与构参

`python scripts/orders_api.py updateReverseOrder '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口处理逆向单updatereverseorder)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateReverseOrder`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/return/update`。参数约束与业务字段见 [接口说明](order-operations.md#接口处理逆向单updatereverseorder)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口处理逆向单updatereverseorder) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：处理买家取消申请（decideOrderCancellation）

### 脚本输入与构参

`python scripts/orders_api.py decideOrderCancellation '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口处理买家取消申请decideordercancellation)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=decideOrderCancellation`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/cancel/seller/decide`。参数约束与业务字段见 [接口说明](order-operations.md#接口处理买家取消申请decideordercancellation)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口处理买家取消申请decideordercancellation) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：处理仅退款申请（decideOnlyRefund）

### 脚本输入与构参

`python scripts/orders_api.py decideOnlyRefund '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](order-operations.md#接口处理仅退款申请decideonlyrefund)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=decideOnlyRefund`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /order/reverse/onlyrefund/seller/decide`。参数约束与业务字段见 [接口说明](order-operations.md#接口处理仅退款申请decideonlyrefund)。

### 脚本输出与业务结果

按 [接口响应结构](order-operations.md#接口处理仅退款申请decideonlyrefund) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：评价历史（listReviewHistory）

### 脚本输入与构参

`python scripts/orders_api.py listReviewHistory '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](communications.md#接口评价历史listreviewhistory)；不展开为顶层字段。 |

脚本固定填入 `operation=listReviewHistory`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /review/seller/history/list`。参数约束与业务字段见 [接口说明](communications.md#接口评价历史listreviewhistory)。

### 脚本输出与业务结果

按 [接口响应结构](communications.md#接口评价历史listreviewhistory) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：按评价 ID 查询（getReviews）

### 脚本输入与构参

`python scripts/orders_api.py getReviews '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](communications.md#接口按评价-id-查询getreviews)；不展开为顶层字段。 |

脚本固定填入 `operation=getReviews`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /review/seller/list/v2`。参数约束与业务字段见 [接口说明](communications.md#接口按评价-id-查询getreviews)。

### 脚本输出与业务结果

按 [接口响应结构](communications.md#接口按评价-id-查询getreviews) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：提交卖家回复（replyReview）

### 脚本输入与构参

`python scripts/orders_api.py replyReview '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](communications.md#接口提交卖家回复replyreview)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=replyReview`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/orders` → `GET /review/seller/reply/add`。参数约束与业务字段见 [接口说明](communications.md#接口提交卖家回复replyreview)。

### 脚本输出与业务结果

按 [接口响应结构](communications.md#接口提交卖家回复replyreview) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：查询写入状态（operationStatus）

### 脚本输入与构参

`python scripts/orders_api.py operationStatus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `requestId` | UUID 字符串 | 是，原写入 UUID 转小写发送；不传 `operation` 和 `params`。 |


网关及上游映射为 `POST /lazada/operationStatus`。参数约束与业务字段见 [接口说明](order-operations.md#接口查询写入状态operationstatus)。

### 脚本输出与业务结果

保存原 `clientRequestId`、上游 `requestId`、`status`、`data` 和 `success`。状态查询完成即可 `success=true`；原写入仍可能 `REJECTED`、`PARTIAL` 或 `UNKNOWN`。
