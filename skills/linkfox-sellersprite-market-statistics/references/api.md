# 卖家精灵-选市场统计 API 参考

本文档与工具 `_sellersprite_market_statistics` 的 `inputSchema` / `outputSchema`（见 `temp/tools20260430.txt`）对齐。

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/market/statistics`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | maxLength 1000，默认 `US` | 站点编码，见 [marketplace](#marketplace-可选值) |
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

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 统计结果列表（对应第三方 `data`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

### data[] 元素（单条节点统计）

工具 schema 中 `hl*` 表示 **头部 Listing 前 N 名**（N 由请求参数 `topN` 决定）。

#### 节点与站点

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeIdPath | string | 节点 ID 路径 |
| nodeLabelPath | string | 节点名称路径 |
| nodeLabelLocale | string | 节点名称翻译 |
| nodeLabelPathLocale | string | 节点名称路径翻译 |
| marketplace | string | 市场标志 |
| countryCode | string | 国家二简码 |
| currency | string | 该市场的货币类型 |

#### 规模与样本

| 字段 | 类型 | 说明 |
|------|------|------|
| totalProducts | integer | 商品总数 |
| products | integer | 样品商品数 |
| sellers | integer | 卖家数 |
| brands | integer | 品牌数 |
| avgSellers | number | 平均卖家数 |
| hlProducts | integer | 头部 Listing 前 N 名商品样本数 |

#### 市场整体指标

| 字段 | 类型 | 说明 |
|------|------|------|
| avgUnits | integer | 月均销量 |
| avgRevenue | number | 月均销售额 |
| avgPrice | number | 平均价格 |
| avgRating | number | 平均星级 |
| avgRatings | integer | 平均评分数 |
| avgRatingsCv | integer | 月评论平均增长数 |
| avgBsr | integer | 平均 BSR |
| avgProfit | number | 平均利润率 |
| avgWeight | number | 平均重量(pound) |
| baseAvgWeight | number | 平均重量(g) |
| avgVolume | number | 平均体积(in³) |
| baseAvgVolume | number | 平均体积(cm³) |

#### 头部 Listing（前 N 名，N = topN）

| 字段 | 类型 | 说明 |
|------|------|------|
| hlAvgUnits | integer | 头部 Listing 前 N 名商品月均销量 |
| hlAvgRevenue | number | 头部 Listing 前 N 名商品月均销售额 |
| hlAvgPrice | number | 头部 Listing 前 N 名商品平均价格 |
| hlAvgRating | number | 头部 Listing 前 N 名商品平均星级 |
| hlAvgRatings | integer | 头部 Listing 前 N 名商品平均评论数 |
| hlAvgRatingsCv | integer | 头部 Listing 前 N 名商品月评论平均增长数 |
| hlAvgBsr | integer | 头部 Listing 前 N 名商品平均 BSR |

#### 新品（口径由 newProduct 定义）

| 字段 | 类型 | 说明 |
|------|------|------|
| newProducts | integer | 新品数量 |
| newProductProportion | number | 新品数量占比 |
| newAvgUnits | integer | 新品月均销量 |
| newAvgRevenue | number | 新品月均销售额 |
| newAvgPrice | number | 新品平均价格 |
| newAvgRating | number | 新品平均星级 |
| newAvgRatings | integer | 新品平均评分数 |
| minNewRatings | integer | 最低新品评分数 |
| maxNewRatings | integer | 最高新品评分数 |

#### 上架时间

| 字段 | 类型 | 说明 |
|------|------|------|
| firstShelfDate | string | 商品首次上架日期 |
| lastShelfDate | string | 商品最新上架日期 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/market/statistics   -H "Authorization: $LINKFOXAGENT_API_KEY"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "nodeIdPath": "172282:281407",
    "month": "nearly",
    "topN": 10,
    "newProduct": 6
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-statistics",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```
