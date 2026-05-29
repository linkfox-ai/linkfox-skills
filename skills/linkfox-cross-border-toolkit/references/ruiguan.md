# Ruiguan IP Detection — Tool Reference

All tools below use:
- **Method**: POST, Content-Type: application/json
- **Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

---

## 1. Design Patent Detection (linkfox-ruiguan-patent-design)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/detectionPatentDesign`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | — | Product image URL to check against the patent database. Max 1000 chars. |
| queryMode | string | Yes | `hybrid` | Search mode. Enum: `physical` (real product photo), `line` (line drawing), `hybrid` (combined). Max 1000 chars. |
| topNumber | integer | Yes | `100` | Number of patent results to return. Max 100. |
| regions | string | No | `US` | Country/region codes, comma-separated. Supported: US, EU, CN, JP, KR, DE, GB, FR, IT, AU, CA, BR, MX, IN, TH, SE, CH, IE, IL, DK, NZ, AT, BX, FI, WO. Max 1000 chars. |
| productTitle | string | No | — | Product title for supplementary context. Max 1000 chars. |
| productDescription | string | No | — | Product description for supplementary context. Max 1000 chars. |
| patentStatus | string | No | `1` | Patent validity filter: `1` (active), `0` (expired), `1,0` (both). Max 1000 chars. |
| enableRadar | boolean | No | `true` | Enable AI radar analysis for suspected infringement judgment. |
| topLoc | string | No | — | LOC level-1 codes to restrict search scope (e.g., `06,07`). Regex: `^(0[1-9]\|1[0-9]\|2[0-9]\|3[0-2]\|ALL)(,…)*$`. Omit to use auto-prediction. |
| sourceLanguage | string | No | — | Source language code for translation (e.g., `zh-CN`). Leave empty if text is English. Max 1000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total patent records returned |
| data | array | Patent list |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| applicationNumber | string | Patent application number |
| publicationNumber | string | Patent publication number |
| patentProd | string | Patent title (English) |
| patentProdCn | string | Patent title (Chinese) |
| similarity | string | Similarity to product image (0–1) |
| patentImageUrl | string | Most-similar patent drawing URL |
| images | array | Full patent image list |
| abstracts | string | Patent abstract |
| specification | string | Patent specification text |
| inventors | array | Inventor list |
| applicants | array | Applicant list |
| applicantAddresses | array | Applicant addresses |
| troCase | boolean | Has TRO enforcement history |
| troHolder | boolean | Is TRO rights holder's patent |
| radarResult | object | AI radar analysis result |
| radarResult.same | boolean | Suspected infringement (true/false) |
| radarResult.exp | string | Radar judgment explanation |
| patentLoc | string | LOC classification (comma-separated) |
| locOneInfo | string | LOC level-1 details |
| locTwoInfo | string | LOC level-2 details |
| patentValidity | string | Patent validity status |
| applicationDate | string | Application date |
| publicationDate | string | Publication date |
| grantDate | string | Grant date |
| estimatedDueDate | string | Estimated expiration date |
| registrationOfficeCode | string | Patent registration office |
| patentFamily | array | Patent family list |
| globalPatentId | string | Global patent ID |
| globalImageId | string | Patent image ID |
| isSketchText | string | Whether the image is a sketch |

### Key Usage Notes
- Similarity ≥ 0.7 or `troCase = true` → high risk, review carefully.
- `radarResult.same = true` → suspected infringement, display `exp` explanation prominently.
- LOC codes 01–32 or `ALL`; omit `topLoc` for automatic LOC prediction.

---

## 2. Utility Patent Detection (linkfox-ruiguan-utility-patent)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/utilityPatentDetection`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| productTitle | string | Yes | — | Product title. Max 1000 chars. |
| productDescription | string | Yes | — | Product description. Max 1000 chars. |
| region | string | Yes | `US` | Target selling country/region codes, comma-separated. Currently supports: US. |
| topNumber | integer | Yes | `100` | Number of results to return. Range: 10–200. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total records |
| detectId | string | Detection ID |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |
| columns | array | Column definitions |
| data | array | Patent list |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| globalUtilityId | string | Patent ID |
| title | string | Patent title (English) |
| titleCn | string | Patent title (Chinese) |
| similarity | number | Similarity to product (0–1) |
| patentValidity | string | Patent validity: `Active` or `Invalid` |
| applicationNumber | string | Application number |
| applicationDate | string | Application date (yyyy-MM-dd) |
| publicationNumber | string | Publication number |
| publicationDate | string | Publication date (yyyy-MM-dd) |
| estimatedDueDate | string | Estimated expiration date (yyyy-MM-dd) |
| region | string | Registration office |
| patentAbstract | string | Abstract (English) |
| patentAbstractCn | string | Abstract (Chinese) |
| claims | string | Claims text |
| claimsCn | string | Claims text (Chinese) |
| specification | string | Specification text |
| specificationCn | string | Specification text (Chinese) |
| inventors | array | Inventors with country |
| inventorAddresses | array | Inventor addresses |
| applicants | array | Applicants with country |
| applicantAddresses | array | Applicant addresses |
| priorityNumber | array | Priority numbers |
| relatedPublicationDate | array | First publication dates |
| patentImageUrl | string | Patent cover image URL |
| images | array | Patent drawings |
| classNumList | array | Classification number paths (classNum1 > classNum2 > classNum3) |
| cpcKindRaw | array | CPC classification (raw JSON array) |
| troCase | boolean | Has TRO enforcement history |
| troHolder | boolean | Is TRO rights holder's patent |

### Key Usage Notes
- Currently only US region is supported.
- Max 200 results per query. Use topNumber=200 for thorough patent clearance.
- `troCase` / `troHolder` = true → elevated enforcement risk.

---

## 3. Copyright Detection (linkfox-ruiguan-copyright)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/copyrightDetection`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | — | Image URL to check for copyright infringement. Max 1000 chars. |
| topNumber | integer | Yes | `100` | Number of results to return. Range: 10–200. |
| enableRadar | boolean | Yes | `true` | Enable radar-based infringement detection. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total records |
| data | array | Detection result list |
| detectId | string | Detection session ID |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| path | string | Copyright work image path |
| pathThumb | string | Copyright work thumbnail path |
| similarity | string | Similarity score (decimal string, e.g., "0.85") |
| subRadarResult | integer | Radar result: `1` = infringing, `0` = not infringing, `null` = radar not run |
| copyrightUrl | string | Source URL |
| copyrightCode | string | Copyright identification code |
| rightsOwner | string | Rights owner |
| link | string | Copyright official website link |
| troCase | boolean | Has TRO enforcement history |
| troHolder | boolean | Is TRO rights holder's copyright |

### Key Usage Notes
- `subRadarResult = 1` and high similarity (≥ 0.80) → high infringement risk.
- `troCase` / `troHolder` = true → rights owner has active enforcement history.
- Max 200 results per query.

---

## 4. Graphic Trademark Detection (linkfox-ruiguan-graphic-trademark)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/trademarkGraphicDetection`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | — | Product image URL or base64-encoded image data. Max 1000 chars. |
| topNumber | integer | Yes | `5` | Max number of YOLO detection results to return. Max 100. |
| productTitle | string | No | — | Product title for context-aware detection. Max 1000 chars. |
| trademarkName | string | No | — | Suspected logo name to narrow results. Max 1000 chars. |
| regions | string | No | All countries | Country/region codes, comma-separated. Supported: US, WO, ES, GB, DE, IT, CA, MX, EM, AU, FR, JP, TR, BX, CN. |
| enableLocalizing | boolean | No | `false` | Enable image cropping for detected logo regions. |
| enableRadar | boolean | No | `true` | Enable radar monitoring. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| boundingBoxCount | integer | Number of detected logo regions |
| radarResult | string | Overall radar detection result |
| total | integer | Total records |
| data | array | Detection result list |
| detectId | string | Detection ID |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| image | string | Matched trademark image URL |
| boundingBox | string | YOLO coordinates (comma-separated) |
| subRadarResult | string | Sub-radar detection result |
| applicationNumber | string | Trademark application number |
| niceClassName | string | Nice classification names (comma-separated) |
| applicantName | string | Rights holder (comma-separated) |
| tradeMarkStatus | string | Trademark status. Enum: `DEL`, `ended`, `registered`, `act`, `pend`, `filed`, `""` |
| niceClass | array | Nice classification details |
| similarity | number | Similarity score (0–1) |
| registrationNumber | string | Registration number |
| registrationOfficeCode | string | Trademark registration office |
| registrationDate | string | Registration date |
| bid | string | Logo identifier |
| trademarkName | string | Text trademark name found in image |
| applicationDate | string | Application date |

### Key Usage Notes
- Uses YOLO object detection to locate logo-like regions in images.
- Similarity > 0.8 → high infringement risk.
- Omit `regions` to search all 15 supported countries by default.

---

## 5. Text Trademark Detection (linkfox-ruiguan-text-trademark)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/textTrademarkDetection`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| productTitle | string | Yes | — | Product title to scan. Max 1000 chars. |
| regions | string | No | US | Country/region codes, comma-separated. Supported: US, EM, GB, DE, FR, IT, ES, AU, CA, MX, JP, CN, WO, TR, BX. |
| limit | integer | Yes | `100` | Max number of results. Max 500. |
| productText | string | No | — | Additional product text (bullet points, description). Max 1000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total matched trademark records |
| data | array | Trademark list (flattened) |
| detectId | string | Detection session ID |
| columns | array | Column definitions |
| blacklistTrademarks | array | Detected blacklist trademarks |
| whitelistTrademarks | array | Detected whitelist (safe) trademarks |
| textTrademarkRadar | string | Product risk level: `"0"` = low risk, `"1"` = needs manual review, `"2"` = high risk |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| trademarkName | string | Trademark word |
| region | string | Country/region code |
| score | integer | Risk score |
| highestModeScore | integer | Highest risk score (0–5) |
| trademarksStatus | string | Highest-score trademark status |
| regionStatus | string | Trademark status in matched region |
| holder | string | Rights holder |
| applicationNumber | string | Application number |
| registrationNumber | string | Registration number |
| isFamous | boolean | Is famous trademark |
| isAmazonBrand | boolean | Is Amazon trending brand |
| isActiveHolder | boolean | Is active enforcement holder |
| isCompatibility | boolean | Is compatibility term |
| isCommonSense | boolean | Is common-use word |
| niceClass | array | Nice classification |
| originalTextMatches | array | Original text that triggered the match |

**blacklistTrademarks[] / whitelistTrademarks[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| trademark | string | Trademark name |
| region | string | Country/region code |
| note | string | Remark |

### Key Usage Notes
- `textTrademarkRadar`: `"0"` = safe, `"1"` = review needed, `"2"` = high risk.
- `highestModeScore`: 0 (safe) to 5 (highest risk).
- Always surface `blacklistTrademarks` prominently.
- Max 500 results per query.

---

## 6. Image Policy Compliance Detection (linkfox-ruiguan-image-compliance)

**Endpoint**: `POST https://tool-gateway.linkfox.com/ruiguan/gunPartsSearch`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | — | Product image URL to check. Max 1000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total records |
| data | array | Detected policy-violating product list |
| detectId | string | Detection session ID |
| columns | array | Column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

**data[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| pdImgOssUrl | string | Matched violating product image URL |
| cosine | number | Similarity between input image and violation (0–1) |
| pdTitle | string | Matched violating product title (English) |
| pdTitleCHNCensored | string | Matched violating product title (Chinese) |

### Key Usage Notes
- Cosine score > 0.8 → strong match to known prohibited product.
- Image-only detection — does not analyze text or metadata.
- Image URL must be publicly accessible.
