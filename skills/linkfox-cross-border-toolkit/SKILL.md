---
name: linkfox-cross-border-toolkit
description: "跨境电商综合AI工具集，整合66个专业工具，覆盖亚马逊/TikTok/eBay/Walmart/Shopee/1688全平台选品分析、关键词研究、竞品分析、评论洞察、专利商标检测、专利深度研究、趋势分析、供应链搜索、AI图像处理和实时网页检索。当用户需要进行跨境电商选品、市场分析、竞品研究、关键词分析、评论挖掘、专利风险排查、趋势洞察、1688找货源、数据导出或任何跨平台商品搜索时触发此技能。Cross-border e-commerce AI toolkit with 66 specialized tools for Amazon/TikTok/eBay/Walmart/Shopee/1688 product research, keyword analysis, competitor intelligence, review insights, patent & trademark detection, trend analysis, sourcing, AI image processing, and web search. Trigger when: product selection, market analysis, competitor research, keyword tracking, review mining, IP risk detection, trend analysis, supplier sourcing, cross-platform product search, image analysis/generation, or data aggregation."
---

# LinkFox Cross-Border E-Commerce Toolkit

A comprehensive AI toolkit with **66 specialized tools** for cross-border e-commerce, covering product research, competitor analysis, keyword tracking, review insights, patent/IP detection, trend analysis, 1688 sourcing, AI image processing, and real-time web search across Amazon, TikTok, eBay, Walmart, Shopee, and 1688.

## Setup

1. Get your API key: https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre
2. Set environment variable: `export LINKFOXAGENT_API_KEY=your-key-here`

All tools call the LinkFox Tool Gateway API (`https://tool-gateway.linkfox.com/`) with `Authorization: <api_key>` header. Full parameters and examples are in this skill’s `references/api.md` (endpoint index) and category files such as `references/zhihuiya.md`, `references/junglescout.md`, etc.

## Tool Selection Guide

When the user doesn't specify a tool, follow these rules:

### Amazon Product Data (choose by use case)
1. **Keepa** — richest fields, strong real-time accuracy. Default choice for most product queries.
2. **Sorftime** — best for long-term trend analysis, historical snapshots, and FBA profit breakdown.
3. **SellerSprite (卖家精灵)** — optimized for product discovery and competitor lookup by keyword.
4. **Amazon Frontend (亚马逊前台)** — best real-time fidelity (live storefront data); use when exact live ranking or A+ content is needed.

### Amazon Keyword & Traffic Analysis
1. **Jungle Scout Keyword by Keyword** — keyword expansion and long-tail discovery with search volume, PPC bids.
2. **Jungle Scout Keyword by ASIN** — reverse ASIN keyword lookup, see what keywords drive traffic to competitors.
3. **Jungle Scout Keyword History** — weekly search volume trends over time, seasonality analysis.
4. **Jungle Scout Share of Voice** — brand share analysis on search result pages.
5. **SIF tools** — ASIN keyword reverse lookup, traffic source breakdown, keyword competition density.
6. **ABA Data Explorer** — Amazon Brand Analytics search term data.

### Niche / Market Analysis
1. **Jiimore (极目) tools** — niche market analysis, reviews, product discovery, competitor mining.
2. **Amazon Opportunity Report** — AI-generated comprehensive market opportunity report by keyword.
3. **Jungle Scout Product Database** — multi-condition Amazon product filtering.
4. **Jungle Scout Sales Estimates** — daily sales estimates for specific ASINs.

### Cross-Platform Product Search
| Platform | Tool |
|----------|------|
| Amazon | Keepa / Sorftime / SellerSprite / Amazon Frontend |
| TikTok | EchoTik (search + new product rank) / FastMoss (search + top-selling) |
| Shopee | YouYing Shopee Product Search |
| Walmart | Walmart Search |
| eBay | eBay Search |
| 1688 | DLD Product Billboard / DLD Product Search |

### Patent & IP Detection
- **Design patent image search** → Zhihuiya Patent Image Search
- **Design patent infringement** → Ruiguan Patent Design
- **Utility patent infringement** → Ruiguan Utility Patent
- **Copyright** → Ruiguan Copyright
- **Graphic trademark** → Ruiguan Graphic Trademark
- **Text trademark** → Ruiguan Text Trademark
- **Product compliance** → Ruiguan Image Compliance
- **Deep patent research** (claims, description, family, legal status, citations, translations, figures, PDF) → Zhihuiya tools

### Trends & Web Search
- **Google Trends** — keyword popularity over time, real-time trending topics.
- **Web Search** — real-time web search for anything outside specialized tools.

### AI Image & Analysis Tools
- **Image generation** → Multimodal Generate Image
- **Image recognition** → Multimodal Recognize Image
- **Product image analysis** → Multimodal Extract Attributes
- **Image similarity grouping** → Multimodal Product Similarity
- **Title word segmentation** → Product Title Analyze

---

## Complete Tool Catalog (66 tools)

### Amazon Frontend (5 tools)

| Skill | Function |
|-------|----------|
| `linkfox-amazon-search` | Amazon search simulation with location settings |
| `linkfox-amazon-product-detail` | Product detail, bullet points, A+ content |
| `linkfox-amazon-reviews` | Product reviews filtered by star rating |
| `linkfox-amazon-search-by-image` | Image-based product search |
| `linkfox-amazon-opportunity-report` | AI-generated market opportunity report by keyword |

### ABA Data (1 tool)

| Skill | Function |
|-------|----------|
| `linkfox-aba-data-explorer` | Amazon Brand Analytics search term data mining |

### Keepa (3 tools)

| Skill | Function |
|-------|----------|
| `linkfox-keepa-product-search` | Product filtering by keywords, BSR, price, sales |
| `linkfox-keepa-product-detail` | Batch ASIN detail lookup (price, sales, monthly data) |
| `linkfox-keepa-product-history` | Price, BSR, and sales history/trends for an ASIN |

### Sorftime (2 tools)

| Skill | Function |
|-------|----------|
| `linkfox-sorftime-product-search` | Product search with historical month snapshots, 14 marketplaces |
| `linkfox-sorftime-product-detail` | ASIN detail with trend history, FBA profit analysis |

### SellerSprite / 卖家精灵 (2 tools)

| Skill | Function |
|-------|----------|
| `linkfox-sellersprite-product-search` | Product discovery by category and filters |
| `linkfox-sellersprite-competitor` | Competitor lookup by keyword |

### Jungle Scout (6 tools)

| Skill | Function |
|-------|----------|
| `linkfox-junglescout-keyword-by-keyword` | Expand seed keyword into related keywords with search volume, PPC bids |
| `linkfox-junglescout-keyword-by-asin` | Reverse ASIN keyword lookup (1-10 ASINs) |
| `linkfox-junglescout-keyword-history` | Weekly historical search volume trends |
| `linkfox-junglescout-keyword-share-of-voice` | Brand share of voice on search result pages |
| `linkfox-junglescout-product-database` | Multi-condition product filtering with auto-paging |
| `linkfox-junglescout-sales-estimates` | Daily sales estimates for an ASIN over a date range |

### SIF Data Analysis (4 tools)

| Skill | Function |
|-------|----------|
| `linkfox-sif-asin-keywords` | Reverse keyword lookup for ASIN |
| `linkfox-sif-asin-summary` | ASIN traffic structure breakdown |
| `linkfox-sif-keyword-overview` | Keyword competition density and overview |
| `linkfox-sif-keyword-traffic` | Keyword traffic source analysis |

### Jiimore / 极目 (5 tools)

| Skill | Function |
|-------|----------|
| `linkfox-jiimore-niche-by-keyword` | Niche market analysis by keyword |
| `linkfox-jiimore-niche-by-asin` | ASIN-based niche competitor discovery |
| `linkfox-jiimore-niche-info` | Niche market metrics and overview |
| `linkfox-jiimore-niche-review` | Niche market review mining and sentiment |
| `linkfox-jiimore-product-discovery` | Product discovery with fine-grained filters |

### TikTok E-Commerce (4 tools)

| Skill | Function |
|-------|----------|
| `linkfox-echotik-product-search` | TikTok product search with sales and creator data |
| `linkfox-echotik-new-product-rank` | TikTok new product rankings across 16 regions |
| `linkfox-fastmoss-product-search` | TikTok product search with keyword, category, sales filters |
| `linkfox-fastmoss-top-selling` | TikTok top-selling product rankings by day/week/month |

### Shopee (1 tool)

| Skill | Function |
|-------|----------|
| `linkfox-youying-shopee-product-search` | Shopee product search across 11 Southeast Asia marketplaces |

### Walmart (1 tool)

| Skill | Function |
|-------|----------|
| `linkfox-walmart-search` | Walmart product search |

### eBay (1 tool)

| Skill | Function |
|-------|----------|
| `linkfox-ebay-search` | eBay product search |

### 1688 Sourcing (2 tools)

| Skill | Function |
|-------|----------|
| `linkfox-dld-product-billboard` | 1688 product rankings and trending items |
| `linkfox-dld-product-search` | 1688 product sourcing search |

### Google Trends (2 tools)

| Skill | Function |
|-------|----------|
| `linkfox-google-trends-keyword` | Keyword popularity trend over time |
| `linkfox-google-trends-rising` | Real-time trending topics |

### Web Search (1 tool)

| Skill | Function |
|-------|----------|
| `linkfox-tsearch-web-search` | Real-time web search (powered by Tavily) |

### AI Image & Analysis Tools (5 tools)

| Skill | Function |
|-------|----------|
| `linkfox-multimodal-generate-image` | AI image generation from text/reference images |
| `linkfox-multimodal-recognize-image` | Image recognition and analysis |
| `linkfox-multimodal-extract-attributes` | Extract visual attributes from product images |
| `linkfox-multimodal-product-similarity` | Group products by image similarity |
| `linkfox-product-title-analyze` | Title word segmentation and frequency analysis |

### IP Risk Detection / 睿观 (6 tools)

| Skill | Function |
|-------|----------|
| `linkfox-ruiguan-patent-design` | Design patent infringement detection |
| `linkfox-ruiguan-utility-patent` | Utility patent infringement detection |
| `linkfox-ruiguan-copyright` | Copyright infringement detection |
| `linkfox-ruiguan-graphic-trademark` | Graphic trademark detection |
| `linkfox-ruiguan-text-trademark` | Text trademark detection |
| `linkfox-ruiguan-image-compliance` | Product image policy compliance check |

### Patent Research / 智慧芽 (15 tools)

| Skill | Function |
|-------|----------|
| `linkfox-zhihuiya-patent-image-search` | Design patent visual similarity search |
| `linkfox-zhihuiya-simple-bibliography` | Simple bibliographic info |
| `linkfox-zhihuiya-bibliography` | Full bibliographic data (applicants, inventors, classifications) |
| `linkfox-zhihuiya-claim-data` | Patent claims text |
| `linkfox-zhihuiya-claim-translated` | Patent claims translation (CN/EN/JP) |
| `linkfox-zhihuiya-abstract-translated` | Patent abstract translation (CN/EN/JP) |
| `linkfox-zhihuiya-description` | Patent specification/description |
| `linkfox-zhihuiya-description-translated` | Patent description translation (CN/EN/JP) |
| `linkfox-zhihuiya-legal-status` | Patent legal status and events |
| `linkfox-zhihuiya-pdf` | Patent PDF full text |
| `linkfox-zhihuiya-cited-references` | References cited by this patent (prior-art list; API `patentForwardCitation`) |
| `linkfox-zhihuiya-cited-by` | Patents that cite this patent (API `patentCited`) |
| `linkfox-zhihuiya-patent-family` | Patent family (simple/INPADOC/PatSnap) |
| `linkfox-zhihuiya-fulltext-image` | Full-text figures and drawings |
| `linkfox-zhihuiya-abstract-image` | Abstract figures |

---

## Tool Reference Files (by classification)

Read the relevant reference file when you need full API parameter details, response fields, and usage constraints:

- **Amazon Frontend + ABA** (6 tools: search, product detail, reviews, image search, opportunity report, ABA): See `references/amazon-frontend.md`
- **Keepa** (3 tools: product search, product detail, price history): See `references/keepa.md`
- **Sorftime** (2 tools: product search, product detail with trends): See `references/sorftime.md`
- **SellerSprite / 卖家精灵** (2 tools: product search, competitor): See `references/sellersprite.md`
- **Jungle Scout** (6 tools: keyword by keyword, keyword by ASIN, keyword history, share of voice, product database, sales estimates): See `references/junglescout.md`
- **SIF Data Analysis** (4 tools: ASIN keywords, ASIN summary, keyword overview, keyword traffic): See `references/sif.md`
- **Jiimore / 极目** (5 tools: niche by keyword, niche by ASIN, niche info, niche review, product discovery): See `references/jiimore.md`
- **TikTok E-Commerce** (4 tools: EchoTik search, EchoTik new product rank, FastMoss search, FastMoss top-selling): See `references/tiktok.md`
- **Shopee + Walmart + eBay** (3 tools): See `references/shopee-walmart-ebay.md`
- **1688 / 店雷达** (2 tools: product billboard, product search): See `references/1688.md`
- **Google Trends + Web Search** (3 tools: keyword trend, rising topics, web search): See `references/trends-websearch.md`
- **AI Image & Analysis Tools** (5 tools: generate image, recognize image, extract attributes, product similarity, title analyze): See `references/ai-tools.md`
- **Ruiguan IP Detection / 睿观** (6 tools: design patent, utility patent, copyright, graphic trademark, text trademark, image compliance): See `references/ruiguan.md`
- **Zhihuiya Patent / 智慧芽** (15 tools: image search, bibliography, claims, translations, description, legal status, PDF, citations, family, figures): See `references/zhihuiya.md`

---

## Common Workflow Examples

### Example 1: Amazon Market Analysis

```
Goal: Evaluate the "yoga mat" market on Amazon US

Step 1: Use linkfox-keepa-product-search to search "yoga mat" on Amazon US, filter by monthly sales > 300
Step 2: Use linkfox-junglescout-keyword-by-keyword to expand "yoga mat" and find related keywords with search volume
Step 3: Use linkfox-jiimore-niche-by-keyword to analyze the niche market's competition level and brand concentration
Step 4: Use linkfox-amazon-opportunity-report for an AI-generated comprehensive market report
```

### Example 2: Competitor Deep Dive

```
Goal: Analyze competitor ASIN B08JYQLKXZ

Step 1: Use linkfox-keepa-product-detail to get product details, price, and monthly sales
Step 2: Use linkfox-junglescout-keyword-by-asin to find which keywords drive traffic to this ASIN
Step 3: Use linkfox-sif-asin-summary to see the traffic structure (organic vs paid)
Step 4: Use linkfox-amazon-reviews to mine customer reviews for pain points
Step 5: Use linkfox-junglescout-sales-estimates to get daily sales over the past 90 days
```

### Example 3: Cross-Platform Product Search

```
Goal: Find trending products across platforms

Step 1: Use linkfox-echotik-new-product-rank to discover TikTok trending new products
Step 2: Use linkfox-amazon-search to check if similar products exist on Amazon
Step 3: Use linkfox-dld-product-search to find suppliers on 1688
Step 4: Use linkfox-google-trends-keyword to verify the trend is growing
```

### Example 4: IP Risk Check Before Listing

```
Goal: Ensure a product doesn't infringe any IP

Step 1: Use linkfox-ruiguan-patent-design to check for design patent infringement (upload product image)
Step 2: Use linkfox-ruiguan-utility-patent to check for utility patent infringement
Step 3: Use linkfox-ruiguan-copyright to check for copyright issues
Step 4: Use linkfox-ruiguan-text-trademark to check if the listing text contains registered trademarks
Step 5: Use linkfox-zhihuiya-patent-image-search to do a broader design patent similarity search
```

### Example 5: Keyword Seasonality & Trend Analysis

```
Goal: Determine if "christmas decorations" is seasonal and plan inventory

Step 1: Use linkfox-junglescout-keyword-history to get 12-month weekly search volume
Step 2: Use linkfox-google-trends-keyword to see the multi-year trend pattern
Step 3: Use linkfox-junglescout-keyword-share-of-voice to see which brands dominate this keyword
Step 4: Use linkfox-junglescout-product-database to find products in this category with good sales
```

### Example 6: TikTok Product Research

```
Goal: Find hot products on TikTok for cross-border sellers

Step 1: Use linkfox-fastmoss-top-selling to get this week's top-selling products
Step 2: Use linkfox-echotik-product-search to search for specific product categories
Step 3: Use linkfox-youying-shopee-product-search to check if these products are also trending on Shopee
Step 4: Use linkfox-dld-product-search to find 1688 suppliers
```

## Display Rules

1. **Present data factually**: Show query results in clear tables without subjective business advice unless the user asks for recommendations.
2. **Currency context**: Different platforms use different currencies. Always remind users of the currency when showing price/revenue data.
3. **Source attribution**: When presenting data, mention which tool/data source it came from.
4. **Error handling**: When a query fails, explain the error and suggest adjusting parameters.
5. **Multi-tool coordination**: When using multiple tools in sequence, summarize findings across all tools into a coherent analysis.

## Important Limitations

- **API Key required**: All tools require `LINKFOXAGENT_API_KEY` environment variable.
- **Rate limits**: Each tool has its own rate limits. Avoid excessive concurrent requests.
- **Data freshness**: Data freshness varies by source. Check individual tool documentation for details.
- **Regional coverage**: Not all tools cover all marketplaces. Check supported regions for each tool.

## User Expression & Scenario Quick Reference

**Applicable** — Cross-border e-commerce research and analysis:

| User Says | Recommended Tool(s) |
|-----------|---------------------|
| "帮我选品" / "什么好卖" | Keepa/Sorftime product search + Jiimore niche analysis |
| "这个ASIN卖得怎么样" | Keepa product detail + Jungle Scout sales estimates |
| "这个词的搜索量" | Jungle Scout keyword history / ABA data explorer |
| "竞品分析" | Keepa + SIF ASIN keywords + Amazon reviews |
| "会不会侵权" | Ruiguan patent/copyright/trademark detection |
| "TikTok什么火" | EchoTik/FastMoss new product rank + top-selling |
| "1688找货源" | DLD product search/billboard |
| "虾皮选品" | YouYing Shopee product search |
| "帮我画个图" | Multimodal generate image |
| "分析这张图" | Multimodal recognize image / extract attributes |
| "这个词热不热" | Google Trends keyword / Jungle Scout keyword history |
| "专利信息查询" | Zhihuiya bibliography / claims / description / legal status |

**Not applicable**:
- Store operations, advertising strategy, logistics planning
- Non-e-commerce tasks (general coding, writing, etc.)
- Real-time inventory management or order processing
- Direct communication with platforms or sellers

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
