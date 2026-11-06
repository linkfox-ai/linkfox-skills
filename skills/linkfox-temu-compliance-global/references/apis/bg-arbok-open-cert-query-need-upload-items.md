# 待上传资质项查询 接口说明

[返回接口总览](../api.md)；[认证与算力指引](../onboarding.md)。Partner 官方文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=84d3118d3a604947abf35144606cdea2

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

## 接口：待上传资质项查询（bg.arbok.open.cert.queryNeedUploadItems）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 全球站业务脚本默认 `global`，上游为 `https://openapi-b-global.temu.com/openapi/router`；通用入口允许 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 全球站脚本默认 `semi-managed`；通用入口允许 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用此值。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键；发送前解析为 accessToken，不发送到网关。 |
| tokenPurpose | string | 否 | 本技能默认 `product-inventory`，用于本地令牌定位；通用脚本默认 `default`。 |
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本 JSON 兼容参数；依次取第一个非空值覆盖环境密钥，设置同值 Authorization + Token 请求头，不进入业务 params。 |
| type | string | 是 | 本接口的 Temu 操作名，见本节；业务脚本固定此值，不从用户 JSON 覆盖。 |
| params | object | 否 | 业务对象；本接口使用 `params.request`。脚本优先使用对象形式的 params，否则提取顶层业务字段；认证和路由字段不进入业务对象。 |
| params.request | OBJECT | 按业务要求 | Partner 请求对象，全部业务字段定义见下表。子字段的必填性见下表；容器本身的必填性未单独声明。 |

本接口 `type` 固定为 `bg.arbok.open.cert.queryNeedUploadItems`。业务脚本为 `scripts/global_compliance_arbok_cert_query_need_upload_items.py`；认证与 CLI 兼容约定见 [运行约定](../api.md#脚本兼容与运行约定)。

#### params.request 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| certType | INTEGER | **是** | 资质类型 |
| productId | LONG | **是** | 商品 ID |

### 响应结构

#### 网关与脚本解析字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断；不得把 0 或 false 当作空值。 |
| errmsg | string | 网关消息；按实际响应保留。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 问题，1003 表示转发失败。 |
| body | string | Temu 原始 JSON 字符串；先判断网关状态，再读取内部业务结果。 |
| temuBody | JSON 值 | 脚本在 body 为有效非空 JSON 字符串时添加的解析结果，业务正常结构通常为 object；解析失败时保留原 body，不补造此字段。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer / null | 业务封装记录的实际 HTTP 状态码；连接失败未收到响应时为 null。随完整响应保存，不是网关业务字段；HTTP 401 / 402 按认证与算力指引处理，不以 JSON 内的成功字段覆盖 HTTP 错误。 |

#### Temu body / temuBody 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 业务是否成功 |
| errorCode | INTEGER | 业务错误码 |
| errorMsg | STRING | 业务错误消息 |
| result | OBJECT | 业务结果；未展开的子字段以实际响应为准 |

#### result 子字段（以下路径相对 result）

| 参数 | 类型 | 说明 |
|------|------|------|
| certNeedUploadItems[] | OBJECT[] | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].aliasName | STRING | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].contentType | INTEGER | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].expireDays | INTEGER | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].expireNoticeDays | INTEGER | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].expireTime | INTEGER | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].expireType | INTEGER | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].hasExpireTime | BOOLEAN | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |
| certNeedUploadItems[].needShowCustomer | BOOLEAN | 来自 Partner 响应示例；字段含义和枚举未声明，以实际响应为准 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002`：核对参数和 LinkFox Token；`code=1003`：检查 Temu token、IP 白名单及网络。不要把未说明的 code 数值推断为成功。
- 网关正常后，解析 `body`，根据 Temu `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；仅 HTTP 成功不代表 Temu 业务成功。errorCode 的统一成功值及完整业务枚举未定义，不自行推断。
- `body` 解析失败时展示响应原始文本与解析失败事实；不将空结果、缺失字段或已提交请求解释为审核通过。

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
  "type": "bg.arbok.open.cert.queryNeedUploadItems",
  "params": {
    "request": {
      "certType": 1,
      "productId": 1
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
  "skillName": "linkfox-temu-compliance-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
