# Lazada 店铺财务查询接口说明

## 公共规则

### 调用规范

- LinkFox 网关使用 `POST /lazada/finance`。基础地址优先取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`。超时 150 秒。
- 请求头使用 `Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0` 和 `Authorization: <LinkFox Key>`。优先从 `LINKFOX_AGENT_API_KEY` 取 Key，兼容 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。
- 业务命令实时查询。`--no-cache` 是兼容选项。`--inline` 打印完整脱敏数据并继续保存。

| 网关字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 是 | 来自已授权店铺记录，原样传递。 |
| `operation` | 字符串 | 是 | 下方的操作标识。命名脚本从命令行操作自动填入。 |
| `params` | 对象 | 是 | 对应操作的上游业务字段。 |

### 响应结构

网关返回业务 `data` 与上游 `requestId`，也可能由外层 `data` 包裹。CLI 去除网关包裹，保存以下字段。金额原本为字符串时按原精度保留。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象或数组 | 上游业务数据，结构见各操作。查询为空可返回空数组。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `success` | 布尔值 | CLI 调用是否成功。 |

## 打款状态

`listPayouts` → `GET /finance/payout/status/get`。

| `params` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `created_after` | 字符串 | 是 | 结算起始日期，格式 `YYYY-MM-DD`。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 打款及结算记录。 |
| `data[].statement_number` | 字符串 | 结算单编号。 |
| `data[].created_at`、`data[].updated_at` | 字符串 | 创建、更新时间。 |
| `data[].paid` | 字符串 | `1` 表示已付，`0` 表示未付。 |
| `data[].payout`、`data[].currency` | 字符串 | 打款金额、币种，以实际返回为准。 |
| `data[].opening_balance`、`data[].closing_balance`、`data[].guarantee_deposit` | 字符串 | 期初余额、期末余额、保证金。 |
| `data[].item_revenue`、`data[].other_revenue_total` | 字符串 | 商品收入、其他收入合计。 |
| `data[].shipment_fee`、`data[].shipment_fee_credit`、`data[].fees_total` | 字符串 | 运费、运费抵扣、费用合计。 |
| `data[].subtotal1`、`data[].subtotal2` | 字符串 | 平台结算小计。 |
| `data[].refunds`、`data[].fees_on_refunds_total` | 字符串 | 退款及退款费用合计。 |

## 交易明细

`listTransactionDetails` → `GET /finance/transaction/details/get`。

| `params` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `start_time` | 字符串 | 是 | 查询起始日，格式 `YYYY-MM-DD`。 |
| `end_time` | 字符串 | 是 | 查询结束日，格式 `YYYY-MM-DD`。 |
| `offset` | 整数 | 否 | 记录偏移量。 |
| `limit` | 整数 | 否 | 每页数量，上游上限 500。 |
| `trans_type` | 字符串 | 否 | 已确认的上游交易类型。 |
| `trade_order_id` | 字符串 | 否 | 目标订单 ID。 |
| `trade_order_line_id` | 字符串 | 否 | 目标订单行 ID。 |

上游要求日期跨度小于 180 天。按原金额正负号解释账单。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 交易明细记录。 |
| `data[].amount`、`data[].VAT_in_amount`、`data[].WHT_amount`、`data[].WHT_included_in_amount` | 字符串 | 交易金额、增值税、预扣税及金额中的预扣税字段，按平台口径读取。 |
| `data[].fee_type`、`data[].fee_name`、`data[].details` | 字符串 | 费用类型、费用名称和费用明细。 |
| `data[].statement`、`data[].paid_status` | 字符串 | 结算期间、付款状态。 |
| `data[].seller_sku`、`data[].lazada_sku` | 字符串 | 卖家 SKU、Lazada SKU。 |
| `data[].order_no`、`data[].orderItem_no`、`data[].orderItem_status` | 字符串 | 订单、订单行编号及订单行状态。 |
| `data[].shipping_provider`、`data[].shipping_speed`、`data[].shipment_type` | 字符串 | 物流服务商、配送时效及履约类型。 |
| `data[].reference`、`data[].payment_ref_id` | 字符串 | 引用编号、付款参考 ID。 |
| `data[].transaction_date`、`data[].transaction_type`、`data[].transaction_number` | 字符串 | 交易日期、类型、编号。 |

上游备注 `comment` 由 LinkFox 移除。

## 账户流水

`listAccountTransactions` → `POST /finance/transaction/accountTransactions/query`，为只读操作。

| `params` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `page_num` | 整数 | 是 | 页码。 |
| `page_size` | 整数 | 是 | 每页数量。 |
| `start_time` | 字符串 | 是 | 查询起始日，格式 `YYYYMMDD`。 |
| `end_time` | 字符串 | 是 | 查询结束日，格式 `YYYYMMDD`。 |
| `transaction_type` | 字符串 | 否 | `Deposit`、`Withdrawal` 或 `Payment`。 |
| `sub_transaction_type` | 字符串 | 否 | `Settlement`、`Failed Payment`、`Returned Payment`、`Auto Withdrawal`、`Manual Withdrawal` 或 `Sponsored Solutions Top-up`。 |
| `transaction_number` | 字符串 | 否 | 指定流水编号。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.page_info` | 对象 | 分页信息。 |
| `data.page_info.page_num`、`data.page_info.page_size`、`data.page_info.total_page`、`data.page_info.total_count` | 整数或数字字符串 | 当前页、页容量、总页数、总条数。 |
| `data.transactions` | 对象数组 | 流水列表。 |
| `data.transactions[].pmt_reference`、`data.transactions[].transaction_number` | 字符串 | 支付参考、流水编号。 |
| `data.transactions[].transaction_time`、`data.transactions[].type`、`data.transactions[].sub_type` | 字符串 | 流水时间、类型及子类型，类型名称可能本地化。 |
| `data.transactions[].amount`、`data.transactions[].currency` | 字符串 | 金额、币种。 |
| `data.transactions[].tracking_list` | 对象数组 | 流水处理进度。 |
| `data.transactions[].tracking_list[].name`、`data.transactions[].tracking_list[].status`、`data.transactions[].tracking_list[].update_time` | 字符串 | 进度节点、状态及更新时间。 |

后端直接返回业务对象的 `page_info` 和 `transactions`。收款账户及备注字段由 LinkFox 移除。

[Lazada Finance API](https://open.lazada.com/apps/doc/doc?docId=108249&nodeId=10556)

## 错误处理

- 先判断 HTTP、网关错误和业务响应形状。失败时保留可用的脱敏错误码和请求标识，脚本以非零状态退出。
- `REAUTHORIZATION_REQUIRED` 时核对当前店铺授权。`LAZADA_PROXY_FORBIDDEN` 时由接入方核查代理出口。其他权限错误时确认目标应用的财务权限。
- 确认是 LinkFox Key 或计费问题后，再按 [认证和算力指引](onboarding.md) 处理。

## Feedback

仅在用户同意后向反馈接口提交脱敏摘要。省略店铺、账户、交易、凭据及原始响应。

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- 请求头 `Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-finance",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "用户同意发送的脱敏反馈摘要"
}
```
