---
name: linkfox-sellersprite-market-research
description: 基于卖家精灵类目维度筛选亚马逊细分市场，评估市场规模、竞争度及选品方向。
---

# 卖家精灵-市场调研（列表）

本业务能力用于按类目维度筛选并排序亚马逊细分市场，帮助评估市场规模、竞争度与选品方向；完整参数与响应字段见本文后部的 API 参考章节。

## 能力边界

### ✅ 能力范围

- 按类目/节点聚合查询亚马逊细分市场画像，覆盖美国、日本、英国、德国、法国、意大利、西班牙、加拿大、印度等站点。
- 评估市场规模（月均销量、月均销售额、商品数量）、竞争结构（卖家/品牌集中度、头部集中度、Amazon 自营占比、FBA/FBM 占比）。
- 筛选新品机会（新品数量、新品占比、新品均价/评分/销量）及价格、评分、毛利、BSR、重量、体积等区间。
- 支持按排序字段与方向排序，最多返回 200 条/页。

### ❌ 边界与限制

- **必填参数**：`marketplace`。
- **分页上限**：每页最多 200 条。
- **历史月份**：`month` 最多支持当前月往前共 24 个月内的月份。
- **集中度刻度**：`GoodsCrn` / `BrandCrn` / `SellerCrn` / `EbcProportion` / `FbaProportion` / `FbmProportion` / `AmazonSelfProportion` 的 `min*` / `max*` 入参须为 **0～1 小数**，勿用整数百分数。
- **不在范围内**：商品级 Listing 分析（用商品榜单/Listing 工具）；关键词反查与搜索量（用关键词工具）；竞品店铺级深度分析；下单与库存管理。

## 核心概念

- **类目市场级分析**：不是商品级列表，而是按类目/节点聚合后的市场画像。
- **市场规模**：月均销量、月均销售额、商品数量等。
- **竞争结构**：卖家/品牌集中度、头部集中度、自营占比、FBA/FBM 占比。
- **入参刻度**：筛选用的 GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion（`min*`/`max*`）须为 **0～1 小数**，见本文后部的 API 参考章节。
- **新品机会**：新品数量、新品占比、新品均价/评分/销量等。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/market/research`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/market/research",
  "arguments": {
    "marketplace": "US",
    "month": "nearly",
    "page": 1,
    "size": 50
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 使用示例

```json
{
  "marketplace": "US",
  "month": "nearly",
  "minAvgRevenue": 10000,
  "maxGoodsCrn": 0.4,
  "minNewProportion": 10,
  "maxSellerCrn": 0.5,
  "orderField": "total_amount",
  "orderDesc": true,
  "page": 1,
  "size": 50
}
```

## 展示规则

1. 先给出市场候选 Top N，再展示核心指标（市场规模、集中度、新品占比）。
2. **入参回显**：`GoodsCrn` / `BrandCrn` / `SellerCrn` / `EbcProportion` / `FbaProportion` / `FbmProportion` / `AmazonSelfProportion` 对应筛选为 **0～1 小数**；向用户说明时可换算为百分数（如传 `0.4` 可表述为「商品集中度上限 40%」）。响应 `data[]` 里若仍带「(%)」字段，与入参刻度可能不同，以返回为准。
3. 其它比例/毛利率等字段的单位以本文后部的 API 参考章节为准。
4. 显示筛选条件回显，便于用户复现。
5. 若结果过少或过多，建议用户调整关键阈值（如集中度、规模阈值）。

## 用户表达与场景速查

**适用** —— 亚马逊类目市场调研与选品方向评估：

| 用户说 | 场景 |
|--------|------|
| "亚马逊市场调研"、"选市场" | 市场机会筛选 |
| "细分类目研究"、"细分类目分析" | 类目市场画像 |
| "市场集中度分析"、"头部集中度" | 竞争结构评估 |
| "新品机会"、"新品占比" | 新品机会发现 |
| "哪个类目好做"、"可进入市场" | 选品方向评估 |
| "SellerSprite market research" | 卖家精灵选市场 |

不适用场景见上方【能力边界】。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 与 403 按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/market/research`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/market/research",
  "arguments": {
    "marketplace": "US",
    "month": "nearly",
    "page": 1,
    "size": 50
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

**必填**：仅 `marketplace`。

**说明**：带「毛利率」等且 schema 写明「输入 N 表示 N%」的数值参数，取值范围一般为 **0–100**。**例外**：下列 **GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion** 的 `min*` / `max*` 入参须传 **小数**，见 [集中度与结构占比](#集中度与结构占比)。

### 类目、地域与头部样本

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | maxLength 1000，默认 `US` | 站点编码，见 [marketplace](#marketplace-可选值) |
| nodeIdPath | string | 否 | maxLength 1000 | 类目节点 ID 路径，如 `172282:281407` |
| departmentKeyword | string | 否 | maxLength 1000 | 类目关键字路径，如 `Electronics:Accessories & Supplies` |
| sellerLocation | string | 否 | maxLength 1000 | 卖家所属地，多个英文逗号分隔；取值见卖家精灵表 1.3 |
| newProduct | integer | 否 | 默认 `3` | 新品定义（月） |
| topNum | integer | 否 | 默认 `10` | 头部 Listing 数量 |

### 时间与分页、排序

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| month | string | 否 | 见 [month](#month) | 筛选日期：`nearly` 或 `yyyyMM` |
| page | integer | 否 | 默认 `1` | 页码，从 1 开始 |
| size | integer | 否 | 默认 `50`，最小 `1`，最大 `200` | 每页条数 |
| orderField | string | 否 | maxLength 1000 | 排序字段，见 [orderField](#orderfield-可选值) |
| orderDesc | boolean | 否 | 默认 `true` | `true` 降序，`false` 升序 |

### 市场规模与主体数量

| 参数 | 类型 | 说明 |
|------|------|------|
| minAvgRevenue / maxAvgRevenue | number | 最低 / 最高月均销售额 |
| minAvgUnits / maxAvgUnits | integer | 最低 / 最高月均销量 |
| minGoodsCount / maxGoodsCount | integer | 最低 / 最高商品数量 |
| minSellers / maxSellers | integer | 最小 / 最大卖家数量 |
| minBrands / maxBrands | integer | 最小 / 最大品牌数量 |
| minAvgSellers / maxAvgSellers | number | 最小 / 最大平均卖家数量 |

### 集中度与结构占比

以下 **7 组**筛选入参（对应卖家精灵字段 **GoodsCrn、BrandCrn、SellerCrn、EbcProportion、FbaProportion、FbmProportion、AmazonSelfProportion**）须传 **小数**，约定为 **0～1** 之间的比例（例如 **`0.35` 表示 35%**）。**不要**按整数百分数传 **0～100**（例如勿用 `40` 表示 40%，除非已与实网行为核对）。

| 参数 | 类型 | 说明 |
|------|------|------|
| minGoodsCrn / maxGoodsCrn | number | 最小 / 最大商品集中度（小数 0～1） |
| minSellerCrn / maxSellerCrn | number | 最小 / 最大卖家集中度（小数 0～1） |
| minBrandCrn / maxBrandCrn | number | 最小 / 最大品牌集中度（小数 0～1） |
| minAmazonSelfProportion / maxAmazonSelfProportion | number | 最小 / 最大 Amazon 自营占比（小数 0～1） |
| minFbaProportion / maxFbaProportion | number | 最小 / 最大 FBA 占比（小数 0～1） |
| minFbmProportion / maxFbmProportion | number | 最小 / 最大 FBM 占比（小数 0～1） |
| minEbcProportion / maxEbcProportion | number | 最小 / 最大 A+ 数量占比（小数 0～1） |

### 新品数量占比（入参刻度以 schema 为准）

| 参数 | 类型 | 说明 |
|------|------|------|
| minNewProportion / maxNewProportion | number | 最小 / 最大新品数量占比（与其它占比字段刻度可能不同，以工具 schema / 实网为准） |

### 价格、评分、毛利、BSR（市场平均）

| 参数 | 类型 | 说明 |
|------|------|------|
| minAvgPrice / maxAvgPrice | number | 最低 / 最高平均价格 |
| minAvgRating / maxAvgRating | number | 最低 / 最高平均评分值 |
| minAvgRatings / maxAvgRatings | integer | 最低 / 最高平均评分数 |
| minAvgProfit / maxAvgProfit | number | 最低 / 最高平均毛利率（输入 N 表示 N%，0–100） |
| minAvgBsr / maxAvgBsr | integer | 最低 / 最高平均 BSR 排名 |

### 新品维度

| 参数 | 类型 | 说明 |
|------|------|------|
| minNewCount / maxNewCount | integer | 最小 / 最大新品数量 |
| minNewAvgPrice / maxNewAvgPrice | number | 最小 / 最大新品平均价格 |
| minNewAvgRating / maxNewAvgRating | number | 最小 / 最大新品平均星级 |
| minNewAvgRatings / maxNewAvgRatings | integer | 最小 / 最大新品平均评分数 |
| minNewAvgUnits / maxNewAvgUnits | number | 最低 / 最高新品月均销量 |
| minNewAvgRevenue / maxNewAvgRevenue | number | 最低 / 最高新品月均销售额 |

### 头部 Listing 指标

| 参数 | 类型 | 说明 |
|------|------|------|
| minTopAvgUnits / maxTopAvgUnits | integer | 最低 / 最高头部月均销量 |
| minTopAvgRevenue / maxTopAvgRevenue | number | 最低 / 最高头部月均销售额 |
| minTopAvgBsr / maxTopAvgBsr | integer | 最低 / 最高头部平均 BSR |

### 重量与体积

| 参数 | 类型 | 说明 |
|------|------|------|
| minWeight / maxWeight | number | 最低 / 最高重量 |
| minVolume / maxVolume | number | 最低 / 最高体积 |

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

### orderField 可选值

与工具 schema「表 1.6」一致。

| 取值 | 含义 |
|------|------|
| total_units | 月销量 |
| total_amount | 月销售额 |
| bsr_rank | BSR 排名 |
| price | 价格 |
| rating | 评分 |
| reviews | 评分数 |
| profit | 毛利率 |
| reviews_rate | 留评率 |
| available_date | 上架时间 |
| questions | Q&A |
| total_units_growth | 月销量增长率 |
| total_amount_growth | 月销售额增长率 |
| reviews_increasement | 月新增评分数 |
| bsr_rank_cv | 近 7 天 BSR 增长数 |
| bsr_rank_cr | 近 7 天 BSR 增长率 |
| amz_unit | 子体销量 |

## 响应结构

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 类目市场列表（对应第三方 `data.items`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

### `data[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[] | object | 单条类目市场 |
| data[].nodeId | string | 节点 ID |
| data[].nodeIdPath | string | 节点 ID 路径 |
| data[].nodeLabelName | string | 节点名称 |
| data[].nodeLabelPath | string | 节点名称路径 |
| data[].nodeLabelLocale | string | 节点名称翻译 |
| data[].nodeLabelPathLocale | string | 节点名称路径翻译 |
| data[].marketplace | string | 市场标志 |
| data[].currency | string | 该市场的货币类型 |
| data[].ranking | integer | 排名 |
| data[].totalProducts | integer | 商品总数 |
| data[].topProducts | integer | 样本数量 |
| data[].sellers | integer | 卖家数量 |
| data[].brands | integer | 品牌数量 |
| data[].avgSellers | number | 平均卖家数 |
| data[].avgUnits | integer | 月均销量 |
| data[].totalUnits | integer | 月总销量 |
| data[].avgRevenue | number | 月均销售额 |
| data[].totalRevenue | number | 月总销售额 |
| data[].avgPrice | number | 平均价格 |
| data[].avgRating | number | 平均评分值 |
| data[].avgRatings | integer | 平均评分数 |
| data[].avgBsr | integer | 平均 BSR |
| data[].avgProfit | number | 平均利润率(%) |
| data[].fbaProportion | number | FBA 占比(%) |
| data[].fbmProportion | number | FBM 占比(%) |
| data[].amazonSelfProportion | number | Amazon 自营占比(%) |
| data[].ebcProportion | number | A+ 商品占比(%) |
| data[].returnRatio | number | 退货率(%) |
| data[].avgReturnRatio | number | 退货率类目平均值(%) |
| data[].searchToPurchaseRatio | number | 搜索购买比(千分比) |
| data[].sellerNation | string | 最多卖家归属地 code |
| data[].sellerNationLabel | string | 最多卖家归属地 label |
| data[].sellerProportion | number | 最多卖家归属地占比(%) |
| data[].avgWeight | number | 平均重量(pound) |
| data[].baseAvgWeight | number | 平均重量(g) |
| data[].avgVolume | number | 平均体积(in³) |
| data[].baseAvgVolume | number | 平均体积(cm³) |
| data[].top10Images | array | 前 10 商品图片，元素见下表 |

### `data[].top10Images[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[].top10Images[] | object | 前 10 商品图片元素 |
| data[].top10Images[].image | string | 图片链接 |
| data[].top10Images[].asin | string | ASIN |

## MCP 调用示例

使用本 reference 的完整 `proxy_call` 示例；其他筛选组合仍直接放入 `arguments`。


## 错误与成本

检查下游 `errcode`/`errorCode` 与 `errmsg`/`message`；401、402、403 按 `onboarding.md` 分层。每次分页、换月份或换条件均是新的收费调用；不得自动重试。
