---
name: linkfox-sorftime-tiktok-seller-data
description: 通过 Sorftime 查询 TikTok Shop 品牌，支持按产品ID或标题关键词找关联品牌、按品牌名称模糊搜索、按卖家店铺ID查在售品牌。用户需要 Sorftime TikTok 品牌检索、卖家经营品牌或产品关联品牌时使用；覆盖美国、马来西亚、菲律宾、越南、泰国、印度尼西亚、英国和日本站。
---

# Sorftime TikTok Seller Data

Query one page of TikTok Shop brands through Sorftime. Use the query mode matching the user's intent; product details, creators, videos, orders and trademark ownership are outside this skill.

## Core Concepts and Parameters

| Intent | queryType | name |
|---|---:|---|
| Find brands related to a product | 1 | Product ID or product-title keyword; Chinese is supported |
| Find brands by name | 2 | Brand name, fuzzy matching |
| Find brands sold by a seller | 3 | Seller/shop ID |

- Keep product and shop IDs as strings. A numeric string alone does not identify whether the user means a product or a seller.
- Markets: `us`, `my`, `ph`, `vn`, `th`, `id`, `uk`, `jp`; `gb` aliases `uk`. Default to the US only when no marketplace is supplied.
- `pageIndex` defaults to 1, must be a positive 32-bit integer, and returns at most 100 brands per page.
- Read [references/api.md](references/api.md) before calling for exact parameters, response fields and billing rules.

## 调用方式

- **API 端点**：`POST /sorftime/tk/brandSearchFromName`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sorftime_tk.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗算力；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改站点连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：

- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-tiktok-seller-data-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务聚合；禁止回退写入用户目录或 `/tmp`，当前目录不可写则在收费查询前报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、实际费用、最大列表长度及前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要；需要具体字段时，优先用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需抽取。

The script reads `LINKFOX_AGENT_API_KEY`, falling back to `LINKFOXAGENT_API_KEY`. `LINKFOX_TOOL_GATEWAY` overrides the default `https://tool-gateway.linkfox.com`.

Identical normalized requests use a 24-hour cache isolated by gateway, endpoint, API identity and parameters. A repeated call prints `Cache hit`; `--inline` keeps the cache. Use `--no-cache` only when a fresh paid request is covered by the user's authorization.

## Usage Example

```bash
python scripts/sorftime_tk.py '{"queryType":2,"name":"medicube","marketplace":"us","pageIndex":1}'
```

This input returned a populated production response on 2026-10-21. Availability can change; do not substitute another query or page automatically after an empty result.

## Display Rules

1. State the marketplace, query mode, page and returned `requestConsumed`, `costToken` and `costCredit`. Cache hits incur no new request; cached costs describe the original live call.
2. Read brand data from `data.value`; preserve unknown fields and the original array/object/null shape. Do not invent brand IDs or missing attributes.
3. `ProductCount`, `MonthlySaleCount`, `MonthlySaleAmount` and `SellerCount` cover products/sellers entering subcategory Top300. Label this scope rather than total platform-wide brand sales.
4. `MaxCategory`, `SecondCategory` and `ThirdCategory` may be objects or JSON-formatted strings. Decode only string values for presentation and preserve raw saved values.
5. `Photo` may contain multiple addresses joined by `>`, including empty segments. Preserve the raw string and display individual nonempty addresses.
6. The amount currency/unit is not specified for this endpoint. Do not apply Amazon/Walmart cents conversion or label all markets USD without evidence.
7. Check framework `errcode` first, then business `code`. `upstreamCode=11` is normal no-data; report actual consumption, because some successful empty responses still cost Request.

## Important Limitations

- Each call covers one query and page. Additional pages, changed queries and provider switches are separate paid actions; do not retry or paginate automatically.
- Results depend on the vendor's collected dataset. Missing data does not establish zero sales, absence of a brand or trademark ownership.
- Preserve the eight-market boundary and the user's chosen query mode. Do not silently convert a seller ID into a product lookup.

## 解决认证和算力问题

Read [references/onboarding.md](references/onboarding.md) for missing keys, authorization errors or LinkFox billing problems. Sorftime supplier quota/access errors belong to the service operator; users do not need to provide a Sorftime key or buy a Sorftime account.

## User Expression & Scenario Quick Reference

**Applicable**: “用Sorftime查美国站medicube品牌”、“查这个卖家经营哪些品牌”、“找这个产品关联的品牌”。

**Not applicable**: product details, influencer/video analytics, orders, account authorization or trademark-rights verification.

**Boundary judgment**: Choose this skill when the requested output is a set of brands identified by a product, brand name or seller. Clarify ambiguous numeric IDs before a paid call.

## 算力消耗规则

按动态规则计费：单个 Sorftime Request 当前显示为 6 算力；多 Request 操作由网关按整单计算并取整，最终以入口脚本返回的 `costCredit` 为准，不要简单用 `requestConsumed × 6` 代替实际账单。

> 用户会因算力消耗而支付费用。不要未经确认补调新的查询条件、站点或下一页。

**Feedback:** When the user requests or authorizes feedback about a behavior/result mismatch or an improvement, use the Feedback API in `references/api.md`. Exclude API keys, supplier credentials and unrelated conversation content.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
