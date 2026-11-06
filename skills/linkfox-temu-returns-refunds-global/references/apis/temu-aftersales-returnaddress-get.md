# 退货地址查询 接口说明

返回 [接口总览](../api.md)；Partner 来源及文档菜单见 [目录](../partner-global-catalog.md)。

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


## 接口：退货地址查询（temu.aftersales.returnaddress.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| site | string | 是 | Global 专用脚本默认 `global`；通用脚本显式提供。兼容值 `cn` / `partner` / `us` / `global` / `eu`，小写。 |
| managementType | string | 是 | Global 专用脚本默认 `semi-managed`；兼容 `full-managed` / `semi-managed`，小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接请求网关时必填，`storeKey` 由脚本本地解析为此字段。 |
| storeKey | string | 与 accessToken 二选一 | 仅脚本参数，本地 Token 存储中的店铺键，不发给网关。 |
| tokenPurpose | string | 否 | 仅脚本选 Token 用途；Global 默认 `order-shipping`，不发给网关。用途必须与店铺授权一致。 |
| type | string | 是 | 本接口固定为 `temu.aftersales.returnaddress.get`；专用脚本自动设置，通用代理要求显式提供。 |
| params | object | 否 | 业务参数，建议按下表放在 `params.request`。 |

#### 脚本鉴权与选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，按该顺序优先于环境变量；不发入业务 Body。 |
| --inline | CLI flag | 否 | 强制完整打印；仍保存响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存；封装调用 `call_api.run` 时始终追加，不读写响应缓存。 |

补充运行约定见 [接口总览](../api.md#脚本运行约定)。Global 专用脚本支持顶层业务字段或 `params` 对象，存在对象 `params` 时优先使用；显式 `request` 按原层级转发。多站点 `temu_proxy.py` 仅使用对象 `params`，不把顶层业务字段自动并入。官方将 `request` 标为选填，内部必填项仍须提供；Partner 示例顶层字段经网关调用时建议放入 `params.request`。

#### `params`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 业务请求对象；位于网关 params 下，内部必填项仍须提供。 |

#### `params.request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentAfterSalesSn | STRING | **是** | 父售后单号 |

### 响应结构

#### LinkFox 网关与脚本字段

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断。 |
| errmsg | string | 若返回，为网关消息。 |
| body | string | Temu 原始 JSON 字符串；代理脚本解析后增加 `temuBody`，同时保留原始 `body` 字符串。 |
| code | integer | 网关兼容错误码：`1002` 参数或 Token 无效，`1003` 转发失败。 |
| temuBody | object / array / scalar / null | 仅代理脚本在 `body` 可解析为 JSON 时增加；解析失败保留原始 `body`。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态；连接失败为 null。 |

Temu 业务数据可能位于解析后根级或 `response` 内；下表保留 Partner 字段层级。不能把 HTTP 请求完成等同于售后业务成功。

#### Temu 响应包装

| 字段 | 类型 | 说明 |
|---|---|---|
| response | OBJECT | Partner 文档的业务响应包装；实返也可能直接使用根对象。下列字段位于此对象内或解析后根级。 |

#### Temu 顶层字段（`response` 内或解析后根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果对象（见下表） |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| receiptAdditionalName | STRING | 收件人附加名 |
| receiptName | STRING | 收件人姓名 |
| regionName1 | STRING | 一级地区名 |
| regionName2 | STRING | 二级地区名 |
| regionName3 | STRING | 三级地区名 |
| regionName4 | STRING | 四级地区名 |
| mail | STRING | 电子邮箱 |
| mobile | STRING | 手机号 |
| backupMobile | STRING | 备用手机号 |
| addressLine1 | STRING | 地址行 1 |
| addressLine2 | STRING | 地址行 2 |
| addressLine3 | STRING | 地址行 3 |
| addressLineAll | STRING | 完整地址拼接 |
| postCode | STRING | 邮政编码 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关兼容字段 `code=1002` 表示参数或 LinkFox Token 无效，`1003` 表示转发失败；先排查 Token、用途和 IP 白名单。
- 在网关正常响应基础上解析 `body`，再根据 Temu `success`、`errorCode` 和 `errorMsg` 判断业务结果；`success=false` 不能认定为业务成功。
- `18002xxxx` 可能表示国家未开放地址查询、未签 DPA，或全托管、仅退款、已上传面单、无需面单等场景不支持；按下表解释，不循环尝试。

| errorCode | errorMsg（接口原值） | 处理建议 |
|-----------|----------|----------------------|
| 180020001 | This country has not yet opened address query capabilities | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 180020008 | Please sign on DPA agreement first | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 180021001 | full managed, unSupport query address | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 180021002 | only refund type, unSupport query address | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 180021003 | uploaded label, unSupport query address | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |
| 180021004 | no need upload label, unSupport query address | 结合原始消息核对入参、售后状态或开通条件；按用户范围修正后再调用，不自动重试 |

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
  "type": "temu.aftersales.returnaddress.get",
  "params": {
    "request": {
      "parentAfterSalesSn": "PAS-001"
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
  "skillName": "linkfox-temu-returns-refunds-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
