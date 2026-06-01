---
name: linkfox-ehunt-etsy-product-query
description: 通过 EHunt MCP 工具 `_ehunt_productQuery`（展示名「Etsy商品查询」）按多维度筛选 Etsy 商品（关键词/URL、价格、销量、收藏、评论、上架时间、类目、手工/复古等类型、Pick/Bestsell/Raving 等）。当用户提到 EHunt Etsy 商品、Etsy listing、Etsy 选品、Etsy 爆款、Etsy handmade、Etsy vintage、ehunt items、Etsy商品查询、_ehunt_productQuery 时触发。即使用户未写 EHunt，只要在 Etsy 上搜商品、看销量/价格/标签或筛品，也应触发此技能。
---

# EHunt Etsy 商品查询（`_ehunt_productQuery`）

在具备 LinkFox「第三方数据服务」MCP 时，按工具名 **`_ehunt_productQuery`** 调用（MCP 展示名：**Etsy商品查询**，以当前环境下发的工具元数据为准）。鉴权与上游路由由网关处理；若响应含根级 `code` 字段，是否成功以实网为准。

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：与店铺接口相同思路，`begin*` / `end*` 成对。
- **排序**：`sortBy` 为 **1~6**（EHunt 上游 `sort_by`）。`sortDesc`：**1=降序，2=升序**（与 `_ehunt_storeQuery` 的 1/0 不同）。
- **商品类型** `productType`：`1` 手工、`2` 复古、`3` 数字、`4` 定制、`9` 其他，多选用逗号。
- **货币**：`currencyCode` 默认 `USD`。
- **类目 id**：`category` 为单品类 ID；可先通过类目检索类技能拿到 id。

## 脚本（可选）

命令行调试：`python scripts/ehunt_etsy_product_query.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/ehunt_etsy_product_query.py --out-dir <DIR> '<params>'
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
