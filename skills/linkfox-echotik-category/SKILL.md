---
name: linkfox-echotik-category
description: 查询 EchoTik TikTok 商品一至三级类目字典、一级类目大盘详情与类目历史趋势。用户需要 EchoTik 类目ID、父子分类、类目销量及GMV趋势时使用；不处理商品搜索、店铺运营或达人档案。
---

# EchoTik TikTok Category Intelligence

Use only the endpoint needed for the current request. These are public market analytics from EchoTik's collected dataset; record the query date and preserve the reported time window.

## Endpoints

| Intent | POST endpoint | Script | Cost |
|---|---|---|---|
| 一级商品类目 | `/echotik/category/l1` | `echotik_category_l1.py` | 5 算力/次 |
| 二级商品类目 | `/echotik/category/l2` | `echotik_category_l2.py` | 5 算力/次 |
| 三级商品类目 | `/echotik/category/l3` | `echotik_category_l3.py` | 5 算力/次 |
| 一级类目大盘详情 | `/echotik/category/detail` | `echotik_category_detail.py` | 5 算力/次 |
| 类目历史趋势 | `/echotik/category/trend` | `echotik_category_trend.py` | 5 算力/次 |

## Core Concepts and Parameters

- Dictionary calls require `language`: `th-TH`, `en-US`, `id-ID`, `zh-CN`, `ms-MY`, or `vi-VN`.
- Level 2/3 accept optional `parentId`; pass the Level 1/2 ID respectively. Omission adds no parent filter.
- Category detail requires a **Level 1** `categoryId` and uppercase `region`. The source updates T+1.
- Trends require a two-letter uppercase `region`, `startDate` and `endDate` (`yyyy-MM-dd`); category IDs are optional. `pageNum` defaults to 1 (range 1–100000), and `pageSize` defaults to 10 (range 1–10).
- These new v3 endpoints do not synchronize or update the existing local category table.

## 调用方式

- **API 端点**：上表端点均为 POST；读取 [references/api.md](references/api.md) 确认字段和错误语义。
- **Python 脚本**：`python scripts/<entry>.py '<JSON 参数>' [--inline] [--no-cache]`。仅使用 Python 3.9+ 标准库。
- **认证**：`LINKFOX_AGENT_API_KEY` 优先，回退 `LINKFOXAGENT_API_KEY`；网关读取 `LINKFOX_TOOL_GATEWAY`，缺省为 `https://tool-gateway.linkfox.com`。EchoTik 供应商凭证仅在服务端管理。
- **成本约束**：本工具会消耗算力；同一会话同一参数组合默认只调用一次，脚本带24h本地缓存。一次只查询一个端点的一页，当前默认每次成功查询5算力，最终以网关返回的 `costCredit` 为准。失败/空结果不得自动换条件、翻页或连续试探；需要继续检索时先说明额外消耗。
- **缓存**：成功响应缓存24小时；按网关、端点、API Key 指纹和完整参数隔离。失败不缓存；`--inline` 保持缓存，`--no-cache` 会真实请求并可能再次计费，仅在用户明确要求刷新或调试时使用。缓存结果中的成本值是原始响应信息，缓存命中不会发起新请求。

**输出策略（脚本默认行为）**：

- **始终**将完整响应以UTF-8写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-category-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务聚合；当前目录不可写则在收费查询前报错，禁止回退至用户目录或 `/tmp`）
- 响应体 ≤ 8 KB：落盘后把完整JSON打印到stdout
- 响应体 > 8 KB：落盘后只输出摘要，包含实际 `costToken` / `costCredit`、最大列表长度及前3条样本
- `--inline` 强制全量输出，同样落盘；二次同参命中缓存时显示 `Cache hit`

**读数据建议**：先看摘要，需要具体字段时用 `jq` 或 `ConvertFrom-Json` 从保存的JSON按需抽取。

## 解决认证和算力问题

Read [references/onboarding.md](references/onboarding.md) when the Key is missing or the gateway reports an authorization or balance error. A supplier error alone is not a reason to register, purchase, or retry.

## Usage Examples

```bash
python scripts/echotik_category_l1.py '{"language":"zh-CN"}'
python scripts/echotik_category_l2.py '{"language":"zh-CN","parentId":"600001"}'
python scripts/echotik_category_l3.py '{"language":"zh-CN","parentId":"851848"}'
python scripts/echotik_category_detail.py '{"categoryId":"600001","region":"US"}'
python scripts/echotik_category_trend.py '{"categoryId":"600001","region":"US","startDate":"2026-10-14","endDate":"2026-10-20","pageNum":1,"pageSize":1}'
```

These example inputs returned nonempty production responses on 2026-10-21. For another parent category or date window, use the user's requested values; do not run every example as a workflow.

## Display Rules

- Present `data` and `total` as the current response records; `total` is not the total number of matches or total history days. Show actual `costToken` and `costCredit`; mark cache costs as historical.
- Include the category ID/level, region and time window when applicable. Full response fields are documented in [references/api.md](references/api.md).
- Separate observed data from analysis; label estimates, dates and metric units as returned.
- Check the response body as well as HTTP status. A gateway `errcode` other than 200 is a failure even with HTTP 200. Business failures exit with status 2 after saving the response.

## Important Limitations

- Source data may be delayed or uncollected; an empty result does not mean zero sales.
- Category detail accepts a Level 1 ID only; dictionary language and marketplace region are different parameters.
- Query one endpoint and page at a time. Do not automatically retry, switch providers, paginate or synchronize categories.

## User Expression & Scenario Quick Reference

**Applicable**: “EchoTik有哪些商品分类”、“查这个一级类目的市场规模”、“看这个细分类目的销量趋势”。

**Not applicable**: creator profiles, shop account operations, category synchronization, product-level trends or non-EchoTik providers.

**Boundary judgment**: Use this skill for category IDs, parent-child dictionaries, category market details or category trends. Product and seller discovery remain with their existing skills; select only the endpoint needed for the user's request.

## 算力消耗规则

每次成功查询预计消耗 5 算力，最终以入口脚本返回的 `costCredit` 为准。缓存命中不产生新消耗，缓存中的费用字段表示原请求费用；空结果和失败响应不返回正常计费成本。

> 用户会因算力消耗而支付费用。多端点或多页查询前说明预计调用次数与额外消耗，由用户决定是否继续。

**Feedback:** Submit feedback only when the user explicitly requests or authorizes it. Follow the Feedback section in `references/api.md`, sanitize the contents, and exclude API keys, credentials and unrelated conversation context.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
