# 子能力归档：linkfox-amazon-opportunity-search-by-metrics

## 功能说明

从历史商业洞察沉淀的 Amazon 赛道指标池中反向筛选关键词/赛道，按市场规模与增长、竞争密度、价格档位、客户画像、产品特征和评论卖点/痛点等维度返回候选。记录是赛道/关键词级，不是 ASIN 级。

## 能力边界与特殊规则

- 当前仅支持美国站，使用 `amazonDomain=US` 或省略；不支持其他站点。
- 至少提供 `keyword`、`nicheName` 或一个指标过滤字段；无 `page` 参数，通过 `limit`（1-200）扩大候选，结果按采集时间倒序。
- 把自然语言业务意图映射为最小可行过滤集合：先用 2-4 个强过滤条件和较小 `limit`，无结果时放宽最激进的条件；不要静默增加用户未提出的价格或人群限制。
- 标签字段使用 snake_case 片段并按 LIKE 匹配；`demoGenderDominant`、`demoPrimaryIncomeTier` 等枚举必须使用 API 规定值。
- 数据是历史报告快照，不是实时市场；不提供 ASIN 级竞品、销量估算、实时排名或跨赛道仓库聚合。需要单关键词完整六维报告时切换到关键词报告能力。

## 执行、展示与反馈规则

- 通过 `LinkFox` 的 `proxy_call` 调用；新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。
- 同一任务内相同 `toolName + arguments` 只调用一次；失败、空结果或返回不理想时不得自动重试。
- 结果用对比表展示关键词/赛道、市场规模、增长、品牌数、价格区间和关键标签，并回显实际使用的过滤条件；空或少量结果时建议放宽最严格过滤器。
- 查询失败时依据 `msg` 解释参数全空、枚举或范围错误并给出修正方式；不要把空结果误判为市场不存在。
- 若用户反馈结果不准确、与意图不符、表达满意/不满或提出改进建议，可按 API 末尾 Feedback API 上报，`skillName` 使用 `linkfox-wb-amazon-business-insight`。

# 亚马逊商业洞察反向选品 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/opportunity/searchByMetrics`
- **arguments**：直接使用本 reference 的请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；禁止在配置或 `arguments` 中加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text 为 JSON 字符串时只解析一次，最后检查下游 `code`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；同一任务内相同 `toolName + arguments` 不得重复调用。

## 请求参数

`proxy_call.arguments`（JSON 对象）。所有参数均为可选，但**必须至少提供 `keyword` / `nicheName` 或任意一个指标过滤字段**，禁止全部为空。

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
| data[].amazonDomain | string | 站点代码（当前固定 `US`） |
| data[].keyword | string | 原始搜索关键词 |
| data[].nicheName | string | 赛道归一化名称（snake_case） |
| data[].nicheRevenue360dMinUsdAtLeast | number | 近 360 天市场营收下界 / 上界（USD） |
| data[].nicheRevenue360dMaxUsdAtLeast | number | 近 360 天市场营收下界 / 上界（USD） |
| data[].nichePeakSearchVolumeAtLeast | integer | 峰值月搜索量 |
| data[].nichePeakMonth | integer | 搜索峰值月份（1-12） |
| data[].nicheSearchVolumeYoyChangePctAtLeast | number | 搜索量同比变化率（%，带符号） |
| data[].nicheBrandCount | integer | 活跃品牌数及其同比变化率 |
| data[].nicheBrandCountYoyChangePctAtLeast | number | 活跃品牌数及其同比变化率 |
| data[].nicheTop5ProductClickSharePctAtLeast | number | Top5 产品点击份额（0-100） |
| data[].featureTop5BrandSharePctAtLeast | number | Top5 品牌合计份额（0-100） |
| data[].featureTopBrands | array | Top 3 品牌名列表（原文） |
| data[].featureTopBrands[] | 来源未说明 | Top 3 品牌名（原文） |
| data[].priceMinUsd | number | 赛道整体最低 / 最高商品价 |
| data[].priceMaxUsd | number | 赛道整体最低 / 最高商品价 |
| data[].priceSweetSpotMinUsd | number | Value Sweet Spot 价格区间下界 / 上界 |
| data[].priceSweetSpotMaxUsd | number | Value Sweet Spot 价格区间下界 / 上界 |
| data[].priceEntryClickSharePctAtLeast | number | 入门 / 中 / 高档点击份额（0-100） |
| data[].priceMidClickSharePctAtLeast | number | 入门 / 中 / 高档点击份额（0-100） |
| data[].priceHighClickSharePctAtLeast | number | 入门 / 中 / 高档点击份额（0-100） |
| data[].demoPrimaryAgeMin | integer | 核心人群年龄下界 / 上界 |
| data[].demoPrimaryAgeMax | integer | 核心人群年龄下界 / 上界 |
| data[].demoGenderDominant | string | 性别主导（`female` / `male` / `mixed` / `unspecified`） |
| data[].demoPrimaryIncomeTier | string | 核心人群收入档 |
| data[].demoLifeStageTags | array | 生命阶段标签列表 |
| data[].demoLifeStageTags[] | 来源未说明 | 生命阶段标签 |
| data[].featureNewAvgReviewCountAtLeast | integer | 新品 / 成熟老品平均评论量 |
| data[].featureEstablishedAvgReviewCountAtLeast | integer | 新品 / 成熟老品平均评论量 |
| data[].featureEmergingTrendTags | array | 新兴趋势 / 稀有差异化特征标签 |
| data[].featureEmergingTrendTags[] | 来源未说明 | 新兴趋势特征标签 |
| data[].featureUncommonFeatureTags | array | 新兴趋势 / 稀有差异化特征标签 |
| data[].featureUncommonFeatureTags[] | 来源未说明 | 稀有差异化特征标签 |
| data[].searchTopCategory1Label | string | 流量第一类目归一化标签 |
| data[].reviewPositiveTop1Topic | string | 好评 #1 主题及在正面评论中的占比 |
| data[].reviewPositiveTop1PctAtLeast | number | 好评 #1 主题及在正面评论中的占比 |
| data[].reviewNegativeTop1Topic | string | 差评 #1 主题、占比及次因 |
| data[].reviewNegativeTop1PctAtLeast | number | 差评 #1 主题、占比及次因 |
| data[].reviewNegativeTop2Topic | string | 差评 #1 主题、占比及次因 |
| data[].reviewStrategicInsightTags | array | 评论策略建议标签 |
| data[].reviewStrategicInsightTags[] | 来源未说明 | 评论策略建议标签 |

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

## MCP 调用示例

按品牌密度低 + 同比高增长筛选新人友好赛道：

```json
{
  "toolName": "amazon/opportunity/searchByMetrics",
  "arguments": {
    "nicheBrandCountLte": 20,
    "nicheSearchVolumeYoyChangePctAtLeastGte": 100,
    "featureNewAvgReviewCountAtLeastLte": 500,
    "limit": 25
  }
}
```

按关键词反向追溯赛道历史：

```json
{
  "toolName": "amazon/opportunity/searchByMetrics",
  "arguments": {
    "keyword": "whoop band",
    "limit": 50
  }
}
```

按差评痛点 + 中档稀缺锁定切入机会：

```json
{
  "toolName": "amazon/opportunity/searchByMetrics",
  "arguments": {
    "reviewNegativeTop1Topic": "size",
    "reviewNegativeTop1PctAtLeastGte": 70,
    "priceMidClickSharePctAtLeastLte": 5,
    "priceEntryClickSharePctAtLeastGte": 70
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
  "skillName": "linkfox-wb-amazon-business-insight",
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
