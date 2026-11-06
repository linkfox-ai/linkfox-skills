---
name: linkfox-shopee-store-ads
description: 管理已授权 Shopee（虾皮）店铺的站内广告，支持广告账户余额与开关查询、推广商品及关键词推荐、手动商品广告和 GMS 活动创建与编辑，以及 CPC、商品活动和 GMS 效果分析。适用于店铺推广维护、预算与 ROI 参考、广告表现查询；广告授权独立于 ERP 授权，不适用于商品刊登、联盟营销 AMS、自动商品广告或其他平台广告。
---
# Shopee 店铺站内广告管理

## 适用范围

### 适用

查看和维护已授权 Shopee 店铺的站内广告。用户希望了解广告余额、商品推广、关键词、广告活动、CPC 效果或 ROI 时使用，无需明确提及 Ads。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 查广告余额和自动充值开关 | 账户状态：展示广告余额与开关。 |
| 哪些商品和关键词适合推广 | 推广准备：展示推荐商品、关键词、预算和 ROI 参考。 |
| 创建或调整手动商品广告 | 广告维护：创建活动或修改设置、关键词。 |
| 看广告每天或每小时的表现 | 效果报表：区分全部 CPC 与指定商品活动。 |
| 检查并维护 GMS 广告 | GMS：查询资格、创建或编辑活动、查看活动及商品效果。 |

### 边界

店铺授权由 `linkfox-shopee-store-auth` 处理，商品刊登使用 `linkfox-shopee-store-product`，联盟营销 AMS（module=127）使用 `linkfox-shopee-store-ams`；Amazon 广告使用相应 Amazon 广告技能。本站内广告范围不包含自动商品广告。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 检查 GMS 商品广告活动创建资格（`check_create_gms_product_campaign_eligibility`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/check_create_gms_product_campaign_eligibility` | [references/apis/check-create-gms-product-campaign-eligibility.md](references/apis/check-create-gms-product-campaign-eligibility.md) | `scripts/check_create_gms_product_campaign_eligibility.py` | 检查 GMS 商品广告活动创建资格。 |
| 创建 GMS 商品广告活动（`create_gms_product_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/create_gms_product_campaign` | [references/apis/create-gms-product-campaign.md](references/apis/create-gms-product-campaign.md) | `scripts/create_gms_product_campaign.py` | 创建 GMS 商品广告活动。 |
| 创建手动选品商品广告（`create_manual_product_ads`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/create_manual_product_ads` | [references/apis/create-manual-product-ads.md](references/apis/create-manual-product-ads.md) | `scripts/create_manual_product_ads.py` | 创建手动选品商品广告。 |
| 编辑 GMS 商品活动（`edit_gms_item_product_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/edit_gms_item_product_campaign` | [references/apis/edit-gms-item-product-campaign.md](references/apis/edit-gms-item-product-campaign.md) | `scripts/edit_gms_item_product_campaign.py` | 编辑 GMS 商品活动。 |
| 编辑 GMS 商品广告活动（`edit_gms_product_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/edit_gms_product_campaign` | [references/apis/edit-gms-product-campaign.md](references/apis/edit-gms-product-campaign.md) | `scripts/edit_gms_product_campaign.py` | 编辑 GMS 商品广告活动。 |
| 编辑手动商品广告关键词（`edit_manual_product_ad_keywords`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/edit_manual_product_ad_keywords` | [references/apis/edit-manual-product-ad-keywords.md](references/apis/edit-manual-product-ad-keywords.md) | `scripts/edit_manual_product_ad_keywords.py` | 编辑手动商品广告关键词。 |
| 编辑手动商品广告（`edit_manual_product_ads`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ads/edit_manual_product_ads` | [references/apis/edit-manual-product-ads.md](references/apis/edit-manual-product-ads.md) | `scripts/edit_manual_product_ads.py` | 编辑手动商品广告。 |
| 查询 Ads Facil 计划店铺费率（`get_ads_facil_shop_rate`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_ads_facil_shop_rate` | [references/apis/get-ads-facil-shop-rate.md](references/apis/get-ads-facil-shop-rate.md) | `scripts/get_ads_facil_shop_rate.py` | 查询 Ads Facil 计划店铺费率。 |
| 查询全部 CPC 广告每日效果（`get_all_cpc_ads_daily_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_all_cpc_ads_daily_performance` | [references/apis/get-all-cpc-ads-daily-performance.md](references/apis/get-all-cpc-ads-daily-performance.md) | `scripts/get_all_cpc_ads_daily_performance.py` | 查询全部 CPC 广告每日效果。 |
| 查询全部 CPC 广告小时效果（`get_all_cpc_ads_hourly_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_all_cpc_ads_hourly_performance` | [references/apis/get-all-cpc-ads-hourly-performance.md](references/apis/get-all-cpc-ads-hourly-performance.md) | `scripts/get_all_cpc_ads_hourly_performance.py` | 查询全部 CPC 广告小时效果。 |
| 查询新建商品广告预算建议（`get_create_product_ad_budget_suggestion`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_create_product_ad_budget_suggestion` | [references/apis/get-create-product-ad-budget-suggestion.md](references/apis/get-create-product-ad-budget-suggestion.md) | `scripts/get_create_product_ad_budget_suggestion.py` | 查询新建商品广告预算建议。 |
| 查询 GMS 广告活动效果（`get_gms_campaign_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_gms_campaign_performance` | [references/apis/get-gms-campaign-performance.md](references/apis/get-gms-campaign-performance.md) | `scripts/get_gms_campaign_performance.py` | 查询 GMS 广告活动效果。 |
| 查询 GMS 商品效果（`get_gms_item_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_gms_item_performance` | [references/apis/get-gms-item-performance.md](references/apis/get-gms-item-performance.md) | `scripts/get_gms_item_performance.py` | 查询 GMS 商品效果。 |
| 查询商品广告活动每日效果（`get_product_campaign_daily_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_product_campaign_daily_performance` | [references/apis/get-product-campaign-daily-performance.md](references/apis/get-product-campaign-daily-performance.md) | `scripts/get_product_campaign_daily_performance.py` | 查询商品广告活动每日效果。 |
| 查询商品广告活动小时效果（`get_product_campaign_hourly_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_product_campaign_hourly_performance` | [references/apis/get-product-campaign-hourly-performance.md](references/apis/get-product-campaign-hourly-performance.md) | `scripts/get_product_campaign_hourly_performance.py` | 查询商品广告活动小时效果。 |
| 查询商品级广告活动 ID 列表（`get_product_level_campaign_id_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_product_level_campaign_id_list` | [references/apis/get-product-level-campaign-id-list.md](references/apis/get-product-level-campaign-id-list.md) | `scripts/get_product_level_campaign_id_list.py` | 查询商品级广告活动 ID 列表。 |
| 查询商品广告活动设置（`get_product_level_campaign_setting_info`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_product_level_campaign_setting_info` | [references/apis/get-product-level-campaign-setting-info.md](references/apis/get-product-level-campaign-setting-info.md) | `scripts/get_product_level_campaign_setting_info.py` | 查询商品广告活动设置。 |
| 查询推荐 ROI 目标（`get_product_recommended_roi_target`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_product_recommended_roi_target` | [references/apis/get-product-recommended-roi-target.md](references/apis/get-product-recommended-roi-target.md) | `scripts/get_product_recommended_roi_target.py` | 查询推荐 ROI 目标。 |
| 查询推荐推广商品（`get_recommended_item_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_recommended_item_list` | [references/apis/get-recommended-item-list.md](references/apis/get-recommended-item-list.md) | `scripts/get_recommended_item_list.py` | 查询推荐推广商品。 |
| 查询推荐广告关键词（`get_recommended_keyword_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_recommended_keyword_list` | [references/apis/get-recommended-keyword-list.md](references/apis/get-recommended-keyword-list.md) | `scripts/get_recommended_keyword_list.py` | 查询推荐广告关键词。 |
| 查询自动充值与 Campaign Surge 开关（`get_shop_toggle_info`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_shop_toggle_info` | [references/apis/get-shop-toggle-info.md](references/apis/get-shop-toggle-info.md) | `scripts/get_shop_toggle_info.py` | 查询自动充值与 Campaign Surge 开关。 |
| 查询广告账户实时余额（`get_total_balance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/get_total_balance` | [references/apis/get-total-balance.md](references/apis/get-total-balance.md) | `scripts/get_total_balance.py` | 查询广告账户实时余额。 |
| 查询 GMS 用户删除商品列表（`list_gms_user_deleted_item`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ads/list_gms_user_deleted_item` | [references/apis/list-gms-user-deleted-item.md](references/apis/list-gms-user-deleted-item.md) | `scripts/list_gms_user_deleted_item.py` | 查询 GMS 用户删除商品列表。 |

## 前置条件

**先完成广告授权并确定目标店铺**：依赖 `linkfox-shopee-store-auth`；先运行 `python scripts/check_auth_dependency.py` 检查依赖。不要在本技能内实现授权或令牌逻辑。店铺还须在 Shopee 侧开通广告能力，并非所有站点、店铺均可用。依赖检查、授权识别和接口要求见 [references/api.md](references/api.md)。

## 业务执行流程

1. 每次任务开头，通过认证技能的 `authorized_stores.py` 检查目标店铺的广告授权。仅有 ERP 记录或历史空值不能视为广告已授权；缺失时使用该技能的 `authorize_url.py` 发起广告授权，完成后再执行本技能。用户只需广告时，无需先开通 ERP；授权链接有效期见 [接口参考](references/api.md)。
2. 查余额与推荐：先查询账户余额，再按任务查询推荐商品或关键词。
3. 创建手动商品广告：先查询预算建议，准备完整广告资料并创建，再按用户要求查询商品活动每日效果；维护现有活动时查询活动 ID 与设置后，编辑广告或关键词。
4. GMS：先检查创建资格，再按任务创建或编辑活动、调整商品活动，查询用户删除的商品或活动及商品效果。
5. 效果分析：按用户目标选择全部 CPC、商品活动或 GMS 的报表，明确每日与小时粒度。依据 [各接口定义](references/api.md) 判断网关、上游与业务结果后展示数据。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本与调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，23 个业务脚本不读取或写入响应缓存。失败或空结果时，不得自动变更参数、翻页或连续试探；需要继续查询时，先说明查询范围与目的。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-ads-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应中的顶层常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **本技能的缓存行为**：23 个业务脚本始终禁用响应缓存；公共调用器仍可能创建空的 `.cache` 目录。同一会话应避免重复请求。运行约定见 [references/api.md](references/api.md)。
- **AD 与 ERP 分离**：广告 Token 与 ERP Token 独立，店铺出现在授权列表中不等于已经取得广告授权。凭证和转发约定见 [references/api.md](references/api.md)。
- **识别产品范围**：手动商品广告支持创建、编辑广告和关键词；GMS 支持活动、商品与效果查询。自动商品广告 `create_auto_product_ads`、`edit_auto_product_ads` 因官方标注即将下线而未纳入。
- **清晰展示结果**：注明目标店铺、时间范围与报表粒度，用表格呈现响应实际包含的余额、推荐或效果数据；币种、单位及空值按返回内容说明，不补造缺失指标。
- **区分查询和维护**：创建与编辑会改变广告投放；依据用户已明确的目标准备内容，说明实际返回的操作结果。写入防重、错误处理及脚本兼容行为见 [references/api.md](references/api.md)。
- **核对字段定义**：各操作的官方字段说明链接见对应接口文档及脚本，未定义的业务字段须核对后再使用。

## 使用示例

### 查看广告账户与推荐

用户：查这家店的广告余额，再看看推荐推广的商品。

检查广告授权后查询余额与推荐商品，展示目标店铺、余额和推荐结果。

### 创建或维护手动商品广告

用户：按这些推广资料创建广告，之后查看效果。

查询预算建议，按用户资料准备完整广告内容，提交创建并解释返回结果，再按用户指定范围查看商品活动效果。

### 查看 GMS 与 CPC 效果

用户：查看指定时间内 GMS 和 CPC 广告的表现。

根据用户需要分别查询 GMS 活动或商品效果、全部 CPC 或指定商品活动报表，区分时间粒度及统计范围。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
