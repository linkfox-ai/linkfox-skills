---
name: linkfox-echotik-influencer
description: 查询 EchoTik TikTok 达人批量详情与近180天历史趋势，支持按达人ID或账号获取档案，并按达人ID查看粉丝、互动及带货趋势。用户点名 EchoTik 达人详情、批量达人核验或达人历史快照时使用；不用于达人搜索、榜单、账号授权或邀约。
---

# EchoTik TikTok Influencer Profiles and Trends

Use only the endpoint needed for the current request. These are public market analytics from EchoTik's collected dataset; record the query date and preserve the reported time window.

## Endpoints

| Intent | POST endpoint | Script | Cost |
|---|---|---|---|
| 批量达人详情 | `/echotik/influencer/detail` | `echotik_influencer_detail.py` | 5 算力/次 |
| 达人历史趋势 | `/echotik/influencer/trend` | `echotik_influencer_trend.py` | 5 算力/次 |

## Core Concepts and Parameters

- Detail requires exactly one nonempty array: `userIds` (numeric IDs as strings) or `uniqueIds` (account names without `@` or URLs). Maximum 10 entries; duplicates are removed. Do not automatically split larger inputs into paid batches.
- Trend requires numeric-string `userId`, `startDate` and `endDate` (`yyyy-MM-dd`) within the most recent 180 days.
- Trend defaults: `pageNum=1`, `pageSize=10`; page number 1–100000 and page size 1–10. Each call retrieves one page only.
- A username must first resolve to `userId` through detail if a historical trend is requested. Make that extra paid call only when the user's request requires it.
- Follower/like increments may be negative. Preserve nulls, missing fields, currency units, ratios and JSON-encoded strings as returned.

## 调用方式

- **API 端点**：上表端点均为 POST；读取 [references/api.md](references/api.md) 确认字段和错误语义。
- **Python 脚本**：`python scripts/<entry>.py '<JSON 参数>' [--inline] [--no-cache]`。仅使用 Python 3.9+ 标准库。
- **认证**：`LINKFOX_AGENT_API_KEY` 优先，回退 `LINKFOXAGENT_API_KEY`；网关读取 `LINKFOX_TOOL_GATEWAY`，缺省为 `https://tool-gateway.linkfox.com`。EchoTik 供应商凭证仅在服务端管理。
- **成本约束**：本工具会消耗算力；同一会话同一参数组合默认只调用一次，脚本带24h本地缓存。一次只查询一页或最多10个达人，当前默认每次成功查询5算力，最终以网关返回的 `costCredit` 为准。失败/空结果不得自动换条件、翻页或连续试探；需要继续检索时先说明额外消耗。
- **缓存**：成功响应缓存24小时；按网关、端点、API Key 指纹和完整参数隔离。失败不缓存；`--inline` 保持缓存，`--no-cache` 会真实请求并可能再次计费，仅在用户明确要求刷新或调试时使用。缓存结果中的成本值是原始响应信息，缓存命中不会发起新请求。

**输出策略（脚本默认行为）**：

- **始终**将完整响应以UTF-8写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-influencer-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务聚合；当前目录不可写则在收费查询前报错，禁止回退至用户目录或 `/tmp`）
- 响应体 ≤ 8 KB：落盘后把完整JSON打印到stdout
- 响应体 > 8 KB：落盘后只输出摘要，包含实际 `costToken` / `costCredit`、最大列表长度及前3条样本
- `--inline` 强制全量输出，同样落盘；二次同参命中缓存时显示 `Cache hit`

**读数据建议**：先看摘要，需要具体字段时用 `jq` 或 `ConvertFrom-Json` 从保存的JSON按需抽取。

## 解决认证和算力问题

Read [references/onboarding.md](references/onboarding.md) when the Key is missing or the gateway reports an authorization or balance error. A supplier error alone is not a reason to register, purchase, or retry.

## Usage Examples

```bash
python scripts/echotik_influencer_detail.py '{"uniqueIds":["jeffreestar"]}'
python scripts/echotik_influencer_trend.py '{"userId":"6787875411281134598","startDate":"2026-10-14","endDate":"2026-10-20","pageNum":1,"pageSize":1}'
```
These inputs returned nonempty production responses on 2026-10-21; detail resolved `jeffreestar` to the displayed numeric ID. For a new task, choose the user's requested dates within the last 180 days and reuse a known `userId`; query detail only when resolution is needed and authorized. Do not run both examples by default or infer that availability remains unchanged.

## Display Rules

- Present `data` and `total` as the current response records; `total` is not the total number of matches or total history days. Show actual `costToken` and `costCredit`; mark cache costs as historical.
- Include the supplied account or numeric user ID and requested time window; show the returned region when available. Full response fields are documented in [references/api.md](references/api.md).
- Separate observed data from analysis; label estimates, dates and metric units as returned.
- Check the response body as well as HTTP status. A gateway `errcode` other than 200 is a failure even with HTTP 200. Business failures exit with status 2 after saving the response.

## Important Limitations

- Source data may be delayed or uncollected; an empty result does not mean zero sales or zero followers.
- Query one batch of at most 10 profiles or one trend page at a time; do not automatically split larger inputs into paid batches.
- Do not automatically retry, switch providers, paginate, contact creators or operate a TikTok account.

## User Expression & Scenario Quick Reference

**Applicable**: “用EchoTik批量查这些达人”、“核验这个达人账号”、“看这个达人最近的粉丝和带货趋势”。

**Not applicable**: creator search/rankings, related products/videos/live streams, real-time account data, authorization, invitations or outreach.

**Boundary judgment**: Use this skill for profiles of supplied creator IDs/accounts or a known creator's historical metrics. Generic creator discovery and rankings remain with their existing provider-specific skills; do not turn a profile check into a search or outreach workflow.

## 算力消耗规则

每次成功查询预计消耗 5 算力，最终以入口脚本返回的 `costCredit` 为准。缓存命中不产生新消耗，缓存中的费用字段表示原请求费用；空结果和失败响应不返回正常计费成本。

> 用户会因算力消耗而支付费用。多端点、多页或多批次查询前说明预计调用次数与额外消耗，由用户决定是否继续。

**Feedback:** Submit feedback only when the user explicitly requests or authorizes it. Follow the Feedback section in `references/api.md`, sanitize the contents, and exclude API keys, credentials and unrelated conversation context.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
