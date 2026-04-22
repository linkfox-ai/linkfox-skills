# Jungle Scout ASIN 销售估算 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/sales-estimates/query`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| asin | string | 是 | 要查询的亚马逊 ASIN |
| startDate | string | 是 | 开始日期（格式：YYYY-MM-DD） |
| endDate | string | 是 | 结束日期（格式：YYYY-MM-DD）；必须早于当前日期 |

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
| salesEstimateList | array | 销售估算结果列表 |

### salesEstimateList 数组中每个对象

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

### dailyEstimates 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 数据日期（YYYY-MM-DD） |
| estimatedUnitsSold | integer | 当日预估售出件数 |
| lastKnownPrice | number | 最近已知价格（USD） |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `salesEstimateList` |
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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/sales-estimates/query \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "asin": "B0CXXX1234", "startDate": "2026-03-01", "endDate": "2026-03-31"}'
```

## 响应示例

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

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-junglescout-sales-estimates",
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
