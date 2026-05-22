---
name: linkfox-eureka-claim-data
description: 从Eureka专利数据库查询专利权利要求（Claims）信息。当用户提到专利权利要求、权利要求书、专利Claims、独立权利要求、从属权利要求、权利要求数量、专利保护范围、patent claims, claim data, independent claims, dependent claims, claim count, patent claim text, patent protection scope, Eureka patent claims时触发此技能。即使用户未明确提及"Eureka"或"权利要求"，只要其需求涉及获取专利的权利要求全文或权利要求数量，也应触发此技能。
---

# Eureka Patent Claim Data

This skill guides you on how to retrieve patent claim data via the Eureka patent platform, helping users quickly access the full claim text and claim count for one or more patents.

## Core Concepts

The Eureka Claim Data tool returns the complete claims section for each queried patent:

1. **Claims Array** — The full text of all claims (independent and dependent) for the patent.
2. **Claim Count** — The total number of claims in the patent.
3. **Related Patent Fallback** — When `replaceByRelated` is enabled ("1"), if the requested patent has no claims data, the system will attempt to use a related patent (e.g., the granted version of an application) to provide claim data. The `pnRelated` field indicates which related patent was used.

**Patent identification**: Patents can be looked up by either patent ID or publication number. When both are provided, patent ID takes priority. Multiple values can be submitted in a single request (comma-separated).

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| patentId | Conditionally | Patent ID. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values. |
| patentNumber | Conditionally | Publication (announcement) number. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values. |
| replaceByRelated | Optional | Whether to use a related patent as fallback when the queried patent has no claims. "1" = enable fallback, "0" = disable (default). |

- If the user provides a publication number (e.g., CN115000000A, US11000000B2), use `patentNumber`.
- If the user provides an internal patent ID, use `patentId`.
- When both are supplied, `patentId` takes precedence.
- Set `replaceByRelated` to "1" when the user wants claim data even if the exact publication has none (common for application-stage patents).

## Response Fields

| Field | Description |
|-------|-------------|
| patentId | The patent's internal ID |
| pn | Publication (announcement) number |
| pnRelated | Publication number of the related patent used as fallback (only present when replaceByRelated is enabled and a fallback occurred) |
| claims | Array of claim objects containing the full claim text |
| claimCount | Total number of claims |
| total | Total number of records returned |
| costToken | Token cost for this query |

## Usage Examples

**1. Retrieve claims for a single patent**
```
Show me the claims for patent CN115000000A.
```

**2. Get the claim count for a patent**
```
How many claims does US11000000B2 have?
```

**3. Batch-query claims for multiple patents**
```
Get the claims for patents EP3000000A1 and CN115000001A.
```

**4. Use related patent fallback for an application**
```
Get the claims for application CN202210000000.0A — if claims aren't available, use the granted version.
```

**5. Compare claims between patents**
```
Show me the independent claims of US11000000B2 and US10000000B1 side by side.
```

## Display Rules

1. **Present claims clearly**: Number each claim and preserve the hierarchical structure (independent vs. dependent claims).
2. **Highlight independent claims**: When the user is interested in the scope of protection, emphasize independent claims (typically claim 1 and any other independent claims).
3. **Claim count summary**: Always mention the total number of claims at the top of the response.
4. **Related patent notice**: If `pnRelated` is present, clearly inform the user that claims were sourced from a related patent and state which one.
5. **Error handling**: If the query fails or returns no results, explain the possible reasons (invalid patent number, patent not found, claims not yet published) and suggest alternatives (e.g., enabling replaceByRelated).
6. **Long claims**: For patents with many claims, consider showing a summary first (independent claims + total count) and offer to show all claims on request.

## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Claims availability**: Some early-stage application patents may not have claims published yet. Use `replaceByRelated` to attempt a fallback to a related patent.
- **Data coverage**: Results depend on the Eureka patent database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** — Queries about patent claims:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims for patent XX" | Full claims retrieval |
| "How many claims does XX have" | Claim count query |
| "What is claim 1 of patent XX" | Independent claim lookup |
| "Get claims using the granted version" | Fallback to related patent |
| "Compare the claims of XX and YY" | Multi-patent claim comparison |
| "What does patent XX protect" | Protection scope (claims-based) |

**Not applicable** — Needs beyond patent claims:

- Patent bibliography/metadata retrieval (use the bibliography skill)
- Patent legal status queries
- Patent full-text description retrieval
- Patent search by keyword or classification
- Patent image/drawing search
- Patent family analysis

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
