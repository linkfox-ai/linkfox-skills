---
name: linkfox-etsy-store-query
description: 通过 MCP 工具 `_ehunt_storeQuery`（展示名「Etsy店铺查询」）按多维度筛选 Etsy 店铺（销量、收藏、评论、开店时间、国家、主营类目、Raving/星标等）。当用户提到 Etsy 店铺、Etsy 店搜、Etsy seller、Etsy 店铺排行、Etsy 周销量店铺、etsy stores、Etsy店铺查询、_ehunt_storeQuery 时触发。即使用户未提及工具名，只要在 Etsy 上找店铺、筛店铺数据或分析店铺表现，也应触发此技能。
---

# Etsy 店铺查询（`_ehunt_storeQuery`）

在具备 LinkFox「第三方数据服务」MCP 时，按工具名 **`_ehunt_storeQuery`** 调用（MCP 展示名：**Etsy店铺查询**，以当前环境下发的工具元数据为准）。鉴权与上游路由由网关处理；若响应含根级 `code` 字段，是否成功以实网为准。

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100。
- **区间入参**：`begin*` / `end*` 成对对应上游逗号范围；只填一侧时上游为「起始~」或「~结束」。
- **排序**：`sortBy` 仅 **8~11**（8 总销量、9 周销量、10 评论数、11 收藏数）。`sortDesc`：**1=降序，0=升序**（勿与商品接口的 `sortDesc` 混用）。

## 脚本（可选）

命令行调试：`python scripts/etsy_store_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
