---
name: linkfox-ai-mode-google-search
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

## 调用方式

- **API 端点**：`POST /aiMode/googleSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/google_ai_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ai-mode-google-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

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

## 积分消耗规则

按动态规则计费：消耗积分 = 对话轮次 × 4.2。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
