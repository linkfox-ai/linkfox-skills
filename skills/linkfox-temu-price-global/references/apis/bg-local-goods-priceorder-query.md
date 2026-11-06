# 定价单列表查询 接口说明

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

## 接口：定价单列表查询（bg.local.goods.priceorder.query）

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

上游统一资源 path 为 `/openapi/router`，通过 Body `type=bg.local.goods.priceorder.query` 区分操作；紫鸟转发路径为 `/temu-proxy/{site}/{managementType}`，不将 type 拼入 LinkFox URL。LinkFox 双头鉴权与脚本参数兼容见 [运行约定](../api.md#脚本运行约定)。

#### `params` 内业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务参数容器。 |
| request.page | INTEGER | 否 | 页码。 |
| request.size | INTEGER | 否 | 每页条数，必须小于 100。 |
| request.priceOrderType | INTEGER | 否 | 默认定价评估报价；1 定价评估报价，2 定价机会或改价报价。 |
| request.priceOrderSubType | INTEGER | 否 | 定价单子类型：2002 基础价上调邀请，2003 销量提升。 |
| request.goodsName | STRING | 否 | 按商品名称搜索。 |
| request.goodsId | STRING | 否 | 按商品 ID 搜索。 |
| request.priceOrderSnList | STRING[] | 否 | 定价单编号列表。 |
| request.orderBy | STRING | 否 | 排序字段：goods_create_time 商品创建时间；order_create_time 定价单创建时间（默认）。 |
| request.orderByType | INTEGER | 否 | 排序方向：0 DESC 降序（默认），1 ASC 升序。 |
| request.goodsCreateTimeFrom | LONG | 否 | 商品创建起始时间；时间单位未明确，不自行换算。 |
| request.goodsCreateTimeTo | LONG | 否 | 商品创建结束时间；时间单位未明确。 |
| request.priceOrderCreateTimeFrom | LONG | 否 | 定价单创建起始时间；时间单位未明确。 |
| request.priceOrderCreateTimeTo | LONG | 否 | 定价单创建结束时间；时间单位未明确。 |
| request.goodsIdList | STRING[] | 否 | 商品 ID 列表。 |
| request.status | INTEGER | 否 | 定价单状态；枚举未明确，按实际返回值核对。 |

#### 参数约束与使用限制

仅支持 Temu 白名单商家查询定价单 / 报价列表，非白名单店铺可能返回业务错误。与发品侧 `temu.goods.price.list.get`（入参 `productSkuIds`）区分，不混用。

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
| result.pageNum | INTEGER | 当前页码。 |
| result.total | LONG | 总记录数。 |
| result.priceAuditList | OBJECT[] | 定价单 / 报价列表。 |
| result.priceAuditList[].priceOrderId | LONG | 定价单 ID。 |
| result.priceAuditList[].goodsId | LONG | 商品 ID。 |
| result.priceAuditList[].pricingType | INTEGER | 0 定价评估报价，1 定价机会报价，2 改价报价；与入参 priceOrderType 枚举不同。 |
| result.priceAuditList[].specName | STRING[] | 规格名称列表。 |
| result.priceAuditList[].skuIdList | LONG[] | SKU ID 列表。 |
| result.priceAuditList[].status | INTEGER | 报价 / 定价单状态；枚举未明确，保留实际值，不推断审核结论。 |
| result.priceAuditList[].suggestSupplierPrice | OBJECT | 参考基础价 / 建议供货价，金额结构见下表。 |
| result.priceAuditList[].targetSupplierPrice | OBJECT | 目标新基础价，金额结构见下表。 |
| result.priceAuditList[].sourceSupplierPrice | OBJECT | 原供货价，金额结构见下表。 |
| result.priceAuditList[].supplierPrice | OBJECT | 最终基础价 / 供货价，金额结构见下表。 |
| result.priceAuditList[].reason | STRING | 拒绝原因。 |
| result.priceAuditList[].rejectTypeDesc | STRING | 拒绝类型描述。 |
| result.priceAuditList[].priceCommitId | LONG | 价格提交 ID。 |
| result.priceAuditList[].priceCommitVersion | INTEGER | 价格提交版本。 |

#### 四类价格对象的共同结构

| 字段 | 类型 | 说明 |
|---|---|---|
| amount | STRING | 金额。 |
| currency | STRING | 币种。 |

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
  "type": "bg.local.goods.priceorder.query",
  "params": {
    "request": {
      "page": 1,
      "size": 20,
      "priceOrderType": 1,
      "orderBy": "order_create_time",
      "orderByType": 0
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
