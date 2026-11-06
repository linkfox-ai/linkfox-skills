# 订单金额/供货价查询 接口说明

返回 [接口总览](../api.md)。Partner 文档入口：https://partner-us.temu.com/documentation（`menu_code` / `sub_menu_code` 以后台对应接口页为准）。

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

## 接口：订单金额/供货价查询 — `bg.order.amount.query`

为自研 ERP 查询订单供货价和金额信息。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站为 `us`；US 脚本默认 `us`。 |
| managementType | string | 是 | 美国半托管为 `semi-managed`；US 脚本默认此值。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用显式 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌替代字段，为 `~/.linkfox/temu-access-tokens.json` 中的店铺键；脚本在本地解析后发送 accessToken。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`（订单/发货）；脚本用于选取对应用途的本地令牌，不混入业务参数，也不转发此字段。 |
| type | string | 是 | 本接口标识：`bg.order.amount.query`，写在 Body 中，不是 URL 路径。 |
| params | object | 否 | 官方业务参数对象，业务字段位于 `params.request`。 |
| params.request | OBJECT | 否 | 官方声明为选填对象；内部字段按下表约定，不因外层选填而免除内部必填要求。 |

脚本允许业务字段放在顶层（如 `request`）或嵌套 `params`；存在对象类型的 `params` 时优先使用该对象。认证、站点等保留键不会混入业务参数。脚本认证兼容与选项见 [运行约定](../api.md#脚本运行约定)。

```text
params
└── request (OBJECT, 选填)
    └── parentOrderSn (STRING, 必填)
```

#### `request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | 父订单号 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断；保留原始值。 |
| errmsg | string | 网关错误消息；完整保留。 |
| code | integer | 网关错误码：`1002` 参数或 Token 错误，`1003` 转发失败；不得与 Temu `errorCode` 混淆。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | JSON value | 脚本在 `body` 为非空且可解析的 JSON 字符串时增加的解析结果；解析失败时不增加此字段。 |
| error | string | HTTP 非 JSON 错误或连接错误信息（仅错误时出现）。 |
| details | string | 非 JSON HTTP 错误的原始响应内容（仅错误时出现）。 |
| gatewayResponse | JSON value | 仅当网关返回非对象 JSON 时，脚本在落盘与展示层包装原始值；不属于 Temu 业务字段。 |

以下为 Temu `body` 解析后的业务字段。先判断外层 HTTP 与 `errcode`，再检查网关 `code` 和 Temu `success` / `errorCode` / `errorMsg`，不得仅因 JSON 可解析而判成功。

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── parentOrderMap
    │   ├── parentOrderSn
    │   ├── basePriceTotal
    │   ├── shippingAmountTotal
    │   ├── taxTotal
    │   ├── discountFromSeller
    │   ├── discountFromTEMU
    │   ├── refundsTotal
    │   ├── estimatedRevenueDeduction
    │   ├── estimatedRevenue
    │   ├── retailPriceTotal
    │   ├── customerPaid
    │   ├── totalDiscount
    │   └── signOnDelivery
    ├── orderList[]
    │   ├── orderSn
    │   ├── basePrice
    │   ├── unitBasePrice
    │   ├── quantity
    │   ├── unitRetailPrice
    │   ├── discountFromSeller
    │   ├── discountFromTEMU
    │   └── shipAmountTotal
    └── warning[]
```

> 下列带 **`currency` + `amount`** 的金额块结构相同，见 [金额块（MoneyAmount）](#金额块moneyamount)。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 订单金额结果 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderMap | OBJECT | 父订单金额汇总 |
| orderList | OBJECT[] | 子订单金额明细 |
| warning | STRING[] | 告警信息 |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderSn | STRING | 父订单号 |
| basePriceTotal | OBJECT | 基础价/供货价合计 |
| shippingAmountTotal | OBJECT | 运费合计 |
| taxTotal | OBJECT | 消费者已付税费，按 realPrice 计算 |
| discountFromSeller | OBJECT | 卖家折扣 |
| discountFromTEMU | OBJECT | 平台折扣 |
| refundsTotal | OBJECT | 退款合计 |
| estimatedRevenueDeduction | OBJECT | 预估收入扣减 |
| estimatedRevenue | OBJECT | 预估收入 |
| retailPriceTotal | OBJECT | 零售价/促销售价合计 |
| customerPaid | OBJECT | 消费者实付合计 |
| totalDiscount | OBJECT | 折扣合计 |
| signOnDelivery | OBJECT | 签收服务费 |

##### `parentOrderMap` 金额字段公式（官方说明）

| 字段 | 公式 / 说明 |
|------|-------------|
| estimatedRevenue | `estimatedRevenue = basePriceTotal + shippingAmountTotal - estimatedRevenueDeduction + signOnDelivery` |
| customerPaid | `customerPaid = retailPriceTotal + shippingAmountTotal + taxTotal - refundsTotal + signOnDelivery - totalDiscount` |
| totalDiscount | `totalDiscount = discountFromTEMU + discountFromSeller` |
| signOnDelivery | 消费者未购买该服务时返回 **NULL**；签收服务费已退款时返回 **0** |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | 子订单号 |
| basePrice | OBJECT | 子单基础价/供货价 |
| unitBasePrice | OBJECT | 单位基础价小计 |
| quantity | INTEGER | 订单原始单品数量 |
| unitRetailPrice | OBJECT | 单位零售价 |
| discountFromSeller | OBJECT | 该商品卖家折扣 |
| discountFromTEMU | OBJECT | 该商品平台折扣 |
| shipAmountTotal | OBJECT | 该商品运费合计 |

---

#### 金额块（MoneyAmount）

以下字段均为 **OBJECT**，结构一致：

| 参数 | 类型 | 说明 |
|------|------|------|
| currency | STRING | 币种代码 |
| amount | LONG | 本地货币**最小单位**金额。例如美国：**Cents（分）** |

适用字段：`basePriceTotal`、`shippingAmountTotal`、`taxTotal`、`discountFromSeller`、`discountFromTEMU`、`refundsTotal`、`estimatedRevenueDeduction`、`estimatedRevenue`、`retailPriceTotal`、`customerPaid`、`totalDiscount`、`signOnDelivery`，以及 `orderList[]` 中的 `basePrice`、`unitBasePrice`、`unitRetailPrice`、`discountFromSeller`、`discountFromTEMU`、`shipAmountTotal`。

> 展示为美元等主币种时，需将 `amount` 除以 100（美国站）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 表示参数或 LinkFox Token 无效，核对参数与认证；`code=1003` 表示转发失败，核对 Temu token、用途、IP 白名单与网络。
- Temu 业务结果以 `body` 中的 `success`、`errorCode`、`errorMsg` 判断；`success=false` 时按上游错误说明处理。保留原始错误，不补造业务结果或未知响应码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.amount.query",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789"
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
  "skillName": "linkfox-temu-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
