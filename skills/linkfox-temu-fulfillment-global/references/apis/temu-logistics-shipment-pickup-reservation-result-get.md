# 查询上门揽收预约结果 接口说明

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

## 接口：查询上门揽收预约结果（temu.logistics.shipment.pickup.reservation.result.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

（查询**上门揽收预约**的异步处理结果。传入 **`packageSnList`** 后，返回各包裹对应的 **`reservationSn`**、**`reservationStatus`** 及该预约下包含的全部 **`packageSnList`**；多个包裹合并为同一预约时，响应会返回该 **`reservationSn`** 下的全部包裹。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：** 须先调用 [**`temu.logistics.shipment.pickup.reservation.create`**](./temu-logistics-shipment-pickup-reservation-create.md) 提交预约；本接口用于异步查询预约是否成功及 **`reservationSn`**。

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

本接口 `type` 固定为 `temu.logistics.shipment.pickup.reservation.result.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    └── packageSnList[] (STRING[], 必填，最多 50)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | **是** | packageSn list, maximum 50（需要查询预约结果的**包裹号列表**，**单次最多 50 个**；通常传入 [**pickup.reservation.create**](./temu-logistics-shipment-pickup-reservation-create.md) 时使用的 **`packageSnList`**） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`packageSnList`** 为必填（True）。Partner **Request Example** CURL 将 **`packageSnList`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.packageSnList`**。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    └── reservationResultList[] (OBJECT[])
        ├── reservationSn
        ├── packageSnList[] (STRING[])
        └── reservationStatus
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
| reservationResultList | OBJECT[] | Reservation result list（按请求 **`packageSnList`** 返回的预约结果列表；同一 **`reservationSn`** 下可能包含多个包裹） |

##### `reservationResultList[]` 元素字段

> Partner **Response** 表中 **`result`** 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **Response Example**，说明结合接口 Description 整理。若 Partner 在线文档 **Expand** 后对 **`reservationStatus`** 有枚举说明，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| reservationSn | STRING | Reservation serial number（预约单号/预约序列号；[**pickup.reservation.create**](./temu-logistics-shipment-pickup-reservation-create.md) 合并预约后生成的唯一标识） |
| packageSnList | STRING[] | Package SN list under this reservation（该 **`reservationSn`** 下包含的全部包裹号；当多个包裹对应同一预约时，此处返回该预约下的**所有**包裹，而不仅是请求中的单个 **`packageSn`**） |
| reservationStatus | INTEGER | Reservation status（预约状态；Response Example 为 **`1`**；具体枚举含义以 Partner 在线 Response 表为准，可轮询本接口直至预约处理完成） |

> 调用成功时先判断 **`success === true`**，再遍历 **`result.reservationResultList`**，按 **`packageSn`** 匹配条目，查看 **`reservationStatus`** 与 **`reservationSn`**。若多个包裹共享同一 **`reservationSn`**，**`packageSnList`** 会列出该预约下的全部包裹。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 | 处理建议 |
|--------|------------------|----------|
| 120011002 | Invalid request parameters. | 检查 **`packageSnList`** 非空且格式正确 |

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
  "type": "temu.logistics.shipment.pickup.reservation.result.get",
  "params": {
    "request": {
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
