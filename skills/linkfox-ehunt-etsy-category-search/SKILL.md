---
name: linkfox-ehunt-etsy-category-search
version: 1.0.0
category: product-sourcing
description: 通过 `_ehunt_etsyCategorySearch`（MCP 展示名「Etsy品类查询」）在已同步到 MCP 库的 EHunt Etsy 类目数据中检索类目名称、id 与 parentIds，用于商品/店铺筛选的类目 id。当用户提到 EHunt Etsy 类目、Etsy category id、Etsy 类目树、_ehunt_etsyCategorySearch、Etsy品类查询、syncEtsyCategory / _ehunt_syncEtsyCategory（Etsy品类同步）后查类目 时触发。即使用户未写 EHunt，只要在本地已同步的 Etsy 类目库里按关键词找类目 id，也应触发此技能。
---

# EHunt Etsy 类目检索（`_ehunt_etsyCategorySearch`）

在具备 LinkFox「第三方数据服务」MCP 时，按工具名 **`_ehunt_etsyCategorySearch`** 调用（MCP 展示名：**Etsy品类查询**，以当前环境下发的工具元数据为准）。数据来自 **MCP 库本地检索**。

## 前置条件

库内须已有 **`_ehunt_syncEtsyCategory`** 写入的全量类目（MCP 展示名：**Etsy品类同步**）。若无数据或结果为空，应先完成同步再检索。

## 要点

- **必填**：`keyword`（子串匹配类目名称、类目 id、`parentIds`）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id`** 可作为 `_ehunt_productQuery` / 店铺侧 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## 脚本（可选）

命令行调试：`python scripts/ehunt_etsy_category_search.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。
