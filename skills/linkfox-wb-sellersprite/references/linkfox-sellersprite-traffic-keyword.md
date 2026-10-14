---
name: linkfox-sellersprite-traffic-keyword
description: 反查亚马逊ASIN的流量关键词，分析自然与广告词结构、转化类型及历史趋势。
---

# 卖家精灵-流量关键词（SellerSprite Traffic Keyword）

本业务能力用于按亚马逊 ASIN 反查其流量关键词，分析自然词与广告词结构、转化类型及历史趋势；完整参数与响应字段见本文后部的 API 参考章节。

## 能力边界

### ✅ 能力范围

- 以商品 ASIN 为输入，反查该商品获得流量的关键词列表。
- 分析关键词的流量占比类型（主要/精准/转化流失）、转化类型（优质/平稳/流失/无效）、曝光位置标签（自然搜索、AC 推荐、SP 广告等）。
- 查看关键词的自然位与广告位排名、月搜索量、月购买量、流量占比、PPC 竞价等指标。
- 支持历史月份（`yyyyMM`）查询与多维排序。

### ❌ 边界与限制

- 必填参数：`marketplace`、`asin`。
- 单次每页最多 100 条，最多查 2000 条。
- 历史查询需传 `month`（格式 `yyyyMM`），不传默认最近 30 天。
- **不在范围内**：亚马逊关键词选品（用选品工具）；竞品店铺整体流量分析；广告投放优化与竞价策略建议；Listing 文案撰写。

## 核心概念

- **ASIN 反查词**：以商品 ASIN 为输入，查看该商品获得流量的关键词列表。
- **流量占比类型**（`trafficKeywordTypes`）：主要流量词、精准流量词、以及 schema 中的 `preciseLongTail`（工具文案为「转化流失词」）等。
- **转化类型**（`conversionKeywordTypes`）：如转化优质词、平稳词、流失词等。
- **词标签**（`badges`）：如自然搜索词、Amazon Choice 推荐词等。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/traffic/keyword`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/traffic/keyword",
  "arguments": {
    "marketplace": "US",
    "asin": "B0XXXXXXXXX",
    "page": 1,
    "size": 50
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 使用示例

**1. 反查某 ASIN 的流量词（最近 30 天）**
```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "size": 50,
  "orderField": "rankPosition",
  "orderDesc": false
}
```

**2. 查询历史月份并按类型筛选**
```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "month": "202507",
  "trafficKeywordTypes": "primary,precise",
  "conversionKeywordTypes": "excellent,stable",
  "page": 1,
  "size": 100
}
```

## 展示规则

1. 结果优先展示：关键词、自然位、广告位、流量占比类型、转化类型。
2. 明确标注查询周期（最近 30 天或历史月份）。
3. 当存在分页时，告知总数与当前页。
4. 不输出与接口无关的主观商业建议，除非用户明确要求。

## 用户表达与场景速查

**适用** —— 按 ASIN 反查流量关键词：

| 用户说 | 场景 |
|--------|------|
| "反查这个 ASIN 的流量词"、"这个 ASIN 靠什么词出单" | ASIN 流量词反查 |
| "这个商品的自然词和广告词有哪些" | 自然/广告词结构分析 |
| "这个词的转化类型是什么" | 转化类型查看 |
| "查一下去年 7 月这个 ASIN 的流量词" | 历史月份流量词 |
| "按流量占比排一下这个 ASIN 的词" | 多维排序 |
| "SellerSprite traffic keyword"、"reverse ASIN keywords" | 英文触发表达 |

不适用场景见上方【能力边界】。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 与 403 按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/traffic/keyword`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/traffic/keyword",
  "arguments": {
    "marketplace": "US",
    "asin": "B0XXXXXXXXX",
    "page": 1,
    "size": 50
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | 见下表 | 市场站点，默认 `US` |
| asin | string | 是 | maxLength 1000 | 要反查的商品 ASIN |
| month | string | 否 | 正则 `^(19\|20)\d{2}(0[1-9]\|1[0-2])$` | 历史月份，格式 `yyyyMM`；不传默认最近 30 天 |
| page | integer | 否 | 默认 1 | 当前页 |
| size | integer | 否 | 默认 50，最小 1，最大 100；最多查 2000 条 | 每页条数 |
| keyword | string | 否 | maxLength 1000 | 关键词筛选 |
| badges | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量词类型（曝光位置），见 [badges 枚举](#badges-枚举) |
| trafficKeywordTypes | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量占比类型，见 [trafficKeywordTypes 枚举](#traffickeywordtypes-枚举) |
| conversionKeywordTypes | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量转化类型，见 [conversionKeywordTypes 枚举](#conversionkeywordtypes-枚举) |
| orderField | string | 否 | maxLength 1000，默认 `rankPosition` | 排序字段，见 [orderField 可选值](#orderfield-可选值) |
| orderDesc | boolean | 否 | 默认 `false` | 排序是否倒序 |

### marketplace 可选值

| 取值 | 含义 |
|------|------|
| US | 美国站 USD($) |
| JP | 日本站 JPY(￥) |
| UK | 英国站 GBP(£) |
| DE | 德国站 EUR(€) |
| FR | 法国站 EUR(€) |
| IT | 意大利站 EUR(€) |
| ES | 西班牙站 EUR(€) |
| CA | 加拿大站 C$($) |
| IN | 印度站 INR(₹) |

### badges 枚举

多个值用英文逗号分隔。

| 取值 | 含义 |
|------|------|
| naturalSearching | 自然搜索词 |
| amazonChoice | AC 推荐词 |
| editorialRecommendations | ER 推荐词 |
| fourStar | 四星推荐词 |
| highlyRated | HR 推荐词 |
| sponsorBrand | 品牌推荐词 |
| sponsorVideo | 视频推荐词 |
| ads | SP 广告词 |

### trafficKeywordTypes 枚举

多个值用英文逗号分隔（与工具 schema 文案一致）。

| 取值 | 含义 |
|------|------|
| primary | 主要流量词 |
| precise | 精准流量词 |
| preciseLongTail | 转化流失词 |

### conversionKeywordTypes 枚举

多个值用英文逗号分隔。

| 取值 | 含义 |
|------|------|
| excellent | 转化优质词 |
| stable | 转化平稳词 |
| lost | 转化流失词 |
| invalid | 无效曝光词 |

### orderField 可选值

| 取值 | 含义 |
|------|------|
| rankPosition | 自然排名（默认） |
| adPosition | 广告排名 |
| createdTime | 创建时间 |
| searchesRank | 搜索量周排名 |
| searches | 月搜索量 |
| purchases | 月购买量 |
| purchaseRate | 购买率 |
| products | 商品数 |
| supplyDemandRatio | 供需比 |
| latest1daysAds | 广告竞品数 |
| bid | PPC 竞价 |
| trafficPercentage | 流量占比 |

## 响应结构

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总条数 |
| marketplace | string | 市场编码 |
| asin | string | 查询的 ASIN |
| data | array | 流量词列表（对应第三方 `data.items`） |
| summaryList | array | 高频词总结列表 |
| columns | array | 列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

### `summaryList[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| summaryList[] | object | 高频词总结元素 |
| summaryList[].total | integer | 总次数 |
| summaryList[].keywords | string | 词 |

### `data[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[] | object | 单条流量词 |
| data[].keyword | string | 关键词 |
| data[].keywordCn | string | 关键词中文翻译 |
| data[].trafficKeywordType | string | 流量占比类型 |
| data[].conversionKeywordType | string | 流量转化类型 |
| data[].badges | array | 曝光位置（流量词类型） |
| data[].rankPosition | object | 自然排名位次信息，结构见 [排名对象](#排名对象-rankposition--adposition) |
| data[].adPosition | object | 广告排名位次信息，结构同 [排名对象](#排名对象-rankposition--adposition) |
| data[].searches | integer | 月搜索量 |
| data[].searchesRank | integer | 周搜索量排名 |
| data[].searchesRankTimeFrom | integer | 周搜索量排名时间范围起 |
| data[].searchesRankTimeTo | integer | 周搜索量排名时间范围止 |
| data[].purchases | integer | 月购买量 |
| data[].purchaseRate | number | 购买率 |
| data[].products | integer | 商品数 |
| data[].supplyDemandRatio | number | 供需比 |
| data[].trafficPercentage | number | 流量占比 |
| data[].naturalRatio | number | 流量分布-自然占比 |
| data[].adRatio | number | 流量分布-广告占比 |
| data[].calculatedWeeklySearches | number | 预估周曝光量 |
| data[].impressions | integer | 展示量 |
| data[].clicks | integer | 点击量 |
| data[].bid | number | PPC 竞价 |
| data[].bidMin | number | PPC 竞价下限 |
| data[].bidMax | number | PPC 竞价上限 |
| data[].latest1daysAds | integer | 最近 1 天广告竞品数 |
| data[].latest7daysAds | integer | 最近 7 天广告竞品数 |
| data[].latest30daysAds | integer | 最近 30 天广告竞品数 |
| data[].sprt | number | SP 相关比率 |
| data[].monopolyClickRate | number | 垄断点击率 |
| data[].top3ClickingRate | number | Top3 点击率 |
| data[].top3ConversionRate | number | Top3 转化率 |
| data[].titleDensity | number | 标题密度 |
| data[].stats | array | 高频词，元素见下表 |
| data[].updatedTime | integer | 更新时间 |
| data[].badges[] | 来源未说明 | 单个曝光位置（流量词类型） |

### `data[].stats[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[].stats[] | object | 单个高频词子项 |
| data[].stats[].keywords | string | 词 |
| data[].stats[].total | integer | 总条数 |
| data[].stats[].rankPosition | object | 自然排名位次，结构见下 |
| data[].stats[].adPosition | object | 广告排名位次，结构见下 |

### 排名对象的完整路径

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[].rankPosition.updatedTime | integer | 排名时间 |
| data[].rankPosition.pageSize | integer | 每页多少条数据 |
| data[].rankPosition.index | integer | 当前页排第几 |
| data[].rankPosition.page | integer | 第几页 |
| data[].rankPosition.position | integer | 总结果中排第几 |
| data[].adPosition.updatedTime | integer | 排名时间 |
| data[].adPosition.pageSize | integer | 每页多少条数据 |
| data[].adPosition.index | integer | 当前页排第几 |
| data[].adPosition.page | integer | 第几页 |
| data[].adPosition.position | integer | 总结果中排第几 |
| data[].stats[].rankPosition.updatedTime | integer | 排名时间 |
| data[].stats[].rankPosition.pageSize | integer | 每页多少条数据 |
| data[].stats[].rankPosition.index | integer | 当前页排第几 |
| data[].stats[].rankPosition.page | integer | 第几页 |
| data[].stats[].rankPosition.position | integer | 总结果中排第几 |
| data[].stats[].adPosition.updatedTime | integer | 排名时间 |
| data[].stats[].adPosition.pageSize | integer | 每页多少条数据 |
| data[].stats[].adPosition.index | integer | 当前页排第几 |
| data[].stats[].adPosition.page | integer | 第几页 |
| data[].stats[].adPosition.position | integer | 总结果中排第几 |

## MCP 调用示例

使用本 reference 的完整 `proxy_call` 示例；其他筛选组合仍直接放入 `arguments`。


## 错误与成本

检查下游 `errcode`/`errorCode` 与 `errmsg`/`message`；401、402、403 按 `onboarding.md` 分层。每次分页、换月份或换条件均是新的收费调用；不得自动重试。
