# 订单收货地址查询 V2 接口说明

返回 [接口总览](../api.md)。Partner 文档入口：https://partner-us.temu.com/documentation（`menu_code` / `sub_menu_code` 以后台对应接口页为准）。

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

## 接口：订单收货地址查询 V2 — `bg.order.shippinginfo.v2.get`

查询指定父订单的常规收货地址及地址返回限制提示。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站为 `us`；US 脚本默认 `us`。 |
| managementType | string | 是 | 美国半托管为 `semi-managed`；US 脚本默认此值。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用显式 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌替代字段，为 `~/.linkfox/temu-access-tokens.json` 中的店铺键；脚本在本地解析后发送 accessToken。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`（订单/发货）；脚本用于选取对应用途的本地令牌，不混入业务参数，也不转发此字段。 |
| type | string | 是 | 本接口标识：`bg.order.shippinginfo.v2.get`，写在 Body 中，不是 URL 路径。 |
| params | object | 否 | 官方业务参数对象，业务字段位于 `params.request`。 |
| params.request | OBJECT | 否 | 官方声明为选填对象；内部字段按下表约定，不因外层选填而免除内部必填要求。 |

脚本允许业务字段放在顶层（如 `request`）或嵌套 `params`；存在对象类型的 `params` 时优先使用该对象。认证、站点等保留键不会混入业务参数。脚本认证兼容与选项见 [运行约定](../api.md#脚本运行约定)。

```text
params
└── request (OBJECT, 选填)
    └── parentOrderSn (STRING, 否)
```

#### `request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | 否 | 父订单号；查询指定订单收货地址时**应传入** |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断；保留原始值。 |
| errmsg | string | 网关错误消息；完整保留。 |
| code | integer | 网关错误码：`1002` 参数或 Token 错误，`1003` 转发失败；不得与 Temu `errorCode` 混淆。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | JSON value | 脚本在 `body` 为非空且可解析的 JSON 字符串时增加的解析结果；解析失败时不增加此字段。 |
| error | string | HTTP 非 JSON 错误或连接错误信息（仅错误时出现）。 |
| details | string | 非 JSON HTTP 错误的原始响应内容（仅错误时出现）。 |
| gatewayResponse | JSON value | 仅当网关返回非对象 JSON 时，脚本在落盘与展示层包装原始值；不属于 Temu 业务字段。 |

以下为 Temu `body` 解析后的业务字段。先判断外层 HTTP 与 `errcode`，再检查网关 `code` 和 Temu `success` / `errorCode` / `errorMsg`，不得仅因 JSON 可解析而判成功。

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── receiptName
    ├── receiptAdditionalName
    ├── mobile
    ├── backupMobile
    ├── mail
    ├── regionName1
    ├── regionName2
    ├── regionName3
    ├── regionName4
    ├── addressLine1
    ├── addressLine2
    ├── addressLine3
    ├── postCode
    ├── addressLineAll
    ├── addressExtra
    │   ├── firstName
    │   ├── lastName
    │   ├── additionalFirstName
    │   └── additionalLastName
    └── warning
        ├── isRestriction
        └── reason
```

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 收货地址等业务结果 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| receiptName | STRING | 收件人姓名 |
| receiptAdditionalName | STRING | 附加姓名 |
| mobile | STRING | 手机号 |
| backupMobile | STRING | 备用电话 |
| mail | STRING | 虚拟邮箱 |
| regionName1 | STRING | 一级行政区名称 |
| regionName2 | STRING | 二级行政区名称 |
| regionName3 | STRING | 三级行政区名称 |
| regionName4 | STRING | 四级行政区名称 |
| addressLine1 | STRING | 地址行 1 |
| addressLine2 | STRING | 地址行 2 |
| addressLine3 | STRING | 地址行 3 |
| postCode | STRING | 邮编 |
| addressLineAll | STRING | Address Line 1 + Line 2 + Line 3（拼接完整地址行） |
| addressExtra | OBJECT | 姓名拆分等扩展信息 |
| warning | OBJECT | 地址/履约限制提示 |

#### `addressExtra`

| 参数 | 类型 | 说明 |
|------|------|------|
| firstName | STRING | 名 |
| lastName | STRING | 姓 |
| additionalFirstName | STRING | 附加名 |
| additionalLastName | STRING | 附加姓 |

#### `warning`

| 参数 | 类型 | 说明 |
|------|------|------|
| isRestriction | BOOLEAN | 是否存在地址返回限制 |
| reason | INTEGER | 存在地址返回限制时，表示限制场景 |

##### `warning.reason` 枚举

| 值 | 说明 |
|----|------|
| `1` | COD（货到付款） |
| `2` | 限制自发货 |
| `3` | 仅承诺购买平台物流 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 表示参数或 LinkFox Token 无效，核对参数与认证；`code=1003` 表示转发失败，核对 Temu token、用途、IP 白名单与网络。
- Temu 业务结果以 `body` 中的 `success`、`errorCode`、`errorMsg` 判断；`success=false` 时按上游错误说明处理。保留原始错误，不补造业务结果或未知响应码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.shippinginfo.v2.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789"
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
  "skillName": "linkfox-temu-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
