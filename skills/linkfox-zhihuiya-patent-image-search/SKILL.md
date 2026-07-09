---
name: linkfox-zhihuiya-patent-image-search
description: 基于智慧芽的专利图片相似度搜索，支持通过图片URL检索外观设计专利和实用新型专利。当用户提到专利图片搜索、外观设计专利侵权检查、外观专利搜索、视觉专利查询、以图搜专利、专利相似度检测、专利图片匹配、洛迦诺分类搜索、检查产品设计是否侵犯已有专利、patent image search, design patent search, patent reverse image search, design patent lookup, PatSnap, patent similarity时触发此技能。即使用户未明确提及"智慧芽"或"专利图片"，只要其需求涉及通过图片查找相似专利或排查外观/实用新型专利风险，也应触发此技能。
---

# Zhihuiya Patent Image Search

This skill guides you on how to perform image-based patent similarity searches using the Zhihuiya patent database, helping users identify potentially similar design patents and utility model patents.

## Core Concepts

**Patent Image Search** uses visual AI models to compare a given product or design image against a global patent image database. It returns a ranked list of similar patents, enabling users to evaluate infringement risks or conduct prior-art research.

**Two patent types are supported:**

| Type | Code | Description |
|------|------|-------------|
| Design Patent | `D` | Protects the ornamental appearance of a product (default) |
| Utility Model Patent | `U` | Protects the functional shape/structure of a product |

**Search models** vary by patent type:

| Model ID | Patent Type | Strategy | Recommendation |
|----------|-------------|----------|----------------|
| 1 | Design (`D`) | Intelligent Association | Recommended for design patents |
| 2 | Design (`D`) | Search This Image | Exact visual match |
| 3 | Utility Model (`U`) | Match Shape | Shape-only comparison |
| 4 | Utility Model (`U`) | Match Shape/Pattern/Color | Recommended for utility model patents |

**Scoring logic**: A higher `score` value means greater visual similarity. When presenting results, sort by score in descending order (highest similarity first) so users can prioritize the most relevant patents for review.

## Parameter Guide

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| url | The image URL to search against | `https://example.com/product.jpg` |
| patentType | Patent type: `D` (design) or `U` (utility model) | `D` |
| model | Search model ID (see table above) | `1` |

### Common Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| country | Patent authority country codes, comma-separated (e.g., `CN,US,JP`) | All countries |
| loc | Locarno classification codes, connectable with AND/OR/NOT | None |
| legalStatus | Legal status codes, comma-separated | None |
| simpleLegalStatus | Simple legal status: `0` (expired), `1` (active), `2` (pending) | None |
| assignees | Applicant / patent holder name | None |
| applyStartTime | Application start date (`yyyyMMdd`) | None |
| applyEndTime | Application end date (`yyyyMMdd`) | None |
| publicStartTime | Publication start date (`yyyyMMdd`) | None |
| publicEndTime | Publication end date (`yyyyMMdd`) | None |
| limit | Number of results to return (1-100) | 10 |
| offset | Pagination offset (0-1000) | 0 |
| field | Sort field: `SCORE`, `APD`, `PBD`, `ISD` | `SCORE` |
| order | Sort order: `desc` or `asc` (for APD/PBD/ISD) | `desc` |
| lang | Title language preference: `original`, `cn`, `en` | `original` |
| preFilter | Enable country/LOC pre-filtering: `1` (on) / `0` (off) | `1` |
| stemming | Enable stemming: `1` (on) / `0` (off) | `0` |
| mainField | Search within title, abstract, claims, description, publication number, application number, applicant, inventor, IPC/UPC/LOC | None |
| includeMachineTranslation | Include machine-translated data in search | None |
| scoreExpansion | Enable score expansion | None |
| isHttps | Return HTTPS image URLs: `1` (yes) / `0` (no) | `0` |
| returnImgId | Return image IDs in results | `false` |

### Commonly Used Country Codes

| Code | Country/Region |
|------|---------------|
| CN | China |
| US | United States |
| JP | Japan |
| KR | South Korea |
| EP | European Patent Office |
| WO | WIPO |
| DE | Germany |
| GB | United Kingdom |
| FR | France |
| AU | Australia |

## 调用方式

- **API 端点**：`POST /zhihuiya/patentImageSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/zhihuiya_patent_image_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-patent-image-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Local Image Upload

This tool requires a **publicly accessible image URL**. If the user provides a local image file path (e.g., `C:\Users\...\photo.png`, `/home/.../image.jpg`), you must upload it first to obtain a public URL.

Run the upload script:
```bash
python scripts/upload_image.py /path/to/local/image.png
```

The script will return a public URL (valid for 24 hours) that can be used as the image URL parameter.

## Usage Examples

**1. Basic design patent search (recommended starting point)**
Search for design patents similar to a product image across all countries:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "limit": 20
}
```

**2. Design patent search limited to specific countries**
Search only in China and the United States:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "country": "CN,US",
  "limit": 20
}
```

**3. Utility model patent search**
Check utility model patents with shape/pattern/color matching:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "country": "CN",
  "limit": 20
}
```

**4. Search with Locarno classification filter**
Narrow results to a specific product category (e.g., LOC 07-01 for tableware):
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "loc": "07-01",
  "preFilter": 1,
  "limit": 20
}
```

**5. Search only active patents within a date range**
Find active design patents filed after 2020:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "simpleLegalStatus": "1",
  "applyStartTime": "20200101",
  "limit": 30
}
```

**6. Search by specific assignee**
Find patents held by a particular company:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "assignees": "Apple Inc.",
  "limit": 20
}
```

**7. Get results with Chinese-translated titles**
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "lang": "cn",
  "limit": 20
}
```

## Display Rules

1. **Sort by score**: Always sort results by `score` in descending order (highest similarity first) to help users quickly identify the most relevant infringement risks.

2. **Show complete details**: When summarizing results or generating reports, include ALL of the following for each patent -- do NOT omit or abbreviate:
   - Application number (`apno`)
   - Patent title in Chinese (use `lang: cn` or provide translation)
   - Inventor (`inventor`)
   - Patent drawing (the matched `url` image)
   - **Every** patent image in the image list
   - Patent abstract
   - Patent description
   - LOC classification information (`loc`)
   - Radar result (`radarResult`) if available
   - Patent specification

3. **Legal disclaimer**: Always append a friendly reminder at the end of results:
   > This search result was generated by LinkfoxAgent. It is recommended to consult a professional patent attorney for legal advice.

4. **Score explanation**: Remind users that the score represents visual similarity -- a higher score indicates a closer match, but does not constitute a legal determination of infringement.

5. **Pagination guidance**: When the total count exceeds the returned results, inform users about the total number of matching patents and guide them to use `offset` and `limit` for additional pages.

6. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., verify the image URL is publicly accessible, check country codes, adjust date formats).
## User Expression & Scenario Quick Reference

**Applicable** -- Image-based patent similarity searches:

| User Says | Scenario |
|-----------|----------|
| "Check if my product design infringes any patents" | Design patent infringement check |
| "Search for similar design patents" | Design patent similarity search |
| "Find patents that look like this image" | Visual patent lookup |
| "Are there any patents similar to my product appearance" | Appearance risk assessment |
| "Utility model patent search by image" | Utility model search |
| "Check patent risks for this product in China and US" | Multi-country patent check |
| "Find active design patents in this category" | Filtered patent search |
| "Who holds patents similar to this design" | Competitor patent discovery |

**Not applicable** -- Needs beyond patent image search:
- Text-based patent search (keyword/abstract/claim search)
- Patent legal status monitoring or annuity management
- Patent valuation or licensing negotiation
- Freedom-to-operate (FTO) legal opinions
- Patent family or citation analysis


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.
---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
