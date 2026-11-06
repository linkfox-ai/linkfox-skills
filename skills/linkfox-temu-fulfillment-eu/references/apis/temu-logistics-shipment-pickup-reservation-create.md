# Temu 欧洲站 预约上门揽收 接口说明

[接口导航](../api.md)；[授权与脚本兼容约定](../api.md#运行约定)。

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

> 官方：[Partner EU 文档](https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `eu`；必须匹配店铺令牌所属站点。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；合作仓仅支持半托管。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；与 LinkFox API Key 不同。脚本调用网关前解析本地选店并填入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库中的店铺键，指向 `~/.linkfox/temu-access-tokens.json`；当前脚本在本地读取并转换为 `accessToken`，不发送此字段。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；脚本用于本地令牌选择，不发送至网关。 |
| type | string | 是 | 当前操作的 Temu 接口标识，见本接口说明。 |
| params | object | 否 | Temu 业务参数；通常使用下方 `request` 对象。 |

本操作的 `type` 固定为 `temu.logistics.shipment.pickup.reservation.create`。脚本：`scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_create.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

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

> 官方请求表将顶层 **`request`** 标为选填（False），但上述三个字段均为必填。Partner **请求示例** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`** 下。

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回此字段，按公共规则判断，不将 `0` 或 `false` 视为空。 |
| errmsg | string | 若返回此字段，为网关消息；保留原文。 |
| body | string | Temu 原始 JSON 字符串；先判断网关状态，再解析业务内容。 |
| code | integer | 网关错误码：`1002` 为参数或 Token 无效，`1003` 为转发失败；不可当作 Temu 错误码。 |
| temuBody | object / array / scalar | 脚本在 `body` 可解析为 JSON 时增加的字段，完整保留原 `body`；不可解析时不增加。 |
| _http_status | integer / null | 仅脚本附加的本次 HTTP 状态码，不是网关字段；连接失败无 HTTP 响应时为 `null`，错误原因仍保留在 `error`。大响应摘要也展示该状态。 |

网关正常响应后，解析 `body`；若存在 `response` 包装则读取其业务对象。以下为 Temu 业务字段，不能替代外层 HTTP 与 `errcode` 判断。

Partner **响应** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态。下列层级按 **响应表 + 响应示例** 全部展开。

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

> 下列字段来自 **响应示例**；若在线 响应表有 **`reservationSn`** 等补充字段，以 Partner 在线文档为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| pickupWarehouseId | STRING | Pickup warehouse ID（揽收仓库 ID） |
| packageSnList | STRING[] | Package SN list（本预约分组内包含的包裹号列表） |
| pickupStartTime | LONG | Scheduled pickup start time（本组预约的揽收开始时间，Unix 秒级时间戳） |
| pickupEndTime | LONG | Scheduled pickup end time（本组预约的揽收结束时间，Unix 秒级时间戳） |

> 多包裹满足合并条件时将合并为单一预约（**`reservationSn`**）。同步响应中的 **`pickupReservationList`** 反映分组与时段；**最终预约是否成功、`reservationSn`、失败原因等须调用 **`temu.logistics.shipment.pickup.reservation.result.get`** 查询（Partner 明确要求）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
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
  -d '
{
  "site": "eu",
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
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
