---
name: linkfox-sif-compliance-detection
description: SIF-外观专利检测，当前提供商品图片外观相似检索，返回相似外观登记候选，支持辅助标题、地区、来源归属、洛迦诺分类和法律状态筛选。用于以图查外观登记和产品外观风险候选排查；结果仅供候选审查，不作侵权判定。
---

# SIF Design Patent Detection

SIF design patent detection currently provides design-similarity search from a product image. Present the source's matching evidence and coverage for candidate review; do not issue an infringement verdict.

## Core Concepts

- Supply exactly one image source: `imageUrl` or `imageBase64`. A title supplements the image and cannot replace it. Image and title searches use separate modalities; their raw scores must not be added.
- `topK` defaults to 20 and accepts 1–200. Candidate count does not determine the user's price.
- `regions` uses ISO-2 identifiers such as CN/US/EM; the upstream source uses EU where this input uses EM. `jurisdictionCodes` uses source identifiers such as USID/EMID. When both filters are supplied, their intersection applies.
- `topLoc` filters two-digit Locarno prefixes; `locarnoClasses` filters full NN-NN codes. Missing classification remains unknown; do not remove such candidates yourself.
- `patentStatus` is an optional integer array: `[0]`, `[1]` or `[0,1]`. Omission adds no status preference. Preserve returned unknown/pending status and coverage; do not infer whether those rows were included or excluded, or refilter them locally.
- Current upstream coverage includes an independent CN scope. Determine usable coverage and loading gaps from returned `coverage` and `warnings`; do not assume every jurisdiction has equal coverage or hardcode dataset counts.
- The backend handles upstream signing and credentials. The skill sends only business parameters and a LinkFox gateway Key.

## Data Fields

Check both the gateway `errcode` (200 on success) and upstream `data.code` (`OK` on success). Candidates are at `data.data.candidates`, with source coverage and warnings alongside them. Candidate fields may be missing or null; omission and null both mean an unknown source fact. The full envelope, optional processing metadata and field types are documented in [references/api.md](references/api.md).

| Candidate fields | Use |
|---|---|
| `design_registration_id`, `primary_identifier`, `application_number`, `registration_number`, `publication_number` | Source identifiers for follow-up review |
| `registration_jurisdiction_code`, `jurisdiction_iso2`, `locarno_classes` | Source jurisdiction and classification; do not interchange the two jurisdiction fields |
| `title`, `title_en`, `title_language`, `title_en_source` | Returned title, language and English-title provenance; do not invent translations |
| `holder_names`, `designer_names` | Source holder and designer information |
| `image_score`, `text_score`, `similarity`, `matched_modality` | Separate raw modality scores and the source's 0–100 similarity conversion; similarity is not a probability |
| `simple_legal_status`, `registration_date`, `application_date`, `publication_date` | Source status and YYYY-MM-DD dates, when returned |
| `image_available` | Image availability hint; it does not supply an image URL |

Also preserve `risk_level` and `risk_reasons` when returned. These existing source rule hints remain compatible with this skill; they do not constitute an infringement finding.

Read [references/api.md](references/api.md) for the request limits, envelope, failures and feedback contract.

## Parameter Guide

| Parameter | Required | Default | Meaning |
|---|---|---|---|
| `imageUrl` | One image source | — | Public HTTP(S) image URL |
| `imageBase64` | One image source | — | Raw Base64 of image bytes, without a data URL prefix; do not also pass imageUrl |
| `title` | No | — | Optional image context, up to 4096 characters |
| `topK` | No | 20 | Integer 1–200 |
| `regions` | No | — | Up to 64 unique two-letter ISO-2 identifiers, e.g. `["CN","US","EM"]` |
| `jurisdictionCodes` | No | — | Source identifiers, e.g. `["USID","EMID"]`; intersects regions when both are supplied |
| `topLoc` | No | — | Up to 32 unique two-digit Locarno prefixes, e.g. `["09","22"]` |
| `locarnoClasses` | No | — | Locarno codes, e.g. `["22-06"]` |
| `patentStatus` | No | — | Gateway array only: `[0]` (inactive), `[1]` (active), or `[0,1]`; no default preference |

For a local image, encode its bytes into `imageBase64` in a UTF-8 JSON file. This supported input avoids an upload dependency. The script does not transform image formats.

## 调用方式

- **API 端点**：`POST /ecDw/designSimilarSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/ec_dw_design_similar_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具每次新检索消耗 5 积分，经网关统一计费；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换图片、筛选条件或候选数连续试探；需要继续检索时先向用户说明可能产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-compliance-detection-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需抽取，避免整份 JSON 进入上下文。

Large image payloads use `python scripts/ec_dw_design_similar_search.py --params-file <UTF-8 JSON file> [--inline]`. UTF-8 BOM is accepted. `--no-cache` deliberately refreshes a result and can incur another charge; it does not enable retries.

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## Workflow

1. Use the image provided or selected by the user. Establish only the requested region, source jurisdiction, Locarno and legal-status filters; do not silently choose a status or jurisdiction.
2. Call the script once. Require HTTP success, gateway `errcode: 200` and upstream `data.code: OK`; use the saved file for details omitted by the summary. An error response is not a candidate list.
3. Present returned candidates and identifiers with actual matching evidence, coverage, warnings and source metadata.
4. On failure or empty candidates, report the actual result and stop. A coverage failure is not a zero-match result.

## Usage Examples

For a local bottle image and an explicitly requested US/EM search, prepare a request from the actual image bytes. Replace `./product.png` with the user's local image path:

```bash
python -c 'import base64,json,sys; from pathlib import Path; params={"imageBase64":base64.b64encode(Path(sys.argv[1]).read_bytes()).decode("ascii"),"title":"Bottle","regions":["US","EM"],"topK":20}; Path("request.json").write_text(json.dumps(params,ensure_ascii=False),encoding="utf-8")' ./product.png
python scripts/ec_dw_design_similar_search.py --params-file request.json
```

Adapt the title and filters to the user's product and request. An image URL can instead be supplied in `imageUrl`; use a real reachable image, and omit `imageBase64`. Optional array filters retain leading zeros, for example `"topLoc":["09"],"locarnoClasses":["09-01"],"patentStatus":[0,1]`.

To view the full response, repeat the same request with `--inline`; within 24h a successful cached result produces `Cache hit` and sends no new request.

## Display Rules

1. Preserve the returned candidate order and identifiers. Show titles, holder names, classifications, dates and status only when present; missing information remains unknown.
2. Attribute scores, modality, risk labels and risk reasons to the source. `similarity` is already on a 0–100 scale; do not multiply it again, call it a probability, or add image/text scores. Matching evidence and a source rule label are not a legal conclusion.
3. Preserve coverage/warning information. Source `coverage_ratio` may exceed 1; it is not a guaranteed patent-coverage percentage. Do not turn unavailable coverage or a service error into “no matching designs”.
4. Display a candidate image only when an actual usable image URL is returned. `image_available` alone is insufficient; never construct a URL.

## Important Limitations

- An empty result does not establish freedom to operate. A separate legal investigation requires a separate user request.
- Use only the nine documented request fields. Do not add `query_mode` or other fields that this gateway does not accept.
- Calls never automatically retry, follow redirects, change images/filters or split into exploratory requests.
- Success cache is isolated by gateway, endpoint, API Key fingerprint and parameters; HTTP/business failures are not cached. A cache hit sends no request and displays fees from the original response, not a new charge.
- The registered price is 5 credits per new search; billing is handled by the gateway. Display actual returned fees, and do not infer the user's charge from server cost, upstream usage or missing fee fields.
- Upstream `data.usage` describes the provider account, including its quota and credits; never present it as the user's LinkFox balance. Internal engine, collection and timing fields are troubleshooting metadata.

## User Expression & Scenario Quick Reference

**Applicable**: “用 SIF-外观专利检测查外观相似候选”, “找这个产品的外观登记候选”, “按 USID 和洛迦诺分类筛相似外观”.

**Not applicable**: issuing an infringement verdict, patent full-text retrieval, trademark/TRO checks, or seller-account operations.

**Boundary judgment**: Use this skill for image-based design-registration candidate retrieval through the data warehouse. If the user asks for a verdict, explain that the returned candidates and source hints support further review only.

## 算力消耗规则

每次新检索消耗 5 积分（￥0.05/次），由网关统一计费。缓存命中不发起新请求，不产生新的调用费用；缓存中的费用字段来自原始响应。实际扣费展示以网关费用响应为准；后端成本、上游积分或空费用字段不作为用户扣费金额或免费依据。继续真实检索前说明可能的额外消耗。

## Feedback

Feedback can cover:

1. Described functionality does not match actual behavior.
2. Results do not match the user's intent.
3. The user expresses dissatisfaction or praise.
4. A concrete improvement is identified.

Follow the Feedback API in `references/api.md` when user authorization or the task permits feedback. Send only a redacted issue summary; exclude credentials, images/Base64 and raw response rows.

---
*For more cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
