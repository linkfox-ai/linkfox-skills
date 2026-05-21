---
name: linkfox-google-aimodel-search
version: 1.0.0
category: product-sourcing
description: 基于 Google 搜索的 AI 概览（AI Overview / AI Mode）抓取与多轮追问，针对一个关键词同时返回主搜索的 AI 概览要点和多个追问问题的答案，适合用最新网页信息做深度调研、技术问答、长尾选品分析、海外消费者偏好分析。当用户提到 Google AI、AI Overview、AI Mode、谷歌AI概览、谷歌AI搜索、海外深度调研、长尾选品调研、消费者偏好分析、网页要点总结、Google AI search, AI Overview, AI Mode, deep research, consumer preference analysis 等场景时触发此技能。即使用户未明确提到"Google AI"，只要其需求是"用谷歌搜索 + AI 总结网页要点 + 多轮追问"，也应触发此技能。
---

# Google AI Search

This skill calls Google Search in AI Mode to get the AI Overview answer for a keyword and follow up with up to several additional questions in a single round trip. The response is unstructured Markdown — summarize it directly, do not route it to a data-analysis sandbox.

## Core Concepts

The tool drives Google's AI Mode (the panel that appears at the top of Google search results and synthesizes an answer with citations) and stitches multi-turn follow-ups into one call:

1. The required `keyword` is sent to Google as the initial query and the AI Overview for it is captured first.
2. Each entry in the optional `prompts` array is asked as a follow-up question in the same AI conversation, in order.
3. All answers are concatenated into a single Markdown document under `stdout`, with each section clearly labelled and citations linked to the source pages.

`resultsNum` reports how many AI Overview blocks were rendered; `0` means the keyword did not trigger an AI Overview on Google for the requested locale.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Initial Google search keyword (≤ 1000 chars). Sent as the `q=` parameter to Google AI Mode. |
| prompts | string[] | No | Follow-up questions for additional turns of the same AI conversation. Recommended ≤ 5 entries; more is allowed but response time degrades sharply. Omit this field for a single-shot AI Overview lookup with no follow-ups. |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| stdout | string | Markdown document with the AI Overview for the keyword and each follow-up answer in order, plus inline citation links |
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

The two inputs work together: `keyword` is the entry point, `prompts` are the follow-ups. Treat them as one continuous AI conversation, not as independent searches.

### Tips

1. **Front-load context in `keyword`**: include market/region cues when relevant (`"open-ear bone-conduction headphones US 2026"`) — the AI Overview is sensitive to phrasing.
2. **Keep `prompts` focused and ordered**: each follow-up reuses the previous turn's context, so cheaper questions go first (e.g. "what are the main use cases?" before "what are the unsolved technical pain points?").
3. **Limit follow-ups to 3–5**: more turns dramatically increase latency without proportional value.
4. **Match the language to the target market**: ask in English for US/UK/AU markets, Japanese for JP, German for DE, etc. — the AI Overview is biased toward the locale's language.
5. **Use natural-language questions in `prompts`**: phrasing like "compare against" / "what are the unsolved pain points" elicits richer AI Overview output than single keywords.

### Usage Examples

**1. Single-shot AI Overview (no follow-ups — `prompts` omitted)**

Pass `keyword` only when the user just wants the AI Overview for one query, with no multi-turn follow-up. `prompts` is optional and can be left out entirely:

```json
{
  "keyword": "GaN charger vs traditional charger comparison"
}
```

**2. Cross-border product research with follow-ups**
```json
{
  "keyword": "best open-ear bone conduction headphones 2026 US",
  "prompts": [
    "What are the main use cases consumers care about?",
    "What unsolved technical pain points still exist compared to in-ear earbuds?"
  ]
}
```

**3. Consumer preference snapshot**
```json
{
  "keyword": "robot vacuum buying preferences 2026 reddit",
  "prompts": [
    "Which features get praised most in user reviews?",
    "Which complaints come up repeatedly?"
  ]
}
```

**4. Long-tail keyword exploration for selection**
```json
{
  "keyword": "smart pet feeder for cats with camera",
  "prompts": [
    "What price ranges are mentioned most often?",
    "Which brands appear in the top picks?"
  ]
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
- **Latency scales with `prompts` length**: each follow-up is an additional AI turn on Google; 5+ prompts can take tens of seconds.
- **Locale follows Google's defaults**: the tool uses Google's standard AI Mode endpoint without an explicit region switch; bias the language and wording of `keyword` to match the market you care about.
- **Real-time fetch**: results are pulled live, so output for the same keyword can vary across calls.

## User Expression & Scenario Quick Reference

**Applicable** — when the user wants AI-summarized live web information with multi-turn depth:

| User Says | Scenario |
|-----------|----------|
| "用 Google AI 帮我搜...", "Google AI Overview 看下..." | Direct AI Overview lookup |
| "海外消费者对 XX 怎么看", "美国市场对 XX 的偏好" | Cross-border consumer preference |
| "XX 的最新趋势 / 痛点 / 使用场景" | Deep research with follow-ups |
| "顺便问一下 / 然后再追问 ..." | Multi-turn follow-up needed |
| "网页上对 XX 的总结", "搜索引擎里大家怎么说 XX" | Web-wide summarization |
| "长尾选品调研 / 蓝海选品方向" | Long-tail product exploration |

**Not applicable** — better routed elsewhere:

- Querying internal structured datasets (use the appropriate data query tool).
- Amazon ABA search-term analytics (use the ABA data explorer).
- Pulling structured product listings, prices, reviews from a specific platform (use the matching platform skill).
- Plain web search where the user only needs raw page content with no AI synthesis (use the standard web search skill).
- Image generation, image recognition, or file analysis.

**Boundary judgment**: when the user wants "AI 帮我汇总网上的说法" or "用谷歌搜并追问几轮", this skill applies. If they explicitly want raw search results, structured data, or already have a specialized data source, do not use this skill.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
