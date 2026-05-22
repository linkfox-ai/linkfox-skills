---
name: linkfox-eureka-bibliography
description: 从Eureka专利数据库查询专利著录项目（Bibliography）信息，包括标题、摘要、申请人、发明人、分类号、优先权、引用文献等。当用户提到专利著录项目、专利基本信息、专利标题摘要、专利申请人发明人、专利分类号、IPC分类、CPC分类、专利代理、审查员、优先权、引用文献、关联文件、预估到期日、patent bibliography, patent basic info, patent title and abstract, patent applicant/inventor, patent classification, IPC/CPC, patent agent, patent examiner, priority claims, cited references, related documents, estimated expiry, Eureka patent data时触发此技能。即使用户未明确提及"Eureka"或"著录项目"，只要其需求涉及查询专利的基础著录信息（标题、摘要、申请人、分类号等），也应触发此技能。
---

# Eureka Patent Bibliography

This skill guides you on how to retrieve patent bibliography (bibliographic) information via the Eureka patent platform, helping users quickly obtain structured metadata for one or more patents — including titles, abstracts, applicants, inventors, classifications, priority claims, cited references, and more.

## Core Concepts

The Eureka Bibliography tool returns comprehensive bibliographic data for each patent, organized into several categories:

1. **Identification** — Patent ID (`patentId`) and publication number (`pn`).
2. **Title & Abstract** — Multi-language invention titles (`inventionTitle`) and abstracts (`abstracts`).
3. **Patent Type** — One of APPLICATION, PATENT, UTILITY, or DESIGN.
4. **Parties** — Original applicants (`applicants`), current assignees (`assignees`), inventors (`inventors`), patent agents (`agents`), filing agency (`agency`), and examiners (`examiners`).
5. **Dates & References** — Application reference, publication reference, dates of public availability, and estimated expiry date (`exdt`).
6. **Classifications** — IPC-R (`classificationIpcr`), CPC (`classificationCpc`), UPC (`classificationUpc`), GBC (`classificationGbc`), Locarno (`classificationLoc`), FI (`classificationFi`), F-term (`classificationFterm`).
7. **Citations & Related Documents** — Cited patents (`referenceCitedPatents`), cited non-patent literature (`referenceCitedOthers`), and related documents such as divisionals/continuations (`relatedDocuments`).
8. **PCT Data** — PCT or regional filing data and publishing data.

**Patent identification**: Patents can be looked up by either patent ID or publication number. When both are provided, patent ID takes priority. Multiple values can be submitted in a single request (comma-separated, up to 100).

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| patentId | Conditionally | Patent ID. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values, up to 100. |
| patentNumber | Conditionally | Publication (announcement) number. At least one of patentId or patentNumber must be provided. Comma-separated for multiple values, up to 100. |

- If the user provides a publication number (e.g., CN115000000A, US11000000B2, EP3000000A1), use `patentNumber`.
- If the user provides an internal patent ID, use `patentId`.
- When both are supplied, `patentId` takes precedence.

## Response Fields

| Field | Description |
|-------|-------------|
| patentId | The patent's internal ID |
| pn | Publication (announcement) number |
| inventionTitle | Array of patent titles with language information |
| abstracts | Array of patent abstracts with language information |
| patentType | Patent type: APPLICATION, PATENT, UTILITY, or DESIGN |
| applicants | Array of original applicants |
| assignees | Array of current assignees (rights holders) |
| inventors | Array of inventors |
| agents | Array of patent agents |
| agency | Array of filing agencies |
| examiners | Array of patent examiners |
| priorityClaims | Array of priority claims |
| applicationReference | Application filing information (object) |
| publicationReference | Publication information (object) |
| datesOfPublicAvailability | Dates when the patent became publicly available (object) |
| classificationIpcr | IPC-R classification (object) |
| classificationCpc | CPC classification (object) |
| classificationUpc | UPC classification (object) |
| classificationGbc | GBC classification (object) |
| classificationLoc | Locarno classification (array) |
| classificationFi | FI classification (array) |
| classificationFterm | F-term classification (array) |
| referenceCitedPatents | Array of cited patent references |
| referenceCitedOthers | Array of cited non-patent literature |
| relatedDocuments | Array of related documents (divisional, continuation, etc.) |
| pctOrRegionalFilingData | PCT or regional filing data (object) |
| pctOrRegionalPublishingData | PCT or regional publishing data (object) |
| exdt | Estimated expiry date (integer timestamp) |
| total | Total number of records returned |
| costToken | Token cost for this query |

## Usage Examples

**1. Retrieve basic info for a single patent**
```
Show me the bibliography for patent CN115000000A.
```

**2. Get applicants and inventors for a patent**
```
Who are the applicants and inventors of US11000000B2?
```

**3. Batch-query bibliographic data for multiple patents**
```
Get the titles, abstracts, and classification for patents EP3000000A1, CN115000001A, and JP2022000001A.
```

**4. Check priority claims and related documents**
```
What are the priority claims and related documents for patent US11000000B2?
```

**5. Look up patent expiry date**
```
When does patent CN115000000A expire?
```

**6. Retrieve patent agent and examiner information**
```
Who is the patent agent and examiner for CN115000000A?
```

## Display Rules

1. **Present data clearly**: Show results in a well-structured format. For single patents, use labeled sections. For multiple patents, use a summary table with key fields and expand details as needed.
2. **Title and abstract**: Display the title and abstract in the language most relevant to the user. If multiple languages are available, show the user's preferred language first, with the original language in parentheses if different.
3. **Classification codes**: Format IPC/CPC/UPC codes clearly. When the user is looking at technology domains, provide the top-level description when possible.
4. **Dates**: Convert integer timestamps to human-readable date formats (YYYY-MM-DD).
5. **Error handling**: If the query fails or returns no results, explain the possible reasons (invalid patent number format, patent not found in database) and suggest the user double-check the input.
6. **Volume notice**: When querying many patents, present a summary table and note the total count returned.

## Important Limitations

- **Up to 100 patents per request**: The maximum number of patent IDs or publication numbers in a single call is 100.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Data coverage**: Results depend on the Eureka patent database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** — Queries about patent bibliographic/metadata information:

| User Says | Scenario |
|-----------|----------|
| "Show me the basic info for patent XX" | Full bibliography retrieval |
| "Who are the applicants/inventors of XX" | Party information lookup |
| "What classifications does patent XX have" | Classification query |
| "Get the title and abstract for these patents" | Batch title/abstract query |
| "When does this patent expire" | Expiry date check |
| "What patents does XX cite" | Cited references query |
| "Is this a utility or design patent" | Patent type check |
| "Show the priority claims for XX" | Priority information lookup |

**Not applicable** — Needs beyond patent bibliography:

- Patent legal status queries (use the legal-status skill)
- Patent full-text claims or description retrieval
- Patent search by keyword or classification
- Patent image/drawing search
- Patent family analysis
- Freedom-to-operate (FTO) analysis

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
