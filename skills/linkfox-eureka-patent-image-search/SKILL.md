---
name: linkfox-eureka-patent-image-search
description: 通过Eureka专利平台进行专利图像检索（以图搜图），上传一张图片URL即可检索外观设计或实用新型的相似专利。当用户提到专利图像检索、以图搜专利、外观设计搜索、图片相似专利、设计专利检索、图像搜索专利、专利视觉搜索、patent image search, search patent by image, design patent search, visual patent search, similar design patent, image similarity search, patent image matching, utility patent shape match, Eureka image search时触发此技能。即使用户未明确提及"Eureka"或"图像检索"，只要其需求涉及通过图片查找相似的外观设计专利或实用新型专利，也应触发此技能。
---

# Eureka Patent Image Search (Single Image)

This skill guides you on how to perform patent image search (search-by-image) via the Eureka patent platform. Given a single image URL, it finds visually similar patents in the design or utility patent databases, supporting multiple search models and extensive filtering options.

## Core Concepts

The Eureka Patent Image Search tool enables visual similarity search across patent databases:

1. **Search Models** — Four models are available depending on the patent type and search intent:
   - Model 1: Design smart association — finds design patents with intelligent visual association
   - Model 2: Design search this image — exact visual match for design patents
   - Model 3: Utility match shape — matches utility patents by shape/contour
   - Model 4: Utility match shape + pattern + color — matches utility patents by shape, pattern, and color combined

2. **Patent Types** — Two patent types are supported:
   - `D` (Design) — search within design/industrial design patents (use models 1 or 2)
   - `U` (Utility) — search within utility model patents (use models 3 or 4)

3. **Filtering** — Extensive optional filters for country/authority, Locarno classification, date ranges, legal status, assignees, and keyword fields.

4. **Scoring** — Results include a similarity `score` and can be sorted by score, application date, publication date, or issue date.

## Parameter Guide

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| url | string | The URL of the image to search with. Must be a publicly accessible image URL. |
| model | integer | Search model: 1 = design smart association, 2 = design search this image, 3 = utility match shape, 4 = utility match shape + pattern + color |
| patentType | string | Patent type to search: "D" = design patent, "U" = utility patent |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| country | string | — | Patent authority codes, comma-separated (e.g., CN,US,JP,EP,WO) |
| loc | string | — | Locarno classification code. Supports AND/OR/NOT boolean operators. |
| applyStartTime | string | — | Application date range start (format: yyyyMMdd) |
| applyEndTime | string | — | Application date range end (format: yyyyMMdd) |
| publicStartTime | string | — | Publication date range start (format: yyyyMMdd) |
| publicEndTime | string | — | Publication date range end (format: yyyyMMdd) |
| mainField | string | — | Search keyword within specific fields: title, abstract, claims, description, pn, applicant, inventor, IPC, UPC, LOC |
| assignees | string | — | Filter by assignee/rights holder name |
| legalStatus | string | — | Legal status codes, comma-separated. Values: 1=Published, 2=Examining, 3=Granted, 11=Withdrawn, 13=Rejected, 14=Revoked, 15=Expired, etc. |
| simpleLegalStatus | string | — | Simplified legal status: 0=Invalid, 1=Valid, 2=Pending, 220=PCT expired, 221=PCT in period, 999=Undetermined |
| preFilter | integer | 1 | Enable (1) or disable (0) pre-filtering by country and LOC classification |
| scoreExpansion | boolean | — | Enable score expansion for broader results |
| stemming | integer | 0 | Enable (1) or disable (0) word stemming in keyword search |
| includeMachineTranslation | boolean | — | Include machine-translated content in search |
| field | string | SCORE | Sort field: SCORE (similarity), APD (application date), PBD (publication date), ISD (issue date) |
| order | string | desc | Sort order: desc or asc |
| limit | integer | 10 | Results per page, range 1–100 |
| offset | integer | 0 | Pagination offset, range 0–1000 |
| lang | string | — | Title language preference: original, cn, en |
| isHttps | integer | — | Return image URLs with HTTPS (1) or HTTP (0) |
| returnImgId | boolean | — | Include image ID in results |

### Model & Patent Type Combinations

| Patent Type | Recommended Models | Description |
|-------------|-------------------|-------------|
| D (Design) | 1, 2 | Model 1 for smart association, Model 2 for exact visual match |
| U (Utility) | 3, 4 | Model 3 for shape match, Model 4 for shape + pattern + color |

## Response Fields

| Field | Description |
|-------|-------------|
| patentId | The patent's internal ID |
| patentPn | Publication number |
| title | Patent title |
| url | URL of the similar image found in the patent |
| score | Similarity score |
| apdt | Application date |
| pbdt | Publication date |
| authority | Patent authority (country code) |
| inventor | Inventor name |
| apno | Application number |
| originalAssignee | Original applicant/assignee |
| currentAssignee | Current rights holder |
| loc | Array of Locarno classification codes |
| imgId | Image ID (when returnImgId is enabled) |
| locMatch | Whether the Locarno classification matched the filter |
| total | Number of results in current page |
| allRecordsCount | Total number of matching results |
| costToken | Token cost for this query |

## Usage Examples

**1. Search for similar design patents using an image**
```
Search for design patents similar to this image: https://example.com/product-image.jpg — look in CN and US patent databases.
```
→ Use model=1 or 2, patentType="D", country="CN,US"

**2. Find utility patents with a similar shape**
```
Find utility patents that have a similar shape to this product image: https://example.com/gadget.png
```
→ Use model=3, patentType="U"

**3. Search with date and legal status filters**
```
Search for valid design patents similar to this image, filed after 2020, in the CN database: https://example.com/design.jpg
```
→ Use model=2, patentType="D", country="CN", applyStartTime="20200101", simpleLegalStatus="1"

**4. Search with Locarno classification**
```
Find design patents in LOC 14-01 similar to this product: https://example.com/phone-case.jpg
```
→ Use model=1, patentType="D", loc="14-01"

**5. Search with keyword and assignee filters**
```
Search for design patents similar to this image from Apple Inc.: https://example.com/device.jpg
```
→ Use model=2, patentType="D", assignees="Apple"

**6. Get more results with pagination**
```
Show me the next 20 design patents similar to this image: https://example.com/product.jpg
```
→ Use limit=20, offset=20

## Display Rules

1. **Present results as a visual gallery when possible**: Show the patent publication number, title, similarity score, and image URL for each result.
2. **Score interpretation**: Higher scores indicate greater visual similarity. Present scores as percentages or relative rankings for user clarity.
3. **Key metadata**: Always include patent number, title, authority, application date, and assignee for each result.
4. **Total count**: Mention `allRecordsCount` to indicate how many total matches were found, and how many are displayed.
5. **Model explanation**: When presenting results, briefly note which search model was used so the user understands the matching approach.
6. **Error handling**: If the query fails, check common issues: invalid image URL, unsupported image format, invalid model/patentType combination.
7. **Pagination guidance**: If there are more results than displayed, inform the user they can request more.

## Important Limitations

- **Single image only**: This endpoint accepts one image URL per request.
- **Image URL must be publicly accessible**: Private or authentication-required image URLs will fail.
- **Model & patent type pairing**: Models 1–2 are for design patents (D), models 3–4 are for utility patents (U). Mismatched combinations may produce poor results.
- **Offset limit**: Maximum offset is 1000, meaning at most 1000 + limit results can be accessed via pagination.
- **Locarno classification**: The `loc` parameter uses Locarno codes; users may need help identifying the correct code for their product category.

## User Expression & Scenario Quick Reference

**Applicable** — Visual patent search queries:

| User Says | Scenario |
|-----------|----------|
| "Search for patents similar to this image" | Basic image search |
| "Find design patents that look like this" | Design patent visual search |
| "Are there utility patents with this shape" | Utility patent shape match |
| "Search CN and US design patents for this product image" | Filtered image search |
| "Find valid patents similar to this design" | Legal status-filtered search |
| "Show me more results" | Pagination request |
| "Search in Locarno class 14-01" | Classification-filtered search |

**Not applicable** — Needs beyond image search:

- Patent text-based search (keyword, classification, applicant)
- Patent bibliography or metadata retrieval
- Patent legal status queries
- Patent claims or description retrieval
- Patent family analysis
- Multi-image or batch image search

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
