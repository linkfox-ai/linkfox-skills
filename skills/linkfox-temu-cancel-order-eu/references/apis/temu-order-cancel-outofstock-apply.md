# 缺货取消申请接口说明

接口导航：[完整接口清单](../api.md)。脚本：`scripts/eu_seller_cancel_order_cancel_outofstock_apply.py`（相对技能根目录）；[脚本运行约定](../api.md#脚本运行约定)。

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

商家主动发起缺货情况，提交风控部门审核。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 （按 type 打开）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body 与脚本认证参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是；EU 脚本可省略 | EU 脚本默认 `eu`；通用脚本需显式填写。通用兼容值 `cn` / `partner` / `us` / `global` / `eu`，须小写并与令牌区域一致。 |
| managementType | string | 是；EU 脚本可省略 | EU 脚本默认 `semi-managed`；通用脚本显式传入 `full-managed` / `semi-managed`，须小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先使用。不是 LinkFox 用户密钥。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键；按 site、managementType、tokenPurpose 读取后，仅把 accessToken 发给网关。 |
| tokenPurpose | string | 否 | EU 默认 `order-shipping`；通用脚本默认 `default`。令牌用途维度，仅供脚本本地解析。 |
| token / linkfoxToken / linkfox_token | string | 否 | 脚本 LinkFox 密钥兼容参数，按此顺序优先于环境变量；不进入业务载荷。 |
| type | string | 是 | 本接口固定值见下方；专用脚本自动填入，`temu_eu_proxy.py` / `temu_proxy.py` 需显式提供。 |
| params | object | 否 | Temu 业务参数；本接口业务字段位于 `params.request`。EU 脚本也接受顶层 `request`，显式对象 `params` 优先。 |
| params.request | OBJECT | 否 | 官方标注为选填的业务请求对象；提供时须满足下列必填字段约束。 |


本接口 `type` 固定为 `temu.order.cancel.outofstock.apply`；Temu 的 type 在 Body，不是 URL path。兼容请求头 `Token` 与 `Authorization` 同值。

#### `request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | 父订单号 |
| orderSnList | STRING[] | **是** | 子订单号列表 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态（若返回），按公共响应码基本规则判断。 |
| errmsg | string | 网关错误信息（若返回）。 |
| body | string | Temu 原始 JSON 字符串；脚本保留原值，并在合法 JSON 时解析为 `temuBody`。 |
| code | integer | 网关错误码：`1002` 参数或 Token 错误，`1003` 转发失败。 |
| temuBody | object / array / scalar | 脚本附加的 body 解析结果；无效 JSON 时不附加。业务字段见下表，不补造缺失字段。 |
| transportHttpStatus | integer / null | 脚本附加的 LinkFox 外层 HTTP 状态；连接失败为 null。 |


下列为 `temuBody`（即原始 body 解析后）的业务字段。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 缺货申请结果 |

#### `temuBody.result`

| 参数 | 类型 | 说明 |
|------|------|------|
| applyResult | BOOLEAN | 缺货申请结果：`true` = 申请成功；`false` = 申请失败 |
| failReasonList | OBJECT[] | 申请失败原因列表；`applyResult=true` 时通常为空或不返回 |

#### `temuBody.result.failReasonList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderSn | STRING | 父订单号 |
| orderSn | STRING | 子订单号 |
| reasonList | STRING[] | 申请失败原因码列表 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002`：核对参数及 LinkFox 用户密钥；`code=1003`：核对 Temu 令牌、用途、IP 白名单和网络。先判断网关，再解析 `body`，依据 Temu `success`、`errorCode`、`errorMsg`、`result` 解释业务结果。

- 缺货提交风控审核。`applyResult=true` 仅表示申请成功；失败时查看逐单 `failReasonList.reasonList`，后续用缺货审核结果接口查询最终进度。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
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
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-cancel-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
