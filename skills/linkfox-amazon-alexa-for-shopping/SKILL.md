---
name: linkfox-amazon-alexa-for-shopping
description: 通过亚马逊前台的 Alexa 购物助手发起自然语言问答，获取与问题相关的导购回答、推荐商品分组、ASIN 列表，以及可继续追问的问题。支持在同一次调用中传入多条 prompts 模拟连续多轮对话，并可用 url 补充亚马逊页面上下文。当用户提到亚马逊 Alexa、Alexa 购物助手、亚马逊智能助手、AI 导购、对话式选品、自然语言购物、亚马逊聊天问答、Amazon Alexa shopping, conversational shopping, AI shopping assistant, follow-up questions、产品推荐对话、上下文追问等场景时触发此技能。即使用户未明确提及"Alexa"，只要其需求是"在亚马逊前台用自然语言问出商品推荐 + 多轮追问"，也应触发此技能。
---

# Amazon Alexa Shopping Assistant

This skill drives Amazon's storefront Alexa shopping assistant: pose a natural-language question and get an answer, a curated product list (with ASINs and links), and a set of follow-up questions Alexa is willing to continue with. Multiple prompts in a single call simulate a continuous multi-turn conversation, not independent searches.

## Core Concepts

1. **Single conversation, ordered turns**: `prompts` is an array — element 0 is the opening question, element 1 the first follow-up, element 2 the next follow-up, and so on. The tool sends them sequentially in one Alexa session and concatenates Alexa's answers in order.
2. **Cross-call context is not preserved**: when a new tool call starts, it begins a brand-new Alexa session. To keep continuity across calls, summarize the previous answer + recommended ASINs yourself and embed them in the next `prompts[0]`.
3. **Optional page context (`url`)**: pass an Amazon page URL only when you want the conversation anchored to a **specific** page (a category page, search results page, or product detail page). Do **not** pass a plain marketplace homepage URL like `https://www.amazon.com/` — it adds no useful context. Omit `url` entirely when there is no specific page to anchor on.
4. **Two output formats**:
   - `markdown` (default) — a single readable Markdown report containing the question, Alexa's answer, recommended product groups, and follow-up questions.
   - `json` — a structured array under `data`, where each entry carries `prompt`, `content`, `products` (grouped recommendations), `followUpQuestions`, and `screenshot`.

`resultsNum` is the number of conversation turns Alexa actually answered; if `0`, Alexa did not produce a usable reply for the input.

## Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| prompts | string[] | Yes | Conversation prompts. Each element is one turn in the same session, sent in order. Recommended ≤ 5 entries. | - |
| format | string | No | Response format: `markdown` returns a readable report; `json` returns a structured array. | markdown |
| url | string | No | Specific Amazon page URL (category, search results, or product detail) to anchor the conversation. Skip when there is no specific page; do **not** pass a plain homepage URL such as `https://www.amazon.com/`. | - |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| stdout | string | Markdown report when `format=markdown`: per-turn question, Alexa answer, recommended product groups, follow-up questions |
| data | array | Structured turns when `format=json`. Each item has `prompt`, `content`, `products[]`, `followUpQuestions[]`, `screenshot` |
| resultsNum | integer | Number of answered turns (0 = Alexa did not respond) |
| code / errcode | string / integer | `200` on success; non-200 indicates a business error |
| msg / errmsg | string | `ok` on success; otherwise an error description |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Tokens consumed (only billed on success) |
| taskId | string | Upstream task identifier for tracing |
| type | string | Render hint: `stdoutWorkbenches` for markdown, `json` for json |

### Structured `data[*]` shape (`format=json`)

| Field | Type | Description |
|-------|------|-------------|
| prompt | string | The question or follow-up sent for this turn |
| content | string | Alexa's natural-language answer |
| products[].title | string | Group title (e.g. "Top picks", "Best for running") |
| products[].items[].asin | string | Product ASIN |
| products[].items[].title | string | Product title |
| products[].items[].url | string | Product detail page URL |
| products[].items[].cover | string | Product cover image URL |
| products[].items[].price | string | Current price string (with currency) |
| products[].items[].originalPrice | string | List price / strikethrough price |
| products[].items[].score | string | Star rating |
| products[].items[].ratingsCount | string | Review count |
| products[].items[].describe | string | Short product blurb |
| followUpQuestions | string[] | Questions Alexa offers to continue with |
| screenshot | string | Screenshot URL for this turn |

## API Usage

This skill calls the LinkFox tool gateway. See `references/api.md` for the calling convention, request/response shape, error codes, and a curl example. You can also run `scripts/amazon_alexa_search.py` directly to test it from the command line.

## How to Build Queries

1. **Front-load the user's intent in `prompts[0]`** — include marketplace cue ("on Amazon US"), use case, and any hard constraints (budget, key feature). Alexa weights the opening turn heavily.
2. **Order follow-ups by dependency** — each turn reuses the prior turn's context. Put broad framing first, then ask Alexa to compare, narrow, or recommend specific picks.
3. **Keep `prompts` short** — 1 to 5 turns is the sweet spot. Longer arrays inflate latency without proportional gain.
4. **Anchor with `url` only when there's a specific page** — pass a category, search results, or product detail URL when the user is reasoning over that page. Skip `url` for general questions; do not pass a plain homepage like `https://www.amazon.com/`.
5. **For continuity across tool calls**: write a one-paragraph summary of the previous answer (key recommendations + ASINs) and prepend it to the new `prompts[0]`. Don't assume Alexa remembers the prior call.
6. **Pick `format` deliberately** — `markdown` is best for showing the user a polished answer; `json` is better when downstream code needs to extract ASINs, prices, or follow-up questions programmatically.

### Usage Examples

**1. Single-turn shopping question**

```json
{
  "prompts": ["best wireless earbuds for running on Amazon US under $100"]
}
```

**2. Multi-turn conversation (compare + narrow)**

```json
{
  "prompts": [
    "best electric kettle on Amazon US",
    "compare the top two recommendations on noise level and boil time",
    "which one is better if I only boil water once a day"
  ]
}
```

**3. Conversation anchored to a category page**

```json
{
  "prompts": [
    "What are the most popular picks on this page?",
    "Which of them have the best reviews for small kitchens?"
  ],
  "url": "https://www.amazon.com/s?k=electric+kettle"
}
```

**4. Structured output for downstream extraction**

```json
{
  "prompts": ["best gift ideas for a 10-year-old who likes science"],
  "format": "json"
}
```

## Display Rules

1. **Render the Markdown directly** when `format=markdown`: `stdout` is already structured with turn headings, product cards, and follow-up questions — preserve that structure.
2. **Surface the recommended ASINs** so the user can click through; show `title`, `price`, `score`/`ratingsCount`, and the product URL.
3. **Show the follow-up questions** Alexa returned — they are usable prompts the user can pick to continue digging.
4. **Don't reroute to a data-analysis sandbox**: the answer body is conversational and the recommended products are nested groups, not a flat tabular dataset suitable for SQL-like aggregation.
5. **Flag empty results**: if `resultsNum` is `0` or `data` is empty, tell the user Alexa did not produce a usable reply and suggest rephrasing or anchoring with a `url`.
6. **Indicate freshness**: results reflect Alexa's live answer at call time; mention this when the user asks about timing.
7. **Handle business errors**: if `code` / `errcode` is not `200`, surface `msg` / `errmsg` and suggest retrying with simpler prompts.

## Important Limitations

- **Alexa-driven, not deterministic**: same prompts can yield different answers across calls — Alexa's response varies with time, traffic, and context.
- **No cross-call memory**: each tool call is a fresh Alexa session; the agent must recap prior context manually.
- **Recommended ≤ 5 prompts per call**: longer arrays sharply increase latency.
- **Marketplace coverage**: anchored on Amazon's storefront Alexa experience (primarily amazon.com); availability on non-US marketplaces depends on Alexa rollout.
- **Output mix**: primary value is the conversational answer plus a curated handful of products; this is not a substitute for SERP-wide product extraction.

## User Expression & Scenario Quick Reference

**Applicable** — natural-language conversational shopping on Amazon:

| User Says | Scenario |
|-----------|----------|
| "用 Alexa 帮我推荐...", "亚马逊 Alexa 问下..." | Direct Alexa Q&A |
| "在亚马逊上聊聊给我推荐 ...", "对话式选品" | Conversational discovery |
| "顺便再追问一下 / 接着问 ..." | Multi-turn follow-up |
| "在这个页面 / 这个分类下推荐...", "基于这个页面再问一下" | Page-anchored conversation (use `url`) |
| "best XX for YY under $Z on Amazon" | Goal + constraint + budget Q&A |
| "对比 Alexa 给的前两个推荐" | Compare within Alexa's reply |
| "Alexa 还能继续问什么 / 给我一些追问思路" | Surface follow-up questions |

**Not applicable** — better routed elsewhere:

- Pulling the full SERP for a keyword with positions, sponsored flags, etc. (use the storefront search-simulation skill).
- Historical search-term analytics or volume trends (use the ABA data explorer).
- Detailed product detail / A+ / bullets for a known ASIN (use the Amazon product detail skill).
- Review-level sentiment analysis (use the Amazon reviews skill).
- Image-based similar product discovery (use the image search skill).
- Aggregated statistics over a flat product list (no structured table here).

**Boundary judgment**: when the user wants a **conversation** — "ask Amazon, get a recommendation, then keep asking" — this skill applies. If they want raw search-result rows, structured analytics, or a specific ASIN's data, route to the matching specialized skill instead.

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
