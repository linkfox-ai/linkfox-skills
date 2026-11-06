# 面单列表查询 接口说明

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

## 接口：面单列表查询（temu.logistics.label.list.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

**说明：** （查询经 **Temu 平台购标** 生成的物流面单信息列表；**仅适用于**在 Temu 平台下单购标的面单，不支持站外自填运单。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **关联能力：** **`packageSnList`** 来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)；面单文件 URL 见 [**`bg.logistics.shipment.document.get`**](./bg-logistics-shipment-document-get.md)；购标结果状态见 [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md)。

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

本接口 `type` 固定为 `temu.logistics.label.list.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── pageNumber              ← 必填
    ├── pageSize                ← 必填
    ├── packageSnList[]         ← 选填
    ├── temuLabelStatus         ← 选填
    ├── printStatus             ← 选填
    ├── createAtStart           ← 选填
    ├── createAtEnd             ← 选填
    ├── trackingNumberList[]    ← 选填
    ├── shippingCompanyIdList[] ← 选填
    └── parentOrderSnList[]     ← 选填
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNumber | INTEGER | **是** | current page number of the result（当前页码，从 **1** 起） |
| pageSize | INTEGER | **是** | page size for pagination（每页条数） |
| packageSnList | STRING[] | 否 | package sn list（包裹号列表；按 **`packageSn`** 筛选） |
| temuLabelStatus | INTEGER | 否 | Temu label status（Temu 面单/购标状态），见下表 |
| printStatus | INTEGER | 否 | Print status（面单打印状态），见下表 |
| createAtStart | INTEGER | 否 | call begin time（购标/下 call 开始时间；一般为 **Unix 秒级时间戳**，用于时间窗筛选） |
| createAtEnd | INTEGER | 否 | call end time（购标/下 call 结束时间；Unix 秒级时间戳，须不早于 **`createAtStart`**） |
| trackingNumberList | STRING[] | 否 | tracking number list（运单号列表） |
| shippingCompanyIdList | STRING[] | 否 | shipping company id list（物流公司 ID 列表；与 **`shipCompanyId`** / 承运商 ID 对应，Partner 示例为字符串数组） |
| parentOrderSnList | STRING[] | 否 | parent order sn list（父订单号列表） |

##### `temuLabelStatus`

| 值 | 说明 |
|----|------|
| `0` | Pending（进行中 / 待完成） |
| `1` | Successful（成功） |
| `2` | Failed（失败） |
| `3` | Canceled（已取消） |

> 与 [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 中 **`shippingLabelStatus`** 语义一致（0/1/2 等）。

##### `printStatus`

| 值 | 说明 |
|----|------|
| `0` | Not printed（未打印） |
| `1` | Printed（已打印） |

> 官方 Request 表为 **`printStatus`**；Response 中对应字段名为 **`labelPrintStatus`**（见出参）。

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`pageNumber`**、**`pageSize`** 为必填。筛选字段可组合使用；Partner **Request Example** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`**。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 说明为 **Specific information**。  
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)                    ← Specific information
    ├── totalItemNum (INTEGER)
    └── shippingLabelInfoList[] (OBJECT[])
        ├── packageSn
        ├── cwFulfillNo
        ├── shippingLabelStatus
        ├── labelPrintStatus
        ├── createTime
        ├── warehouseInfo (OBJECT)
        │   ├── warehouseId
        │   └── warehouseName
        ├── trackingInfoList[] (OBJECT[])
        │   ├── trackingNumber
        │   ├── shippingCompanyId
        │   └── shippingCompanyName
        ├── orderInfoList[] (OBJECT[])
        │   ├── orderSn
        │   ├── parentOrderSn
        │   └── quantity
        └── packageDimensionInfo (OBJECT)
            ├── weight / weightUnit
            ├── extendWeight / extendWeightUnit
            ├── length / width / height
            └── dimensionUnit
```

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | Specific information（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| totalItemNum | INTEGER | Total item count（符合筛选条件的面单记录总条数，用于分页） |
| shippingLabelInfoList | OBJECT[] | Shipping label information list（面单信息列表） |

##### `shippingLabelInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号） |
| cwFulfillNo | STRING | Cooperative warehouse fulfillment number（合作仓履约单号；合作仓场景可能有值） |
| shippingLabelStatus | INTEGER | Shipping label status（面单/购标状态），见下表 |
| labelPrintStatus | INTEGER | Label print status（面单打印状态），见下表 |
| createTime | INTEGER | Create time（面单/购标创建时间；Partner 示例为数值时间戳，一般为 **Unix 秒**） |
| warehouseInfo | OBJECT | Warehouse information（发货仓库信息） |
| trackingInfoList | OBJECT[] | Tracking information list（运单/承运商信息列表；一单可能多段） |
| orderInfoList | OBJECT[] | Order information list（关联订单商品行） |
| packageDimensionInfo | OBJECT | Package dimension and weight（包裹尺寸与重量） |

###### `shippingLabelStatus`（出参）

| 值 | 说明 |
|----|------|
| `0` | Pending（进行中） |
| `1` | Successful（成功） |
| `2` | Failed（失败） |
| `3` | Canceled（已取消） |

> 与入参 **`temuLabelStatus`** 筛选枚举一致。

###### `labelPrintStatus`（出参）

| 值 | 说明 |
|----|------|
| `0` | Not printed（未打印） |
| `1` | Printed（已打印） |

> 与入参 **`printStatus`** 筛选枚举一致。

###### `warehouseInfo` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| warehouseId | STRING | Warehouse ID（仓库 ID） |
| warehouseName | STRING | Warehouse name（仓库名称） |

###### `trackingInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| trackingNumber | STRING | Tracking number（运单号 / 跟踪号） |
| shippingCompanyId | INTEGER / LONG | Shipping company ID（物流公司 ID） |
| shippingCompanyName | STRING | Shipping company name（物流公司名称） |

###### `orderInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | Order number（子订单号 / 订单号） |
| parentOrderSn | STRING | Parent order number（父订单号） |
| quantity | INTEGER | Quantity（该行商品数量） |

###### `packageDimensionInfo` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| weight | STRING | Package weight（包裹重量） |
| weightUnit | STRING | Weight unit（重量单位，美国常为 **`lb`**） |
| extendWeight | STRING | Extended weight（扩展重量，美国本地盎司部分等） |
| extendWeightUnit | STRING | Extended weight unit（扩展重量单位，如 **`oz`**） |
| length | STRING | Package length（长度） |
| width | STRING | Package width（宽度） |
| height | STRING | Package height（高度） |
| dimensionUnit | STRING | Dimension unit（尺寸单位，美国常为 **`in`**） |

> 调用成功时先判断 **`success === true`**，按 **`totalItemNum`** 与 **`pageNumber` / `pageSize`** 翻页；对 **`shippingLabelStatus=1`** 的记录可调用 **`bg.logistics.shipment.document.get`** 获取面单 URL。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

- 业务错误按实际返回的 errorCode、errorMsg 解释，不预设独立错误码枚举。

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
  "type": "temu.logistics.label.list.get",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 20,
      "packageSnList": [
        "PKG-001"
      ],
      "temuLabelStatus": 1,
      "printStatus": 0
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
