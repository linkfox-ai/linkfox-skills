---
name: linkfox-sif-compliance-detection
description: SIF-外观专利检测，支持按商品图片查找相似外观登记候选，以及按登记 ID 或主号码查询登记详情、权利人、设计人、法律状态、日期与分类。检索支持地区、来源归属、洛迦诺分类和法律状态筛选；用于产品外观候选审查，不作侵权判定。
---

# SIF Design Patent Detection

Find similar design registrations from a product image, or inspect registration details by ID or primary identifier. Both operations belong to this SIF skill. Present the source's evidence and coverage for review; do not issue an infringement verdict.

## Endpoints

| User goal | POST endpoint | Entry script | Cost per new call |
|---|---|---|---|
| Find similar designs from a product image | `/ecDw/designSimilarSearch` | `ec_dw_design_similar_search.py` | 5 算力 |
| Inspect known registration IDs or a primary number | `/ecDw/designProfile` | `ec_dw_design_profile.py` | 2 算力 |

Call only the operation needed for the user's request. A known ID or primary number goes directly to details without an image search. When the user requests search followed by details, reuse IDs from that search; one search plus one detail batch costs 7 credits. Keep both operations in this single skill, with one direct script per endpoint.

## Core Concepts

- For image search, supply exactly one image source: `imageUrl` or `imageBase64`. A title supplements the image and cannot replace it. Image and title searches use separate modalities; their raw scores must not be added. Detail lookup needs no image.
- `topK` defaults to 20 and accepts 1–200. Candidate count does not determine the user's price.
- `regions` uses ISO-2 identifiers such as CN/US/EM; the upstream source uses EU where this input uses EM. `jurisdictionCodes` uses source identifiers such as USID/EMID. When both filters are supplied, their intersection applies.
- `topLoc` filters two-digit Locarno prefixes; `locarnoClasses` filters full NN-NN codes. Missing classification remains unknown; do not remove such candidates yourself.
- `patentStatus` is an optional integer array: `[0]`, `[1]` or `[0,1]`. Omission adds no status preference. Preserve returned unknown/pending status and coverage; do not infer whether those rows were included or excluded, or refilter them locally.
- Current upstream coverage includes an independent CN scope. Determine usable coverage and loading gaps from returned `coverage` and `warnings`; do not assume every jurisdiction has equal coverage or hardcode dataset counts.
- The backend handles upstream signing and credentials. The skill sends only business parameters and a LinkFox gateway Key.
- Detail lookup accepts 1–200 unique registration IDs, or one primary identifier with an optional ISO-2 jurisdiction. Use IDs supplied by the user or returned by search; never construct an ID from a number. Do not automatically fetch details for every search candidate.

## Data Fields

Check both the gateway `errcode` (200 on success) and upstream `data.code` (`OK` on success). HTTP 200 alone is insufficient. Use the response path for the chosen endpoint:

| Operation | Result path | Context |
|---|---|---|
| Image search | `data.data.candidates[]` | `data.data.coverage` and `data.data.warnings` |
| Registration details | `data.data.items[]` | `data.data.returned`, with each item's source status, dates and coverage |

Business fields may be missing or null; both mean an unknown source fact. The full envelope, optional processing metadata and field types are documented in [references/api.md](references/api.md).

Registration details are at `data.data.items`; `data.data.returned` is the returned row count. Show actual identifiers, holders/designers, dates, status, classification and coverage. Preserve `as_of_date` and `data_version` when available; the confirmation date is not necessarily today. Details do not create new similarity scores or image URLs.

| Candidate fields | Use |
|---|---|
| `design_registration_id`, `primary_identifier`, `application_number`, `registration_number`, `publication_number` | Source identifiers for follow-up review |
| `registration_jurisdiction_code`, `jurisdiction_iso2`, `locarno_classes` | Source jurisdiction and classification; do not interchange the two jurisdiction fields |
| `title`, `title_en`, `title_language`, `title_en_source` | Returned title, language and English-title provenance; do not invent translations |
| `holder_names`, `designer_names` | Source holder and designer information |
| `image_score`, `text_score`, `similarity`, `matched_modality` | Separate raw modality scores and the source's 0–100 similarity conversion; similarity is not a probability |
| `simple_legal_status`, `registration_date`, `application_date`, `publication_date` | Source status and YYYY-MM-DD dates, when returned |
| `image_available` | Image availability hint; it does not supply an image URL |
| `image_url` | Candidate-image URL; use the returned value unchanged |

Also preserve `risk_level` and `risk_reasons` when returned. These existing source rule hints remain compatible with this skill; they do not constitute an infringement finding.

Read [references/api.md](references/api.md) for the request limits, envelope, failures and feedback contract.

## Parameter Guide

### Image search

| Parameter | Required | Default | Meaning |
|---|---|---|---|
| `imageUrl` | One image source | — | Public HTTP(S) image URL |
| `imageBase64` | One image source | — | Raw Base64, 16–20,971,520 characters (20 MiB text, approximately 15 MiB original image); no data URL prefix or imageUrl |
| `title` | No | — | Optional image context, up to 4096 characters |
| `topK` | No | 20 | Integer 1–200 |
| `regions` | No | — | Up to 64 unique two-letter ISO-2 identifiers, e.g. `["CN","US","EM"]` |
| `jurisdictionCodes` | No | — | Source identifiers, e.g. `["USID","EMID"]`; intersects regions when both are supplied |
| `topLoc` | No | — | Up to 32 unique two-digit Locarno prefixes, e.g. `["09","22"]` |
| `locarnoClasses` | No | — | Locarno codes, e.g. `["22-06"]` |
| `patentStatus` | No | — | Gateway array only: `[0]` (inactive), `[1]` (active), or `[0,1]`; no default preference |

For a local image, encode its bytes into `imageBase64` in a UTF-8 JSON file. This supported input avoids an upload dependency. The script does not transform image formats.

### Registration details

| Parameter | Required | Meaning |
|---|---|---|
| `designRegistrationIds` | One identifier mode | Array of 1–200 unique strings, each 1–128 characters; reuse exact user-provided or search-returned IDs |
| `primaryIdentifier` | One identifier mode | One exact primary number as a string, 1–128 characters; preserve leading zeros |
| `jurisdictionIso2` | No | Two letters such as US/EM; accepted only with `primaryIdentifier` to narrow ambiguous numbers |

The two identifier modes are mutually exclusive. Values must be strings without leading/trailing whitespace; do not mix search fields into detail requests. Details are exact lookups, and one batch is one paid call. Read the [detail contract](references/api.md#外观登记详情) for the full field dictionary.

## 调用方式

- **API 端点**：检索 `POST /ecDw/designSimilarSearch`；详情 `POST /ecDw/designProfile`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：检索 `python scripts/ec_dw_design_similar_search.py '<JSON 参数>' [--inline]`；详情 `python scripts/ec_dw_design_profile.py '<JSON 参数>' [--inline]`
- **成本约束**：按上表端点分别收费，详情 1–200 个登记 ID 按一次收费；相同端点和参数默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换参数连续试探；需要继续调用时先说明可能产生额外消耗，不自动逐条查详情或拆分批次。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-compliance-detection-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需抽取，避免整份 JSON 进入上下文。

Large image payloads use `python scripts/ec_dw_design_similar_search.py --params-file <UTF-8 JSON file> [--inline]`. UTF-8 BOM is accepted. `--no-cache` deliberately refreshes a result and can incur another charge; it does not enable retries.

The detail script accepts the same `--params-file`, `--inline` and `--no-cache` options. Both scripts use the same skill slug; cache entries are isolated by endpoint, gateway, Key fingerprint and parameters. The 20 MiB limit applies to the Base64 field; JSON adds overhead to the whole HTTP request.

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **LinkFox 网关响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

仅处理用户网关 Key、认证和余额问题。若错误明确来自上游服务凭据、授权或额度，按 `references/api.md` 联系服务管理员，不引导用户重复注册或充值。

## Workflow

1. Choose the requested operation. For image search, use the user's image and requested filters. For details, use the user's ID/primary identifier or a saved candidate ID; an image search is unnecessary when an identifier is already known.
2. Call the matching script once. Require HTTP success, gateway `errcode: 200` and upstream `data.code: OK`; inspect the saved file for fields omitted by the summary. An error response is not a result list.
3. If the user requested search followed by details, pass the selected candidate's `design_registration_id` unchanged to the detail script. Perform both authorized steps without asking again; account for the 5-credit search and 2-credit detail call (7 credits total). A search-only request does not require a detail call.
4. Present candidates with matching evidence, or details with source facts and coverage. Preserve all returned matches for an ambiguous primary number. On failure/empty results, report the actual outcome and stop; a coverage failure or 404 does not establish absence of a patent or risk.

## Usage Examples

For a local bottle image and an explicitly requested US/EM search, prepare a request from the actual image bytes. Replace `./product.png` with the user's local image path:

```bash
python -c 'import base64,json,sys; from pathlib import Path; params={"imageBase64":base64.b64encode(Path(sys.argv[1]).read_bytes()).decode("ascii"),"title":"Bottle","regions":["US","EM"],"topK":20}; Path("request.json").write_text(json.dumps(params,ensure_ascii=False),encoding="utf-8")' ./product.png
python scripts/ec_dw_design_similar_search.py --params-file request.json
```

Adapt the title and filters to the user's product and request. An image URL can instead be supplied in `imageUrl`; use a real reachable image, and omit `imageBase64`. Optional array filters retain leading zeros, for example `"topLoc":["09"],"locarnoClasses":["09-01"],"patentStatus":[0,1]`.

Read the already saved JSON file first when more fields are needed. `--inline` also shows the full response: if a valid success cache exists for the same gateway, endpoint, Key and parameters, it prints `Cache hit` without a new request. A missing or expired cache can cause another paid call.

For a request to inspect the following actual candidate ID, use the detail entry directly:

```bash
python scripts/ec_dw_design_profile.py '{"designRegistrationIds":["DSR:wipo_hague:EMID.001431738-0001"]}'
```

Replace the example with the ID supplied by the user or returned by their search. For a known primary number, the alternative request is `{"primaryIdentifier":"001431738","jurisdictionIso2":"EM"}`. Use one identifier mode, preserve leading zeros and do not guess a number from an image.

## Display Rules

1. Preserve the returned candidate order and identifiers. Show titles, holder names, classifications, dates and status only when present; missing information remains unknown.
2. Attribute scores, modality, risk labels and risk reasons to the source. `similarity` is already on a 0–100 scale; do not multiply it again, call it a probability, or add image/text scores. Matching evidence and a source rule label are not a legal conclusion.
3. Preserve coverage/warnings and each row's actual `jurisdiction_iso2` and source jurisdiction. Do not relabel or discard a returned row solely to match requested `regions`, or treat those filters as proof of protection territory. Source `coverage_ratio` may exceed 1; it is not a guaranteed patent-coverage percentage. Do not turn unavailable coverage or a service error into “no matching designs”.
4. Display candidate `image_url` as a Markdown image when returned; use the complete URL unchanged. Do not construct a URL from `image_available`.
5. Detail `has_readable_image` (observed as integer 1) and `image_count` indicate source media facts, not image URLs. Do not convert them into a cover or download link. Show raw status and confirmation date when relevant without inferring current legal validity.

## Important Limitations

- An empty result does not establish freedom to operate. A separate legal investigation requires a separate user request.
- Search accepts its nine documented fields; details accept only `designRegistrationIds`, `primaryIdentifier` and `jurisdictionIso2`. Do not mix the schemas or add `query_mode`.
- Calls never automatically retry, follow redirects, change images/filters or split into exploratory requests.
- Success cache is isolated by gateway, endpoint, API Key fingerprint and parameters; HTTP/business failures are not cached. A cache hit sends no request and displays fees from the original response, not a new charge.
- Detail batches accept at most 200 IDs. Do not split a larger list automatically or query every search candidate individually.
- Upstream `data.usage` describes the provider account, including its quota and credits; never present it as the user's LinkFox balance. Internal engine, collection and timing fields are troubleshooting metadata.

## User Expression & Scenario Quick Reference

**Applicable**: “用 SIF-外观专利检测查外观相似候选”, “找这个产品的外观登记候选”, “按 USID 和洛迦诺分类筛相似外观”, “查看这个候选的登记详情/权利人/法律状态”.

**Not applicable**: issuing an infringement verdict, patent full-text retrieval, trademark/TRO checks, or seller-account operations.

**Boundary judgment**: Use this skill for image-based design-registration retrieval and exact registration detail lookup. It does not provide the separate general-patent publication-number lookup. If the user asks for a verdict, explain that the returned facts and source hints support further review only.

## 算力消耗规则

检索每次新调用消耗 5 算力（￥0.05/次），详情每次新调用消耗 2 算力（￥0.02/次）；检索后查一次详情合计 7 算力，由网关统一计费。详情单次支持 1–200 个登记 ID，按次收费，不按条数收费。缓存命中不发起新请求，不产生新的调用费用；缓存中的费用字段来自原始响应。实际扣费展示以网关费用响应为准；后端成本、上游积分或空费用字段不作为用户扣费金额或免费依据。继续真实调用前说明可能的额外消耗。

## Feedback

Feedback can cover:

1. Described functionality does not match actual behavior.
2. Results do not match the user's intent.
3. The user expresses dissatisfaction or praise.
4. A concrete improvement is identified.

Follow the Feedback API in `references/api.md` when user authorization or the task permits feedback. Send only a redacted issue summary; exclude credentials, images/Base64 and raw response rows.

---
*For more cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
