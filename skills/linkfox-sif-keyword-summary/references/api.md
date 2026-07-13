# SIF-关键词流量来源 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/keywordSummary`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKeyword | string | 是 | 搜索关键词，尽量翻译成对应国家站点的语言。最大长度 1000 字符 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| asins | string | 否 | ASIN 过滤列表，多个用英文逗号分隔；不传则返回该关键词下所有 ASIN。最大长度 1000 字符 |
| condition | string | 否 | 条件筛选，每次只能传一个。<br>**标志类**：`nfPosition`（自然流量词）、`isSpAd`（SP广告词）、`isVedioAd`（视频广告词）、`isBrandAd`（品牌广告词）、`isPPCAd`（PPC广告词）、`isSearchRecommend`（搜索推荐词）、`acAd`（SP 推荐）<br>**周期计数类**：`totalPeriod.in`（新进全部流量词）、`nfKeywordCnt.total` / `.in`、`adKeywordCnt.total` / `.in`、`allSpKeywordCnt.total` / `.in`、`spKeywordCnt.total` / `.in`、`recSpKeywordCnt.total` / `.in`、`allSbKeywordCnt.total` / `.in`、`sbKeywordCnt.total` / `.in`、`sbvKeywordCnt.total` / `.in` |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效；不填取系统最新整周） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |
| sortBy | string | 否 | 排序字段。可选值：`totalKeywordNum`（全部流量词）、`naturalKeywordNum`（自然流量词）、`brandKeywordNum`（品牌广告词）、`vedioKeywordNum`（视频广告词）、`acKeywordNum`（AC推荐词）、`erKeywordNum`（ER推荐词）、`trKeywordNum`（TR推荐词）、`sumScore`（所有关键词曝光总得分）、`totalNfScore`、`totalSpSocre`（注意拼写）、`totalBrandScore`、`totalVedioScore`、`totalAcScore`、`totalTrScore`、`totalErScore` |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小 10，最大 100，默认 `100` |
| desc | boolean | 否 | 是否降序，默认 `true` |


## 响应结构

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据，商品关键词流量数据对象数组 |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

> 本接口不返回 `isParentAsin`、`variantsNum`、`noKeywordVariantsNum`；如需这些字段请使用 `sif/asinSummary` 接口。

### 数据项字段（`data` 数组中的每个对象）

> 两类得分：无前缀字段（如 `naturalSearchExposureScore`）为该 ASIN 在所有关键词上的商品级整体指标；`keyword*` 前缀字段（如 `keywordNaturalExposureScore`）为该 ASIN 仅在本次查询的关键词上的指标。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编码 |
| productTitle | string | 商品标题 |
| productImageUrl | string | 商品主图 URL |
| productPrice | number | 商品售价 |
| customerRatingCount | integer | 客户评分总数 |
| productStarRating | number | 商品星级（0–5 星） |
| productRatingScore | number | 商品评分数值 |
| productUpdateTime | string | 产品更新时间（`yyyy-MM-dd HH:mm:ss`） |
| dataPeriodStartDate | string | 数据周期起始日期（`yyyy-MM-dd`） |
| totalExposureScore | number | 总曝光分数 |
| totalExposureRatio | number | 总流量份额 |
| naturalSearchExposureScore | number | 自然搜索曝光总分 |
| naturalSearchExposureRatio | number | 自然搜索曝光占比 |
| sponsoredProductsExposureScore | number | SP 广告曝光总分 |
| sponsoredProductsExposureRatio | number | SP 广告曝光占比 |
| brandAdExposureScore | number | 品牌广告曝光总分 |
| brandAdExposureRatio | number | 品牌广告曝光占比 |
| videoAdExposureScore | number | 视频广告曝光总分 |
| videoAdExposureRatio | number | 视频广告曝光占比 |
| amazonsChoiceExposureScore | number | AC 曝光总分 |
| amazonsChoiceExposureRatio | number | AC 曝光占比 |
| editorialRecommendationsExposureScore | number | ER 曝光总分 |
| editorialRecommendationsExposureRatio | number | ER 曝光占比 |
| topRatedExposureScore | number | TR 曝光总分 |
| topRatedExposureRatio | number | TR 曝光占比 |
| recommendPositionExposureScore | number | 推荐位曝光总分 |
| recommendAdExposureScore | number | 推荐位广告曝光分数 |
| recommendAdExposureRatio | number | 推荐位广告流量份额 |
| recommendNonadExposureScore | number | 推荐位非广告曝光分数 |
| recommendNonadExposureRatio | number | 推荐位非广告流量份额 |
| comprehensiveNaturalExposureScore | number | 综合自然流量得分（自然搜索 + 推荐位非广告） |
| comprehensiveNaturalExposureRatio | number | 综合自然流量份额 |
| keywordTotalExposureScore | number | 关键词总得分 |
| keywordNaturalExposureScore | number | 关键词自然得分 |
| keywordSponsoredProductsExposureScore | number | 关键词 SP 广告得分 |
| keywordBrandAdExposureScore | number | 关键词品牌广告得分 |
| keywordVideoAdExposureScore | number | 关键词视频广告得分 |
| keywordAmazonsChoiceExposureScore | number | 关键词 AC 得分 |
| keywordRecommendExposureScore | number | 关键词推荐位得分 |
| keywordRecommendAdExposureScore | number | 关键词推荐位广告得分 |
| keywordRecommendNonadExposureScore | number | 关键词推荐位非广告得分 |
| keywordComprehensiveNaturalExposureScore | number | 关键词综合自然得分（自然 + 推荐位非广告） |
| ppcTrafficSources | array | PPC 付费广告流量来源标记。包含：SP 广告、头部品牌广告、底部品牌广告、视频广告 |
| naturalSearchTrafficSources | array | 自然搜索流量来源标记 |
| amazonRecommendationSources | array | 亚马逊推荐流量来源标记。包含：Best Seller、AC、ER、TR、TRFOB 等 |
| promotionalDealSources | array | 促销活动流量来源标记。包含：Coupon、Limited Time Deal、Lowest Price in 30 Days 等 |

> 本接口不返回以下字段：`productCategory`、`productFeatures`、`isVariantProduct`、`isMonitored`、`monitoringStartTime`，以及 per-ASIN 的 `totalTrafficKeywordCount`、`naturalSearchKeywordCount`、`sponsoredProductsKeywordCount`、`brandAdKeywordCount`、`topBrandAdKeywordCount`、`bottomBrandAdKeywordCount`、`videoAdKeywordCount`、`amazonsChoiceKeywordCount`、`editorialRecommendationsKeywordCount`、`topRatedKeywordCount`、`frequentlyBoughtKeywordCount`。如需这些字段，请使用 `sif/asinSummary` 接口。

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
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
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US"}'
```

### 带条件筛选（仅SP广告词）：

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "condition": "isSpAd"}'
```

### 按 ASIN 过滤 + 指定日期区间：

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "asins": "B01NBNDC1T,B09VLJJPL6", "last7d": false, "startDate": "2026-04-05", "endDate": "2026-04-11"}'
```

### 按 SP 曝光得分排序：

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "wireless charger", "country": "US", "sortBy": "totalSpSocre", "desc": true}'
```

### 带分页参数：

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"searchKeyword": "phone case", "country": "US", "pageNum": 2, "pageSize": 50}'
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
