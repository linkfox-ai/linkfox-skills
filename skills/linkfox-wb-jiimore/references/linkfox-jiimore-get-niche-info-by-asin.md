# 子能力归档：ASIN 细分市场分析

## 功能说明

根据一个亚马逊 ASIN 找到其所属细分市场，并返回需求、销量、搜索、转化、价格、品牌集中度、广告、新品、退货和 CPC 指标。通过 `proxy_call` 调用精确 `toolName` `jiimore/getNicheInfoByAsin`。

## 能力边界与特殊规则

- 必须提供 `asin`；`countryCode` 仅支持 `US`、`JP`、`DE`，`count` 控制返回数量，接口不提供分页和排序。
- 筛选参数中的比例、份额和转化率使用 0-1 小数，展示时转换为百分比；可展示中文标题 `translationZh` 和 CPC 三档。
- `errcode=10000` 表示没有符合筛选的市场，应解释为空结果并建议放宽筛选或核验 ASIN；不要把它当成认证失败。
- 这是 ASIN 到细分市场的映射与市场分析，不用于单个商品销售预估、Listing 详情、评论明细或关键词发现。

## 展示与执行补充

- 默认突出 `nicheInfoVoList` 中的市场标题、`nicheId`、`demand`、7 天搜索量/销量、品牌数和 TOP5 品牌点击份额。

## SKILL.md 归档

---
name: linkfox-jiimore-get-niche-info-by-asin
description: 按商品 ASIN 深度分析亚马逊细分市场，涵盖垄断程度、品牌集中度、新品成功率和市场机会评分。当用户提到按ASIN分析细分市场、ASIN市场调研、ASIN所属Niche查询、垄断评估、品牌集中度分析、新品成功率、市场需求评分、竞争格局、亚马逊子市场探索、ASIN niche analysis, niche by ASIN, monopoly level, brand concentration, new product success rate, market opportunity score, competitive landscape, Jiimore data时触发此技能。即使用户未明确提及"细分市场"或"ASIN"，只要其需求涉及根据某个商品ASIN评估其所在细分市场的竞争格局、品牌密度或机会潜力，也应触发此技能。
---

# Jiimore Niche Info by ASIN

This skill guides you on how to query and analyze Amazon niche market data by a reference ASIN, helping Amazon sellers evaluate market segments for competitive intensity, brand maturity, pricing structure, and entry opportunity.

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`jiimore/getNicheInfoByAsin`（区分大小写）
- `arguments`：直接使用本 reference 的请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "jiimore/getNicheInfoByAsin",
  "arguments": {
    "asin": "B0D9NWVC6Z",
    "countryCode": "US",
    "count": 10
  }
}
```

先检查 MCP 连接、schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 时只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 和 403 必须按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## Core Concepts

A **niche** (sub-market segment) is a grouping of products that share a common keyword theme on Amazon. Given a reference ASIN, this tool finds the niche segments that ASIN belongs to and returns rich analytical dimensions for each, including search volume, sales volume, click-through rates, brand count, top-brand concentration, new product launch success rates, CPC estimates, and a composite demand score. Data is available for **US**, **JP**, and **DE** marketplaces.

**ASIN is required**: Every query must include an `asin`. The tool locates the niche segments associated with that ASIN and returns them with detailed metrics. Use this when the user already has a specific product (ASIN) in hand and wants to understand the market segments it competes in — as opposed to keyword-driven niche discovery.

**Percentage fields**: Several parameters and response fields use a 0-1 decimal range representing 0%-100%. When displaying these values to users, convert them to percentages (e.g., 0.35 -> 35%).

**Demand score**: The `demand` field is a composite opportunity score assigned to each niche. A higher value indicates greater market demand potential.

## Parameter Guide

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| asin | string | Reference product ASIN. The tool finds niche segments associated with this ASIN. |

### Marketplace & Count

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, DE |
| count | integer | 10 | Number of niche segments to return |

### Filter Parameters (all optional, min/max ranges)

**Product & Pricing**:
| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Search & Sales (7-day)**:
| Parameter | Type | Description |
|-----------|------|-------------|
| searchVolumeT7Min / searchVolumeT7Max | integer | Weekly search volume range |
| unitsSoldT7Min / unitsSoldT7Max | integer | Weekly units sold range |
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickConversionRateT7Min / clickConversionRateT7Max | number | Weekly click conversion rate (0-1) |

**Brand Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| brandCountMin / brandCountMax | integer | Number of brands in niche |
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share (0-1) |
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |

**Seller Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**Competition & Advertising**:
| Parameter | Type | Description |
|-----------|------|-------------|
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share (0-1) |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage (0-1) |
| cpcMediumMin / cpcMediumMax | number | CPC median value range |

**New Product & Returns**:
| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | 180-day new product success rate (0-1) |
| returnRateT360Min / returnRateT360Max | number | 360-day return rate (0-1) |

## Usage Examples

**1. Basic niche exploration by ASIN**
Find the niche segments associated with ASIN `B0D9NWVC6Z` in the US market:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "count": 10
}
```

**2. Low-competition niche filtering by ASIN**
Find niches for an ASIN where the top 5 brands hold less than 50% click share and brand count exceeds 20:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "count": 20,
  "top5BrandsClickShareMax": 0.5,
  "brandCountMin": 20
}
```

**3. High-demand, high-conversion niches by ASIN**
Find niches for an ASIN with weekly search volume above 10000 and click conversion rate above 10%:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "searchVolumeT7Min": 10000,
  "clickConversionRateT7Min": 0.1
}
```

**4. New product opportunity analysis by ASIN**
Find niches for an ASIN with high new product success rate (above 20%) and low return rate (below 5%):
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "launchRateT180Min": 0.2,
  "returnRateT360Max": 0.05
}
```

**5. Japanese market niche research by ASIN**
Explore niches associated with an ASIN in the Japan market:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "JP",
  "count": 10
}
```

**6. Price-range-specific niche analysis by ASIN**
Find niches for an ASIN with average price between $20 and $50 and low advertising saturation:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "avgPriceMin": 20,
  "avgPriceMax": 50,
  "sponsoredProductsPercentageMax": 0.3
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Convert decimal ratios to percentages for readability (e.g., 0.25 -> 25%).
2. **Highlight key metrics**: Always surface the niche title, demand score, weekly search volume, weekly sales, brand count, and top 5 brands click share as primary columns.
3. **Translate niche titles**: When the `translationZh` field is present and the user prefers Chinese, show it alongside the original `nicheTitle`.
4. **Empty result handling**: When the response indicates no matching niche info (errcode 10000), explain that no niches matched the filters and suggest broadening ranges or verifying the ASIN.
5. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting filter criteria (e.g., broadening ranges or checking the ASIN/country).
6. **CPC display**: When CPC data is present, show all three tiers (low, medium, high) to give a complete advertising cost picture.
7. **No subjective advice**: Present data objectively without adding unsolicited business recommendations. Only provide interpretation when explicitly requested by the user.

## Important Limitations

- **Supported marketplaces**: Only US, JP, and DE are available. Other marketplace codes will be rejected.
- **ASIN required**: Every query must include an ASIN. The API will not return results without one.
- **No pagination/sorting**: This endpoint returns a fixed number of niches via `count` (default 10); it does not expose page/pageSize/sort parameters. Use the keyword-based niche skill when sorting or deeper pagination is needed.
- **Percentage values**: All rate/share parameters use 0-1 range, not 0-100. Ensure correct values when constructing filters.

## User Expression & Scenario Quick Reference

**Applicable** -- Niche-level market segment analysis driven by a reference ASIN:

| User Says | Scenario |
|-----------|----------|
| "Which niches does this ASIN belong to" | ASIN-to-niche mapping |
| "Analyze the market for ASIN XXXXX" | ASIN-driven niche assessment |
| "How competitive is the niche this product is in" | Monopoly / brand concentration by ASIN |
| "Find low-competition niches for this ASIN" | Blue ocean segment filtering |
| "What's the new product success rate for this ASIN's niches" | New entrant viability |
| "Show me niche data for this product" | General niche exploration by ASIN |
| "What's the CPC / ad cost for this ASIN's niches" | Advertising cost analysis |
| "Brand concentration in this ASIN's market" | Brand dominance assessment |

**Not applicable** -- Needs beyond ASIN-driven niche segment data:
- Keyword-driven niche discovery (use the keyword-based niche skill instead)
- Individual ASIN performance or sales estimation
- Search term ranking trends (use ABA data tools instead)
- Advertising campaign management or bid optimization
- Product review analysis or listing optimization

**Boundary judgment**: When users say "market research" or "product opportunity" while holding a specific ASIN, if their intent focuses on evaluating the competitive landscape and demand potential of the niche segments that ASIN competes in, this skill applies. If they need keyword-driven discovery, ASIN-level sales estimates, or comprehensive business strategy, direct them to the appropriate tool.

## 积分消耗规则

消耗 9 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the Feedback API section in this reference. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*


## API 参考

# 极目-亚马逊-根据 ASIN 查询相关细分市场信息 API 参考

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`jiimore/getNicheInfoByAsin`（区分大小写）
- `arguments`：直接使用本 reference 的请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "jiimore/getNicheInfoByAsin",
  "arguments": {
    "asin": "B0D9NWVC6Z",
    "countryCode": "US",
    "count": 10
  }
}
```

先检查 MCP 连接、schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 时只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 商品 ASIN（必填）。工具会查找与该 ASIN 共享相同细分市场（Niche）的市场段落 |

### 站点与数量

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| countryCode | string | 否 | US | 国家编码，可选值：`US`（美国）、`JP`（日本）、`DE`（德国） |
| count | integer | 否 | 10 | 返回的细分市场数量 |

### 筛选参数（均为可选）

**商品与价格**：

| 参数 | 类型 | 说明 |
|------|------|------|
| productCountMin | integer | 商品数量（当前）最小值 |
| productCountMax | integer | 商品数量（当前）最大值 |
| avgPriceMin | number | 平均价格（当前）最小值 |
| avgPriceMax | number | 平均价格（当前）最大值 |

**搜索与销售（7天统计）**：

| 参数 | 类型 | 说明 |
|------|------|------|
| searchVolumeT7Min | integer | 搜索量（7天统计）最小值 |
| searchVolumeT7Max | integer | 搜索量（7天统计）最大值 |
| unitsSoldT7Min | integer | 销售量（7天统计）最小值 |
| unitsSoldT7Max | integer | 销售量（7天统计）最大值 |
| clickCountT7Min | integer | 点击量（7天统计）最小值 |
| clickCountT7Max | integer | 点击量（7天统计）最大值 |
| clickConversionRateT7Min | number | 点击转换率（7天统计）最小值，数值范围为0-1，0.1表示10%的转换率 |
| clickConversionRateT7Max | number | 点击转换率（7天统计）最大值，数值范围为0-1，0.1表示10%的转换率 |

**品牌指标**：

| 参数 | 类型 | 说明 |
|------|------|------|
| brandCountMin | integer | 品牌数量最小值 |
| brandCountMax | integer | 品牌数量最大值 |
| top5BrandsClickShareMin | number | 前5个品牌所占细分市场的点击量份额最小值，数值范围为0-1，0.1表示10%的点击份额 |
| top5BrandsClickShareMax | number | 前5个品牌所占细分市场的点击量份额最大值，数值范围为0-1，0.1表示10%的点击份额 |
| avgBrandAgeMin | number | 平均品牌年龄（当前）最小值 |
| avgBrandAgeMax | number | 平均品牌年龄（当前）最大值 |
| avgBrandAgeQoqMin | number | 平均品牌年龄（90天统计）最小值 |
| avgBrandAgeQoqMax | number | 平均品牌年龄（90天统计）最大值 |
| avgBrandAgeYoyMin | number | 平均品牌年龄（360天统计）最小值 |
| avgBrandAgeYoyMax | number | 平均品牌年龄（360天统计）最大值 |

**卖家指标**：

| 参数 | 类型 | 说明 |
|------|------|------|
| avgSellingPartnerAgeMin | number | 平均销售伙伴年龄最小值 |
| avgSellingPartnerAgeMax | number | 平均销售伙伴年龄最大值 |
| avgSellingPartnerAgeQoqMin | number | 平均销售伙伴年龄（90天统计）最小值 |
| avgSellingPartnerAgeQoqMax | number | 平均销售伙伴年龄（90天统计）最大值 |
| avgSellingPartnerAgeYoyMin | number | 平均销售伙伴年龄（360天统计）最小值 |
| avgSellingPartnerAgeYoyMax | number | 平均销售伙伴年龄（360天统计）最大值 |

**竞争与广告**：

| 参数 | 类型 | 说明 |
|------|------|------|
| top5ProductsClickShareMin | number | 排名前5位的商品点击份额（当前）最小值，数值范围为0-1，0.1表示10%的点击份额 |
| top5ProductsClickShareMax | number | 排名前5位的商品点击份额（当前）最大值，数值范围为0-1，0.1表示10%的点击份额 |
| sponsoredProductsPercentageMin | number | SP广告占比最小值，数值范围为0-1，0.1表示10%的占比 |
| sponsoredProductsPercentageMax | number | SP广告占比最大值，数值范围为0-1，0.1表示10%的占比 |
| cpcMediumMin | number | CPC（当前）最小值 |
| cpcMediumMax | number | CPC（当前）最大值 |

**新品与退货**：

| 参数 | 类型 | 说明 |
|------|------|------|
| launchRateT180Min | number | 发布商品的成功率（180天统计）最小值，数值范围为0-1，0.1表示10%的成功率 |
| launchRateT180Max | number | 发布商品的成功率（180天统计）最大值，数值范围为0-1，0.1表示10%的成功率 |
| returnRateT360Min | number | 退货率（360天统计）最小值，数值范围为0-1，0.1表示10%的退货率 |
| returnRateT360Max | number | 退货率（360天统计）最大值，数值范围为0-1，0.1表示10%的退货率 |

## 响应结构

| 字段路径 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| costToken | integer | 消耗 token |
| nicheInfoVoList | array | 细分市场信息列表（见下方细分市场对象字段） |

> 说明：业务状态通过响应体中的 `errcode` 字段区分（`errcode = 200` 表示成功）。当结果为空时接口会返回业务错误（无符合要求的细分市场信息）。
### 细分市场对象字段（`nicheInfoVoList` 数组内）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| nicheInfoVoList[] | object | nicheInfoVoList 数组元素（来源的对象字段表） |
| nicheInfoVoList[].nicheId | string | 细分市场ID |
| nicheInfoVoList[].nicheTitle | string | 细分市场标题 |
| nicheInfoVoList[].translationZh | string | 细分市场标题(中文) |
| nicheInfoVoList[].demand | integer | 细分市场得分 |
| nicheInfoVoList[].productCount | integer | 商品数量 |
| nicheInfoVoList[].avgPrice | number | 产品均价 |
| nicheInfoVoList[].minimumPrice | number | 产品最低价 |
| nicheInfoVoList[].maximumPrice | number | 产品最高价 |
| nicheInfoVoList[].searchVolumeWeekly | integer | 搜索量（周数据） |
| nicheInfoVoList[].searchVolumeQuarterly | integer | 搜索量（季度数据） |
| nicheInfoVoList[].searchVolumeGrowthWeekly | number | 搜索量增长率（周数据） |
| nicheInfoVoList[].searchVolumeGrowthQuarterly | number | 搜索量增长率（季度数据） |
| nicheInfoVoList[].unitsSoldWeekly | integer | 销售数量（周数据） |
| nicheInfoVoList[].unitsSoldQuarterly | integer | 销售数量（季度数据） |
| nicheInfoVoList[].clickCountWeekly | integer | 点击量（周数据） |
| nicheInfoVoList[].clickCountQuarterly | integer | 点击量（季度数据） |
| nicheInfoVoList[].clickToSaleConversionWeekly | number | 点击转换率（周数据） |
| nicheInfoVoList[].clickConversionRateQuarterly | number | 点击转换率（季度数据） |
| nicheInfoVoList[].searchConversionRateWeekly | number | 搜索转换率（周数据） |
| nicheInfoVoList[].searchConversionRateQuarterly | number | 搜索转换率（季度数据） |
| nicheInfoVoList[].brandCount | integer | 品牌数量 |
| nicheInfoVoList[].top5BrandsClickShare | number | 前5个品牌所占细分市场的点击量份额 |
| nicheInfoVoList[].top5ProductsClickShare | number | 排名前5位的商品点击份额 |
| nicheInfoVoList[].avgBrandAgeNow | number | 平均品牌年龄(当前) |
| nicheInfoVoList[].avgBrandAgeQuarterly | number | 平均品牌年龄(季度数据) |
| nicheInfoVoList[].newProductsLaunchedSemiannual | integer | 已发布新产品的数量（半年数据） |
| nicheInfoVoList[].successfulLaunchedSemiannual | integer | 成功发布商品的数量（半年数据） |
| nicheInfoVoList[].launchRateSemiannual | number | 发布商品的成功率（半年数据） |
| nicheInfoVoList[].returnRateAnnual | number | 退货率（全年数据） |
| nicheInfoVoList[].acos | number | （ACOS）广告销售成本比 |
| nicheInfoVoList[].profitMarginGt50PctSkuRatio | number | 利润率大于50%的商品比例 |
| nicheInfoVoList[].breakEvenRatio | number | 盈亏平衡自然占比 |
| nicheInfoVoList[].cpc | object | CPC数据：`{ high（最高价）, medium（中间价）, low（最低价） }` |
| nicheInfoVoList[].categorieList | array | 商品品类列表 |
| nicheInfoVoList[].referenceAsinImageUrl | string | 细分市场参考图片地址 |
### 来源明确列出的 `cpc` 子字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| nicheInfoVoList[].cpc.high | 来源未说明 | 最高价 |
| nicheInfoVoList[].cpc.medium | 来源未说明 | 中间价 |
| nicheInfoVoList[].cpc.low | 来源未说明 | 最低价 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 10000 | 无符合要求的细分市场信息 | 放宽筛选条件或更换 ASIN 后重试 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 调用示例

请求示例见本 reference 的“ MCP 调用”章节及上方业务 JSON 示例；执行时必须使用完整 `proxy_call` 结构。

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-jiimore-get-niche-info-by-asin",
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
