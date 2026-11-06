# 缺货取消申请 接口说明

返回总览见 [../api.md](../api.md)，运行与授权约定见其“脚本运行约定”。

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

## 接口：缺货取消申请（temu.order.cancel.outofstock.apply）

提交缺货取消风控审核。

> Partner 文档：https://partner-us.temu.com/documentation（menu_code / sub_menu_code 尚未确认，以后台该接口页为准）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/openapi/router`；上游 `https://openapi-b-us.temu.com/openapi/router`，Body 的 `type` 固定为 `temu.order.cancel.outofstock.apply`，不是 URL 路径。对应脚本：`scripts/us_seller_cancel_order_cancel_outofstock_apply.py`。

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 美国站为 `us`；美国站脚本默认 `us`，去首尾空白并转小写。 |
| managementType | string | 是 | `semi-managed` / `full-managed`；美国站脚本默认 `semi-managed`，去首尾空白并转小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用直接传入值，否则从本地读取后填入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键，不原样转发；与 site、managementType、tokenPurpose 一起选择令牌。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；美国站脚本在 storeKey 且未直接传 accessToken、未指定用途时默认使用该值。本字段用于本地令牌选择，不原样转发。 |
| type | string | 是 | 本接口的 Temu 操作名，见本节；专用脚本固定该值，不采用用户覆盖值。 |
| params | object | 否 | 业务参数；本技能取消操作使用 `params.request`。通用代理允许传其他已知操作的业务块，但不增加本技能接口定义。 |

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序取第一个非空值，优先于环境变量；仅供 LinkFox 用户鉴权，不转发为 Temu 业务字段。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 条件必需 | JSON 未提供 LinkFox 密钥时，按此顺序取值。 |
| --inline | CLI flag | 否 | 强制全量打印，完整响应仍落盘。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI 选项；业务封装每次调用 run 均强制附加，不读取或保存响应缓存。 |

#### params.request 业务字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| params.request | OBJECT | 否 | 官方 request 容器标注选填；若提供，下列内部必填字段仍须满足。 |
| params.request.parentOrderSn | STRING | 是 | 父订单号。 |
| params.request.orderSnList | STRING[] | 是 | 子订单号列表。 |

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|---|---|---|
| _http_status | integer / null | 脚本附加的本地 HTTP 传输状态，连接失败为 null；用于判断公共 HTTP 规则，不是网关或 Temu 业务字段。大响应摘要前也单独输出该状态。 |
| errcode | integer / string / null | 网关状态按公共规则判断；不替代 Temu 业务状态。 |
| errmsg | string | 网关错误说明；有错误时保留实际消息。 |
| code | integer | 网关 code 错误码：1002 为参数或 Token 错误，1003 为转发失败；不得当成 Temu errorCode。 |
| body | string | Temu 原始 JSON 字符串；代理脚本尝试解析为 temuBody，原始 body 保留。 |
| temuBody | object / array / scalar / null | 代理脚本附加的解析结果，类型以实际 JSON 为准；body 为空或不是合法 JSON 时不附加。 |
| error | string | 脚本生成的连接错误或异常响应说明；出现时不能视为业务成功。 |
| gatewayResponse | 任意 JSON 类型 | 仅网关顶层返回非对象 JSON 时由脚本附加，完整保留异常原值；与正常响应的 body 不同。 |

#### Temu body / temuBody 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码。 |
| errorMsg | STRING | Temu 业务错误信息。 |
| result | OBJECT | 具体业务结果，见下方。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| result.applyResult | BOOLEAN | 缺货申请受理结果：true 申请成功，false 申请失败；不代表最终审核通过。 |
| result.failReasonList | OBJECT[] | 申请失败原因列表；applyResult=true 时通常为空或不返回。 |
| result.failReasonList[].parentOrderSn | STRING | 父订单号。 |
| result.failReasonList[].orderSn | STRING | 子订单号。 |
| result.failReasonList[].reasonList | STRING[] | 申请失败原因码列表，按实际返回解释，不补造枚举。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 为参数或 LinkFox Token 问题，`code=1003` 为转发失败；结合 Temu token、用途、IP 白名单和网络排查。
- 在网关响应正常且未报告上述网关错误后，再解析 body，结合 Temu `success`、`errorCode`、`errorMsg` 和 result 判断；Temu 失败不视为业务成功，保留原始消息。
- 缺货申请提交风控部门审核；applyResult 仅说明申请受理结果，同时检查 failReasonList。父子订单从订单列表或详情取得。

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
  "type": "temu.order.cancel.outofstock.apply",
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
  "skillName": "linkfox-temu-cancel-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
