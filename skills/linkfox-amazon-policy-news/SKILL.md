---
name: linkfox-amazon-policy-news
description: 查询亚马逊卖家后台 Seller News 政策与合规类新闻，支持按站点、发布时间区间、标题关键词分页检索新闻列表，并按新闻 ID 获取完整正文。当用户提到亚马逊政策新闻、卖家合规公告、平台规则变动、政策预警、FBA/费用政策更新、Seller News、多站点政策动态、政策原文、新闻详情，或 Amazon policy news, seller compliance, Seller News, platform policy changes, policy alerts, FBA fee policy 时触发此技能。即使用户未明确提及"政策新闻"，只要其需求涉及亚马逊官方面向卖家发布的政策/合规公告及其原文，也应触发此技能。
---

# Amazon Seller Policy News

This skill retrieves Amazon **Seller News** policy & compliance announcements for cross-border sellers. It is a two-step (list → detail) flow: first list news by site / time window / title keyword, then fetch the full article body by its `id`.

## Core Concepts

- **Source**: Amazon Seller Central 「Seller News」 official announcements, captured via periodic snapshots. Content reflects the snapshot time and may lag the live page; the Amazon backend original is authoritative.
- **Scope**: Currently only the **Policy and Compliance** (政策与合规) category.
- **Two coupled tools**:
  1. `amazon/policyNews` — paginated **list**; returns structured records, including a ~300-char preview snippet.
  2. `amazon/newsDetail` — full article **body** (Markdown) for a single news `id` obtained from the list.
- **Time range**: Defaults to the last 3 months; queryable up to the last 1 year (earlier requests error out).

## Parameters

### List (`amazon/policyNews`)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| site | string | Yes | Marketplace code (uppercase); see Supported Marketplaces | US |
| keyword | string | No | Title fuzzy match (case-insensitive) | - |
| publishedAtGte | string | No | Published-time lower bound (incl.), `yyyy-MM-dd HH:mm:ss` | last 3 months |
| publishedAtLte | string | No | Published-time upper bound (incl.), `yyyy-MM-dd HH:mm:ss` | now |
| page | integer | No | Page number, starting at 1 | 1 |
| pageSize | integer | No | Items per page, 1-100 | 20 |

### Detail (`amazon/newsDetail`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | News article ID from the list response `data[].id` |
| site | string | No | Marketplace code (uppercase); pass the same site the news was listed under. Default US |

### Supported Marketplaces

`site` accepts (uppercase): US, JP, UK, AU, BE, BR, CA, EG, FR, DE, IN, IT, MX, NL, PL, SA, SG, ES, SE, TR, AE, ZA, IE. Default is **US** when the user doesn't specify.

## API Usage

This skill calls the LinkFox tool gateway. See `references/api.md` for calling conventions, request parameters, response structure, and error codes. You can also run the scripts directly:

```bash
python scripts/amazon_policy_news.py '{"site": "US", "keyword": "FBA", "pageSize": 20}'
python scripts/amazon_news_detail.py '{"id": "<id from the list response>", "site": "US"}'
```

## How to Build Queries

1. **Pick the marketplace**: map the user's target country to the `site` code (default US).
2. **Set the time window**: convert "近一个月 / last month / since 2026-01" into `publishedAtGte` / `publishedAtLte`. Leave empty for the default last 3 months.
3. **Filter by keyword**: pass topical terms (e.g. `FBA`, `fee`, `tax`) into `keyword` for title matching.
4. **Paginate**: increase `page` to scan deeper.
5. **Drill into a story**: take a record's `id` from the list and call the detail script to read the full body. Pass the same `site` the news was listed under (default US).

### Usage Examples

**1. Recent US policy news**
```json
{"site": "US", "pageSize": 20}
```
**2. US news mentioning FBA in a date range**
```json
{"site": "US", "keyword": "FBA", "publishedAtGte": "2026-01-01 00:00:00", "publishedAtLte": "2026-05-28 23:59:59"}
```
**3. UK policy news, page 2**
```json
{"site": "UK", "page": 2, "pageSize": 50}
```
**4. Full body of one article (pass the source site)**
```json
{"id": "QVRWUERLSUtYMERFUiNHOTZRODY5N1pXWU1DR0I3", "site": "US"}
```

## Display Rules

1. **List view**: present results as a table with title, site, category, published time, and the preview snippet; include the original `url` so users can open the source.
2. **Detail view**: render the `stdout` Markdown as-is; keep the leading meta line (site / category / published time / source link).
3. **Only present data**: report what the news says; do not add subjective business advice or speculate on future policy.
4. **Snapshot reminder**: when relevant, note that content is a snapshot and the Amazon backend original is authoritative.
5. **Error handling**: on a failed call, explain the reason from the error response (e.g. invalid `id` → re-fetch from the list) instead of guessing.

## Important Limitations

- **Policy & Compliance only**: other Seller News categories are not covered.
- **Default window is 3 months; max 1 year**: requests beyond ~1 year error out.
- **Detail needs a valid list `id`**: `amazon/newsDetail` only accepts an `id` returned by `amazon/policyNews`; unknown ids return a "news not found" error.
- **Not for aggregation**: detail returns long-form text and the list is news metadata — this skill's output is **not** suited for second-pass statistical/aggregation analysis.

## User Expression & Scenario Quick Reference

**Applicable** — Amazon official seller policy / compliance announcements:

| User Says | Scenario |
|-----------|----------|
| "近一个月美国站有哪些政策新闻" | Recent policy news by site/time |
| "亚马逊最近 FBA 费用政策有变化吗" | Keyword-filtered policy lookup |
| "帮我看看这条政策新闻的全文" | Fetch full article body by id |
| "英国站的合规公告" | Cross-marketplace policy news |
| "亚马逊平台规则有什么更新" | Platform rule-change monitoring |

**Not applicable** — beyond official Seller News policy announcements:
- Help-doc (帮助中心) content changes → use the Amazon help-doc change skill
- Product / keyword / sales analytics, listing optimization, review analysis
- Real-time storefront search results or product detail
- Account-specific notifications inside an individual seller account

**Boundary judgment**: if the user wants Amazon's **publicly published policy & compliance news for sellers** (and its full text), this skill applies. If they want changes to Amazon **help documentation**, use the help-doc change skill; if they want product/keyword/sales data, use the corresponding data skills.

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
python scripts/response_io.py run --script scripts/amazon_news_detail.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `amazon_news_detail.py`, `amazon_policy_news.py`. Pass `--script scripts/<name>.py` to choose the one you need.

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
