---
name: linkfox-sellersprite-market-statistics
description: 使用卖家精灵选市场统计能力，按类目节点输出市场统计看板，包含头部Listing平均评分、均价、BSR、销量、卖家数量与新品相关指标，适合快速判断某类目市场质量与竞争格局。当用户提到类目市场统计、选市场看板、市场基础盘评估、节点市场质量、头部商品统计、SellerSprite market statistics、category statistics时触发此技能。即使用户未明确提及"卖家精灵"，只要需求是按类目节点查看聚合统计结果，也应触发此技能。
---

# SellerSprite Market Statistics

This skill helps fetch node-level market statistics for Amazon categories via SellerSprite.

## Core Concepts

- **节点统计**：对指定类目节点做聚合统计，不返回完整商品明细。
- **TopN 口径**：`topN` 决定头部商品统计样本数量（默认 10）。
- **新品定义**：`newProduct` 指定“新品”按最近 N 个月定义（默认 6）。

## API Usage

- Endpoint: `POST https://tool-gateway.linkfox.com/sellersprite/market/statistics`
- Auth: Header `Authorization: <api_key>` (`LINKFOXAGENT_API_KEY`)
- 完整说明见 `references/api.md`：含 `marketplace` / `month` 规则，必填 `nodeIdPath`，`topN`/`newProduct` 默认值；响应含 `data[]` 中市场整体、`hl*` 头部、`new*` 新品与上架日期等全部字段（与 `_sellersprite_market_statistics` 的 `outputSchema` 一致）。
- Runnable script: `scripts/sellersprite_market_statistics.py`

## Parameters

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| nodeIdPath | string | 是 | 节点ID路径，如 `1064954:1069242:...` |
| month | string | 否 | `nearly` 或 `yyyyMM` |
| topN | integer | 否 | 头部样本数，默认 10 |
| newProduct | integer | 否 | 新品定义（月），默认 6 |

## Usage Example

```json
{
  "marketplace": "US",
  "nodeIdPath": "172282:281407",
  "month": "nearly",
  "topN": 10,
  "newProduct": 6
}
```

## Display Rules

1. 明确展示统计口径：`topN`、`newProduct`、时间范围。
2. 先输出关键总览指标，再输出扩展字段。
3. 若用户未给 `nodeIdPath`，先引导用户提供节点路径或先做类目定位。

## Important Limitations

- 必填参数：`marketplace`、`nodeIdPath`
- `nodeIdPath` 必须为合法节点路径
- 月份查询受第三方历史范围限制

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.
