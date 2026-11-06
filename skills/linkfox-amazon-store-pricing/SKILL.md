---
name: linkfox-amazon-store-pricing
description: 查询已授权亚马逊店铺的商品报价与竞争定价，支持按 ASIN 或卖家 SKU 查看价格、最低报价、批量报价、预期 Featured Offer 价格和竞争摘要。适用于价格对标、Buy Box 竞争力判断和定价研究；不适用于修改 Listing 售价、批量文件提交或未授权店铺的前台竞品采集。
---
# Amazon 店铺报价与竞争定价

## 适用范围

### 适用

查询已授权店铺在目标站点的 Product Pricing 数据，比较商品报价或评估 Featured Offer 竞争力。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看这些 ASIN 或 SKU 的当前价格 | 商品价格或竞争价格。 |
| 看这个商品的最低报价和购物车竞争 | 单商品报价，按需批量查询。 |
| 估算赢得 Featured Offer 的价格 | 预期 Featured Offer 价格（FOEP）。 |
| 看一组商品的竞争情况 | 竞争摘要。 |

### 边界

本技能只查询价格。修改刊登售价使用 `linkfox-amazon-store-listings`，批量文件提交使用对应 Feed 技能；店铺授权与选店依赖 `linkfox-amazon-store-auth`。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 商品价格（`getPricing`） | POST `/spApi/developerProxy` → 上游 GET，path：`products/pricing/v0/price` | `scripts/get_pricing.py` | 查询商品价格。 |
| 竞争价格（`getCompetitivePricing`） | POST `/spApi/developerProxy` → 上游 GET，path：`products/pricing/v0/competitivePrice` | `scripts/get_competitive_pricing.py` | 查询竞争价格。 |
| 单 SKU 报价（`getListingOffers`） | POST `/spApi/developerProxy` → 上游 GET，path：`products/pricing/v0/listings/{SellerSKU}/offers` | `scripts/get_listing_offers.py` | 查询单 SKU 报价。 |
| 单 ASIN 报价（`getItemOffers`） | POST `/spApi/developerProxy` → 上游 GET，path：`products/pricing/v0/items/{Asin}/offers` | `scripts/get_item_offers.py` | 查询单 ASIN 报价。 |
| 批量 ASIN 报价（`getItemOffersBatch`） | POST `/spApi/developerProxy` → 上游 POST，path：`batches/products/pricing/v0/itemOffers` | `scripts/post_item_offers_batch.py` | 查询批量 ASIN 报价。 |
| 批量 SKU 报价（`getListingOffersBatch`） | POST `/spApi/developerProxy` → 上游 POST，path：`batches/products/pricing/v0/listingOffers` | `scripts/post_listing_offers_batch.py` | 查询批量 SKU 报价。 |
| 预期 Featured Offer 价格（`getFeaturedOfferExpectedPriceBatch`） | POST `/spApi/developerProxy` → 上游 POST，path：`batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice` | `scripts/post_featured_offer_expected_price_batch.py` | 查询预期 Featured Offer 价格。 |
| 竞争摘要（`getCompetitiveSummary`） | POST `/spApi/developerProxy` → 上游 POST，path：`batches/products/pricing/2022-05-01/items/competitiveSummary` | `scripts/post_competitive_summary_batch.py` | 查询竞争摘要。 |

## 前置条件

**先完成授权并确定店铺与站点**：运行 `python scripts/check_auth_dependency.py` 检查认证技能，缺失时先安装；不得在本技能内绕过依赖另行实现授权或令牌逻辑。选定店铺后准备商品标识和查询目标，依赖检测约定及权限要求见 `references/api.md`。

## 查询流程

1. 检查认证依赖，确认目标店铺、站点、商品及比较口径。
2. 按商品价格、竞争价格、单商品报价、批量报价、FOEP 或竞争摘要选择操作。批量脚本保留简化输入组装和官方原始请求两种模式，具体参数见 `references/api.md`。
3. 先判断网关响应，再判断上游状态；批量响应还需逐条核对结果。错误与冷却处理见接口定义及 `references/spapi-protection.md`。
4. 先读已保存结果的摘要，按需提取字段，展示价格、币种、报价口径和可用竞争信息。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存结果；业务脚本不读取或写入响应缓存。失败或空结果时，不得自动更换商品、站点或比较口径连续试探；需要继续查询时，先说明原因与查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-pricing-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、存在于顶层的常见计数或状态值（如 `total`、`costToken`），以及最大非空列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **清晰展示数据**：标明店铺、站点、ASIN 或卖家 SKU、币种与查询时间；有价格组成时区分商品价、运费与其他返回项目，不补造未返回指标。
- **统一比较口径**：区分成色、消费者或企业买家视角、报价类型；Listing Offers 面向卖家 SKU，Item Offers 面向 ASIN。FOEP 是预期价格，不承诺实际赢得 Featured Offer。
- **保留诊断信息**：查看原始网关和上游结果；批量输出保留组装后的请求与每条结果，不把整批成功视为每条都成功。
- **说明缺失与失败**：保留已有数据，按接口参考说明空结果、路径未放行、权限不足或店铺保护，不自动扩大查询范围。
- **响应缓存**：本技能业务封装始终禁用响应缓存；具体 CLI、环境变量兼容和输出约定见 `references/api.md`。

## 使用示例

### 比较一组商品价格

用户：比较我店铺这几个 ASIN 的当前报价与竞争价格。

确认店铺、站点和比较口径，分别选择商品价格或竞争价格操作，展示返回的价格和币种，说明缺失项。

### 查询单商品或批量低价报价

用户：查这些卖家 SKU 的最低报价。

确认卖家 SKU 与目标站点，选择单条或批量报价，逐条展示结果及错误。

### 查看预期 Featured Offer 价格与竞争摘要

用户：评估这些商品的购物车竞争力。

按用户提供的商品与细分场景查询可用数据，区分实际报价和预期价格，说明竞争摘要能够支持的判断。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
