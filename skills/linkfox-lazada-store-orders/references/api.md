# Lazada 店铺订单查询接口参考

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

### 只读代理请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 当前用户的店铺连接 ID，最长 36 字符。 |
| `operation` | 字符串 | 是 | 对应商品或订单查询名称，最长 32 字符。 |
| `queryParams` | 对象 | 按操作 | 无参数可省略；有必填字段时须提供。网关按操作校验后转发到固定上游路径。 |

### 业务操作请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 当前用户的店铺连接 ID，最长 36 字符。 |
| `operation` | 字符串 | 是 | 对应操作名称，最长 64 字符；不能传任意上游路径。 |
| `params` | 对象 | 按操作 | 仅传当前操作列出的字段；无参数时可省略，按 `{}` 处理。对象、数组和字符串化 JSON 的类型按下表保留。 |
| `requestId` | UUID 字符串 | 写入必填 | 带连字符，最长 36 字符；只读操作不传。与响应中的上游 `requestId` 不同。 |

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

### 写入与续查

后端按当前用户、连接、原 `requestId` UUID 和请求内容识别重复提交。`PENDING` 按原 UUID 续查，`SUCCEEDED` 结合具体业务结果确认生效，`REJECTED` 核对拒绝原因，`PARTIAL` 逐项核对，`UNKNOWN` 核对店铺实际状态。结果不明时不自动重放，也不换 UUID 重试。

`requestId` 已用于不同操作／参数时为冲突；查不到写记录时核对当前用户、原连接和 UUID，并检查目标状态。状态查询的 HTTP 成功不等于原写入成功。

## 接口：订单列表（listOrders）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/developerProxy`。
- **上游方法与路径**：`GET /orders/get`。本操作为只读。

### 请求参数

公共顶层字段见 [只读代理请求字段](api.md#只读代理请求字段)。本操作 `operation=listOrders`；下表列出 `queryParams` 内部字段。

`listOrders` → `GET /orders/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `created_after` | 字符串 | 与 `update_after` 至少提供一个 | 创建时间下界 |
| `created_before` | 字符串 | 否 | 创建时间上界 |
| `update_after` | 字符串 | 与 `created_after` 至少提供一个 | 更新时间下界 |
| `update_before` | 字符串 | 否 | 更新时间上界 |
| `status` | 字符串 | 否 | 按订单行状态筛选，`all` 表示所有状态 |
| `sort_by` | 字符串 | 否 | Lazada 排序字段 |
| `sort_direction` | 字符串 | 否 | Lazada 排序方向 |
| `offset` | 0–5000 的整数或数字字符串 | 否 | 结果偏移量，默认 0 |
| `limit` | 1–100 的整数或数字字符串 | 否 | 每页条数，默认 20 |

时间使用含时区的 ISO 8601，优先采用官方示例的 `+08:00` 偏移格式，例如 `2026-11-01T00:00:00+08:00`。LinkFox 也接受 `+0800` 并原样转发。需要继续翻页时保持查询条件，递增 `offset`。达到上限后调整时间范围，从 `offset=0` 开始并按当前店铺内的 `order_id` 去重。 [Lazada 订单查询指南](https://open.lazada.com/apps/doc/doc?docId=121327&nodeId=29616)

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段路径 | 类型 | 说明 |
| --- | --- | --- |
| `data.orders` | 对象数组 | 本页订单，字段同[订单详情](#接口订单详情getorder)。空数组是成功结果。 |
| `data.count` | 数值或数字字符串 | 上游返回的本页数量，可能缺失。 |
| `data.countTotal` | 数值或数字字符串 | 查询条件下的订单总量，可能缺失。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：订单详情（getOrder）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/developerProxy`。
- **上游方法与路径**：`GET /order/get`。本操作为只读。

### 请求参数

公共顶层字段见 [只读代理请求字段](api.md#只读代理请求字段)。本操作 `operation=getOrder`；下表列出 `queryParams` 内部字段。

`getOrder` → `GET /order/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `order_id` | 1 至 20 位的正整数文本 | 是 | 当前店铺的真实订单 ID |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

详情对象位于业务 `data`。字段由后端按下表保留，缺失或 null 的字段可能省略。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `order_id` | 字符串 | 订单 ID，在当前店铺内使用。 |
| `statuses`、`status` | 字符串数组、字符串 | `statuses` 汇总订单行状态，同一订单可能含多种状态。 |
| `created_at`、`updated_at` | 字符串 | 创建及更新时间。 |
| `items_count` | 数值或数字字符串 | 商品行数量，按实际字段展示。 |
| `price`、`shipping_fee`、`voucher` | 数值或数字字符串 | 价格、运费与优惠。价格字段需结合优惠及运费解释买家实付。 |
| `currency` | 字符串 | 金额币种。 |

[Lazada 订单字段说明](https://open.lazada.com/apps/doc/doc?docId=121327&nodeId=29616)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：订单商品明细（getOrderItems）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/developerProxy`。
- **上游方法与路径**：`GET /order/items/get`。本操作为只读。

### 请求参数

公共顶层字段见 [只读代理请求字段](api.md#只读代理请求字段)。本操作 `operation=getOrderItems`；下表列出 `queryParams` 内部字段。

`getOrderItems` → `GET /order/items/get`。

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `order_id` | 1 至 20 位的正整数文本 | 是 | 当前店铺的真实订单 ID |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

商品行位于业务 `data` 数组，空数组是成功结果。同款商品可有多个 `order_item_id`，核对时分别保留。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `order_item_id`、`order_id` | 字符串 | 订单行 ID 和所属订单 ID。 |
| `item_id`、`product_id` | 字符串 | 上游返回的商品标识，按实际字段区分。 |
| `sku`、`shop_sku`、`name`、`status` | 字符串 | SKU、商品名称和行状态。 |
| `created_at`、`updated_at` | 字符串 | 商品行创建及更新时间。 |
| `item_price`、`paid_price`、`shipping_amount`、`voucher_amount` | 数值或数字字符串 | 行价格、实付、运费与优惠。 |
| `currency`、`quantity` | 字符串、数值或数字字符串 | 金额币种及数量，按实际字段展示。 |

订单数据以服务端保留的业务字段为准。输出前额外移除地址、买家姓名和联系方式。 [Lazada 订单商品响应示例](https://open.lazada.com/apps/doc/doc?docId=121784&nodeId=45697)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 履约、售后与评价

发货及逆向单使用 [履约与售后接口](order-operations.md)。评价查询和回复使用 [评价接口](communications.md)。订单列表、详情和商品行继续使用本页的原查询入口。

## 接口：已接收店铺通知（listStoreEvents）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/events`。
- 本接口由 LinkFox 管理申请、连接或已接收通知，不由 CLI 直调上游。

### 请求参数

`POST /lazada/events` 通过当前用户连接读取对应店铺的已接收通知。

| 请求字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 是 | 当前用户的真实店铺连接 ID，36 字符。 |
| `limit` | 整数 | 否 | 单页 1–100 条，默认 20。 |
| `beforeId` | 字符串 | 否 | 下一页读取原样使用上页的 `nextBeforeId`；最长 19 位正整数文本，须在有符号 64 位范围内。 |

### 响应结构

| 响应字段 | 类型 | 含义 |
| --- | --- | --- |
| `events` | 对象数组 | 按接收记录倒序返回。本页无记录时为空数组。 |
| `events[].eventId`、`events[].notifyId` | 字符串 | LinkFox 事件记录及通知标识。 |
| `events[].type` | 字符串 | 事件类型。 |
| `events[].occurredAt` | 整数 | 事件时间，Unix 毫秒。 |
| `events[].status` | 字符串 | 事件携带的状态，可缺失。 |
| `events[].orderId`、`orderItemId`、`productId`、`skuId`、`reverseOrderId`、`reverseOrderLineId`、`packageId` | 字符串 | 事件关联的业务标识，按类型提供。 |
| `nextBeforeId` | 字符串或 null | 下一页游标。可缺省，表示无下一页。CLI 归一化见脚本参考。 |

通知来自已配置且通过可信入口接收的推送。同店同站点的多名已绑定用户可用各自的 connectionId 查询同一通知；仅返回当前用户本轮连续绑定时间范围内的记录。连续绑定中重新授权保留通知历史，解绑后重新绑定开始新的时间范围。解绑后该用户不能再查询，不影响其他用户；缺失或冲突的站点不返回。空列表只表示当前连接在本次查询范围内无记录。核对实际业务状态时查询原订单、商品或售后接口。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 错误处理

- HTTP 2xx 且 JSON `errcode` 缺失、为 null、为空字符串或纯空白，或者是 200–299 的整数或数字字符串，才继续检查业务数据。`0`、`false` 与 XML `ToolErrorResponse` 属于失败。失败时保存可用诊断并以非零状态退出。
- 输出可用的 `httpStatus`、`errcode`、`requestId`、`traceId` 以及服务端提供的 `upstreamCode`、`upstreamRequestId`，省略原始错误正文。
- `error=REAUTHORIZATION_REQUIRED` 时通过授权 Skill 核对该店铺连接。单凭 401 无法区分店铺授权和 LinkFox Key，应结合诊断定位。已确认 LinkFox Key 故障时按 [认证和算力指引](onboarding.md) 处理。
- `error=LAZADA_PROXY_FORBIDDEN` 时将代理出口白名单问题交给接入维护方核查。其他 403 时核对店铺或应用权限。出现 402 时先按实际调用的接口核对网关账户或计费诊断。
- `upstreamCode=SellerNotVerified` 表示 Lazada 尚未验证该卖家。请用户在对应站点的卖家中心确认验证状态，完成后再查询。
- 超时或 5xx 保留请求标识，脚本不会自动重发。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。仅发送用户授权的脱敏摘要，不含凭据或原始业务数据。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-orders",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
