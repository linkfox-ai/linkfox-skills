# Jungle Scout 关键词市场份额 Share of Voice API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/share-of-voice`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| keyword | string | 是 | 要查询的关键词 |

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

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| shareOfVoice | object | Share of Voice 数据主体 |

### shareOfVoice 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 资源标识 |
| type | string | 固定值 `share_of_voice` |
| estimated30DaySearchVolume | integer | 过去 30 天精确匹配搜索量 |
| exactSuggestedBidMedian | number | PPC 竞价中位数（美元） |
| productCount | integer | 前 3 页搜索结果中的商品总数 |
| updatedAt | string | 数据更新时间 |
| topAsinsModelStartDate | string | TOP ASIN 点击/转化数据窗口起始日期 |
| topAsinsModelEndDate | string | TOP ASIN 点击/转化数据窗口结束日期 |
| brands | array | 品牌 SOV 明细列表 |
| topAsins | array | TOP 3 ASIN 点击转化列表 |

### brands 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| brand | string | 品牌名称 |
| organicProducts | integer | 自然搜索结果中的商品数量 |
| sponsoredProducts | integer | 广告位中的商品数量 |
| combinedProducts | integer | 综合商品数量 |
| organicBasicSov | number | 自然搜索基础 SOV（0–1） |
| organicWeightedSov | number | 自然搜索加权 SOV（0–1） |
| sponsoredBasicSov | number | 广告搜索基础 SOV（0–1） |
| sponsoredWeightedSov | number | 广告搜索加权 SOV（0–1） |
| combinedBasicSov | number | 综合基础 SOV（0–1） |
| combinedWeightedSov | number | 综合加权 SOV（0–1） |
| organicAveragePosition | number | 自然搜索平均排名位置 |
| sponsoredAveragePosition | number | 广告搜索平均排名位置 |
| combinedAveragePosition | number | 综合平均排名位置 |
| organicAveragePrice | number | 自然搜索商品平均价格 |
| sponsoredAveragePrice | number | 广告搜索商品平均价格 |
| combinedAveragePrice | number | 综合商品平均价格 |

### topAsins 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编号 |
| name | string | 商品名称 |
| brand | string | 品牌名称 |
| clicks | integer | 点击量（30 天窗口） |
| conversions | integer | 转化量（30 天窗口） |
| conversionRate | number | 转化率（0–1） |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `shareOfVoice` 对象 |
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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/share-of-voice \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "keyword": "portable charger"}'
```

## 响应示例

```json
{
  "costToken": 1,
  "shareOfVoice": {
    "id": "us_portable_charger",
    "type": "share_of_voice",
    "estimated30DaySearchVolume": 125000,
    "exactSuggestedBidMedian": 1.25,
    "productCount": 60,
    "updatedAt": "2026-04-10T00:00:00",
    "topAsinsModelStartDate": "2026-03-11",
    "topAsinsModelEndDate": "2026-04-10",
    "brands": [
      {
        "brand": "Anker",
        "organicProducts": 5,
        "sponsoredProducts": 3,
        "combinedProducts": 8,
        "organicBasicSov": 0.083,
        "organicWeightedSov": 0.112,
        "sponsoredBasicSov": 0.15,
        "sponsoredWeightedSov": 0.18,
        "combinedBasicSov": 0.133,
        "combinedWeightedSov": 0.152,
        "organicAveragePosition": 12.4,
        "sponsoredAveragePosition": 5.0,
        "combinedAveragePosition": 9.5,
        "organicAveragePrice": 29.99,
        "sponsoredAveragePrice": 25.99,
        "combinedAveragePrice": 28.49
      }
    ],
    "topAsins": [
      {
        "asin": "B09V3KXJPB",
        "name": "Anker Portable Charger 10000mAh",
        "brand": "Anker",
        "clicks": 15200,
        "conversions": 4560,
        "conversionRate": 0.30
      }
    ]
  }
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-junglescout-keyword-share-of-voice",
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
