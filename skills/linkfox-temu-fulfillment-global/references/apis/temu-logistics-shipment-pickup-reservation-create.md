# 预约上门揽收 接口说明

[接口导航与运行约定](../api.md)

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

### 使用限制

（卖家为已购标包裹**预约上门揽收**；符合合并条件的多个包裹将合并为同一预约（**`reservationSn`**）。**预约结果须异步查询** [**`temu.logistics.shipment.pickup.reservation.result.get`**](./temu-logistics-shipment-pickup-reservation-result-get.md)。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：**  
> - **`packageSnList`** 来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)（购标成功）。  
> - **`pickupStartTime`** / **`pickupEndTime`** 宜来自 [**`bg.logistics.shippingservices.get`**](./bg-logistics-shippingservices-get.md) 返回的 **`availablePickupTimeSlotList`**（错误码 **120019025**）。  
> - 单次请求的 **`packageSnList`** 须来自**同一渠道、同一仓库**（**120019002**），且**最多 50** 个包裹（**120019030**）。

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能为 `global`；Global 业务脚本默认此值，不能因上游主机相同而改用 US/EU 店铺令牌。 |
| managementType | string | 是 | 本技能业务为 `semi-managed`，Global 业务脚本默认此值。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；HTTP 请求必须携带。脚本可从本地 storeKey 解析后填入。 |
| storeKey | string | 仅脚本，与 accessToken 二选一 | 本地令牌键；脚本按 site、managementType、tokenPurpose 解析，不将此键发送给网关。 |
| tokenPurpose | string | 否，仅脚本 | 本技能默认 `order-shipping`，用于选择本地令牌，不进入网关 Body。 |
| type | string | 是 | 本接口的操作标识，见下方。专用脚本固定该值，通用代理须传入。 |
| params | object | 否 | 原样转发的业务参数；本接口字段见下方。 |
| params.request | OBJECT | 否（官方顶层） | Temu Request 表标为选填；包含必填子字段或接口要求时须提供完整对象。 |

#### 脚本 JSON 与 CLI

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥兼容别名，按此顺序优先于环境变量；仅用于请求头，不作为业务参数。 |
| params | object | 否 | 显式提供对象时优先转发该对象；否则 Global 脚本将非保留顶层字段作为 params，包括 request。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终附加；不读取或写入响应缓存。 |

保留键为 token、linkfoxToken、linkfox_token、accessToken、storeKey、site、managementType、tokenPurpose、type、params。通用入口 `temu_proxy.py` 只接受显式 params 对象；Global 入口兼容顶层业务字段。认证、本地令牌与输出约定见 [运行约定](../api.md#运行约定)。

本接口 `type` 固定为 `temu.logistics.shipment.pickup.reservation.create`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── pickupStartTime (LONG, 必填)
    ├── pickupEndTime (LONG, 必填)
    └── packageSnList[] (STRING[], 必填，最多 50)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pickupStartTime | LONG | **是** | The start time for scheduling pickup, with a timestamp of seconds（预约上门揽收**开始时间**，**Unix 秒级时间戳**） |
| pickupEndTime | LONG | **是** | The end time for scheduling pickup, with a timestamp of seconds（预约上门揽收**结束时间**，**Unix 秒级时间戳**；须晚于 **`pickupStartTime`**） |
| packageSnList | STRING[] | **是** | packageSn list, maximum 50（需要预约揽收的**包裹号列表**，**单次最多 50 个**；须为同一物流渠道、同一仓库下的包裹） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但上述三个字段均为必填。Partner **Request Example** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`** 下。

### 响应结构

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断，不能把 0 或 false 视为空。 |
| errmsg | string | 若返回，保留完整网关错误消息。 |
| code | integer | 网关错误码：1002 为参数或 LinkFox Token 无效，1003 为转发失败；不替代外层 HTTP 与 errcode 判断。 |
| body | string | 原始 Temu JSON 字符串，保留原值。 |
| temuBody | object / array / scalar | 脚本仅在非空 body 可解析为 JSON 时添加；不强制改写其结构，解析失败仍保留 body。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |

以下为 body 解析后的 Temu 业务结构；如存在 response 包装，读取其内对象，否则读取根对象。

| 字段 | 类型 | 说明 |
|------|------|------|
| response | OBJECT | Partner 表的 Temu 响应包装；实际响应可能直接使用根对象，不能假定每次都有此层。 |

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态。下列层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    └── pickupReservationList[] (OBJECT[])
        ├── pickupWarehouseId
        ├── packageSnList[] (STRING[])
        ├── pickupStartTime
        └── pickupEndTime
```

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

> 多包裹满足合并条件时将合并为单一预约（**`reservationSn`**）。同步响应中的 **`pickupReservationList`** 反映分组与时段；最终预约是否成功、`reservationSn`、失败原因等须调用 **`temu.logistics.shipment.pickup.reservation.result.get`** 查询（Partner 明确要求）。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息摘要 | 处理建议 |
|--------|----------------------|----------|
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
  "site": "global",
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
  "skillName": "linkfox-temu-fulfillment-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
