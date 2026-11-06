# 订单金额查询 V2 接口说明

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

## 接口：订单金额查询 V2（temu.order.amount.v2.query）

| 项 | 值 |
|----| ----- |
| **脚本** | `scripts/eu_order_amount_v2_query.py` |
| **Partner 文档** | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9&sub_menu_code=91661bf0642440ddbd462b25fa96edfb |
| **网关** | `POST /temu/proxy`，`type`=`temu.order.amount.v2.query`，业务载荷放在 Body 的 `params` |

用于订单金额查询 V2。

> **与 V1 区别：** [`bg.order.amount.query`](./bg-order-amount-query.md)（`bg.order.amount.query`）字段结构较简；**V2** 使用 **`salesProceeds`** / **`customerPaid`** 分组及更多 `TaxExcl`/`TaxIncl` 明细。欧洲站含税价场景可对照 [`temu.order.amount.v3.query`](./temu-order-amount-v3-query.md)。

> **网关鉴权字段**由本技能处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**，**`site=eu`**。

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
| type | string | 是 | 固定为 `temu.order.amount.v2.query`；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
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

#### 顶层字段

| 参数 | 类型 | 说明 |
|------|------| ------ |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 订单金额结果（V2） |

#### `result`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| parentOrderMap | OBJECT | 父订单金额汇总，含 `salesProceeds` 与 `customerPaid` |
| orderList | OBJECT[] | 子订单金额明细列表 |
| warning | STRING[] | 告警信息，如部分金额仍在系统计算中 |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| parentOrderSn | STRING | 父订单号 |
| salesProceeds | OBJECT | 卖家侧销售收入/结算相关金额 |
| customerPaid | OBJECT | 消费者支付相关金额 |

#### `parentOrderMap.salesProceeds`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| productTax | MoneyAmount | 商品税 |
| productTaxCustomerDiscounted | MoneyAmount | 消费者折扣后商品税 |
| shippingTaxCustomerDiscounted | MoneyAmount | 消费者折扣后运费税 |
| basePriceSellerDiscount | MoneyAmount | 卖家基础价折扣 |
| shippingTotalTaxExcl | MoneyAmount | 不含税运费合计 |
| basePriceOff | MoneyAmount | 基础价减免 |
| basePriceDiscountedTotal | MoneyAmount | 折后基础价合计 |
| estimatedSettlementTotal | MoneyAmount | 预估结算合计 |
| shippingTax | MoneyAmount | 运费税 |
| productTaxTemu | MoneyAmount | Temu 部分商品税 |
| shippingTaxTemu | MoneyAmount | Temu 部分运费税 |
| shippingCustomerTotalTaxExcl | MoneyAmount | 消费者不含税运费合计 |
| estimatedDeduction | MoneyAmount | 预估扣减 |
| basePriceTotal | MoneyAmount | 基础价/供货价合计 |
| shippingTemuDiscountTotalTaxExcl | MoneyAmount | Temu 不含税运费折扣合计 |

#### `parentOrderMap.customerPaid`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| retailPriceDiscountedTotalTaxExcl | MoneyAmount | 折后不含税零售价合计 |
| productRefundsTotal | MoneyAmount | 商品退款合计 |
| retailPriceTemuDiscountTaxExcl | MoneyAmount | Temu 不含税零售价折扣 |
| retailPriceSellerDiscountTaxExcl | MoneyAmount | 卖家不含税零售价折扣 |
| retailPriceTotalTaxIncl | MoneyAmount | 含税零售价合计 |
| shippingDiscountedTotalTaxExcl | MoneyAmount | 折后不含税运费合计 |
| shippingTotalTaxExcl | MoneyAmount | 不含税运费合计 |
| shippingTaxTemuDiscount | MoneyAmount | Temu 运费税折扣 |
| shippingTax | MoneyAmount | 运费税 |
| customerPaidTotal | MoneyAmount | 消费者实付合计 |
| retailPriceTotalTaxExcl | MoneyAmount | 不含税零售价合计 |
| shippingTaxDiscounted | MoneyAmount | 折后运费税 |
| productTaxDiscounted | MoneyAmount | 折后商品税 |
| shippingTemuDiscountTotalTaxExcl | MoneyAmount | Temu 不含税运费折扣合计 |
| shippingTotalTaxIncl | MoneyAmount | 含税运费合计 |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| orderSn | STRING | 子订单号 |
| quantity | INTEGER | 数量 |
| productTaxRate | INTEGER/NUMBER | 商品税率，示例为数值 |
| shipTaxRate | INTEGER/NUMBER | 运费税率 |
| productTax | MoneyAmount | 商品税 |
| productTaxCustomerDiscounted | MoneyAmount | 消费者折扣后商品税 |
| shippingTaxCustomerDiscounted | MoneyAmount | 消费者折扣后运费税 |
| retailPriceTotalTaxIncl | MoneyAmount | 含税零售价合计 |
| basePriceSellerDiscount | MoneyAmount | 卖家基础价折扣 |
| shippingTotalTaxExcl | MoneyAmount | 不含税运费合计 |
| basePriceOff | MoneyAmount | 基础价减免 |
| estimatedSettlementTotal | MoneyAmount | 预估结算合计 |
| shippingTax | MoneyAmount | 运费税 |
| productTaxTemu | MoneyAmount | Temu 部分商品税 |
| shippingCustomerTotalTaxExcl | MoneyAmount | 消费者不含税运费合计 |
| unitRetailPriceTaxExcl | MoneyAmount | 单位不含税零售价 |
| shippingTemuDiscountTotalTaxExcl | MoneyAmount | Temu 不含税运费折扣合计 |
| shippingTotalTaxIncl | MoneyAmount | 含税运费合计 |
| retailPriceDiscountedTotalTaxExcl | MoneyAmount | 折后不含税零售价合计 |
| retailPriceTemuDiscountTaxExcl | MoneyAmount | Temu 不含税零售价折扣 |
| unitRetailPriceTaxIncl | MoneyAmount | 单位含税零售价 |
| basePriceDiscountedTotal | MoneyAmount | 折后基础价合计 |
| unitBasePrice | MoneyAmount | 单位基础价 |
| shippingTaxTemu | MoneyAmount | Temu 部分运费税 |
| retailPriceTotalTaxExcl | MoneyAmount | 不含税零售价合计 |
| estimatedDeduction | MoneyAmount | 预估扣减 |
| basePriceTotal | MoneyAmount | 基础价/供货价合计 |


#### 金额块（MoneyAmount）

除 **`quantity`**、**`productTaxRate`**、**`shipTaxRate`**、**`orderSn`**、**`parentOrderSn`**、**`warning`** 外，上表中标为 **MoneyAmount** 的字段均为 **OBJECT**：

| 参数 | 类型 | 说明 |
|------|------| ------ |
| currency | STRING | 币种 |
| amount | LONG | 本地货币最小单位，如欧区常为分 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先应用外层 HTTP / errcode 基础规则，再检查网关 `code`、解析 `body`，按 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 解释业务结果；不能仅因 JSON 可解析就认定业务成功。
- 网关 `code=1002`：核对参数及 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单及网络。Temu 业务失败时保留 `errorMsg` 和原始响应。

| errorCode | errorMsg | 处理建议 |
|-----------|----------| ---------------------- |
| 140020015 | This API is not applicable to the country or region where the current store is located. | 确认店铺区域与 `site=eu`；换适用接口或站点 |
| 140020002 | Order not found | 核对 `parentOrderSn` |
| 140020008 | Some amount fields are still undergoing system calculation. Please try again later. | 稍后重试；关注 `result.warning` |

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
  "type": "temu.order.amount.v2.query",
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
