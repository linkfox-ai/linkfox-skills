# Google Trends 时下流行趋势 接口说明

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

## 接口：按时间范围查询热门趋势（getTrendByTime）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/googleTrend/getTrendByTime`

### 请求参数

#### POST Body（JSON）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| days | integer | 否 | 7 | 查询最近多少天的趋势；常用值为 1（过去 24 小时）、2、7（过去一周），不是限定枚举。本接口用于近期或实时趋势，不用于数月、数年的长期历史分析。 |
| region | string | 否 | US | 国家或地区代码，仅支持以下 18 个地区：US（美国）、GB（英国）、JP（日本）、CA（加拿大）、MX（墨西哥）、DE（德国）、FR（法国）、IT（意大利）、ES（西班牙）、NL（荷兰）、AU（澳大利亚）、SG（新加坡）、AE（阿联酋）、BR（巴西）、IN（印度）、TR（土耳其）、PL（波兰）、SE（瑞典）。不支持的代码会产生错误。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 第一个位置参数；内容为上述 POST Body，未指定筛选条件时可传 `{}`。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时保存完整文件。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；默认启用 24 小时缓存。 |

- 缓存键算法：对原始 JSON 参数按键排序并序列化，取 SHA-256 前 16 位。缓存文件为 `<cwd>/linkfox/.cache/linkfox-google-trend-get-trend-by-time/linkfox-google-trend-get-trend-by-time-<参数哈希>.json`，以文件修改时间计算 24 小时有效期；命中时添加 `_cache.hit=true`。不补齐默认参数后再计算键，不叠加第二层缓存。
- 脚本会缓存收到的响应，包括错误或空结果；缓存命中不代表业务成功，仍须按响应码规则判断。使用 `--no-cache` 重新查询会产生新的接口调用。
- 脚本通过公共调用器执行请求与缓存。业务封装将输出根目录固定为当前工作目录的 `linkfox/`；请求前检查可写性，失败则报错，不回退到工作区环境变量、家目录或临时目录，禁止写入 `/tmp`。
- 支持双密钥环境变量，优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；支持 `LINKFOX_TOOL_GATEWAY` 覆盖及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共规则判断。 |
| errmsg | string | 错误原因；如认证失败时为 `authorized error`。 |
| errorCode | 未约定 | 另一种返回码字段：200 表示成功，其他值表示业务错误，401 表示认证失败。按实际返回的字段解释；字段缺失时仍按公共规则判断，不额外判为失败。 |
| costToken | integer | 消耗的 token 数量。 |
| chartOption | object | 图表配置对象，包含可视化数据。 |
| chartOption.data | array | 图表数据点对象数组。 |
| chartOption.fieldX | string | X 轴字段。 |
| chartOption.fieldY | array | Y 轴字段。 |
| chartOption.type | string | 数据类型。 |
| chartOption.title | string | 图表标题。 |
| trendValues | array | 热门查询对象数组，元素结构见下表。 |

#### trendValues 元素结构

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 热门搜索关键词。 |
| searchVolume | integer | 相对搜索量值，不是绝对搜索次数。 |
| increasePercentage | integer | 涨幅百分比；整数，范围 −100～100，单位为 %。 |
| startTime | string | 趋势观察窗口的开始时间戳。 |
| endTime | string | 趋势观察窗口的结束时间戳。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口未定义独立业务错误码；空趋势列表只能说明本次条件下未返回趋势，不据此编造热门话题或自动扩大检索范围。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/googleTrend/getTrendByTime" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"days": 7, "region": "US"}'
```

### 响应示例

认证失败示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-google-trend-get-trend-by-time",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```