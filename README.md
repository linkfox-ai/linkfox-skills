# LinkFox Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-orange)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/skills-163-brightgreen)](#skills-catalog)

**LinkFox Skills** is an AI skill set designed for cross-border e-commerce. It provides 163 API-driven skills covering product research, competitor analysis, keyword tracking, Amazon Ads reporting, patent search, compliance detection, and more.

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
| `linkfox-amazon-ads-sp-insights-report` | Retrieve Sponsored Products audience performance and search-term impression share/rank reports through the beta Amazon Ads Reporting API v1 |
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
| `linkfox-amazon-store-external-fulfillment` | Amazon Store External Fulfillment |
| `linkfox-amazon-store-fba` | Amazon Store Fba |
| `linkfox-amazon-store-feeds` | Amazon Store Feeds |
| `linkfox-amazon-store-fulfillment-inbound` | Manage Amazon FBA inbound plans, packing, placement, transportation, shipments, delivery windows, labels, and bills of lading with Fulfillment Inbound v2024-03-20 and retained v0 operations |
| `linkfox-amazon-store-fulfillment-outbound` | Manage Amazon Multi-Channel Fulfillment quotes, previews, orders, tracking, sandbox status simulations, and related invoice-header discovery with Fulfillment Outbound v2026-07-04 |
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
| `linkfox-echotik-batch-video-detail` | Batch-fetch detailed TikTok video metrics (views with 1d/7d/30d breakdown, likes with increments, comments, shares, favorites, video sales and GMV, duration, resolution, publish date, creator, and ad/AI/selling flags) by video ID or video URL |
| `linkfox-echotik-get-video-download-url` | Resolve a TikTok video URL into no-watermark and watermarked download links, plus playback URL and cover images |
| `linkfox-echotik-list-new-product-rank` | Echotik List New Product Rank |
| `linkfox-echotik-list-product` | Echotik List Product |
| `linkfox-echotik-list-seller` | List and filter TikTok Shop sellers (stores) by region, category, 30-day GMV, sales trend, listing date, and local/cross-border type, returning store sales, GMV, followers, ratings, reviews, and influencer/video/livestream counts across 16 marketplaces |
| `linkfox-echotik-list-seller-product` | List the in-store products of a single TikTok Shop seller by sellerId, returning per-product title, price, multi-period (1d/7d/15d/30d/60d/90d/total) sales and GMV, rating, reviews, commission rate, listing date, and sales channel |
| `linkfox-echotik-list-video` | List and filter TikTok videos by region, creator, product, category, views, duration, publish time, and ad/AI/selling flags, returning views, likes, comments, shares, favorites, video sales, and GMV across 16 marketplaces |
| `linkfox-echotik-list-video-rank` | Query dated TikTok video rankings by date, region, rank type, and ranking metric, returning views, likes, comments, shares, favorites, video sales, and GMV across 16 marketplaces |
| `linkfox-echotik-product-video` | Query promotional videos for a TikTok product with engagement and sales metrics |
| `linkfox-echotik-seller-detail` | Fetch the full profile of a single TikTok Shop seller (store) by sellerId, returning total and multi-period (1d/7d/30d/90d) sales and GMV, followers, rating, reviews, fulfillment rates, product counts, price range, categories, and influencer/video/livestream counts across 16 marketplaces |

### TikTok (FastMoss)

| Skill | Description |
| --- | --- |
| `linkfox-fastmoss-product-rank-top-selling` | Fastmoss Product Rank Top Selling |
| `linkfox-fastmoss-product-search` | Search TikTok products with keyword, category, sales, and creator filters |

### TikTok (Kalodata)

| Skill | Description |
| --- | --- |
| `linkfox-kalodata-tiktok-creator` | Browse TikTok Shop creator leaderboards and fetch detailed creator profile and performance data by creator ID via the Kalodata data source |
| `linkfox-kalodata-tiktok-livestream` | Browse TikTok Shop livestream rankings by region, currency, language, and date range and fetch detailed livestream data by livestream ID via the Kalodata data source |
| `linkfox-kalodata-tiktok-product` | Browse TikTok Shop product rankings by region, currency, language, and date range and fetch detailed product data by product ID via the Kalodata data source |
| `linkfox-kalodata-tiktok-shop` | Browse TikTok Shop store leaderboards and fetch detailed store data by shop ID via the Kalodata data source |
| `linkfox-kalodata-tiktok-video` | Browse top TikTok Shop video leaderboards and fetch detailed shoppable video metrics by video ID via the Kalodata data source |

### Ozon (Mpstats)

| Skill | Description |
| --- | --- |
| `linkfox-mpstats-ozon-brand-products` | Drill into all Ozon SKUs under a brand with filters, sorting, and currency conversion via MPSTATS |
| `linkfox-mpstats-ozon-category-products` | Drill into all Ozon SKUs under a Russian category path with filters for niche mining via MPSTATS |
| `linkfox-mpstats-ozon-product-detail` | Fetch one full Ozon product card by productId (price, sales, stock, rating, lost profit) via MPSTATS |
| `linkfox-mpstats-ozon-product-search` | Search Ozon (Russia) products by Russian keyword, SKU list, brand, or seller - the MPSTATS Ozon discovery entry point |
| `linkfox-mpstats-ozon-product-trend` | Daily time-series for a single Ozon SKU (sales, price, stock, optional search visibility) via MPSTATS |
| `linkfox-mpstats-ozon-seller-products` | Drill into all Ozon SKUs under a seller ID for shop structure audits via MPSTATS |

### Google Trends

| Skill | Description |
| --- | --- |
| `linkfox-google-patent-search` | Search Google Patents by keyword, inventor, assignee, country, date, and status; returns publication numbers, titles, dates, CPC classifications, and PDF links |
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
| `linkfox-jiimore-get-niche-info-by-asin` | Jiimore Get Niche Info By Asin |
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
| `linkfox-sif-compliance-detection` | SIF design patent detection: find visually similar design-registration candidates from a product image, with optional title, region, source jurisdiction, Locarno and legal-status filters; candidates do not establish infringement |
| `linkfox-sif-keyword-overview` | Get keyword search volume, competition, and CPC overview |
| `linkfox-sif-keyword-summary` | Sif Keyword Summary |

### Sorftime

| Skill | Description |
| --- | --- |
| `linkfox-sorftime-amazon-product-detail` | Sorftime Amazon Product Detail |
| `linkfox-sorftime-amazon-product-query` | Sorftime Amazon Product Query |
| `linkfox-sorftime-walmart-category-market` | Retrieve the Walmart US category tree, match natural-language category names, and analyze category markets with returned Best Seller product data via Sorftime |
| `linkfox-sorftime-walmart-keyword-research` | Research Walmart keywords, product-keyword relationships, related terms, and saved keyword folders via Sorftime |
| `linkfox-sorftime-walmart-product-analysis` | Find Walmart products by natural-language name and query product details, trends, and variant sales via Sorftime |

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
| `linkfox-zhihuiya-retrieval-patent-search` | Search patents using PatSnap Analytics query expressions (e.g. TACD: keyword), returning patent IDs, publication numbers, and total hit count |
| `linkfox-zhihuiya-simple-bibliography` | Get simplified patent metadata (title, date, status) |
| `linkfox-zhihuiya-utility-patent-image-search` | Zhihuiya Utility Patent Image Search |

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
| `linkfox-1688-procurement` | Run authorized 1688 procurement workflows including OAuth checks, SKU and address lookup, order preview, guarded order creation, payment links, order status, logistics, cancellation, and receipt confirmation |
| `linkfox-1688-product-detail` | Retrieve 1688 product details by offer ID with one-piece retail prices, wholesale tiers for two or more units, SKU stock, logistics, and supplier data |
| `linkfox-1688-search-by-image` | Find similar 1688 supplier products using image-based visual search |
| `linkfox-ai-mode-google-search` | Ai Mode Google Search |
| `linkfox-aigc-clothing-suite` | Generate apparel model, selling-point, seeding, size, white-background and A+ images. |
| `linkfox-aigc-image-edit` | Edit one source image with an instruction and an explicitly chosen image model. |
| `linkfox-aigc-image-to-video` | Generate video from one image or multiple images with optional reference videos and templates. |
| `linkfox-aigc-imagegen` | Aigc Imagegen |
| `linkfox-aigc-imagegen-brand-gene-extract` | Aigc Imagegen Brand Gene Extract |
| `linkfox-aigc-imagegen-cloth` | Aigc Imagegen Cloth |
| `linkfox-aigc-imagegen-product` | Aigc Imagegen Product |
| `linkfox-aigc-multi-image-edit` | Combine multiple reference images into one coherent edited visual. |
| `linkfox-aigc-product-suite` | Generate product selling-point, scene, close-up, white-background and A+ images from reference assets. |
| `linkfox-aigc-sales-video` | Create product sales videos from a supplied script and reference images. |
| `linkfox-aigc-textgen` | Aigc Textgen |
| `linkfox-aigc-video-edit` | Edit a source video with an instruction and optional reference images. |
| `linkfox-aigc-video-reclone` | Recreate a reference video using product images, target market and language. |
| `linkfox-aigc-video-translate` | Translate speech in an existing video into a target language with optional lip synchronization. |
| `linkfox-aigc-videogen` | Aigc Videogen |
| `linkfox-aigc-videogen-multi` | Aigc Videogen Multi |
| `linkfox-chuhaijiang-tiktok-ads` | Research public TikTok ads and creative assets with filtered discovery, detailed performance data, promoted-product relationships, content-structure analysis, and embeddings |
| `linkfox-chuhaijiang-tiktok-creator` | Research TikTok creators with multi-filter search, detailed profiles, related livestream/product/video drill-downs, and agency, commerce, and follower-growth rankings |
| `linkfox-chuhaijiang-tiktok-live` | Research public TikTok livestream commerce with multi-filter discovery, detailed room and performance metrics, and products sold in each livestream |
| `linkfox-chuhaijiang-tiktok-product` | Research TikTok Shop products with multi-filter search, detailed metrics, creator/live/video/review relationships, three rankings, and image similarity search |
| `linkfox-chuhaijiang-tiktok-shop` | Research TikTok Shop stores with multi-filter discovery, detailed profiles, creator/product/video relationships, and most-promoted and top-selling rankings |
| `linkfox-chuhaijiang-tiktok-video` | Research public TikTok videos with multi-filter discovery, detailed performance profiles, promoted-product relationships, and public comment drill-downs |
| `linkfox-damai-mercado-market-intelligence` | Research Mercado Libre markets across Mexico, Brazil, Argentina, Chile, and Colombia with Damai category, industry, product, sales-trend, image-similarity, and review data through the LinkFox gateway |
| `linkfox-etsy-category-search` | Etsy Category Search |
| `linkfox-etsy-product-detail` | Retrieve one public Etsy listing with pricing, images, variants, inventory, shipping, shop, ratings, and review data |
| `linkfox-etsy-product-query` | Etsy Product Query |
| `linkfox-etsy-store-query` | Etsy Store Query |
| `linkfox-geekbi-temu-market-research` | Research Temu category opportunities and buyer-demand keywords by marketplace, demand, revenue, price, supply, semi-managed penetration, and daily, weekly, or monthly growth |
| `linkfox-geekbi-temu-product` | Search and filter Temu products and retrieve product details and 30-day history via GeekBI, with internal region and category ID resolution |
| `linkfox-geekbi-temu-search-by-image` | Find visually similar or matching Temu products from an image for product research and competitor discovery |
| `linkfox-geekbi-temu-shop` | Search and benchmark Temu shops by marketplace, category, sales, revenue, ratings, followers, product count, average order value, hosting mode, and opening date, with internal region and category ID resolution |
| `linkfox-lingxing-erp` | Lingxing Erp |
| `linkfox-maidalv-product-tro-detection` | Detect product TRO (Temporary Restraining Order) and trademark/patent/copyright infringement risk from a product image, returning risk level, infringement items, TRO plaintiff info, and an AI legal report |
| `linkfox-mercado-product-selection` | Query Mercado Libre (Mexico, Brazil, Argentina, Chile, Colombia) product, catalog, keyword, category, trend, seller, review, exchange-rate, and plan-usage data via 24 tools through the LinkFox gateway |
| `linkfox-product-title-analyze` | Analyze and optimize Amazon product listing titles |
| `linkfox-seerfar-ozon-category-search` | List an Ozon category's products by categoryId with category aggregates (total sales, total revenue, average price, rating, seasonality) and per-product sales, price, rating, reviews, brand, seller, and fulfillment via Seerfar |
| `linkfox-seerfar-ozon-keyword-back-search` | Reverse-lookup Ozon (and Wildberries) search keywords by a product SKU list (organic and ad terms), filtered by search volume, growth, competition, natural/ad rank, exposure, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-keyword-mining` | Mine Ozon (and Wildberries) keywords around a seed term, filtered by search volume, growth, competition, price, relevancy, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-market-keyword-search` | Search and filter Ozon (and Wildberries) market keywords by search volume, growth, competition, price, and conversion metrics via Seerfar |
| `linkfox-seerfar-ozon-product-detail-search` | Fetch full detail of a single Ozon product by SKU (title, price, rating, reviews, QA, windowed total + daily-average + daily-trend sales, revenue, stock, category rank history, brand, seller, fulfillment, weight, listing age) via Seerfar |
| `linkfox-seerfar-ozon-product-report-search` | Screen and filter Ozon products by sales, revenue, growth, conversion, price, rating, reviews, brand, seller, fulfillment, and listing-age metrics via Seerfar - the Ozon product report / selection screener returning per-product SKU, price (RUB), sales, revenue, conversion, rating, reviews, brand, seller, fulfillment, and listing age |
| `linkfox-seerfar-ozon-shop-search` | List an Ozon shop's product catalog by seller ID with 30-day sales, price, rating, weight, fulfillment, seller type, return rate, and shop total sales via Seerfar |
| `linkfox-shopee-product-detail` | Retrieve one public Shopee listing across eight marketplaces with available pricing, sales, stock, variants, media, categories, shop, and rating data |
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
| `linkfox-smart-table` | Smart Table |
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
| `linkfox-tiktok-shop-product-detail` | Retrieve one public TikTok Shop product with pricing, sales, SKU inventory, media, seller, reviews, shipping, and promotion data |
| `linkfox-tsearch-search` | Tsearch Search |
| `linkfox-wallysmarter-product-detail` | Walmart product detail with historical pricing and sales trends via WallySmarter |
| `linkfox-wb-1688-procurement` | Wb 1688 Procurement |
| `linkfox-wb-1688-sourcing` | Wb 1688 Sourcing |
| `linkfox-wb-amazon-ads` | Wb Amazon Ads |
| `linkfox-wb-amazon-business-insight` | Wb Amazon Business Insight |
| `linkfox-wb-amazon-front-data` | Wb Amazon Front Data |
| `linkfox-wb-amazon-sp-api` | Wb Amazon Sp Api |
| `linkfox-wb-damai-mercado-intelligence` | Wb Damai Mercado Intelligence |
| `linkfox-wb-e-commerce-compliance` | Wb E Commerce Compliance |
| `linkfox-wb-ebay-product-selection` | Wb Ebay Product Selection |
| `linkfox-wb-echotik-tiktok` | Wb Echotik Tiktok |
| `linkfox-wb-etsy-data` | Wb Etsy Data |
| `linkfox-wb-fastmoss-tiktok` | Wb Fastmoss Tiktok |
| `linkfox-wb-google-tools` | Wb Google Tools |
| `linkfox-wb-jiimore` | Wb Jiimore |
| `linkfox-wb-jungle-scout` | Wb Jungle Scout |
| `linkfox-wb-kalodata-tiktok` | Wb Kalodata Tiktok |
| `linkfox-wb-keepa` | Wb Keepa |
| `linkfox-wb-linkfox-aigc` | Wb Linkfox Aigc |
| `linkfox-wb-maidalv-product-tro-detection` | Wb Maidalv Product Tro Detection |
| `linkfox-wb-mercado-selection` | Wb Mercado Selection |
| `linkfox-wb-mpstats-ozon` | Wb Mpstats Ozon |
| `linkfox-wb-ruiguan-detection` | Wb Ruiguan Detection |
| `linkfox-wb-seerfar-ozon` | Wb Seerfar Ozon |
| `linkfox-wb-sellersprite` | Wb Sellersprite |
| `linkfox-wb-shopee-official-api` | Wb Shopee Official Api |
| `linkfox-wb-shopee-product-selection` | Wb Shopee Product Selection |
| `linkfox-wb-shopify-data` | Wb Shopify Data |
| `linkfox-wb-sif-search-intelligence` | Wb Sif Search Intelligence |
| `linkfox-wb-smart-table` | Wb Smart Table |
| `linkfox-wb-sorftime` | Wb Sorftime |
| `linkfox-wb-sorftime-walmart` | Wb Sorftime Walmart |
| `linkfox-wb-temu-data` | Wb Temu Data |
| `linkfox-wb-tiktok-official-api` | Wb Tiktok Official Api |
| `linkfox-wb-tiktok-official-video-api` | Wb Tiktok Official Video Api |
| `linkfox-wb-walmart-product-selection` | Wb Walmart Product Selection |
| `linkfox-wb-workflow` | Wb Workflow |
| `linkfox-workflow` | Workflow |


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

## Download History

[![Download History](https://skill-history.com/chart/linkfox-ai/linkfoxagent.svg)](https://skill-history.com/linkfox-ai/linkfoxagent)
