# LinkFox Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-orange)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/skills-70-brightgreen)](#skills-catalog)

**LinkFox Skills** is an AI skill set designed for cross-border e-commerce. It provides 70 API-driven skills covering product research, competitor analysis, keyword tracking, Amazon Ads reporting, patent search, compliance detection, and more.

Built on the [Agent Skills](https://agentskills.io) open standard, compatible with Claude Code, Cursor, GitHub Copilot, and 30+ AI agent platforms.

---

## Installation

Make sure you have [Node.js](https://nodejs.org/) installed (provides `npx`).

### Install all skills

```bash
npx skills add linkfox-ai/linkfox-skills
```

### Install specific skills

```bash
npx skills add linkfox-ai/linkfox-skills --skill linkfox-amazon-search linkfox-keepa-product-search
```

### List available skills

```bash
npx skills add linkfox-ai/linkfox-skills --list
```

### Install for a specific agent

```bash
npx skills add linkfox-ai/linkfox-skills --agent claude-code
npx skills add linkfox-ai/linkfox-skills --agent cursor
```

## Setup

Get your API key and configure the environment before using any skill.

1. Follow the [LinkFoxAgent API Setup Guide](https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre) to obtain your key.
2. Set the environment variable:
   ```bash
   export LINKFOXAGENT_API_KEY=your-key-here
   ```

## Skills Catalog


### Amazon

| Skill | Description |
| --- | --- |
| `linkfox-aba-data-explorer` | Explore Amazon Brand Analytics (ABA) search term data and trends |
| `linkfox-amazon-ads-auth` | Amazon Ads OAuth authorization, profile discovery, and access-token management |
| `linkfox-amazon-ads-entity` | List Amazon Ads SP/SB entities (campaigns, ad groups, keywords, product ads, targets) |
| `linkfox-amazon-ads-report` | One-stop Amazon Ads SP/SB reporting: request, poll, download, and auto-extract |
| `linkfox-amazon-opportunity-report` | Generate AI-powered Amazon opportunity reports with market potential, pricing, reviews, and trend analysis |
| `linkfox-amazon-opportunity-screener` | Reverse-screen Amazon niches and keywords by 30+ business metrics (market size, growth, competition, pricing, demographics, review themes) |
| `linkfox-amazon-product-detail` | Get detailed Amazon product info by ASIN (price, BSR, bullets, etc.) |
| `linkfox-amazon-reviews` | Retrieve and analyze Amazon product reviews |
| `linkfox-amazon-search` | Search Amazon products by keyword with real-time ranking data |
| `linkfox-amazon-search-by-image` | Find similar Amazon products using image-based search |
| `linkfox-amazon-store-aplus-content` | Amazon Store Aplus Content |
| `linkfox-amazon-store-auth` | Amazon Store Auth |
| `linkfox-amazon-store-catalog` | Amazon Store Catalog |
| `linkfox-amazon-store-customer-feedback` | Amazon Store Customer Feedback |
| `linkfox-amazon-store-feeds` | Amazon Store Feeds |
| `linkfox-amazon-store-listings` | Amazon Store Listings |
| `linkfox-amazon-store-orders` | Amazon Store Orders |
| `linkfox-amazon-store-pricing` | Amazon Store Pricing |
| `linkfox-amazon-store-report` | Amazon Store Report |
| `linkfox-amazon-store-uploads` | Amazon Store Uploads |

### 1688

| Skill | Description |
| --- | --- |
| `linkfox-dld-product-billboard` | Browse 1688 wholesale product rankings and trending items |
| `linkfox-dld-product-search` | Search 1688 wholesale marketplace for supplier products |

### eBay

| Skill | Description |
| --- | --- |
| `linkfox-ebay-search` | Search eBay listings by keyword with price and seller data |

### Walmart

| Skill | Description |
| --- | --- |
| `linkfox-walmart-search` | Search Walmart products by keyword with pricing and availability |
| `linkfox-walmart-wmtwin` | Walmart Wmtwin |

### TikTok (EchoTik)

| Skill | Description |
| --- | --- |
| `linkfox-echotik-new-product-rank` | Track new product rankings on TikTok Shop |
| `linkfox-echotik-product-search` | Search TikTok Shop products with sales and engagement data |

### TikTok (FastMoss)

| Skill | Description |
| --- | --- |
| `linkfox-fastmoss-product-search` | Search TikTok products with keyword, category, sales, and creator filters |
| `linkfox-fastmoss-top-selling` | Browse TikTok top-selling product rankings by day, week, or month |

### Ozon (Mpstats)

| Skill | Description |
| --- | --- |
| `linkfox-mpstats-ozon-brand-products` | Drill into all Ozon SKUs under a brand with filters, sorting, and currency conversion via MPSTATS |
| `linkfox-mpstats-ozon-category-products` | Drill into all Ozon SKUs under a Russian category path with filters for niche mining via MPSTATS |
| `linkfox-mpstats-ozon-product-detail` | Batch-fetch full Ozon product card (price, sales, stock, rating, lost profit) for up to 100 SKUs via MPSTATS |
| `linkfox-mpstats-ozon-product-search` | Search Ozon (Russia) products by Russian keyword, SKU list, brand, or seller - the MPSTATS Ozon discovery entry point |
| `linkfox-mpstats-ozon-product-trend` | Daily time-series for a single Ozon SKU (sales, price, stock, optional search visibility) via MPSTATS |
| `linkfox-mpstats-ozon-seller-products` | Drill into all Ozon SKUs under a seller ID for shop structure audits via MPSTATS |

### Google Trends

| Skill | Description |
| --- | --- |
| `linkfox-google-aimodel-search` | Google AI Mode search with optional multi-turn follow-up prompts; returns Markdown AI Overview with citations for cross-border deep research |
| `linkfox-google-trends-keyword` | Analyze Google Trends data for specific keywords |
| `linkfox-google-trends-rising` | Discover rising and breakout search queries on Google Trends |

### Keepa

| Skill | Description |
| --- | --- |
| `linkfox-keepa-product-detail` | Get Keepa-powered product details including monthly sales estimates |
| `linkfox-keepa-product-history` | View historical price, BSR, and sales trends from Keepa |
| `linkfox-keepa-product-search` | Advanced Amazon product search with Keepa data (BSR, sales, price filters) |

### Jiimore

| Skill | Description |
| --- | --- |
| `linkfox-jiimore-niche-by-asin` | Find niche market and competitors by ASIN |
| `linkfox-jiimore-niche-by-keyword` | Discover niche opportunities by keyword analysis |
| `linkfox-jiimore-niche-info` | Get niche market size, competition level, and growth trends |
| `linkfox-jiimore-niche-review` | Analyze review sentiment and pain points in a niche |
| `linkfox-jiimore-product-discovery` | Discover profitable products with FBA profitability screening |

### JungleScout

| Skill | Description |
| --- | --- |
| `linkfox-junglescout-keyword-by-asin` | Junglescout Keyword By Asin |
| `linkfox-junglescout-keyword-by-keyword` | Junglescout Keyword By Keyword |
| `linkfox-junglescout-keyword-history` | Junglescout Keyword History |
| `linkfox-junglescout-keyword-share-of-voice` | Junglescout Keyword Share Of Voice |
| `linkfox-junglescout-product-database` | Junglescout Product Database |
| `linkfox-junglescout-sales-estimates` | Junglescout Sales Estimates |

### SellerSprite

| Skill | Description |
| --- | --- |
| `linkfox-sellersprite-competitor` | Reverse ASIN lookup for competitor sales and keyword data |
| `linkfox-sellersprite-market-research` | Sellersprite Market Research |
| `linkfox-sellersprite-market-statistics` | Sellersprite Market Statistics |
| `linkfox-sellersprite-product-search` | Search and filter Amazon products using SellerSprite analytics |
| `linkfox-sellersprite-traffic-keyword` | Sellersprite Traffic Keyword |

### SIF (Search Intelligence)

| Skill | Description |
| --- | --- |
| `linkfox-sif-asin-keywords` | Reverse lookup traffic keywords for an ASIN (organic + ad rankings) |
| `linkfox-sif-asin-summary` | Analyze ASIN traffic sources and distribution |
| `linkfox-sif-keyword-overview` | Get keyword search volume, competition, and CPC overview |
| `linkfox-sif-keyword-traffic` | Analyze keyword traffic trends and seasonal patterns |

### Sorftime

| Skill | Description |
| --- | --- |
| `linkfox-sorftime-product-detail` | Get Amazon product detail and historical trends by ASIN via Sorftime (sales, price, BSR history) |
| `linkfox-sorftime-product-search` | Search and filter Amazon products with Sorftime data (BSR, sales, price, historical snapshots) |

### Shopee (YouYing)

| Skill | Description |
| --- | --- |
| `linkfox-youying-shopee-product-search` | Search and filter Shopee products across 11 marketplaces with YouYing data |

### Compliance (Ruiguan)

| Skill | Description |
| --- | --- |
| `linkfox-ruiguan-copyright` | Detect image copyright infringement and TRO risk |
| `linkfox-ruiguan-graphic-trademark` | Search graphic/logo trademarks for infringement risk |
| `linkfox-ruiguan-image-compliance` | Check product image compliance and IP risk |
| `linkfox-ruiguan-patent-design` | Search design patents for potential infringement |
| `linkfox-ruiguan-text-trademark` | Search text trademarks for naming conflict risk |
| `linkfox-ruiguan-utility-patent` | Search utility patents for technical infringement risk |

### PatSnap (Zhihuiya) Patent

| Skill | Description |
| --- | --- |
| `linkfox-zhihuiya-abstract-image` | Retrieve patent abstract images from PatSnap |
| `linkfox-zhihuiya-abstract-translated` | Get translated patent abstracts from PatSnap |
| `linkfox-zhihuiya-bibliography` | Look up patent bibliographic data (applicant, inventor, classification) |
| `linkfox-zhihuiya-cited-by` | Find patents that cite a given patent |
| `linkfox-zhihuiya-cited-references` | Get the reference list cited by a patent |
| `linkfox-zhihuiya-claim-data` | Retrieve patent claim text and structure |
| `linkfox-zhihuiya-claim-translated` | Get translated patent claims from PatSnap |
| `linkfox-zhihuiya-description` | Retrieve full patent description text |
| `linkfox-zhihuiya-description-translated` | Get translated patent description from PatSnap |
| `linkfox-zhihuiya-fulltext-image` | Retrieve full-text images from a patent document |
| `linkfox-zhihuiya-legal-status` | Check patent legal status (granted, expired, pending, etc.) |
| `linkfox-zhihuiya-patent-family` | Look up INPADOC patent family members |
| `linkfox-zhihuiya-patent-image-search` | Search patents by image similarity |
| `linkfox-zhihuiya-pdf` | Download patent full-text PDF document |
| `linkfox-zhihuiya-simple-bibliography` | Get simplified patent metadata (title, date, status) |

### Eureka Patent

| Skill | Description |
| --- | --- |
| `linkfox-eureka-abstract-image` | Eureka Abstract Image |
| `linkfox-eureka-abstract-translated` | Eureka Abstract Translated |
| `linkfox-eureka-bibliography` | Eureka Bibliography |
| `linkfox-eureka-claim-data` | Eureka Claim Data |
| `linkfox-eureka-claim-translated` | Eureka Claim Translated |
| `linkfox-eureka-description` | Eureka Description |
| `linkfox-eureka-description-translated` | Eureka Description Translated |
| `linkfox-eureka-patent-family` | Eureka Patent Family |
| `linkfox-eureka-patent-image-search` | Eureka Patent Image Search |

### AI Multimodal

| Skill | Description |
| --- | --- |
| `linkfox-multimodal-extract-attributes` | Extract product attributes from images using AI |
| `linkfox-multimodal-generate-image` | Generate or edit product images with AI (text-to-image, background swap) |
| `linkfox-multimodal-product-similarity` | Compare product image similarity using AI vision |
| `linkfox-multimodal-recognize-image` | Recognize and describe image content with AI (OCR, visual analysis) |

### Other Tools

| Skill | Description |
| --- | --- |
| `linkfox-ehunt-etsy-category-search` | Ehunt Etsy Category Search |
| `linkfox-ehunt-etsy-product-query` | Ehunt Etsy Product Query |
| `linkfox-ehunt-etsy-store-query` | Ehunt Etsy Store Query |
| `linkfox-lingxing-erp` | Lingxing Erp |
| `linkfox-product-title-analyze` | Analyze and optimize Amazon product listing titles |
| `linkfox-tsearch-web-search` | Search the web for market research and trending topics |
| `linkfox-wallysmarter-product-detail` | Walmart product detail with historical pricing and sales trends via WallySmarter |

## Requirements

- **Python 3.x** — All scripts use only the standard library. No additional dependencies required.
- **Environment variable** `LINKFOXAGENT_API_KEY` must be set before use.

## Compatible Platforms

Built on the [Agent Skills](https://agentskills.io) open standard:

| Platform | Status |
| --- | --- |
| Claude Code | Supported |
| OpenClaw | Supported |
| Cursor | Supported |
| GitHub Copilot | Supported |
| VS Code Copilot | Supported |
| Gemini CLI | Supported |
| OpenHands | Supported |


## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
