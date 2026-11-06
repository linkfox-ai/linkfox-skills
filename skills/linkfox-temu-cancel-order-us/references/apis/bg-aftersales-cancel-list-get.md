# 取消订单售后列表查询 接口说明

返回总览见 [../api.md](../api.md)，运行与授权约定见其“脚本运行约定”。

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

## 接口：取消订单售后列表查询（bg.aftersales.cancel.list.get）

查询买家取消申请及售后状态。

> Partner 文档：https://partner-us.temu.com/documentation（menu_code / sub_menu_code 尚未确认，以后台该接口页为准）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/openapi/router`；上游 `https://openapi-b-us.temu.com/openapi/router`，Body 的 `type` 固定为 `bg.aftersales.cancel.list.get`，不是 URL 路径。对应脚本：`scripts/us_cancel_aftersales_cancel_list_get.py`。

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 美国站为 `us`；美国站脚本默认 `us`，去首尾空白并转小写。 |
| managementType | string | 是 | `semi-managed` / `full-managed`；美国站脚本默认 `semi-managed`，去首尾空白并转小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用直接传入值，否则从本地读取后填入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键，不原样转发；与 site、managementType、tokenPurpose 一起选择令牌。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；美国站脚本在 storeKey 且未直接传 accessToken、未指定用途时默认使用该值。本字段用于本地令牌选择，不原样转发。 |
| type | string | 是 | 本接口的 Temu 操作名，见本节；专用脚本固定该值，不采用用户覆盖值。 |
| params | object | 否 | 业务参数；本技能取消操作使用 `params.request`。通用代理允许传其他已知操作的业务块，但不增加本技能接口定义。 |

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序取第一个非空值，优先于环境变量；仅供 LinkFox 用户鉴权，不转发为 Temu 业务字段。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 条件必需 | JSON 未提供 LinkFox 密钥时，按此顺序取值。 |
| --inline | CLI flag | 否 | 强制全量打印，完整响应仍落盘。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI 选项；业务封装每次调用 run 均强制附加，不读取或保存响应缓存。 |

#### params.request 业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| params.request | OBJECT | 否 | 官方 request 容器标注选填；若提供，下列内部必填字段仍须满足。 |
| params.request.pageSize | INTEGER | 否 | 分页条数，默认 10，最大 200。 |
| params.request.pageNo | INTEGER | 否 | 页码，默认 1。 |
| params.request.parentOrderSnList | STRING[] | 否 | 父订单号列表；留空不限制父订单范围；单次最多 200 条。 |
| params.request.parentAfterSalesSnList | STRING[] | 否 | 父售后单号列表；留空不限制父售后范围；单次最多 200 条。 |
| params.request.afterSalesStatusGroup | INTEGER | 否 | 取消售后状态组：8 待处理、9 已同意、10 已拒绝、11 已撤销。 |

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|---|---|---|
| _http_status | integer / null | 脚本附加的本地 HTTP 传输状态，连接失败为 null；用于判断公共 HTTP 规则，不是网关或 Temu 业务字段。大响应摘要前也单独输出该状态。 |
| errcode | integer / string / null | 网关状态按公共规则判断；不替代 Temu 业务状态。 |
| errmsg | string | 网关错误说明；有错误时保留实际消息。 |
| code | integer | 网关 code 错误码：1002 为参数或 Token 错误，1003 为转发失败；不得当成 Temu errorCode。 |
| body | string | Temu 原始 JSON 字符串；代理脚本尝试解析为 temuBody，原始 body 保留。 |
| temuBody | object / array / scalar / null | 代理脚本附加的解析结果，类型以实际 JSON 为准；body 为空或不是合法 JSON 时不附加。 |
| error | string | 脚本生成的连接错误或异常响应说明；出现时不能视为业务成功。 |
| gatewayResponse | 任意 JSON 类型 | 仅网关顶层返回非对象 JSON 时由脚本附加，完整保留异常原值；与正常响应的 body 不同。 |

#### Temu body / temuBody 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码。 |
| errorMsg | STRING | Temu 业务错误信息。 |
| result | OBJECT | 具体业务结果，见下方。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| result.total | LONG | 匹配记录总数。 |
| result.pageNumber | INTEGER | 当前结果页码；入参是 pageNo，勿混用。 |
| result.data | OBJECT[] | 本次返回的取消售后记录。 |
| result.data[].parentAfterSalesSn | STRING | 取消订单的父售后单号。 |
| result.data[].parentAfterSalesStatus | INTEGER | 父售后状态：1 买家申请退款待处理；4 退款已发起、系统处理中；5 退款已发放；6 买家撤销售后；7 售后被拒绝；9 退款已发起、系统处理中。与入参 afterSalesStatusGroup 不是同一枚举。 |
| result.data[].afterSalesInfoList | OBJECT[] | 取消订单售后信息列表。 |
| result.data[].afterSalesInfoList[].afterSalesSn | STRING | 售后单号。 |
| result.data[].afterSalesInfoList[].parentOrderSn | STRING | 父订单号。 |
| result.data[].afterSalesInfoList[].orderSn | STRING | 子订单号。 |
| result.data[].afterSalesInfoList[].productSkuId | LONG | 产品 SKU ID。 |
| result.data[].afterSalesInfoList[].applyGoodsNumber | LONG | 申请取消数量。 |
| result.data[].afterSalesInfoList[].goodsId | LONG | 商品 ID。 |
| result.data[].afterSalesInfoList[].productList | OBJECT[] | 产品信息列表。 |
| result.data[].afterSalesInfoList[].productList[].productSkuId | LONG | 产品 SKU ID。 |
| result.data[].afterSalesInfoList[].productList[].extCode | STRING | 商品外部编码。 |
| result.data[].afterSalesInfoList[].createAtMillis | LONG | 售后单创建时间，毫秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 为参数或 LinkFox Token 问题，`code=1003` 为转发失败；结合 Temu token、用途、IP 白名单和网络排查。
- 在网关响应正常且未报告上述网关错误后，再解析 body，结合 Temu `success`、`errorCode`、`errorMsg` 和 result 判断；Temu 失败不视为业务成功，保留原始消息。
- 先用 `linkfox-temu-order-us` 的订单列表/详情找 `pending_buyer_cancellation` 标签，再按 `parentOrderSnList` 拉取取消售后明细。查询为空不代表该订单已取消。

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
  "type": "bg.aftersales.cancel.list.get",
  "params": {
    "request": {
      "pageNo": 1,
      "pageSize": 20,
      "afterSalesStatusGroup": 8,
      "parentOrderSnList": [
        "PO-123456789"
      ]
    }
  }
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-cancel-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
