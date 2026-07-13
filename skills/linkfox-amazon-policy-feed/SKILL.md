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

## 调用方式

- **API 端点**：
  - `POST /amazon/policyFeed`（`amazon_policy_feed.py`，完整参数/响应/错误码见 `references/api.md`）
  - `POST /amazon/policyFeedDetail`（`amazon_policy_feed_detail.py`，完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-policy-feed-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## 积分消耗规则

消耗 15 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
