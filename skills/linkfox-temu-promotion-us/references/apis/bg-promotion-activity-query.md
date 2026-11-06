# Temu 美国站促销：促销活动查询 接口说明

> Partner 接口文档：<https://partner-us.temu.com/documentation?menu_code=873ac072a78249c893e5f8d0e656a11f&sub_menu_code=05820fed7179430c8e353905692d51b6>；脚本：`scripts/us_promotion_activity_query.py`。

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

## 接口：促销活动查询（bg.promotion.activity.query）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站使用 us；US 脚本默认 us。通用兼容脚本支持 cn / partner / us / global / eu，须小写。 |
| managementType | string | 是 | US 脚本默认 semi-managed；通用脚本支持 full-managed / semi-managed，须小写；具体权限以授权店铺为准。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本可用本地 storeKey 解析后填入，不能以 LinkFox API key 替代。 |
| type | string | 是 | 本接口操作标识，见本节接口标题；它位于 Body，不是 URL path。 |
| tokenPurpose | string | 否 | 建议使用 product-inventory；脚本仅将其用于本地令牌匹配，不发送此字段。 |
| params | object | 否 | 本接口的业务载荷，按下方 params.request 结构提供。 |
| params.request | OBJECT | 否（官方顶层标记） | 官方请求表将 request 标为选填（False）；下表标为必填的子字段仍须在 params.request 提供。 |

#### 脚本认证与业务参数约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessToken / storeKey | string | 二选一 | 直接令牌优先；storeKey 仅为本地令牌索引，不发送网关。 |
| site | string | 否 | US 脚本默认 us；通用脚本必填，支持站点见网关表。 |
| managementType | string | 否 | US 脚本默认 semi-managed；通用脚本必填。 |
| tokenPurpose | string | 否 | US 脚本默认 product-inventory；通用脚本默认 default。令牌按 storeKey + site + managementType + tokenPurpose 精确匹配，不跨店铺或用途回退。 |
| token / linkfoxToken / linkfox_token | string | 否 | 兼容的 LinkFox 鉴权字段，依次取首个非空值，优先于两种 API key 环境变量；仅用于请求头，不混入业务载荷。 |
| params | object | 否 | 显式对象优先；未提供对象时 US 脚本将顶层非保留业务字段（如 request）收集为 params；通用 temu_proxy.py 只接受显式 params 对象。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 保留兼容选项；业务封装始终向 call_api.run 添加此选项，不读取或保存响应缓存。 |

保留参数集合为 token、linkfoxToken、linkfox_token、accessToken、storeKey、site、managementType、tokenPurpose、type、params。通用 temu_us_proxy.py 的 type 必填，专用促销脚本固定 type。授权步骤见 [access-token.md](../access-token.md)。

#### `params.request` 内字段

| 参数 | 类型 | 必填 | 说明 |
| ------ | ------ | ------ | ------ |
| pageNumber | INTEGER | **是** | 分页页码，默认 1；该字段仍为必填。 |
| activityEndTime | LONG | 否 | 查询活动的结束时间，秒级时间戳。 |
| activityIdList | LONG[] | 否 | 活动的唯一标识。 |
| activityStatus | INTEGER | 否 | 活动状态，见下方 activityStatus 枚举。 |
| pageSize | INTEGER | **是** | 每页条数，默认 10，最大 100；该字段仍为必填。 |
| activityStartTime | LONG | 否 | 查询活动的开始时间，秒级时间戳。 |
| activityType | INTEGER | **是** | 活动类型，见下方 activityType 枚举。 |
| onlyQueryJoinedActivity | BOOLEAN | 否 | 是否仅查询已报名活动，TRUE / FALSE。 |

#### `activityType`（必填）

| 值 | 说明 |
| ---- | ------ |
| `2` | 秒杀 |
| `13` | 提前大促 |
| `27` | 清仓促销 |
| `100` | 官方大促 |

#### `activityStatus`（入参筛选）

| 值 | 说明 |
| ---- | ------ |
| `1` | 未开始 |
| `2` | 进行中 |
| `3` | 已结束 |

### 响应结构

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，依公共响应码基本规则判断。 |
| errmsg | string | 网关错误消息，若返回则按实际内容解释。 |
| body | string | Temu 原始 JSON 字符串，脚本保留原文并尝试解析。 |
| code | integer | 网关业务错误码：1002 参数或 Token 无效；1003 转发失败。不能替代 errcode 的公共判断。 |
| temuBody | 任意 JSON 类型 | 脚本解析字段：body 能解析为 JSON 时的业务对象；解析失败时不添加，仍保留 body。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| rawResponse | 任意 JSON 类型 | 仅网关返回非对象 JSON 时，脚本用此字段保留原值。 |
| error / details | string | 连接错误或非 JSON 响应的说明与原文；HTTP 成功但响应非 JSON 时也保留，不自动重试。 |

#### Temu 顶层字段

以下字段位于解析后的 temuBody 根级或其 response 内；须按实际层级读取。

| 参数 | 类型 | 说明 |
| ------ | ------ | ------ |
| success | BOOLEAN | 当前请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码。 |
| errorMsg | STRING | Temu 业务错误消息。 |
| result | OBJECT 或 OBJECT[] | 业务结果支持 OBJECT 或 OBJECT[]；本接口按对象读取。 |

#### `result`

| 参数 | 类型 | 说明 |
| ------ | ------ | ------ |
| total | LONG | 匹配活动总数。 |
| activityList | OBJECT[] | 活动列表。 |

#### `activityList[]`

| 参数 | 类型 | 说明 |
| ------ | ------ | ------ |
| activityId | LONG | 活动的唯一标识（活动 ID）。 |
| activityName | STRING | 活动名称。 |
| activityType | INTEGER | 活动类型，见入参 activityType 枚举。 |
| activityStatus | INTEGER | 活动状态：1 未开始，2 进行中，3 已结束。 |
| activityStartTime | LONG | 活动开始时间，秒级时间戳。 |
| activityEndTime | LONG | 活动结束时间，秒级时间戳。 |
| isJoinedActivity | BOOLEAN | 卖家是否已报名该活动。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 表示参数或 Token 无效，code=1003 表示转发失败。网关正常时解析 body，并按 Temu 的 success / errorCode / errorMsg 判断业务结果。
- body 不能解析时保留原文，不将传输完成或空结果当作业务成功。

| errorCode | errorMsg | 说明 / 处理建议 |
|-----------|----------|----------------------|
| 220010001 | parameter is illegal | 按 Partner 文档核对入参、活动状态或服务异常；后续调用遵守成本约束。 |
| 220010002 | system error, please try again later | 按 Partner 文档核对入参、活动状态或服务异常；后续调用遵守成本约束。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.promotion.activity.query",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 20,
      "activityType": 2,
      "activityStatus": 2,
      "onlyQueryJoinedActivity": false
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
  "skillName": "linkfox-temu-promotion-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
