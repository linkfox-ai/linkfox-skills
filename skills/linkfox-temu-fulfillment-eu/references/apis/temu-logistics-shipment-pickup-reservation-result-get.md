# Temu 欧洲站 查询上门揽收预约结果 接口说明

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

## 接口：查询上门揽收预约结果（temu.logistics.shipment.pickup.reservation.result.get）

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

本操作的 `type` 固定为 `temu.logistics.shipment.pickup.reservation.result.get`。脚本：`scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_result_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（查询**上门揽收预约**的异步处理结果。传入 **`packageSnList`** 后，返回各包裹对应的 **`reservationSn`**、**`reservationStatus`** 及该预约下包含的全部 **`packageSnList`**；多个包裹合并为同一预约时，响应会返回该 **`reservationSn`** 下的全部包裹。）

> **前置依赖：** 须先调用 [**`temu.logistics.shipment.pickup.reservation.create`**](./temu-logistics-shipment-pickup-reservation-create.md) 提交预约；本接口用于异步查询预约是否成功及 **`reservationSn`**。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | **是** | packageSn list, maximum 50（需要查询预约结果的**包裹号列表**，**单次最多 50 个**；通常传入 [**pickup.reservation.create**](./temu-logistics-shipment-pickup-reservation-create.md) 时使用的 **`packageSnList`**） |

> 官方请求表将顶层 **`request`** 标为选填（False），但 **`packageSnList`** 为必填（True）。Partner **请求示例** CURL 将 **`packageSnList`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.packageSnList`**。

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

Partner **响应** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **响应表 + 响应示例** 全部展开。

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
| reservationResultList | OBJECT[] | Reservation result list（按请求 **`packageSnList`** 返回的预约结果列表；同一 **`reservationSn`** 下可能包含多个包裹） |

##### `reservationResultList[]` 元素字段

> Partner **响应** 表中 **`result`** 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **响应示例**，说明结合接口说明 整理。若 Partner 在线文档 **Expand** 后对 **`reservationStatus`** 有枚举说明，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| reservationSn | STRING | Reservation serial number（预约单号/预约序列号；[**pickup.reservation.create**](./temu-logistics-shipment-pickup-reservation-create.md) 合并预约后生成的唯一标识） |
| packageSnList | STRING[] | Package SN list under this reservation（该 **`reservationSn`** 下包含的全部包裹号；当多个包裹对应同一预约时，此处返回该预约下的**所有**包裹，而不仅是请求中的单个 **`packageSn`**） |
| reservationStatus | INTEGER | Reservation status（预约状态；响应示例 为 **`1`**；具体枚举含义以 Partner 在线 响应表为准，可轮询本接口直至预约处理完成） |

> 调用成功时先判断 **`success === true`**，再遍历 **`result.reservationResultList`**，按 **`packageSn`** 匹配条目，查看 **`reservationStatus`** 与 **`reservationSn`**。若多个包裹共享同一 **`reservationSn`**，**`packageSnList`** 会列出该预约下的全部包裹。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120011002 | Invalid request parameters. | 检查 **`packageSnList`** 非空且格式正确 |

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
  "type": "temu.logistics.shipment.pickup.reservation.result.get",
  "params": {
    "request": {
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
