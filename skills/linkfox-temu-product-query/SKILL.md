---
name: linkfox-temu-product-query
description: 按多维度筛选 Temu 商品（关键词/商品 ID/店铺 ID、前后台类目、价格、评分、评论、总/周/日销量、上架时间、全托管/半托管、半托管地区、标签等）。当用户提到 Temu 商品、Temu 选品、拼多多跨境、Temu 爆款、Temu 半托管、全托管商品、Temu product query、temu items 时触发。即使用户未提及工具名，只要在 Temu 上搜商品、看销量/评分/价格或筛品，也应触发此技能。
---

# Temu 商品查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Begin` / `*End` 成对出现（价格、评分、评论、总/周/日销量、上架时间），组成上游区间。
- **类目**：`categoryHome` 前台类目 ID、`categoryBackend` 后台类目 ID；可先用 Temu 品类检索拿到 id。
- **托管模式**：`isLocal`（0=全托管，1=半托管）；半托管可用 `region` 限定地区（多个逗号分隔）。
- **上下架**：`soldOut`（0=上架，1=下架）。
- **标签**：`tags` / `customTags` 多个用逗号分隔。
- **排序**：`sortBy` 为「字段-方向」字符串，如 `order_week-0`（周销量降序，默认）、`price-0`、`order_total-0`、`rating-0`。

## 脚本（可选）

命令行调试：`python scripts/temu_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
