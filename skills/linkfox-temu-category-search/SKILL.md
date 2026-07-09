---
name: linkfox-temu-category-search
description: 在已同步到本地库的 Temu 类目数据中按关键词检索类目中文名、英文名与类目 id，用于商品/店铺筛选的类目 id。当用户提到 Temu 类目、Temu category id、Temu 类目树、Temu 后台类目、temu 品类、syncTemuCategory（Temu 品类同步）后查询类目、Temu category search 时触发。即使用户未提及工具名，只要在本地已同步的 Temu 类目库里按关键词找类目 id，也应触发此技能。
---

# Temu 类目检索

## 要点

- **必填**：`keyword`（子串匹配类目中文名、英文名、类目 id）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id` / `categoryId`** 可作为 Temu 商品查询的 `categoryHome`/`categoryBackend`、店铺查询的 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## 脚本（可选）

命令行调试：`python scripts/temu_category_search.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
