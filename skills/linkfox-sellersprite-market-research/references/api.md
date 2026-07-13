# 卖家精灵-选市场列表 API 参考

本文档与工具 `_sellersprite_market_research` 的 `inputSchema` / `outputSchema`（见 `temp/tools20260430.txt`）对齐。

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/market/research`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

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

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 类目市场列表（对应第三方 `data.items`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

### data[] 元素（单条类目市场）

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeId | string | 节点 ID |
| nodeIdPath | string | 节点 ID 路径 |
| nodeLabelName | string | 节点名称 |
| nodeLabelPath | string | 节点名称路径 |
| nodeLabelLocale | string | 节点名称翻译 |
| nodeLabelPathLocale | string | 节点名称路径翻译 |
| marketplace | string | 市场标志 |
| currency | string | 该市场的货币类型 |
| ranking | integer | 排名 |
| totalProducts | integer | 商品总数 |
| topProducts | integer | 样本数量 |
| sellers | integer | 卖家数量 |
| brands | integer | 品牌数量 |
| avgSellers | number | 平均卖家数 |
| avgUnits | integer | 月均销量 |
| totalUnits | integer | 月总销量 |
| avgRevenue | number | 月均销售额 |
| totalRevenue | number | 月总销售额 |
| avgPrice | number | 平均价格 |
| avgRating | number | 平均评分值 |
| avgRatings | integer | 平均评分数 |
| avgBsr | integer | 平均 BSR |
| avgProfit | number | 平均利润率(%) |
| fbaProportion | number | FBA 占比(%) |
| fbmProportion | number | FBM 占比(%) |
| amazonSelfProportion | number | Amazon 自营占比(%) |
| ebcProportion | number | A+ 商品占比(%) |
| returnRatio | number | 退货率(%) |
| avgReturnRatio | number | 退货率类目平均值(%) |
| searchToPurchaseRatio | number | 搜索购买比(千分比) |
| sellerNation | string | 最多卖家归属地 code |
| sellerNationLabel | string | 最多卖家归属地 label |
| sellerProportion | number | 最多卖家归属地占比(%) |
| avgWeight | number | 平均重量(pound) |
| baseAvgWeight | number | 平均重量(g) |
| avgVolume | number | 平均体积(in³) |
| baseAvgVolume | number | 平均体积(cm³) |
| top10Images | array | 前 10 商品图片，元素见下表 |

### top10Images[] 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| image | string | 图片链接 |
| asin | string | ASIN |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/market/research   -H "Authorization: $LINKFOXAGENT_API_KEY"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "month": "nearly",
    "minAvgRevenue": 10000,
    "maxGoodsCrn": 0.4,
    "orderField": "total_amount",
    "orderDesc": true,
    "page": 1,
    "size": 50
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-research",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```
