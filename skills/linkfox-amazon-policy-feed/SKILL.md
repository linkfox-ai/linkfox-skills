---
name: linkfox-amazon-policy-feed
description: 查询亚马逊最新政策法规与资讯，支持按站点、时间区间分页检索资讯列表（含 AI 中文摘要），并按记录 ID 获取完整正文。当用户提到亚马逊政策法规、卖家合规公告、平台规则变动、政策预警、FBA/费用政策更新、多站点政策动态、政策原文、资讯详情，或 Amazon policy feed, seller compliance, policy changes, regulation alerts 时触发此技能。即使用户未明确提及"政策法规"，只要其需求涉及亚马逊官方面向卖家发布的政策法规与资讯及其原文，也应触发此技能。
---

# Amazon Policy & Regulation Feed

This skill retrieves Amazon's latest **policy & regulation** feed for cross-border sellers. It is a two-step (list then detail) flow: first list feed items by site / time window, then fetch the full article body by its `id`.

## Core Concepts

- **Source**: Amazon official policy & regulation updates for sellers, curated by AI to surface items valuable to cross-border operations.
- **AI summary**: Each feed item includes a `summaryZh` field — an AI-generated 1-3 sentence Chinese summary for quick scanning.
- **Two coupled tools**:
  1. `amazon/policyFeed` — paginated **list**; returns structured records with title, AI summary, original URL, and publish time.
  2. `amazon/policyFeedDetail` — full article **body** (Markdown) for a single record `id` obtained from the list.
- **Time range**: Defaults to the last 7 days; supports custom time windows via `publishedAtGte` / `publishedAtLte`.

## Parameters

### List (`amazon/policyFeed`)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| site | string | No | Marketplace code (uppercase); site filtering only applies to some feed item types, others are always returned regardless of site | US |
| publishedAtGte | string | No | Publish/change time lower bound (incl.), `yyyy-MM-dd HH:mm:ss` | last 7 days |
| publishedAtLte | string | No | Publish/change time upper bound (incl.), `yyyy-MM-dd HH:mm:ss` | now |
| page | integer | No | Page number, starting at 1 | 1 |
| pageSize | integer | No | Items per page, 1-100 | 20 |

### Detail (`amazon/policyFeedDetail`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Record ID (32-char string) from the list response `data[].id` |

### Supported Marketplaces (for `site`)

US, JP, UK, AU, BE, BR, CA, EG, FR, DE, IN, IT, MX, NL, PL, SA, SG, ES, SE, TR, AE, ZA, IE. Default is **US** when not specified. Note: `site` filtering only applies to some feed item types; others are always returned regardless of site.

## API Usage

See `references/api.md` for calling conventions, request parameters, response structure, and error codes. Run scripts directly:

```bash
python scripts/amazon_policy_feed.py '{"site": "US", "pageSize": 20}'
python scripts/amazon_policy_feed_detail.py '{"id": "<id from list>"}'
```

## How to Build Queries

1. **Set the time window**: convert user's time reference into `publishedAtGte` / `publishedAtLte`. Leave empty for the default last 7 days.
2. **Pick the marketplace**: map user's target country to the `site` code (default US). Note this only filters some feed item types.
3. **Paginate**: increase `page` to scan deeper; max 100 items per page.
4. **Drill into a record**: take a record's `id` from the list and call the detail script to read the full body.

### Usage Examples

**1. Recent feed (last 7 days, US)**
```json
{"site": "US", "pageSize": 20}
```
**2. Custom date range**
```json
{"site": "US", "publishedAtGte": "2026-05-01 00:00:00", "publishedAtLte": "2026-05-31 23:59:59"}
```
**3. Japan site feed, page 2**
```json
{"site": "JP", "page": 2, "pageSize": 50}
```
**4. Full body of one record**
```json
{"id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}
```

## Display Rules

1. **List view**: present results as a table with title, AI summary (`summaryZh`), publish time, and original URL link.
2. **Detail view**: render the `stdout` Markdown as-is; the response also includes `title` and `summaryZh` for context.
3. **Only present data**: report what the feed says; do not add subjective business advice or speculate on future policy.
4. **Timeliness note**: data may lag the live page by a short period; the Amazon original is authoritative.
5. **Error handling**: on a failed call, explain the reason from the error response (e.g. invalid `id` -> re-fetch from the list) instead of guessing.

## Important Limitations

- **Default window is 7 days**: without explicit time params, only the last 7 days are returned.
- **Max 100 items per page**: `pageSize` range is 1-100.
- **Detail needs a valid list `id`**: `amazon/policyFeedDetail` only accepts an `id` returned by `amazon/policyFeed`; unknown ids return an error.
- **Not for aggregation**: this skill's output is long-form text and metadata — **not** suited for second-pass statistical/aggregation analysis via `_dataQuery_executeDynamicQuery`.

## User Expression & Scenario Quick Reference

**Applicable** — Amazon official policy & regulation feed:

| User Says | Scenario |
|-----------|----------|
| "最近亚马逊有什么政策变化" | Recent policy feed overview |
| "亚马逊美国站近一周的政策新闻" | Site-filtered policy news |
| "亚马逊最近有什么政策法规更新" | General policy/regulation updates |
| "亚马逊 FBA 最新政策法规" | Topic-specific policy lookup |
| "查看这条政策资讯的全文" | Fetch full article body by id |
| "Amazon latest policy updates" | English trigger |

**Not applicable** — beyond policy & regulation feed:
- Product / keyword / sales analytics, listing optimization, review analysis
- Real-time storefront search results or product detail
- Account-specific notifications inside an individual seller account
- Historical patent or trademark searches

**Boundary judgment**: if the user wants Amazon's **officially published policy, regulation, or compliance updates for sellers** (and its full text), this skill applies. If they want product/keyword/sales data, use the corresponding data skills.

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
python scripts/response_io.py run --script scripts/amazon_policy_feed.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `amazon_policy_feed.py`, `amazon_policy_feed_detail.py`. Pass `--script scripts/<name>.py` to choose the one you need.

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
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
