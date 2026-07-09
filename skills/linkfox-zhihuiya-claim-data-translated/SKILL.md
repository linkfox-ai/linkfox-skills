---
name: linkfox-zhihuiya-claim-data-translated
description: 从智慧芽专利数据库获取翻译后的专利权利要求。当用户询问专利权利要求、权利要求翻译、查看特定语言（中文、英文或日文）的权利要求、通过专利ID或公开号查询专利权利、分析权利要求文本、claim translation, patent claim translation, PatSnap, patent translation时触发此技能。即使用户未明确提及"翻译版权利要求"，只要其需求涉及获取特定语言的专利权利要求内容，也应触发此技能。
---

# Zhihuiya Patent Claims (Translated)

This skill guides you on how to query translated patent claims from the Zhihuiya (PatSnap) patent database, enabling users to retrieve claim texts in Chinese, English, or Japanese for one or more patents.

## Core Concepts

Patent claims define the legal scope of protection granted by a patent. This tool retrieves the **translated text** of patent claims, supporting three languages: Chinese (`cn`), English (`en`), and Japanese (`jp`). You can look up patents by their internal patent ID or by their publication (announcement) number.

**Family patent substitution**: When claims are unavailable for a specific patent, the tool can optionally substitute claims from a related family patent. This is controlled by the `replaceByRelated` parameter.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Patent ID | patentId | Internal patent identifier | 84a1b2c3-... |
| Publication Number | pn | Publication (announcement) number of the patent | CN112345678A |
| Related Publication Number | pnRelated | Publication number of the substitute family patent (only present when family substitution is used) | US20210012345A1 |
| Claims | claims | Translated patent claim text | 1. A method for... |

## Supported Languages

| Code | Language |
|------|----------|
| en | English (default) |
| cn | Chinese |
| jp | Japanese |

Default language is **en** (English). Use English when the user does not specify a language.

## 调用方式

- **API 端点**：`POST /zhihuiya/claimDataTranslated`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_claim_translated.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-claim-data-translated-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## Parameter Guide

### Patent Identification

You must provide **at least one** of the following:

- **patentId** -- The internal patent ID. When both `patentId` and `patentNumber` are provided, `patentId` takes precedence. Multiple values separated by commas, up to 100 patents per request.
- **patentNumber** -- The publication or announcement number. Multiple values separated by commas, up to 100 patents per request.

### Optional Parameters

- **lang** -- Target translation language: `en` (English, default), `cn` (Chinese), or `jp` (Japanese).
- **replaceByRelated** -- Whether to substitute claims from a family patent when the original claims are unavailable: `1` = yes, `0` = no (default).

## Usage Examples

**1. Get English claims for a single patent by publication number**
```
patentNumber: "CN112345678A"
lang: "en"
```

**2. Get Chinese claims for multiple patents by publication number**
```
patentNumber: "US20210012345A1,EP3456789B1"
lang: "cn"
```

**3. Get Japanese claims with family patent fallback**
```
patentNumber: "JP2021123456A"
lang: "jp"
replaceByRelated: 1
```

**4. Query by patent ID**
```
patentId: "84a1b2c3-d4e5-6f78-9abc-def012345678"
lang: "en"
```

## Display Rules

1. **Present claims clearly**: Show the translated claim text with proper formatting. If multiple patents are returned, separate each patent's claims with its publication number as a heading.
2. **Family substitution notice**: When `pnRelated` is present in the response, clearly inform the user that the claims were sourced from a related family patent and show the substitute publication number.
3. **Language notice**: State the language of the returned claims so the user knows which translation they are viewing.
4. **Large results**: When multiple patents are returned, summarize the count and show a few representative entries, reminding the user of the total.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest checking the patent ID or publication number.
## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; otherwise the query will fail.
- **Batch limit**: A maximum of 100 patents per request.
- **Language support**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **Family substitution**: Substitute claims are only returned when `replaceByRelated` is set to `1` and the original claims are unavailable.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries related to patent claim text and translation:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims for patent XX" | Single patent claim lookup |
| "Translate claims to Chinese/Japanese" | Claim translation |
| "What does patent XX claim?" | Claim content retrieval |
| "Get claims for these patents: XX, YY" | Batch patent claim lookup |
| "Claims unavailable, try family patent" | Family patent substitution |
| "Patent rights scope of XX" | Claim text retrieval |

**Not applicable** -- Needs beyond patent claim translation:

- Patent search or discovery (finding patents by keyword)
- Patent citation or legal status analysis
- Patent abstract or description retrieval
- Patent portfolio analytics or statistics


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
