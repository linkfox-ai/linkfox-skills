# 发票明细查询 接口说明

[接口总览](../api.md)；业务脚本：`scripts/eu_tax_invoice_detail_query.py`（相对技能根目录）。

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

## 接口：发票明细查询（temu.pay.tax.invoice.detail.query）

> 官方：[Partner EU 文档](https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=3985fe93bff5437c87863a22112b72db)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 封装默认 `eu`；通用兼容脚本支持 `cn` / `partner` / `us` / `global` / `eu`，须小写。 |
| managementType | string | 是 | EU 封装默认 `semi-managed`；通用兼容脚本支持 `full-managed` / `semi-managed`，须小写。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本也可通过下方 `storeKey` 解析后填入。与 LinkFox 用户密钥不同。 |
| type | string | 是 | `temu.pay.tax.invoice.detail.query`；写在 Body 中，不作为 URL 路径。 |
| params | object | 否 | Temu 业务参数；本接口业务对象为 `params.request`。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容字段，按此顺序优先于 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；不会转发到业务参数。 |
| accessToken | string | 与 storeKey 二选一 | 直接传入时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；按 site + managementType + tokenPurpose 精确查找，不借用其他店铺或用途的令牌。 |
| site | string | 否 | EU 业务封装默认 `eu`；自动去首尾空白并转小写。 |
| managementType | string | 否 | EU 业务封装默认 `semi-managed`；自动去首尾空白并转小写。 |
| tokenPurpose | string | 否 | EU 封装默认 `product-inventory`，以 Partner 对目标税务接口的要求为准。仅供本地令牌选择，不转发。 |
| params | object | 否 | 若为对象则整体作为业务参数，优先于顶层业务字段。 |
| request | OBJECT | 视业务 | 可直接放在脚本 JSON 顶层，或放在 `params.request`；转发后均为网关 `params.request`。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容通用调用器选项；本技能封装始终添加此选项，不读取也不写入响应缓存。 |

上述鉴权、店铺选择及 `type` 等保留字段不作为顶层业务字段转发。令牌存储位置和通用 CLI 行为见 [运行与认证约定](../api.md#运行与认证约定)。

#### Temu 业务参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 视业务 | Temu 业务请求对象；容器必填性未单独定义，按本接口子字段要求组织。 |
| params.request.parentOrderSn | STRING | **是** | 父订单号。 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共响应码基本规则判断，不与下方 Temu errorCode 混淆。 |
| errmsg | string | 网关消息；保留实际返回。 |
| code | integer | 网关错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串，原样保留。 |
| temuBody | object / array / scalar / null | 脚本在 body 为有效 JSON 字符串时追加解析结果；解析失败不添加，不丢弃原始 body。下表是其业务对象结构。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _linkfoxHttpStatus | integer / null | 实际 HTTP 状态；连接失败为 null。仅由脚本记录，不是网关字段；按此状态执行 401 / 402 等处理。 |
| _rawGatewayResponse | array / scalar / null | 仅当网关响应不是 JSON 对象时，由脚本保存原始 JSON 值；此时不能按下方 Temu 业务结构解释为成功。 |

#### Temu 顶层字段（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | Temu API 调用是否成功。 |
| errorCode | INTEGER | Temu 业务错误码。 |
| errorMsg | STRING | Temu 业务错误信息。 |
| result | OBJECT | 业务结果，完整嵌套字段如下。 |

#### result 嵌套字段

| 字段 | 类型 | 说明 |
|------|------|------|
| result.invoiceDetailInfoList[] | OBJECT[] | 发票明细列表。 |
| result.invoiceDetailInfoList[].orderMetaInfo | OBJECT | 订单元信息。 |
| result.invoiceDetailInfoList[].orderMetaInfo.isCustomerServiceChargeOrder | BOOLEAN | 是否为客服收费订单。 |
| result.invoiceDetailInfoList[].orderMetaInfo.parentAppealOrderSn | STRING | 父申诉订单号。 |
| result.invoiceDetailInfoList[].orderMetaInfo.originParentOrderTimeMillis | INTEGER | 原父订单时间（毫秒）。 |
| result.invoiceDetailInfoList[].orderMetaInfo.orderTimeMillis | INTEGER | 订单时间（毫秒）。 |
| result.invoiceDetailInfoList[].orderMetaInfo.tradeTransactionSn | STRING | 交易流水号。 |
| result.invoiceDetailInfoList[].orderMetaInfo.parentOrderSn | STRING | 父订单号。 |
| result.invoiceDetailInfoList[].orderMetaInfo.parentShippingTimeMillis | INTEGER | 父订单发货时间（毫秒）。 |
| result.invoiceDetailInfoList[].orderMetaInfo.refundTimeMillis | INTEGER | 退款时间（毫秒）。 |
| result.invoiceDetailInfoList[].orderMetaInfo.originParentOrderSn | STRING | 原父订单号。 |
| result.invoiceDetailInfoList[].orderMetaInfo.financeParentOrderSn | STRING | 财务父订单号。 |
| result.invoiceDetailInfoList[].platformInfo | OBJECT | 平台信息。 |
| result.invoiceDetailInfoList[].platformInfo.platformName | STRING | 平台名称。 |
| result.invoiceDetailInfoList[].platformInfo.platformAddress | STRING | 平台地址。 |
| result.invoiceDetailInfoList[].shippingFee | OBJECT | 运费。 |
| result.invoiceDetailInfoList[].shippingFee.shippingAmountWithTax | INTEGER | 含税运费。 |
| result.invoiceDetailInfoList[].shippingFee.shippingAmountExcludeTax | INTEGER | 不含税运费。 |
| result.invoiceDetailInfoList[].goodsInfoList[] | OBJECT[] | 商品信息列表。 |
| result.invoiceDetailInfoList[].goodsInfoList[].unitPriceWithVAT | INTEGER | 含 VAT 单价。 |
| result.invoiceDetailInfoList[].goodsInfoList[].skuSpec | STRING | SKU 规格。 |
| result.invoiceDetailInfoList[].goodsInfoList[].quantity | INTEGER | 数量。 |
| result.invoiceDetailInfoList[].goodsInfoList[].vatRateBase | INTEGER | VAT 税率基数。 |
| result.invoiceDetailInfoList[].goodsInfoList[].orderSn | STRING | 订单号。 |
| result.invoiceDetailInfoList[].goodsInfoList[].vatRate | INTEGER | VAT 税率。 |
| result.invoiceDetailInfoList[].goodsInfoList[].description | STRING | 描述。 |
| result.invoiceDetailInfoList[].goodsInfoList[].unitPriceExcludeVAT | INTEGER | 不含 VAT 单价。 |
| result.invoiceDetailInfoList[].goodsInfoList[].totalGoodsAmount | INTEGER | 商品总金额。 |
| result.invoiceDetailInfoList[].invoiceDetailType | INTEGER | 发票明细类型；枚举未定义，按实际返回展示。 |
| result.invoiceDetailInfoList[].shippingInfoList[] | OBJECT[] | 运费明细列表。 |
| result.invoiceDetailInfoList[].shippingInfoList[].unitPriceWithVAT | INTEGER | 含 VAT 单价。 |
| result.invoiceDetailInfoList[].shippingInfoList[].skuSpec | STRING | SKU 规格。 |
| result.invoiceDetailInfoList[].shippingInfoList[].quantity | INTEGER | 数量。 |
| result.invoiceDetailInfoList[].shippingInfoList[].vatRateBase | INTEGER | VAT 税率基数。 |
| result.invoiceDetailInfoList[].shippingInfoList[].orderSn | STRING | 订单号。 |
| result.invoiceDetailInfoList[].shippingInfoList[].vatRate | INTEGER | VAT 税率。 |
| result.invoiceDetailInfoList[].shippingInfoList[].description | STRING | 描述。 |
| result.invoiceDetailInfoList[].shippingInfoList[].unitPriceExcludeVAT | INTEGER | 不含 VAT 单价。 |
| result.invoiceDetailInfoList[].shippingInfoList[].totalGoodsAmount | INTEGER | 商品总金额。 |
| result.invoiceDetailInfoList[].invoiceType | INTEGER | 发票类型；枚举未定义，按实际返回展示。 |
| result.invoiceDetailInfoList[].currency | STRING | 币种。 |
| result.invoiceDetailInfoList[].promotionInfo | OBJECT | 优惠信息。 |
| result.invoiceDetailInfoList[].promotionInfo.promotionAmountExcludeTax | INTEGER | 不含税优惠金额。 |
| result.invoiceDetailInfoList[].promotionInfo.promotionAmountWithTax | INTEGER | 含税优惠金额。 |
| result.invoiceDetailInfoList[].addOrderInfoList[] | OBJECT[] | 附加订单信息列表。 |
| result.invoiceDetailInfoList[].addOrderInfoList[].amountWithTax | INTEGER | 含税金额。 |
| result.invoiceDetailInfoList[].addOrderInfoList[].amountExcludeTax | INTEGER | 不含税金额。 |
| result.invoiceDetailInfoList[].addOrderInfoList[].addOrderDetailType | INTEGER | 附加订单明细类型；枚举未定义，按实际返回展示。 |

金额和税率字段为 INTEGER；金额单位、税率缩放规则及类型枚举未定义，不自行除以 100 或补造含义。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先按公共规则判断网关，再检查网关 code（1002 / 1003）；其后解析 body，结合 Temu success / errorCode / errorMsg / result 判断业务结果。成功解析 JSON 本身不代表业务成功。

本接口专属 errorCode 未定义；按实际返回的 errorCode 和 errorMsg 解释结果，不补造错误码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.pay.tax.invoice.detail.query",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789"
    }
  }
}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-tax-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
