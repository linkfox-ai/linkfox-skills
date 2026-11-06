# 批量修改 SKU 基础价 接口说明

网关与脚本运行约定见 [总览](../api.md)。

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

## 接口：批量修改 SKU 基础价（bg.local.goods.priceorder.change.sku.price）

Partner 文档：<https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a>（未提供子菜单编号时以后台对应接口页为准）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是；脚本有默认值 | `global`；通用多站点入口接受 `cn` / `partner` / `us` / `global` / `eu`，必须小写。 |
| managementType | string | 是；脚本有默认值 | `semi-managed`；通用入口兼容 `full-managed`，必须小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；业务脚本优先使用直接令牌，否则从本地 `storeKey` 读取后注入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；脚本通过 site、managementType、tokenPurpose 在 ~/.linkfox/temu-access-tokens.json 解析后只发送 accessToken。 |
| tokenPurpose | string | 否 | 建议 product-inventory；业务脚本用于本地令牌检索，不发送此字段。 |
| type | string | 是 | Temu 操作名称，取本接口标题中的值；专用脚本自动填入。 |
| params | object | 否 | 业务参数对象；本技能定价操作的业务块为 `params.request`。 |

上游统一资源 path 为 `/openapi/router`，通过 Body `type=bg.local.goods.priceorder.change.sku.price` 区分操作；紫鸟转发路径为 `/temu-proxy/{site}/{managementType}`，不将 type 拼入 LinkFox URL。LinkFox 双头鉴权与脚本参数兼容见 [运行约定](../api.md#脚本运行约定)。

#### `params` 内业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务参数容器。 |
| request.goodsId | LONG | 是 | 商品 ID。 |
| request.changeSkuPriceDTOList | OBJECT[] | 是 | 调价 SKU 信息及原因。 |
| request.changeSkuPriceDTOList[].reason | STRING | 否 | 调价原因。 |
| request.changeSkuPriceDTOList[].skuChangePriceBaseDTOList | OBJECT[] | 是 | SKU 信息列表。 |
| request.changeSkuPriceDTOList[].skuChangePriceBaseDTOList[].skuId | LONG | 是 | SKU ID。 |
| request.changeSkuPriceDTOList[].skuChangePriceBaseDTOList[].newSupplierPrice | OBJECT | 是 | 新基础价 / 供货价。 |
| request.changeSkuPriceDTOList[].skuChangePriceBaseDTOList[].newSupplierPrice.amount | STRING | 否 | 金额。 |
| request.changeSkuPriceDTOList[].skuChangePriceBaseDTOList[].newSupplierPrice.currency | STRING | 否 | 币种。 |
| request.rejectSkuPricing | BOOLEAN | 否 | 定价单处于等待商家确认时是否拒绝。 |

#### 参数约束与使用限制

仅支持 Temu 白名单商家。同一 goodsId 下可在一个 changeSkuPriceDTOList 项中放多个 SKU，也可按调价原因拆成多项。改价后通过定价单查询核对 priceAuditList 中的 supplierPrice；成功和失败列表来自本次返回，不为核对结果再次提交本写入接口。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码，按公共规则判断。 |
| errmsg | string | 网关错误说明。 |
| code | integer | 网关错误码：1002 参数或 Token 错误，1003 转发失败。 |
| body | string | Temu 原始 JSON 字符串；代理脚本保留原值并解析为 `temuBody`。 |
| temuBody | object / array / scalar | 脚本附加的解析结果；body 非 JSON 或为空时不添加，不代表业务成功。 |
| transportHttpStatus | integer / null | 业务适配层附加的 LinkFox HTTP 状态；连接失败为 null。 |

#### Temu `body` 解析后的字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 当前请求是否成功。 |
| errorCode | INTEGER | Temu 错误码；成功响应示例为 0，与外层 errcode 判断分开。 |
| errorMsg | STRING | Temu 错误信息。 |
| result | OBJECT | 具体业务结果。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| result.successSkuList | LONG[] | 调价成功的 SKU 列表。 |
| result.failedSkuList | LONG[] | 调价失败的 SKU 列表。 |
| result.failedSkuReasonMap | MAP | 调价失败原因映射。 |
| result.failedSkuReasonMap.$key | STRING | SKU ID 字符串（动态键）。 |
| result.failedSkuReasonMap.$value | STRING | 失败原因（动态键对应值）。 |
| result.successPriceOrderList | OBJECT[] | 成功请求调价的定价单列表。 |
| result.successPriceOrderList[].priceOrderSn | STRING | 定价单编号。 |
| result.successPriceOrderList[].skuIdList | LONG[] | 该定价单对应的 SKU 列表。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，检查网关 `code`，再解析 `body`，根据 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；保留原错误，不将可解析的 body 当作成功。
- 网关 `code=1002` 时核对参数和 LinkFox Token；`code=1003` 时核对 Temu Token、权限白名单和网络。
- 检查逐 SKU 成功、失败与失败原因，整体 success 不代表全部 SKU 调价成功；需要查询核对最终价格。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "<TEMU_ACCESS_TOKEN>",
  "type": "bg.local.goods.priceorder.change.sku.price",
  "params": {
    "request": {
      "goodsId": 123456,
      "changeSkuPriceDTOList": [
        {
          "skuChangePriceBaseDTOList": [
            {
              "skuId": 58224724203874,
              "newSupplierPrice": {
                "amount": "15.99",
                "currency": "USD"
              }
            }
          ]
        }
      ]
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
  "skillName": "linkfox-temu-price-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
