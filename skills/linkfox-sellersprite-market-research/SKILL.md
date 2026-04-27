---
name: linkfox-sellersprite-market-research
description: 使用卖家精灵选市场列表能力，基于类目维度筛选亚马逊细分市场，支持市场规模、竞争度、头部集中度、卖家结构、新品占比、价格/评分/毛利区间等大量条件，用于发现可进入市场与评估选品方向。当用户提到亚马逊市场调研、细分类目研究、市场机会筛选、市场集中度分析、新品机会、选市场、SellerSprite market research、category market research时触发此技能。即使用户未明确提及"卖家精灵"，只要需求是按类目维度筛选和评估亚马逊市场，也应触发此技能。
---

# SellerSprite Market Research

This skill helps screen and rank Amazon category markets using SellerSprite market-research data.

## Core Concepts

- **类目市场级分析**：不是商品级列表，而是按类目/节点聚合后的市场画像。
- **市场规模**：月均销量、月均销售额、商品数量等。
- **竞争结构**：卖家/品牌集中度、头部集中度、自营占比、FBA/FBM 占比。
- **新品机会**：新品数量、新品占比、新品均价/评分/销量等。

## API Usage

- Endpoint: `POST https://tool-gateway.linkfox.com/sellersprite/market/research`
- Auth: Header `Authorization: <api_key>` (`LINKFOXAGENT_API_KEY`)
- See full details in `references/api.md`.
- Runnable script: `scripts/sellersprite_market_research.py`

## Key Parameters

> 该接口支持大量筛选项（70+），以下为高频参数；完整说明见 `references/api.md`。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| month | string | 否 | `nearly` 或 `yyyyMM` |
| nodeIdPath | string | 否 | 类目节点路径 |
| departmentKeyword | string | 否 | 类目关键字路径 |
| page / size | integer | 否 | 分页，默认 1/50，`size` 最大 200 |
| orderField / orderDesc | string/boolean | 否 | 排序字段与方向 |
| minAvgRevenue / maxAvgRevenue | number | 否 | 月均销售额范围 |
| minAvgUnits / maxAvgUnits | integer | 否 | 月均销量范围 |
| minGoodsCount / maxGoodsCount | integer | 否 | 商品数量范围 |
| minGoodsCrn / maxGoodsCrn | number | 否 | 商品集中度（%） |
| minSellerCrn / maxSellerCrn | number | 否 | 卖家集中度（%） |
| minBrandCrn / maxBrandCrn | number | 否 | 品牌集中度（%） |
| minNewProportion / maxNewProportion | number | 否 | 新品占比（%） |
| minAvgPrice / maxAvgPrice | number | 否 | 平均价格范围 |
| minAvgRating / maxAvgRating | number | 否 | 平均评分范围 |
| minAvgProfit / maxAvgProfit | number | 否 | 平均毛利率（%） |

## Usage Example

```json
{
  "marketplace": "US",
  "month": "nearly",
  "minAvgRevenue": 10000,
  "maxGoodsCrn": 40,
  "minNewProportion": 10,
  "maxSellerCrn": 50,
  "orderField": "total_amount",
  "orderDesc": true,
  "page": 1,
  "size": 50
}
```

## Display Rules

1. 先给出市场候选 Top N，再展示核心指标（市场规模、集中度、新品占比）。
2. 清晰标注单位：比例字段是 `%`，金额按站点币种。
3. 显示筛选条件回显，便于用户复现。
4. 若结果过少或过多，建议用户调整关键阈值（如集中度、规模阈值）。

## Important Limitations

- 必填参数：`marketplace`
- 每页最多 200 条
- 历史月份范围受第三方限制（通常近24个月）

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.
