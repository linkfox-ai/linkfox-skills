# 1688采购流程地图

## 总原则

- 这是按需流程地图，不是自动执行的完整闭环。
- 每次调用都使用 `LinkFox.proxy_call` 和 `references/api.md` 中的精确 `toolName`。
- 除授权链接与授权状态外，业务调用前先检查 `authorizedStores`；无 ACTIVE 且未过期授权时停止。
- 查询、预览、下单、支付链接、履约、取消、收货和开票可以独立触发；不要自动串联、重试或轮询。
- 创建订单、获取支付链接、取消订单、确认收货和申请开票分别需要紧邻调用前的单独中文确认。

## 1. 授权检查

调用 `alibaba1688/authorizedStores`，读取当前 Linkfox 用户的 `stores`：

- 有 `status=ACTIVE` 且 `expired=false`：可以按需继续。
- 无账号或授权失效：停止业务调用，进入授权流程。
- 只展示授权是否可用，不展示 token 有效期、刷新窗口或内部字段。

## 2. 发起授权

调用 `alibaba1688/authorizeUrl` 生成链接，让用户手动打开并完成 OAuth。浏览器跳转不能证明授权成功；完成后必须重新调用 `authorizedStores` 核验。不得自动打开授权链接，也不得索取 token 或 callback code。

## 3. 找货与 SKU

已有 `offerId` 时调用 `alibaba1688/sku`。价格与库存只用于规格选择，最终可购性、价格、运费和优惠以 `orderPreview` 为准。图片找货交给 `linkfox-1688-search-by-image`。

## 4. 收货地址

调用 `alibaba1688/receiveAddressList`。多地址时让用户明确选择 `addressId`；展示足够选择的信息即可，避免无必要重复完整手机号与详细地址。也可在预览中按参数契约使用完整 `addressParam`。

## 5. 下单预览

使用 `alibaba1688/orderPreview`，普通采购显式传 `flow=general`。展示商品、规格、数量、商品金额、运费、优惠、地址、总额和警告。

以下情况停止，不进入创建订单：

- `status=false` 或上游消息表示失败。
- 金额为 0。
- 交易、支付或优惠等关键列表异常为空。
- SKU、规格、起批量、售卖单位、数量或地址仍不明确。

预览返回不等于用户同意下单。不得为试探而自动改变数量、地址或 flow 重试。

## 6. 创建订单

向用户复述预览摘要、金额、收货对象和“创建订单”动作，取得本次单独中文确认。确认后调用 `alibaba1688/createOrder`，并加入 JSON boolean `confirmCreateOrder=true`。优先传稳定且业务唯一的 `outOrderId`。

创建调用超时或结果不明确时，先用状态查询核验，不得再次创建相同业务订单。成功返回的 `orderId` 是后续支付、状态、物流、取消和确认收货使用的 1688 订单号。

## 7. 获取支付链接

创建订单成功不代表用户同意获取支付链接。再次复述具体订单并取得单独确认后，调用 `alibaba1688/paymentUrl`，加入 `confirmGetPaymentUrl=true`。链接只展示给用户手动打开，不自动打开或支付，也不重复获取或展示。

## 8. 订单状态与物流

- `alibaba1688/orderStatus`：查询履约状态。
- `alibaba1688/logistics`：查询物流摘要并取得 `logisticsId`。
- `alibaba1688/logisticsTrace`：查询指定物流轨迹。

仅在用户提出查询时调用，不主动轮询。轨迹时间按 Asia/Shanghai 展示。

## 9. 取消订单

先查询订单状态：

- 未付款/待付款：可进入取消确认。
- 已付款待发货：不要调用取消；引导用户到 1688 发起退款/售后。
- 已发货/已完成：不要调用取消；引导用户到 1688 处理退货退款或售后。
- 已取消：无需重复调用。

对可取消订单复述订单号、当前状态、取消原因，并明确“取消不等于退款”。取得单独确认后调用 `alibaba1688/cancelOrder`，加入 `confirmCancel=true`。失败或结果不明时不自动重试。

## 10. 确认收货

查询物流、看到已签收或询问状态都不等于确认收货。复述具体订单和不可逆影响，取得单独确认后调用 `alibaba1688/confirmReceive`，加入 `confirmReceive=true`。不得自动重试。

## 11. 开发票

开票分两步，不能自动联动多订单。

### 11.1 查询可开票金额

调用 `alibaba1688/invoiceAmount`。逐单读取 `orderInvoiceAmountModelList[].amount`，以分为单位原样保留，不自行计算或换算。`success=false` 时结合 `retCodes` 与列表逐单判断，不可开票订单不得进入申请步骤。

### 11.2 申请开票

向用户复述订单号、发票类型、抬头和可开票金额。取得本次明确确认后调用 `alibaba1688/invoiceApply`，加入 `confirmApplyInvoice=true`，并使用上一步金额原值。

- 企业抬头需要税号；企业专票还需要开户行、银行账号、注册地址和企业电话。
- 遍历 `successList` / `failedList` 逐单报告，不只看顶层 `success`。
- `INVOICE_ALREADY_APPLIED` 表示历史已开票。
- 开票成功不可在本系统回滚，红冲需联系商家。
- 失败、超时或结果不明确时不得自动重放申请。

## MCP 失败纪律

MCP 停用或工具缺失时，提示检查 `LinkFox` 配置并刷新会话。禁止回退旧 HTTP route、脚本或其他未声明工具。text JSON 只解析一次，并区分 MCP/代理错误与下游业务错误。
