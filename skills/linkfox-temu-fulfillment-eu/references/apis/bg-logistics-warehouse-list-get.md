# Temu 欧洲站 店铺仓库列表 接口说明

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

## 接口：店铺仓库列表（bg.logistics.warehouse.list.get）

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

本操作的 `type` 固定为 `bg.logistics.warehouse.list.get`。脚本：`scripts/eu_buy_shipping_logistics_warehouse_list_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（获取店铺仓库信息；购标前筛选支持 Temu 面单的仓库、取 `warehouseId` / `selfShippingWarehouseId` 等）。

> 下游 **`linkfox-temu-fulfillment-eu`** 的 `bg.logistics.shipment.v2.confirm` 等接口中的 **`selfShippingWarehouseId`** 可来自本接口返回的 **`warehouseId`**。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| returnEnableBuyShippingLabelOnly | BOOLEAN | 否 | 是否仅返回支持购买 Temu 物流面单（Buy Shipping Label）的仓库，见下表 |

##### `returnEnableBuyShippingLabelOnly`

| 值 / 行为 | 说明 |
|-----------|------|
| `true` | Only warehouses that support purchasing Temu shipping labels will be returned（仅返回支持购买 Temu 物流面单的仓库） |
| `false` | All warehouses will be returned (regardless of Temu shipping label support)（返回全部仓库，不论是否支持 Temu 面单） |
| 不传（默认） | Default behavior: all warehouses will be returned (same as `false`)（默认与 `false` 相同，返回全部仓库） |

> 官方表将顶层 **`request`** 标为选填（False）；筛选购标仓库时建议显式传 **`returnEnableBuyShippingLabelOnly: true`**。

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

#### 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| warehouseList | OBJECT[] | 店铺仓库列表 |

##### `warehouseList[]` 元素字段

> 下列字段来自 Partner **响应示例** 与接口结构；若 Partner 在线文档 响应表有补充说明，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| defaultWarehouse | BOOLEAN | 是否为默认仓库 |
| pushOrderToOpenPlatform | BOOLEAN | 是否将订单推送到开放平台 |
| warehouseId | STRING | Warehouse ID（仓库 ID；自发货确认等接口中的 **`selfShippingWarehouseId`** 通常使用此值） |
| cooperativeWarehouseAuthorizationStatus | BOOLEAN | 合作仓授权状态 |
| warehouseBrand | STRING | Warehouse brand（仓库品牌/品牌名） |
| supportsUspsGroundAdvantage | BOOLEAN | 是否支持 USPS Ground Advantage |
| regionId1 | INTEGER | Region ID（区域 ID，一级区域编码） |
| warehouseName | STRING | Warehouse name（仓库名称） |
| warehouseManagementType | INTEGER | Warehouse management type（仓库管理类型；具体枚举以 Partner 文档为准） |
| enableBuyShippingLabel | BOOLEAN | 是否支持购买 Temu 物流面单（Buy Shipping Label）；与入参 **`returnEnableBuyShippingLabelOnly=true`** 筛选逻辑相关 |

> 调用成功时先判断 **`response.success === true`**，再遍历 **`result.warehouseList`**。购标流程可优先选择 **`enableBuyShippingLabel === true`** 的仓库。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

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
  "type": "bg.logistics.warehouse.list.get",
  "params": {
    "request": {
      "returnEnableBuyShippingLabelOnly": true
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
