---
name: linkfox-ehunt-etsy-category-search
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

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/ehunt_etsy_category_search.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
