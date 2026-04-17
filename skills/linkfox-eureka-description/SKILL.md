---
name: linkfox-eureka-description
description: 通过Eureka专利数据平台获取专利说明书（描述）数据。当用户提到专利说明书、专利全文、专利技术描述、专利实施方式详情、Eureka说明书数据、patent specification, patent full text, technical description, embodiment details, Eureka, patent detailed description, patent description data时触发此技能。即使用户未明确说"Eureka"，只要其需要查看一项或多项专利的完整说明书/描述内容，也应触发此技能。
---

# Eureka Patent Description Data

This skill guides you on how to query patent description (specification) data from the Eureka patent data platform, helping users retrieve the full-text description content of specific patents.

## Core Concepts

A patent description (also called the specification) is the detailed technical document that accompanies a patent filing. It discloses how the invention works, preferred embodiments, and other technical details required by patent law. This tool queries the Eureka platform to return description data for one or more patents identified by their internal patent ID or public publication number.

**Identifier priority**: When both a patent ID and a publication number are provided for the same query, the patent ID takes precedence.

**Family substitution**: If the description for a given patent is unavailable, the tool can optionally return the description from a related family member patent instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Internal patent ID. At least one of patentId or patentNumber must be provided. Multiple values separated by commas; max 100. |
| patentNumber | string | Conditionally | Publication / announcement number. At least one of patentId or patentNumber must be provided. Multiple values separated by commas; max 100. |
| replaceByRelated | string | No | Whether to substitute a family patent's description when the target patent's description is unavailable. `1` = yes, `0` = no. |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of patent records returned |
| data | array | List of patent description objects |
| data[].patentId | string | Patent ID |
| data[].pn | string | Publication number |
| data[].pnRelated | string | Publication number of the substitute family patent (only present when family substitution is used) |
| data[].description | array | Description / specification content sections |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by the query |
| type | string | Rendering style hint |

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/eureka_description.py` directly to run queries.

## How to Build Queries

### Querying by Publication Number

When users provide a patent publication number (e.g., CN115099012A, US20230012345A1), pass it via the `patentNumber` parameter:

```
patentNumber: "CN115099012A"
```

### Querying by Patent ID

When users provide internal patent IDs, pass them via the `patentId` parameter:

```
patentId: "abc123def456"
```

### Batch Queries

Both `patentId` and `patentNumber` accept comma-separated values for batch lookups (up to 100):

```
patentNumber: "CN115099012A,US20230012345A1,EP4123456A1"
```

### Family Substitution

When a patent's description is not available in the database and the user still wants content, enable family substitution:

```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

## Usage Examples

**1. Look up a single patent description by publication number**
```
patentNumber: "CN115099012A"
```

**2. Look up descriptions for multiple patents at once**
```
patentNumber: "CN115099012A,US20230012345A1"
```

**3. Look up with family substitution enabled**
```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

**4. Look up by patent ID**
```
patentId: "some-patent-id"
```

## Display Rules

1. **Present data faithfully**: Show the returned description content clearly without altering technical details or adding subjective interpretation.
2. **Structured output**: When the description contains multiple sections (background, summary, detailed description, claims, etc.), present them with clear headings for readability.
3. **Family substitution notice**: If the response includes a `pnRelated` field, explicitly inform the user that the description was sourced from a related family patent and state the substitute publication number.
4. **Batch results**: When multiple patents are returned, clearly separate each patent's content with its publication number as a heading.
5. **Error handling**: When a query fails or returns no data, explain the reason and suggest the user verify the patent ID or publication number.

## Important Limitations

- **Identifier requirement**: At least one of `patentId` or `patentNumber` must be provided; the tool cannot search by keyword or applicant name.
- **Batch limit**: A maximum of 100 patents can be queried in a single request.
- **Availability**: Not all patents have descriptions available in the database. Use `replaceByRelated: "1"` to attempt family substitution when needed.
- **Priority rule**: If both `patentId` and `patentNumber` are supplied, `patentId` takes precedence.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about patent description / specification content:

| User Says | Scenario |
|-----------|----------|
| "Show me the description of patent XX" | Single patent description lookup |
| "Get the full specification for these patents" | Batch patent description retrieval |
| "I need the detailed text of CN115099012A" | Lookup by publication number |
| "Can you find a family patent's description instead" | Family substitution query |
| "What does this patent describe technically" | Description content review |

**Not applicable** -- Needs beyond patent description data:
- Patent search by keyword, applicant, or classification
- Patent claim analysis or claim chart generation
- Patent legal status or prosecution history
- Patent landscape or statistical analysis
- Freedom-to-operate or infringement opinions


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
