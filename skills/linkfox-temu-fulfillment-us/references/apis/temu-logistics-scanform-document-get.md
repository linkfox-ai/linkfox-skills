# 获取 Scan Form 文档 接口说明

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

## 接口：获取 Scan Form 文档（temu.logistics.scanform.document.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=temu.logistics.scanform.document.get`；**对应脚本**：`scripts/us_buy_shipping_logistics_scanform_document_get.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=442a5ca8a9fd4bf7bb5493344a7e818f&sub_menu_code=1c9d0c2fade74f48a6bb22296c6fc509

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

> **前置依赖：** **`scanFormSn`** 来自 [**`temu.logistics.scanform.create`**](./temu-logistics-scanform-create.md) 返回的 **`result.scanFormInfoList[].scanFormSn`**。若 Scan Form 状态异常，可先调用 **`temu.logistics.scanform.get`** 查看失败原因（错误码 **120016058**）。
> 返回的 **`result.url`** 若为加签链接，可用本 skill 的 **`temu_us_file_download.py`**（`POST /temu/fileDownload`）下载文件。

（卖家根据 **Scan Form 编号** 获取 Scan Form 文档下载 URL，用于打印交运扫描单（manifest）等。）

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scanFormSn | STRING | **是** | Scan form serial number, the unique identification field when creating a scan form（Scan Form 序列号；创建 Scan Form 时的唯一标识，来自 **`temu.logistics.scanform.create`** 的 **`scanFormInfoList[].scanFormSn`**） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`scanFormSn`** 为必填。Partner **Request Example** CURL 将 **`scanFormSn`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.scanFormSn`**（与 Request 表一致）。

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

Partner **Response** 表顶层为 **`response`** 对象；**`result`** 说明为 **Specific information**。
**`result`** 子行在导出 HTML 中为折叠状态；下列字段来自 **Response 表 + Response Example** 全部展开。

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
| url | STRING | Scan Form document URL（Scan Form 文档下载地址；用于打印或下载 manifest/扫描单文件。若为 Temu 加签 URL，须通过 **`temu_us_file_download.py`** 按网关规范下载） |

> 调用成功时先判断 **`success === true`**，再使用 **`result.url`** 下载或打印 Scan Form 文档。USPS 等渠道完成 Scan Form 后，相关包裹面单 **`shipLabelPrintableTime`** 可能更新，可再查 [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 或 [**`bg.logistics.shipment.document.get`**](./bg-logistics-shipment-document-get.md)。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 120016058 | The status of {*} is failed. Please check the failReason by "temu.logistics.scanform.get". | 调用 **`temu.logistics.scanform.get`** 查看 Scan Form 失败原因 |
| 120011070 | The {*} is invalid. Please check the request area or if the scanFormSn is nonexistent. | 核对 **`scanFormSn`** 是否存在、请求区域是否为 US |
| 120011001 | System abnormality, please check the data and try again | 检查入参后重试 |
| 120011002 | Invalid request parameters. | 确认 **`scanFormSn`** 已传入且格式正确 |

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
  "type": "temu.logistics.scanform.document.get",
  "params": {
    "request": {
      "scanFormSn": "SF-20260101001"
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
