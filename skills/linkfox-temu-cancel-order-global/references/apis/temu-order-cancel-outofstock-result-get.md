# Temu 全球站 查询缺货取消审核结果 接口说明

[接口总览与运行约定](../api.md)；[Partner 目录](../partner-global-catalog.md)。

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

## 接口：查询缺货取消审核结果（temu.order.cancel.outofstock.result.get）

> Partner 文档：https://partner-global.temu.com/documentation（menu_code / sub_menu_code 按 Partner 后台接口目录核对）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 全球站为 global，Global 专用脚本默认 global；非 US/EU。 |
| managementType | string | 是 | 本业务使用 semi-managed，Global 专用脚本默认此值。 |
| accessToken | string | 是 | Temu 店铺令牌。直接请求必须传入；脚本可从 storeKey 对应本地记录解析。 |
| type | string | 是 | 固定为 temu.order.cancel.outofstock.result.get，写在 Body 中，不是 URL 路径。 |
| params | object | 否 | 业务参数对象，业务块通常为 params.request；各字段见下表。 |

#### 业务参数（位于 params）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 官方业务请求对象；其内部必填项见下表。 |
| request.parentOrderSn | STRING | 是 | 父订单号；与缺货取消申请一致。 |
| request.orderSnList | STRING[] | 是 | 子订单号列表；与缺货取消申请一致。 |

#### 脚本选项与认证兼容

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| accessToken | string | 与 storeKey 二选一 | 直接传入优先；与 LinkFox 用户 Token 是不同令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺记录键；脚本读取令牌后只把 accessToken 发给网关，不转发 storeKey。 |
| site | string | 否 | Global 专用脚本去首尾空白并转小写，缺省或空值使用 global；通用兼容脚本要求显式传入小写 cn / partner / us / global / eu。 |
| managementType | string | 否 | Global 专用脚本去首尾空白并转小写，缺省或空值使用 semi-managed；通用兼容脚本要求显式传入小写 full-managed / semi-managed。 |
| tokenPurpose | string | 否 | Global 专用脚本读取 storeKey 时默认 order-shipping；通用兼容脚本默认 default。按店铺、站点、托管类型、用途精确查找，不跨用途回退。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户 Token，按上述顺序优先于环境变量 LINKFOX_AGENT_API_KEY、LINKFOXAGENT_API_KEY。同时发送 Authorization 与 Token 同值请求头，不转发为业务字段。 |
| params | object | 否 | Global 专用脚本优先使用嵌套 params 对象；未提供时，将除认证、站点、type、params 等保留键以外的顶层字段作为业务参数，例如顶层 request 整体进入 params.request。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时保存文件。 |
| --no-cache | CLI flag | 否 | 业务调用不使用响应缓存；业务封装调用 call_api.run 时始终加入此选项，读取与写入均不缓存响应。 |

基础地址依次取 LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com；默认超时 150 秒。请求携带 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。
完整响应必须落到当前工作目录，写入前检查可写性，不回退家目录或临时目录。公共调用器即使禁用缓存仍可能创建空的 .cache 目录，该目录不保存响应，也不会复用旧响应。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码，按公共规则判断；不把 0 或 false 当作空值。 |
| errmsg | string | 网关消息，以实际返回为准。 |
| code | integer | 网关错误码：1002 参数或 Token 无效；1003 转发失败。 |
| body | string | Temu 原始 JSON 字符串；脚本保留原值并尝试解析为 temuBody。 |
| temuBody | object / 实际 JSON 类型 | 脚本派生字段，仅 body 为非空且合法 JSON 字符串时新增；解析失败保留原始 body，不补造结果。 |
| _http_status | integer | 脚本本地附加字段，仅 HTTP 非 2xx 的对象响应添加，保存实际 HTTP 状态；不是网关返回字段。非对象响应保留原 JSON，状态另写标准错误输出。 |

#### Temu body 解析后的业务对象（脚本为 temuBody）

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 请求是否成功。 |
| errorCode | INTEGER | Temu 错误码。 |
| errorMsg | STRING | Temu 错误信息。 |
| result | OBJECT | 业务结果；子字段如下，未展开部分以实际响应为准。 |
| result.applyResultInfoList | OBJECT[] | 缺货取消申请结果信息列表。 |
| result.applyResultInfoList[].orderSn | STRING | 子订单号。 |
| result.applyResultInfoList[].applyStatus | INTEGER | 缺货申请审核状态；展示实际返回的状态值，仅在有明确状态定义时解释其含义。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 在公共基础判断后，检查网关 code；1002 为参数或 LinkFox Token 无效，修正参数或用户 Token；1003 为转发失败，核对 Temu token、tokenPurpose、IP 白名单和网络。
- 对 body 解析得到的 Temu 响应，依据 success、errorCode、errorMsg 与 result 判断业务结果；外层请求完成不表示订单已取消。
- 缺货取消是异步操作，提交后通过本接口获取最新审核状态；只解释已定义或实际返回的状态，不臆测 applyStatus 枚举。

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
  "type": "temu.order.cancel.outofstock.result.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789",
      "orderSnList": [
        "O-111111111"
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
  "skillName": "linkfox-temu-cancel-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
