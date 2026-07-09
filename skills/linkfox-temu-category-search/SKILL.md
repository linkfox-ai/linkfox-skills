---
name: linkfox-temu-category-search
description: 通过 Temu 品类检索（网关路由 `ehunt/temu/temuCategorySearch`）在已同步到本地库的 Temu 类目数据中按关键词检索类目中文名、英文名与类目 id，用于商品/店铺筛选的类目 id。当用户提到 Temu 类目、Temu category id、Temu 类目树、Temu 后台类目、temu 品类、syncTemuCategory（Temu 品类同步）后查询类目、Temu category search 时触发。即使用户未提及工具名，只要在本地已同步的 Temu 类目库里按关键词找类目 id，也应触发此技能。
---

# Temu 类目检索（`ehunt/temu/temuCategorySearch`）

在具备 LinkFox「第三方数据服务」MCP 时，对应网关路由 **`ehunt/temu/temuCategorySearch`** 调用（MCP 展示名：**Temu 品类查询**，确切工具名以当前环境下发的工具元数据为准）。数据来自 **本地库检索**。

## 前置条件

库内须已有 **`ehunt/temu/syncTemuCategory`**（MCP 展示名：**Temu 品类同步**）写入的全量类目。若无数据或结果为空，应先完成同步再检索。

## 要点

- **必填**：`keyword`（子串匹配类目中文名、英文名、类目 id）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id` / `categoryId`** 可作为 Temu 商品查询的 `categoryHome`/`categoryBackend`、店铺查询的 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## 脚本（可选）

命令行调试：`python scripts/temu_category_search.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
