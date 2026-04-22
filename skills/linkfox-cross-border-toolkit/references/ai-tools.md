# AI Tools — Tool Reference

All tools below use:
- **Method**: POST, Content-Type: application/json
- **Auth**: Header `Authorization: <api_key>` (env: `LINKFOXAGENT_API_KEY`)

---

## 1. AI Image Generation (linkfox-multimodal-generate-image)

**Endpoint**: `POST https://tool-gateway.linkfox.com/multimodal/generateImage`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| prompt | string | Yes | — | Text description of the desired image. Supports text-to-image, image-to-image, editing, model swapping, etc. Max 1000 chars. |
| referenceImageUrl | string | No | — | Reference image URL(s). Multiple URLs separated by commas, up to 3 images. Max 1000 chars. |
| aspectRatio | string | No | `1:1` | Output aspect ratio. Enum: `1:1` (square), `3:4` (portrait), `4:3` (landscape), `9:16` (vertical fullscreen), `16:9` (horizontal fullscreen). |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Request ID |
| finished | boolean | Whether generation is complete |
| status | string | Status indicator |
| text | string | Generated image content (markdown image) |
| type | string | Markdown type |
| title | string | Image title |
| costToken | integer | Tokens consumed |

### Key Usage Notes
- Reference images by number in prompts: "image 1", "image 2", etc.
- Max 3 reference images per request.
- Image URLs must be publicly accessible.

---

## 2. Image Recognition (linkfox-multimodal-recognize-image)

**Endpoint**: `POST https://tool-gateway.linkfox.com/multimodal/recognizeImage`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | — | Publicly accessible image URL. Supported formats: JPG, JPEG, PNG, GIF, WebP, BMP. Max 1000 chars. |
| requirement | string | No | "描述这张图片里面的内容" | Natural-language instruction describing what to identify or analyze. Max 1000 chars. |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| text | string | Image analysis text result |
| stdout | string | Standard output content |
| status | string | Response status indicator |
| type | string | Component type |
| costToken | integer | Tokens consumed |

### Key Usage Notes
- Be specific with `requirement`: "Extract all visible text" is better than "analyze this image".
- Supports OCR text extraction, object identification, product analysis, A+ page review.

---

## 3. Product Main Image Attribute Extraction (linkfox-multimodal-extract-attributes)

**Endpoint**: `POST https://tool-gateway.linkfox.com/multimodal/extractPromptsFromMainImage`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| productImageAnalysisPrompt | string | Yes | — | Natural-language instruction describing which visual dimensions to extract (color, shape, material, style, etc.). Max 1000 chars. |
| analyzeAdditionalImages | boolean | No | `false` | Whether to also analyze additional product images beyond the main image. |
| refResultData | string | No | — | Reference data from a previous step, containing the product list to analyze. Must be a JSON string with a `products` array. Max 2,024,000 chars. |
| userInput | string | No | — | Supplementary user input for additional context. Max 10,000,000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| sourceType | string | Source type |
| columns | array | Column definitions for table rendering |
| costToken | integer | Total LLM tokens consumed (input + output) |
| type | string | Rendering style |
| products | array | Product attribute list (one record per product per attribute) |
| attributeGroups | array | Products grouped by attribute name and value |

**products[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Product ASIN |
| productId | string | Product ID |
| title | string | Product title |
| imageUrl | string | Main image URL |
| productImageUrls | array | Product image list |
| asinUrl | string | Product detail page URL |
| brand | string | Brand name |
| price | number | Price |
| rating | number | Rating score |
| ratings | integer | Number of ratings |
| color | string | Color |
| material | string | Material |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales growth rate |
| availableDate | string | Listing date |
| sourceType | string | Source type (e.g., "amazon") |
| sourceTool | string | Source tool |
| attributeName | string | Extracted attribute name (e.g., color, material, shape) |
| attributeValue | string | Extracted attribute value (e.g., red, plastic, round) |

**attributeGroups[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| attributeName | string | Attribute name |
| groups | array | Groups under this attribute |
| groups[].attributeValue | string | Attribute value |
| groups[].count | integer | Number of products in this group |
| groups[].asins | array | ASINs sharing this attribute value |

### Key Usage Notes
- Requires upstream product data with image URLs via `refResultData`.
- Extracting N dimensions from M products produces up to M × N rows.
- Focus on one or two dimensions per call for cleaner results.

---

## 4. Product Image Similarity Analysis (linkfox-multimodal-product-similarity)

**Endpoint**: `POST https://tool-gateway.linkfox.com/multimodal/analyzeProductSimilarity`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| similarityThreshold | integer | No | `60` | Similarity threshold (0–100). Higher = stricter matching. |
| includeSingleBrandGroups | boolean | No | `true` | Whether to include groups with only one brand. `false` = focus on cross-brand similarity. |
| refResultData | string | No | — | JSON string of preceding tool's result data containing `products` array. Max 2,024,000 chars. |
| userInput | string | No | — | User input text. Max 10,000,000 chars. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| groups | array | Similarity group list |
| analysisInfo | object | Analysis summary |
| tables | array | Tabular result data (each with `data`, `columns`, `name`) |
| total | integer | Total result items |
| title | string | Result title |
| type | string | Rendering style |
| costToken | integer | Total LLM tokens consumed |

**groups[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| groupNumber | integer | Group sequence number |
| reason | string | Reason for grouping |
| brandCount | integer | Number of distinct brands in group |
| asins | array | Product list within group |

**groups[].asins[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Product ASIN |
| productId | string | Product ID |
| brand | string | Brand name |
| price | number | Price |
| rating | number | Rating score |
| ratings | integer | Number of ratings |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales growth rate |
| imageUrl | string | Main image URL |
| productImageUrls | array | All product image URLs |
| imagePrompt | string | AI-generated image description |
| asinUrl | string | Product detail page URL |
| availableDate | string | Listing date |
| color | string | Color |
| material | string | Material |
| sourceTool | string | Source tool |
| sourceType | string | Source type |

**analysisInfo fields:**

| Field | Type | Description |
|-------|------|-------------|
| totalProductsAnalyzed | integer | Total products analyzed |
| totalGroupsFound | integer | Total groups found |
| similarityThreshold | number | Similarity threshold (0–1 decimal) |
| analysisTimestamp | string | Analysis timestamp |

### Key Usage Notes
- Post-processing tool only — requires upstream product data.
- Set `includeSingleBrandGroups: false` for cross-brand competitor detection.
- Higher threshold (80+) for near-identical products; lower (40) for broad clustering.

---

## 5. Product Title Analyzer (linkfox-product-title-analyze)

**Endpoint**: `POST https://tool-gateway.linkfox.com/product/titleAnalyze`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| tokenizationAndCountingRequest | string | Yes | — | Natural-language instruction specifying one attribute dimension to extract from titles (e.g., scene words, audience words, material). One dimension per call. |
| outputMode | string | No | `MULTIPLE_RECORDS` | Attribute value output mode. `MULTIPLE_RECORDS`: each value as separate record. `COMMA_SEPARATED`: multiple values comma-separated in one record. |
| refResultData | string | No | — | Externally supplied product data (JSON string). Only needed when referencing data from a previous conversation turn; current-turn products are auto-aggregated. |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| sourceType | string | Source type |
| type | string | Rendering style |
| columns | array | Column definitions |
| costToken | integer | Total LLM tokens consumed |
| products | array | Product attribute list (one record per ASIN per attribute) |
| attributeGroups | array | Products grouped by attribute name and value |

**products[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| asin | string | Product ASIN |
| productId | string | Product ID |
| title | string | Product title |
| attributeName | string | Extracted attribute name (e.g., "Scene Word") |
| attributeValue | string | Extracted attribute value (e.g., "Outdoor") |
| price | number | Price |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | number | Monthly sales revenue |
| monthlySalesUnitsGrowthRate | number | Monthly sales growth rate |
| rating | number | Rating score |
| ratings | integer | Number of ratings |
| brand | string | Brand name |
| imageUrl | string | Main image URL |
| asinUrl | string | Product detail page URL |
| availableDate | string | Listing date |
| color | string | Color |
| material | string | Material |
| productImageUrls | array | Product image list |
| sourceTool | string | Source tool |
| sourceType | string | Source type |

**attributeGroups[] fields:**

| Field | Type | Description |
|-------|------|-------------|
| attributeName | string | Attribute name |
| groups | array | Groups under this attribute |
| groups[].attributeValue | string | Attribute value |
| groups[].count | integer | Number of products in this group |
| groups[].asins | array | ASINs sharing this attribute value |

### Key Usage Notes
- Analyze ONE dimension per call (scene words OR audience words, NOT both).
- Auto-aggregates products from all prior steps in the current conversation turn.
- Use `MULTIPLE_RECORDS` for counting/sorting; `COMMA_SEPARATED` for at-a-glance view.
