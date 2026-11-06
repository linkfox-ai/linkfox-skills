# 广告操作日志查询 接口说明

[接口总览与运行约定](../api.md) · [接口目录](README.md)

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

## 接口：广告操作日志查询（temu.searchrec.ad.log.query）

> Partner 文档：https://partner-us.temu.com/documentation?menu_code=1e72b5cceef545ec8f9652b9e56dd054&sub_menu_code=c2c5eda51c414e788bab914a297d1881

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；美国站上游为 `https://openapi-b-us.temu.com/openapi/router`。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；须与店铺授权一致。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，直接传入时优先；使用 storeKey 时由脚本读取后写入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 本地 `~/.linkfox/temu-access-tokens.json` 的店铺键；仅供脚本查找，脚本不发送此字段。 |
| tokenPurpose | string | 否 | 建议 `product-inventory`，以本接口 Partner 授权要求为准；用于本地查找令牌，US 脚本默认该值，脚本不发送此字段。 |
| type | string | 是 | 固定为 `temu.searchrec.ad.log.query`；它是 Body 字段，不是 URL path，专用脚本自动设置。 |
| params | object | 否 | 本接口业务参数，包含下方的 `request`。 |

#### 业务参数封装

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否（官方顶层表） | Partner 将 `request` 标为选填（False），其中标为必填的业务字段仍须放入 `params.request`。 |

US 脚本接受顶层 `request` 或嵌套 `params.request`；若 `params` 是对象则优先整体使用，其他非保留顶层字段才作为业务参数。认证、站点、管理方式、用途、type、params 等保留字段不会混入业务载荷。网关鉴权兼容与 CLI 约定见 [运行约定](../api.md#运行约定)。

#### request 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsId | LONG | **是** | 商品 ID |
| startTime | LONG | **是** | 查询开始时间，毫秒时间戳，取当地时区 0:00 |
| endTime | LONG | **是** | 查询结束时间，毫秒时间戳，取当地时区 23:59:59.999 |

### 响应结构

#### 网关与脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 网关错误码：`1002` 表示参数或 Token 问题，`1003` 表示转发失败；存在该业务错误时不将 body 解释为成功。 |
| body | string | Temu 原始 JSON 字符串；先判断外层 HTTP、errcode 与网关 code，再解析业务字段。 |
| temuBody | object / array / 其他 JSON 类型 | 脚本在网关正常且 body 为有效非空 JSON 字符串时添加的解析结果；解析失败保留原始 body。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态；连接失败时为 null，不等同于 Temu 的 errorCode。 |
| gatewayResponse | 任意 JSON 类型 | 仅网关返回非对象 JSON 时，脚本用此字段保留原始值；不能据此认定业务成功。 |

网关业务 `code` 只明确列出 `1002`、`1003` 错误，不能套用外层 `errcode` 的成功枚举；其他 `code` 原样保留并解析 body 供诊断，解析成功不等于业务成功。

下表展开 `body` 解析后的 Temu 字段与嵌套层级；Partner 响应表中的折叠行按其响应示例解读，不补造未定义枚举或字段。

#### Temu 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | Temu 业务是否成功 |
| errorCode | INTEGER | Temu 业务错误码 |
| errorMsg | STRING | Temu 业务错误消息 |
| result | OBJECT 或 OBJECT[] | 业务结果（见下表） |

#### `result`（OBJECT[]）

Partner 响应示例中 **`result`** 直接为数组。

| 参数 | 类型 | 说明 |
|------|------|------|
| eventType | STRING | 操作事件类型 |
| updateSellerName | STRING | 执行变更的卖家名称 |
| changeInfo | STRING | 变更内容描述 |
| updatedAt | STRING | 更新时间；Partner 示例为字符串 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002`：参数或 LinkFox Token 无效，核对参数及密钥；`code=1003`：转发失败，核对 Temu token、tokenPurpose、IP 白名单及网络。错误不自动重试。
- 网关正常后才解析 `body`，再检查 Temu `success`、`errorCode`、`errorMsg` 和 `result`；Temu 业务失败不等同于 LinkFox 鉴权失败。

#### Temu 业务错误码

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 230012000 | bad query params | 见 Partner 文档；修正入参或权限后重试 |
| 230012003 | unmatch mall and goods | 见 Partner 文档；修正入参或权限后重试 |
| 230013000 | business exception | 见 Partner 文档；修正入参或权限后重试 |
| 230014000 | system exception | 见 Partner 文档；修正入参或权限后重试 |
| 230016701 | has no permission | 见 Partner 文档；修正入参或权限后重试 |
| 230016103 | not signed because of not main account | 见 Partner 文档；修正入参或权限后重试 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site": "us", "managementType": "semi-managed", "accessToken": "TOKEN", "type": "temu.searchrec.ad.log.query", "params": {"request": {"goodsId": 100001, "startTime": 1714521600000, "endTime": 1714607999999}}}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-ads-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
