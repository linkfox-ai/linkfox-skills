# 推荐基础价/供货价估算 接口说明

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

## 接口：推荐基础价/供货价估算（temu.local.goods.baseprice.recommend）

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

上游统一资源 path 为 `/openapi/router`，通过 Body `type=temu.local.goods.baseprice.recommend` 区分操作；紫鸟转发路径为 `/temu-proxy/{site}/{managementType}`，不将 type 拼入 LinkFox URL。LinkFox 双头鉴权与脚本参数兼容见 [运行约定](../api.md#脚本运行约定)。

#### `params` 内业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务参数容器。 |
| request.language | STRING | 否 | 语言。 |
| request.supplierPriceEstimateQry | OBJECT | 是 | 供货价估算信息。 |
| request.supplierPriceEstimateQry.trademarkInfo | OBJECT | 否 | 品牌信息；提供后有助于估算更准确的价格。 |
| request.supplierPriceEstimateQry.trademarkInfo.brandId | LONG | 否 | 品牌 ID。 |
| request.supplierPriceEstimateQry.trademarkInfo.trademarkId | LONG | 否 | 商标 ID。 |
| request.supplierPriceEstimateQry.goodsBasicInfo | OBJECT | 是 | 商品基础信息。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.catId | LONG | 是 | 商品类目 ID，必须为与 `category_version` 指定类目树类型对应的叶子类目。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.taxCode | STRING | 否 | 商品税码。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.costTemplateId | STRING | 否 | 可用配送配置 ID，以逗号分隔；卖家按业务需要创建配置，发品创建报价时选择，平台据此取得有效配送选项。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList | OBJECT[] | 是 | 按 SKU / 规格提供的估算信息。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].specIdList | LONG[] | 是 | 规格 ID 列表。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo | OBJECT | 是 | 其他平台售价。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo.amount | STRING | 否 | 其他平台售价金额。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo.currency | STRING | 否 | 币种代码。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo | OBJECT | 否 | 商品尺寸与重量。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.weight | STRING | 否；巴西必填 | 商品重量。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.weightUnit | STRING | 否；巴西必填 | 美国为 `lb`，其他国家为 `kg`。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.length | STRING | 否；巴西必填 | 长度，保留两位小数。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.width | STRING | 否；巴西必填 | 宽度，保留两位小数。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.height | STRING | 否；巴西必填 | 高度，保留两位小数。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.dimensionUnit | STRING | 否；巴西必填 | 美国为 `inch`，其他国家为 `cm`。 |

#### 参数约束与使用限制

签名字段 `type`、`app_key`、`access_token`、`sign`、`timestamp` 由网关处理，不放入业务 `params`。尺寸和重量单位按目标国家选择：美国使用 `lb` / `inch`，其他国家使用 `kg` / `cm`；巴西必填要求见字段表，不能将美国单位推广到全球区。

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
| errorCode | INTEGER | Temu 业务错误码；与外层 errcode 分开判断，不套用外层响应码规则。 |
| errorMsg | STRING | Temu 错误信息。 |
| result | OBJECT | 具体业务结果。 |

`result` 返回推荐价/估算结果，具体子字段以 Partner 文档和实际返回为准，不预设字段结构。

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
  "type": "temu.local.goods.baseprice.recommend",
  "params": {
    "request": {
      "supplierPriceEstimateQry": {
        "goodsBasicInfo": {
          "catId": 12345
        },
        "supplierPriceEstimateSkuQryList": [
          {
            "specIdList": [
              9001
            ],
            "externPlatformPriceInfo": {
              "amount": "19.99",
              "currency": "USD"
            }
          }
        ]
      }
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
