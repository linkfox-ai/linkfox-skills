# 查询 Scan Form 详情 接口说明

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

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=temu.logistics.scanform.get`；**对应脚本**：`scripts/us_buy_shipping_logistics_scanform_get.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=d8425dcd25b04658843e622e178a3b42&sub_menu_code=9cc3edb526494a059c477fd99953fa3e

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

> **关联能力：** 创建 Scan Form 见 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md)；获取 Scan Form 文档见 **`temu.logistics.scanform.document.get`**（本技能已接入）。购标与包裹号见 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)。

（卖家按分页与筛选条件查询 Scan Form（物流扫描单）的详情信息，例如创建状态等。）

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

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`pageNumber`**、**`pageSize`** 为必填。筛选字段可组合使用。Partner **Request Example** CURL 将业务字段写在 JSON 顶层，经 LinkFox 网关时建议放在 **`params.request`**。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 在表内标注为 **Specific information**。
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **Response 表 + Response Example** 全部展开。

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
| scanFormCreateTime | STRING | Scan form creating time（Scan Form 创建时间；Partner **Response Example** 为字符串，一般为时间戳字符串） |
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

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
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
  -d '{
  "site": "us",
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
