# LinkFox Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-orange)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/skills-117-brightgreen)](#skills-catalog)

**LinkFox Skills** is an AI skill set designed for cross-border e-commerce. It provides 117 API-driven skills covering product research, competitor analysis, keyword tracking, Amazon Ads reporting, patent search, compliance detection, and more.

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

1. Follow the [LinkFoxAgent API Setup Guide](https://skill.linkfox.com/linkfoxskills/guide.htm) to obtain your key.
2. Set the environment variable:
   ```bash
   export LINKFOXAGENT_API_KEY=your-key-here
   ```

## Skills Catalog


### Amazon

| Skill | Description |
| --- | --- |
| `linkfox-aba-intelligent-query` | Aba Intelligent Query |
| `linkfox-amazon-ads-auth` | Amazon Ads OAuth authorization, profile discovery, and access-token management |
| `linkfox-amazon-ads-manager` | Manage Amazon Ads SP/SB/SD entities: list, create, and update campaigns, ad groups, keywords, targets, product ads, and budget rules |
| `linkfox-amazon-ads-report` | One-stop Amazon Ads SP/SB reporting: request, poll, download, and auto-extract |
| `linkfox-amazon-alexa-search` | Amazon Alexa Search |
| `linkfox-amazon-opportunity-report-by-keyword` | Amazon Opportunity Report By Keyword |
| `linkfox-amazon-opportunity-search-by-metrics` | Amazon Opportunity Search By Metrics |
| `linkfox-amazon-policy-feed` | Query Amazon latest policy and regulation feed with AI Chinese summaries, and read full article bodies by record ID |
| `linkfox-amazon-product-detail` | Get detailed Amazon product info by ASIN (price, BSR, bullets, etc.) |
| `linkfox-amazon-reviews-list` | Amazon Reviews List |
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

### TikTok (EchoTik)

| Skill | Description |
| --- | --- |
| `linkfox-echotik-batch-product-detail` | Batch-fetch detailed TikTok Shop product metrics (multi-period sales and GMV, live, video, influencer, and views data) by product ID or URL |
| `linkfox-echotik-get-video-download-url` | Resolve a TikTok video URL into no-watermark and watermarked download links, plus playback URL and cover images |
| `linkfox-echotik-list-new-product-rank` | Echotik List New Product Rank |
| `linkfox-echotik-list-product` | Echotik List Product |
| `linkfox-echotik-product-video` | Query promotional videos for a TikTok product with engagement and sales metrics |

### TikTok (FastMoss)

| Skill | Description |
| --- | --- |
| `linkfox-fastmoss-product-rank-top-selling` | Fastmoss Product Rank Top Selling |
| `linkfox-fastmoss-product-search` | Search TikTok products with keyword, category, sales, and creator filters |

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
| `linkfox-google-trend-get-trend-by-keys` | Google Trend Get Trend By Keys |
| `linkfox-google-trend-get-trend-by-time` | Google Trend Get Trend By Time |

### Keepa

| Skill | Description |
| --- | --- |
| `linkfox-keepa-product-request` | Keepa Product Request |
| `linkfox-keepa-product-search` | Advanced Amazon product search with Keepa data (BSR, sales, price filters) |
| `linkfox-keepa-product-series` | Keepa Product Series |

### Jiimore

| Skill | Description |
| --- | --- |
| `linkfox-jiimore-get-niche-info` | Jiimore Get Niche Info |
| `linkfox-jiimore-get-niche-info-by-keyword` | Jiimore Get Niche Info By Keyword |
| `linkfox-jiimore-get-niche-review-from-keyword` | Jiimore Get Niche Review From Keyword |
| `linkfox-jiimore-page-asins-by-asin` | Jiimore Page Asins By Asin |
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
| `linkfox-sellersprite-competitor-lookup` | Sellersprite Competitor Lookup |
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
| `linkfox-sif-keyword-summary` | Sif Keyword Summary |

### Sorftime

| Skill | Description |
| --- | --- |
| `linkfox-sorftime-amazon-product-detail` | Sorftime Amazon Product Detail |
| `linkfox-sorftime-amazon-product-query` | Sorftime Amazon Product Query |

### Shopee (YouYing)

| Skill | Description |
| --- | --- |
| `linkfox-youying-shopee-get-product-infos` | Youying Shopee Get Product Infos |

### Compliance (Ruiguan)

| Skill | Description |
| --- | --- |
| `linkfox-ruiguan-copyright-detection` | Ruiguan Copyright Detection |
| `linkfox-ruiguan-detection-patent-design` | Ruiguan Detection Patent Design |
| `linkfox-ruiguan-gun-parts-search` | Ruiguan Gun Parts Search |
| `linkfox-ruiguan-text-trademark-detection` | Ruiguan Text Trademark Detection |
| `linkfox-ruiguan-trademark-graphic-detection` | Ruiguan Trademark Graphic Detection |
| `linkfox-ruiguan-utility-patent-detection` | Ruiguan Utility Patent Detection |

### PatSnap (Zhihuiya) Patent

| Skill | Description |
| --- | --- |
| `linkfox-zhihuiya-abstract-data-translated` | Zhihuiya Abstract Data Translated |
| `linkfox-zhihuiya-abstract-image` | Retrieve patent abstract images from PatSnap |
| `linkfox-zhihuiya-bibliography` | Look up patent bibliographic data (applicant, inventor, classification) |
| `linkfox-zhihuiya-claim-data` | Retrieve patent claim text and structure |
| `linkfox-zhihuiya-claim-data-translated` | Zhihuiya Claim Data Translated |
| `linkfox-zhihuiya-description-data` | Zhihuiya Description Data |
| `linkfox-zhihuiya-description-data-translated` | Zhihuiya Description Data Translated |
| `linkfox-zhihuiya-fulltext-image` | Retrieve full-text images from a patent document |
| `linkfox-zhihuiya-legal-status` | Check patent legal status (granted, expired, pending, etc.) |
| `linkfox-zhihuiya-patent-cited` | Zhihuiya Patent Cited |
| `linkfox-zhihuiya-patent-family` | Look up INPADOC patent family members |
| `linkfox-zhihuiya-patent-forward-citation` | Zhihuiya Patent Forward Citation |
| `linkfox-zhihuiya-patent-image-search` | Search patents by image similarity |
| `linkfox-zhihuiya-pdf-data` | Zhihuiya Pdf Data |
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
| `linkfox-1688-search-by-image` | Find similar 1688 supplier products using image-based visual search |
| `linkfox-ai-mode-google-search` | Ai Mode Google Search |
| `linkfox-aigc-imagegen` | Aigc Imagegen |
| `linkfox-aigc-imagegen-brand-gene-extract` | Aigc Imagegen Brand Gene Extract |
| `linkfox-aigc-imagegen-cloth` | Aigc Imagegen Cloth |
| `linkfox-aigc-imagegen-product` | Aigc Imagegen Product |
| `linkfox-aigc-textgen` | Aigc Textgen |
| `linkfox-aigc-videogen` | Aigc Videogen |
| `linkfox-aigc-videogen-multi` | Aigc Videogen Multi |
| `linkfox-etsy-category-search` | Etsy Category Search |
| `linkfox-etsy-product-query` | Etsy Product Query |
| `linkfox-etsy-store-query` | Etsy Store Query |
| `linkfox-lanjing-mercado-product-selection` | Query Mercado Libre (Mexico, Brazil, Argentina, Chile, Colombia) product, catalog, keyword, category, trend, seller, review, exchange-rate, and plan-usage data via 24 Lanjing tools through the LinkFox gateway |
| `linkfox-lingxing-erp` | Lingxing Erp |
| `linkfox-product-title-analyze` | Analyze and optimize Amazon product listing titles |
| `linkfox-seerfar-ozon-category-search` | List an Ozon category's products by categoryId with category aggregates (total sales, total revenue, average price, rating, seasonality) and per-product sales, price, rating, reviews, brand, seller, and fulfillment via Seerfar |
| `linkfox-seerfar-ozon-keyword-back-search` | Reverse-lookup Ozon (and Wildberries) search keywords by a product SKU list (organic and ad terms), filtered by search volume, growth, competition, natural/ad rank, exposure, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-keyword-mining` | Mine Ozon (and Wildberries) keywords around a seed term, filtered by search volume, growth, competition, price, relevancy, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-market-keyword-search` | Search and filter Ozon (and Wildberries) market keywords by search volume, growth, competition, price, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-product-detail-search` | Fetch full detail of a single Ozon product by SKU (title, price, rating, reviews, QA, windowed total + daily-average + daily-trend sales, revenue, stock, category rank history, brand, seller, fulfillment, weight, listing age) via Seerfar |
| `linkfox-seerfar-ozon-product-report-search` | Screen and filter Ozon products by sales, revenue, growth, conversion, price, rating, reviews, brand, seller, fulfillment, and listing-age metrics via Seerfar - the Ozon product report / selection screener returning per-product SKU, price (RUB), sales, revenue, conversion, rating, reviews, brand, seller, fulfillment, and listing age |
| `linkfox-seerfar-ozon-shop-search` | List an Ozon shop's product catalog by seller ID with 30-day sales, price, rating, weight, fulfillment, seller type, return rate, and shop total sales via Seerfar |
| `linkfox-shopee-store-account-health` | Shopee Store Account Health |
| `linkfox-shopee-store-add-on-deal` | Shopee Store Add On Deal |
| `linkfox-shopee-store-ads` | Shopee Store Ads |
| `linkfox-shopee-store-ams` | Shopee Store Ams |
| `linkfox-shopee-store-auth` | Shopee Store Auth |
| `linkfox-shopee-store-bundle-deal` | Shopee Store Bundle Deal |
| `linkfox-shopee-store-discount` | Shopee Store Discount |
| `linkfox-shopee-store-fbs` | Shopee Store Fbs |
| `linkfox-shopee-store-first-mile` | Shopee Store First Mile |
| `linkfox-shopee-store-follow-prize` | Shopee Store Follow Prize |
| `linkfox-shopee-store-global-product` | Shopee Store Global Product |
| `linkfox-shopee-store-livestream` | Shopee Store Livestream |
| `linkfox-shopee-store-logistics` | Shopee Store Logistics |
| `linkfox-shopee-store-media` | Shopee Store Media |
| `linkfox-shopee-store-media-space` | Shopee Store Media Space |
| `linkfox-shopee-store-merchant` | Shopee Store Merchant |
| `linkfox-shopee-store-orders` | Shopee Store Orders |
| `linkfox-shopee-store-payment` | Shopee Store Payment |
| `linkfox-shopee-store-product` | Shopee Store Product |
| `linkfox-shopee-store-public` | Shopee Store Public |
| `linkfox-shopee-store-push` | Shopee Store Push |
| `linkfox-shopee-store-returns` | Shopee Store Returns |
| `linkfox-shopee-store-sbs` | Shopee Store Sbs |
| `linkfox-shopee-store-shop` | Shopee Store Shop |
| `linkfox-shopee-store-shop-category` | Shopee Store Shop Category |
| `linkfox-shopee-store-shop-flash-sale` | Shopee Store Shop Flash Sale |
| `linkfox-shopee-store-top-picks` | Shopee Store Top Picks |
| `linkfox-shopee-store-video` | Shopee Store Video |
| `linkfox-shopee-store-voucher` | Shopee Store Voucher |
| `linkfox-shopify-product-query` | Shopify Product Query |
| `linkfox-shopify-store-query` | Shopify Store Query |
| `linkfox-temu-add-product-us` | Temu Add Product Us |
| `linkfox-temu-ads-eu` | Temu Ads Eu |
| `linkfox-temu-ads-global` | Temu Ads Global |
| `linkfox-temu-ads-us` | Temu Ads Us |
| `linkfox-temu-cancel-order-eu` | Temu Cancel Order Eu |
| `linkfox-temu-cancel-order-global` | Temu Cancel Order Global |
| `linkfox-temu-cancel-order-us` | Temu Cancel Order Us |
| `linkfox-temu-category-search` | Temu Category Search |
| `linkfox-temu-compliance-global` | Temu Compliance Global |
| `linkfox-temu-fulfillment-eu` | Temu Fulfillment Eu |
| `linkfox-temu-fulfillment-global` | Temu Fulfillment Global |
| `linkfox-temu-fulfillment-us` | Temu Fulfillment Us |
| `linkfox-temu-manage-product-eu` | Temu Manage Product Eu |
| `linkfox-temu-manage-product-global` | Temu Manage Product Global |
| `linkfox-temu-manage-product-us` | Temu Manage Product Us |
| `linkfox-temu-order-eu` | Temu Order Eu |
| `linkfox-temu-order-global` | Temu Order Global |
| `linkfox-temu-order-us` | Temu Order Us |
| `linkfox-temu-price-eu` | Temu Price Eu |
| `linkfox-temu-price-global` | Temu Price Global |
| `linkfox-temu-price-us` | Temu Price Us |
| `linkfox-temu-product-query` | Temu Product Query |
| `linkfox-temu-promotion-eu` | Temu Promotion Eu |
| `linkfox-temu-promotion-global` | Temu Promotion Global |
| `linkfox-temu-promotion-us` | Temu Promotion Us |
| `linkfox-temu-returns-refunds-eu` | Temu Returns Refunds Eu |
| `linkfox-temu-returns-refunds-global` | Temu Returns Refunds Global |
| `linkfox-temu-returns-refunds-us` | Temu Returns Refunds Us |
| `linkfox-temu-store-query` | Temu Store Query |
| `linkfox-temu-tax-eu` | Temu Tax Eu |
| `linkfox-tsearch-search` | Tsearch Search |
| `linkfox-wallysmarter-product-detail` | Walmart product detail with historical pricing and sales trends via WallySmarter |
| `linkfox-xiyou-dongcha` | Xiyou Insights Amazon ASIN and keyword analytics via LinkFox gateway (traffic scores, reverse ASIN lookup, rank trends, ABA weekly data) |


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
