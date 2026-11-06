# 获取面单/运单文档 接口说明

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

## 接口：获取面单/运单文档（bg.logistics.shipment.document.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

（卖家获取已通过 **Temu 集成物流渠道** 成功履约包裹的**快递面单/运单文档 URL**，用于打印面单、包裹出库。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：**  
> - **`packageSnList`** 来自 **`bg.logistics.shipment.create`** 或 **`bg.logistics.shipment.result.get`**（购标成功 **`shippingLabelStatus=1`**）。  
> - 须在订单 **`earliestTimeGetShippingDocument`** 之后调用（错误码 **120012038**）。  
> 返回的 **`url`** 若为加签链接，可用本 skill 的 **`temu_global_file_download.py`**（`POST /temu/fileDownload`）下载 PDF/PNG 文件。

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

本接口 `type` 固定为 `bg.logistics.shipment.document.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── documentType (STRING, 选填)
    └── packageSnList[] (STRING[], 选填)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| documentType | STRING | 否 | Document Type（面单文档类型），见下表 |
| packageSnList | STRING[] | 否 | Package List that needs to get the shipping label（需要获取面单的包裹号列表） |

##### `documentType`

| 值 | 说明 |
|----|------|
| `SHIPPING_LABEL_PDF` | The document URL will return the shipping label in **PDF** format for all the carriers you choose（返回 PDF 格式面单；**推荐使用**） |
| `SHIPPING_LABEL_PNG` | The document URL will return the shipping label in **PNG** format for all the carriers you choose（返回 PNG 格式面单） |
| 不传 | The document URL will return the shipping label in PDF format or PNG format **based on which carrier you choose**（按承运商默认返回 PDF 或 PNG） |

> 官方 Request 表将 **`request`**、**`documentType`**、**`packageSnList`** 均标为选填（False）；实际调用须传入有效 **`packageSnList`**（错误码 **120018027**）。Partner **Request Example** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`** 下。

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

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

```text
response
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    ├── shippingLabelUrlList[] (OBJECT[])
    │   ├── packageSn
    │   ├── documentType
    │   └── url
    └── warningMessage[] (STRING[])
```

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
| shippingLabelUrlList | OBJECT[] | 面单文档 URL 列表（每个元素对应一个 **`packageSn`** 的可打印面单链接） |
| warningMessage | STRING[] | Warning messages（警告信息列表；部分包裹成功、部分有提示时可能出现，见 Response Example） |

##### `shippingLabelUrlList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号；与请求 **`packageSnList`** 中项对应） |
| documentType | STRING | Document type actually returned（实际返回的文档类型，如 **`SHIPPING_LABEL_PDF`** / **`SHIPPING_LABEL_PNG`**） |
| url | STRING | Document download URL（面单/运单文档下载地址；用于打印或经 **`temu_global_file_download.py`** 拉取文件） |

##### `warningMessage[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| （元素） | STRING | 单条警告文案（Partner 未在 Response 表展开子字段；示例为字符串数组） |

> 调用成功时先判断 **`response.success === true`**，再遍历 **`result.shippingLabelUrlList`** 取 **`url`** 打印或下载。若 **`warningMessage`** 非空，须阅读警告内容（可能部分包裹未返回 URL 或需额外操作）。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 | 处理建议 |
|--------|------------------|----------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. | 核对 **`packageSn`** 与站点 |
| 120012038 | Order can only get shipping document after the "earliestTimeGetShippingDocument". | 等待订单到达可获取面单时间后再调 |
| 120018075 | The package {*} only supports shipping from cooperative warehouses and restricts the printing of shippingLabel | 合作仓包裹限制打印面单 |
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 包裹已取消，需重新履约 |

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
  "type": "bg.logistics.shipment.document.get",
  "params": {
    "request": {
      "documentType": "SHIPPING_LABEL_PDF",
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
