---
name: linkfox-1688-procurement
description: 1688采购全流程技能。用于1688授权链接、授权店铺检查、收货地址、商品SKU、下单预览、创建订单、支付链接、订单状态、物流、物流轨迹、取消订单、确认收货、开发票等已授权采购履约场景。用户提到1688采购、1688下单、1688授权、1688订单、1688支付、1688物流、1688开发票、1688开票、1688发票、1688 sourcing procurement或1688 order processing时触发。以图搜图使用linkfox-1688-search-by-image。
---

# 1688 Procurement Workflow

通过 `LinkFox.proxy_call` 处理已授权 1688 采购履约。完整参数、响应字段和错误码见 `references/api.md`，多步骤状态规则见 `references/workflow.md`。

## Core Rules

- WorkBuddy 自动注入 Linkfox 调用授权；禁止在 `arguments` 中传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- `alibaba1688/authorizeUrl` 发起 1688 OAuth；`alibaba1688/authorizedStores` 检查当前 Linkfox 用户的授权状态。
- 除上述两个授权 operation 外，每个采购 operation 前都先调用 `authorizedStores`；仅在存在 `status=ACTIVE` 且 `expired=false` 的账号时继续。
- 浏览器跳转不等于授权成功，必须重新调用 `authorizedStores` 核验。
- 各 operation 可按用户需求独立执行；不得自动跑完整采购闭环、连续轮询或因错误自动换参数重试。
- 创建订单、获取支付链接、取消订单、确认收货和申请开票都需要紧邻调用前、针对具体对象和动作的单独中文确认。
- `cancelOrder` 不是退款或售后。已付款、已发货或已完成订单应转到 1688 退款/售后流程。
- 图片找货属于 `linkfox-1688-search-by-image`，不在本能力中。

## MCP Tools

| `toolName` | 风险 | OAuth 前置 | 用途 |
|---|---:|---:|---|
| `alibaba1688/authorizeUrl` | 低 | 否 | 生成授权链接 |
| `alibaba1688/authorizedStores` | 低 | 否 | 检查当前用户授权账号 |
| `alibaba1688/receiveAddressList` | 低 | 是 | 查询收货地址 |
| `alibaba1688/sku` | 低 | 是 | 查询 SKU/规格 |
| `alibaba1688/orderPreview` | 中 | 是 | 预览商品、运费、优惠和地址 |
| `alibaba1688/createOrder` | 高 | 是 | 创建订单 |
| `alibaba1688/paymentUrl` | 高 | 是 | 获取手动支付链接 |
| `alibaba1688/orderStatus` | 低 | 是 | 查询订单状态 |
| `alibaba1688/logistics` | 低 | 是 | 查询物流摘要 |
| `alibaba1688/logisticsTrace` | 低 | 是 | 查询物流轨迹 |
| `alibaba1688/confirmReceive` | 高 | 是 | 确认收货 |
| `alibaba1688/cancelOrder` | 高 | 是 | 尝试取消订单 |
| `alibaba1688/invoiceAmount` | 低 | 是 | 查询逐单可开票金额 |
| `alibaba1688/invoiceApply` | 高 | 是 | 申请开票 |

## MCP Call Contract

`toolName` 必须使用上表精确值，区分大小写且没有前导 `/`。原请求对象直接放在 `arguments`，不要增加 `body`、`params`、`data` 或另一层 `arguments`。

```json
{
  "toolName": "alibaba1688/sku",
  "arguments": {"offerId":"1234567890123456789"}
}
```

text JSON 只解析一次。先处理 MCP 连接、工具、schema 和 `isError`，再处理下游 `errcode`、`code`、`success` 与消息字段。MCP 缺失时不得回退旧 HTTP 网关。

## High-Risk Confirmation

紧邻每个高风险调用前，用业务语言复述具体订单、金额、当前状态和动作，并取得单独中文明确确认。只有上一条消息已清楚询问同一具体动作时，“确认”才有效；更早的“继续”“可以”“按上面来”无效。

确认后才可加入对应 JSON boolean 安全字段：

| `toolName` | 安全字段 | 额外门禁 |
|---|---|---|
| `alibaba1688/createOrder` | `confirmCreateOrder=true` | 必须先展示成功预览；优先使用稳定唯一的 `outOrderId` |
| `alibaba1688/paymentUrl` | `confirmGetPaymentUrl=true` | 创建订单确认不代表支付链接确认 |
| `alibaba1688/cancelOrder` | `confirmCancel=true` | 先核验订单仍处于可取消状态；取消不等于退款 |
| `alibaba1688/confirmReceive` | `confirmReceive=true` | 已签收或状态查询不等于确认收货 |
| `alibaba1688/invoiceApply` | `confirmApplyInvoice=true` | 先查询逐单金额并确认类型、抬头和金额 |

高风险调用超时、MCP 错误或结果不明确时不得自动重放。创建订单结果不确定时先查询已有订单状态，不再次创建相同业务订单。

## Common Workflow

1. 调用 `alibaba1688/authorizedStores`，仅在 ACTIVE 且未过期时继续。
2. 无有效授权时调用 `alibaba1688/authorizeUrl`，让用户手动完成 OAuth，再复查授权状态。
3. 按需调用 `sku` 与 `receiveAddressList`，再调用 `orderPreview`。
4. 展示商品、规格、数量、单价、运费、地址、订单总额和警告。预览失败、金额为 0 或关键列表为空时停止。
5. 单独确认后调用 `createOrder`；成功不表示用户同意获取支付链接。
6. 再次单独确认后调用 `paymentUrl`，只把链接交给用户手动打开，不自动支付。
7. 按用户请求调用订单状态、物流摘要和物流轨迹；不主动轮询。
8. 取消前先查状态，确认收货前核对具体订单；两项分别确认，均不自动重试。
9. 开票先调用 `invoiceAmount`，将逐单 `amount` 以分为单位原样传递；确认发票信息后才调用 `invoiceApply`。

## Invoice Rules

- `invoiceAmount.success=false` 但业务调用成功时，按 `retCodes` 和金额列表逐单判断，不直接申请不可开票订单。
- 普票为 `VATAX_COMM`，专票为 `VATAX_SPEC`；个人抬头为 `PERSONAL`，企业抬头为 `COMPANY`。
- 企业抬头需要税号；企业专票还需要开户行、银行账号、注册地址和企业电话。
- 遍历 `successList` 与 `failedList` 逐单报告。`INVOICE_ALREADY_APPLIED` 表示历史已开票，不作为系统故障。
- 开票成功无法在本系统回滚；红冲需要联系商家。

## Display And Privacy

- 仅展示授权是否可用，不展示 token 有效期、刷新窗口或内部授权字段。
- 收货地址只展示足以安全选择的信息，避免重复完整手机号和地址。
- 金额必须区分分与元；开票金额使用 `invoiceAmount` 原值，不自行换算。
- 支付链接只展示给用户手动打开，不自动打开、支付或无必要重复展示。
- 不展示任何凭证、token、secret、callback code、支付敏感字段或内部确认实现。
- 同一任务内相同 `toolName + arguments` 不重复调用；继续查询前说明可能产生积分消耗。

## Important Limitations

- 不暴露 `/alibaba1688/proxy/callback`、`/alibaba1688/authorizeCallback` 或 OAuth callback URL。
- 不要求用户提供 1688 token、refresh token、callback code 或 secret。
- 不查询后端数据库判断授权，唯一依据是 `authorizedStores`。
- 不使用 `_dataQuery_executeDynamicQuery` 获取实时采购响应。
- 旧脚本的自动脱敏、按大小落盘和 stdout 摘要不属于 MCP 返回能力；本 skill 不声称这些行为仍会自动发生。

## Feedback

用户明确表达满意、不满、结果不符或改进建议时，按 `references/api.md` 的 Feedback API 规则处理。反馈不得包含凭证、完整地址、手机号或支付链接。
