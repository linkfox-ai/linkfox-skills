# Jungle Scout 关键词历史搜索量 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/historical-search-volume`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| keyword | string | 是 | 要查询的关键词 |
| startDate | string | 是 | 开始日期（格式：YYYY-MM-DD） |
| endDate | string | 是 | 结束日期（格式：YYYY-MM-DD）；与 startDate 间隔最大 366 天 |

### 站点映射

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

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| historicalSearchVolumeList | array | 历史搜索量周期列表 |

### historicalSearchVolumeList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 数据周期标识（市场/关键词/日期范围） |
| estimateStartDate | string | 周期开始日期（YYYY-MM-DD，7天统计周期起点） |
| estimateEndDate | string | 周期结束日期（YYYY-MM-DD，7天统计周期终点） |
| estimatedExactSearchVolume | integer | 该周期内精确匹配搜索量（次/周） |
| type | string | 资源类型，固定值 `historical_keyword_search_volume` |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `historicalSearchVolumeList` |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/historical-search-volume \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "keyword": "yoga mat", "startDate": "2025-10-01", "endDate": "2026-03-31"}'
```

## 响应示例

```json
{
  "costToken": 1,
  "historicalSearchVolumeList": [
    {
      "id": "us_yoga_mat_20251005_20251011",
      "estimateStartDate": "2025-10-05",
      "estimateEndDate": "2025-10-11",
      "estimatedExactSearchVolume": 85420,
      "type": "historical_keyword_search_volume"
    },
    {
      "id": "us_yoga_mat_20251012_20251018",
      "estimateStartDate": "2025-10-12",
      "estimateEndDate": "2025-10-18",
      "estimatedExactSearchVolume": 87650,
      "type": "historical_keyword_search_volume"
    }
  ]
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-junglescout-keyword-history",
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
