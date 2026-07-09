# 谷歌趋势-时下流行 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/googleTrend/getTrendByTime`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | integer | 否 | 时间范围，查询最近多少天的趋势数据，默认 `7`。常用值：1、2、7 |
| region | string | 否 | 国家/地区代码，默认 `US`。可选值：US、GB、JP、CA、MX、DE、FR、IT、ES、NL、AU、SG、AE、BR、IN、TR、PL、SE |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗token |
| chartOption | object | 图表配置对象，包含可视化数据 |
| chartOption.data | array | 数据，图表数据点对象数组 |
| chartOption.fieldX | string | X轴字段 |
| chartOption.fieldY | array | Y轴字段 |
| chartOption.type | string | 数据类型 |
| chartOption.title | string | 标题 |
| trendValues | array | 趋势值，热门查询对象数组（见下方） |

### trendValues 元素结构

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 关键词 |
| searchVolume | integer | 搜索量值 |
| increasePercentage | integer | 涨幅百分比：整数，取值范围 −100～100，单位为％ |
| startTime | string | 开始时间戳 |
| endTime | string | 结束时间戳 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
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
curl -X POST https://tool-gateway.linkfox.com/googleTrend/getTrendByTime \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "region": "US"}'
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
