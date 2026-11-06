# Temu 欧洲站 创建 Scan Form 接口说明

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

## 接口：创建 Scan Form（temu.logistics.scanform.create）

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

本操作的 `type` 固定为 `temu.logistics.scanform.create`。脚本：`scripts/eu_buy_shipping_logistics_scanform_create.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家在录入**包裹号列表**后，按平台校验规则**创建 Scan Form（物流扫描单）**；常用于 **USPS** 等承运商的 **manifestation**，以便正常打印面单或交运。）

> **前置依赖：**
> - **`packageSnList`** 中的包裹须已成功 **Buy-Shipping 购标**（错误码 **120016055**）。
> - 仅支持 **USPS** 物流（**120016053**）；目的地区须为 **美国** 且一致（**120016059** / **120016051**）。
> - **`warehouseId`**、**`shipCompanyId`** 须与所选包裹一致；若不一致，应重新调用 [**`temu.logistics.candidate.scanform.list.get`**](./temu-logistics-candidate-scanform-list-get.md) 获取可生成同一 Scan Form 的包裹列表（**120016060** / **120016061** / **120016062**）。
> - 合作仓履约包裹**无需**生成 Scan Form（**120016063**）。
> - 单次最多 **500** 个包裹（**120011067**）；生成同一 scanform 至少须包含平台要求的最少包裹数（**120011099**）。
> - 邮寄日期须在**当日**至**当日+7 天（不含第 7 天）**之间（**120016054**）。
> 购标与面单流程见 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)、[**`bg.logistics.shipment.document.get`**](./bg-logistics-shipment-document-get.md)。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | **是** | package number list（待纳入同一 Scan Form 的包裹号列表；须满足仓库、承运商、目的地、购标状态等一致性校验） |
| shipCompanyId | LONG | **是** | Ship company id（物流公司 ID；须与列表内包裹实际承运商一致，不一致时错误码 **120016060**） |
| warehouseId | STRING | **是** | Warehouse id（发货仓库 ID；须与列表内包裹仓库一致，不一致时错误码 **120016061**） |

> 官方请求表将顶层 **`request`** 标为选填（False），但 **`packageSnList`**、**`shipCompanyId`**、**`warehouseId`** 均为必填。Partner **请求示例** CURL 将业务字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`** 下（亦可与 `extract_business_params` 一致放在 `params` 顶层，由网关转发）。

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

Partner **响应** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **响应表 + 响应示例** 全部展开。

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

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

> [**`bg.logistics.shipment.document.get`**](./bg-logistics-shipment-document-get.md) 错误码 **120018012** 提示 USPS 面单须先完成 manifestation，可结合本接口或卖家中心 Scan Form 处理。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120016063 | The selected packages {*} are fulfilled by a cooperative warehouse. No scan form needs to be generated. | 合作仓包裹无需 Scan Form |
| 120011099 | At least {*} packages must be included in order to generate the corresponding scanform. | 增加 **`packageSnList`** 数量至平台要求下限 |
| 120016062 | The current packages cannot generate the same scan form. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 重新调用 [**`temu.logistics.candidate.scanform.list.get`**](./temu-logistics-candidate-scanform-list-get.md) |
| 120016061 | The current packages have inconsistent warehouseId. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 统一 **`warehouseId`** 或按候选列表重选包裹 |
| 120016060 | The current packages have inconsistent shipCompanyID. Please request the "temu.logistics.candidate.scanform.list.get" interface again to obtain a list of package numbers that can generate the same scan form. | 统一 **`shipCompanyId`** 或按候选列表重选包裹 |
| 120016056 | The selected packages {*} have been associated with other scan forms. | 勿重复创建；查已有 Scan Form |
| 120016054 | The mailing date must be between the current date and current date + 7 days (exclusive).Please check packages {*} | 检查包裹邮寄日期窗口 |
| 120016055 | Shipping labels must be successfully bought for the packages.Please check packages {*} | 先完成购标 **`bg.logistics.shipment.create`** |
| 120016053 | Only USPS logistics is supported. Please check packages {*} | 仅 USPS 包裹可创建 Scan Form |
| 120016059 / 120016051 | destination region must be U.S. / consistent | 目的地须为美国且一致 |
| 120016052 | The {*} is invalid. Please check the request area or if the packageSn is nonexistent. | 核对 **`packageSn`**、站点与请求区域 |
| 120011067 | The selected packages exceed the maximum limit of 500. | 分批，每批 ≤500 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 包裹已取消，需重新履约 |
| 120011001 / 120011002 | System abnormality / Invalid request parameters | 重试或修正参数 |
| 120016059 | The destination region must be U.S.. |  |
| 120016051 | The destination region must be consistent. |  |
| 120011001 | System abnormality, please check the data and try again |  |
| 120011002 | Invalid request parameters. |  |

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
