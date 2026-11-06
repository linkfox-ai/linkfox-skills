# Jungle Scout ASIN 销售估算 接口说明

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

## 接口：ASIN 销售估算

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/sales-estimates/query`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码；请求体必填，用户未指定站点时由调用方填入 `us`，并非服务端可省略。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| asin | string | 是 | 要查询的标准亚马逊 ASIN，共 10 位，通常以 B0 开头；每次仅查询一个 ASIN，多 ASIN 对比需分别请求 |
| startDate | string | 是 | 开始日期（格式：YYYY-MM-DD） |
| endDate | string | 是 | 结束日期（格式：YYYY-MM-DD）；必须早于当前日期 |

#### 站点映射

| 站点 | marketplace 值 |
|------|---------------|
| 美国 | us |
| 英国 | uk |
| 德国 | de |
| 印度 | in |
| 加拿大 | ca |
| 法国 | fr |
| 意大利 | it |
| 西班牙 | es |
| 墨西哥 | mx |
| 日本 | jp |

#### 日期换算与使用限制

- 不能查询今天或未来的销量；本工具不提供实时销量。
- “过去 30 天”：结束日期取昨天，开始日期取当前日期前 30 天；“上个月”：上月 1 日至上月末日。
- “Q3 与 Q4 对比”：分别请求同一年的 7 月 1 日至 9 月 30 日、10 月 1 日至 12 月 31 日。仅查询已经过去的区间，不将未结束季度的未来日期直接用于请求。
- 日期相对实际执行日换算；脚本透传 JSON，不自动补齐必填项或修正日期，应在调用前核对。

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数是 JSON 字符串，字段见上表；脚本透传参数 |
| --inline | CLI flag | 否 | 强制完整打印，同时仍保存完整响应 |
| --no-cache | CLI flag | 否 | 禁止读取和写入响应缓存；不传时使用 24 小时本地缓存 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用配置值并去除末尾 `/`，默认值见公共规则 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是，二选一 | 优先前者，兼容后者；两者均为空时退出并提示 API Key 未配置 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 脚本将其传入同名请求头，未配置时为空字符串 |

调用入口：`python scripts/junglescout_sales_estimates.py '<JSON 参数>' [--inline] [--no-cache]`。
业务脚本在请求前检查当前工作目录下的会话数据目录可写，并固定公共调用器的输出根目录；不可写或位于 `/tmp` 下时退出，不回退到用户目录或临时目录。业务请求、缓存、会话数据保存与输出均委托 `call_api.run`，不另建缓存层。
缓存保存在 `<cwd>/linkfox/.cache/linkfox-junglescout-sales-estimates/`；键为按字段名排序后的参数 JSON 的 SHA-256 前 16 位。过期或损坏缓存视为未命中；成功、失败及空结果均可缓存，命中后不发请求。`--no-cache` 不读取或更新已有缓存。原始响应固定保存在当前工作目录下，不使用 `ACPX_WORKSPACES` 或其他目录兜底。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数；保留实际返回值，不与 SKILL.md 的算力估算混为一谈 |
| salesEstimateList | array | 销售估算结果列表 |
| errcode | integer / string / null | 网关业务状态码，若返回则按公共规则判断；认证失败示例为 401 |
| errmsg | string | 网关消息；认证失败消息示例为 `authorized error` |
| errorCode | 未约定类型 | 业务码：200 表示成功、其他值表示业务错误；错误响应也可能使用 errcode，以实际返回为准，不假定两字段同时存在 |

#### salesEstimateList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 查询的 ASIN |
| id | string | 数据点标识 |
| type | string | 资源类型，固定值 `sales_estimate_result` |
| parentAsin | string | 父体 ASIN（变体场景下返回） |
| isParent | boolean | 是否为父体商品 |
| isVariant | boolean | 是否为变体商品 |
| isStandalone | boolean | 是否为独立商品（非变体） |
| variants | array | 该父体下的变体 ASIN 数组 |
| dailyEstimates | array | 每日估算数据数组 |

#### dailyEstimates 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 数据日期（YYYY-MM-DD） |
| estimatedUnitsSold | integer | 当日预估售出件数 |
| lastKnownPrice | number | 最近已知价格（USD） |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 读取缓存时由脚本附加的标记，不是服务端业务字段 |
| _cache.hit | boolean | 缓存命中时为 true |
| error | string | HTTP 非 JSON 错误或连接失败时，公共调用器返回的错误说明 |
| details | string | HTTP 错误响应无法解析为 JSON 时保留的原始响应文本 |

`dailyEstimates` 每条记录代表一天；`lastKnownPrice` 单位为 USD（美元），不是目标站点本地货币。销量为预估值，价格为最近已知价格，不能视为该日实测销量或成交价。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后解析 `salesEstimateList`，保留父体、变体、独立商品标识与每日数据；空列表表示本次未取得估算，不据此推断实际销量为零。
- 响应可能包含 `errorCode` 或 `errcode`；`errorCode=200` 表示业务成功，其他值表示业务错误。依据实际返回的字段及消息解释业务异常，仍须按公共规则检查 HTTP 状态与 `errcode`。
- 日期或 ASIN 等查询条件不符合要求时，依据原始错误消息说明原因并给出调整建议；不自动改条件重试。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/sales-estimates/query" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace":"us","asin":"B0CXXX1234","startDate":"2026-03-01","endDate":"2026-03-31"}'
```

### 响应示例

```json
{
  "costToken": 1,
  "salesEstimateList": [
    {
      "asin": "B0CXXX1234",
      "id": "sales_estimate_B0CXXX1234_20260301",
      "type": "sales_estimate_result",
      "parentAsin": "B0CXXX0000",
      "isParent": false,
      "isVariant": true,
      "isStandalone": false,
      "variants": [],
      "dailyEstimates": [
        {
          "date": "2026-03-01",
          "estimatedUnitsSold": 35,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-02",
          "estimatedUnitsSold": 42,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-03",
          "estimatedUnitsSold": 38,
          "lastKnownPrice": 27.99
        }
      ]
    }
  ]
}
```

#### 错误响应示例

```json
{"errcode":401,"errmsg":"authorized error"}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-junglescout-sales-estimates",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```