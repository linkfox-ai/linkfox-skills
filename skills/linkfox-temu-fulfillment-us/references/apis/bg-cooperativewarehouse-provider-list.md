# 合作仓服务商列表 接口说明

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

## 接口：合作仓服务商列表（bg.cooperativewarehouse.provider.list）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.cooperativewarehouse.provider.list`；**对应脚本**：`scripts/us_co_warehouse_cooperativewarehouse_provider_list.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=e77d444a60b540039bfa1fc64e3cada7

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是；美国站脚本默认 | `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，本技能业务使用美国站。 |
| managementType | string | 是；美国站脚本默认 | `semi-managed`；通用脚本还兼容 `full-managed`，合作仓业务仅支持半托管。 |
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

（查询当前店铺可用的**合作仓服务商**（Warehouse Provider）列表，包含服务商编码、品牌、支持的承运商、区域、客户编码及包裹配送类型等；**`permitsStatus`** 反映合作仓相关许可/授权状态。）

> **后续：** 授权绑定见 [**`bg.cooperativewarehouse.token.authorization`**](./bg-cooperativewarehouse-token-authorization.md)；履约提交见 [**`bg.cooperativewarehouse.fulfill.submit`**](./bg-cooperativewarehouse-fulfill-submit.md)；查询见 **`bg.cooperativewarehouse.fulfill.query`**（待接入）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| needAllPlatformProviders | BOOLEAN | 否 | needAllPlatformProviders（是否返回**全平台**合作仓服务商列表；Partner Request 表将该说明写在 Required 列。`true` 时通常返回平台侧全部可选服务商；`false` 或不传时返回与当前店铺/授权范围相关的服务商，以实际调通为准） |

> 官方 Request 表将 **`request`** 与 **`needAllPlatformProviders`** 均标为选填（False）。Partner **Request Example** CURL 将 **`needAllPlatformProviders`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.needAllPlatformProviders`**。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

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
| permitsStatus | INTEGER | Permits / authorization status（合作仓相关许可或授权状态；Response Example 为 **`1`**；具体枚举含义以 Partner 在线 Response 表为准，可结合后续 **`bg.cooperativewarehouse.token.authorization`** 判断店铺是否已完成服务商授权） |
| warehouseProviderList | OBJECT[] | Warehouse provider list（合作仓服务商列表） |

##### `warehouseProviderList[]` 元素字段

> Partner **Response** 表中 **`result`** 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **Response Example**，说明结合 Co-Warehouse 履约语义整理。若 Partner 在线文档 **Expand** 后有更完整枚举，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| warehouseProviderCode | STRING | Warehouse provider code（合作仓服务商编码；后续授权、履约接口中标识服务商） |
| warehouseProviderBrandName | STRING | Warehouse provider brand name（合作仓服务商品牌/展示名称） |
| supportNoCwCustomCode | INTEGER | Whether supports scenarios without cooperative warehouse custom code（是否支持无合作仓客户编码（cw custom code）的场景；Response Example 为 **`1`**，具体布尔语义以 Partner 为准） |
| cwCustomerCodeList | STRING[] | Cooperative warehouse customer code list（合作仓客户编码列表；绑定/授权后用于履约） |
| regionId | STRING[] | Region ID list（该服务商支持的发货/履约区域 ID 列表） |
| supportedPackageDeliveryType | INTEGER[] | Supported package delivery type list（支持的包裹配送类型列表；Response Example 为整数数组，具体类型枚举以 Partner 为准） |
| supportedShipCompany | OBJECT[] | Supported shipping company list（该合作仓服务商支持的物流公司/承运商列表） |

###### `warehouseProviderList[].supportedShipCompany[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shipCompanyId | INTEGER | Ship company ID（物流公司/承运商 ID） |
| shipCompanyName | STRING | Ship company name（物流公司/承运商名称） |

> 调用成功时先判断 **`success === true`**，再读 **`result.permitsStatus`** 与 **`warehouseProviderList`**。选定 **`warehouseProviderCode`** 后，通常继续调用 [**`bg.cooperativewarehouse.token.authorization`**](./bg-cooperativewarehouse-token-authorization.md) 完成授权，再使用 **`bg.cooperativewarehouse.fulfill.submit`** 等提交合作仓履约。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

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
  "type": "bg.cooperativewarehouse.provider.list",
  "params": {
    "request": {
      "needAllPlatformProviders": true
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
