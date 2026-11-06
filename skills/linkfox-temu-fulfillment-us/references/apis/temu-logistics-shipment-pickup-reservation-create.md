# 预约上门揽收 接口说明

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

## 接口：预约上门揽收（temu.logistics.shipment.pickup.reservation.create）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=temu.logistics.shipment.pickup.reservation.create`；**对应脚本**：`scripts/us_buy_shipping_logistics_shipment_pickup_reservation_create.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=cf516cfc49364acba34be29c2600ec20&sub_menu_code=aff85d40b1364572a8383bcf5171f75b

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

（卖家为已购标包裹**预约上门揽收**；符合合并条件的多个包裹将合并为同一预约（**`reservationSn`**）。**预约结果须异步查询** [**`temu.logistics.shipment.pickup.reservation.result.get`**](./temu-logistics-shipment-pickup-reservation-result-get.md)。）

> **前置依赖：**
> - **`packageSnList`** 来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)（购标成功）。
> - **`pickupStartTime`** / **`pickupEndTime`** 宜来自 [**`bg.logistics.shippingservices.get`**](./bg-logistics-shippingservices-get.md) 返回的 **`availablePickupTimeSlotList`**（错误码 **120019025**）。
> - 单次请求的 **`packageSnList`** 须来自**同一渠道、同一仓库**（**120019002**），且**最多 50** 个包裹（**120019030**）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pickupStartTime | LONG | **是** | The start time for scheduling pickup, with a timestamp of seconds（预约上门揽收**开始时间**，**Unix 秒级时间戳**） |
| pickupEndTime | LONG | **是** | The end time for scheduling pickup, with a timestamp of seconds（预约上门揽收**结束时间**，**Unix 秒级时间戳**；须晚于 **`pickupStartTime`**） |
| packageSnList | STRING[] | **是** | packageSn list, maximum 50（需要预约揽收的**包裹号列表**，**单次最多 50 个**；须为同一物流渠道、同一仓库下的包裹） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但上述三个字段均为必填。Partner **Request Example** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`** 下。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态。下列层级按 **Response 表 + Response Example** 全部展开。

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
| pickupReservationList | OBJECT[] | Pickup reservation list（本次提交的揽收预约分组列表；符合合并条件的包裹可能合并为一组，对应一个 **`reservationSn`**，详见 Partner 说明与 **`temu.logistics.shipment.pickup.reservation.result.get`**） |

##### `pickupReservationList[]` 元素字段

> 下列字段来自 **Response Example**；若在线 Response 表有 **`reservationSn`** 等补充字段，以 Partner 在线文档为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| pickupWarehouseId | STRING | Pickup warehouse ID（揽收仓库 ID） |
| packageSnList | STRING[] | Package SN list（本预约分组内包含的包裹号列表） |
| pickupStartTime | LONG | Scheduled pickup start time（本组预约的揽收开始时间，Unix 秒级时间戳） |
| pickupEndTime | LONG | Scheduled pickup end time（本组预约的揽收结束时间，Unix 秒级时间戳） |

> 接口 Description 说明：多包裹满足合并条件时将合并为单一预约（**`reservationSn`**）。同步响应中的 **`pickupReservationList`** 反映分组与时段；**最终预约是否成功、`reservationSn`、失败原因等须调用 **`temu.logistics.shipment.pickup.reservation.result.get`** 查询（Partner 明确要求）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 120019030 | The number of packages must be less than {*} | **`packageSnList`** 不超过 **50** 个 |
| 120019009 | Invalid pickup reservation time. See pickupRules for valid options. | 按 **`pickupRules`** / 查价返回时段重选 |
| 120019025 | pickupStartTime or pickupEndTime invalid; get valid time slot from bg.logistics.shippingservices.get | 使用 [**shippingservices.get**](./bg-logistics-shippingservices-get.md) 的 **`availablePickupTimeSlotList`** |
| 120019002 | PackageSn doesn't match; same channel and same warehouse | 同一请求内包裹须同渠道、同仓 |
| 120019005 | PackageSn in packageSnList is invalid | 核对 **`packageSn`** 是否有效、已购标 |
| 120019006 | Pickup reservation of this package is ongoing | 勿重复预约 |
| 120019023 | Duplicated packageSn in one api call | 去重 **`packageSnList`** |
| 120019001 | Haven't support pickup reservation of this channel through open api yet | 该渠道暂不支持 OpenAPI 预约揽收 |
| 120011002 | Invalid request parameters. | 检查必填字段与时间戳 |

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
  "type": "temu.logistics.shipment.pickup.reservation.create",
  "params": {
    "request": {
      "pickupStartTime": 1717200000,
      "pickupEndTime": 1717203600,
      "packageSnList": [
        "PKG-001",
        "PKG-002"
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
