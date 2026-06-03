---
name: linkfox-ehunt-shopify-product-query
description: 通过 EHunt Shopify 商品查询（网关路由 `ehunt/shopify/productQuery`）按多维度筛选独立站 Shopify 商品（关键词/URL、价格、周销量、上架时间、Facebook 广告、竞争度、是否有货源、发货国家等）。当用户提到 EHunt Shopify 商品、Shopify 选品、独立站选品、Shopify 爆款、Shopify dropshipping、独立站铺货、Facebook 广告商品、Shopify product query、shopify items 时触发。即使用户未写 EHunt，只要在 Shopify 独立站上搜商品、看周销量/销售额/竞争度或筛品，也应触发此技能。
---

# EHunt Shopify 商品查询（`ehunt/shopify/productQuery`）

在具备 LinkFox「第三方数据服务」MCP 时，对应网关路由 **`ehunt/shopify/productQuery`** 调用（MCP 展示名：**Shopify 商品查询**，确切工具名以当前环境下发的工具元数据为准）。鉴权与上游路由由网关处理；若响应含根级 `code` 字段，是否成功以实网为准。

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Min` / `*Max` 成对出现，组成上游区间；只填一侧时上游为「起始~」或「~结束」。
- **排序**：`sortBy` 为整数枚举（默认 `14`=周销量降序，另含价格/广告数/竞争度/销售额等多种取值，详见 `references/api.md`）。
- **布尔类筛选**：`facebookAd`（1=有广告）、`hasSupplier`（1=有货源，0=无）、`showDeleted`（1=含已下架）均为整数开关。
- **发货国家**：`country` 传两位国家代码（如 `US`）。

## 脚本（可选）

命令行调试：`python scripts/ehunt_shopify_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/ehunt_shopify_product_query.py --out-dir <DIR> '<params>'
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
