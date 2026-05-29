# Zhihuiya (PatSnap) Patent Tools — Tool Reference

All tools below use:
- **Method**: POST, Content-Type: application/json
- **Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

## Shared Input Pattern

Most Zhihuiya tools (except Patent Image Search) share a common input pattern:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | At least one of patentId / patentNumber | Zhihuiya internal patent ID. Comma-separated, max 100 entries. Max 60,000 chars. If both patentId and patentNumber are provided, patentId takes priority. |
| patentNumber | string | At least one of patentId / patentNumber | Publication/grant number (e.g., `US11234567B2`, `CN115000000A`). Comma-separated, max 100 entries. Max 60,000 chars. |

Additional per-tool parameters are listed below each tool.

---

## 1. Patent Image Search (linkfox-zhihuiya-patent-image-search)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/patentImageSearch`

> This tool does NOT follow the shared input pattern. It uses image URL as primary input.

### Request Parameters

**Required:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Yes | Image URL to search against. Max 1000 chars. |
| patentType | string | Yes | Patent type: `D` (design, default) or `U` (utility model). |
| model | integer | Yes | Search model ID. Design: `1` (intelligent association, recommended), `2` (exact visual match). Utility: `3` (shape match), `4` (shape/pattern/color, recommended). |

**Optional:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| country | string | All | Patent authority country codes, comma-separated (e.g., `CN,US,JP`). |
| loc | string | — | Locarno classification codes, connectable with AND/OR/NOT. |
| legalStatus | string | — | Legal status codes, comma-separated. Values: `1`(published), `2`(examining), `3`(granted), `8`(double grant avoided), `11`(withdrawn), `12`(withdrawn-unspecified), `17`(withdrawn-deemed), `18`(withdrawn-voluntary), `13`(rejected), `14`(revoked), `15`(expired), `16`(non-payment), `21`(restoration), `22`(ceased), `23`(partially revoked), `24`(discontinued), `30`(abandoned), `19`(abandoned-deemed), `20`(abandoned-voluntary), `25`(abandoned-unspecified), `222`(PCT-unentered-in-period), `223`(PCT-entered-in-period), `224`(PCT-entered-expired), `225`(PCT-unentered-expired). |
| simpleLegalStatus | string | — | Simple legal status, comma-separated. Values: `0`(expired), `1`(active), `2`(pending), `220`(PCT designated expiration), `221`(PCT designated period), `999`(undetermined). |
| assignees | string | — | Applicant / patent holder name. Max 1000 chars. |
| applyStartTime | string | — | Application start date (`yyyyMMdd`). |
| applyEndTime | string | — | Application end date (`yyyyMMdd`). |
| publicStartTime | string | — | Publication start date (`yyyyMMdd`). |
| publicEndTime | string | — | Publication end date (`yyyyMMdd`). |
| limit | integer | `10` | Number of results (1–100). |
| offset | integer | `0` | Pagination offset (0–1000). |
| field | string | `SCORE` | Sort field: `SCORE`, `APD` (application date), `PBD` (publication date), `ISD` (grant date). |
| order | string | `desc` | Sort order for APD/PBD/ISD: `desc` or `asc`. |
| lang | string | `original` | Title language: `original`, `cn` (Chinese), `en` (English). |
| preFilter | integer | `1` | Enable country/LOC pre-filtering: `1` (on), `0` (off). |
| stemming | integer | `0` | Enable stemming: `1` (on), `0` (off). |
| mainField | string | — | Search within title, abstract, claims, description, publication number, application number, applicant, inventor, IPC/UPC/LOC. Max 1000 chars. |
| includeMachineTranslation | boolean | — | Include machine-translated data in search. |
| scoreExpansion | boolean | — | Enable score expansion. |
| isHttps | integer | `0` | Return HTTPS image URLs: `1` (yes), `0` (no). |
| returnImgId | boolean | `false` | Return image IDs in results. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned this page |
| allRecordsCount | integer | Total matching records in database |
| data | array | Patent record list |
| columns | array | Column definitions |
| type | string | Rendering style |
| costToken | integer | Tokens consumed |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| patentPn | string | Patent publication number |
| apno | string | Application number |
| title | string | Patent title |
| inventor | string | Inventor |
| originalAssignee | string | Original assignee |
| currentAssignee | string | Current assignee |
| authority | string | Patent authority (country code) |
| url | string | Similar patent drawing URL |
| score | number | Similarity score (higher = more similar; only valid when field=SCORE) |
| loc | array | LOC classification codes |
| locMatch | integer | High-weight LOC hit: `1` (hit), `0` (miss). Only when model=1 & field=SCORE. |
| apdt | integer | Application date (timestamp) |
| pbdt | integer | Publication date (timestamp) |
| imgId | string | Patent image ID (only when returnImgId=true) |

### Key Usage Notes
- `model` must match `patentType`: models 1–2 for `D`, models 3–4 for `U`.
- Higher `score` = greater visual similarity.
- Use `offset` + `limit` for pagination when `allRecordsCount` > returned results.

---

## 2. Simple Bibliography (linkfox-zhihuiya-simple-bibliography)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/simpleBibliography`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| allRecordsCount | integer | Total records |
| data | array | Bibliography data list |
| columns | array | Column definitions |
| type | string | Rendering style |
| costToken | integer | Tokens consumed |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| title | string | Patent title |
| abstractContent | string | Patent abstract |
| publicationNumber | string | Publication number |
| pn | string | Publication/grant number |
| country | string | Country code |
| publicationCountry | string | Publication country |
| publicationDate | string | Publication date |
| publicationKind | string | Publication kind code |
| patentType | string | Patent type (invention, utility model, design, etc.) |
| kind | string | Patent kind code |
| applicationNo | string | Application number |
| applicationDate | string | Application date |
| applicants | array | Applicant list |
| inventors | array | Inventor list |
| assignees | array | Patent assignee list |
| assigneeAddresses | array | Assignee address list |
| ipcMain | string | IPC main classification |
| ipcFurther | array | IPC additional classifications |
| cpcMain | string | CPC main classification |
| cpcFurther | array | CPC additional classifications |
| loc | array | LOC classification codes |
| gbc | array | GBC classification codes |
| priorityClaims | array | Priority claim entries |
| pctApplicationNo | string | PCT application number |
| pctFilingDate | string | PCT filing date |
| pctEntryDate | string | PCT national phase entry date |
| citedPatents | array | Cited patent references |
| citedNonPatents | array | Cited non-patent literature |

---

## 3. Bibliography (linkfox-zhihuiya-bibliography)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/bibliography`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Bibliography data list |
| columns | array | Column definitions |
| type | string | Rendering style |
| costToken | integer | Tokens consumed |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| inventionTitle | array | Patent title with language info |
| abstracts | array | Patent abstract |
| patentType | string | Patent type: `APPLICATION` (invention application), `PATENT` (granted invention), `UTILITY` (utility model), `DESIGN` (design patent) |
| applicants | array | Original applicants |
| assignees | array | Current patent holders / assignees |
| inventors | array | Inventors |
| agents | array | Patent agents / attorneys |
| agency | array | Filing agencies / patent firms |
| examiners | array | Patent examiners |
| priorityClaims | array | Priority claim declarations |
| applicationReference | object | Application filing data |
| publicationReference | object | Publication data |
| datesOfPublicAvailability | object | Public availability dates |
| classificationIpcr | object | IPC classification |
| classificationCpc | object | CPC classification |
| classificationUpc | object | US Patent Classification |
| classificationLoc | array | Locarno Classification (designs) |
| classificationFi | array | FI classification (Japan) |
| classificationFterm | array | F-term classification (Japan) |
| classificationGbc | object | GBC classification |
| referenceCitedPatents | array | Cited patent documents |
| referenceCitedOthers | array | Cited non-patent literature |
| relatedDocuments | array | Divisional / continuation application info |
| pctOrRegionalFilingData | object | PCT or regional phase filing data |
| pctOrRegionalPublishingData | object | PCT or regional phase publication data |
| exdt | integer | Estimated patent expiration date (Zhihuiya, timestamp) |

---

## 4. Claims Data (linkfox-zhihuiya-claim-data)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/claimData`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| replaceByRelated | string | No | `0` | Substitute with family patent claims when unavailable: `1` = yes, `0` = no. Max 1000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |
| claims | array | Claims array with claim text and metadata |
| claimCount | integer | Total number of claims |

---

## 5. Claims Translated (linkfox-zhihuiya-claim-translated)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/claimDataTranslated`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| lang | string | No | `en` | Translation language: `en` (English), `cn` (Chinese), `jp` (Japanese). Max 1000 chars. |
| replaceByRelated | integer | No | `0` | Substitute with family patent claims when unavailable: `1` = yes, `0` = no. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |
| claims | string | Translated claims text |

---

## 6. Abstract Translated (linkfox-zhihuiya-abstract-translated)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/abstractDataTranslated`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| lang | string | No | `en` | Translation language: `en` (English), `cn` (Chinese), `jp` (Japanese). Max 1000 chars. |
| replaceByRelated | integer | No | `0` | Substitute with family patent abstract when unavailable: `1` = yes, `0` = no. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| title | string | Translated patent title |
| abstractText | string | Translated patent abstract |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |

---

## 7. Description Data (linkfox-zhihuiya-description)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/descriptionData`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| replaceByRelated | string | No | `0` | Substitute with family patent description when unavailable: `1` = yes, `0` = no. Max 1000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |
| description | array | Description content sections |

---

## 8. Description Translated (linkfox-zhihuiya-description-translated)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/descriptionDataTranslated`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| lang | string | No | `en` | Translation language: `en` (English), `cn` (Chinese), `jp` (Japanese). Max 1000 chars. |
| replaceByRelated | integer | No | `0` | Substitute with family patent description when unavailable: `1` = yes, `0` = no. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| description | string | Translated description text |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |

---

## 9. Legal Status (linkfox-zhihuiya-legal-status)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/legalStatus`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Legal status list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| simpleLegalStatus | array | Simple legal status. Values: Inactive, Active, Pending, Undetermined, PCT designated period, PCT designated expiration |
| legalStatus | array | Detailed legal status. Values: Published, Examining, Granted, Double, Abandoned-Undetermined, Abandoned-Voluntarily, Abandoned-Deemed, Withdrawn-Undetermined, Withdrawn-Voluntarily, Withdrawn-Deemed, Rejected, Revoked, Expired, Non-Payment, Restoration, Ceased, P-Revoked, Discontinuation, PCT published, PCT entering(designated period), PCT entering(designated expiration), PCT unentered |
| eventStatus | array | Legal events. Values: Transfer, License, Pledge, Trust, Opposition, Re-examination, Customs, Litigation, Preservation, Invalid-procedure, Oral-procedure, Declassification, Double application |
| legalDate | integer | Legal status update date (timestamp) |

---

## 10. PDF Full Text (linkfox-zhihuiya-pdf)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/pdfData`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| replaceByRelated | string | No | `0` | Substitute with family patent PDF when unavailable: `1` = yes, `0` = no. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| pdfPath | string | PDF full-text download URL |
| pnRelated | string | Substitute family patent publication number (only when substitution occurred) |

---

## 11. Cited References — prior art cited by this patent (linkfox-zhihuiya-cited-references)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/patentForwardCitation`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| citedPatents | array | List of cited patent references |
| citedOthers | array | List of cited non-patent literature |

---

## 12. Cited By — later patents citing this patent (linkfox-zhihuiya-cited-by)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/patentCited`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| citedBy3y | integer | Times cited in last 3 years |
| citedBy5y | integer | Times cited in last 5 years |
| citedBySimpleFamily | integer | Simple family cited patent count |
| citedByInpadocFamily | integer | INPADOC family cited patent count |
| citedByPatsnapFamily | integer | PatSnap family cited patent count |
| citedByPatents | array | List of patents that cite this patent |

---

## 13. Patent Family (linkfox-zhihuiya-patent-family)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/patentFamily`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Patent family result list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| simpleFamilyId | integer | Simple family ID |
| simpleFamily | array | Simple family patent list |
| inpadocFamilyId | integer | INPADOC family ID |
| inpadocFamily | array | INPADOC family patent list |
| patsnapFamilyId | integer | PatSnap family ID |
| patsnapFamily | array | PatSnap family patent list |

---

## 14. Full-Text Images (linkfox-zhihuiya-fulltext-image)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/fulltextImage`

### Additional Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | string | No | `"100"` | Number of images to return. Max 100. All params are string type, max 1000 chars. |
| offset | string | No | `"0"` | Pagination offset. String type, max 1000 chars. |

> Note: For this tool, patentId and patentNumber are also string type with max 1000 chars (not 60,000).

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Image list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| fulltextImagePath | string | Full-text image download path |
| imageType | string | Image type |

---

## 15. Abstract Image (linkfox-zhihuiya-abstract-image)

**Endpoint**: `POST https://tool-gateway.linkfox.com/zhihuiya/abstractImage`

### Additional Request Parameters

Uses shared input pattern only (patentId / patentNumber). No additional parameters.

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Records returned |
| data | array | Abstract image result list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| abstractDrawingPath | string | Abstract drawing image download path |
