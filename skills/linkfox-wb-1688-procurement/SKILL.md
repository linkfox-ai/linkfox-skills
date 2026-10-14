---
name: linkfox-wb-1688-procurement
display_name: LinkFox 1688采购履约
display_name_en: LinkFox 1688 Procurement Fulfillment
description: 面向已授权账号的 1688 采购履约能力，覆盖授权、商品规格、收货地址、订单预览与下单、支付、物流、收货、取消及开票。
description_zh: 当用户需要查询或发起已授权的 1688 采购、下单、支付链接、订单状态、物流、确认收货、取消订单或开发票时使用。能力通过 1688 OAuth 授权状态校验与实时 MCP 接口完成商品 SKU、收货地址、订单预览、订单履约和发票处理；高风险写操作必须逐项取得中文明确确认，完整参数与 MCP 契约见 references/。
description_en: Use for authorized 1688 procurement fulfillment through Linkfox MCP. OAuth status and authorization links, SKU and receiving-address lookup, order preview and creation, payment URL retrieval, order status and logistics tracking, receipt confirmation, cancellation, invoiceable-amount lookup, and invoice application. Authorization is checked before procurement calls; high-risk writes require separate explicit confirmation. Full parameters and MCP contracts are in references/.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox 1688采购履约（LinkFox 1688 Procurement Fulfillment）

为用户处理已授权 1688 账号的采购履约事项：先验证当前用户的授权可用性，再按需查询商品规格、收货地址、订单价格与履约状态，并在用户逐项确认后执行下单、获取支付链接、取消订单、确认收货或申请开票。能力覆盖 1 个业务子能力标识 `linkfox-1688-procurement` 和 14 个 1688 operation，均通过 `LinkFox.proxy_call` 调用。完整参数、响应、错误码与工作流见 `references/`。

## 能力边界

### ✅ 能力范围

- **授权与授权状态**：使用 `authorizeUrl` / `authorizedStores` 生成 1688 OAuth 授权链接、检查当前 LinkFox 用户的授权账号，并以 `status=ACTIVE` 且未过期作为后续采购调用条件。
- **商品规格与采购地址**：使用 `sku` 查询 `offerId` 的 SKU、规格、价格和库存参考信息，使用 `receiveAddressList` 查询当前用户可用收货地址。最终可购性、价格、运费和优惠以订单预览为准。
- **订单评估与创建**：使用 `orderPreview` 核对商品、规格、数量、收货地址、商品总价、运费、优惠和支付信息；用户单独明确确认后，使用 `createOrder` 创建 1688 订单。
- **支付与履约查询**：用户单独明确确认后，使用 `paymentUrl` 获取手动支付链接；按用户请求使用 `orderStatus`、`logistics`、`logisticsTrace` 查询订单状态、物流单摘要和物流轨迹。
- **收货与取消**：在具体对象和动作被单独确认后，使用 `confirmReceive` 确认收货，使用 `cancelOrder` 尝试取消订单。取消只表示尝试取消 1688 订单，不是退款或售后申请。
- **发票处理**：先使用 `invoiceAmount` 查询逐单可开票金额，再在用户明确确认发票类型、抬头和金额后使用 `invoiceApply` 申请开票。金额必须使用查询结果原值，单位为分。

### ❌ 边界与限制

- **WorkBuddy 自动授权**：不得向用户索取或展示 Linkfox 凭证、1688 access token、refresh token、callback code、app secret、JWT 或 Authorization Header；不得把任何认证字段放入 `arguments`。
- **必须有可用 1688 OAuth 授权**：除 `authorizeUrl` 和 `authorizedStores` 外，每次目标 operation 前先通过 MCP 调用 `authorizedStores`，只有当前用户存在 ACTIVE 且未过期授权才继续；无授权时停止目标调用，先完成 OAuth 后再复查。浏览器跳转结果不能替代 `authorizedStores` 返回结果。
- **只处理普通采购履约**：普通采购默认使用 `flow=general`；只有用户明确要求分销或精选货源分销时，才可透传 `fenxiao` 或 `boutiquefenxiao`。不提供分销专属校验或保障，也不要求用户选择内部采购类型。
- **高风险动作不可代办**：`createOrder`、`paymentUrl`、`confirmReceive`、`cancelOrder`、`invoiceApply` 必须在紧邻调用前取得针对具体对象的中文明确确认；不得因用户早先说过“继续”“可以”或“按上面来”而自动执行后续高风险动作。
- **不等同于退款售后**：已付款（含已付款待发货）订单不得用 `cancelOrder` 作为退款方案；已发货或已完成订单也不要调用取消，退款、退货和售后应由用户在 1688 订单页处理。本能力没有退款申请接口。
- **不自动跑完整闭环**：授权有效后，各查询、预览、下单、支付链接、状态、物流、收货和开票步骤可以按用户需求单独执行；失败、空结果、授权不足或参数问题时不得自动换参数、重试写操作、连续轮询或批量推进整个购买流程。
- **不在范围内的找货能力**：图片找货、关键词搜索、同款发现、供应商排名等商品发现任务不由本能力处理；应转到相应的 1688 搜索能力。也不处理 OAuth callback/proxy callback、手工修复 token 或直接提交 1688 token。
- **实时数据与计费**：本能力不做 24 小时响应缓存；授权、库存、价格、订单状态、物流和高风险写操作以实时返回为准。继续查询或重试前先向用户说明可能产生额外消耗，由用户决定。

## 工具选择指南

根据用户意图先选择最小必要 operation，再到【业务需求路由速查】定位 `toolName` 和 reference。涉及下单或发票时，先选择只读查询和预览，确认后才选择对应写操作。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 查询“我的 1688 授权店铺/账号” | `alibaba1688/authorizedStores` | 没有 ACTIVE 授权且用户要开始授权时，换用 `alibaba1688/authorizeUrl` |
| “生成 1688 授权链接” | `alibaba1688/authorizeUrl` | 用户完成浏览器授权后必须回到 `alibaba1688/authorizedStores` 验证，不直接假定成功 |
| “查这个 offerId 的 SKU/规格/库存” | `alibaba1688/sku` | 需要真实价格、运费、优惠或可购性时，换用 `alibaba1688/orderPreview`；不要把 SKU 价格当最终成交价 |
| “查我的 1688 收货地址” | `alibaba1688/receiveAddressList` | 多地址时让用户选择具体地址；下单预览可在没有地址 ID 时使用完整 `addressParam` |
| “帮我预览这个订单” | `alibaba1688/orderPreview` | 预览失败、金额为 0 或交易列表为空时停止，不换用 `createOrder` |
| “确认下单/创建订单” | `alibaba1688/createOrder` | 只有已展示预览摘要且刚取得该订单的中文确认时才调用；支付链接是另一项独立确认 |
| “获取支付链接” | `alibaba1688/paymentUrl` | 只有用户刚确认获取具体订单的支付链接时调用；只展示链接供用户手动打开，不自动支付 |
| “查订单状态/物流/物流轨迹” | 按需选择 `orderStatus`、`logistics`、`logisticsTrace` | 多物流单先用 `logistics` 取得 `logisticsId`，再查询指定轨迹；不主动轮询 |
| “取消订单” | 先 `orderStatus`，再按状态决定是否 `cancelOrder` | 已付款、已发货或已完成转为 1688 退款/售后；待付款订单仍需单独确认取消 |
| “确认收货” | `alibaba1688/confirmReceive` | 查询物流或已签收不等于确认收货；必须先明确确认具体订单 |
| “这个订单能开多少发票” | `alibaba1688/invoiceAmount` | 逐单不可开票时依据 `retCodes` 和列表跳过，不直接申请 |
| “给这个订单开发票/确认开票” | 先 `invoiceAmount`，再 `invoiceApply` | 只有用户确认发票类型、抬头与查询得到的金额后才申请；开票成功不可系统侧回滚 |

### 工具选择思路

- 先区分**只读查询**与**状态改变**：授权状态、SKU、地址、预览、订单状态、物流和可开票金额是只读或评估操作；创建订单、取支付链接、取消、收货和申请开票是独立高风险动作。
- 多个 operation 都能部分满足需求时，优先选择更贴近用户问题且出参更小的 operation：规格问题用 `sku`，最终成交核对用 `orderPreview`；物流摘要用 `logistics`，具体时间线用 `logisticsTrace`。
- 订单流程按实际需要推进，不把“查询授权”误当成所有步骤的强制链；但任何非授权 operation 前都必须通过 MCP 完成 ACTIVE 授权检查。
- 当用户表达含糊时，先展示已有只读结果并说明将要执行的具体业务动作，再让用户决定是否进入高风险步骤；不要让用户填写内部确认字段。

## 业务需求路由速查

按【工具选择指南】确定 operation 后，使用以下固定映射查精确 `toolName` 和归档 reference。表中每一行对应一个 1688 API/operation；14 项均属于 `linkfox-1688-procurement`。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-1688-procurement` | 生成授权链接（`authorizeUrl`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/authorizeUrl` | `alibaba1688/authorizeUrl` |
| `linkfox-1688-procurement` | 查询已授权账号（`authorizedStores`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/authorizedStores` | `alibaba1688/authorizedStores` |
| `linkfox-1688-procurement` | 查询收货地址（`receiveAddressList`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/receiveAddressList` | `alibaba1688/receiveAddressList` |
| `linkfox-1688-procurement` | 查询商品 SKU（`sku`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/sku` | `alibaba1688/sku` |
| `linkfox-1688-procurement` | 下单预览（`orderPreview`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/orderPreview` | `alibaba1688/orderPreview` |
| `linkfox-1688-procurement` | 创建订单（`createOrder`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/createOrder` | `alibaba1688/createOrder` |
| `linkfox-1688-procurement` | 获取支付链接（`paymentUrl`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/paymentUrl` | `alibaba1688/paymentUrl` |
| `linkfox-1688-procurement` | 查询订单状态（`orderStatus`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/orderStatus` | `alibaba1688/orderStatus` |
| `linkfox-1688-procurement` | 查询物流摘要（`logistics`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/logistics` | `alibaba1688/logistics` |
| `linkfox-1688-procurement` | 查询物流轨迹（`logisticsTrace`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/logisticsTrace` | `alibaba1688/logisticsTrace` |
| `linkfox-1688-procurement` | 确认收货（`confirmReceive`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/confirmReceive` | `alibaba1688/confirmReceive` |
| `linkfox-1688-procurement` | 取消订单（`cancelOrder`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/cancelOrder` | `alibaba1688/cancelOrder` |
| `linkfox-1688-procurement` | 查询可开票金额（`invoiceAmount`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/invoiceAmount` | `alibaba1688/invoiceAmount` |
| `linkfox-1688-procurement` | 申请开票（`invoiceApply`） | `references/linkfox-1688-procurement.md`；完整参数见 `references/api.md` | `/alibaba1688/invoiceApply` | `alibaba1688/invoiceApply` |

`references/api.md` 保存完整请求/响应对象、错误码、MCP 示例和 Feedback API；`references/workflow.md` 保存授权、预览、写操作、履约与开票的流程分支；`references/onboarding.md` 保存 MCP、认证和余额引导。本 skill 没有本地 helper。

## MCP 调用方式

- **MCP 契约**：只使用 `LinkFox.proxy_call`。`toolName` 必须是路由表中的精确值，区分大小写且不带前导 `/`；业务请求对象直接放入 `arguments`，不增加 `body`、`params`、`data` 或第二层 `arguments`。
- **自动授权**：WorkBuddy 自动注入 Linkfox 授权上下文，不传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **1688 OAuth 前置检查**：`authorizeUrl` 与 `authorizedStores` 不需要 ACTIVE 预检；其余 12 个 operation 先调用 `alibaba1688/authorizedStores`，只有存在 `status=ACTIVE` 且 `expired=false` 的授权才调用目标 endpoint。accessToken 普通过期由后端刷新；只有授权明确失效时才重新授权。
- **高风险调用**：在紧邻调用前用中文向用户复述具体订单、金额、状态和动作并取得单独明确确认，然后加入对应 JSON boolean：`createOrder` 使用 `confirmCreateOrder=true`，`paymentUrl` 使用 `confirmGetPaymentUrl=true`，`confirmReceive` 使用 `confirmReceive=true`，`cancelOrder` 使用 `confirmCancel=true`，`invoiceApply` 使用 `confirmApplyInvoice=true`。字符串 `"true"`、数字 `1` 或大小写变体均不算确认；不得向用户展示这些内部字段。
- **下单、幂等与发票顺序**：下单必须先完成 SKU、地址和预览；创建订单优先使用稳定、唯一的 `outOrderId`。响应不确定时先查询状态，不得自动重放。预览 `status=false`、金额为 0、关键列表为空或有失败信息时停止。开票必须先取得 `invoiceAmount` 的逐单金额并原样传递。
- **响应与错误**：text JSON 只解析一次。先处理 MCP 连接、工具、schema 与 `isError`，再处理下游 `errcode`/`code`/`success` 和消息字段；不要把 MCP 外层对象当业务响应。
- **本地能力变化**：旧脚本的响应脱敏、按大小自动落盘和 stdout 摘要不属于 MCP 能力，迁移后不再承诺。展示结果时仍须隐藏凭证、支付敏感信息和不必要的完整地址/电话。
- **失败纪律**：MCP 不可用时禁止回退旧 HTTP 网关或其他工具。相同 `toolName + arguments` 在同一任务内不重复调用；高风险调用失败、超时或结果不明确时绝不自动重试、重放或连续轮询。
- **反馈**：当实际行为与意图不符、结果错误或用户明确表达满意/不满时，按 `references/api.md` 的 Feedback API 规则提交反馈；Feedback URL 与 MCP 业务调用分离，内容不得含凭证、完整地址、电话号码或支付链接。

## 使用示例

以下示例展示业务 `arguments`。执行真实请求前读取对应 reference，确认 1688 OAuth 授权状态、用户确认和积分影响；示例中的 ID、金额和姓名均为占位值。

### 1. 授权状态与授权链接

查询当前 LinkFox 用户的授权状态：

```json
{"toolName":"alibaba1688/authorizedStores","arguments":{}}
```

若没有 ACTIVE 且未过期账号，生成授权链接（低风险，不自动打开浏览器）：

```json
{"accountName":"1688采购账号"}
```

使用 `toolName="alibaba1688/authorizeUrl"` 调用上面的业务参数。出参 `authorizeUrl` 只作为用户手动打开的链接；完成 OAuth 后必须再次调用 `alibaba1688/authorizedStores`，不能以浏览器跳转作为成功依据。该调用可能消耗积分，但不执行采购动作。

### 2. SKU 与收货地址

查询商品 SKU；`offerId` 必须是字符串：

```json
{"offerId":"1234567890123456789"}
```

使用 `toolName="alibaba1688/sku"`。重点读取 `skuList[].specId`、`skuId`、`price`、`amountOnSale`、`attributes` 和 `skuImageUrl`，但把价格和库存仅作为规格选择参考。

查询当前用户的收货地址：

```json
{}
```

使用 `toolName="alibaba1688/receiveAddressList"`，从 `items[]` 读取 `addressId`、收货人、手机号、省市区、详细地址和 `isDefault`，多地址时让用户明确选择。两项查询都需要已有 ACTIVE 1688 授权，且应按需执行，避免无必要重复计费。

### 3. 下单预览

用已选 SKU、数量和地址进行普通采购预览：

```json
{
  "flow":"general",
  "addressId":"987654321012345678",
  "cargoParamList":[
    {
      "offerId":"1234567890123456789",
      "specId":"456789012345678901",
      "quantity":2
    }
  ]
}
```

使用 `toolName="alibaba1688/orderPreview"`。展示 `cargoList` 商品、SKU/规格、数量、单价、商品总价、`sumCarriage` 运费、优惠、收货地址、订单总额和警告；注意 `sumPayment`/`sumCarriage`/`discountFee` 为分，而 `cargoList.finalUnitPrice`/`amount` 为元，不能混算。预览返回不等于下单许可，若业务状态失败或关键列表为空，停止后续写操作。调用通常消耗积分，不要为了试探而自动改数量或地址重试。

### 4. 创建订单与获取支付链接

用户已看到预览并单独确认“确认创建这个订单”后，才可在 MCP 调用中加入内部确认字段：

```json
{
  "confirmCreateOrder":true,
  "flow":"general",
  "addressId":"987654321012345678",
  "cargoParamList":[
    {"offerId":"1234567890123456789","specId":"456789012345678901","quantity":2}
  ],
  "useRedEnvelope":"n"
}
```

使用 `toolName="alibaba1688/createOrder"`。成功出参中的 `orderId` 是后续接口使用的 1688 订单号。创建成功不表示用户同意支付；若用户随后明确确认获取该订单的支付链接，再调用：

```json
{
  "confirmGetPaymentUrl":true,
  "orderIdList":["1234567890123456789"]
}
```

使用 `toolName="alibaba1688/paymentUrl"`，只展示 `payUrl` 供用户手动打开。两次调用均是高风险/计费操作，不得自动串联、自动支付、自动重放或把历史“继续”当作当前确认。

### 5. 订单状态与物流

查询订单状态：

```json
{"aliOrderId":"1234567890123456789"}
```

按需使用 `alibaba1688/orderStatus`、`alibaba1688/logistics` 或 `alibaba1688/logisticsTrace`。物流摘要可读取 `logisticsOrders[].logisticsId`、运单号、承运商和状态；指定某条轨迹时可追加 `logisticsId`：

```json
{"aliOrderId":"1234567890123456789","logisticsId":"LOGISTICS-ID-001"}
```

轨迹字段 `traceTime` 按 Asia/Shanghai 展示。不主动轮询；只有用户再次提出查询要求时才重新调用。查询是低风险，但同样可能产生积分消耗。

### 6. 取消订单与确认收货

取消前先检查订单状态。仅对允许取消的未付款/待付款订单进入确认流程，向用户说明“取消不等于退款”，取得该订单的单独中文确认后调用：

```json
{
  "confirmCancel":true,
  "aliOrderId":"1234567890123456789",
  "cancelReason":"不再需要",
  "remark":"用户确认取消"
}
```

使用 `toolName="alibaba1688/cancelOrder"`。已付款待发货、已发货或已完成订单转到 1688 退款/售后，不调用取消 endpoint。

用户明确确认具体订单收货后调用：

```json
{"confirmReceive":true,"aliOrderId":"1234567890123456789"}
```

使用 `toolName="alibaba1688/confirmReceive"`。物流已签收、用户查看状态或询问“怎么样”都不能替代确认。取消和收货均不可逆/高风险，不得自动重试。

### 7. 查询可开票金额与申请开票

先查询可开票金额：

```json
{"orderIds":["1234567890123456789"]}
```

使用 `toolName="alibaba1688/invoiceAmount"`。逐单读取 `orderInvoiceAmountModelList[].amount`，单位为分，必须原样传给申请接口；`success=false` 但业务调用成功时，依据 `retCodes` 和列表逐单判断，不可直接申请不可开票订单。

用户已明确确认具体订单、发票类型、抬头和金额后，申请增值税普通发票：

```json
{
  "confirmApplyInvoice":true,
  "invoiceApplyModelList":[
    {
      "orderId":"1234567890123456789",
      "amount":30500,
      "invoiceType":"VATAX_COMM",
      "purchaserInvoiceTitleModel":{
        "titleType":"COMPANY",
        "title":"深圳某某科技有限公司",
        "taxpayerIdentify":"91440300MA5XXXXXX"
      }
    }
  ]
}
```

使用 `toolName="alibaba1688/invoiceApply"`。个人抬头可用 `titleType=PERSONAL`；企业抬头必须有 `taxpayerIdentify`，企业专票 `VATAX_SPEC` 还必须有开户行、银行账号、注册地址和企业电话。申请结果要逐项遍历 `successList` 与 `failedList`；`INVOICE_ALREADY_APPLIED` 按已开票处理。开票成功不可系统侧回滚，红冲需联系商家。

## 展示规则

1. **先展示授权结论**：依赖 OAuth 的采购操作先说明当前授权可用、需重新授权或无法判断；只展示可用性，不展示 token 过期时间、刷新窗口或内部授权字段。
2. **客观呈现订单数据**：预览和履约结果按业务语言展示商品、规格、数量、金额、运费、地址、订单号、状态、物流和警告；不要把数据结果包装成超出接口依据的采购、退款或法律结论。
3. **标注数据来源与时间**：说明数据来自 1688 履约接口及具体业务 operation；物流轨迹时间按 Asia/Shanghai 展示，价格、库存、订单状态和物流以本次实时响应为准。
4. **金额单位不混用**：明确区分分与元；开票金额以 `invoiceAmount` 返回值为准，原样传递，不自行换算。支付渠道只有编码时原样展示，不猜测其含义。
5. **高风险操作先确认**：调用创建订单、获取支付链接、取消订单、确认收货或申请开票前，复述具体对象、当前状态、金额和动作，向用户请求单独中文确认；不得展示内部 boolean 字段或实现细节。
6. **保护隐私与凭据**：收货地址展示到足以让用户安全选择的程度，避免无必要重复完整手机号/地址；永不展示 API Key、token、secret、callback code、Authorization Header、支付敏感字段或隐藏的 `tokenExpiresAt`。
7. **链接与不可逆事项**：支付链接仅供用户手动打开，不自动打开或支付；取消结果只表示尝试取消，不承诺退款；确认收货和开票的不可逆性要在确认前说明。
8. **逐单报告开票结果**：遍历 `successList` / `failedList`，将 `INVOICE_ALREADY_APPLIED` 解释为历史已开票，不把它误报为系统故障；不能只根据顶层 `success` 下结论。
9. **错误与不可用字段**：遇到 `authorization_required`、`confirmation_required`、`1002`、`1003`、`1005`、401、402 或 4xx/5xx 时，根据错误信息给出修正建议；未返回、为 `0` 或 `-1` 的业务字段标为 N/A 或省略，不猜测缺失值。
10. **失败停止与费用提示**：预览业务失败、授权无效、参数不合法或余额不足时停止依赖它的后续调用；需要再次查询、改参数或重试前提示可能产生额外消耗，由用户决定是否继续。

## 解决认证和积分问题

发生以下异常情况时读取 `references/onboarding.md`。WorkBuddy 自动处理 Linkfox 调用授权，不索取或配置凭证：

### 异常情况

- **MCP 工具不存在或不可用**：检查 `LinkFox` 配置并刷新会话；禁止改走旧 HTTP 网关。
- **响应 401 或 `authorized error`**：视为 WorkBuddy 自动授权上下文异常，提示刷新会话或检查连接；不在参数中补传凭证。
- **响应 402 / 积分或余额不足**：识别“积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值”等同义信息，引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动查询套餐、下单、支付或轮询。
- **1688 OAuth 授权缺失或失效**：`authorization_required`、1005 或 `authorizedStores` 没有 ACTIVE 且未过期账号时，调用 `alibaba1688/authorizeUrl`，用户完成 OAuth 后再调用 `alibaba1688/authorizedStores`；不要向用户暴露 token 刷新细节。
- **不属于本流程的 403**：403 表示权限问题，不将其误归类为认证或余额问题；根据返回错误说明需要的权限或人工处理。

充值和重新查询都不是自动动作，必须让用户决定是否继续。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
