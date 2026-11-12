# Lazada 店铺财务查询接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`。
- **请求方式**：POST JSON，HTTP 超时 150 秒。上游 method/path 见各操作；外层 POST 不表示业务写入。
- **请求头**：`Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <api_key>`。
- Key 优先取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 原样透传，缺省为空字符串。
- 店铺令牌由后端管理。`connectionId` 必须属于当前 LinkFox 用户，站点由该连接确定。CLI 输入和保存结果见 [script-usage.md](script-usage.md)，不属于额外网关字段。

### 响应码基本规则

- **正常响应**：HTTP 200–299，且 `errcode` 缺失、为 null、为空字符串或纯空白，或为 200–299 的整数／数字字符串；再按各接口检查业务结果。
- **未正常响应**：HTTP 非 2xx 或 `errcode` 为其他非空值。`0`、`false` 不视为空；HTTP 200 的 XML `ToolErrorResponse` 或非 JSON 正文不作为业务成功。
- **认证或用量错误**：401／402 结合 `errmsg` 定位；确认是 LinkFox Key 或计费问题后，按 [onboarding.md](onboarding.md) 处理。店铺授权、应用权限、站点和代理限制分别核查，不引导重复注册充值。
- 上游 HTTP 和业务码由后端判定；网关不返回独立 `httpStatus`，不要把 CLI 诊断字段当作上游 HTTP 状态。合法空数组／空页可成功，缺失结构不擅自当空结果。

### 网关错误响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | 整数或数字字符串 | 网关错误码，HTTP 200 也可能为业务失败。 |
| `errmsg` | 字符串 | 网关或经后端处理的上游错误说明。CLI 只输出可安全保留的诊断，见脚本参考。 |

`1002` 表示身份或参数问题，`1004` 表示当前用户未拥有对应申请／连接；结合消息确认具体对象。原始错误正文不进入报告或反馈。

### 业务操作请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 当前用户的店铺连接 ID，最长 36 字符。 |
| `operation` | 字符串 | 是 | 对应操作名称，最长 64 字符；不能传任意上游路径。 |
| `params` | 对象 | 按操作 | 仅传当前操作列出的字段；无参数时可省略，按 `{}` 处理。对象、数组和字符串化 JSON 的类型按下表保留。 |

对象、数组在紫鸟 POST 代理参数中按约定编码成 JSON 文本；接口要求的 XML／JSON 文本放在字符串字段中，不提前编码普通对象。普通 `params` 序列化大小上限为 1 MiB；素材接口限制见各操作。

### 网关成功响应

成功响应为下表对象；网关部署可能将该对象放在外层 `data` 中。下文 `data.*` 从本表的业务 `data` 开始，外层包装单独判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作定义的标量／null | 业务结果。写记录续查／重复提交可能为 null，不能据此推断未执行。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `clientRequestId` | 字符串，可缺省 | 写操作原 UUID；只读代理查询不返回此字段。 |
| `status` | 字符串，可缺省 | 写记录状态；只读代理查询不返回此字段。 |

仅含业务 `data` 的上游响应由后端去除该层；仍含 `success`、`result`、`_trace_id_` 等独立字段时保留原业务层次。后端去除传输层 `code`、`type`、`message`、`msg` 及敏感字段。各操作的字段表注明实际路径；上游业务 `success` 与本地 CLI 顶层 `success` 含义不同，网关没有额外的 CLI 成功字段。

官方示例中的数字、布尔值可能为字符串，也可能返回 null 或字符串 `"null"`；保留实际类型，不把缺失值补成 0。LinkFox 将 `id`、`ids` 或 `idList` 结尾的整数字段转为字符串，其他字段按合同处理，避免损失长 ID 精度。

## 接口：打款状态（listPayouts）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/finance`。
- **上游方法与路径**：`GET /finance/payout/status/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listPayouts`；下表列出 `params` 内部字段。

`listPayouts` → `GET /finance/payout/status/get`。

| `params` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `created_after` | 字符串 | 是 | 结算起始日期，格式 `YYYY-MM-DD`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

本操作固定提取上游业务 `data` 作为网关 `data`，即使上游同时带独立跟踪字段也不增加业务包装层。

| 响应字段 | 类型 | 说明 |
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

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：交易明细（listTransactionDetails）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/finance`。
- **上游方法与路径**：`GET /finance/transaction/details/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listTransactionDetails`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

本操作固定提取上游业务 `data` 作为网关 `data`，即使上游同时带独立跟踪字段也不增加业务包装层。

| 响应字段 | 类型 | 说明 |
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

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：账户流水（listAccountTransactions）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/finance`。
- **上游方法与路径**：`POST /finance/transaction/accountTransactions/query`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listAccountTransactions`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

本操作固定提取上游业务 `data` 作为网关 `data`，即使上游同时带独立跟踪字段也不增加业务包装层。

| 响应字段 | 类型 | 说明 |
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

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 错误处理

- 先判断 HTTP、网关错误和业务响应形状。失败时保留可用的脱敏错误码和请求标识，脚本以非零状态退出。
- `REAUTHORIZATION_REQUIRED` 时核对当前店铺授权。`LAZADA_PROXY_FORBIDDEN` 时由接入方核查代理出口。其他权限错误时确认目标应用的财务权限。
- 确认是 LinkFox Key 或计费问题后，再按 [认证和算力指引](onboarding.md) 处理。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。仅发送用户授权的脱敏摘要，不含凭据或原始业务数据。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-finance",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
