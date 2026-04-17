---
name: linkfox-eureka-claim-translated
description: 通过Eureka专利数据平台获取翻译后的专利权利要求。当用户询问专利权利要求、权利要求翻译、查看特定语言（中文、英文或日文）的权利要求、通过专利ID或公开号查询专利权利、分析权利要求文本、Eureka权利要求、claim translation, patent claim translation, Eureka patent, patent translation时触发此技能。即使用户未明确提及"翻译版权利要求"，只要其需求涉及获取特定语言的专利权利要求内容，也应触发此技能。
---

# Eureka Patent Claim Translation

This skill guides you on how to query translated patent claims from the Eureka patent data platform, enabling users to retrieve claim texts in Chinese, English, or Japanese for one or more patents.

## Core Concepts

Patent claims define the legal scope of protection granted by a patent. This tool retrieves the **translated text** of patent claims from the Eureka platform, supporting three languages: Chinese (`cn`), English (`en`), and Japanese (`jp`). You can look up patents by their internal patent ID or by their publication (announcement) number.

**Family patent substitution**: When claims are unavailable for a specific patent, the tool can optionally substitute claims from a related family patent. This is controlled by the `replaceByRelated` parameter.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | At least one of patentId or patentNumber | Internal patent ID. Separate multiple IDs with commas. Up to 100 patents per request. |
| patentNumber | string | At least one of patentId or patentNumber | Publication (announcement) number. Separate multiple numbers with commas. Up to 100 patents per request. |
| replaceByRelated | integer | No | Whether to substitute claims from a family patent when unavailable. `1` = yes, `0` = no. Default `0`. |
| lang | string | No | Target translation language. `en` = English (default), `cn` = Chinese, `jp` = Japanese. |

### Key Rules

1. **At least one identifier is required**: You must provide either `patentId` or `patentNumber` (or both). If both are supplied, `patentId` takes priority.
2. **Batch queries**: Multiple patents can be queried at once by separating values with commas, up to 100 per request.
3. **Default language is English**: When the user does not specify a language, use `en`.
4. **Family fallback**: Set `replaceByRelated` to `1` only when the user explicitly wants substitute claims from a family patent if the original is missing.

## Response Fields

| Field | Description |
|-------|-------------|
| total | Number of patent records returned |
| data | Array of patent objects (see below) |
| data[].patentId | Internal patent ID |
| data[].pn | Publication (announcement) number |
| data[].claims | Translated patent claims text |
| data[].pnRelated | Publication number of the substitute family patent (only present when family substitution was used) |
| costToken | Tokens consumed by this request |

## Usage Examples

**1. Get English claims for a single patent by publication number**
```
Show me the English claims for patent CN112345678A.
```
Parameters: `patentNumber = "CN112345678A"`, `lang = "en"`

**2. Get Chinese claims for multiple patents**
```
Get the Chinese translation of claims for US20210012345A1 and EP3456789B1.
```
Parameters: `patentNumber = "US20210012345A1,EP3456789B1"`, `lang = "cn"`

**3. Get Japanese claims with family patent fallback**
```
Get Japanese claims for JP2021123456A. If unavailable, try a family patent.
```
Parameters: `patentNumber = "JP2021123456A"`, `lang = "jp"`, `replaceByRelated = 1`

**4. Query by patent ID**
```
Get claims for patent ID 84a1b2c3 in English.
```
Parameters: `patentId = "84a1b2c3"`, `lang = "en"`

**5. Batch query with fallback enabled**
```
Translate claims for these patents: CN112345678A, US20200012345A1, EP3456789B1. Use family patents if needed.
```
Parameters: `patentNumber = "CN112345678A,US20200012345A1,EP3456789B1"`, `lang = "en"`, `replaceByRelated = 1`

## Display Rules

1. **Present claims clearly**: Show the translated claim text with proper formatting. If multiple patents are returned, separate each patent's claims with its publication number as a heading.
2. **Family substitution notice**: When `pnRelated` is present in the response, clearly inform the user that the claims were sourced from a related family patent and show the substitute publication number.
3. **Language notice**: State the language of the returned claims so the user knows which translation they are viewing.
4. **Large results**: When multiple patents are returned, summarize the count and show a few representative entries, reminding the user of the total.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest checking the patent ID or publication number.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/eureka_claim_translated.py` directly to run queries.

## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; otherwise the query will fail.
- **Batch limit**: A maximum of 100 patents per request.
- **Language support**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **Family substitution**: Substitute claims are only returned when `replaceByRelated` is set to `1` and the original claims are unavailable.
- **No claim analysis**: This tool returns raw translated text only; it does not analyze or compare claims.

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

**Boundary** -- Edge cases:

- If the user asks for "patent text" without specifying claims, clarify whether they want claims, abstract, or description.
- If the user provides more than 100 patents, split into multiple batches.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
