---
name: linkfox-shopify-product-query
description: 按多维度筛选独立站 Shopify 商品（关键词/URL、价格、周销量、上架时间、Facebook 广告、竞争度、是否有货源、发货国家等）。当用户提到 Shopify 商品、Shopify 选品、独立站选品、Shopify 爆款、Shopify dropshipping、独立站铺货、Facebook 广告商品、Shopify product query、shopify items 时触发。即使用户未提及工具名，只要在 Shopify 独立站上搜商品、看周销量/销售额/竞争度或筛品，也应触发此技能。
---

# Shopify 商品查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Min` / `*Max` 成对出现，组成上游区间；只填一侧时上游为「起始~」或「~结束」。
- **排序**：`sortBy` 为整数枚举（默认 `14`=周销量降序，另含价格/广告数/竞争度/销售额等多种取值，详见 `references/api.md`）。
- **布尔类筛选**：`facebookAd`（1=有广告）、`hasSupplier`（1=有货源，0=无）、`showDeleted`（1=含已下架）均为整数开关。
- **发货国家**：`country` 传两位国家代码（如 `US`）。

## 脚本（可选）

命令行调试：`python scripts/shopify_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
