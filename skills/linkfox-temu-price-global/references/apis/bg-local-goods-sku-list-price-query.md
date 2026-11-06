# SKU 供货价列表查询 接口说明

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

## 接口：SKU 供货价列表查询（bg.local.goods.sku.list.price.query）

Partner 文档：<https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=a9bd154c38384f2c99e57c2ebe271299>（未提供子菜单编号时以后台对应接口页为准）。

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

上游统一资源 path 为 `/openapi/router`，通过 Body `type=bg.local.goods.sku.list.price.query` 区分操作；紫鸟转发路径为 `/temu-proxy/{site}/{managementType}`，不将 type 拼入 LinkFox URL。LinkFox 双头鉴权与脚本参数兼容见 [运行约定](../api.md#脚本运行约定)。

#### `params` 内业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 未明确；含必填子字段 | 业务参数容器；经 LinkFox 网关使用 params.request，脚本也接受顶层 request。 |
| request.language | STRING | 否 | 语言。 |
| request.querySupplierPriceBaseList | OBJECT[] | 是 | 供货价查询基础列表。 |
| request.querySupplierPriceBaseList[].goodsId | LONG | 是 | 商品 ID。 |
| request.querySupplierPriceBaseList[].skuIdList | LONG[] | 是 | SKU ID 列表。 |

#### 参数约束与使用限制

请求中的 goodsId、skuIdList 使用 LONG / LONG[]；响应中的 goodsId、skuId 使用 INTEGER，分别遵循下表类型，不相互替换。

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

以下响应明细按 Partner `Response Example` 展开；导出文档中的 `Response` 字段表多为折叠，不将示例视为完整字段定义，按实际返回核对。

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 当前请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码；与外层 errcode 分开判断，不套用外层响应码规则。 |
| errorMsg | STRING | Temu 错误信息。 |
| result | OBJECT | 具体业务结果。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| result.openapiGoodsSupplierPriceDTOList | OBJECT[] | 商品供货价列表。 |
| result.openapiGoodsSupplierPriceDTOList[].goodsId | INTEGER | 商品 ID，响应类型为 INTEGER。 |
| result.openapiGoodsSupplierPriceDTOList[].openapiSkuSupplierPriceDTOList | OBJECT[] | SKU 供货价列表。 |
| result.openapiGoodsSupplierPriceDTOList[].openapiSkuSupplierPriceDTOList[].skuId | INTEGER | SKU ID，响应类型为 INTEGER。 |
| result.openapiGoodsSupplierPriceDTOList[].openapiSkuSupplierPriceDTOList[].supplierPrice | OBJECT | 供货价。 |
| result.openapiGoodsSupplierPriceDTOList[].openapiSkuSupplierPriceDTOList[].supplierPrice.amount | STRING | 金额。 |
| result.openapiGoodsSupplierPriceDTOList[].openapiSkuSupplierPriceDTOList[].supplierPrice.currency | STRING | 币种。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，检查网关 `code`，再解析 `body`，根据 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；保留原错误，不将可解析的 body 当作成功。
- 网关 `code=1002` 时核对参数和 LinkFox Token；`code=1003` 时核对 Temu Token、权限白名单和网络。

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
  "type": "bg.local.goods.sku.list.price.query",
  "params": {
    "request": {
      "querySupplierPriceBaseList": [
        {
          "goodsId": 123456789,
          "skuIdList": [
            58224724203874
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
