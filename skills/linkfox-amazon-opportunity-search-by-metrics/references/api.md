# 亚马逊商业洞察反向选品 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/opportunity/searchByMetrics`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`

## 请求参数

POST Body（JSON）。所有参数均为可选，但**必须至少提供 `keyword` / `nicheName` 或任意一个指标过滤字段**，禁止全部为空。

### 站点与翻页

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| amazonDomain | string | 亚马逊站点代码（闭枚举），当前仅支持 `US`，未指定时默认仅查美国站 | `US` |
| limit | integer | 返回条数上限（1-200），默认 25。无 page 参数，按采集时间倒序返回最近 N 条 | `25` |

### 文本搜索

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| keyword | string | 搜索关键词文本片段（LIKE 模糊匹配） | `whoop band` |
| nicheName | string | 赛道归一化名称片段（LIKE，snake_case 小写），适合赛道时序对比 | `wired_ribbon` |

### 市场规模与增长

| 参数 | 类型 | 说明 |
|------|------|------|
| nicheRevenue360dMinUsdAtLeastGte | number | 360 天市场营收下界（USD）的最小值 |
| nicheRevenue360dMinUsdAtLeastLte | number | 360 天市场营收下界（USD）的最大值 |
| nicheRevenue360dMaxUsdAtLeastGte | number | 360 天市场营收上界（USD）的最小值 |
| nicheRevenue360dMaxUsdAtLeastLte | number | 360 天市场营收上界（USD）的最大值 |
| nichePeakSearchVolumeAtLeastGte | integer | 峰值月搜索量下界（非负整数） |
| nichePeakSearchVolumeAtLeastLte | integer | 峰值月搜索量上界（非负整数） |
| nicheSearchVolumeYoyChangePctAtLeastGte | number | 搜索量同比变化率下限（%，带符号） |
| nicheSearchVolumeYoyChangePctAtLeastLte | number | 搜索量同比变化率上限（%，带符号） |
| nichePeakMonthGte | integer | 搜索峰值月份下限（1-12） |
| nichePeakMonthLte | integer | 搜索峰值月份上限（1-12） |

### 竞争格局（品牌 / 产品集中度）

| 参数 | 类型 | 说明 |
|------|------|------|
| nicheBrandCountGte | integer | 活跃品牌数下限 |
| nicheBrandCountLte | integer | 活跃品牌数上限 |
| nicheBrandCountYoyChangePctAtLeastGte | number | 品牌数同比变化率下限（%，带符号） |
| nicheBrandCountYoyChangePctAtLeastLte | number | 品牌数同比变化率上限（%，带符号） |
| nicheTop5ProductClickSharePctAtLeastGte | number | Top5 产品点击份额下限（0-100） |
| nicheTop5ProductClickSharePctAtLeastLte | number | Top5 产品点击份额上限（0-100） |
| featureTop5BrandSharePctAtLeastGte | number | Top5 品牌合计份额下限（0-100） |
| featureTop5BrandSharePctAtLeastLte | number | Top5 品牌合计份额上限（0-100） |
| featureTopBrandsContains | string | Top3 品牌名片段（原文 LIKE，区分大小写） |

### 价格与档位

| 参数 | 类型 | 说明 |
|------|------|------|
| priceMinUsdGte | number | 赛道最低商品价格下限（USD） |
| priceMinUsdLte | number | 赛道最低商品价格上限（USD） |
| priceMaxUsdGte | number | 赛道最高商品价格下限（USD） |
| priceMaxUsdLte | number | 赛道最高商品价格上限（USD） |
| priceSweetSpotMinUsdGte | number | Sweet Spot 下限的下界（USD） |
| priceSweetSpotMinUsdLte | number | Sweet Spot 下限的上界（USD） |
| priceSweetSpotMaxUsdGte | number | Sweet Spot 上限的下界（USD） |
| priceSweetSpotMaxUsdLte | number | Sweet Spot 上限的上界（USD） |
| priceEntryClickSharePctAtLeastGte | number | 入门档点击份额下限（0-100） |
| priceEntryClickSharePctAtLeastLte | number | 入门档点击份额上限（0-100） |
| priceMidClickSharePctAtLeastGte | number | 中档点击份额下限（0-100） |
| priceMidClickSharePctAtLeastLte | number | 中档点击份额上限（0-100） |
| priceHighClickSharePctAtLeastGte | number | 高端档点击份额下限（0-100） |
| priceHighClickSharePctAtLeastLte | number | 高端档点击份额上限（0-100） |

### 客户画像（年龄 / 性别 / 收入 / 生命阶段）

| 参数 | 类型 | 说明 |
|------|------|------|
| demoPrimaryAgeMinGte | integer | 主人群年龄下界的最小值（0-120 岁） |
| demoPrimaryAgeMinLte | integer | 主人群年龄下界的最大值（0-120 岁） |
| demoPrimaryAgeMaxGte | integer | 主人群年龄上界的最小值（0-120 岁） |
| demoPrimaryAgeMaxLte | integer | 主人群年龄上界的最大值（0-120 岁） |
| demoGenderDominant | string | 性别主导（闭枚举）：`female` / `male` / `mixed` / `unspecified` |
| demoPrimaryIncomeTier | string | 收入档（闭枚举）：`low` / `middle_low` / `middle` / `middle_upper` / `upper_middle` / `high` |
| demoLifeStageTagsContains | string | 生命阶段标签片段（snake_case，LIKE）：`parent`、`student`、`retiree`、`athlete` 等 |

### 产品特征（成熟度 / 趋势 / 差异化 / 搜索形态）

| 参数 | 类型 | 说明 |
|------|------|------|
| featureNewAvgReviewCountAtLeastGte | integer | 新品平均评论量下限（非负整数） |
| featureNewAvgReviewCountAtLeastLte | integer | 新品平均评论量上限（非负整数） |
| featureEstablishedAvgReviewCountAtLeastGte | integer | 成熟老品平均评论量下限（非负整数） |
| featureEstablishedAvgReviewCountAtLeastLte | integer | 成熟老品平均评论量上限（非负整数） |
| featureEmergingTrendTagsContains | string | 新兴趋势特征标签片段（snake_case，LIKE）：`cordless`、`portable`、`smart` 等 |
| featureUncommonFeatureTagsContains | string | 稀有差异化特征标签片段（snake_case，LIKE）：`hema_free`、`medical_grade_silicone` 等 |
| searchTopCategory1Label | string | 搜索流量第一类目标签片段（snake_case，LIKE）：`core_product_terms`、`set_kit_configurations` 等 |

### 评论卖点 / 痛点

| 参数 | 类型 | 说明 |
|------|------|------|
| reviewPositiveTop1Topic | string | 好评 #1 主题片段（snake_case，LIKE）：`comfort`、`quality_overall_generic` 等 |
| reviewPositiveTop1PctAtLeastGte | number | 好评 #1 主题占比下限（0-100，正面评论中占比） |
| reviewPositiveTop1PctAtLeastLte | number | 好评 #1 主题占比上限（0-100） |
| reviewNegativeTop1Topic | string | 差评 #1 主题片段（snake_case，LIKE）：`size`、`quality`、`durability` 等 |
| reviewNegativeTop1PctAtLeastGte | number | 差评 #1 主题占比下限（0-100，负面评论中占比） |
| reviewNegativeTop1PctAtLeastLte | number | 差评 #1 主题占比上限（0-100） |
| reviewNegativeTop2Topic | string | 差评 #2 主题片段（snake_case，LIKE） |
| reviewStrategicInsightTagsContains | string | 评论策略建议标签片段（snake_case，LIKE）：`sizing_clarity`、`material_transparency` 等 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 响应码，`200` 为成功 |
| msg | string | 提示信息，成功为 `ok`，失败为错误描述 |
| data | array | 关键词指标记录数组，每条对应一个 (站点, 关键词) 组合，约 37 个字段，按采集时间倒序 |

`data[]` 主要字段（节选）：

| 字段 | 类型 | 说明 |
|------|------|------|
| amazonDomain | string | 站点代码（当前固定 `US`） |
| keyword | string | 原始搜索关键词 |
| nicheName | string | 赛道归一化名称（snake_case） |
| nicheRevenue360dMinUsdAtLeast / nicheRevenue360dMaxUsdAtLeast | number | 近 360 天市场营收下界 / 上界（USD） |
| nichePeakSearchVolumeAtLeast | integer | 峰值月搜索量 |
| nichePeakMonth | integer | 搜索峰值月份（1-12） |
| nicheSearchVolumeYoyChangePctAtLeast | number | 搜索量同比变化率（%，带符号） |
| nicheBrandCount / nicheBrandCountYoyChangePctAtLeast | integer / number | 活跃品牌数及其同比变化率 |
| nicheTop5ProductClickSharePctAtLeast | number | Top5 产品点击份额（0-100） |
| featureTop5BrandSharePctAtLeast | number | Top5 品牌合计份额（0-100） |
| featureTopBrands | array | Top 3 品牌名列表（原文） |
| priceMinUsd / priceMaxUsd | number | 赛道整体最低 / 最高商品价 |
| priceSweetSpotMinUsd / priceSweetSpotMaxUsd | number | Value Sweet Spot 价格区间下界 / 上界 |
| priceEntryClickSharePctAtLeast / priceMidClickSharePctAtLeast / priceHighClickSharePctAtLeast | number | 入门 / 中 / 高档点击份额（0-100） |
| demoPrimaryAgeMin / demoPrimaryAgeMax | integer | 核心人群年龄下界 / 上界 |
| demoGenderDominant | string | 性别主导（`female` / `male` / `mixed` / `unspecified`） |
| demoPrimaryIncomeTier | string | 核心人群收入档 |
| demoLifeStageTags | array | 生命阶段标签列表 |
| featureNewAvgReviewCountAtLeast / featureEstablishedAvgReviewCountAtLeast | integer | 新品 / 成熟老品平均评论量 |
| featureEmergingTrendTags / featureUncommonFeatureTags | array | 新兴趋势 / 稀有差异化特征标签 |
| searchTopCategory1Label | string | 流量第一类目归一化标签 |
| reviewPositiveTop1Topic / reviewPositiveTop1PctAtLeast | string / number | 好评 #1 主题及在正面评论中的占比 |
| reviewNegativeTop1Topic / reviewNegativeTop1PctAtLeast / reviewNegativeTop2Topic | string / number / string | 差评 #1 主题、占比及次因 |
| reviewStrategicInsightTags | array | 评论策略建议标签 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 `code` 字段区分；未授权时 HTTP 状态码为 401。

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常解析 `data` 数组并展示给用户 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非 200 值 | 业务异常 | 参考 `msg` 字段获取具体错误原因，常见为参数全空或参数取值非法 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

按品牌密度低 + 同比高增长筛选新人友好赛道：

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/opportunity/searchByMetrics \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "nicheBrandCountLte": 20,
    "nicheSearchVolumeYoyChangePctAtLeastGte": 100,
    "featureNewAvgReviewCountAtLeastLte": 500,
    "limit": 25
  }'
```

按关键词反向追溯赛道历史：

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/opportunity/searchByMetrics \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{"keyword": "whoop band", "limit": 50}'
```

按差评痛点 + 中档稀缺锁定切入机会：

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/opportunity/searchByMetrics \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "reviewNegativeTop1Topic": "size",
    "reviewNegativeTop1PctAtLeastGte": 70,
    "priceMidClickSharePctAtLeastLte": 5,
    "priceEntryClickSharePctAtLeastGte": 70
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-opportunity-screener",
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
