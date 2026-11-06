# 订单金额/供货价查询 接口说明

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

## 接口：订单金额/供货价查询（bg.order.amount.query）

| 项 | 值 |
|----| ----- |
| **脚本** | `scripts/eu_order_amount_query.py` |
| **Partner 文档** | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9（按 `type` 在 Partner EU 后台打开） |
| **网关** | `POST /temu/proxy`，`type`=`bg.order.amount.query`，业务载荷放在 Body 的 `params` |

用于订单金额/供货价查询。

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
| type | string | 是 | 固定为 `bg.order.amount.query`；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
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

> 下列带 **`currency` + `amount`** 的金额块结构相同，见 [金额块（MoneyAmount）](#金额块moneyamount)。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------| ------ |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 订单金额结果 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| parentOrderMap | OBJECT | 父订单信息（父订单金额汇总） |
| orderList | OBJECT[] | 子订单信息（子订单金额明细） |
| warning | STRING[] | 告警信息 |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------| ------ |
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

#### `parentOrderMap` 金额字段公式（官方说明）

| 字段 | 公式 / 说明 |
|------| ------------- |
| estimatedRevenue | `estimatedRevenue = basePriceTotal + shippingAmountTotal - estimatedRevenueDeduction + signOnDelivery` |
| customerPaid | `customerPaid = retailPriceTotal + shippingAmountTotal + taxTotal - refundsTotal + signOnDelivery - totalDiscount` |
| totalDiscount | `totalDiscount = discountFromTEMU + discountFromSeller` |
| signOnDelivery | 消费者未购买该服务时返回 **NULL**；签收服务费已退款时返回 **0** |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| orderSn | STRING | 子订单号 |
| basePrice | OBJECT | 子单基础价/供货价 |
| unitBasePrice | OBJECT | 单位基础价小计 |
| quantity | INTEGER | 订单原始单品数量 |
| unitRetailPrice | OBJECT | 单位零售价 |
| discountFromSeller | OBJECT | 该商品卖家折扣 |
| discountFromTEMU | OBJECT | 该商品平台折扣 |
| shipAmountTotal | OBJECT | 该商品运费合计 |


#### 金额块（MoneyAmount）

以下字段均为 **OBJECT**，结构一致：

| 参数 | 类型 | 说明 |
|------|------| ------ |
| currency | STRING | 币种代码 |
| amount | LONG | 本地货币**最小单位**金额。例如美国：**Cents（分）** |

适用字段：`basePriceTotal`、`shippingAmountTotal`、`taxTotal`、`discountFromSeller`、`discountFromTEMU`、`refundsTotal`、`estimatedRevenueDeduction`、`estimatedRevenue`、`retailPriceTotal`、`customerPaid`、`totalDiscount`、`signOnDelivery`，以及 `orderList[]` 中的 `basePrice`、`unitBasePrice`、`unitRetailPrice`、`discountFromSeller`、`discountFromTEMU`、`shipAmountTotal`。

> 展示金额时注明返回的 `currency`，按该币种的最小单位换算为主币种；以分为最小单位时，将 `amount` 除以 100。

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
  "skillName": "linkfox-temu-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
