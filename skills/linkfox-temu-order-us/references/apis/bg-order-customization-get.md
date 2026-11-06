# 订单定制商品内容批量查询 接口说明

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

## 接口：订单定制商品内容批量查询 — `bg.order.customization.get`

供自研卖家和第三方 ISV 批量读取子订单的定制商品内容。

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
| type | string | 是 | 本接口标识：`bg.order.customization.get`，写在 Body 中，不是 URL 路径。 |
| params | object | 否 | 官方业务参数对象，业务字段位于 `params.request`。 |
| params.request | OBJECT | 否 | 官方声明为选填对象；内部字段按下表约定，不因外层选填而免除内部必填要求。 |

脚本允许业务字段放在顶层（如 `request`）或嵌套 `params`；存在对象类型的 `params` 时优先使用该对象。认证、站点等保留键不会混入业务参数。脚本认证兼容与选项见 [运行约定](../api.md#脚本运行约定)。

```text
params
└── request (OBJECT, 选填)
    └── orderSnList[] (STRING[], 否)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderSnList | STRING[] | 否 | 子订单号列表；**单次最多查询 10 个订单** |

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
└── result[] (OBJECT[])
    ├── orderSn
    ├── customizedType
    ├── customizedData          ← 仅 customizedType=2 时返回
    ├── previewList[]           ← 仅 customizedType=2 时返回
    │   ├── previewType
    │   ├── imageUrl
    │   ├── customizedText
    │   └── customizedAreaId
    ├── templateId
    ├── templateType
    ├── customizedText          ← 仅 customizedType=1 时返回（result 层级）
    └── customizedSvgList[]
        └── compressedFileUrl
```

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT[] | 各子订单的定制内容列表（与请求的 `orderSnList` 对应） |

#### `result[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | 对应该定制信息的子订单号 |
| customizedType | INTEGER | 定制类型，见下表 |
| customizedData | STRING | 图文定制内容，JSON 字符串；**仅当 `customizedType=2` 时返回** |
| previewList | OBJECT[] | 图文定制预览信息；**仅当 `customizedType=2` 时返回** |
| templateId | LONG | 用户创建定制信息时的模板 ID；商品无模板时为 `null` |
| templateType | INTEGER | 定制模板类型；商品无模板时为 `null`，见下表 |
| customizedText | STRING | 纯文本定制内容；**仅当 `customizedType=1` 时返回**（位于 `result[]` 元素顶层，与 `previewList[].customizedText` 不同） |
| customizedSvgList | OBJECT[] | SVG 格式定制信息列表 |

##### `customizedType`

| 值 | 说明 |
|----|------|
| `1` | 纯文本定制，无定制模板 |
| `2` | 图文定制，有定制模板 |

##### `templateType`

| 值 | 说明 |
|----|------|
| `1` | 仅图片 |
| `2` | 仅文字 |
| `3` | 文字 + 图片 |

> 商品无定制模板时，`templateId` / `templateType` 为 `null`。

#### `previewList[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| previewType | INTEGER | 预览项类型，见下表 |
| imageUrl | STRING | 图片 URL |
| customizedText | STRING | 预览项中的定制文字 |
| customizedAreaId | STRING | 定制区域 ID；**仅当 `templateType=3` 且 `previewType=3` 或 `4` 时返回** |

##### `previewType`

| 值 | 说明 |
|----|------|
| `1` | 整体预览图；若商品未配置定制区域，则为商家上传的效果图 |
| `3` | 用户上传图片 |
| `4` | 定制文字 |

#### `customizedSvgList[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| compressedFileUrl | STRING | 图片/压缩包下载 URL；调用方需 **GET** 该 URL 拉取文件；**创建后 10 分钟内有效**，过期需重新调本接口获取新 URL |

##### 下载 `compressedFileUrl` 的 TOA 请求头

对 `compressedFileUrl` 发起 **GET** 时，需在 Header 携带以下公共参数（与 Partner 文档一致）：

| Header | 说明 |
|--------|------|
| `toa-app-key` | `${app_key}` |
| `toa-access-token` | `${access_token}` |
| `toa-random` | 32 位随机数字符串 |
| `toa-timestamp` | 时间戳 |
| `toa-sign` | 签名（见下） |

**`toa-sign` 计算逻辑：**

1. 将 Header 中参与签名的参数按参数名 **ASCII 升序**排序：`toa-app-key`、`toa-access-token`、`toa-random`、`toa-timestamp`
2. 按 `参数名 + 参数值` 依次拼接（中间**无**分隔符），得到长字符串
3. 在拼接结果**首尾**各拼接一次 `app_secret`，得到签名字符串
4. 对签名字符串做 **MD5**，再将密文转为**大写**，即为 `toa-sign`

> 实际 `app_key` / `access_token` / `app_secret` 以店铺授权与 Partner 应用配置为准；经 LinkFox 网关调用本 `type` 时，业务 JSON 仍走 `POST /temu/proxy`，**文件下载**为对上述 URL 的独立 GET + TOA 头。

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
  "type": "bg.order.customization.get",
  "params": {
    "request": {
      "orderSnList": [
        "SO-123456789",
        "SO-987654321"
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
  "skillName": "linkfox-temu-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
