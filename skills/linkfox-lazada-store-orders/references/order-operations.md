# Lazada 履约与售后接口

## 公共规则

请求头、网关基础地址、请求字段、响应 envelope、响应码和写入恢复统一见 [接口总览](api.md#公共规则)。本页各操作只补充业务差异。CLI 参数映射与本地输出见 [script-usage.md](script-usage.md)。

## 接口：查询可用物流服务（getShipmentProviders）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/shipment/providers/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getShipmentProviders`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `getShipmentProvidersReq` | 对象 | 是 | 指定订单及商品行。 |
| `getShipmentProvidersReq.orders` | 对象数组 | 是 | 1–20 个订单条目。 |
| `getShipmentProvidersReq.orders[].order_id` | 正整数 | 是 | 从同店铺读取的订单 ID。 |
| `getShipmentProvidersReq.orders[].order_item_ids` | 正整数数组 | 是 | 非空正整数数组，使用实际 ID，保留精度，同一订单下的商品行不得重复。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或布尔字符串 | 物流服务查询结果。 |
| `data.result.data.platform_default` | 整数或数字字符串 | `1` 表示由平台分配或无法选择中转仓，`0` 表示打包时需要选择。 |
| `data.result.data.shipment_providers` | 对象数组 | 可选中转服务，可为空。 |
| `data.result.data.shipment_providers[].name`、`provider_code` | 字符串 | 服务名称及代码。选择服务后，将代码传入 `packReq.shipment_provider_code`。 |
| `data.result.data.shipping_allocate_type` | 字符串 | `TFS` 或 `NTFS`。将返回值传入 `packReq.shipping_allocate_type`。 |

[Lazada 物流服务接口](https://open.lazada.com/apps/doc/api?path=%2Forder%2Fshipment%2Fproviders%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：获取运单标签（getShippingLabel）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/package/document/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getShippingLabel`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `getDocumentReq` | 对象 | 是 | 标签请求。 |
| `getDocumentReq.doc_type` | 字符串 | 是 | PDF 或 HTML。 |
| `getDocumentReq.packages` | 对象数组 | 是 | 1–20 个不同包裹。 |
| `getDocumentReq.packages[].package_id` | 字符串 | 是 | 同一店铺的真实包裹 ID。 |
| `getDocumentReq.print_item_list` | 布尔值 | 否 | 是否打印商品清单。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.data.file` | 字符串 | 上游提供的文件或标签正文。与 pdf_url 至少返回一个。 |
| `data.result.data.pdf_url` | 字符串 | 上游提供的 PDF 链接。与 file 至少返回一个。 |
| `data.result.data.doc_type` | 字符串 | 上游给出的标签格式，可能缺失。 |

标签可能含收件信息，按用户授权范围处理；本地输出限制见脚本参考。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询物流轨迹（getOrderTrace）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /logistic/order/trace`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getOrderTrace`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `order_id` | 字符串 | 是 | 已标记待揽收的实际订单 ID。 |
| `locale` | 字符串 | 否 | 需要的上游语言或地区代码。 |
| `ofcPackageIdList` | 字符串数组 | 否 | 筛选同一订单的包裹。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success`、`data.result.not_success` | 布尔值或布尔字符串 | 上游查询成功、失败标志。 |
| `data.result.module` | 对象数组 | 订单轨迹列表，空数组表示没有轨迹条目。缺失该字段不当作空列表。 |
| `data.result.module[].ofc_order_id` | 字符串 | 履约订单 ID。 |
| `data.result.module[].package_detail_info_list` | 对象数组 | 包裹列表，包含 ofc_package_id、tracking_number、logistic_detail_info_list。 |
| `logistic_detail_info_list[].status_code`、`title`、`description` | 字符串 | 轨迹状态、标题与说明。 |
| `logistic_detail_info_list[].event_date`、`event_time`、`receive_time` | 字符串 | 上游轨迹时间，按实际时区与格式展示。 |

后端过滤 warehouse_detail_info、order_line_info_list 和 proof_images。字段层次见 [Lazada 物流轨迹接口](https://open.lazada.com/apps/doc/api?path=%2Flogistic%2Forder%2Ftrace)。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询可取消范围及原因（validateOrderCancellation）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/cancel/validate`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=validateOrderCancellation`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `order_id` | 正整数或数字字符串 | 是 | 1–20 位正整数或对应数字字符串，首位不能为 0。 |
| `order_item_id_list` | 字符串数组 | 是 | 同订单下的非空、去重商品行 ID 列表。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data` | 对象 | 取消校验信息。取实际返回的可取消范围与原因，作为取消请求的输入。 |

核对返回的可取消范围和原因后，向用户确认再提交取消。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询逆向单列表（listReverseOrders）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /reverse/getreverseordersforseller`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listReverseOrders`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `page_size` | 整数 | 是 | 页容量。 |
| `page_no` | 整数 | 是 | 页码。 |
| `request_type_list` | 字符串数组 | 否 | 逆向申请类型，例如 `["ONLY_REFUND"]`。 |
| `ofc_status_list` | 字符串数组 | 否 | 履约状态，例如 `["RETURN_CANCELED"]`。 |
| `reverse_order_id` | 正整数或数字字符串 | 否 | 逆向订单 ID。 |
| `trade_order_id` | 正整数或数字字符串 | 否 | 原交易订单 ID。 |
| `reverse_status_list` | 字符串数组 | 否 | 逆向状态，例如 `["REQUEST_INITIATE"]`。 |
| `return_to_type` | 字符串 | 否 | `RTM` 退回卖家，`RTW` 退回 Lazada 仓库。 |
| `dispute_in_progress` | 布尔值 | 否 | 是否有进行中的争议。 |
| `TradeOrderLineCreatedTimeRangeStart`、`TradeOrderLineCreatedTimeRangeEnd` | 整数 | 否 | 交易订单行创建时间范围，Unix 毫秒。 |
| `ReverseOrderLineTimeRangeStart`、`ReverseOrderLineTimeRangeEnd` | 整数 | 否 | 逆向商品行时间范围，Unix 毫秒。 |
| `ReverseOrderLineModifiedTimeRangeStart`、`ReverseOrderLineModifiedTimeRangeEnd` | 整数 | 否 | 逆向商品行修改时间范围，Unix 毫秒。 |
| `QC_Decision` | 字符串 | 否 | `scrap`、`return_to_merchant`、`return_to_merchant_cb`、`return_to_customer`、`return_to_warehouse` 或 `not_returned`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或布尔字符串 | 查询结果。 |
| `data.result.page_no`、`page_size`、`total` | 整数或数字字符串 | 当前页码、页容量、总记录数。 |
| `data.result.items` | 对象数组 | 逆向单列表，可为空。 |
| `data.result.items[].reverse_order_id`、`trade_order_id` | 字符串 | 逆向单和原订单 ID。 |
| `data.result.items[].request_type`、`shipping_type` | 字符串 | 申请类型、退货运输方式。 |
| `data.result.items[].is_rtm` | 布尔值或布尔字符串 | 是否退回卖家。 |
| `data.result.items[].reverse_order_lines` | 对象数组 | 逆向商品行。 |
| `reverse_order_lines[].reverse_order_line_id`、`trade_order_line_id` | 字符串 | 逆向商品行和原商品行 ID。 |
| `reverse_order_lines[].reverse_status`、`ofc_status`、`whqc_decision` | 字符串 | 逆向状态、履约状态和仓库质检决定。 |
| `reverse_order_lines[].product.product_id`、`product.product_sku`、`seller_sku_id`、`platform_sku_id` | 字符串 | 商品及 SKU 标识。 |
| `reverse_order_lines[].reason_code`、`reason_text` | 整数或数字字符串、字符串 | 原因代码和说明。 |
| `reverse_order_lines[].refund_amount`、`item_unit_price` | 数值或数字字符串 | 退款额和商品单价，按当地货币的百分之一计，越南站按越南盾计。 |
| `reverse_order_lines[].trade_order_gmt_create`、`return_order_line_gmt_create`、`return_order_line_gmt_modified`、`sla` | 整数或数字字符串 | 交易创建时间、逆向行创建和修改时间、卖家操作时限。 |
| `reverse_order_lines[].is_dispute`、`is_need_refund` | 布尔值或布尔字符串、字符串 | 是否有争议、是否需退款。 |
| `reverse_order_lines[].refund_payment_method`、`tracking_number` | 字符串 | 退款支付方式和退货运单号。 |

筛选状态使用当前站点的 Lazada 枚举值。 [Lazada 逆向单接口](https://open.lazada.com/apps/doc/api?path=%2Freverse%2Fgetreverseordersforseller)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询逆向单详情（getReverseOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/return/detail/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getReverseOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reverse_order_id` | 正整数或数字字符串 | 是 | 当前店铺的真实逆向单 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.reverse_order_id`、`trade_order_id` | 字符串 | 逆向单和原订单 ID。 |
| `data.request_type`、`shipping_type` | 字符串 | 申请类型，例如 `CANCEL`、`RETURN`、`ONLY_REFUND`。运输方式例如 `PICK_UP`、`DROP_OFF`。 |
| `data.is_rtm` | 布尔值或布尔字符串 | 是否退回卖家。 |
| `data.reverseOrderLineDTOList` | 对象数组 | 逆向商品行。 |
| `reverseOrderLineDTOList[].reverse_order_line_id`、`trade_order_line_id` | 字符串 | 逆向商品行和原商品行 ID。 |
| `reverseOrderLineDTOList[].reverse_status`、`ofc_status`、`whqc_decision` | 字符串 | 逆向状态、履约状态和仓库质检决定。 |
| `reverseOrderLineDTOList[].productDTO.product_id`、`productDTO.sku`、`seller_sku_id`、`platform_sku_id` | 字符串 | 商品及 SKU 标识。 |
| `reverseOrderLineDTOList[].reason_code`、`reason_text` | 整数或数字字符串、字符串 | 原因代码和说明。 |
| `reverseOrderLineDTOList[].refund_amount`、`item_unit_price` | 数值或数字字符串 | 退款额和商品单价。单位同逆向单列表。 |
| `reverseOrderLineDTOList[].trade_order_gmt_create`、`return_order_line_gmt_create`、`return_order_line_gmt_modified`、`sla` | 整数或数字字符串 | 交易创建时间、逆向行创建和修改时间、卖家操作时限。 |
| `reverseOrderLineDTOList[].is_dispute`、`is_need_refund` | 布尔值或布尔字符串 | 是否有争议、是否需退款。 |
| `reverseOrderLineDTOList[].refund_payment_method`、`tracking_number` | 字符串 | 退款支付方式和退货运单号。 |

[Lazada 逆向单详情接口](https://open.lazada.com/apps/doc/api?path=%2Forder%2Freverse%2Freturn%2Fdetail%2Flist)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询售后原因（listReverseOrderReasons）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/reason/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listReverseOrderReasons`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reverse_order_line_id` | 正整数或数字字符串 | 是 | 真实逆向商品行 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 该逆向商品行的可用售后原因。 |
| `data[].reason_id` | 字符串 | 提交时使用对应原因 ID。 |
| `data[].muti_language_text`、`text` | 字符串 | 本地化原因与英文原因。 |

[Lazada 售后原因接口](https://open.lazada.com/apps/doc/api?path=%2Forder%2Freverse%2Freason%2Flist)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：查询售后历史（listReverseOrderHistory）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/return/history/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listReverseOrderHistory`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reverse_order_line_id` | 正整数或数字字符串 | 是 | 真实逆向商品行 ID。 |
| `page_size` | 整数 | 否 | 页容量，上游默认 10。 |
| `page_number` | 整数 | 否 | 页码，上游默认 1。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.list` | 对象数组 | 售后历史记录，后端排除操作人及证据图片。 |
| `data.list[].time` | 整数或数字字符串 | 历史记录时间，Unix 毫秒。 |
| `data.page_info.page_size`、`current_page_number`、`total` | 整数或数字字符串 | 页容量、当前页码、总记录数。 |

[Lazada 售后历史接口](https://open.lazada.com/apps/doc/api?path=%2Forder%2Freverse%2Freturn%2Fhistory%2Flist)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：打包（packOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/fulfill/pack`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=packOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `packReq` | 对象 | 是 | 待打包的订单与商品行。 |
| `packReq.pack_order_list` | 对象数组 | 是 | 1–20 个订单条目。 |
| `packReq.pack_order_list[].order_id` | 正整数 | 是 | 同店铺订单 ID。 |
| `packReq.pack_order_list[].order_item_list` | 正整数数组 | 是 | 非空正整数数组，使用实际 ID，保留精度，同一订单下的商品行不得重复。 |
| `packReq.delivery_type` | 字符串 | 是 | 当前流程使用 dropship。 |
| `packReq.shipping_allocate_type` | 字符串 | 是 | TFS 或 NTFS。 |
| `packReq.shipment_provider_code` | 字符串 | 按物流规则 | 物流服务商编码。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.pack_order_list` | 对象数组 | 按订单列出商品行结果。 |
| `data.result.data.pack_order_list[].order_id` | 字符串 | 返回的订单 ID。 |
| `data.result.data.pack_order_list[].order_item_list` | 对象数组 | 当前订单下的商品行结果。 |
| `data.result.data.pack_order_list[].order_item_list[].order_item_id` | 字符串 | 对应商品行。 |
| `data.result.data.pack_order_list[].order_item_list[].item_err_code` | 整数或字符串 | 0 表示该行成功，其他值表示该项失败。 |

核对各商品行结果，并从实际返回记录中提取包裹 ID。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：重新打包（repackOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/package/repack`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=repackOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `rePackReq` | 对象 | 是 | 包裹批次请求。 |
| `rePackReq.packages` | 对象数组 | 是 | 1–20 个不同包裹。 |
| `rePackReq.packages[].package_id` | 字符串 | 是 | 同一店铺的真实包裹 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.packages` | 对象数组 | 按提交的包裹逐项返回。 |
| `data.result.data.packages[].package_id` | 字符串 | 对应请求包裹。 |
| `data.result.data.packages[].item_err_code` | 整数或字符串 | 0 表示该包裹成功，其他值表示该项失败。 |

核对每个包裹的结果及返回的新包裹 ID。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：标记待揽收（readyToShip）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/package/rts`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=readyToShip`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `readyToShipReq` | 对象 | 是 | 包裹批次请求。 |
| `readyToShipReq.packages` | 对象数组 | 是 | 1–20 个不同包裹。 |
| `readyToShipReq.packages[].package_id` | 字符串 | 是 | 同一店铺的真实包裹 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.packages` | 对象数组 | 按提交的包裹逐项返回。 |
| `data.result.data.packages[].package_id` | 字符串 | 对应请求包裹。 |
| `data.result.data.packages[].item_err_code` | 整数或字符串 | 0 表示该包裹成功，其他值表示该项失败。 |

标记前核对实际打包状态和目标包裹。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：取消订单行（cancelOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/cancel/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=cancelOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `order_id` | 正整数或数字字符串 | 是 | 1–20 位正整数或对应数字字符串，首位不能为 0。 |
| `order_item_id_list` | 字符串数组 | 是 | 同订单下的非空、去重商品行 ID 列表。 |
| `reason_id` | 字符串 | 是 | 可取消校验返回的有效原因。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data.tip_type` | 字符串 | success 确认成功，error 拒绝。警告或缺少确认时为 UNKNOWN。 |
| `status` | 字符串 | LinkFox 写入状态。 |

该上游 GET 会修改订单状态，且可能影响店铺指标。先确认取消范围和原因。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：确认商家配送送达（confirmDbsDelivery）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/package/sof/delivered`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=confirmDbsDelivery`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `dbsDeliveryReq` | 对象 | 是 | 包裹批次请求。 |
| `dbsDeliveryReq.packages` | 对象数组 | 是 | 1–20 个不同包裹。 |
| `dbsDeliveryReq.packages[].package_id` | 字符串 | 是 | 同一店铺的真实包裹 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.packages` | 对象数组 | 按提交的包裹逐项返回。 |
| `data.result.data.packages[].package_id` | 字符串 | 对应请求包裹。 |
| `data.result.data.packages[].item_err_code` | 整数或字符串 | 0 表示该包裹成功，其他值表示该项失败。 |

按已核实的商家配送送达范围提交。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：标记商家配送失败（markDbsDeliveryFailed）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/package/sof/failed_delivery`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=markDbsDeliveryFailed`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `dbsFailedDeliveryReq` | 对象 | 是 | 包裹批次请求。 |
| `dbsFailedDeliveryReq.packages` | 对象数组 | 是 | 1–20 个不同包裹。 |
| `dbsFailedDeliveryReq.packages[].package_id` | 字符串 | 是 | 同一店铺的真实包裹 ID。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.packages` | 对象数组 | 按提交的包裹逐项返回。 |
| `data.result.data.packages[].package_id` | 字符串 | 对应请求包裹。 |
| `data.result.data.packages[].item_err_code` | 整数或字符串 | 0 表示该包裹成功，其他值表示该项失败。 |

按已核实的商家配送失败范围提交。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：标记数字订单交付（deliverDigitalOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`POST /order/digital/delivered`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=deliverDigitalOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `digitalDeliveryReq` | 对象 | 是 | 数字订单交付请求。 |
| `digitalDeliveryReq.orders` | 对象数组 | 是 | 1–20 个订单条目。 |
| `digitalDeliveryReq.orders[].order_id` | 正整数 | 是 | 实际订单 ID。 |
| `digitalDeliveryReq.orders[].order_item_list` | 正整数数组 | 是 | 非空正整数数组，使用实际 ID，保留精度，同一订单下的商品行不得重复。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.success` | 布尔值或字符串 | 上游批次处理标志。 |
| `data.result.data.orders` | 对象数组 | 按订单列出商品行结果。 |
| `data.result.data.orders[].order_id` | 字符串 | 返回的订单 ID。 |
| `data.result.data.orders[].order_item_list` | 对象数组 | 当前订单下的商品行结果。 |
| `data.result.data.orders[].order_item_list[].order_item_id` | 字符串 | 对应商品行。 |
| `data.result.data.orders[].order_item_list[].item_err_code` | 整数或字符串 | 0 表示该行成功，其他值表示该项失败。 |

仅处理符合数字交付条件的商品行。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：处理买家取消申请（decideOrderCancellation）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/cancel/seller/decide`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=decideOrderCancellation`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reverse_order_id` | 正整数或数字字符串 | 是 | 1–20 位正整数或对应数字字符串，首位不能为 0。 |
| `agree_cancel` | 布尔值 | 是 | true 同意取消，false 拒绝。 |
| `reason_code` | 整数 | 否 | 按所选处理结果和平台要求传入原因代码。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data` | 对象、null 或缺失 | 平台可在确认后返回空结果。 |
| 上游 `data.reverse_order_id` | 字符串 | 可选回传的逆向单 ID。与请求 ID 不一致时状态为 UNKNOWN。 |
| `status` | 字符串 | 读取 LinkFox 写入状态，按原逆向单核对实际处理结果。 |

先读取并确认买家取消申请、适用原因及涉及的订单行。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：处理逆向单（updateReverseOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/return/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateReverseOrder`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | 字符串 | 是 | instantRefund、agreeReturn、refuseReturn、agreeRefund、refuseRefund 或 confirmDelivery。 |
| `reverse_order_id` | 正整数或数字字符串 | 是 | 1–20 位正整数或对应数字字符串，首位不能为 0。 |
| `reverse_order_item_ids` | 正整数数组 | 是 | 同一逆向单的非空、去重商品行列表。refuseReturn、refuseRefund 只允许一个商品行。 |
| `reason_id` | 正整数或数字字符串 | 拒绝退货或退款时 | 使用平台返回的原因 ID。其他动作允许按上游规则填写。 |
| `comment` | 字符串 | 拒绝退货或退款时 | 用户确认的非空处理说明。 |
| `image_info` | 对象数组 | refuseRefund 时 | 拒绝退款至少一项图片证据，条目可含 name、url 字符串；其他动作按需提供。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data` | 对象、null 或缺失 | 平台可在确认后返回空结果。 |
| 上游 `data.reverse_order_id` | 字符串 | 可选回传的逆向单 ID。与请求 ID 不一致时状态为 UNKNOWN。 |
| `status` | 字符串 | 读取 LinkFox 写入状态，按原逆向单核对实际处理结果。 |

提交前确认逆向商品行、动作、原因和证据。条件必填及单行限制见 [Lazada 逆向单处理接口的错误码 108–111](https://open.lazada.com/apps/doc/api?path=%2Forder%2Freverse%2Freturn%2Fupdate)。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：处理仅退款申请（decideOnlyRefund）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/orders`。
- **上游方法与路径**：`GET /order/reverse/onlyrefund/seller/decide`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=decideOnlyRefund`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | 字符串 | 是 | agreeRefund 或 startDispute。 |
| `reverse_order_id` | 正整数或数字字符串 | 是 | 1–20 位正整数或对应数字字符串，首位不能为 0。 |
| `reverse_order_item_ids` | 正整数数组 | 是 | 只含一个实际逆向商品行 ID。 |
| `comment` | 字符串 | startDispute 时 | 用户确认的争议说明。 |
| `image_info_list` | 对象数组 | startDispute 时 | 发起争议至少一项，每项提供 file_name 和 file_url 字符串。 |
| `video_info_list` | 对象数组 | 否 | 视频证据，每项按需传 cover_url、video_url 字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 结果字段 | 类型 | 说明 |
| --- | --- | --- |
| 上游 `data` | 对象、null 或缺失 | 平台可在确认后返回空结果。 |
| 上游 `data.reverse_order_id` | 字符串 | 可选回传的逆向单 ID。与请求 ID 不一致时状态为 UNKNOWN。 |
| `status` | 字符串 | 读取 LinkFox 写入状态，按原逆向单核对实际处理结果。 |

提交前确认退款或争议目标和实际证据。

批次履约按请求中的商品行或包裹逐项核对返回的错误码。响应缺少目标、重复目标或包含未请求目标时，返回 `UNKNOWN`。读取运单时保留脱敏诊断与本地结果路径。 [Lazada 履约 API](https://open.lazada.com/apps/doc/doc?docId=120984&nodeId=30764) [订单取消](https://open.lazada.com/apps/doc/doc?docId=121329&nodeId=43454)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。


## 接口：查询写入状态（operationStatus）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/operationStatus`。读取 LinkFox 已有写记录，不重新调用上游写接口。

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 原写入的店铺连接，最长 36 字符。 |
| `requestId` | UUID 字符串 | 是 | 原写入 UUID，最长 36 字符。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | null | 查询已存写记录不重取业务结果。 |
| `requestId` | 字符串或 null | 已存上游请求标识。 |
| `clientRequestId` | 字符串 | 原写入 UUID。 |
| `status` | 字符串 | `PENDING`、`SUCCEEDED`、`REJECTED`、`PARTIAL` 或 `UNKNOWN`。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 查询成功不等于写入成功。按 [写入与续查](api.md#写入与续查) 处理原状态；记录不存在时核对原用户、连接及 UUID，不换 UUID 自动重放。
