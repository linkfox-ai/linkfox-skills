# SIF-ASIN流量来源 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/asinSummary`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchValue | string | 是 | 搜索值，ASIN码，多个用逗号分隔，最多10个ASIN，最大长度1000字符 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效；不填取系统最新周） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |
| conditions | string | 否 | 条件筛选，多个以英文逗号隔开。可选值：`nf`（自然流量）、`sp`（SP广告）、`sb`（SB常规）、`sbv`（视频广告）、`ad`（广告流量）、`acAd`（SP推荐）、`totalPeriod.in`（新进全部流量词） |
| sortBy | string | 否 | 排序字段，可选值：`totalKeywordNum`（全部流量词）、`naturalKeywordNum`（自然流量词）、`brandKeywordNum`（品牌广告词）、`vedioKeywordNum`（视频广告词）、`acKeywordNum`（AC推荐词）、`erKeywordNum`（ER推荐词）、`trKeywordNum`（TR推荐词）、`sumScore`（所有关键词曝光总得分）、`totalNfScore`（所有自然排名曝光总得分）、`totalSpSocre`（所有SP广告曝光总得分，注意拼写）、`totalBrandScore`（所有品牌广告曝光总得分）、`totalVedioScore`（所有视频广告曝光总得分）、`totalAcScore`（所有AC推荐曝光总得分）、`totalTrScore`（所有TR推荐曝光总得分）、`totalErScore`（所有ER推荐曝光总得分） |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小10，最大 **10000**，默认 `10000` |
| desc | boolean | 否 | 是否降序，默认 `true` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据，ASIN汇总对象数组（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| isParentAsin | boolean | 搜索的是否是父ASIN |
| variantsNum | integer | 有关键词的变体商品数量 |
| noKeywordVariantsNum | integer | 无关键词的变体商品数量 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

### data 数组元素字段

> 字段后缀约定：`*Prev` 为上一周期数值；`*In` / `*Out` 为本周期相对上期新进 / 退出数量，用于跨周对比。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编码。亚马逊商品标准识别码 |
| productTitle | string | 商品标题 |
| productCategory | string | 商品类目 |
| productPrice | number | 商品售价 |
| productImageUrl | string | 商品主图 URL |
| productFeatures | array | 商品特征列表 |
| customerRatingCount | integer | 客户评分总数 |
| productStarRating | number | 商品星级（0–5 星） |
| productRatingScore | number | 商品评分数值（0–5，亚马逊页面显示数值） |
| isVariantProduct | boolean | 是否为变体 |
| recentMonthlySalesBucket | string | 近一月销量桶（仅 keywordSummary 路径有值，形如 `"300+"` 或 `"1,000+"`） |
| isMonitored | boolean | 是否已监控 |
| monitoringStartTime | string | 商品关注时间 |
| dataPeriodStartDate | string | 数据周期起始日期（`yyyy-MM-dd`） |
| totalExposureScore | number | 总曝光分数。该商品在所有关键词下的曝光量综合评分 |
| totalExposureScorePrev | number | 上周期总曝光分数 |
| totalTrafficKeywordCount | integer | 流量关键词总数 |
| totalTrafficKeywordCountIn | integer | 本周期新进流量关键词数量 |
| totalTrafficKeywordCountOut | integer | 本周期退出流量关键词数量 |
| totalTrafficKeywordCountPrev | integer | 上周期流量关键词总数 |
| naturalSearchExposureScore | number | 自然搜索曝光总分 |
| naturalSearchExposureRatio | number | 自然搜索曝光占比 |
| naturalSearchExposureScorePrev | number | 上周期自然搜索曝光分数 |
| naturalSearchKeywordCount | integer | 自然搜索关键词数量 |
| naturalSearchKeywordCountIn | integer | 本周期新进自然搜索关键词数量 |
| naturalSearchKeywordCountOut | integer | 本周期退出自然搜索关键词数量 |
| naturalSearchKeywordCountPrev | integer | 上周期自然搜索关键词数量 |
| sponsoredProductsExposureScore | number | SP 广告曝光总分 |
| sponsoredProductsExposureRatio | number | SP 广告曝光占比 |
| sponsoredProductsExposureScorePrev | number | 上周期 SP 广告曝光分数 |
| sponsoredProductsKeywordCount | integer | SP 广告关键词数量 |
| brandAdExposureScore | number | 品牌广告曝光总分 |
| brandAdExposureRatio | number | 品牌广告曝光占比 |
| brandAdExposureScorePrev | number | 上周期品牌广告曝光分数 |
| brandAdKeywordCount | integer | 品牌广告关键词总数 |
| topBrandAdKeywordCount | integer | 页面顶部品牌广告关键词数量 |
| bottomBrandAdKeywordCount | integer | 页面底部品牌广告关键词数量 |
| videoAdExposureScore | number | 视频广告曝光总分 |
| videoAdExposureRatio | number | 视频广告曝光占比 |
| videoAdExposureScorePrev | number | 上周期视频广告曝光分数 |
| videoAdKeywordCount | integer | 视频广告关键词数量 |
| amazonsChoiceExposureScore | number | Amazon's Choice 曝光总分 |
| amazonsChoiceExposureRatio | number | Amazon's Choice 曝光占比 |
| amazonsChoiceExposureScorePrev | number | 上周期 AC 曝光分数 |
| amazonsChoiceKeywordCount | integer | Amazon's Choice 关键词数量 |
| amazonsChoiceKeywordCountIn | integer | 本周期新进 AC 关键词数量 |
| amazonsChoiceKeywordCountOut | integer | 本周期退出 AC 关键词数量 |
| editorialRecommendationsExposureScore | number | Editorial Recommendations 曝光总分 |
| editorialRecommendationsExposureRatio | number | Editorial Recommendations 曝光占比 |
| editorialRecommendationsKeywordCount | integer | Editorial Recommendations 关键词数量 |
| topRatedExposureScore | number | Top Rated 推荐曝光总分 |
| topRatedExposureRatio | number | Top Rated 推荐曝光占比 |
| topRatedKeywordCount | integer | Top Rated 推荐关键词数量 |
| frequentlyBoughtKeywordCount | integer | 高频购买推荐关键词数量（Top Rated Frequently Bought） |
| recommendPositionExposureScore | number | 推荐位曝光总分 |
| recommendAdExposureScore | number | 推荐位广告曝光分数 |
| recommendNonadExposureScore | number | 推荐位非广告曝光分数 |
| nonAcRecommendExposureScore | number | 非 AC 推荐位曝光分数 |
| recommendKeywordCount | integer | 推荐位关键词总数 |
| recommendAdKeywordCount | integer | 推荐位广告关键词数量 |
| recommendNonadKeywordCount | integer | 推荐位非广告关键词数量 |
| ppcTrafficSources | array | PPC 付费广告流量来源标记。包含：SP 广告、头部品牌广告、底部品牌广告、视频广告 |
| naturalSearchTrafficSources | array | 自然搜索流量来源标记 |
| amazonRecommendationSources | array | 亚马逊推荐流量来源标记。包含：Best Seller、AC、ER、TR、TRFOB 等 |
| promotionalDealSources | array | 促销活动流量来源标记。包含：Coupon、Limited Time Deal、Lowest Price in 30 Days 等 |

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
curl -X POST https://tool-gateway.linkfox.com/sif/asinSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB", "country": "US"}'
```

### 多ASIN查询

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/asinSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB,B0BN1K7WJP", "country": "US", "pageSize": 10000, "pageNum": 1, "desc": true}'
```

### 指定日期区间 + 仅查广告流量

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/asinSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchValue": "B09V3KXJPB", "country": "US", "last7d": false, "startDate": "2026-03-08", "endDate": "2026-03-14", "conditions": "ad", "sortBy": "totalSpSocre"}'
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
