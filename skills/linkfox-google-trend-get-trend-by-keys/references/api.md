# 谷歌趋势-关键词趋势信息 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/googleTrend/getTrendByKeys`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词（关键词必须是国家的语言！比如美国要用英语关键词，德国要用德语关键词。如果不是对应国家的语言，请先翻译。）最大长度100字符 |
| region | string | 否 | 国家/地区，默认 `US`。可选值：US、GB、JP、CA、MX、DE、FR、IT、ES、NL、AU、SG、AE、BR、IN、TR、PL、SE |
| dayRangeStart | string | 否 | 时间范围开始时间（希望自由指定时间范围时使用，以时间范围优先），格式为YYYY-MM-DD，从2004年开始 |
| dayRangeEnd | string | 否 | 时间范围结束时间（希望自由指定时间范围时使用，以时间范围优先），格式为YYYY-MM-DD，从2004年开始 |

- 当同时提供 `dayRangeStart` 和 `dayRangeEnd` 时，自定义时间范围优先

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| trendInfoForKeys | array | 关键词趋势信息数组 |
| trendInfoForKeys[].keyword | string | 关键词 |
| trendInfoForKeys[].trendValues | array | 趋势值数组 |
| trendInfoForKeys[].trendValues[].timeRange | string | 时间，格式为 yyyy-MM-dd |
| trendInfoForKeys[].trendValues[].value | string | 值（归一化搜索热度，0-100） |
| chartOption | object | 图表渲染元数据 |
| chartOption.type | string | 数据类型 |
| chartOption.fieldX | string | X轴字段 |
| chartOption.fieldY | array | Y轴字段 |
| chartOption.data | array | 数据 |
| costToken | integer | 消耗token |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/googleTrend/getTrendByKeys \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless charger", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-01-01"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
