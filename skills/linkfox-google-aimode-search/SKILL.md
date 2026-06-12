---
name: linkfox-google-aimode-search
description: 基于 Google 搜索的 AI 概览（AI Overview / AI Mode）抓取，针对一个关键词返回主搜索的 AI 概览要点，适合用最新网页信息做深度调研、技术问答、长尾选品分析、海外消费者偏好分析。仅支持单轮对话，如需追问须由 agent 总结上下文后发起新请求。当用户提到 Google AI、AI Overview、AI Mode、谷歌AI概览、谷歌AI搜索、海外深度调研、长尾选品调研、消费者偏好分析、网页要点总结、Google AI search, AI Overview, AI Mode, deep research, consumer preference analysis 等场景时触发此技能。即使用户未明确提到"Google AI"，只要其需求是"用谷歌搜索 + AI 总结网页要点"，也应触发此技能。
---

# Google AI Search

This skill calls Google Search in AI Mode to get the AI Overview answer for a single keyword. Only one question per call is supported — there is no multi-turn follow-up within a single request. The response is unstructured Markdown — summarize it directly, do not route it to a data-analysis sandbox.

## Core Concepts

The tool drives Google's AI Mode (the panel that appears at the top of Google search results and synthesizes an answer with citations):

1. The required `keyword` is sent to Google as the query and the AI Overview for it is captured.
2. **Single-round only**: each call handles exactly one question. There is no `prompts` parameter for follow-ups.
3. **For follow-up questions**: the agent must summarize the previous AI Overview answer (key points, citations, relevant context) and concatenate it with the new question into a new `keyword`, then make a fresh API call.
4. All answers are returned as a single Markdown document under `stdout`, with citations linked to the source pages.

`resultsNum` reports how many AI Overview blocks were rendered; `0` means the keyword did not trigger an AI Overview on Google for the requested locale.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Google search keyword. Sent as the `q=` parameter to Google AI Mode. For follow-up questions, the agent should summarize the previous answer and concatenate with the new question into this field. |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| stdout | string | Markdown document with the AI Overview for the keyword, plus inline citation links |
| sourceUrl | string | The Google AI Mode search URL that was actually requested |
| resultsNum | integer | Number of AI Overview blocks rendered (0 = keyword did not trigger AI Overview) |
| code / errcode | string / integer | `200` on success; non-200 indicates a business error |
| msg / errmsg | string | `ok` on success; otherwise an error description |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Tokens consumed (only billed on success) |
| taskId | string | Upstream task identifier for tracing |
| type | string | Render hint, fixed value `stdoutWorkbenches` |

## API Usage

This tool is exposed via the LinkFox tool gateway. See `references/api.md` for the calling convention, request/response shape, error codes, and a curl example. You can also run `scripts/google_ai_search.py` directly to test it from the command line.

## How to Build Queries

Each call takes a single `keyword`. For follow-up questions, the agent must summarize the previous result and build a new query.

### Tips

1. **Front-load context in `keyword`**: include market/region cues when relevant (`"open-ear bone-conduction headphones US 2026"`) — the AI Overview is sensitive to phrasing.
2. **Match the language to the target market**: ask in English for US/UK/AU markets, Japanese for JP, German for DE, etc. — the AI Overview is biased toward the locale's language.
3. **Use natural-language questions**: phrasing like "compare against" / "what are the unsolved pain points" elicits richer AI Overview output than single keywords.
4. **For follow-ups, summarize and re-ask**: when the user wants to dig deeper, the agent should summarize key points from the previous AI Overview response and concatenate with the new question into a new `keyword` for a fresh call. Example: `"Based on the AI overview that top bone-conduction headphones are Shokz OpenRun Pro and AfterShokz Aeropex, what are the unsolved technical pain points compared to in-ear earbuds?"`

### Usage Examples

**1. Single-shot AI Overview**

```json
{
  "keyword": "GaN charger vs traditional charger comparison"
}
```

**2. Cross-border product research**
```json
{
  "keyword": "best open-ear bone conduction headphones 2026 US"
}
```

**3. Follow-up question (agent summarizes prior result and re-asks in a new call)**

First call:
```json
{
  "keyword": "best open-ear bone conduction headphones 2026 US"
}
```

Second call (agent builds context summary + new question):
```json
{
  "keyword": "The AI overview mentioned OpenRun Pro and AfterShokz Aeropex as top picks for bone conduction headphones. What unsolved technical pain points still exist compared to in-ear earbuds?"
}
```

**4. Consumer preference snapshot**
```json
{
  "keyword": "robot vacuum buying preferences 2026 reddit"
}
```

**5. Long-tail keyword exploration for selection**
```json
{
  "keyword": "smart pet feeder for cats with camera"
}
```

## Display Rules

1. **Render the Markdown directly**: `stdout` is already structured Markdown with headings, bullets, and citation links — preserve that structure when answering the user.
2. **Cite sources**: keep the inline reference links from `stdout` so the user can verify each claim.
3. **Flag empty AI Overview**: if `resultsNum` is `0`, tell the user Google AI Overview did not trigger for that keyword and suggest rephrasing or trying a different region.
4. **Don't reroute to a data-analysis sandbox**: the output is unstructured text and not suitable for SQL-like processing.
5. **Indicate freshness**: results reflect Google AI Mode at call time; mention this when the user asks about recency.
6. **Handle business errors**: if `code` / `errcode` is not `200`, surface the `msg` / `errmsg` to the user and suggest retrying or refining the input.

## Important Limitations

- **Unstructured output**: Markdown text only — no structured tables, no second-pass data query.
- **AI Overview not guaranteed**: some keywords (especially niche, ambiguous, or sensitive ones) do not trigger AI Overview at all (`resultsNum = 0`).
- **Single-round only**: no multi-turn follow-up within one call. For follow-ups, the agent must summarize previous context and make a new call.
- **Locale follows Google's defaults**: the tool uses Google's standard AI Mode endpoint without an explicit region switch; bias the language and wording of `keyword` to match the market you care about.
- **Real-time fetch**: results are pulled live, so output for the same keyword can vary across calls.

## User Expression & Scenario Quick Reference

**Applicable** — when the user wants AI-summarized live web information:

| User Says | Scenario |
|-----------|----------|
| "用 Google AI 帮我搜...", "Google AI Overview 看下..." | Direct AI Overview lookup |
| "海外消费者对 XX 怎么看", "美国市场对 XX 的偏好" | Cross-border consumer preference |
| "XX 的最新趋势 / 痛点 / 使用场景" | Deep research |
| "顺便问一下 / 然后再追问 ..." | Follow-up needed (agent summarizes prior result and re-asks in new call) |
| "网页上对 XX 的总结", "搜索引擎里大家怎么说 XX" | Web-wide summarization |
| "长尾选品调研 / 蓝海选品方向" | Long-tail product exploration |

**Not applicable** — better routed elsewhere:

- Querying internal structured datasets (use the appropriate data query tool).
- Amazon ABA search-term analytics (use the ABA data explorer).
- Pulling structured product listings, prices, reviews from a specific platform (use the matching platform skill).
- Plain web search where the user only needs raw page content with no AI synthesis (use the standard web search skill).
- Image generation, image recognition, or file analysis.

**Boundary judgment**: when the user wants "AI 帮我汇总网上的说法" or "用谷歌搜一下", this skill applies. If the user wants to ask follow-up questions, the agent should summarize the previous answer and make a new call. If they explicitly want raw search results, structured data, or already have a specialized data source, do not use this skill.

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
python scripts/response_io.py run --script scripts/google_ai_search.py --out-dir <DIR> '<params>'
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

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
