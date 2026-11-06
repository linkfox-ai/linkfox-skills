# 父售后单详情 接口说明

返回 [接口总览](../api.md)；Partner 来源及文档菜单见 [目录](../partner-global-catalog.md)。

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


## 接口：父售后单详情（temu.aftersales.parentaftersales.detail.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| site | string | 是 | Global 专用脚本默认 `global`；通用脚本显式提供。兼容值 `cn` / `partner` / `us` / `global` / `eu`，小写。 |
| managementType | string | 是 | Global 专用脚本默认 `semi-managed`；兼容 `full-managed` / `semi-managed`，小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接请求网关时必填，`storeKey` 由脚本本地解析为此字段。 |
| storeKey | string | 与 accessToken 二选一 | 仅脚本参数，本地 Token 存储中的店铺键，不发给网关。 |
| tokenPurpose | string | 否 | 仅脚本选 Token 用途；Global 默认 `order-shipping`，不发给网关。用途必须与店铺授权一致。 |
| type | string | 是 | 本接口固定为 `temu.aftersales.parentaftersales.detail.get`；专用脚本自动设置，通用代理要求显式提供。 |
| params | object | 否 | 业务参数，建议按下表放在 `params.request`。 |

#### 脚本鉴权与选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，按该顺序优先于环境变量；不发入业务 Body。 |
| --inline | CLI flag | 否 | 强制完整打印；仍保存响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存；封装调用 `call_api.run` 时始终追加，不读写响应缓存。 |

补充运行约定见 [接口总览](../api.md#脚本运行约定)。Global 专用脚本支持顶层业务字段或 `params` 对象，存在对象 `params` 时优先使用；显式 `request` 按原层级转发。多站点 `temu_proxy.py` 仅使用对象 `params`，不把顶层业务字段自动并入。官方将 `request` 标为选填，内部必填项仍须提供；Partner 示例顶层字段经网关调用时建议放入 `params.request`。

#### `params`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务请求对象；位于网关 params 下，内部必填项仍须提供。 |

#### `params.request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | 父订单号 |
| parentAfterSalesSn | STRING | **是** | 父售后单号 |

### 响应结构

#### LinkFox 网关与脚本字段

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断。 |
| errmsg | string | 若返回，为网关消息。 |
| body | string | Temu 原始 JSON 字符串；代理脚本解析后增加 `temuBody`，同时保留原始 `body` 字符串。 |
| code | integer | 网关兼容错误码：`1002` 参数或 Token 无效，`1003` 转发失败。 |
| temuBody | object / array / scalar / null | 仅代理脚本在 `body` 可解析为 JSON 时增加；解析失败保留原始 `body`。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态；连接失败为 null。 |

Temu 业务数据可能位于解析后根级或 `response` 内；下表保留 Partner 字段层级。不能把 HTTP 请求完成等同于售后业务成功。

#### Temu 响应包装

| 字段 | 类型 | 说明 |
|---|---|---|
| response | OBJECT | Partner 文档的业务响应包装；实返也可能直接使用根对象。下列字段位于此对象内或解析后根级。 |

#### Temu 顶层字段（`response` 内或解析后根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果对象（见下表） |

#### `result` 业务字段

| 参数 | 类型 | 说明 |
|------|------|------|
| parentAfterSalesSn | STRING | 父售后单号 |
| availableOperateList | INTEGER[] | 卖家可执行操作码列表 |
| createAtMillis | LONG | 创建时间，毫秒 |
| parentAfterSalesStatus | INTEGER | 父售后单状态码 |
| refundSummary | OBJECT | 退款金额汇总 |
| parentOrderSn | STRING | 父订单号 |
| lastUpdateAtMillis | LONG | 最后更新时间，毫秒 |
| afterSalesType | INTEGER | 售后类型 |
| afterSalesList | OBJECT[] | 子售后行列表 |

#### `result.refundSummary` 内金额对象

各子字段均为 **OBJECT**，结构相同：

| 参数 | 类型 | 说明 |
|------|------|------|
| currency | STRING | 币种 |
| amount | NUMBER | 金额 |

| 子字段 | 类型 | 说明 |
|---|---|---|
| discountFromSellerRefund | OBJECT | 卖家侧优惠退款 |
| discountFromTEMURefund | OBJECT | 平台侧优惠退款 |
| buyerTotalRefund | OBJECT | 买家总退款 |
| shippingAmountRefundTaxExcl | OBJECT | 运费退款，不含税 |
| taxTotalRefund | OBJECT | 税费退款合计 |
| retailPriceRefundTaxExcl | OBJECT | 零售价退款，不含税 |

#### `result.afterSalesList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| applyAfterSalesGoodsNumber | INTEGER | 申请售后商品数量 |
| afterSalesSn | STRING | 子售后单号 |
| orderSn | STRING | 子订单号 |
| applyRefundAmount | OBJECT | 申请退款金额，`currency` + `amount` |
| afterSalesReasonDesc | STRING | 售后原因描述 |
| afterSalesGoodsInfo | OBJECT | 售后商品信息 |
| afterSalesReasonCode | INTEGER | 售后原因码 |
| buyerComment | STRING | 买家留言 |
| afterSalesStatus | INTEGER | 子售后状态码 |

#### `result.afterSalesList[].afterSalesGoodsInfo`

| 参数 | 类型 | 说明 |
|------|------|------|
| productSkuId | LONG | 商品 SKU ID |
| goodsId | LONG | 商品 ID |
| skuId | LONG | SKU ID |
| productList | OBJECT[] | 商品列表，元素含 `productSkuId`、`extCode` |

#### `result.afterSalesList[].afterSalesGoodsInfo.productList[]`

| 字段 | 类型 | 说明 |
|---|---|---|
| productSkuId | LONG | 商品 SKU ID。 |
| extCode | STRING | 商家外部编码。 |

#### `result.afterSalesList[].applyRefundAmount`

| 字段 | 类型 | 说明 |
|---|---|---|
| currency | STRING | 币种。 |
| amount | NUMBER | 申请退款金额。 |

各退款汇总子字段均为 OBJECT，其币种和金额定义见上方金额表。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关兼容字段 `code=1002` 表示参数或 LinkFox Token 无效，`1003` 表示转发失败；先排查 Token、用途和 IP 白名单。
- 在网关正常响应基础上解析 `body`，再根据 Temu `success`、`errorCode` 和 `errorMsg` 判断业务结果；`success=false` 不能认定为业务成功。

| errorCode | errorMsg（接口原值） | 处理建议 |
|-----------|----------|----------------------|
| 130010000 | system error | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 130010005 | operate forbid | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 130010001 | The parameter is illegal. Please check if the input parameter meets the regulations. | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 130010002 | The order has been fully shipped. | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.aftersales.parentaftersales.detail.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-001",
      "parentAfterSalesSn": "PAS-001"
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
  "skillName": "linkfox-temu-returns-refunds-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
