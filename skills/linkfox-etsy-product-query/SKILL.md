---
name: linkfox-etsy-product-query
description: 按多维度筛选 Etsy 商品（关键词/URL、价格、销量、收藏、评论、上架时间、类目、手工/复古等类型、Pick/Bestsell/Raving 等标签）。当用户提到 Etsy 商品、Etsy listing、Etsy 选品、Etsy 爆款、Etsy handmade、Etsy vintage、etsy items、Etsy商品查询时触发。即使用户未提及工具名，只要在 Etsy 上搜商品、看销量/价格/标签或筛品，也应触发此技能。
---

# Etsy 商品查询（`_ehunt_productQuery`）

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：与店铺接口相同思路，`begin*` / `end*` 成对。
- **排序**：`sortBy` 为 **1~6**（上游 `sort_by`）。`sortDesc`：**1=降序，2=升序**（与 `_ehunt_storeQuery` 的 1/0 不同）。
- **商品类型** `productType`：`1` 手工、`2` 复古、`3` 数字、`4` 定制、`9` 其他，多选用逗号。
- **货币**：`currencyCode` 默认 `USD`。
- **类目 id**：`category` 为单品类 ID；可先通过类目检索类技能拿到 id。

## 脚本（可选）

命令行调试：`python scripts/etsy_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
