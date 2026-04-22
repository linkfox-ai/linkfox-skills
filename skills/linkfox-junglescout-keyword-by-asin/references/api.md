# Jungle Scout 根据 ASIN 反查关键词 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-asin`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |
| asins | array\<string\> | 是 | ASIN 列表，最多 10 个 |

### 可选参数 — 结果控制

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| needCount | int | 否 | 返回的结果总数（内部自动分页） |
| includeVariants | boolean | 否 | 是否包含变体商品的关键词 |
| sort | string | 否 | 排序字段，默认 `-monthly_search_volume_exact`（精确搜索量降序）。可选值见下方排序字段表 |

### 可选参数 — 搜索量筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minMonthlySearchVolumeExact | int | 否 | 最小月精确搜索量（1-999999） |
| maxMonthlySearchVolumeExact | int | 否 | 最大月精确搜索量（1-999999） |
| minMonthlySearchVolumeBroad | int | 否 | 最小月广泛搜索量（1-999999） |
| maxMonthlySearchVolumeBroad | int | 否 | 最大月广泛搜索量（1-999999） |

### 可选参数 — 关键词特征筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWordCount | int | 否 | 最小单词数（1-99999） |
| maxWordCount | int | 否 | 最大单词数（1-99999） |
| minOrganicProductCount | int | 否 | 最小自然搜索结果数（1-99999） |
| maxOrganicProductCount | int | 否 | 最大自然搜索结果数（1-99999） |

### 排序字段

| sort 值 | 说明 |
|---------|------|
| name / -name | 关键词名称 升序/降序 |
| dominant_category / -dominant_category | 主类目 升序/降序 |
| monthly_trend / -monthly_trend | 月趋势 升序/降序 |
| quarterly_trend / -quarterly_trend | 季度趋势 升序/降序 |
| monthly_search_volume_exact / -monthly_search_volume_exact | 精确搜索量 升序/降序（默认降序） |
| monthly_search_volume_broad / -monthly_search_volume_broad | 广泛搜索量 升序/降序 |
| recommended_promotions / -recommended_promotions | 推荐促销 升序/降序 |
| sp_brand_ad_bid / -sp_brand_ad_bid | SP品牌广告出价 升序/降序 |
| ppc_bid_broad / -ppc_bid_broad | PPC广泛出价 升序/降序 |
| ppc_bid_exact / -ppc_bid_exact | PPC精确出价 升序/降序 |
| ease_of_ranking_score / -ease_of_ranking_score | 排名难度分 升序/降序 |
| relevancy_score / -relevancy_score | 相关度分 升序/降序 |
| organic_product_count / -organic_product_count | 自然结果数 升序/降序 |

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
| name | string | 关键词 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月广泛匹配搜索量 |
| monthlyTrend | float | 月环比趋势（%） |
| quarterlyTrend | float | 季度趋势（%） |
| dominantCategory | string | 主要类目 |
| relevancyScore | integer | 关键词与 ASIN 的相关度（0-100） |
| easeOfRankingScore | integer | 排名容易程度（0-100，越高越容易排名） |
| organicRank | integer | ASIN 的自然搜索排名 |
| sponsoredRank | integer | ASIN 的广告排名 |
| overallRank | integer | 综合排名位置 |
| organicProductCount | integer | 自然搜索结果中的商品总数 |
| sponsoredProductCount | integer | 广告位商品总数 |
| ppcBidExact | float | 精确匹配 PPC 建议出价（USD） |
| ppcBidBroad | float | 广泛匹配 PPC 建议出价（USD） |
| spBrandAdBid | float | SP 品牌广告建议出价（USD） |
| recommendedPromotions | integer | 推荐促销量 |
| primaryAsin | string | 该关键词下排名最高的 ASIN |
| relativeOrganicPosition | float | 查询 ASIN 的自然排名相对位置 |
| relativeSponsoredPosition | float | 查询 ASIN 的广告排名相对位置 |
| organicRankingAsinsCount | integer | 有自然排名的查询 ASIN 数量 |
| sponsoredRankingAsinsCount | integer | 有广告排名的查询 ASIN 数量 |
| avgCompetitorOrganicRank | float | 查询 ASIN 的平均自然排名 |
| avgCompetitorSponsoredRank | float | 查询 ASIN 的平均广告排名 |
| variationLowestOrganicRank | integer | 变体中最佳自然排名 |
| variationLowestSponsoredRank | integer | 变体中最佳广告排名 |
| competitorOrganicRank | array | 各 ASIN 的自然排名，元素为 `{asin, organicRank}` |
| competitorSponsoredRank | array | 各 ASIN 的广告排名，元素为 `{asin, sponsoredRank}` |
| updatedAt | string | 数据最后更新时间 |

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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-asin \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "asins": ["B0DXXXXXXX"], "needCount": 50, "sort": "-monthly_search_volume_exact"}'
```

## 响应示例

```json
{
  "costToken": 10,
  "keywordInfoList": [
    {
      "name": "yoga mat",
      "country": "us",
      "monthlySearchVolumeExact": 85420,
      "monthlySearchVolumeBroad": 125000,
      "monthlyTrend": 12.5,
      "quarterlyTrend": 8.3,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 95,
      "easeOfRankingScore": 42,
      "organicRank": 5,
      "sponsoredRank": 3,
      "overallRank": 4,
      "organicProductCount": 2000,
      "sponsoredProductCount": 48,
      "ppcBidExact": 1.25,
      "ppcBidBroad": 0.95,
      "spBrandAdBid": 2.10,
      "recommendedPromotions": 5,
      "primaryAsin": "B0DXXXXXXX",
      "relativeOrganicPosition": 0.12,
      "relativeSponsoredPosition": 0.08,
      "organicRankingAsinsCount": 1,
      "sponsoredRankingAsinsCount": 1,
      "avgCompetitorOrganicRank": 5.0,
      "avgCompetitorSponsoredRank": 3.0,
      "variationLowestOrganicRank": 3,
      "variationLowestSponsoredRank": 2,
      "competitorOrganicRank": [{"asin": "B0DXXXXXXX", "organicRank": 5}],
      "competitorSponsoredRank": [{"asin": "B0DXXXXXXX", "sponsoredRank": 3}],
      "updatedAt": "2026-04-10"
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
  "skillName": "linkfox-junglescout-keyword-by-asin",
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
