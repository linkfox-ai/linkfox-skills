# 活动已报名商品查询 接口说明

Partner 文档定位见 [目录](../partner-eu-catalog.md)；接口索引见 [README.md](README.md)，网关与运行约定见 [../api.md](../api.md)。

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

## 接口：活动已报名商品查询（bg.promotion.activity.goods.query）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body 与脚本输入

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 欧洲站默认 `eu`。通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，须与授权区域一致。 |
| managementType | string | 是 | 默认 `semi-managed`；通用脚本允许 `full-managed` / `semi-managed`，须与授权一致。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先使用。脚本解析本地 storeKey 后仅向网关发送 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 使用 storeKey + site + managementType + tokenPurpose 定位令牌。业务脚本从 `~/.linkfox/temu-access-tokens.json` 本地解析该键，不随构造后的请求发送。 |
| tokenPurpose | string | 否 | 可选的令牌用途字段，建议 `product-inventory`；欧洲站封装读取 storeKey 时以此为默认值，本地查找后不随构造后的请求发送。 |
| type | string | 是 | 固定 `bg.promotion.activity.goods.query`；专用脚本自动填写，通用代理须显式提供。 |
| params | object | 否 | 业务参数对象，本接口使用 `params.request`。 |
| params.request | OBJECT | 官方标为选填 | 其内部标为必填的字段仍必须提供。 |

专用脚本和 `temu_eu_proxy.py` 允许顶层 `request` 或 `params.request`；显式对象 `params` 优先，否则去除网关与认证保留字段后整体作为 params。脚本不会自动把裸业务字段包成 request。通用 `temu_proxy.py` 仅转发显式 params，不做此提取；必须显式提供 site 与 managementType。

#### 脚本选项与认证

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，优先级按此顺序，高于环境变量；不会进入业务 params。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 接受该选项；业务封装始终向 call_api.run 传入 --no-cache，不读取或写入响应缓存。 |

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 默认网关；密钥环境变量优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。网关请求发送同值 `Authorization` 与 `Token` 请求头。

#### params.request 内字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| activityId | LONG | 是 | 活动唯一标识。 |
| pageNumber | INTEGER | 是 | 页码，官方默认 1；仍须显式提供。 |
| pageSize | INTEGER | 是 | 每页条数，官方默认 10，最大 100；仍须显式提供。 |


### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若网关返回此字段，按公共响应码基本规则判断，不将 0 或 false 视为空。 |
| errmsg | string | 网关返回的错误说明（如有）。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 问题，1003 表示转发失败；其他值按实际响应判断，不推测成功码。 |
| body | string | Temu 原始 JSON 字符串；脚本保留原值，并在可解析时增加 temuBody。 |
| transportHttpStatus | integer / null | 脚本增加的外层 HTTP 状态；连接失败为 null，不属于 Temu 上游状态码。 |
| temuBody | JSON value | 仅 body 为有效 JSON 字符串时增加；业务响应通常是 object / array，保留实际 JSON 类型。Temu 可在根级或 response 内返回业务对象，脚本不擅自改写层级。 |
| error | string | 连接失败、非 JSON 的 HTTP 错误或网关返回非对象时的脚本错误说明。 |
| details | string | HTTP 错误响应不是 JSON 时保留其原始文本。 |
| gatewayBody | JSON value | 仅网关返回非对象时保留原响应，并同时标记 error。 |

#### Temu body 解析后：根级或 response 内

| 字段 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | 当前请求是否成功。 |
| errorCode | INTEGER | Temu 错误码。 |
| errorMsg | STRING | Temu 错误消息。 |
| result | OBJECT 或 OBJECT[] | 业务结果；本接口按对象结构展示，保留实际返回类型。 |

#### result

| 字段 | 类型 | 说明 |
|---|---|---|
| total | LONG | 总记录数。 |
| activityInfo | OBJECT | 当前活动信息。 |
| goodsList | OBJECT[] | 已报名商品列表。 |

#### result.activityInfo

| 字段 | 类型 | 说明 |
|---|---|---|
| activityId | LONG | 活动唯一标识。 |
| activityName | STRING | 活动名称。 |
| activityType | INTEGER | 活动类型；查询枚举为 2（秒杀）、13（预热大促）、27（清仓）、100（官方大促）。 |
| activityStatus | INTEGER | 活动状态：1 未开始，2 进行中，3 已结束。 |
| activityStartTime | LONG | 活动开始时间，秒级时间戳。 |
| activityEndTime | LONG | 活动结束时间，秒级时间戳。 |
| isJoinedActivity | BOOLEAN | 卖家是否已参加该活动。 |

#### result.goodsList[]

| 字段 | 类型 | 说明 |
|---|---|---|
| goodsId | LONG | 商品标识。 |
| activityQuantity | INTEGER | 活动数量或名额。 |
| remainingActivityQuantity | INTEGER | 剩余活动数量。 |
| skuList | OBJECT[] | 已报名 SKU 列表。 |

#### result.goodsList[].skuList[]

| 字段 | 类型 | 说明 |
|---|---|---|
| skuId | LONG | SKU 标识。 |
| activitySupplierPrice | LONG | 活动供货价。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 表示参数或 LinkFox Token 问题；code=1003 表示转发失败，核对 Temu 令牌、用途、IP 白名单和网络。不得仅因可解析 body 就认定业务成功。
- 网关正常后解析 body，再根据 Temu success、errorCode、errorMsg 与 result 判断；success=false 表示业务失败。响应无法解析时保留 body 原文，不补造业务对象。

#### Partner 错误码

| errorCode | errorMsg（原值） | 说明与处理 |
|---|---|---|
| 220010001 | parameter is illegal | 参数非法；核对请求字段与活动状态。 |
| 220010002 | system error, please try again later | 系统异常；说明原因，后续调用遵守调用约束。 |
| 220010003 | The activity has been cancelled, please select another activity to participate | 活动已取消；说明原因，由用户决定是否更换活动。 |
| 220010004 | The activity has ended, please select another activity to participate | 活动已结束；说明原因，由用户决定是否更换活动。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.promotion.activity.goods.query",
  "params": {
    "request": {
      "activityId": 123456,
      "pageNumber": 1,
      "pageSize": 20
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
  "skillName": "linkfox-temu-promotion-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
