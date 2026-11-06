# Google Trends 关键词趋势信息 接口说明

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

## 接口：关键词趋势信息（getTrendByKeys）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/googleTrend/getTrendByKeys`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词，最大长度 100 字符。必须使用目标国家的语言，例如美国用英语、德国用德语、日本用日语；不匹配时先翻译。 |
| region | string | 否 | 国家或地区，默认 `US`。可选值：US（美国）、GB（英国）、JP（日本）、CA（加拿大）、MX（墨西哥）、DE（德国）、FR（法国）、IT（意大利）、ES（西班牙）、NL（荷兰）、AU（澳大利亚）、SG（新加坡）、AE（阿联酋）、BR（巴西）、IN（印度）、TR（土耳其）、PL（波兰）、SE（瑞典）。 |
| dayRangeStart | string | 否 | 自定义时间范围开始日期，格式 `YYYY-MM-DD`，从 2004 年起。与 `dayRangeEnd` 同时提供时，自定义时间范围优先。 |
| dayRangeEnd | string | 否 | 自定义时间范围结束日期，格式 `YYYY-MM-DD`，从 2004 年起。与 `dayRangeStart` 同时提供时，自定义时间范围优先。 |

#### 使用限制

- 每次调用处理一个关键词；多个关键词、地区或不同时间范围的对比需分别调用，遵守 SKILL.md 的成本约束。
- 数据自 2004 年起可用，小众词可能数据稀疏。接口提供相对兴趣值，不提供绝对搜索量。
- 单独提供开始日期或结束日期时，不推定另一端的默认日期，以实际返回的时间范围为准。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | string | 是 | 第一个位置参数，内容为上述请求体 JSON。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时保存完整 JSON。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存的读取和写入；默认启用 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 显示用法，不请求接口。 |

缓存使用 `<cwd>/linkfox/.cache/linkfox-google-trend-get-trend-by-keys/` 路径，以排序后的参数 JSON 的 SHA-256 前 16 位生成文件名，有效期为文件修改时间起 24 小时。仅使用公共调用器的一层缓存；命中时在字典响应中标记 `_cache.hit=true`，并仍然保存完整响应。收到的错误或空结果也会缓存，不自动更换参数或重试；需要绕过缓存时由调用者明确使用 `--no-cache`。

`LINKFOX_TOOL_GATEWAY` 优先，未设置时使用公共规则中的默认地址；认证兼容两种密钥变量。请求保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。趋势脚本在请求前拒绝 `/tmp` 及其子目录，并检查当前工作目录的 `linkfox/` 是否可写；响应固定写到当前工作目录，禁止自动回退到家目录或临时目录。预检失败或后续响应文件未完整保存时，以非零状态退出，不自动重复请求。公共认证引导脚本的运行方式见 `onboarding.md`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| trendInfoForKeys | array | 关键词趋势信息数组。 |
| trendInfoForKeys[].keyword | string | 关键词。 |
| trendInfoForKeys[].trendValues | array | 趋势值数组。 |
| trendInfoForKeys[].trendValues[].timeRange | string | 时间，格式为 `yyyy-MM-dd`，保留原值。 |
| trendInfoForKeys[].trendValues[].value | string | 归一化搜索热度，0–100。可能出现 `"<1"` 等字符串，必须保留，不能转为零。 |
| chartOption | object | 图表渲染元数据。 |
| chartOption.type | string | 数据类型。 |
| chartOption.fieldX | string | X 轴字段。 |
| chartOption.fieldY | array | Y 轴字段。 |
| chartOption.data | array | 图表数据。 |
| costToken | integer | 消耗 Token 数量。 |
| errcode | integer | 业务错误码，例如 `401`；正常与异常判断使用公共规则。 |
| errmsg | string | 错误消息，例如 `authorized error`，用于解释具体原因。 |
| errorCode | 未限定 | 业务码字段，`200` 表示成功，其他值用于说明业务错误；类型和完整封装以实际响应为准，不据此覆盖公共响应码基本规则。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 趋势列表为空或小众词数据稀疏时，说明当前关键词、地区与时间范围内数据不足，不把空结果直接判断为接口错误；可建议核对拼写、目标语言或日期范围，继续请求前遵守成本约束。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/googleTrend/getTrendByKeys \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "wireless charger", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-01-01"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-google-trend-get-trend-by-keys",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
