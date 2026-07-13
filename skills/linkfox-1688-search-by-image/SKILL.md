---
name: linkfox-1688-search-by-image
description: 1688平台以图搜图，通过商品图片精准检索外观相似或同款的1688货源，返回标题、价格、起批量、月销量、复购率、交易评分等核心数据。当用户提到1688以图搜图、1688找货源、以图找同款、跨境找工厂、1688识图、图片找货源、找相似货源、image search 1688、find supplier by image时触发此技能。即使用户未明确提及"以图搜图"，只要用户提供了图片URL并希望在1688上查找匹配或相似的货源商品，也应触发此技能。
---

# 1688 Image-Based Product Search

This skill performs visual product searches on the 1688 platform using an image URL, helping cross-border sellers find visually similar supplier products for sourcing.

## Core Concepts

1688 Image Search uses visual recognition to find products with similar appearance on the 1688 wholesale marketplace. It returns supplier product data including title, price, minimum order quantity, monthly sales, repurchase rate, trade score, and seller identity badges.

## Data Fields

| Field | Description |
|-------|-------------|
| offerId | Product ID on 1688 |
| title | Product title |
| imageUrl | Product main image |
| price | Wholesale price (CNY) |
| consignPrice | Dropship price (CNY) |
| salesQuantity | Monthly sales volume |
| estimatedSalesAmount | Estimated monthly revenue |
| quantityBegin | Minimum order quantity |
| repurchaseRate | Repurchase rate |
| tradeScore | Product trade score |
| compositeServiceScore | Composite service experience score |
| sellerIdentities | Seller identity (超级工厂/实力商家/诚信通会员) |
| offerIdentities | Product badge (严选) |
| sendGoodsAddressText | Shipping origin |
| deliveryTime | Delivery time (24/48 hours) |
| isOnePsale | Supports dropshipping (是/否) |
| isJxhy | Premium sourcing (是/否) |
| hasPromotion | Has promotion (是/否) |
| isPatentProduct | Patent product (是/否) |

## Parameter Guide

**Image Rules:**
1. Only png, jpg, jpeg formats are supported. webp, gif, and other formats are NOT supported.
2. Base64 string must be pure encoded content WITHOUT the `data:image/jpeg;base64,` prefix.
3. Image source — one of imageUrl, imageBase64, or imageId must be provided (at least one required).

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| imageUrl | Conditional | - | Public image URL (max 1000 chars). Only png/jpg/jpeg formats supported |
| imageBase64 | Conditional | - | Pure Base64 encoded image string, without `data:image/...;base64,` prefix. Only png/jpg/jpeg supported |
| imageId | Conditional | - | 1688 image ID from previous search result (speeds up pagination) |
| page | No | 1 | Page number, starting from 1 |
| pageSize | No | 20 | Results per page (1-50) |
| priceStart | No | - | Min price filter (CNY) |
| priceEnd | No | - | Max price filter (CNY) |
| filter | No | - | Filter conditions, comma-separated (see supported filters below) |
| sort | No | {"monthSold":"desc"} | Sort as JSON: {field: direction} (see supported sort fields below) |
| keyword | No | - | Keyword to further filter results |
| productCollectionId | No | - | Product collection ID (see supported IDs below) |

### Supported Filters

Multiple filters can be combined with commas (e.g. `1688Selection,totalEpScoreLv1,qrr0`).

| Filter Value | Description |
|--------------|-------------|
| 1688Selection | 1688严选 |
| certifiedFactory | 认证工厂 |
| totalEpScoreLv1 | 综合体验分5星 |
| totalEpScoreLv2 | 综合体验分4星 |
| totalEpScoreLv3 | 综合体验分3星 |
| totalEpScoreLv4 | 综合体验分2星 |
| qrr0 | 无品质退款 |
| qrr1 | 品质退款率<1% |
| qrr5 | 品质退款率<5% |
| qrr10 | 品质退款率<10% |
| shipInToday | 当日发货 |
| shipIn24Hours | 24小时发货 |
| shipIn48Hours | 48小时发货 |
| noReason7DReturn | 7天无理由退货 |
| isOnePsale | 一件代发 |
| isOnePsaleFreePost | 一件代发包邮 |
| new7 | 7天内新品 |
| new30 | 30天内新品 |
| isQqyx | 全球严选 |
| JPFL | 日本专线 |
| USFL | 美国专线 |
| KRFL | 韩国专线 |
| VNFL | 越南专线 |
| SAFL | 沙特专线 |
| RUFL | 俄罗斯专线 |
| KZFL | 哈萨克斯坦专线 |
| HKFL | 香港专线 |
| MOFL | 澳门专线 |
| TWFL | 台湾专线 |

### Supported Sort Fields

| Field | Direction | Description |
|-------|-----------|-------------|
| price | asc/desc | Price ascending/descending |
| monthSold | asc/desc | Monthly sales ascending/descending |
| rePurchaseRate | asc/desc | Repurchase rate ascending/descending |

Sort format example: `{"price":"asc"}` for price low to high.

### Supported Product Collection IDs

| ID | Usage |
|----|-------|
| 262105288 | 跨境货盘 |
| 262105286 | 跨境货盘 |
| 262105253 | 跨境货盘 |
| 262105281 | 跨境货盘 |
| 262105280 | 跨境货盘 |
| 262105277 | 跨境货盘 |
| 262105276 | 跨境货盘 |
| 262105274 | 跨境货盘 |
| 262105269 | 跨境货盘 |
| 262185282 | 跨境货盘 |

## 调用方式

- **API 端点**：`POST /alibaba1688/imageSearch`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/alibaba1688_image_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-1688-search-by-image-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## Local Image Upload

This tool requires a **publicly accessible image URL**. If the user provides a local image file path, you must upload it first to obtain a public URL.

Run the upload script:
```bash
python scripts/upload_image.py /path/to/local/image.png
```

The script will return a public URL (valid for 24 hours) that can be used as the imageUrl parameter.

## Usage Examples

**1. Basic image search**
```
在1688搜索与图片相似的商品，图片地址为 https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg
```

**2. Search with filters**
```
在1688搜索与图片相似的商品，图片地址为 https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg，查询第1页，筛选1688严选，并按价格从高到低排序
```

**3. Search with sorting**
```
在1688搜索与图片相似的商品，图片地址为 https://example.com/product.jpg，按价格从高到低排序
```

**4. Paginated search**
```
在1688搜索与图片相似的商品，图片地址为 https://example.com/product.jpg，查询第2页，每页50条
```

**5. Price range filter**
```
在1688搜索与图片相似的商品，图片地址为 https://example.com/product.jpg，价格区间10-100元
```

## Display Rules

1. **Present data clearly**: Show results in a structured table with key columns: product image, title, price, dropship price, monthly sales, minimum order quantity, repurchase rate, and seller identity
2. **Image display**: When the response includes imageUrl for products, display them inline for visual comparison
3. **Price display**: Always show price in CNY (¥) format
4. **Seller badges**: Display seller identity badges (超级工厂/实力商家/诚信通会员) and product badges (严选) prominently
5. **Result count**: Always inform the user of total results and current page/total pages
6. **Pagination hint**: When more pages are available, suggest the user can request the next page
7. **Filter/sort limitation**: If the user requests a sort or filter not in the supported list, do NOT attempt any workaround. Inform the user of the supported options
8. **No secondary processing**: Results are real-time and not stored in a database, so secondary SQL/data processing is not available

## Important Limitations

1. **Data real-time nature**: Results are live searches, not stored in any database. Cannot use `_dataQuery_executeDynamicQuery` for secondary processing.
2. **Logic constraint**: If the user requests sort or filter conditions not in the preset supported list, do NOT call any other tool or logic to compensate.
3. **Image input**: One of imageUrl, imageBase64, or imageId is required. For page > 1, prefer passing imageId from the first page result to speed up queries.
4. **Image format**: Only png, jpg, jpeg are supported. webp, gif, and other formats will be rejected.
5. **Base64 format**: The imageBase64 value must be the raw Base64 string only — do NOT include the `data:image/jpeg;base64,` prefix.
6. **Page size**: Maximum 50 results per page.

## User Expression & Scenario Quick Reference

**Applicable** -- Visual product sourcing scenarios on 1688:

| User Says | Scenario |
|-----------|----------|
| "1688以图搜图" / "用图片找1688货源" | Basic image search |
| "帮我在1688找这个图片的同款" | Find same-style products |
| "跨境找工厂，图片是..." | Cross-border supplier sourcing |
| "这个Amazon产品在1688有没有货源" | Reverse sourcing from Amazon image |
| "筛选1688严选的相似商品" | Filtered image search |
| "按月销量排序找相似货源" | Sorted image search |
| "查看第2页结果" | Pagination |

**Not applicable** -- Needs beyond 1688 image search:

- Text/keyword-based 1688 search (use 店雷达-1688选品库)
- 1688 product rankings/trending (use 店雷达-1688商品榜单)
- Amazon image search (use 亚马逊前端-以图搜图)
- Image generation or editing
- Product review analysis
- Price history or trend analysis

**Boundary judgment**: When users say "找货源" or "找同款", if they provide an image URL and the intent is to find visually similar products on 1688, this skill applies. If they want keyword-based search or ranking data on 1688, use the 店雷达 tools instead.

## 积分消耗规则

消耗 4.5 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
