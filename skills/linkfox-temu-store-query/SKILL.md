---
name: linkfox-temu-store-query
description: 按多维度筛选 Temu 店铺（店名/ID、国家站点、后台类目、全托管/半托管、总/周/月销量与销售额、评分、评论、粉丝、商品数、开店时间等）。当用户提到 Temu 店铺、Temu 店铺分析、Temu seller、Temu 店铺排行、Temu 半托管店铺、Temu 销售额、temu stores、Temu store query 时触发。即使用户未提及工具名，只要在 Temu 上找店铺、筛店铺数据或分析店铺表现，也应触发此技能。
---

# Temu 店铺查询

在具备 LinkFox「第三方数据服务」MCP 时，对应网关路由 **`ehunt/temu/storeQuery`** 调用（MCP 展示名：**Temu 店铺查询**，确切工具名以当前环境下发的工具元数据为准）。鉴权与上游路由由网关处理；若响应含根级 `code` 字段，是否成功以实网为准。

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100。
- **区间入参**：`*Min` / `*Max` 成对出现（总/周/月销量、总/周/月销售额、评分、评论、粉丝、商品数），组成上游区间。
- **站点**：`siteId` 国家站点 ID，多个逗号分隔（如 `211`=美国、`76`=英国）。
- **类目**：`category` 后台类目 ID，多个逗号分隔。
- **托管模式**：`isLocal`（0=全托管，1=半托管，字符串）。
- **开店时间**：`listedTimeBegin` / `listedTimeEnd`（YYYY-MM-DD）。
- **排序**：`sortBy` 为「字段-方向」字符串，如 `order_week_count-0`（周销量降序，默认）、`order_count-0`、`total_revenue-0`、`rating-0`。

## 脚本（可选）

命令行调试：`python scripts/temu_store_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
