# 订单核验信息上传 接口说明

接口总览见 [../api.md](../api.md)，认证指引见 [../onboarding.md](../onboarding.md)。

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

## 接口：订单核验信息上传（temu.local.order.verification.upload）

上传 SN、IMEI 或二手商品鉴真信息。

使用子订单 orderSn，可从列表或详情的 orderList[].orderSn 取得；父单 parentOrderSn 不能替代子单号。

官方文档：https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`；全球区，非 US/EU。通用脚本兼容 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本兼容 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；业务脚本优先直接使用，或从本地令牌存储读取后填入。 |
| storeKey | string | 与 accessToken 二选一 | 令牌键，对应 `~/.linkfox/temu-access-tokens.json` 中的记录（路径可由 `TEMU_TOKEN_STORE_PATH` 覆盖）；本技能脚本在本地解析，不把此字段转发到网关。 |
| tokenPurpose | string | 否 | 令牌用途，订单建议 `order-shipping`；本技能脚本仅用于本地选取令牌，不转发此字段。 |
| type | string | 是 | 本接口操作名，见下方操作标识；Temu 操作放在 Body，不是 URL path。 |
| params | object | 否 | 业务参数，使用本接口下方定义的 `request` 结构；无业务字段时脚本可省略。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessToken | string | 与 storeKey 二选一 | 直接提供时优先于本地令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌键；按 site + managementType + tokenPurpose 精确匹配，不跨店铺、站点或用途回退。 |
| tokenPurpose | string | 否 | 全球区订单脚本默认 `order-shipping`；仅用于本地令牌选择，不转发为业务字段。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序读取首个非空值，优先于环境变量；用于 LinkFox 用户鉴权，与 Temu accessToken 不同。 |
| --inline | CLI flag | 否 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 业务脚本不使用响应缓存；调用公共 run 时始终传入此选项，不读取或保存响应缓存。 |

LinkFox 环境变量按 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY` 顺序读取；Header `Authorization` 与 `Token` 同值。基础地址按 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL` 顺序兼容，默认正式网关。HTTP 超时默认 150 秒。
全球区专用脚本允许业务字段放在输入顶层，或放在对象 `params` 内；后者优先。顶层 `request` 整体作为 `params.request` 转发，不自动把任意业务字段再包一层。通用 `temu_proxy.py` 需显式传 site、managementType、type 和对象 params。令牌存储与授权 CLI 见 [../access-token.md](../access-token.md)。
会话数据保存在当前工作目录，禁止回退到临时目录；目录不可写时在请求前报错。无响应缓存仍可能由公共调用器创建空缓存目录，不保存响应缓存文件。

本接口 `type` 固定为 `temu.local.order.verification.upload`；对应脚本 `scripts/global_order_verification_upload.py`。

#### params 业务载荷

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 业务请求对象，官方标注为选填；子字段必填性见下表。 |

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderList | OBJECT[] | 否 | order unique info list（订单唯一标识/核验信息列表）；按子订单维度批量上传 |

#### `orderList[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderSn | STRING | 否 | order sn（子订单号） |
| verificationInfo | OBJECT[] | 否 | electronic ams open unique info list（高价值/电子产品唯一标识列表，如 SN、IMEI） |
| secondHandVerificationInfo | OBJECT[] | 否 | second hand ams open verification info（二手商品鉴真/认证信息列表） |

#### `verificationInfo[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| serialNumber | STRING | 否 | serial number（序列号 SN） |
| imeiNumberList | STRING[] | 否 | imei number list（IMEI 号码列表） |

> 高价值商品场景：按实际商品要求填写 `serialNumber` 和/或 `imeiNumberList`；同一 `orderSn` 可包含多条 `verificationInfo`（例如多件商品各一条 SN）。

#### `secondHandVerificationInfo[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secondHandProofCertificateCode | STRING | 否 | second hand proof certificate code（二手商品鉴真/证明证书编码） |

> 二手商品场景：填写 `secondHandProofCertificateCode`；与高价值 `verificationInfo` 按订单实际类型择一或组合使用（以 Partner 与订单标签为准）。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 外层状态；遵循公共响应码基本规则，不替换为 Temu 成功判断。 |
| errmsg | string | LinkFox 外层消息；错误时保留。 |
| code | integer | 网关错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array | 脚本对非空且合法的 body 解析所得；解析失败时不生成，不补造业务结果。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败时为 null。 |
| error / details | string | 连接异常或非 JSON HTTP 错误的说明与原始内容（存在时保留）。 |

先检查外层 HTTP 与 errcode，再检查网关 code（如有错误），然后解析 body，依据 Temu 的 success / errorCode / errorMsg / result 解释结果。下列为 Temu body 解析后的原始业务字段。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功（success） |
| errorCode | INTEGER | 错误码（error code） |
| errorMsg | STRING | 错误消息（error message） |
| result | OBJECT | 业务结果对象；官方出参表未展开子字段，上传成功时通常以 `success=true` 为准，具体以 Temu 实际返回为准 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| _(无子字段)_ | — | Partner 文档未列出 `result` 内嵌套属性；若响应体含其它字段，以实际 JSON 为准 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002`：修正参数或 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单和转发情况。
- Temu `success=false` 时根据 `errorCode`、`errorMsg` 解释失败；外层 HTTP 正常不代表 Temu 操作成功。保留 `result` 与 warning，不自动重试、翻页或换参数试探。
- body 不是合法 JSON 时保留原文，不把解析失败当作空业务结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.local.order.verification.upload",
  "params": {
    "request": {
      "orderList": [
        {
          "orderSn": "SO-123456789",
          "verificationInfo": [
            {
              "serialNumber": "SN-001234567890",
              "imeiNumberList": [
                "352099001761481",
                "352099001761482"
              ]
            }
          ]
        }
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
  "skillName": "linkfox-temu-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
