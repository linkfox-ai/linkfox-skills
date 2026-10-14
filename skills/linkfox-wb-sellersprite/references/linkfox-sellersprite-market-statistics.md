---
name: linkfox-sellersprite-market-statistics
description: 提供亚马逊类目节点的市场统计看板，快速评估头部商品均价、销量及市场竞争格局。
---

# 卖家精灵-市场统计（SellerSprite Market Statistics）

本业务能力通过卖家精灵按亚马逊类目节点输出市场统计看板，帮助快速判断某类目的市场质量与竞争格局；完整参数与响应字段见本文后部的 API 参考章节。

## 能力边界

### ✅ 能力范围

- 按类目节点（`nodeIdPath`）输出聚合统计看板，不返回完整商品明细。
- 覆盖头部 Listing 平均星级、均价、BSR、月均销量/销售额、卖家数、品牌数、新品相关指标。
- 支持按 `topN` 自定义头部样本数量、按 `newProduct` 自定义新品口径、按 `month` 选择最近 30 天或具体月份。

### ❌ 边界与限制

- 必填参数：`marketplace`、`nodeIdPath`。
- `nodeIdPath` 必须为合法节点路径（如 `1064954:1069242:...`）。
- 月份查询受第三方历史范围限制，`yyyyMM` 最多支持当前月往前共 24 个月内的月份。
- **不在范围内**：商品级明细与 Listing 内容分析；关键词搜索与选词；竞品 Listing 监控；店铺级分析；类目定位（用户未给 `nodeIdPath` 时需先做类目定位）。

## 核心概念

- **节点统计**：对指定类目节点做聚合统计，不返回完整商品明细。
- **TopN 口径**：`topN` 决定头部商品统计样本数量（默认 10）。
- **新品定义**：`newProduct` 指定“新品”按最近 N 个月定义（默认 6）。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/market/statistics`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/market/statistics",
  "arguments": {
    "marketplace": "US",
    "nodeIdPath": "172282:281407",
    "month": "nearly",
    "topN": 10,
    "newProduct": 6
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 使用示例

```json
{
  "marketplace": "US",
  "nodeIdPath": "172282:281407",
  "month": "nearly",
  "topN": 10,
  "newProduct": 6
}
```

## 展示规则

1. 明确展示统计口径：`topN`、`newProduct`、时间范围。
2. 先输出关键总览指标，再输出扩展字段。
3. 若用户未给 `nodeIdPath`，先引导用户提供节点路径或先做类目定位。

## 用户表达与场景速查

**适用** —— 类目市场统计与基础盘评估：

| 用户说 | 场景 |
|--------|------|
| "类目市场统计"、"选市场看板" | 节点聚合统计 |
| "市场基础盘评估" | 类目整体规模与竞争格局 |
| "头部商品统计"、"头部 Listing 均价" | 头部样本指标 |
| "新品占比"、"新品销量" | 新品相关指标 |
| "SellerSprite market statistics" | 卖家精灵市场统计 |

不适用场景见上方【能力边界】。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 与 403 按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/market/statistics`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/market/statistics",
  "arguments": {
    "marketplace": "US",
    "nodeIdPath": "172282:281407",
    "month": "nearly",
    "topN": 10,
    "newProduct": 6
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | maxLength 1000，默认 `US` | 站点编码，见 [marketplace 可选值](#marketplace-可选值) |
| nodeIdPath | string | 是 | maxLength 1000 | 节点 ID 路径字符串，如 `1064954:1069242:1069784:1069820:1069838:1069828` |
| month | string | 否 | 见 [month](#month) | 筛选日期：`nearly` 或 `yyyyMM` |
| topN | integer | 否 | 默认 `10` | 头部 Listing 数量（用于头部相关指标口径） |
| newProduct | integer | 否 | 默认 `6` | 新品定义（月） |

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

### month

- **格式**：正则 `^(nearly|(19|20)\d{2}(0[1-9]|1[0-2]))$`
- **`nearly`**：最近 30 天
- **`yyyyMM`**：具体月份（如 `202507`）；最多支持**当前月往前共 24 个月内**的月份

## 响应结构

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 统计结果列表（对应第三方 `data`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

### `data[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[] | object | 单条节点统计 |
| data[].nodeIdPath | string | 节点 ID 路径 |
| data[].nodeLabelPath | string | 节点名称路径 |
| data[].nodeLabelLocale | string | 节点名称翻译 |
| data[].nodeLabelPathLocale | string | 节点名称路径翻译 |
| data[].marketplace | string | 市场标志 |
| data[].countryCode | string | 国家二简码 |
| data[].currency | string | 该市场的货币类型 |
| data[].totalProducts | integer | 商品总数 |
| data[].products | integer | 样品商品数 |
| data[].sellers | integer | 卖家数 |
| data[].brands | integer | 品牌数 |
| data[].avgSellers | number | 平均卖家数 |
| data[].hlProducts | integer | 头部 Listing 前 N 名商品样本数 |
| data[].avgUnits | integer | 月均销量 |
| data[].avgRevenue | number | 月均销售额 |
| data[].avgPrice | number | 平均价格 |
| data[].avgRating | number | 平均星级 |
| data[].avgRatings | integer | 平均评分数 |
| data[].avgRatingsCv | integer | 月评论平均增长数 |
| data[].avgBsr | integer | 平均 BSR |
| data[].avgProfit | number | 平均利润率 |
| data[].avgWeight | number | 平均重量(pound) |
| data[].baseAvgWeight | number | 平均重量(g) |
| data[].avgVolume | number | 平均体积(in³) |
| data[].baseAvgVolume | number | 平均体积(cm³) |
| data[].hlAvgUnits | integer | 头部 Listing 前 N 名商品月均销量 |
| data[].hlAvgRevenue | number | 头部 Listing 前 N 名商品月均销售额 |
| data[].hlAvgPrice | number | 头部 Listing 前 N 名商品平均价格 |
| data[].hlAvgRating | number | 头部 Listing 前 N 名商品平均星级 |
| data[].hlAvgRatings | integer | 头部 Listing 前 N 名商品平均评论数 |
| data[].hlAvgRatingsCv | integer | 头部 Listing 前 N 名商品月评论平均增长数 |
| data[].hlAvgBsr | integer | 头部 Listing 前 N 名商品平均 BSR |
| data[].newProducts | integer | 新品数量 |
| data[].newProductProportion | number | 新品数量占比 |
| data[].newAvgUnits | integer | 新品月均销量 |
| data[].newAvgRevenue | number | 新品月均销售额 |
| data[].newAvgPrice | number | 新品平均价格 |
| data[].newAvgRating | number | 新品平均星级 |
| data[].newAvgRatings | integer | 新品平均评分数 |
| data[].minNewRatings | integer | 最低新品评分数 |
| data[].maxNewRatings | integer | 最高新品评分数 |
| data[].firstShelfDate | string | 商品首次上架日期 |
| data[].lastShelfDate | string | 商品最新上架日期 |

## MCP 调用示例

使用本 reference 的完整 `proxy_call` 示例；其他筛选组合仍直接放入 `arguments`。


## 错误与成本

检查下游 `errcode`/`errorCode` 与 `errmsg`/`message`；401、402、403 按 `onboarding.md` 分层。每次分页、换月份或换条件均是新的收费调用；不得自动重试。
