# 查询未发货包裹 接口说明

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

## 接口：查询未发货包裹（bg.order.unshipped.package.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.order.unshipped.package.get`；**对应脚本**：`scripts/us_buy_shipping_order_unshipped_package_get.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=746951536ea1455faaf17ae9d60e5b34&sub_menu_code=5798cc84b38e4ca59bb60895d66630c9

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是；美国站脚本默认 | `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，本技能业务使用美国站。 |
| managementType | string | 是；美国站脚本默认 | `semi-managed`；通用脚本还兼容 `full-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；显式传入时优先于本地存储。 |
| storeKey | string | 与 accessToken 二选一 | 脚本按店铺、站点、托管类型和用途从本地令牌库读取，不发送给网关。 |
| tokenPurpose | string | 否 | 美国站脚本本地选令牌默认 `order-shipping`；通用脚本默认 `default`。此字段不进入实际网关 Body。 |
| type | string | 是；专用脚本固定 | 本节列出的 Temu 操作标识；上游路径为 `https://openapi-b-us.temu.com/openapi/router`，通过 type 区分操作，没有 developerProxy.path 字段。 |
| params | object | 否 | 业务参数；有显式对象时原样转发，否则美国站脚本将非保留顶层字段收集为 params。 |
| params.request | OBJECT | 否（Partner 表） | 本接口业务对象；子字段必填与实际使用要求见下文，不因外层选填而省略必要内容。专用脚本也接受顶层 request 并收进 params。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，按列出顺序优先于环境变量；只用于请求头，不进入业务参数。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 保留可传选项；业务封装内部始终禁用缓存，既不读也不写响应缓存。 |

美国站默认值、兼容认证头、参数提取和输出约定详见 [运行约定](../api.md#运行约定)。以下 Partner 字段表的路径均相对于 `params.request`；响应子表路径相对于解析后的 Temu 对象。

#### 业务说明与前置限制

> **关联能力：** 购标后包裹号来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)；订单号来自 **`linkfox-temu-order-us`**；确认发货见 [**`bg.logistics.shipped.package.confirm`**](./bg-logistics-shipped-package-confirm.md)。

（卖家查询经 **Temu 集成物流** 已成功履约、但尚未完成发货确认的**未发货包裹**信息，含运单、承运商及包裹内可发/已取消订单行。）

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNumber | INTEGER | **是** | Page number（页码，从 **1** 起） |
| pageSize | INTEGER | **是** | Page size（每页条数） |
| parentOrderSnList | STRING[] | 否 | Parent order number list（父订单号列表；按父订单筛选未发货包裹） |
| orderSnList | STRING[] | 否 | Order number list（子订单号 / 订单号列表；按子订单筛选未发货包裹） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`pageNumber`**、**`pageSize`** 为必填。筛选时至少可传 **`parentOrderSnList`** 和/或 **`orderSnList`** 缩小范围；均不传时按分页返回店铺下符合条件的未发货包裹（以 Partner 与账号权限为准）。
> Partner **Request Example** CURL 将字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`**（与 Request 表一致）。

### 响应结构

#### LinkFox 外层与脚本解析字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer / null | 脚本本地诊断字段，记录本次真实 HTTP 状态；连接失败时为 null，不是网关保证字段。先按此判断 HTTP 结果，401/402 转入 onboarding 引导，不以正文中的成功字段覆盖。 |
| _raw_response | 以实际响应为准 | 仅当响应根不是对象，或上游已有同名 _http_status 时，脚本将完整原响应放在此字段，并在外层记录真实状态；此时从原响应读取业务内容。 |
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断；不将 `0` 或 `false` 当成空。 |
| errmsg | string | 若返回，网关消息或错误说明。 |
| code | integer | 网关业务错误码：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；不能据 HTTP 成功推断履约成功。 |
| body | string | Temu 原始 JSON 字符串，保留原值。 |
| temuBody | object / array / scalar | 脚本对可解析的非空 body 增加的解析结果；解析失败时不生成此字段，仍保留原始 body。 |

以下为 Temu `body` 解析后的结构；Partner 表中的 `response` 可能是结构标注，实际响应也可能直接以 success 等字段为根，不强行增删层级。

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **Response 表 + Response Example** 全部展开。

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| totalItemNum | INTEGER | Total item count（符合查询条件的未发货包裹总条数，用于分页） |
| unshippedPackage | OBJECT[] | Unshipped package list（未发货包裹列表；经 Temu 集成物流已成功履约的包裹） |

##### `unshippedPackage[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号；与 **`bg.logistics.shipment.create`** 返回的 **`packageSnList`**、**`bg.logistics.shipment.result.get`** 等一致） |
| mainPackageSn | STRING | Main package SN（主包裹号；拆分子包裹时标识主包裹） |
| subPackageSnList | STRING[] | Sub-package SN list（子包裹号列表；一单多包裹/拆包场景） |
| subPackageType | STRING | Sub-package type（子包裹类型标识；具体枚举以 Partner 在线文档为准） |
| trackingNumber | STRING | Tracking number（物流运单号 / 跟踪号） |
| carrierId | INTEGER / LONG | Carrier ID（承运商 ID） |
| carrierName | STRING | Carrier name（承运商名称，展示用） |
| packageDetail | OBJECT | Package detail（包裹内订单行明细：可发货与已取消） |

###### `packageDetail` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shippableOrders | OBJECT[] | Shippable orders in this package（本包裹内**仍可发货**的订单商品行） |
| canceledOrders | OBJECT[] | Canceled orders in this package（本包裹内**已取消**、不可再发的订单商品行） |

###### `shippableOrders[]` / `canceledOrders[]` 元素字段

> 两类数组元素结构相同；**`canceledOrders`** 为购标后订单被取消等场景，**`shippableOrders`** 为仍可继续发货确认的行。

| 参数 | 类型 | 说明 |
|------|------|------|
| semiUniqueId | STRING | Semi-unique ID（半托管订单行唯一标识；与 **`bg.logistics.shipment.result.get`** 的 **`orderSendInfoList[].semiUniqueId`** 等同系列字段） |
| quantity | INTEGER | Quantity（该行商品数量） |
| orderSn | STRING | Order number（子订单号 / 订单号） |
| parentOrderSn | STRING | Parent order number（父订单号） |
| mallId | INTEGER / LONG | Mall ID（店铺/商城 ID） |

> 调用成功时先判断 **`success === true`**，再根据 **`result.totalItemNum`** 与 **`pageNumber` / `pageSize`** 翻页；对每个 **`unshippedPackage`** 查看 **`trackingNumber`**、**`packageSn`** 及 **`packageDetail.shippableOrders`**，再调用 **`bg.logistics.shipped.package.confirm`** 等完成发货确认。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限 |
| 120011072 | The request area is incorrect... US / global | 美国站请求区域须为 US |
| 120012016 | The parentOrder or Order is invalid... | 核对 **`parentOrderSnList`** / **`orderSnList`** 与订单是否存在、父子关系是否匹配 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.unshipped.package.get",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 20,
      "parentOrderSnList": [
        "PO-20260101001"
      ],
      "orderSnList": [
        "O-20260101001-1"
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
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
