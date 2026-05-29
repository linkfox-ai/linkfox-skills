---
name: linkfox-amazon-help-doc-changes
description: 监控亚马逊卖家帮助文档（帮助中心）的内容变更，经 AI 筛选后返回对卖家有价值的改动，支持按变更时间区间、标题关键词分页检索，并按变更记录 ID 获取 AI 变更摘要、具体改动点与最新文档全文。当用户提到亚马逊帮助文档变更、帮助中心更新、规则变动监控、政策/费用文档调整、合规预警、文档改了什么、最新文档全文，或 Amazon help doc changes, Seller Central help center updates, policy/fee documentation changes, compliance alert 时触发此技能。即使用户未明确提及"帮助文档变更"，只要其需求涉及亚马逊帮助中心文档的更新监控及变更详情，也应触发此技能。
---

# Amazon Help Doc Change Monitor

This skill monitors changes to Amazon **Seller Central Help** documentation. An AI layer pre-screens edits and surfaces only the changes that actually matter to sellers. It is a two-step (list → detail) flow: first list AI-curated valuable changes by time window / title keyword, then fetch the change detail + latest full document by its `id`.

## Core Concepts

- **AI-curated, not raw diffs**: results contain **only** changes the AI judges "valuable to sellers". Pure formatting / non-substantive edits are filtered out, so the returned count is usually far smaller than the document's actual edit count — this is by design, not missing data.
- **Two coupled tools**:
  1. `amazon/helpDocChanges` — paginated **list** of valuable changes (structured), each with an AI-generated Chinese summary, ordered by change time (newest first).
  2. `amazon/helpDocDetail` — full **change detail** for one change `id`: AI summary + what specifically changed + the latest document body (Markdown).
- **Coverage & timing**: monitors English (`en-US`) help docs by default. `changedAt` is the **detection** time (when the system detected the diff), not Amazon's official publish time. Change monitoring data starts from **2026-05-29**. The Amazon backend original is authoritative.

## Parameters

### List (`amazon/helpDocChanges`)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| keyword | string | No | Document-title fuzzy match (case-insensitive) | - |
| changedAtGte | string | No | Change-time lower bound (incl.), `yyyy-MM-dd HH:mm:ss` | last 3 months |
| changedAtLte | string | No | Change-time upper bound (incl.), `yyyy-MM-dd HH:mm:ss` | now |
| page | integer | No | Page number, starting at 1 | 1 |
| pageSize | integer | No | Items per page, 1-100 | 20 |

No parameter is required — call with no params to get the last 3 months of valuable changes.

### Detail (`amazon/helpDocDetail`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Change-record ID (≥1) from the list response `data[].id` |

## API Usage

This skill calls the LinkFox tool gateway. See `references/api.md` for calling conventions, request parameters, response structure, and error codes. You can also run the scripts directly:

```bash
python scripts/amazon_help_doc_changes.py '{"keyword": "FBA", "pageSize": 20}'
python scripts/amazon_help_doc_detail.py '{"id": <id from the list response>}'
```

## How to Build Queries

1. **Set the time window**: convert "近一个月 / since 2026-03" into `changedAtGte` / `changedAtLte`. Leave empty for the default last 3 months.
2. **Filter by keyword**: pass topical terms (e.g. `FBA`, `fee`, `inventory`) into `keyword` for title matching.
3. **Paginate**: increase `page` to scan more changes.
4. **Drill into a change**: take a record's `id` (integer) from the list and call the detail script to read the AI summary, the specific edits, and the latest document.

### Usage Examples

**1. Valuable changes in the last 3 months (default)**
```json
{}
```
**2. FBA-related doc changes in a date range**
```json
{"keyword": "FBA", "changedAtGte": "2026-03-01 00:00:00", "changedAtLte": "2026-05-28 23:59:59"}
```
**3. Page 2, 50 per page**
```json
{"page": 2, "pageSize": 50}
```
**4. Full change detail of one record**
```json
{"id": 35}
```

## Display Rules

1. **List view**: present results as a table with title, breadcrumb (目录路径), change time, and the AI summary; include the original `url`.
2. **Detail view**: render the `stdout` Markdown as-is; keep the leading change-summary / change-time / breadcrumb / source-link block.
3. **Set expectations on count**: when results look sparse, remind the user that only AI-judged valuable changes are returned (formatting-only edits are filtered) — a low count is expected, not a data gap.
4. **Only present data**: report what changed; do not add subjective business advice.
5. **Detection-time caveat**: note that `changedAt` is the detection time, not Amazon's official publish time; the backend original is authoritative.
6. **Error handling**: on a failed call, explain the reason from the error response (e.g. invalid `id` → re-fetch from the list).

## Important Limitations

- **AI-filtered results**: only "valuable to sellers" changes appear; returned count is far smaller than the raw edit count (by design).
- **English docs by default**: monitors `en-US` help documentation.
- **Monitoring start**: change data begins from 2026-05-29; earlier history is unavailable.
- **Detail needs a valid list `id`**: `amazon/helpDocDetail` only accepts an integer `id` returned by `amazon/helpDocChanges`.
- **Not for aggregation**: detail returns long-form text and the list is change metadata — this skill's output is **not** suited for second-pass statistical/aggregation analysis.

## User Expression & Scenario Quick Reference

**Applicable** — Amazon help-center documentation change monitoring:

| User Says | Scenario |
|-----------|----------|
| "近一个月亚马逊帮助文档有哪些值得关注的变更" | Recent valuable changes by time |
| "亚马逊关于 FBA 的帮助文档改了什么" | Keyword-filtered doc-change lookup |
| "帮我看看这条文档变更的详情和最新全文" | Fetch change detail + latest doc by id |
| "帮助中心规则有更新吗" | Help-center rule-change monitoring |
| "费用相关的文档调整" | Fee/policy documentation change tracking |

**Not applicable** — beyond help-doc change monitoring:
- Amazon Seller News policy announcements → use the Amazon policy-news skill
- Product / keyword / sales analytics, listing optimization, review analysis
- Real-time storefront search results or product detail
- Account-specific notifications inside an individual seller account

**Boundary judgment**: if the user wants to know **what changed in Amazon's help documentation** (and the change detail / latest text), this skill applies. If they want Amazon's published **Seller News policy announcements**, use the policy-news skill; if they want product/keyword/sales data, use the corresponding data skills.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/amazon_help_doc_changes.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `amazon_help_doc_changes.py`, `amazon_help_doc_detail.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
