# 创建 Scan Form 接口说明

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

## 接口：创建 Scan Form（temu.logistics.scanform.create）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=temu.logistics.scanform.create`；**对应脚本**：`scripts/us_buy_shipping_logistics_scanform_create.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=729bda2db47944d98b3bf5f100dc9e2f&sub_menu_code=f70e104a1e114ce4a16bc17fcd7996fb

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

（卖家在录入**包裹号列表**后，按平台校验规则**创建 Scan Form（物流扫描单）**；常用于 **USPS** 等承运商的 **manifestation**，以便正常打印面单或交运。）

> **前置依赖：**
> - **`packageSnList`** 中的包裹须已成功 **Buy-Shipping 购标**（错误码 **120016055**）。
> - 仅支持 **USPS** 物流（**120016053**）；目的地区须为 **美国** 且一致（**120016059** / **120016051**）。
> - **`warehouseId`**、**`shipCompanyId`** 须与所选包裹一致；若不一致，应重新调用 [**`temu.logistics.candidate.scanform.list.get`**](./temu-logistics-candidate-scanform-list-get.md) 获取可生成同一 Scan Form 的包裹列表（**120016060** / **120016061** / **120016062**）。
> - 合作仓履约包裹**无需**生成 Scan Form（**120016063**）。
> - 单次最多 **500** 个包裹（**120011067**）；生成同一 scanform 至少须包含平台要求的最少包裹数（**120011099**）。
> - 邮寄日期须在**当日**至**当日+7 天（不含第 7 天）**之间（**120016054**）。
> 购标与面单流程见 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)、[**`bg.logistics.shipment.document.get`**](./bg-logistics-shipment-document-get.md)。Scan Form 专项 skill：**`linkfox-temu-fulfillment-us`**。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | **是** | package number list（待纳入同一 Scan Form 的包裹号列表；须满足仓库、承运商、目的地、购标状态等一致性校验） |
| shipCompanyId | LONG | **是** | Ship company id（物流公司 ID；须与列表内包裹实际承运商一致，不一致时错误码 **120016060**） |
| warehouseId | STRING | **是** | Warehouse id（发货仓库 ID；须与列表内包裹仓库一致，不一致时错误码 **120016061**） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`packageSnList`**、**`shipCompanyId`**、**`warehouseId`** 均为必填。Partner **Request Example** CURL 将业务字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`** 下（亦可与 `extract_business_params` 一致放在 `params` 顶层，由网关转发）。

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

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

#### 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | Whether it was successful or not（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | Error code（错误码） |
| errorMsg | STRING | Error message（错误信息） |
| result | OBJECT | Specific information（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| scanFormInfoList | OBJECT[] | List of created scan form information（本次创建的 Scan Form 信息列表；一次请求可能因分组规则返回多条，每条对应一个 **`scanFormSn`** 及其关联包裹） |

##### `scanFormInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| scanFormSn | STRING | Scan Form serial number（Scan Form 编号；用于后续 [**`temu.logistics.scanform.document.get`**](./temu-logistics-scanform-document-get.md) 获取文档 URL、交运对账等） |
| packageSnList | STRING[] | Package number list（本 Scan Form 关联的包裹号列表；为请求 **`packageSnList`** 的子集或分组结果） |

> 调用成功时先判断 **`response.success === true`**，再读取 **`result.scanFormInfoList`**。若部分包裹未能纳入 Scan Form，平台可能通过错误码整单失败；已关联其他 Scan Form 的包裹见 **120016056**。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 120016063 | The selected packages {*} are fulfilled by a cooperative warehouse. No scan form needs to be generated. | 合作仓包裹无需 Scan Form |
| 120011099 | At least {*} packages must be included in order to generate the corresponding scanform. | 增加 **`packageSnList`** 数量至平台要求下限 |
| 120016062 | The current packages cannot generate the same scan form. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 重新调用 [**`temu.logistics.candidate.scanform.list.get`**](./temu-logistics-candidate-scanform-list-get.md) |
| 120016061 | The current packages have inconsistent warehouseId. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 统一 **`warehouseId`** 或按候选列表重选包裹 |
| 120016060 | The current packages have inconsistent shipCompanyID. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 统一 **`shipCompanyId`** 或按候选列表重选包裹 |
| 120016056 | The selected packages {*} have been associated with other scan forms. | 勿重复创建；查已有 Scan Form |
| 120016054 | The mailing date must be between the current date and current date + 7 days (exclusive).Please check packages {*} | 检查包裹邮寄日期窗口 |
| 120016055 | Shipping labels must be successfully bought for the packages.Please check packages {*} | 先完成购标 **`bg.logistics.shipment.create`** |
| 120016053 | Only USPS logistics is supported. Please check packages {*} | 仅 USPS 包裹可创建 Scan Form |
| 120016059 | The destination region must be U.S.. | 目的地须为美国且一致 |
| 120016051 | The destination region must be consistent. | 目的地须为美国且一致 |
| 120016052 | The {*} is invalid. Please check the request area or if the packageSn is nonexistent. | 核对 **`packageSn`**、站点与请求区域 |
| 120011067 | The selected packages exceed the maximum limit of 500. | 分批，每批 ≤500 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 包裹已取消，需重新履约 |
| 120011001 | System abnormality, please check the data and try again | 重试或修正参数 |
| 120011002 | Invalid request parameters. | 修正请求参数，继续调用遵守成本约束 |

- `bg.logistics.shipment.document.get` 返回 `120018012` 时，USPS 面单须先完成 manifestation，可结合本接口或卖家中心 Scan Form 处理。

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
  "type": "temu.logistics.scanform.create",
  "params": {
    "request": {
      "packageSnList": [
        "PKG-001",
        "PKG-002"
      ],
      "shipCompanyId": 123456789,
      "warehouseId": "WH-US-001"
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
