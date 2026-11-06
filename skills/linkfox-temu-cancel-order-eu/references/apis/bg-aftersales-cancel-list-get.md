# 取消订单售后列表查询接口说明

接口导航：[完整接口清单](../api.md)。脚本：`scripts/eu_cancel_aftersales_cancel_list_get.py`（相对技能根目录）；[脚本运行约定](../api.md#脚本运行约定)。

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

## 接口：取消订单售后列表查询（bg.aftersales.cancel.list.get）

查询取消订单售后信息。

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


本接口 `type` 固定为 `bg.aftersales.cancel.list.get`；Temu 的 type 在 Body，不是 URL path。兼容请求头 `Token` 与 `Authorization` 同值。

#### `request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageSize | INTEGER | 否 | 分页大小，**默认 10**，**最大 200** |
| pageNo | INTEGER | 否 | 分页页码，**默认 1** |
| parentOrderSnList | STRING[] | 否 | 父订单号列表；留空则不限制父订单号范围；**单次查询最多 200 条** |
| parentAfterSalesSnList | STRING[] | 否 | 父售后单号列表；留空则不限制父售后单号范围；**单次查询最多 200 条** |
| afterSalesStatusGroup | INTEGER | 否 | 取消订单售后状态组，见下表 |

##### `afterSalesStatusGroup`（入参筛选）

| 值 | 说明 |
|----|------|
| `8` | 取消订单待处理 |
| `9` | 取消订单已同意 |
| `10` | 取消订单已拒绝 |
| `11` | 取消订单已撤销 |

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
| result | OBJECT | 具体结果信息 |

#### `temuBody.result`

| 参数 | 类型 | 说明 |
|------|------|------|
| total | LONG | 匹配记录总数 |
| pageNumber | INTEGER | 当前结果页码 |
| data | OBJECT[] | 本次查询返回的记录 |

> 入参分页字段为 **`pageNo`**，出参当前页为 **`pageNumber`**，勿混用。

#### `temuBody.result.data[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentAfterSalesSn | STRING | 取消订单的父售后单号 |
| parentAfterSalesStatus | INTEGER | 当前父售后状态，见下表 |
| afterSalesInfoList | OBJECT[] | 取消订单售后信息列表 |

##### `parentAfterSalesStatus`（出参）

| 值 | 说明 |
|----|------|
| `1` | 买家已申请退款，待处理 |
| `4` | 退款已发起，系统处理中 |
| `5` | 退款已发放 |
| `6` | 买家已撤销售后申请 |
| `7` | 售后申请已被拒绝 |
| `9` | 退款已发起，系统处理中 |

#### `temuBody.result.data[].afterSalesInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| afterSalesSn | STRING | 售后单号 |
| parentOrderSn | STRING | 父订单号 |
| orderSn | STRING | 子订单号 |
| productSkuId | LONG | 商品 SKU ID |
| applyGoodsNumber | LONG | 申请取消数量 |
| goodsId | LONG | 商品 ID |
| productList | OBJECT[] | 产品信息列表 |
| createAtMillis | LONG | 售后单创建时间，毫秒 |

#### `temuBody.result.data[].afterSalesInfoList[].productList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| productSkuId | LONG | 商品 SKU ID |
| extCode | STRING | 商品外部编码 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002`：核对参数及 LinkFox 用户密钥；`code=1003`：核对 Temu 令牌、用途、IP 白名单和网络。先判断网关，再解析 `body`，依据 Temu `success`、`errorCode`、`errorMsg`、`result` 解释业务结果。

- 入参 `afterSalesStatusGroup` 与出参 `parentAfterSalesStatus` 是不同枚举；`pageNo` 为请求页码，`pageNumber` 为返回页码。

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
  "type": "bg.aftersales.cancel.list.get",
  "params": {
    "request": {
      "pageNo": 1,
      "pageSize": 20,
      "afterSalesStatusGroup": 8
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
