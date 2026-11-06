# 在线发货物流类型 接口说明

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

## 接口：在线发货物流类型（temu.logistics.shiplogisticstype.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

（获取全部**在线发货**（online-shipment）可用的物流类型；选定类型后可调用 **`bg.logistics.shipment.create`** 在 Temu 平台购标；Temu 会按所选 **ship logistics type** 自动选择推荐 **channel id** 并完成购标。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。

**Permission Package（Partner）：**

| 权限包（原名） | 应用类型 |
|--------------------|----------|
| Semi Online Call Shipment Management | private, public（私有、公开应用） |
| Local Order Fulfillment Management | private, public（私有、公开应用） |

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

本接口 `type` 固定为 `temu.logistics.shiplogisticstype.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    └── regionId (LONG, 必填)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| regionId | LONG | **是** | regionId（请求区域 ID）。错误码 **120011072** 提示：美国请求区域为 **US**，其他非欧洲国家为 **global**；请与业务站点一致。订单/物流示例为 **`regionId=211`**（USA），应按目标订单确定实际区域，见 [regionId 编码说明](https://partner.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896) 与 `linkfox-temu-order-global`；Partner **Request Example**  CURL 示例为 `regionId: 1`，以实际调通值为准。 |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`request.regionId`** 为必填（True）。

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

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`（与 **Response Example** 一致）。下列层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    ├── regionId
    └── shipLogisticsTypeInfoDTOList[] (OBJECT[])
        ├── logisticsProviderLabelList[] (STRING[])
        ├── shipLogisticsType
        ├── shippingCompanyName
        └── shipCompanyId
```

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| regionId | LONG | regionId（与请求区域对应的区域 ID；Response Example 中与入参呼应） |
| shipLogisticsTypeInfoDTOList | OBJECT[] | 在线发货物流类型列表（可选物流类型及承运商信息） |

##### `shipLogisticsTypeInfoDTOList[]` 元素字段

> 下列字段在 Partner **Response** 表中位于 **`result`** 子树（需在线文档点击 **Expand** 展开）；字段用途与 **Response Example** 及购标流程对应。若在线 Response 表有更完整描述，以 Partner 为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| shipLogisticsType | STRING | Ship logistics type（发货物流类型编码/标识；购标时在 **`bg.logistics.shipment.create`** 等接口中选择此类型，Temu 将自动匹配推荐 channel） |
| shippingCompanyName | STRING | Shipping company name（物流公司/承运商名称） |
| shipCompanyId | LONG | Ship company ID（物流公司 ID） |
| logisticsProviderLabelList | STRING[] | Logistics provider label list（物流服务商标签列表，用于展示或筛选） |

> 调用成功时先判断 **`success === true`**，再遍历 **`result.shipLogisticsTypeInfoDTOList`**，选定 **`shipLogisticsType`** 后调用 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md) 完成购标。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 |
|------------|---------------|
| 120011001 | System abnormality, please check the data and try again |
| 120011002 | Invalid request parameters. |
| 120011072 | The request area is incorrect. Please check the request area and replace it with the correct request area. The request area for the United States is US, and the request area for other non-European countries is global. |

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
  "type": "temu.logistics.shiplogisticstype.get",
  "params": {
    "request": {
      "regionId": 211
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
