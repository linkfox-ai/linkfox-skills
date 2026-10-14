---
name: linkfox-amazon-reviews-list
description: 按ASIN获取并分析亚马逊商品评论，支持15个站点(含美国站)，按星级筛选评论。当用户提到亚马逊评论、美国站评论、商品评价、买家投诉、差评、好评、星级评分、评论分析、评论情感、产品改良建议、Vine评论、已验证购买评论、竞品评论研究、Amazon reviews, US reviews, Amazon.com reviews, product feedback, negative review analysis, positive review analysis, star rating filter, review sentiment analysis, product improvement insights, Vine reviews, competitor reviews, customer feedback时触发此技能。即使用户未明确说"评论"，只要其需求涉及读取、筛选或分析亚马逊商品的买家评论，也应触发此技能。
---

# Amazon Product Reviews

Fetch and analyze Amazon product reviews to help sellers extract actionable insights from customer feedback.

## Core Concepts

This tool retrieves real customer reviews for a given Amazon ASIN across **15 marketplaces**. You can control how many reviews to fetch per star rating (1-5 stars, up to 100 each), sort by recency or helpfulness, and apply various filters. Only one ASIN per request; for multiple ASINs, make separate calls.

## 调用方式

- **异步提交端点**：`POST /amazon/reviews/async/submit`
- **轮询查询端点**：`POST /amazon/reviews/async/result`
- **完整参数、响应和错误码**：见 `references/api.md`
- **Python 脚本**：`python scripts/amazon_reviews.py '<JSON 参数>' [--inline]`；每次只提交或查询一次并立即返回
- **成本约束**：本工具会消耗算力；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

### 异步调用流程

1. 首次执行脚本只调用 `/amazon/reviews/async/submit`，保存并立即返回 `taskId`，不得在同一次脚本调用内等待结果。不要因任务仍在运行或单次查询失败而重新提交。
2. 提交参数与原评论参数一致，不传 `provider`；后端根据 `domainCode` 自动选择 Pango 或 Apify，实际供应商可从响应的 `provider` 查看。
3. Agent 可继续执行用户请求中的其他独立工作；需要结果时，使用原参数再次执行脚本，或传入 `{"taskId":"..."}`。每次执行只调用一次 `/amazon/reviews/async/result` 并立即返回，不在脚本内部循环或休眠。
4. 根据当前实测经验，Pango 通常约 `10~30` 秒、Apify 通常约 `15~60` 秒返回，这不是 SLA。脚本会返回 `estimatedReadyInSeconds` 和 `suggestedNextCheckAfterSeconds`；优先继续其他工作，到建议时间再查询，不要按接口的最小轮询间隔忙轮询。
5. 从任务创建时间起最多观察 `200` 秒。窗口内若为 `PENDING` 或 `RUNNING`，保留原 `taskId`，继续其他工作，约 `10~20` 秒后再查询；`SUCCEEDED`：读取 `result`；`FAILED`：向用户说明 `error` 并停止；`CANCELLED`：友好说明当前评论服务可能请求较多、任务在等待执行资源时已自动取消且未产生费用，建议稍后重新提交。
6. 超过 `200` 秒仍为 `PENDING` 或 `RUNNING` 时返回 `POLL_TIMEOUT` 并停止自动查询，让用户选择：继续查询同一个 `taskId`，或停止查询并放弃本次结果。不得自动提交新任务。当前没有手动取消端点；后端只会自动取消等待执行资源超时且尚未调用供应商的 `PENDING` 任务，已进入 `RUNNING` 的任务仍可能完成并产生费用。
7. 未读取任务从提交起最多保留 `4` 小时；首次读取到 `SUCCEEDED`、`FAILED` 或 `CANCELLED` 终态后，后端立即删除任务。脚本将成功结果保存到本地文件，任务缓存只保留“已领取”和文件路径。原参数与 `taskId` 在同一工作目录内共用任务记录；24h 本地缓存有效期内再次执行会返回 `ALREADY_RECEIVED`、`resultFile` 和本次 `costToken: 0`，应读取该文件，不再查后端或重新提交。文件不存在时也不得自动重新抓取。
8. 查询返回“任务不存在或已过期”时停止，不得自动创建新的付费任务。只有用户明确要求重试时才能重新提交。
9. 任务费用由后端在上游处理结束后独立结算，与是否查询或领取结果无关。提交和查询响应的 `X-Cost-Token`/`costToken` 为 `0` 只表示该次接口不再扣费，不代表整个任务免费；实际消耗以消费记录为准，不得由 Agent 按预计公式推算或补记。

脚本只执行上述异步流程，并在本地缓存未完成的 `taskId` 以便后续查询。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-reviews-list-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## Parameter Guide

| Parameter | Type | Required | Scope | Description | Default |
|-----------|------|----------|-------|-------------|---------|
| taskId | string | Yes | Async result | Task ID returned by async submit | - |
| asin | string | Yes | Async submit | Amazon product ASIN | - |
| star1Num | integer | No | Async submit | 1-star reviews to fetch (0-100) | 10 |
| star2Num | integer | No | Async submit | 2-star reviews to fetch (0-100) | 10 |
| star3Num | integer | No | Async submit | 3-star reviews to fetch (0-100) | 10 |
| star4Num | integer | No | Async submit | 4-star reviews to fetch (0-100) | 10 |
| star5Num | integer | No | Async submit | 5-star reviews to fetch (0-100) | 10 |
| sortBy | string | No | All | `recent` (newest) or `helpful` (most helpful) | `recent` |
| formatType | string | No | All | `all_formats` or `current_format` | `all_formats` |
| domainCode | string | No | Async submit | Marketplace code (see Supported Marketplaces); use `com` for US | `com` |
| filterByKeyword | string | No | Async submit | Filter reviews by keyword (max 1000 chars) | - |
| reviewerType | string | No | Async submit | `all_reviews` or `avp_only_reviews` (verified only) | `all_reviews` |
| mediaType | string | No | Async submit | `all_contents` or `media_reviews_only` | `all_contents` |

### Star Count Defaults

- If no star count fields are provided, `star1Num` to `star5Num` all default to `10`.
- If any star count field is provided, unspecified star counts default to `0`.

## Supported Marketplaces

| Marketplace | Code |
|-------------|------|
| United States | `com` |
| Canada | `ca` |
| United Kingdom | `co.uk` |
| Germany | `de` |
| France | `fr` |
| Italy | `it` |
| Spain | `es` |
| Japan | `co.jp` |
| India | `in` |
| Australia | `com.au` |
| Brazil | `com.br` |
| Mexico | `com.mx` |
| Netherlands | `nl` |
| Sweden | `se` |
| United Arab Emirates | `ae` |

Use `domainCode` for every supported marketplace. Always confirm the user's intended marketplace.

## Usage Examples

**1. Fetch US reviews (Amazon.com)**
```json
{"asin": "B08N5WRWNW", "domainCode": "com", "star1Num": 10, "star2Num": 10, "star3Num": 10, "star4Num": 10, "star5Num": 10, "sortBy": "recent"}
```

**2. Fetch negative reviews with keyword filter (Germany)**
```json
{"asin": "B08N5WRWNW", "domainCode": "de", "star1Num": 30, "star2Num": 30, "filterByKeyword": "quality", "reviewerType": "avp_only_reviews"}
```

**3. Fetch 5-star reviews with media (Japan)**
```json
{"asin": "B08N5WRWNW", "domainCode": "co.jp", "star5Num": 50, "star1Num": 0, "star2Num": 0, "star3Num": 0, "star4Num": 0, "sortBy": "helpful", "mediaType": "media_reviews_only"}
```

**4. Fetch only 3-star reviews (explicit star mode)**
```json
{"asin": "B0FP5C63HZ", "domainCode": "com", "star3Num": 100}
```

## Display Rules

1. **Present data clearly**: Show reviews grouped by star rating with key fields: rating, title, text, date, verified status, helpful count.
2. **Summarize when appropriate**: For many reviews, provide a theme/pain-point summary before listing individuals.
3. **Highlight actionable insights**: Call out recurring complaints in negative reviews; note praised features in positive reviews.
4. **Vine and verified labels**: Clearly indicate Vine Voice and verified purchase status.
5. **Media indicators**: Note when reviews include images or videos.
6. **Response normalization**: Normalize rating and helpful-count fields for consistent display when the raw response uses marketplace-specific text formats.
7. **Review origin**: Use each review's `reviewCountry` to describe where that review was posted; `domainCode` identifies the queried marketplace, not every review's origin. Country names may be localized (`Canada` and `Canadá` both mean Canada); treat them as the same country in analysis. If `reviewCountry` is missing, mark the origin unknown rather than inferring it from `domainCode` or `locale.country`.
8. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting parameters.
9. **Single ASIN limitation**: If the user asks about multiple ASINs, make separate requests for each.

## Important Limitations

- **One ASIN per request**: Only a single ASIN can be queried at a time.
- **Per-star cap**: Each star rating returns max 100 reviews per request.
- **Parameter scope**: `filterByKeyword`, `reviewerType`, `mediaType` are available on async submit, including `domainCode: "com"`.
- **No historical snapshots**: Reviews are fetched in real-time.
- **Review text language**: Reviews are returned in their original language as posted.

## User Expression & Scenario Quick Reference

**Applicable** — Tasks involving Amazon product reviews:

| User Says | Scenario |
|-----------|----------|
| "Show me the reviews for this ASIN" | Direct review lookup |
| "Get US reviews for B08N5WRWNW" | Marketplace-specific lookup |
| "What are customers complaining about" | Negative review analysis |
| "Get me all the 1-star reviews" | Star-filtered retrieval |
| "Any common issues in the bad reviews" | Pain point mining |
| "What do people like about this product" | Positive review analysis |
| "Find reviews mentioning 'battery'" | Keyword-filtered reviews |
| "Show me reviews with photos" | Media-filtered reviews |
| "Verified purchase reviews only" | Reviewer-type filtering |
| "Help me analyze competitor reviews" | Competitor review research |
| "Product improvement suggestions from reviews" | Actionable insight extraction |

**Not applicable** — Needs beyond product review data:

- ABA search term data / keyword research (use ABA Data Explorer instead)
- Sales estimation or revenue analysis
- Listing copywriting or A+ content creation
- Advertising / PPC strategy
- Pricing strategy or profit margin calculations

**Boundary judgment**: If "product research" or "competitor analysis" boils down to reading customer reviews for specific ASINs, this skill applies. If it involves search volume, keyword rankings, sales estimates, or market sizing, it does not.

## 算力消耗规则

按计划抓取页数动态计费。设 `P = Σ min(ceil(各星级请求评论数 / 10), 10)`，则：

- 计费 Token：`21000 × P`。
- **实际消耗算力 = `ceil((21000 × P) / 2000) = ceil(10.5 × P)`**，按每次请求分别向上取整。
- 未传任何星级数量时，1~5 星默认各抓取 10 条，`P = 5`，消耗 `53` 算力。
- 传入任意星级数量后，未传星级按 `0`；五个星级均显式传 `0` 时，`P = 0`，不调用供应商且消耗 `0` 算力。
- 请求成功但结果为空，或经关键词、认证购买、媒体筛选后为空，仍按计划页数计费；部分子任务失败但整体成功时仍按全部计划页数计费；上游调用完全失败不计费。

常见消耗：1 页 `11` 算力，2 页 `21` 算力，5 页 `53` 算力，10 页 `105` 算力。

> **重要**：费用按请求的抓取页数计算，而不是按最终返回评论数计算。请求多个星级或大量评论前必须向用户说明预计页数和算力消耗。

> 上述公式只用于调用前预估，实际是否扣费及金额以消费记录为准。费用由后端独立结算，领取结果不重复扣费；未领取、查询失败或本地观察超时不代表任务免费，不得据此报告零消耗或按预估值计为已消耗。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in the references. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
