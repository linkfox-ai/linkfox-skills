# Temu 欧洲站 查询 Scan Form 详情 接口说明

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

## 接口：查询 Scan Form 详情（temu.logistics.scanform.get）

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

本操作的 `type` 固定为 `temu.logistics.scanform.get`。脚本：`scripts/eu_buy_shipping_logistics_scanform_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家按分页与筛选条件查询 Scan Form（物流扫描单）的详情信息，例如创建状态等。）

> **关联能力：** 创建 Scan Form 见 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md)；获取 Scan Form 文档见 **`temu.logistics.scanform.document.get`**。购标与包裹号见 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNumber | INTEGER | **是** | Page number for pagination（分页页码） |
| pageSize | INTEGER | **是** | Page size for pagination, max is 10.（每页条数；**最大为 10**，超出将报错 **120016057**） |
| scanFormSnList | STRING[] | 否 | Scan form serial number list, the lists of the unique identification field when creating a scan form.（Scan Form 序列号列表；为创建 Scan Form 时返回的唯一标识字段列表，用于按单号筛选） |
| shipCompanyIdList | LONG[] | 否 | Ship company id list（物流公司 ID 列表；与购标/Scan Form 创建时的 **`shipCompanyId`** 对应） |
| warehouseIdList | STRING[] | 否 | Warehouse id list（仓库 ID 列表；来自 **`bg.logistics.warehouse.list.get`** 的 **`warehouseId`**） |
| scanFormCreateStatus | INTEGER | 否 | The status of scan form（Scan Form 创建/处理状态），见下表 |
| scanFormCreateTimeStart | INTEGER | 否 | Start time for querying scan form creating time with second-level timestamp.（查询 Scan Form **创建时间**的起始时间；**秒级 Unix 时间戳**） |
| scanFormCreateTimeEnd | INTEGER | 否 | End time for querying scan form creating time with second-level timestamp.（查询 Scan Form **创建时间**的结束时间；**秒级 Unix 时间戳**，应不早于 **`scanFormCreateTimeStart`**） |
| trackingNumberList | STRING[] | 否 | Tracking number list（运单号/跟踪号列表；按包裹运单号反查关联 Scan Form） |

##### `scanFormCreateStatus`

| 值 | 说明 |
|----|------|
| `1` | under creation（创建中） |
| `2` | successful（成功） |
| `3` | failed（失败） |

> 官方请求表将顶层 **`request`** 标为选填（False），但 **`pageNumber`**、**`pageSize`** 为必填。筛选字段可组合使用。Partner **请求示例** CURL 将业务字段写在 JSON 顶层，经 LinkFox 网关时建议放在 **`params.request`**。

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

Partner **响应** 表顶层为 **`response`** 对象；**`result`** 在表内标注为 **Specific information**。
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **响应表 + 响应示例** 全部展开。

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | Whether it was successful or not（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | Error code（错误码） |
| errorMsg | STRING | Error message（错误信息） |
| result | OBJECT | Specific information（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| total | INTEGER | Total count（符合当前筛选条件的 Scan Form 记录总条数，用于配合 **`pageNumber`** / **`pageSize`** 分页） |
| scanFormInfoList | OBJECT[] | Scan form information list（Scan Form 详情列表） |

##### `scanFormInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| scanFormSn | STRING | Scan form serial number, the unique identification field when creating a scan form（Scan Form 序列号；创建时的唯一标识，用于 [**`temu.logistics.scanform.document.get`**](./temu-logistics-scanform-document-get.md) 的 **`scanFormSn`**） |
| scanFormNumber | STRING | Scan form number（Scan Form 业务编号/承运商侧编号，Partner 示例为字符串） |
| scanFormCreateStatus | INTEGER | The status of scan form（Scan Form 状态），见下表（与入参 **`scanFormCreateStatus`** 枚举一致） |
| scanFormCreateTime | STRING | Scan form creating time（Scan Form 创建时间；Partner **响应示例** 为字符串，一般为时间戳字符串） |
| warehouseId | STRING | Warehouse id（发货仓库 ID） |
| shipCompanyId | INTEGER / LONG | Ship company id（物流公司 ID） |
| shippingCompanyName | STRING | Shipping company name（物流公司名称） |
| labelCount | INTEGER | Label count（该 Scan Form 关联的面单/标签数量） |
| failReason | STRING | Fail reason（失败原因；当 **`scanFormCreateStatus=3`** 时有值，可配合本接口排查 [**`temu.logistics.scanform.document.get`**](./temu-logistics-scanform-document-get.md) 报错 **120016058**） |
| scanFormPackageList | OBJECT[] | Package list included in this scan form（本 Scan Form 包含的包裹列表） |

###### `scanFormCreateStatus`（出参）

| 值 | 说明 |
|----|------|
| `1` | under creation（创建中） |
| `2` | successful（成功） |
| `3` | failed（失败） |

###### `scanFormPackageList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号；来自购标 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)） |
| trackingNumber | STRING | Tracking number（运单号/跟踪号） |

> 调用成功时先判断 **`success === true`**，再读取 **`result.total`** 与 **`scanFormInfoList`**。分页查询须配合 **`pageNumber`** / **`pageSize`**（**`pageSize` ≤ 10**）。状态为 **`2`** 时可调用 **`temu.logistics.scanform.document.get`** 获取文档 URL。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120016057 | The pageSize exceeds the maximum limit of 10. | 将 **`pageSize`** 调整为 **≤ 10** |
| 120011001 | System abnormality, please check the data and try again | 检查入参后重试；持续失败联系平台 |
| 120011002 | Invalid request parameters. | 核对 **`request`** 字段类型、必填项与时间窗 |

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
  "type": "temu.logistics.scanform.get",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 10,
      "scanFormSnList": [
        "SCANFORM-SN-001"
      ],
      "scanFormCreateStatus": 2,
      "warehouseIdList": [
        "WH-001"
      ],
      "shipCompanyIdList": [
        314439762
      ],
      "scanFormCreateTimeStart": 1717200000,
      "scanFormCreateTimeEnd": 1717286400,
      "trackingNumberList": [
        "1Z999AA10123456784"
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
