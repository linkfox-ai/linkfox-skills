# 极目-亚马逊-细分市场洞察信息 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/getNicheInfo`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nicheId | string | 是 | 细分市场ID，最大长度1000字符，只支持单个ID查询 |
| countryCode | string | 否 | 国家编码，仅支持 `US`、`JP`、`DE`，默认 `US` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 细分市场信息列表，每个元素为包含以下字段的对象 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

### `data` 元素关键字段

#### 市场概览

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | string | 细分市场ID |
| nicheTitle | string | 细分市场标题 |
| translationZh | string | 细分市场标题(中文) |
| referenceAsinImageUrl | string | 细分市场参考图片地址 |
| marketplaceId | string | 市场ID |
| demand | integer | 细分市场得分 |
| categorieList | array | 商品品类列表 |

#### 商品与品牌数量

| 字段 | 类型 | 说明 |
|------|------|------|
| productCount | integer | 商品数量 |
| productCountNow | integer | 商品数量(当前) |
| productCountT90Before | integer | 商品数量(90天前) |
| productCountT360Before | integer | 商品数量(360天前) |
| brandCount | integer | 品牌数量 |
| brandCountNow | integer | 品牌数量(当前) |
| brandCountT90Before | integer | 品牌数量(90天前) |
| brandCountT360Before | integer | 品牌数量(360天前) |
| brandCountT360Now | integer | 品牌数量(360天统计)(当前) |
| brandCountT360T90Before | integer | 品牌数量(360天统计)(90天前) |
| brandCountT360T360Before | integer | 品牌数量(360天统计)(360天前) |
| sellingPartnerCountNow | integer | 销售伙伴数量(当前) |
| sellingPartnerCountT90Before | integer | 销售伙伴数量(90天前) |
| sellingPartnerCountT360Before | integer | 销售伙伴数量(360天前) |
| sellingPartnerCountT360Now | integer | 销售伙伴数量(360 天统计)(当前) |
| sellingPartnerCountT360T90Before | integer | 销售伙伴数量(360 天统计)(90天前) |
| sellingPartnerCountT360T360Before | integer | 销售伙伴数量(360 天统计)(360天前) |

#### 价格

| 字段 | 类型 | 说明 |
|------|------|------|
| avgPrice | number | 产品均价 |
| avgProductPriceNow | number | 产品均价(当前) |
| avgProductPriceT90Before | number | 产品均价(90天前) |
| avgProductPriceT360Before | number | 产品均价(360天前) |
| minimumPrice | number | 产品最低价 |
| maximumPrice | number | 产品最高价 |

#### 搜索与转化

| 字段 | 类型 | 说明 |
|------|------|------|
| searchVolumeWeekly | integer | 搜索量（周数据） |
| searchVolumeQuarterly | integer | 搜索量（季度数据） |
| searchVolumeGrowthWeekly | number | 搜索量增长率（周数据） |
| searchVolumeGrowthQuarterly | number | 搜索量增长率（季度数据） |
| searchConversionRateWeekly | number | 搜索转换率（周数据） |
| searchConversionRateQuarterly | number | 搜索转换率（季度数据） |
| clickCountWeekly | integer | 点击量（周数据） |
| clickCountQuarterly | integer | 点击量（季度数据） |
| clickConversionRateQuarterly | number | 点击转换率（季度数据） |
| clickToSaleConversionWeekly | number | 点击转换率（周数据） |
| unitsSoldWeekly | integer | 销售数量（周数据） |
| unitsSoldQuarterly | integer | 销售数量（季度数据） |

#### 竞争 - 商品点击份额

| 字段 | 类型 | 说明 |
|------|------|------|
| top5ProductsClickShare | number | 排名前 5 位的商品点击份额 |
| top5ProductsClickShareNow | number | 前5个商品所占细分市场的点击量份额(当前) |
| top5ProductsClickShareT90Before | number | 前5个商品所占细分市场的点击量份额(90天前) |
| top5ProductsClickShareT360Before | number | 前5个商品所占细分市场的点击量份额(360天前) |
| top5ProductsClickShareT360Now | number | 排名前 5 位的商品点击份额（360天统计）(当前) |
| top5ProductsClickShareT360T90Before | number | 排名前 5 位的商品点击份额（360天统计）(90天前) |
| top5ProductsClickShareT360T360Before | number | 排名前 5 位的商品点击份额（360天统计）(360天前) |
| top20ProductsClickShareNow | number | 前20个商品所占细分市场的点击量份额（当前) |
| top20ProductsClickShareT90Before | number | 前20个商品所占细分市场的点击量份额（90天前) |
| top20ProductsClickShareT360Before | number | 前20个商品所占细分市场的点击量份额（360天前) |
| top20ProductsClickShareT360Now | number | 排名前20位的商品点击份额(360 天统计)(当前) |
| top20ProductsClickShareT360T90Before | number | 排名前20位的商品点击份额(360 天统计)(90天前) |
| top20ProductsClickShareT360T360Before | number | 排名前20位的商品点击份额(360 天统计)(360天前) |

#### 竞争 - 品牌点击份额

| 字段 | 类型 | 说明 |
|------|------|------|
| top5BrandsClickShare | number | 前5个品牌所占细分市场的点击量份额 |
| top5BrandsClickShareNow | number | 前5个品牌所占细分市场的点击量份额(当前) |
| top5BrandsClickShareT90Before | number | 前5个品牌所占细分市场的点击量份额(90天前) |
| top5BrandsClickShareT360Before | number | 前5个品牌所占细分市场的点击量份额(360天前) |
| top5BrandsClickShareT360Now | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(当前) |
| top5BrandsClickShareT360T90Before | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(90天前) |
| top5BrandsClickShareT360T360Before | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(360天前) |
| top20BrandsClickShareNow | number | 前20个品牌所占细分市场的点击量份额(当前) |
| top20BrandsClickShareT90Before | number | 前20个品牌所占细分市场的点击量份额(90天前) |
| top20BrandsClickShareT360Before | number | 前20个品牌所占细分市场的点击量份额(360天前) |
| top20BrandsClickShareT360Now | number | 前20个品牌所占细分市场的点击量份额(360天统计)（当前) |
| top20BrandsClickShareT360T90Before | number | 前20个品牌所占细分市场的点击量份额(360天统计)（90天前) |
| top20BrandsClickShareT360T360Before | number | 前20个品牌所占细分市场的点击量份额(360天统计)（360天前) |

#### 商品上架

| 字段 | 类型 | 说明 |
|------|------|------|
| newProductsLaunchedSemiannual | integer | 已发布新产品的数量（半年数据） |
| newProductsLaunchedT180Now | integer | 已发布新产品的数量(180天统计)(当前) |
| newProductsLaunchedT180T90Before | integer | 已发布新产品的数量(180天统计)(90天前) |
| newProductsLaunchedT180T360Before | integer | 已发布新产品的数量(180天统计)(360天前) |
| newProductsLaunchedT360Now | integer | 新上架商品数(360天统计)(当前) |
| newProductsLaunchedT360T90Before | integer | 新上架商品数(360天统计)(90天前) |
| newProductsLaunchedT360T360Before | integer | 新上架商品数(360天统计)(360天前) |
| successfulLaunchedSemiannual | integer | 成功发布商品的数量（半年数据） |
| launchRateSemiannual | number | 发布商品的成功率（半年数据） |
| successfulLaunchesT90Now | integer | 成功上架数(90天统计)(当前） |
| successfulLaunchesT90T90Before | integer | 成功上架数(90天统计)(90天前) |
| successfulLaunchesT90T360Before | integer | 成功上架数(90天统计)(360天前) |
| successfulLaunchesT180Now | integer | 成功发布商品的数量（180 天统计）(当前) |
| successfulLaunchesT180T90Before | integer | 成功发布商品的数量（180 天统计）(90天前) |
| successfulLaunchesT180T360Before | integer | 成功发布商品的数量（180 天统计）(360天前) |
| successfulLaunchesT360Now | integer | 成功发布商品的数量（360 天统计）(当前) |
| successfulLaunchesT360T90Before | integer | 成功发布商品的数量（360 天统计）(90天前) |
| successfulLaunchesT360T360Before | integer | 成功发布商品的数量（360 天统计）(360天前) |

#### 库存与运营

| 字段 | 类型 | 说明 |
|------|------|------|
| avgOOSRateNow | number | 平均缺货率(当前) |
| avgOOSRateT90Before | number | 平均缺货率(90天前) |
| avgOOSRateT360Before | number | 平均缺货率(360天前) |
| avgOOSRateT360Now | number | 平均缺货率(360天统计)(当前) |
| avgOOSRateT360T90Before | number | 平均缺货率(360天统计)(90天前) |
| avgOOSRateT360T360Before | number | 平均缺货率(360天统计)(360天前) |
| primeProductsPercentageNow | number | prime商品的百分比(当前) |
| primeProductsPercentageT90Before | number | prime商品的百分比(90天前) |
| primeProductsPercentageT360Before | number | prime商品的百分比(360天前) |
| primeProductsPercentageT360Now | number | prime商品的百分比(360 天统计）(当前) |
| primeProductsPercentageT360T90Before | number | prime商品的百分比(360 天统计）(90天前) |
| primeProductsPercentageT360T360Before | number | prime商品的百分比(360 天统计）(360天前) |

#### 评论与评分

| 字段 | 类型 | 说明 |
|------|------|------|
| avgReviewRatingNow | number | 平均评论评分(当前) |
| avgReviewRatingT90Before | number | 平均评论评分(90天前) |
| avgReviewRatingT360Before | number | 平均评论评分(360天前) |
| avgReviewCountNow | number | 平均评论数(当前) |
| avgReviewCountT90Before | number | 平均评论数(90天前) |
| avgReviewCountT360Before | number | 平均评论数(360天前) |
| positiveCustomerReviewInsights | array | 正面客户评论见解信息 |
| negativeCustomerReviewInsights | array | 负面客户评论见解信息 |
| productStarRatingImpact | array | 产品星级影响力信息 |

#### 卖家成熟度

| 字段 | 类型 | 说明 |
|------|------|------|
| avgBrandAgeNow | number | 平均品牌年龄(当前) |
| avgBrandAgeT90Before | number | 平均品牌年龄(90天前) |
| avgBrandAgeT360Before | number | 平均品牌年龄(360天前) |
| avgBrandAgeQuarterly | number | 平均品牌年龄(季度数据) |
| avgBrandAgeT360Now | number | 平均品牌年龄(360 天统计)(当前) |
| avgBrandAgeT360T90Before | number | 平均品牌年龄(360 天统计)(90天前) |
| avgBrandAgeT360T360Before | number | 平均品牌年龄(360 天统计)(360天前) |
| avgSellingPartnerAgeNow | number | 平均销售伙伴年龄(当前) |
| avgSellingPartnerAgeT90Before | number | 平均销售伙伴年龄(90天前) |
| avgSellingPartnerAgeT360Before | number | 平均销售伙伴年龄(360天前) |
| avgBestSellerRankNow | number | 平均BestSeller排名(当前) |
| avgBestSellerRankT90Before | number | 平均BestSeller排名(90天前) |
| avgBestSellerRankT360Before | number | 平均BestSeller排名(360天前) |

#### 广告与盈利

| 字段 | 类型 | 说明 |
|------|------|------|
| acos | number | （ACOS）广告销售成本比 |
| sponsoredProductsPercentageNow | number | 已进行商品推广的商品的百分比(当前) |
| sponsoredProductsPercentageT90Before | number | 已进行商品推广的商品的百分比(90天前) |
| sponsoredProductsPercentageT360Before | number | 已进行商品推广的商品的百分比(360天前) |
| sponsoredProductsPercentageT360Now | number | 已进行商品推广的商品的百分比(360 天统计)(当前) |
| sponsoredProductsPercentageT360T90Before | number | 已进行商品推广的商品的百分比(360 天统计)(90天前) |
| sponsoredProductsPercentageT360T360Before | number | 已进行商品推广的商品的百分比(360 天统计)(360天前) |
| profitMarginGt50PctSkuRatio | number | 利润率大于50%的商品比例 |
| breakEvenRatio | number | 盈亏平衡比率 |
| returnRateAnnual | number | 退货率（全年数据） |
| cpc | object | CPC（每次点击费用）数据 |

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
curl -X POST https://tool-gateway.linkfox.com/jiimore/getNicheInfo \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"nicheId": "12345678", "countryCode": "US"}'
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
