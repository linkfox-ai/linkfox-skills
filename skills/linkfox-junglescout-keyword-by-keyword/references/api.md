# Jungle Scout 根据关键词扩展关键词信息 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-keyword`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`。默认 `us` |
| searchTerms | string | 是 | 种子关键词（单个关键词字符串） |

### 可选参数 — 结果控制

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| needCount | int | 否 | 返回结果总数 |
| sort | string | 否 | 排序字段，默认 `-monthly_search_volume_exact`（精确搜索量降序） |

### 可选参数 — 搜索量筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minMonthlySearchVolumeExact | int | 否 | 精确搜索量下限 |
| maxMonthlySearchVolumeExact | int | 否 | 精确搜索量上限 |
| minMonthlySearchVolumeBroad | int | 否 | 广泛搜索量下限 |
| maxMonthlySearchVolumeBroad | int | 否 | 广泛搜索量上限 |

### 可选参数 — 其他筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWordCount | int | 否 | 关键词最少词数（用于筛选长尾词） |
| maxWordCount | int | 否 | 关键词最多词数 |
| minOrganicProductCount | int | 否 | 自然排名商品数下限 |
| maxOrganicProductCount | int | 否 | 自然排名商品数上限 |

### sort 可选值

| 值 | 说明 |
|----|------|
| name / -name | 关键词名称 升序/降序 |
| dominant_category / -dominant_category | 主类目 升序/降序 |
| monthly_trend / -monthly_trend | 月度趋势 升序/降序 |
| quarterly_trend / -quarterly_trend | 季度趋势 升序/降序 |
| monthly_search_volume_exact / -monthly_search_volume_exact | 精确搜索量 升序/降序（默认降序） |
| monthly_search_volume_broad / -monthly_search_volume_broad | 广泛搜索量 升序/降序 |
| recommended_promotions / -recommended_promotions | 推荐促销 升序/降序 |
| sp_brand_ad_bid / -sp_brand_ad_bid | 品牌广告出价 升序/降序 |
| ppc_bid_broad / -ppc_bid_broad | PPC广泛出价 升序/降序 |
| ppc_bid_exact / -ppc_bid_exact | PPC精确出价 升序/降序 |
| ease_of_ranking_score / -ease_of_ranking_score | 排名难度 升序/降序 |
| relevancy_score / -relevancy_score | 相关性评分 升序/降序 |
| organic_product_count / -organic_product_count | 自然商品数 升序/降序 |

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
| keywordInfoList | array | 关键词信息列表 |

### keywordInfoList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 关键词名称 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月均精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月均广泛匹配搜索量 |
| monthlyTrend | number | 月度搜索量变化百分比 |
| quarterlyTrend | number | 季度搜索量变化百分比 |
| dominantCategory | string | 搜索结果中占比最高的品类 |
| relevancyScore | integer | 与种子词的相关性评分 |
| easeOfRankingScore | integer | 排名容易度评分（越高越容易排名） |
| organicProductCount | integer | 自然排名商品数量 |
| sponsoredProductCount | integer | 广告商品数量 |
| ppcBidExact | number | 精确匹配 PPC 建议出价（美元） |
| ppcBidBroad | number | 广泛匹配 PPC 建议出价（美元） |
| spBrandAdBid | number | Sponsored Brand 广告建议出价（美元） |
| recommendedPromotions | integer | 推荐促销赠品数量 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `keywordInfoList` |
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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-keyword \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "searchTerms": "yoga mat", "needCount": 20}'
```

## 响应示例

```json
{
  "costToken": 1,
  "keywordInfoList": [
    {
      "name": "yoga mat thick",
      "country": "us",
      "monthlySearchVolumeExact": 45000,
      "monthlySearchVolumeBroad": 120000,
      "monthlyTrend": 15.3,
      "quarterlyTrend": -5.2,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 856,
      "easeOfRankingScore": 3,
      "organicProductCount": 342,
      "sponsoredProductCount": 28,
      "ppcBidExact": 1.25,
      "ppcBidBroad": 0.89,
      "spBrandAdBid": 2.50,
      "recommendedPromotions": 150
    },
    {
      "name": "yoga mat non slip",
      "country": "us",
      "monthlySearchVolumeExact": 38000,
      "monthlySearchVolumeBroad": 95000,
      "monthlyTrend": 8.1,
      "quarterlyTrend": 12.4,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 920,
      "easeOfRankingScore": 2,
      "organicProductCount": 510,
      "sponsoredProductCount": 35,
      "ppcBidExact": 1.58,
      "ppcBidBroad": 1.12,
      "spBrandAdBid": 3.10,
      "recommendedPromotions": 200
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
  "skillName": "linkfox-junglescout-keyword-by-keyword",
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
