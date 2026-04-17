---
name: linkfox-eureka-abstract-image
description: 通过Eureka专利数据平台获取专利摘要附图。当用户提到专利摘要附图、专利图纸、专利示意图、专利图片、摘要附图检索、专利图片查询、Eureka摘要附图、patent abstract images, patent drawings, patent illustrations, Eureka, abstract image lookup, patent figure时触发此技能。即使用户未明确说"摘要附图"，只要其需要查看专利文件中的图纸或示意图，也应触发此技能。
---

# Eureka Patent Abstract Image

This skill guides you on how to retrieve abstract images (drawings) from the Eureka patent data platform, helping users quickly obtain the illustrative figures associated with specific patents.

## Core Concepts

Abstract images (abstract drawings) are the representative figures attached to a patent document's abstract section. They provide a quick visual overview of the invention. This tool queries the Eureka patent platform and returns download paths for these images.

**Lookup logic**: You must provide at least one of two identifiers -- a patent ID or a publication number. If both are provided, patent ID takes priority. You can query up to 100 patents in a single request by separating values with commas.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | Conditionally (one of the two must be provided) | Internal patent identifier; multiple values separated by commas, max 100 | 5e6f7a8b9c |
| Publication Number | patentNumber | Conditionally (one of the two must be provided) | Patent publication/announcement number; multiple values separated by commas, max 100 | CN115059423A, US11234567B2 |

- At least one of `patentId` or `patentNumber` must be supplied.
- If both are supplied, `patentId` takes precedence.
- Multiple values are separated by commas (English commas), with an upper limit of 100.

## Response Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | The internal patent identifier |
| Publication Number | pn | The publication/announcement number |
| Abstract Drawing Path | abstractDrawingPath | URL path to the abstract image file |
| Total | total | Total number of records returned |
| Cost Token | costToken | Tokens consumed by the query |

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/eureka_abstract_image.py` directly to run queries.

## Usage Examples

**1. Single patent lookup by publication number**
```
Retrieve the abstract image for patent CN115059423A.
```

**2. Multiple patents lookup by publication number**
```
Get abstract drawings for patents US11234567B2, EP3456789A1, and CN115059423A.
```

**3. Lookup by patent ID**
```
Fetch the abstract image for patent ID 5e6f7a8b9c.
```

**4. Batch lookup with mixed identifiers**
```
I have the following patent IDs: abc123, def456. Please get their abstract images.
```

## Display Rules

1. **Show the image**: When the response includes an `abstractDrawingPath`, display the image directly using Markdown image syntax so the user can see the drawing inline.
2. **Patent identification**: Always show the publication number (`pn`) alongside each image so the user knows which patent each drawing belongs to.
3. **Missing images**: If a patent has no abstract drawing (empty `abstractDrawingPath`), explicitly inform the user that no abstract image is available for that patent.
4. **Batch results**: When multiple patents are queried, present results in a clear, organized list or table format.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest the user verify their patent IDs or publication numbers.

## Important Limitations

- **Up to 100 patents per request**: The maximum number of patent IDs or publication numbers in a single call is 100.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Data coverage**: Results depend on the Eureka patent platform's database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent abstract image retrieval:

| User Says | Scenario |
|-----------|----------|
| "Show me the abstract image for patent XX" | Single patent image lookup |
| "Get the drawings for these patents" | Batch patent image lookup |
| "What does the patent figure look like" | Abstract drawing retrieval |
| "Retrieve patent illustrations for XX" | Image download path retrieval |
| "I need the abstract drawing for publication number XX" | Lookup by publication number |

**Not applicable** -- Needs beyond abstract image retrieval:
- Full patent text or claims analysis
- Patent search by keyword or classification
- Patent legal status or family information
- Patent citation or prior art analysis
- Patent valuation or infringement analysis


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
