# 订单详情查询 V2 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：订单详情查询 V2（bg.order.detail.v2.get）

| 项 | 值 |
|----| ----- |
| **脚本** | `scripts/eu_order_detail_v2_get.py` |
| **Partner 文档** | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9（按 `type` 在 Partner EU 后台打开） |
| **网关** | `POST /temu/proxy`，`type`=`bg.order.detail.v2.get`，业务载荷放在 Body 的 `params` |

用于订单详情查询 V2。

> **网关鉴权字段**由本技能网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。

---

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| site | string | 是 | EU 封装默认 `eu`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，须为小写。 |
| managementType | string | 是 | EU 封装默认 `semi-managed`；通用脚本允许 `full-managed`、`semi-managed`，须为小写。 |
| accessToken | string | 是 | Temu 店铺令牌；使用脚本的 `storeKey` 时在本地读取后写入此字段。 |
| type | string | 是 | 固定为 `bg.order.detail.v2.get`；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
| params | object | 否 | Temu 业务参数，本接口的业务块为 `params.request`。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序取首个非空值，优先于环境变量；不转发到 Temu。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；以 site、managementType、tokenPurpose 精确读取，accessToken 非空时优先。 |
| tokenPurpose | string | 否 | EU 封装在仅用 storeKey 且未显式指定时默认 `order-shipping`；通用脚本默认 `default`。不转发到 Temu。 |
| params | object | 否 | EU 封装优先使用该对象，否则将剔除保留控制字段后的顶层业务字段整体放入网关 params；`request` 的层级保持不变。 |
| --inline | CLI flag | 否 | 强制完整打印，并保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存，调用公共 run 时始终加入该选项，不读写响应缓存；公共调用器可能创建空缓存目录。 |

网关地址按 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 正式地址选择。保留 `Authorization` 与 `Token` 同值双请求头及会话头。HTTP 默认超时 150 秒，不自动重试。完整响应只保存在当前工作目录的 linkfox 会话目录；不可写则请求前报错，禁止回退到家目录或临时目录。同秒多次结果使用微秒文件名避免覆盖。

本地令牌保存在 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；提供保存、读取、列举与授权指引 CLI，详见 [授权说明](../access-token.md)。本地令牌存储不属于接口响应缓存。


#### 业务对象

| 参数 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| params.request | OBJECT | 否 | 官方业务请求对象；嵌套字段的必填性见下表。 |

#### `params.request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------| ------ |
| parentOrderSn | STRING | **是** | 父订单号 |
| fulfillmentTypeList | STRING[] | 否 | 订单履约类型，见下表 |

#### `fulfillmentTypeList[]`

| 值 | 说明 |
|----| ------ |
| `fulfillBySeller` | 卖家履约 |
| `fulfillByCooperativeWarehouse` | 合作仓履约 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---| --- |
| errcode | integer / string / null | 公共响应业务状态；是否正常按基础规则判断。 |
| errmsg | string | 公共响应消息，错误时依据实际内容解释。 |
| body | string | Temu 原始 JSON 字符串，完整保留；可解析时脚本增加 temuBody。 |
| code | integer | 网关错误码；`1002` 表示参数或 LinkFox Token 无效，`1003` 表示转发失败，不覆盖公共 errcode 规则。 |
| temuBody | object / array / scalar / null | 脚本对非空合法 JSON body 解析后的值；解析失败不添加该字段。 |
| transportHttpStatus | integer / null | 脚本保留的外层 LinkFox HTTP 状态码；连接失败为 null。 |

下面字段属于 `body` 解析后的 Temu 响应，不属于外层网关对象。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------| ------ |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| parentOrderMap | OBJECT | 父订单信息 |
| orderList | OBJECT[] | 子订单信息（子订单列表） |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| parentOrderSn | STRING | 父订单号 |
| parentOrderStatus | INTEGER | 父订单状态：`1` PENDING；`2` UN_SHIPPING；`3` CANCELED；`4` SHIPPED；`41` PARTIALLY_SHIPPED；`5` DELIVERED；`51` PARTIALLY_DELIVERED |
| parentOrderTime | INTEGER | 父订单下单时间（下单时间，秒） |
| expectShipLatestTime | INTEGER | 最晚发货时间（最晚发货时间，秒） |
| parentOrderPendingFinishTime | INTEGER | 父订单待处理完成时间（待处理完成时间，秒） |
| latestDeliveryTime | INTEGER | 最晚送达时间（最晚送达时间，秒） |
| parentShippingTime | INTEGER | 父订单发货时间（父订单发货时间，秒） |
| siteId | LONG | 站点编号 |
| regionId | LONG | 区域编号，例如美国 - **211** |
| parentOrderLabel | OBJECT[] | 父订单状态标签列表（父订单状态标签） |
| fulfillmentWarning | STRING[] | 履约提示，见下表 |
| hasShippingFee | BOOLEAN | 用户实付运费是否为零：`true` 为零，`false` 非零（**仅本土店铺**） |
| regionName1 | STRING | 地址区域 1 |
| regionName2 | STRING | 地址区域 2 |
| regionName3 | STRING | 地址区域 3 |
| orderPaymentType | STRING | 订单支付类型：`COD`、`PPD` |
| batchOrderNumberList | STRING[] | 批次单号列表；**仅合作仓履约**有值，否则为空 |
| shippingMethod | INTEGER | 配送渠道类型：`1` 标准配送，`2` 门店配送，`3` 买家自提 |
| isShipmentConsolidatedByMainMall | BOOLEAN | 为 `true` 表示 PO 已由主站合并发货，需在主站侧确认发货/面单 |
| parentConfirmTime | INTEGER | 父订单确认时间，秒级时间戳 |

#### `parentOrderMap.parentOrderLabel[]` — `name` 常见值

| name | 说明 |
|------| ------ |
| `soon_to_be_overdue` | 即将逾期 |
| `past_due` | 已逾期 |
| `pending_buyer_cancellation` | 买家取消待处理 |
| `pending_buyer_address_change` | 买家改地址待处理 |
| `pending_risk_control_alert` | 风控预警待处理 |
| `signature_required_on_delivery` | 需要签收 |

| 参数 | 类型 | 说明 |
|------|------| ------ |
| name | STRING | 标签名 |
| value | INTEGER | 是否有标签：`0` = 无标签，`1` = 有标签 |

#### `parentOrderMap.fulfillmentWarning[]`

| 值 | 说明 |
|----| ------ |
| `SUGGEST_SIGNATURE_ON_DELIVERY` | 建议为该订单购买签收服务以确保履约 |
| `CONFIRMED_CHANGED_ADDRESS` | 地址已变更并确认，重新拉单获取最新地址 |
| `RESTRICT_FEDEX_SELF_SHIPPING` | 限制用 FedEx 运单号确认发货 |
| `RESTRICT_USPS_SELF_SHIPPING` | 限制用 USPS 运单号确认发货 |
| `RESTRICT_SELF_SHIPPING` | 限制用运单号确认发货 |
| `BLOCK_LOGISTICS_PROVIDERS_{Name1,Name2,...}` | 买家屏蔽部分物流商，名称见响应 |
| `REQUIRES_CUSTOMER_PICKUP` | 仅支持买家自提履约 |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| orderSn | STRING | 子订单号 |
| quantity | INTEGER | 卖家需履约数量：`quantity = originalOrderQuantity - canceledQuantityBeforeShipment` |
| canceledQuantityBeforeShipment | INTEGER | 发货前取消数量 |
| originalOrderQuantity | INTEGER | 原始下单数量 |
| goodsId | LONG | 商品编号 |
| packageSnInfo | OBJECT[] | 包裹信息 |
| packageAbnormalTypeList | STRING[] | 发货后物流异常，见下表 |
| skuId | LONG | SKU 编号；**仅适用于 LOCAL 卖家，不适用于 SEMI 卖家** |
| spec | STRING | 买家可见商品规格 |
| originalSpecName | STRING | 卖家侧商品规格；**仅适用于确认时间在最近六个月内的订单** |
| thumbUrl | STRING | 缩略图 URL |
| goodsName | STRING | 买家可见商品名 |
| originalGoodsName | STRING | 卖家侧商品名；**仅适用于确认时间在最近六个月内的订单** |
| orderStatus | INTEGER | 子订单状态：`1` PENDING；`2` UN_SHIPPING；`3` CANCELED；`4` SHIPPED；`41` PARTIALLY_SHIPPED；`5` DELIVERED；`51` PARTIALLY_DELIVERED |
| productList | OBJECT[] | 商品信息；**仅 SEMI 卖家有效，非 LOCAL** |
| orderLabel | OBJECT[] | 子订单标签 |
| fulfillmentWarning | STRING[] | 履约提示（子订单履约提示），见下表 |
| fulfillmentType | STRING | `fulfillBySeller`（卖家履约） / `fulfillByCooperativeWarehouse`（合作仓履约） |
| inventoryDeductionWarehouseId | STRING | 库存扣减仓库编号 |
| inventoryDeductionWarehouseName | STRING | 库存扣减仓库名称 |
| orderPaymentType | STRING | 订单支付类型：`COD`、`PPD` |
| isCancelledDuringPending | BOOLEAN | 是否在待处理期间全部取消 |
| earliestTimeBuyShippingLabel | INTEGER | 仅可在该时间之后购买面单 |
| earliestTimeGetShippingDocument | INTEGER | 仅可在该时间之后获取发货文件 |
| orderShippingTime | INTEGER | 子订单发货时间；若含未发货或延迟包裹，返回 **null** |
| isShipmentConsolidatedByMainMall | BOOLEAN | 主站合并发货标记 |
| orderCreateTime | INTEGER | 子订单创建时间 |
| qualificationUploadEndTime | LONG | 订单资质文件上传截止时间 |
| hasUploadedEvidence | BOOLEAN | 商家是否已上传 SN、IMEI、鉴定报告等核验信息 |

#### `packageSnInfo[]`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| packageSn | STRING | 该订单包裹号 |
| packageDeliveryType | INTEGER | 包裹配送类型：`1` 卖家非集成物流；`2` 卖家 Temu 集成物流；`3` 合作仓非集成物流；`4` 合作仓 Temu 集成物流 |
| callSuccess | BOOLEAN | 最近一次请求是否 `bg.logistics.shipment.create` 成功；与 Temu 非集成物流无关 |

#### `orderList[].packageAbnormalTypeList[]`

| 值 | 说明 |
|----| ------ |
| `WRONG_SHIPPING_ADDRESS` | 收货地址错误 |
| `SUSPECTED_ERROR_PROVIDER` | 疑似承运商异常 |
| `NO_TRACK` | 无轨迹 |
| `TRACK_TOO_EARLY` | 轨迹过早 |
| `OVERTIME_COLLECTION` | 揽收超时 |
| `TRACK_COLLECT_FAIL` | 揽收失败 |
| `SIGNED_BUT_UNRECEIVED_TASK` | 已签收但未收货任务 |

#### `productList[]`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| productId | LONG | 商品编号 |
| productSkuId | LONG | 商品 SKU 编号；**仅适用于 SEMI 卖家，不适用于 LOCAL 卖家** |
| soldFactor | LONG | 商品数量与件数换算因子 |
| extCode | STRING | 货号 |

#### `orderList[].orderLabel[]` — `name` 常见值

`customized_products`、`US_to_CA`、`is_US_to_CA_BBC`、`Y2_advance_sale`、`pre_sale_order`、`made_to_order`、`vacation_order`、`second_hand_collectible_order`、`second_hand_luxury_order`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| name | STRING | 标签名 |
| value | INTEGER | 是否有标签：`0` = 无标签，`1` = 有标签；BBC 订单需结合以下标识判断： `is_US_to_CA_BBC` |

#### `orderList[].fulfillmentWarning[]`

| 值 | 说明 |
|----| ------ |
| `SAVE_SN_INFORMATION_FOR_RETURN` | 建议保存该订单 SN 信息以鉴别退货真伪 |
| `REQUIRES_AUTHENTICATION_REPORT_SUBMISSION` | 须在 Temu 卖家中心提交鉴定报告；超时自动取消并可能处罚 |
| `REQUIRES_AGE_VERIFICATION` | 建议购买签收人年龄验证服务 |
| `SPECIFIC_LOGISTICS_REQUIRED` | 须使用指定物流履约 |
| `REQUIRES_CUSTOMER_PICKUP` | 仅支持买家自提履约 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先应用外层 HTTP / errcode 基础规则，再检查网关 `code`、解析 `body`，按 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 解释业务结果；不能仅因 JSON 可解析就认定业务成功。
- 网关 `code=1002`：核对参数及 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单及网络。Temu 业务失败时保留 `errorMsg` 和原始响应。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.detail.v2.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789",
      "fulfillmentTypeList": [
        "fulfillBySeller"
      ]
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
