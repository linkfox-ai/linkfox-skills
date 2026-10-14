# 1688采购流程 API 参考

## MCP 调用规范

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **响应字段来源**：`skills/linkfox-1688-procurement/references/api.md`。仅从该文件的“响应结构”核对和恢复响应字段。
- **调用结构**：`toolName` 使用下表的精确值，区分大小写且不带前导 `/`；原请求对象直接放进 `arguments`，不包裹 `body`、`params` 或 `data`。
- **自动授权**：WorkBuddy 自动注入 Linkfox 调用授权。禁止在 `arguments` 中加入 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **响应解析**：`proxy_call` 返回 text JSON 时只解析一次。先判断 MCP 连接、工具、schema 与 `isError`，再检查下游 `errcode`/`code`/`success` 和消息字段。
- **OAuth 前置**：除 `authorizeUrl`、`authorizedStores` 外，目标 operation 前先单独调用 `alibaba1688/authorizedStores`，仅当存在 `status=ACTIVE` 且 `expired=false` 的授权才继续。不得把浏览器跳转当作授权成功。
- **缓存与重放**：不做 24 小时缓存。高风险写操作不得缓存、自动重试或自动重放；同一任务内相同 `toolName + arguments` 不得重复调用。

```json
{
  "toolName": "alibaba1688/authorizedStores",
  "arguments": {}
}
```

## API 与 toolName

| 能力 | 原 Path | 精确 `toolName` | 风险 | OAuth 前置检查 | 确认规则 |
|---|---|---|---|---|---|
| 生成授权链接 | `/alibaba1688/authorizeUrl` | `alibaba1688/authorizeUrl` | 低 | 否 | - |
| 查询已授权账号 | `/alibaba1688/authorizedStores` | `alibaba1688/authorizedStores` | 低 | 否 | - |
| 查询收货地址 | `/alibaba1688/receiveAddressList` | `alibaba1688/receiveAddressList` | 低 | 是 | - |
| 查询 SKU | `/alibaba1688/sku` | `alibaba1688/sku` | 低 | 是 | - |
| 下单预览 | `/alibaba1688/orderPreview` | `alibaba1688/orderPreview` | 中 | 是 | - |
| 创建订单 | `/alibaba1688/createOrder` | `alibaba1688/createOrder` | 高 | 是 | 紧邻调用前单独确认 |
| 获取支付链接 | `/alibaba1688/paymentUrl` | `alibaba1688/paymentUrl` | 高 | 是 | 紧邻调用前单独确认 |
| 查询订单状态 | `/alibaba1688/orderStatus` | `alibaba1688/orderStatus` | 低 | 是 | - |
| 查询物流 | `/alibaba1688/logistics` | `alibaba1688/logistics` | 低 | 是 | - |
| 查询物流轨迹 | `/alibaba1688/logisticsTrace` | `alibaba1688/logisticsTrace` | 低 | 是 | - |
| 确认收货 | `/alibaba1688/confirmReceive` | `alibaba1688/confirmReceive` | 高 | 是 | 紧邻调用前单独确认 |
| 取消订单 | `/alibaba1688/cancelOrder` | `alibaba1688/cancelOrder` | 高 | 是 | 状态核验后单独确认 |
| 查询可开票金额 | `/alibaba1688/invoiceAmount` | `alibaba1688/invoiceAmount` | 低 | 是 | - |
| 申请开票 | `/alibaba1688/invoiceApply` | `alibaba1688/invoiceApply` | 高 | 是 | 金额核验后单独确认 |

`_alibaba1688_imageSearch` 由 `linkfox-1688-search-by-image` 独立承担，本 Skill 不包含图搜能力。不要把 `/alibaba1688/proxy/callback`、`/alibaba1688/authorizeCallback`、`/alibaba1688/oauth/callback` 暴露为 Skill 能力。

## 请求参数

以下对象直接作为 `proxy_call.arguments`：

| 能力 | 参数 | 必填 | 说明 |
|---|---|---:|---|
| `authorizeUrl` | `accountName` | 是 | 授权账号展示名，用于标识本次 1688 OAuth 授权。 |
| `authorizedStores` | - | 否 | 通常传 `{}`。返回当前 LinkFox 用户的 1688 授权状态，不是全库账号列表。 |
| `receiveAddressList` | - | 否 | 通常传 `{}`。返回当前用户可用收货地址。 |
| `sku` | `offerId` | 是 | 1688 商品 ID，必须用字符串，避免 JS 大数精度丢失。 |
| `orderPreview` | `addressId` 或 `addressParam` | 条件必填 | 二选一。优先使用 `receiveAddressList` 返回的 `addressId`；`addressParam` 至少含 `fullName`、`mobile`、`address`。 |
| `orderPreview` | `cargoParamList` | 是 | 货品列表，每项含 `offerId`、可选 `specId`、`quantity`；`quantity >= 1`。 |
| `orderPreview` | `flow` | 是 | 下单流程类型。当前主流程为普通采购，使用 `general`。仅当用户明确要求分销/精选货源分销时，才可透传 `fenxiao`/`boutiquefenxiao`；本 Skill 不提供分销专属校验或保障。 |
| `orderPreview` | `isvBizType` | 否 | 默认 `cross`；仅支持 `cross`、`cross_daigou`、`cross_distribution`。 |
| `createOrder` | `confirmCreateOrder` | 是 | 必须是 JSON boolean `true`。未传或 false 时不会调用 1688 下单。 |
| `createOrder` | 下单参数 | 是 | 与 `orderPreview` 保持一致，必须显式包含相同 `flow`；可额外传 `message`、`tradeType`、`shopPromotionId`、`useRedEnvelope`、`anonymousBuyer`、`outOrderId` 等。 |
| `createOrder` | `useRedEnvelope` | 否 | 是否使用红包，仅支持 `y`/`n`；默认 `n`。 |
| `paymentUrl` | `confirmGetPaymentUrl` | 是 | 必须是 JSON boolean `true`。只获取支付链接，不自动打开、不自动支付。 |
| `paymentUrl` | `orderIdList` | 是 | 1688 订单 ID 字符串数组。使用 `createOrder` 返回的 `orderId`。 |
| `orderStatus` | `aliOrderId` | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `logistics` | `aliOrderId` | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `logisticsTrace` | `aliOrderId` | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `logisticsTrace` | `logisticsId` | 否 | 物流订单 ID；多个物流单时建议从 `logistics` 返回中选择。 |
| `confirmReceive` | `aliOrderId` | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `confirmReceive` | `confirmReceive` | 是 | 必须是 JSON boolean `true`。确认收货不可逆，需用户单独中文确认。 |
| `cancelOrder` | `aliOrderId` | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `cancelOrder` | `confirmCancel` | 是 | 必须是 JSON boolean `true`。取消订单不可逆，需用户单独中文确认。 |
| `cancelOrder` | `cancelReason`、`remark` | 否 | 取消原因和备注，非空时透传。 |
| `invoiceAmount` | `orderIds` | 是 | 1688 订单 ID 字符串数组，至少 1 项，每项必须为数字字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `invoiceApply` | `confirmApplyInvoice` | 是 | 必须是 JSON boolean `true`。申请开票高风险且不可逆，需用户单独中文确认。 |
| `invoiceApply` | `invoiceApplyModelList` | 是 | 开票申请列表，至少 1 项，每项见下「开票申请逐单模型」。 |
| `invoiceApply` | 逐单 `amount` | 是 | 必须通过 `invoiceAmount` 查到的可开票金额**原样传入**，不得自行计算；单位为分（1元=100分）。 |
| `invoiceApply` | 逐单 `invoiceType` | 是 | `VATAX_COMM`（增值税普通发票）/ `VATAX_SPEC`（增值税专用发票）。 |
| `invoiceApply` | 逐单 `purchaserInvoiceTitleModel` | 是 | 买家发票抬头，见下「开票抬头」。企业抬头建议经 1688 `trade.invoiceTitle.getPageList` 查到既有抬头后原样传入，避免手填不一致。 |

### 开票相关对象

`invoiceApplyModelList` 每项结构：

```json
{
  "orderId": "3309156590237728779",
  "amount": 30500,
  "invoiceType": "VATAX_COMM",
  "purchaserInvoiceTitleModel": {
    "titleType": "COMPANY",
    "title": "深圳某某科技有限公司",
    "taxpayerIdentify": "91440300MA5XXXXXX"
  }
}
```

`purchaserInvoiceTitleModel`（开票抬头）：

| 字段 | 必填 | 说明 |
|---|---|---|
| `titleType` | 是 | `PERSONAL`（个人和社会组织）/ `COMPANY`（企业） |
| `title` | 是 | 发票抬头 |
| `taxpayerIdentify` | 条件必填 | 纳税人识别号，**企业开票必填** |
| `bankName` | 条件必填 | 开户行，**企业开专票必填** |
| `bankAccountId` | 条件必填 | 银行账号，**企业开专票必填** |
| `registerAddress` | 条件必填 | 企业注册地址，**企业开专票必填** |
| `registerPhone` | 条件必填 | 企业电话，**企业开专票必填** |

> 条件必填规则：`titleType=COMPANY`（不论普票/专票）须填 `taxpayerIdentify`；`titleType=COMPANY` 且 `invoiceType=VATAX_SPEC`（企业开专票）须再填 `bankName`/`bankAccountId`/`registerAddress`/`registerPhone` 四项；`titleType=PERSONAL` 以上条件字段可不填。违反返回错误码 `1002` 且不调用 1688。

### 常用对象

`cargoParamList` 示例：

```json
[
  {
    "offerId": "1234567890123456789",
    "specId": "456789012345678901",
    "quantity": 2
  }
]
```

`addressParam` 示例：

```json
{
  "fullName": "张三",
  "mobile": "13800000000",
  "provinceText": "广东省",
  "cityText": "深圳市",
  "areaText": "南山区",
  "address": "科技园示例路 1 号"
}
```

## 响应结构

来源未提供这些字段的类型、必填性或可空性，因此对应属性统一标为“来源未说明”，不根据字段名推断。

### `authorizeUrl`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `authorizeUrl` | 来源未说明 | 1688 授权链接；给用户手动打开，不自动打开，不返回 token。 |

### `authorizedStores`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `stores` | 来源未说明 | 来源未说明。 |
| `stores[].accountName` | 来源未说明 | 来源未说明。 |
| `stores[].status` | 来源未说明 | 授权状态；继续采购必须为 `ACTIVE`。 |
| `stores[].expired` | 来源未说明 | 授权是否失效；继续采购必须为 `false`。`true` 通常表示 refreshToken 为空、失效或刷新失败；accessToken 普通过期会由后端在调用授权或业务接口时自动刷新。即使响应包含 token 过期时间，也只作内部判断，不展示给用户。 |

### `receiveAddressList`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `items` | 来源未说明 | 来源未说明。 |
| `items[].addressId` | 来源未说明 | 来源未说明。 |
| `items[].fullName` | 来源未说明 | 来源未说明。 |
| `items[].mobile` | 来源未说明 | 来源未说明；展示时注意脱敏。 |
| `items[].provinceText` | 来源未说明 | 来源未说明。 |
| `items[].cityText` | 来源未说明 | 来源未说明。 |
| `items[].areaText` | 来源未说明 | 来源未说明。 |
| `items[].address` | 来源未说明 | 来源未说明；展示时注意脱敏。 |
| `items[].isDefault` | 来源未说明 | 来源未说明。 |

### `sku`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `offerId` | 来源未说明 | 来源未说明。 |
| `skuList` | 来源未说明 | 来源未说明。 |
| `skuList[].specId` | 来源未说明 | 规格 ID；多 SKU 商品下单时使用。 |
| `skuList[].skuId` | 来源未说明 | 来源未说明。 |
| `skuList[].price` | 来源未说明 | SKU 价格仅作规格选择参考；真实可购性、最终价格、运费和优惠以 `orderPreview` 为准。 |
| `skuList[].amountOnSale` | 来源未说明 | 库存仅作规格选择参考；真实可购性以 `orderPreview` 为准。 |
| `skuList[].attributes` | 来源未说明 | 来源未说明。 |
| `skuList[].skuImageUrl` | 来源未说明 | 来源未说明。 |

### `orderPreview`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | 来源未说明 | 来源明确业务失败时可仍为 `200`。 |
| `status` | 来源未说明 | 预览业务状态；`false` 时停止创建订单。 |
| `message` | 来源未说明 | 预览消息；失败时展示上游原文。 |
| `sumPayment` | 来源未说明 | 订单总额，单位为分。 |
| `sumCarriage` | 来源未说明 | 运费，单位为分。 |
| `discountFee` | 来源未说明 | 优惠金额，单位为分。 |
| `cargoList` | 来源未说明 | 来源未说明。 |
| `cargoList[].finalUnitPrice` | 来源未说明 | 最终单价，单位为元。 |
| `cargoList[].amount` | 来源未说明 | 商品金额，单位为元。 |
| `tradeModelList` | 来源未说明 | 为空可能表示预览业务失败。 |
| `payChannelInfos` | 来源未说明 | 支付渠道列表；只有编码时原样展示。 |
| `shopPromotionList` | 来源未说明 | 为空可能表示预览业务失败。 |

### `createOrder`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 创建是否成功。 |
| `orderId` | 来源未说明 | 1688 订单号；可用于后续支付、状态、物流、取消和确认收货。 |
| `message` | 来源未说明 | 结果消息。 |
| `code` | 来源未说明 | 结果码。 |

### `paymentUrl`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 来源未说明。 |
| `payUrl` | 来源未说明 | 支付链接；只展示给用户手动打开。 |
| `errorMessage` | 来源未说明 | 来源未说明。 |
| `errorCode` | 来源未说明 | 来源未说明。 |

### `orderStatus`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `aliOrderId` | 来源未说明 | 来源未说明。 |
| `aliStatus` | 来源未说明 | 用于判断订单当前履约阶段。 |
| `normalizedStatus` | 来源未说明 | 用于判断订单当前履约阶段。 |

### `logistics`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `aliOrderId` | 来源未说明 | 来源未说明。 |
| `logisticsOrders` | 来源未说明 | 来源未说明。 |
| `logisticsOrders[].logisticsId` | 来源未说明 | 物流订单 ID，可用于查询轨迹。 |
| `logisticsOrders[].logisticsBillNo` | 来源未说明 | 来源未说明。 |
| `logisticsOrders[].logisticsCompanyName` | 来源未说明 | 来源未说明。 |
| `logisticsOrders[].status` | 来源未说明 | 来源未说明。 |

### `logisticsTrace`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `aliOrderId` | 来源未说明 | 来源未说明。 |
| `logisticsId` | 来源未说明 | 来源未说明。 |
| `traceList` | 来源未说明 | 来源未说明。 |
| `traceList[].traceTime` | 来源未说明 | 轨迹时间；按 Asia/Shanghai 展示。 |
| `traceList[].location` | 来源未说明 | 来源未说明。 |
| `traceList[].traceDescription` | 来源未说明 | 来源未说明。 |
| `traceList[].traceStatus` | 来源未说明 | 来源未说明。 |

### `confirmReceive`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 确认收货是否成功。 |
| `aliOrderId` | 来源未说明 | 来源未说明。 |

### `cancelOrder`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 尝试取消是否成功，不代表退款或售后。 |
| `aliOrderId` | 来源未说明 | 来源未说明。 |
| `orderId` | 来源未说明 | 兼容出参；后续请求仍按接口要求使用 `aliOrderId` 或 `orderIdList`。 |
| `message` | 来源未说明 | 来源未说明。 |

### `invoiceAmount`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 查询整体业务结果；订单不存在、已取消或不可开票等情况下可为 `false`，但业务调用仍可能成功，须按 `retCodes` 与金额列表逐单判断。 |
| `code` | 来源未说明 | 来源未说明。 |
| `message` | 来源未说明 | 来源未说明。 |
| `subCode` | 来源未说明 | 来源未说明。 |
| `subMessage` | 来源未说明 | 来源未说明。 |
| `retCodes` | 来源未说明 | 逐单返回码列表，与金额列表逐项对应。 |
| `retCodes[]` | 来源未说明 | 来源未说明。 |
| `orderInvoiceAmountModelList` | 来源未说明 | 与 `retCodes` 逐项对应。 |
| `orderInvoiceAmountModelList[].orderId` | 来源未说明 | 来源未说明。 |
| `orderInvoiceAmountModelList[].amount` | 来源未说明 | 可开票金额，单位为分；须原样传给 `invoiceApply`。 |

### `invoiceApply`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | 来源未说明 | 顶层结果；批量逐单成败独立，不能代替对 `successList` / `failedList` 的逐项判断。业务失败时调用仍可能成功。 |
| `code` | 来源未说明 | `1003` 或 4xx/5xx 才视为传输异常。 |
| `message` | 来源未说明 | 来源未说明。 |
| `subCode` | 来源未说明 | 来源未说明。 |
| `subMessage` | 来源未说明 | 来源未说明。 |
| `successList` | 来源未说明 | 成功订单列表。 |
| `failedList` | 来源未说明 | 失败订单列表。 |
| `successList[].orderId` | 来源未说明 | 来源未说明。 |
| `successList[].outBizId` | 来源未说明 | 来源未说明。 |
| `successList[].result` | 来源未说明 | 来源未说明。 |
| `successList[].tradeOrderCompleted` | 来源未说明 | 来源未说明。 |
| `successList[].errorCode` | 来源未说明 | 来源未说明。 |
| `successList[].errorDesc` | 来源未说明 | 来源未说明。 |
| `failedList[].orderId` | 来源未说明 | 来源未说明。 |
| `failedList[].outBizId` | 来源未说明 | 来源未说明。 |
| `failedList[].result` | 来源未说明 | 来源未说明。 |
| `failedList[].tradeOrderCompleted` | 来源未说明 | 来源未说明。 |
| `failedList[].errorCode` | 来源未说明 | 逐单错误码；`INVOICE_ALREADY_APPLIED` 表示历史已开票。 |
| `failedList[].errorDesc` | 来源未说明 | 来源未说明。 |

## 高风险校验

用户侧只需要用中文自然语言做单独明确确认，例如“确认”“确认创建这个订单”“确认获取这个订单的支付链接”“确认取消这个订单”“确认收货”。只有当上一条消息已明确复述一个具体高风险动作和对象时，单独回复“确认”才算有效；不要要求用户输入英文参数名或 `=true`，也不要向普通用户展示内部确认字段、请求字段名或实现细节。

Agent 在收到中文确认后，才可在对应 `proxy_call.arguments` 中加入 JSON boolean 安全字段。字符串 `"true"`、数字 `1`、大小写变体都不算确认。这些字段只用于调用和排错，不属于用户可见流程文案。

| `toolName` | 阻止调用的条件 |
|---|---|
| `alibaba1688/createOrder` | 未取得本次订单的单独确认，或缺少 JSON boolean `confirmCreateOrder=true` |
| `alibaba1688/paymentUrl` | 未取得具体订单支付链接的单独确认，或缺少 JSON boolean `confirmGetPaymentUrl=true` |
| `alibaba1688/confirmReceive` | 未取得具体订单确认收货的单独确认，或缺少 JSON boolean `confirmReceive=true` |
| `alibaba1688/cancelOrder` | 未核验可取消状态、未取得单独确认，或缺少 JSON boolean `confirmCancel=true` |
| `alibaba1688/invoiceApply` | 未核验逐单金额和抬头、未取得单独确认，或缺少 JSON boolean `confirmApplyInvoice=true` |

创建订单时优先提供稳定且业务唯一的 `outOrderId`；调用结果不确定时先用订单状态能力核验，不得用相同业务意图再次创建订单。其他高风险操作同样不得因超时、MCP 错误或响应不明确而自动重放。

## 错误码

| errcode / error | 含义 | 处理建议 |
|---|---|---|
| 200 | 请求已有返回 | 是否可继续下单以具体预览结果、订单结果或提示信息为准 |
| 401 / authorized error | 认证失败 | 按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| 402 | 积分或余额不足 | 按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| `authorization_required` | 当前用户没有 ACTIVE 且未过期的 1688 授权 | 调用 `alibaba1688/authorizeUrl`，用户授权后再调用 `alibaba1688/authorizedStores` 验证 |
| `confirmation_required` | 高风险确认字段缺失或不是 JSON boolean `true` | 停止并让用户单独中文确认；不要自动补字符串 `"true"` |
| 1002 | 参数缺失或不合法 | 检查字段名、必填项、枚举值、订单号是否为数字字符串 |
| 1003 | 上游调用或业务失败 | 不要自动重试高风险写操作；向用户说明失败原因 |
| 1005 | 1688 授权缺失或失效 | 重新走授权检查/授权流程 |

错误响应示例：

```json
{
  "error": "authorization_required",
  "message": "1688 OAuth authorization is required before this procurement operation."
}
```

## MCP 示例

查询 SKU：

```json
{"toolName":"alibaba1688/sku","arguments":{"offerId":"1234567890123456789"}}
```

下单预览：

```json
{
  "toolName": "alibaba1688/orderPreview",
  "arguments": {
    "flow": "general",
    "addressId": "987654321012345678",
    "cargoParamList": [{"offerId":"1234567890123456789","specId":"456789012345678901","quantity":2}]
  }
}
```

申请开票属于高风险且不可逆操作。以下仅展示参数结构；只有完成金额核验并取得本次明确确认后才能调用：

```json
{
  "toolName": "alibaba1688/invoiceApply",
  "arguments": {
    "confirmApplyInvoice": true,
    "invoiceApplyModelList": [{
      "orderId": "1234567890123456789",
      "amount": 30500,
      "invoiceType": "VATAX_COMM",
      "purchaserInvoiceTitleModel": {
        "titleType": "COMPANY",
        "title": "深圳某某科技有限公司",
        "taxpayerIdentify": "91440300MA5XXXXXX"
      }
    }]
  }
}
```

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-1688-procurement",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`linkfox-1688-procurement`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise. Do not include API keys, tokens, full addresses, phone numbers, or payment URLs.
