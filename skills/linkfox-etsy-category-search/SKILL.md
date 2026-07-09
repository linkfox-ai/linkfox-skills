---
name: linkfox-etsy-category-search
description: Etsy 类目数据。可检索类目名称、id 与 parentIds，用于商品/店铺筛选的类目 id。当用户提到 Etsy 类目、Etsy category id、Etsy 类目树、Etsy品类查询、syncEtsyCategory、查询类目时触发。即使用户未提及工具名，只要在本地已同步的 Etsy 类目库里按关键词找类目 id，也应触发此技能。
---

# Etsy 类目检索

## 要点

- **必填**：`keyword`（子串匹配类目名称、类目 id、`parentIds`）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id`** 可作为 Etsy商品搜索 / 店铺侧 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## 脚本（可选）

命令行调试：`python scripts/etsy_category_search.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
