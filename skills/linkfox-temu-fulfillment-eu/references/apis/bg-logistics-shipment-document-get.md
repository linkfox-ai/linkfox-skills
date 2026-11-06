# Temu 欧洲站 获取面单/运单文档 接口说明

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

## 接口：获取面单/运单文档（bg.logistics.shipment.document.get）

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

本操作的 `type` 固定为 `bg.logistics.shipment.document.get`。脚本：`scripts/eu_buy_shipping_logistics_shipment_document_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家获取已通过 **Temu 集成物流渠道** 成功履约包裹的**快递面单/运单文档 URL**，用于打印面单、包裹出库。）

> **前置依赖：**
> - **`packageSnList`** 来自 **`bg.logistics.shipment.create`** 或 **`bg.logistics.shipment.result.get`**（购标成功 **`shippingLabelStatus=1`**）。
> - 须在订单 **`earliestTimeGetShippingDocument`** 之后调用（错误码 **120012038**）。
> - USPS 等渠道可能须先完成 **manifestation**；可通过 **`bg.logistics.shipment.result.get`** 查看 **`shipLabelPrintableTime`**，或使用 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) / 卖家中心 Scan Form（错误码 **120018012**）。
> 返回的 **`url`** 若为加签链接，可用本技能的 **`temu_eu_file_download.py`**（`POST /temu/fileDownload`）下载 PDF/PNG 文件。

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

> 官方请求表将 **`request`**、**`documentType`**、**`packageSnList`** 均标为选填（False）；实际调用须传入有效 **`packageSnList`**（错误码 **120018027**）。Partner **请求示例** CURL 将字段写在顶层，经 LinkFox 网关时建议放在 **`params.request`** 下。

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
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shippingLabelUrlList | OBJECT[] | 面单文档 URL 列表（每个元素对应一个 **`packageSn`** 的可打印面单链接） |
| warningMessage | STRING[] | Warning messages（警告信息列表；部分包裹成功、部分有提示时可能出现，见 响应示例） |

##### `shippingLabelUrlList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号；与请求 **`packageSnList`** 中项对应） |
| documentType | STRING | Document type actually returned（实际返回的文档类型，如 **`SHIPPING_LABEL_PDF`** / **`SHIPPING_LABEL_PNG`**） |
| url | STRING | Document download URL（面单/运单文档下载地址；用于打印或经 **`temu_eu_file_download.py`** 拉取文件） |

##### `warningMessage[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| （元素） | STRING | 单条警告文案（Partner 未在 响应表展开子字段；示例为字符串数组） |

> 调用成功时先判断 **`response.success === true`**，再遍历 **`result.shippingLabelUrlList`** 取 **`url`** 打印或下载。若 **`warningMessage`** 非空，须阅读警告内容（可能部分包裹未返回 URL 或需额外操作）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. | 核对 **`packageSn`** 与站点 |
| 120012038 | Order can only get shipping document after the "earliestTimeGetShippingDocument". | 等待订单到达可获取面单时间后再调 |
| 120018012 | USPS labels require manifestation before printing. Check 'shipLabelPrintableTime' via 'bg.logistics.shipment.result.get' or use 'temu.logistics.scanform.create'/Seller Central Scan Form to update immediately. | 先查 **`shipLabelPrintableTime`** 或调用 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) |
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
  -d '
{
  "site": "eu",
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
