---
name: linkfox-wb-shopee-official-api
display_name: LinkFox Shopee 官方API
display_name_en: LinkFox Shopee Official API
description: 面向 Shopee 店铺全链路运营的官方 API 能力，覆盖授权选店、商品、订单、物流、促销、广告、内容、仓储、支付与店铺健康管理，并返回可审计结果。
description_zh: 面向 Shopee 店铺运营与系统集成的统一官方 API 能力。当用户需要授权或选择 Shopee 店铺，查询或修改商品、订单、物流、退货、店铺资料、促销、广告、联盟营销、直播视频、媒体、仓储、支付结算、Push 或账户健康数据时触发；通过官方 Open API 网关调用并按业务返回结构化结果。支持 ERP 与 AD 授权边界、完整参数参考、MCP 执行、错误分层处理和余额提醒；不替代 Shopee 后台人工审核、平台政策判断或法律意见。
description_en: Unified official API capability for end-to-end Shopee store operations and integrations. Use it for Shopee store authorization and selection, products, orders, logistics, returns, shop settings, promotions, ads, affiliate campaigns, livestreams, videos, media, warehousing, payments, Push, and account health. It routes requests through the official Open API gateway with structured results, full parameter references, MCP execution and layered error handling, and ERP/AD authorization boundaries. It does not replace Shopee console review, platform-policy decisions, or legal advice.
icon: icons/logo.png
version: 1.2.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Shopee 官方API（LinkFox Shopee Official API）

为 Shopee 店铺运营与系统集成提供统一的官方 API 执行能力：先完成店铺授权与选店，再按业务意图调用商品、交易履约、营销增长、内容媒体、仓储财务或平台公共接口，返回可审计的结构化响应。覆盖 29 个业务子能力、429 个 Shopee Open API operation，以及授权管理的 3 个操作，共 432 个路由项。每个子能力的完整参数、响应字段、错误码、特殊限制和执行依赖归档在对应 reference 中。

## 能力边界

### 能力范围
- **linkfox-shopee-store-account-health**：店铺健康指标、扣分处罚、问题 Listing 与逾期订单查询；适用时读取 references/linkfox-shopee-store-account-health.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-add-on-deal**：加购优惠活动、主商品与子商品管理；适用时读取 references/linkfox-shopee-store-add-on-deal.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-ads**：站内广告余额、推荐、Campaign、关键词与效果报表；适用时读取 references/linkfox-shopee-store-ads.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-ams**：联盟营销 Open/Targeted Campaign、达人、商品与效果管理；适用时读取 references/linkfox-shopee-store-ams.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-auth**：店铺 OAuth 授权、ERP/AD 应用区分、已授权店铺与授权状态管理；适用时读取 references/linkfox-shopee-store-auth.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-bundle-deal**：套装优惠活动及商品项管理；适用时读取 references/linkfox-shopee-store-bundle-deal.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-discount**：折扣活动及商品项的创建、查询、更新、结束与删除；适用时读取 references/linkfox-shopee-store-discount.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-fbs**：巴西 FBS 店铺/商品拦截、入驻与发票问题查询；适用时读取 references/linkfox-shopee-store-fbs.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-first-mile**：头程运单、承运渠道、转运仓与绑定解绑管理；适用时读取 references/linkfox-shopee-store-first-mile.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-follow-prize**：关注有礼活动管理；适用时读取 references/linkfox-shopee-store-follow-prize.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-global-product**：全球商品、跨店发布、属性、尺码表、价格库存与发布任务管理；适用时读取 references/linkfox-shopee-store-global-product.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-livestream**：直播场次、展示商品、评论与互动管理；适用时读取 references/linkfox-shopee-store-livestream.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-logistics**：物流渠道、面单、发货、地址、营业时间与轨迹管理；适用时读取 references/linkfox-shopee-store-logistics.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-media**：媒体图片与视频分片上传；适用时读取 references/linkfox-shopee-store-media.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-media-space**：MediaSpace 图片与视频分片上传；适用时读取 references/linkfox-shopee-store-media-space.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-merchant**：商户信息、下属店铺、仓库与预付账户查询；适用时读取 references/linkfox-shopee-store-merchant.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-orders**：订单、包裹、发票、取消、拆单与预约仓处理；适用时读取 references/linkfox-shopee-store-orders.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-payment**：结算、Escrow、钱包、打款、收入报表与分期设置；适用时读取 references/linkfox-shopee-store-payment.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-product**：商品 Listing、类目属性、变体、库存价格、推广、评论与合规信息；适用时读取 references/linkfox-shopee-store-product.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-public**：Partner 公共查询、OAuth Token 与 Shopee IP 范围；适用时读取 references/linkfox-shopee-store-public.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-push**：Push 回调配置、丢失消息查询与确认消费；适用时读取 references/linkfox-shopee-store-push.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-returns**：退货退款、争议、凭证与逆向物流处理；适用时读取 references/linkfox-shopee-store-returns.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-sbs**：SBS 仓储绑定、库存、库龄、效期与库存变动报表；适用时读取 references/linkfox-shopee-store-sbs.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-shop**：店铺资料、仓库、通知、授权品牌与假期模式管理；适用时读取 references/linkfox-shopee-store-shop.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-shop-category**：店铺自定义分类及分类商品管理；适用时读取 references/linkfox-shopee-store-shop-category.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-shop-flash-sale**：店铺秒杀时段、活动与商品项管理；适用时读取 references/linkfox-shopee-store-shop-flash-sale.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-top-picks**：精选商品集合管理；适用时读取 references/linkfox-shopee-store-top-picks.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-video**：店铺视频发布、视频信息与效果分析；适用时读取 references/linkfox-shopee-store-video.md，按其中 `toolName` 与参数契约执行。
- **linkfox-shopee-store-voucher**：店铺优惠券的创建、查询、更新、结束与删除；适用时读取 references/linkfox-shopee-store-voucher.md，按其中 `toolName` 与参数契约执行。
### 边界与限制

- **授权前置**：除授权/公共 OAuth 类操作外，店铺级接口需要已授权的 shopId 或 merchantId；按 shopId/merchantId + appType 判断授权状态。ERP 与 AD 是两套独立授权，广告路径必须使用 AD 授权。
- **统一代理**：业务接口使用 `proxy_call`，精确 `toolName` 为 `shopee/developerProxy`；`arguments` 只提交 path、HTTP method、店铺/商户标识以及上游所需 query/body，不提交 accessToken 或 appType。服务端按 `api/v2/ads/**` 路径选择 AD，其余业务路径选择 ERP。
- **参数与区域**：每个 operation 的必填字段、分页、日期、国家/站点、批量上限和异步轮询规则以对应 reference 为准；不要从相近 operation 推断字段。
- **数据类型**：上传类接口按 reference 要求使用可访问 URL、分片或媒体句柄；本地文件不能直接当作公开图片/视频 URL。异步任务必须查询结果后再报告最终状态。
- **不适用**：不负责 Shopee 账号注册、后台人工操作、平台政策或法律结论、侵权判定、支付扣款确认、供应商采购、站外广告，以及未在路由表和 references 中列出的端点。
- **安全与审计**：不向用户展示 access token、refresh token 或 API Key；写操作（上架、改价、发货、退款、活动、广告预算等）执行前核对店铺、参数和目标状态，并在结果中标明操作是否已被平台接受。

## 工具选择指南

先按用户业务目标选定一个默认模块，再根据输入字段、授权类型、读写风险、是否异步和成本决定是否切换。相近需求按下表区分：
| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 授权店铺、确认 ERP/AD、自然语言选店 | linkfox-shopee-store-auth | 业务调用不要手取 token；按业务端点自动选择 ERP/AD |
| 商品上架、Listing、库存价格、变体、评论 | linkfox-shopee-store-product | 跨店全球商品发布用 linkfox-shopee-store-global-product；仅分类用 linkfox-shopee-store-shop-category |
| 订单、包裹、发票、取消、拆单 | linkfox-shopee-store-orders | 退货退款用 linkfox-shopee-store-returns；配送/面单用 linkfox-shopee-store-logistics |
| 物流发货、面单、轨迹、渠道 | linkfox-shopee-store-logistics | 头程绑定用 linkfox-shopee-store-first-mile；巴西 FBS/SBS 用对应仓储模块 |
| 退货、退款、争议、凭证 | linkfox-shopee-store-returns | 订单主流程仍用 linkfox-shopee-store-orders |
| 店铺资料、假期、仓库、商户 | linkfox-shopee-store-shop | 商户级仓库/下属店铺用 linkfox-shopee-store-merchant |
| 广告余额、关键词、Campaign、广告效果 | linkfox-shopee-store-ads | 达人联盟与佣金活动用 linkfox-shopee-store-ams；广告必须有 AD 授权 |
| 折扣、优惠券、套装、加购、秒杀 | 对应 discount / voucher / bundle-deal / add-on-deal / shop-flash-sale | 先按活动对象选择；不要用通用商品模块代替促销模块 |
| 关注有礼、精选商品、直播、视频 | 对应 follow-prize / top-picks / livestream / video | 图片/视频文件上传先用 media 或 media-space，再调用业务模块 |
| 结算、钱包、打款、收入报表 | linkfox-shopee-store-payment | 订单金额明细需联动 linkfox-shopee-store-orders |
| 账户健康、扣分、处罚、逾期订单 | linkfox-shopee-store-account-health | Listing 详情回到 linkfox-shopee-store-product |
| Push、公共 OAuth、仓储报表 | 对应 push / public / sbs / fbs | 仅在需求明确涉及回调、Partner 公共接口或仓储服务时使用 |
### 选择思路

- 先识别用户要操作的对象（店铺、商品、订单、包裹、退货、活动、广告、媒体或财务），再识别动作（查询、创建、更新、结束、删除、上传或报表）。
- 需要广告时先核对 appType=ad；需要普通店铺业务时核对 appType=erp。同一店铺可能同时出现两条授权记录。
- 同一对象存在轻量查询与详细查询时，先使用满足目标的较小接口；批量、报表和异步任务按 reference 的上限与轮询要求处理。
- 多个 operation 都能满足时，优先默认推荐，并把替代选项、必填参数、授权要求和可能的积分消耗告知用户，由用户决定是否继续。

## 业务需求路由速查

端点均使用 JSON。除授权管理三项外，路由表中的业务请求统一经 `proxy_call` 调用 `shopee/developerProxy`；reference 是该子能力的完整参数与响应归档，本地旧 HTTP 脚本已从调用链移除。

| 子能力 | 业务能力 | reference | `toolName` / 上游 operation | 本地 helper |
|---|---|---|---|---|
| linkfox-shopee-store-account-health | get_late_orders | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_late_orders` | — |
| linkfox-shopee-store-account-health | get_listings_with_issues | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_listings_with_issues` | — |
| linkfox-shopee-store-account-health | get_metric_source_detail | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_metric_source_detail` | — |
| linkfox-shopee-store-account-health | get_penalty_point_history | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_penalty_point_history` | — |
| linkfox-shopee-store-account-health | get_punishment_history | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_punishment_history` | — |
| linkfox-shopee-store-account-health | get_shop_performance | references/linkfox-shopee-store-account-health.md | `shopee/developerProxy` -> GET `api/v2/account_health/get_shop_performance` | — |
| linkfox-shopee-store-add-on-deal | add_add_on_deal | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/add_add_on_deal` | — |
| linkfox-shopee-store-add-on-deal | add_add_on_deal_main_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/add_add_on_deal_main_item` | — |
| linkfox-shopee-store-add-on-deal | add_add_on_deal_sub_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/add_add_on_deal_sub_item` | — |
| linkfox-shopee-store-add-on-deal | delete_add_on_deal | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/delete_add_on_deal` | — |
| linkfox-shopee-store-add-on-deal | delete_add_on_deal_main_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/delete_add_on_deal_main_item` | — |
| linkfox-shopee-store-add-on-deal | delete_add_on_deal_sub_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/delete_add_on_deal_sub_item` | — |
| linkfox-shopee-store-add-on-deal | end_add_on_deal | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/end_add_on_deal` | — |
| linkfox-shopee-store-add-on-deal | get_add_on_deal | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> GET `api/v2/add_on_deal/get_add_on_deal` | — |
| linkfox-shopee-store-add-on-deal | get_add_on_deal_list | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> GET `api/v2/add_on_deal/get_add_on_deal_list` | — |
| linkfox-shopee-store-add-on-deal | get_add_on_deal_main_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> GET `api/v2/add_on_deal/get_add_on_deal_main_item` | — |
| linkfox-shopee-store-add-on-deal | get_add_on_deal_sub_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> GET `api/v2/add_on_deal/get_add_on_deal_sub_item` | — |
| linkfox-shopee-store-add-on-deal | update_add_on_deal | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/update_add_on_deal` | — |
| linkfox-shopee-store-add-on-deal | update_add_on_deal_main_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/update_add_on_deal_main_item` | — |
| linkfox-shopee-store-add-on-deal | update_add_on_deal_sub_item | references/linkfox-shopee-store-add-on-deal.md | `shopee/developerProxy` -> POST `api/v2/add_on_deal/update_add_on_deal_sub_item` | — |
| linkfox-shopee-store-ads | check_create_gms_product_campaign_eligibility | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/check_create_gms_product_campaign_eligibility` | — |
| linkfox-shopee-store-ads | create_gms_product_campaign | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/create_gms_product_campaign` | — |
| linkfox-shopee-store-ads | create_manual_product_ads | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/create_manual_product_ads` | — |
| linkfox-shopee-store-ads | edit_gms_item_product_campaign | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/edit_gms_item_product_campaign` | — |
| linkfox-shopee-store-ads | edit_gms_product_campaign | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/edit_gms_product_campaign` | — |
| linkfox-shopee-store-ads | edit_manual_product_ad_keywords | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/edit_manual_product_ad_keywords` | — |
| linkfox-shopee-store-ads | edit_manual_product_ads | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> POST `api/v2/ads/edit_manual_product_ads` | — |
| linkfox-shopee-store-ads | get_ads_facil_shop_rate | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_ads_facil_shop_rate` | — |
| linkfox-shopee-store-ads | get_all_cpc_ads_daily_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_all_cpc_ads_daily_performance` | — |
| linkfox-shopee-store-ads | get_all_cpc_ads_hourly_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_all_cpc_ads_hourly_performance` | — |
| linkfox-shopee-store-ads | get_create_product_ad_budget_suggestion | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_create_product_ad_budget_suggestion` | — |
| linkfox-shopee-store-ads | get_gms_campaign_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_gms_campaign_performance` | — |
| linkfox-shopee-store-ads | get_gms_item_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_gms_item_performance` | — |
| linkfox-shopee-store-ads | get_product_campaign_daily_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_product_campaign_daily_performance` | — |
| linkfox-shopee-store-ads | get_product_campaign_hourly_performance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_product_campaign_hourly_performance` | — |
| linkfox-shopee-store-ads | get_product_level_campaign_id_list | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_product_level_campaign_id_list` | — |
| linkfox-shopee-store-ads | get_product_level_campaign_setting_info | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_product_level_campaign_setting_info` | — |
| linkfox-shopee-store-ads | get_product_recommended_roi_target | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_product_recommended_roi_target` | — |
| linkfox-shopee-store-ads | get_recommended_item_list | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_recommended_item_list` | — |
| linkfox-shopee-store-ads | get_recommended_keyword_list | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_recommended_keyword_list` | — |
| linkfox-shopee-store-ads | get_shop_toggle_info | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_shop_toggle_info` | — |
| linkfox-shopee-store-ads | get_total_balance | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/get_total_balance` | — |
| linkfox-shopee-store-ads | list_gms_user_deleted_item | references/linkfox-shopee-store-ads.md | `shopee/developerProxy` -> GET `api/v2/ads/list_gms_user_deleted_item` | — |
| linkfox-shopee-store-ams | add_all_products_to_open_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/add_all_products_to_open_campaign` | — |
| linkfox-shopee-store-ams | batch_add_products_to_open_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/batch_add_products_to_open_campaign` | — |
| linkfox-shopee-store-ams | batch_edit_products_open_campaign_setting | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/batch_edit_products_open_campaign_setting` | — |
| linkfox-shopee-store-ams | batch_get_products_suggested_rate | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/batch_get_products_suggested_rate` | — |
| linkfox-shopee-store-ams | batch_remove_products_open_campaign_setting | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/batch_remove_products_open_campaign_setting` | — |
| linkfox-shopee-store-ams | create_new_targeted_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/create_new_targeted_campaign` | — |
| linkfox-shopee-store-ams | edit_affiliate_list_of_targeted_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/edit_affiliate_list_of_targeted_campaign` | — |
| linkfox-shopee-store-ams | edit_all_products_open_campaign_setting | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/edit_all_products_open_campaign_setting` | — |
| linkfox-shopee-store-ams | edit_product_list_of_targeted_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/edit_product_list_of_targeted_campaign` | — |
| linkfox-shopee-store-ams | get_affiliate_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_affiliate_performance` | — |
| linkfox-shopee-store-ams | get_auto_add_new_product_toggle_status | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_auto_add_new_product_toggle_status` | — |
| linkfox-shopee-store-ams | get_campaign_key_metrics_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_campaign_key_metrics_performance` | — |
| linkfox-shopee-store-ams | get_content_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_content_performance` | — |
| linkfox-shopee-store-ams | get_conversion_report | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_conversion_report` | — |
| linkfox-shopee-store-ams | get_managed_affiliate_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_managed_affiliate_list` | — |
| linkfox-shopee-store-ams | get_open_campaign_added_product | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_open_campaign_added_product` | — |
| linkfox-shopee-store-ams | get_open_campaign_batch_task_result | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_open_campaign_batch_task_result` | — |
| linkfox-shopee-store-ams | get_open_campaign_not_added_product | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_open_campaign_not_added_product` | — |
| linkfox-shopee-store-ams | get_open_campaign_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_open_campaign_performance` | — |
| linkfox-shopee-store-ams | get_optimization_suggestion_product | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_optimization_suggestion_product` | — |
| linkfox-shopee-store-ams | get_performance_data_update_time | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_performance_data_update_time` | — |
| linkfox-shopee-store-ams | get_product_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_product_performance` | — |
| linkfox-shopee-store-ams | get_recommended_affiliate_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_recommended_affiliate_list` | — |
| linkfox-shopee-store-ams | get_shop_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_shop_performance` | — |
| linkfox-shopee-store-ams | get_shop_suggested_rate | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_shop_suggested_rate` | — |
| linkfox-shopee-store-ams | get_targeted_campaign_addable_product_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_targeted_campaign_addable_product_list` | — |
| linkfox-shopee-store-ams | get_targeted_campaign_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_targeted_campaign_list` | — |
| linkfox-shopee-store-ams | get_targeted_campaign_performance | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_targeted_campaign_performance` | — |
| linkfox-shopee-store-ams | get_targeted_campaign_settings | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_targeted_campaign_settings` | — |
| linkfox-shopee-store-ams | get_validation_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_validation_list` | — |
| linkfox-shopee-store-ams | get_validation_report | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/get_validation_report` | — |
| linkfox-shopee-store-ams | query_affiliate_list | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> GET `api/v2/ams/query_affiliate_list` | — |
| linkfox-shopee-store-ams | remove_all_products_open_campaign_setting | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/remove_all_products_open_campaign_setting` | — |
| linkfox-shopee-store-ams | terminate_targeted_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/terminate_targeted_campaign` | — |
| linkfox-shopee-store-ams | update_auto_add_new_product_setting | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/update_auto_add_new_product_setting` | — |
| linkfox-shopee-store-ams | update_basic_info_of_targeted_campaign | references/linkfox-shopee-store-ams.md | `shopee/developerProxy` -> POST `api/v2/ams/update_basic_info_of_targeted_campaign` | — |
| linkfox-shopee-store-auth | authorizedStores | references/linkfox-shopee-store-auth.md | `shopee/authorizedStores` | — |
| linkfox-shopee-store-auth | authorizeUrl | references/linkfox-shopee-store-auth.md | `shopee/authorizeUrl` | — |
| linkfox-shopee-store-auth | storeTokens | references/linkfox-shopee-store-auth.md | `shopee/storeTokens` | — |
| linkfox-shopee-store-bundle-deal | add_bundle_deal | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/add_bundle_deal` | — |
| linkfox-shopee-store-bundle-deal | add_bundle_deal_item | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/add_bundle_deal_item` | — |
| linkfox-shopee-store-bundle-deal | delete_bundle_deal | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/delete_bundle_deal` | — |
| linkfox-shopee-store-bundle-deal | delete_bundle_deal_item | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/delete_bundle_deal_item` | — |
| linkfox-shopee-store-bundle-deal | end_bundle_deal | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/end_bundle_deal` | — |
| linkfox-shopee-store-bundle-deal | get_bundle_deal | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> GET `api/v2/bundle_deal/get_bundle_deal` | — |
| linkfox-shopee-store-bundle-deal | get_bundle_deal_item | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> GET `api/v2/bundle_deal/get_bundle_deal_item` | — |
| linkfox-shopee-store-bundle-deal | get_bundle_deal_list | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> GET `api/v2/bundle_deal/get_bundle_deal_list` | — |
| linkfox-shopee-store-bundle-deal | update_bundle_deal | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/update_bundle_deal` | — |
| linkfox-shopee-store-bundle-deal | update_bundle_deal_item | references/linkfox-shopee-store-bundle-deal.md | `shopee/developerProxy` -> POST `api/v2/bundle_deal/update_bundle_deal_item` | — |
| linkfox-shopee-store-discount | add_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/add_discount` | — |
| linkfox-shopee-store-discount | add_discount_item | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/add_discount_item` | — |
| linkfox-shopee-store-discount | delete_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/delete_discount` | — |
| linkfox-shopee-store-discount | delete_discount_item | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/delete_discount_item` | — |
| linkfox-shopee-store-discount | delete_sip_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/delete_sip_discount` | — |
| linkfox-shopee-store-discount | end_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/end_discount` | — |
| linkfox-shopee-store-discount | get_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> GET `api/v2/discount/get_discount` | — |
| linkfox-shopee-store-discount | get_discount_list | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> GET `api/v2/discount/get_discount_list` | — |
| linkfox-shopee-store-discount | get_sip_discounts | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> GET `api/v2/discount/get_sip_discounts` | — |
| linkfox-shopee-store-discount | set_sip_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/set_sip_discount` | — |
| linkfox-shopee-store-discount | update_discount | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/update_discount` | — |
| linkfox-shopee-store-discount | update_discount_item | references/linkfox-shopee-store-discount.md | `shopee/developerProxy` -> POST `api/v2/discount/update_discount_item` | — |
| linkfox-shopee-store-fbs | query_br_shop_block_status | references/linkfox-shopee-store-fbs.md | `shopee/developerProxy` -> GET `api/v2/fbs/query_br_shop_block_status` | — |
| linkfox-shopee-store-fbs | query_br_shop_enrollment_status | references/linkfox-shopee-store-fbs.md | `shopee/developerProxy` -> GET `api/v2/fbs/query_br_shop_enrollment_status` | — |
| linkfox-shopee-store-fbs | query_br_shop_invoice_error | references/linkfox-shopee-store-fbs.md | `shopee/developerProxy` -> GET `api/v2/fbs/query_br_shop_invoice_error` | — |
| linkfox-shopee-store-fbs | query_br_sku_block_status | references/linkfox-shopee-store-fbs.md | `shopee/developerProxy` -> GET `api/v2/fbs/query_br_sku_block_status` | — |
| linkfox-shopee-store-first-mile | bind_courier_delivery_first_mile_tracking_number | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/bind_courier_delivery_first_mile_tracking_number` | — |
| linkfox-shopee-store-first-mile | bind_first_mile_tracking_number | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/bind_first_mile_tracking_number` | — |
| linkfox-shopee-store-first-mile | generate_and_bind_first_mile_tracking_number | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/generate_and_bind_first_mile_tracking_number` | — |
| linkfox-shopee-store-first-mile | generate_first_mile_tracking_number | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/generate_first_mile_tracking_number` | — |
| linkfox-shopee-store-first-mile | get_channel_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_channel_list` | — |
| linkfox-shopee-store-first-mile | get_courier_delivery_channel_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_courier_delivery_channel_list` | — |
| linkfox-shopee-store-first-mile | get_courier_delivery_detail | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_courier_delivery_detail` | — |
| linkfox-shopee-store-first-mile | get_courier_delivery_tracking_number_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_courier_delivery_tracking_number_list` | — |
| linkfox-shopee-store-first-mile | get_courier_delivery_waybill | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_courier_delivery_waybill` | — |
| linkfox-shopee-store-first-mile | get_detail | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_detail` | — |
| linkfox-shopee-store-first-mile | get_tracking_number_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_tracking_number_list` | — |
| linkfox-shopee-store-first-mile | get_transit_warehouse_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_transit_warehouse_list` | — |
| linkfox-shopee-store-first-mile | get_unbind_order_list | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_unbind_order_list` | — |
| linkfox-shopee-store-first-mile | get_waybill | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> GET `api/v2/first_mile/get_waybill` | — |
| linkfox-shopee-store-first-mile | unbind_first_mile_tracking_number | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/unbind_first_mile_tracking_number` | — |
| linkfox-shopee-store-first-mile | unbind_first_mile_tracking_number_all | references/linkfox-shopee-store-first-mile.md | `shopee/developerProxy` -> POST `api/v2/first_mile/unbind_first_mile_tracking_number_all` | — |
| linkfox-shopee-store-follow-prize | add_follow_prize | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> POST `api/v2/follow_prize/add_follow_prize` | — |
| linkfox-shopee-store-follow-prize | delete_follow_prize | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> POST `api/v2/follow_prize/delete_follow_prize` | — |
| linkfox-shopee-store-follow-prize | end_follow_prize | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> POST `api/v2/follow_prize/end_follow_prize` | — |
| linkfox-shopee-store-follow-prize | get_follow_prize_detail | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> GET `api/v2/follow_prize/get_follow_prize_detail` | — |
| linkfox-shopee-store-follow-prize | get_follow_prize_list | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> GET `api/v2/follow_prize/get_follow_prize_list` | — |
| linkfox-shopee-store-follow-prize | update_follow_prize | references/linkfox-shopee-store-follow-prize.md | `shopee/developerProxy` -> POST `api/v2/follow_prize/update_follow_prize` | — |
| linkfox-shopee-store-global-product | add_global_item | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/add_global_item` | — |
| linkfox-shopee-store-global-product | add_global_model | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/add_global_model` | — |
| linkfox-shopee-store-global-product | category_recommend | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/category_recommend` | — |
| linkfox-shopee-store-global-product | create_publish_task | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/create_publish_task` | — |
| linkfox-shopee-store-global-product | delete_global_item | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/delete_global_item` | — |
| linkfox-shopee-store-global-product | delete_global_model | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/delete_global_model` | — |
| linkfox-shopee-store-global-product | get_attribute_tree | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_attribute_tree` | — |
| linkfox-shopee-store-global-product | get_brand_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_brand_list` | — |
| linkfox-shopee-store-global-product | get_category | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_category` | — |
| linkfox-shopee-store-global-product | get_global_item_id | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_global_item_id` | — |
| linkfox-shopee-store-global-product | get_global_item_info | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_global_item_info` | — |
| linkfox-shopee-store-global-product | get_global_item_limit | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_global_item_limit` | — |
| linkfox-shopee-store-global-product | get_global_item_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_global_item_list` | — |
| linkfox-shopee-store-global-product | get_global_model_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_global_model_list` | — |
| linkfox-shopee-store-global-product | get_local_adjustment_rate | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_local_adjustment_rate` | — |
| linkfox-shopee-store-global-product | get_publish_task_result | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_publish_task_result` | — |
| linkfox-shopee-store-global-product | get_publishable_shop | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_publishable_shop` | — |
| linkfox-shopee-store-global-product | get_published_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_published_list` | — |
| linkfox-shopee-store-global-product | get_recommend_attribute | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/get_recommend_attribute` | — |
| linkfox-shopee-store-global-product | get_shop_publishable_status | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_shop_publishable_status` | — |
| linkfox-shopee-store-global-product | get_size_chart_detail | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_size_chart_detail` | — |
| linkfox-shopee-store-global-product | get_size_chart_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_size_chart_list` | — |
| linkfox-shopee-store-global-product | get_variations | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> GET `api/v2/global_product/get_variations` | — |
| linkfox-shopee-store-global-product | init_tier_variation | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/init_tier_variation` | — |
| linkfox-shopee-store-global-product | search_global_attribute_value_list | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/search_global_attribute_value_list` | — |
| linkfox-shopee-store-global-product | set_sync_field | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/set_sync_field` | — |
| linkfox-shopee-store-global-product | support_size_chart | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/support_size_chart` | — |
| linkfox-shopee-store-global-product | update_global_item | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_global_item` | — |
| linkfox-shopee-store-global-product | update_global_model | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_global_model` | — |
| linkfox-shopee-store-global-product | update_local_adjustment_rate | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_local_adjustment_rate` | — |
| linkfox-shopee-store-global-product | update_price | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_price` | — |
| linkfox-shopee-store-global-product | update_size_chart | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_size_chart` | — |
| linkfox-shopee-store-global-product | update_stock | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_stock` | — |
| linkfox-shopee-store-global-product | update_tier_variation | references/linkfox-shopee-store-global-product.md | `shopee/developerProxy` -> POST `api/v2/global_product/update_tier_variation` | — |
| linkfox-shopee-store-livestream | add_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/add_item_list` | — |
| linkfox-shopee-store-livestream | apply_item_set | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/apply_item_set` | — |
| linkfox-shopee-store-livestream | ban_user_comment | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/ban_user_comment` | — |
| linkfox-shopee-store-livestream | create_session | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/create_session` | — |
| linkfox-shopee-store-livestream | delete_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/delete_item_list` | — |
| linkfox-shopee-store-livestream | delete_show_item | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/delete_show_item` | — |
| linkfox-shopee-store-livestream | end_session | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/end_session` | — |
| linkfox-shopee-store-livestream | get_item_count | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_item_count` | — |
| linkfox-shopee-store-livestream | get_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_item_list` | — |
| linkfox-shopee-store-livestream | get_item_set_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_item_set_item_list` | — |
| linkfox-shopee-store-livestream | get_item_set_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_item_set_list` | — |
| linkfox-shopee-store-livestream | get_latest_comment_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_latest_comment_list` | — |
| linkfox-shopee-store-livestream | get_like_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_like_item_list` | — |
| linkfox-shopee-store-livestream | get_recent_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_recent_item_list` | — |
| linkfox-shopee-store-livestream | get_session_detail | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_session_detail` | — |
| linkfox-shopee-store-livestream | get_session_item_metric | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_session_item_metric` | — |
| linkfox-shopee-store-livestream | get_session_metric | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_session_metric` | — |
| linkfox-shopee-store-livestream | get_show_item | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> GET `api/v2/livestream/get_show_item` | — |
| linkfox-shopee-store-livestream | post_comment | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/post_comment` | — |
| linkfox-shopee-store-livestream | start_session | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/start_session` | — |
| linkfox-shopee-store-livestream | unban_user_comment | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/unban_user_comment` | — |
| linkfox-shopee-store-livestream | update_item_list | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/update_item_list` | — |
| linkfox-shopee-store-livestream | update_session | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/update_session` | — |
| linkfox-shopee-store-livestream | update_show_item | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/update_show_item` | — |
| linkfox-shopee-store-livestream | upload_image | references/linkfox-shopee-store-livestream.md | `shopee/developerProxy` -> POST `api/v2/livestream/upload_image` | — |
| linkfox-shopee-store-logistics | batch_ship_order | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/batch_ship_order` | — |
| linkfox-shopee-store-logistics | batch_update_tpf_warehouse_tracking_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/batch_update_tpf_warehouse_tracking_status` | — |
| linkfox-shopee-store-logistics | check_polygon_update_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/check_polygon_update_status` | — |
| linkfox-shopee-store-logistics | create_booking_shipping_document | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/create_booking_shipping_document` | — |
| linkfox-shopee-store-logistics | create_shipping_document | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/create_shipping_document` | — |
| linkfox-shopee-store-logistics | create_shipping_document_job | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/create_shipping_document_job` | — |
| linkfox-shopee-store-logistics | delete_address | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/delete_address` | — |
| linkfox-shopee-store-logistics | delete_special_operating_hour | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/delete_special_operating_hour` | — |
| linkfox-shopee-store-logistics | download_booking_shipping_document | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/download_booking_shipping_document` | — |
| linkfox-shopee-store-logistics | download_shipping_document | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/download_shipping_document` | — |
| linkfox-shopee-store-logistics | download_shipping_document_job | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/download_shipping_document_job` | — |
| linkfox-shopee-store-logistics | download_to_label | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/download_to_label` | — |
| linkfox-shopee-store-logistics | get_address_list | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_address_list` | — |
| linkfox-shopee-store-logistics | get_booking_shipping_document_data_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_shipping_document_data_info` | — |
| linkfox-shopee-store-logistics | get_booking_shipping_document_parameter | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_shipping_document_parameter` | — |
| linkfox-shopee-store-logistics | get_booking_shipping_document_result | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_shipping_document_result` | — |
| linkfox-shopee-store-logistics | get_booking_shipping_parameter | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_shipping_parameter` | — |
| linkfox-shopee-store-logistics | get_booking_tracking_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_tracking_info` | — |
| linkfox-shopee-store-logistics | get_booking_tracking_number | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_booking_tracking_number` | — |
| linkfox-shopee-store-logistics | get_channel_list | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_channel_list` | — |
| linkfox-shopee-store-logistics | get_mart_packaging_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_mart_packaging_info` | — |
| linkfox-shopee-store-logistics | get_mass_shipping_parameter | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/get_mass_shipping_parameter` | — |
| linkfox-shopee-store-logistics | get_mass_tracking_number | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/get_mass_tracking_number` | — |
| linkfox-shopee-store-logistics | get_operating_hour_restrictions | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_operating_hour_restrictions` | — |
| linkfox-shopee-store-logistics | get_operating_hours | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_operating_hours` | — |
| linkfox-shopee-store-logistics | get_pause_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_pause_status` | — |
| linkfox-shopee-store-logistics | get_shipping_document_data_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_shipping_document_data_info` | — |
| linkfox-shopee-store-logistics | get_shipping_document_job_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_shipping_document_job_status` | — |
| linkfox-shopee-store-logistics | get_shipping_document_parameter | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_shipping_document_parameter` | — |
| linkfox-shopee-store-logistics | get_shipping_document_result | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_shipping_document_result` | — |
| linkfox-shopee-store-logistics | get_shipping_parameter | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_shipping_parameter` | — |
| linkfox-shopee-store-logistics | get_tracking_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_tracking_info` | — |
| linkfox-shopee-store-logistics | get_tracking_number | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> GET `api/v2/logistics/get_tracking_number` | — |
| linkfox-shopee-store-logistics | mass_ship_order | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/mass_ship_order` | — |
| linkfox-shopee-store-logistics | set_address_config | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/set_address_config` | — |
| linkfox-shopee-store-logistics | set_mart_packaging_info | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/set_mart_packaging_info` | — |
| linkfox-shopee-store-logistics | set_pause_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/set_pause_status` | — |
| linkfox-shopee-store-logistics | ship_booking | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/ship_booking` | — |
| linkfox-shopee-store-logistics | ship_order | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/ship_order` | — |
| linkfox-shopee-store-logistics | update_address | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_address` | — |
| linkfox-shopee-store-logistics | update_channel | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_channel` | — |
| linkfox-shopee-store-logistics | update_operating_hours | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_operating_hours` | — |
| linkfox-shopee-store-logistics | update_self_collection_order_logistics | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_self_collection_order_logistics` | — |
| linkfox-shopee-store-logistics | update_shipping_order | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_shipping_order` | — |
| linkfox-shopee-store-logistics | update_tracking_status | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/update_tracking_status` | — |
| linkfox-shopee-store-logistics | upload_serviceable_polygon | references/linkfox-shopee-store-logistics.md | `shopee/developerProxy` -> POST `api/v2/logistics/upload_serviceable_polygon` | — |
| linkfox-shopee-store-media | cancel_video_upload | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> POST `api/v2/media/cancel_video_upload` | — |
| linkfox-shopee-store-media | complete_video_upload | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> POST `api/v2/media/complete_video_upload` | — |
| linkfox-shopee-store-media | get_video_upload_result | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> GET `api/v2/media/get_video_upload_result` | — |
| linkfox-shopee-store-media | init_video_upload | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> POST `api/v2/media/init_video_upload` | — |
| linkfox-shopee-store-media | upload_image | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> POST `api/v2/media/upload_image` | — |
| linkfox-shopee-store-media | upload_video_part | references/linkfox-shopee-store-media.md | `shopee/developerProxy` -> POST `api/v2/media/upload_video_part` | — |
| linkfox-shopee-store-media-space | cancel_video_upload | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> POST `api/v2/media_space/cancel_video_upload` | — |
| linkfox-shopee-store-media-space | complete_video_upload | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> POST `api/v2/media_space/complete_video_upload` | — |
| linkfox-shopee-store-media-space | get_video_upload_result | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> GET `api/v2/media_space/get_video_upload_result` | — |
| linkfox-shopee-store-media-space | init_video_upload | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> POST `api/v2/media_space/init_video_upload` | — |
| linkfox-shopee-store-media-space | upload_image | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> POST `api/v2/media_space/upload_image` | — |
| linkfox-shopee-store-media-space | upload_video_part | references/linkfox-shopee-store-media-space.md | `shopee/developerProxy` -> POST `api/v2/media_space/upload_video_part` | — |
| linkfox-shopee-store-merchant | get_merchant_info | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_merchant_info` | — |
| linkfox-shopee-store-merchant | get_merchant_prepaid_account_list | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_merchant_prepaid_account_list` | — |
| linkfox-shopee-store-merchant | get_merchant_warehouse_list | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_merchant_warehouse_list` | — |
| linkfox-shopee-store-merchant | get_merchant_warehouse_location_list | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_merchant_warehouse_location_list` | — |
| linkfox-shopee-store-merchant | get_shop_list_by_merchant | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_shop_list_by_merchant` | — |
| linkfox-shopee-store-merchant | get_warehouse_eligible_shop_list | references/linkfox-shopee-store-merchant.md | `shopee/developerProxy` -> GET `api/v2/merchant/get_warehouse_eligible_shop_list` | — |
| linkfox-shopee-store-orders | cancel_order | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/cancel_order` | — |
| linkfox-shopee-store-orders | download_fbs_invoices | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/download_fbs_invoices` | — |
| linkfox-shopee-store-orders | download_invoice_doc | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/download_invoice_doc` | — |
| linkfox-shopee-store-orders | generate_fbs_invoices | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/generate_fbs_invoices` | — |
| linkfox-shopee-store-orders | get_booking_detail | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_booking_detail` | — |
| linkfox-shopee-store-orders | get_booking_list | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_booking_list` | — |
| linkfox-shopee-store-orders | get_buyer_invoice_info | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/get_buyer_invoice_info` | — |
| linkfox-shopee-store-orders | get_estimiate_cancel_value | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/get_estimiate_cancel_value` | — |
| linkfox-shopee-store-orders | get_fbs_invoices_result | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/get_fbs_invoices_result` | — |
| linkfox-shopee-store-orders | get_order_detail | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_order_detail` | — |
| linkfox-shopee-store-orders | get_order_list | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_order_list` | — |
| linkfox-shopee-store-orders | get_package_detail | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_package_detail` | — |
| linkfox-shopee-store-orders | get_pending_buyer_invoice_order_list | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_pending_buyer_invoice_order_list` | — |
| linkfox-shopee-store-orders | get_shipment_list | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_shipment_list` | — |
| linkfox-shopee-store-orders | get_warehouse_filter_config | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> GET `api/v2/order/get_warehouse_filter_config` | — |
| linkfox-shopee-store-orders | handle_buyer_cancellation | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/handle_buyer_cancellation` | — |
| linkfox-shopee-store-orders | handle_prescription_check | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/handle_prescription_check` | — |
| linkfox-shopee-store-orders | search_package_list | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/search_package_list` | — |
| linkfox-shopee-store-orders | set_note | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/set_note` | — |
| linkfox-shopee-store-orders | split_order | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/split_order` | — |
| linkfox-shopee-store-orders | unsplit_order | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/unsplit_order` | — |
| linkfox-shopee-store-orders | upload_invoice_doc | references/linkfox-shopee-store-orders.md | `shopee/developerProxy` -> POST `api/v2/order/upload_invoice_doc` | — |
| linkfox-shopee-store-payment | generate_income_report | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> POST `api/v2/payment/generate_income_report` | — |
| linkfox-shopee-store-payment | generate_income_statement | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> POST `api/v2/payment/generate_income_statement` | — |
| linkfox-shopee-store-payment | get_billing_transaction_info | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_billing_transaction_info` | — |
| linkfox-shopee-store-payment | get_escrow_detail | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_escrow_detail` | — |
| linkfox-shopee-store-payment | get_escrow_detail_batch | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> POST `api/v2/payment/get_escrow_detail_batch` | — |
| linkfox-shopee-store-payment | get_escrow_list | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_escrow_list` | — |
| linkfox-shopee-store-payment | get_income_detail | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_income_detail` | — |
| linkfox-shopee-store-payment | get_income_overview | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_income_overview` | — |
| linkfox-shopee-store-payment | get_income_report | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_income_report` | — |
| linkfox-shopee-store-payment | get_income_statement | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_income_statement` | — |
| linkfox-shopee-store-payment | get_item_installment_status | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_item_installment_status` | — |
| linkfox-shopee-store-payment | get_payment_method_list | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_payment_method_list` | — |
| linkfox-shopee-store-payment | get_payout_detail | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_payout_detail` | — |
| linkfox-shopee-store-payment | get_payout_info | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_payout_info` | — |
| linkfox-shopee-store-payment | get_shop_installment_status | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_shop_installment_status` | — |
| linkfox-shopee-store-payment | get_wallet_transaction_list | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> GET `api/v2/payment/get_wallet_transaction_list` | — |
| linkfox-shopee-store-payment | set_item_installment_status | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> POST `api/v2/payment/set_item_installment_status` | — |
| linkfox-shopee-store-payment | set_shop_installment_status | references/linkfox-shopee-store-payment.md | `shopee/developerProxy` -> POST `api/v2/payment/set_shop_installment_status` | — |
| linkfox-shopee-store-product | add_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/add_item` | — |
| linkfox-shopee-store-product | add_kit_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/add_kit_item` | — |
| linkfox-shopee-store-product | add_model | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/add_model` | — |
| linkfox-shopee-store-product | boost_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/boost_item` | — |
| linkfox-shopee-store-product | category_recommend | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/category_recommend` | — |
| linkfox-shopee-store-product | delete_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/delete_item` | — |
| linkfox-shopee-store-product | delete_model | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/delete_model` | — |
| linkfox-shopee-store-product | generate_kit_image | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/generate_kit_image` | — |
| linkfox-shopee-store-product | get_aitem_by_pitem_id | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_aitem_by_pitem_id` | — |
| linkfox-shopee-store-product | get_all_vehicle_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_all_vehicle_list` | — |
| linkfox-shopee-store-product | get_attribute_tree | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_attribute_tree` | — |
| linkfox-shopee-store-product | get_boosted_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_boosted_list` | — |
| linkfox-shopee-store-product | get_brand_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_brand_list` | — |
| linkfox-shopee-store-product | get_category | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_category` | — |
| linkfox-shopee-store-product | get_comment | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_comment` | — |
| linkfox-shopee-store-product | get_direct_item_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_direct_item_list` | — |
| linkfox-shopee-store-product | get_direct_shop_recommended_price | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/get_direct_shop_recommended_price` | — |
| linkfox-shopee-store-product | get_item_base_info | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_base_info` | — |
| linkfox-shopee-store-product | get_item_content_diagnosis_result | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_content_diagnosis_result` | — |
| linkfox-shopee-store-product | get_item_extra_info | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_extra_info` | — |
| linkfox-shopee-store-product | get_item_limit | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_limit` | — |
| linkfox-shopee-store-product | get_item_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_list` | — |
| linkfox-shopee-store-product | get_item_list_by_content_diagnosis | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_list_by_content_diagnosis` | — |
| linkfox-shopee-store-product | get_item_promotion | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_promotion` | — |
| linkfox-shopee-store-product | get_item_violation_info | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_item_violation_info` | — |
| linkfox-shopee-store-product | get_kit_item_info | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_kit_item_info` | — |
| linkfox-shopee-store-product | get_kit_item_limit | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_kit_item_limit` | — |
| linkfox-shopee-store-product | get_main_item_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_main_item_list` | — |
| linkfox-shopee-store-product | get_mart_item_by_outlet_item_id | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_mart_item_by_outlet_item_id` | — |
| linkfox-shopee-store-product | get_mart_item_mapping_by_id | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_mart_item_mapping_by_id` | — |
| linkfox-shopee-store-product | get_model_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_model_list` | — |
| linkfox-shopee-store-product | get_product_certification_rule | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_product_certification_rule` | — |
| linkfox-shopee-store-product | get_recommend_attribute | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/get_recommend_attribute` | — |
| linkfox-shopee-store-product | get_size_chart_detail | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_size_chart_detail` | — |
| linkfox-shopee-store-product | get_size_chart_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_size_chart_list` | — |
| linkfox-shopee-store-product | get_ssp_info | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_ssp_info` | — |
| linkfox-shopee-store-product | get_ssp_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_ssp_list` | — |
| linkfox-shopee-store-product | get_variations | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_variations` | — |
| linkfox-shopee-store-product | get_vehicle_list_by_compatibility_detail | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/get_vehicle_list_by_compatibility_detail` | — |
| linkfox-shopee-store-product | get_weight_recommendation | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/get_weight_recommendation` | — |
| linkfox-shopee-store-product | init_tier_variation | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/init_tier_variation` | — |
| linkfox-shopee-store-product | link_ssp | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/link_ssp` | — |
| linkfox-shopee-store-product | publish_item_to_outlet_shop | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/publish_item_to_outlet_shop` | — |
| linkfox-shopee-store-product | register_brand | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/register_brand` | — |
| linkfox-shopee-store-product | reply_comment | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/reply_comment` | — |
| linkfox-shopee-store-product | search_attribute_value_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/search_attribute_value_list` | — |
| linkfox-shopee-store-product | search_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> GET `api/v2/product/search_item` | — |
| linkfox-shopee-store-product | search_unpackaged_model_list | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/search_unpackaged_model_list` | — |
| linkfox-shopee-store-product | unlink_ssp | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/unlink_ssp` | — |
| linkfox-shopee-store-product | unlist_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/unlist_item` | — |
| linkfox-shopee-store-product | update_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_item` | — |
| linkfox-shopee-store-product | update_kit_item | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_kit_item` | — |
| linkfox-shopee-store-product | update_model | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_model` | — |
| linkfox-shopee-store-product | update_price | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_price` | — |
| linkfox-shopee-store-product | update_sip_item_price | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_sip_item_price` | — |
| linkfox-shopee-store-product | update_stock | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_stock` | — |
| linkfox-shopee-store-product | update_tier_variation | references/linkfox-shopee-store-product.md | `shopee/developerProxy` -> POST `api/v2/product/update_tier_variation` | — |
| linkfox-shopee-store-public | get_access_token | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> POST `api/v2/public/get_access_token` | — |
| linkfox-shopee-store-public | get_merchants_by_partner | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> GET `api/v2/public/get_merchants_by_partner` | — |
| linkfox-shopee-store-public | get_shopee_ip_ranges | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> GET `api/v2/public/get_shopee_ip_ranges` | — |
| linkfox-shopee-store-public | get_shops_by_partner | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> GET `api/v2/public/get_shops_by_partner` | — |
| linkfox-shopee-store-public | get_token_by_resend_code | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> POST `api/v2/public/get_token_by_resend_code` | — |
| linkfox-shopee-store-public | refresh_access_token | references/linkfox-shopee-store-public.md | `shopee/developerProxy` -> POST `api/v2/public/refresh_access_token` | — |
| linkfox-shopee-store-push | confirm_consumed_lost_push_message | references/linkfox-shopee-store-push.md | `shopee/developerProxy` -> POST `api/v2/push/confirm_consumed_lost_push_message` | — |
| linkfox-shopee-store-push | get_app_push_config | references/linkfox-shopee-store-push.md | `shopee/developerProxy` -> GET `api/v2/push/get_app_push_config` | — |
| linkfox-shopee-store-push | get_lost_push_message | references/linkfox-shopee-store-push.md | `shopee/developerProxy` -> GET `api/v2/push/get_lost_push_message` | — |
| linkfox-shopee-store-push | set_app_push_config | references/linkfox-shopee-store-push.md | `shopee/developerProxy` -> POST `api/v2/push/set_app_push_config` | — |
| linkfox-shopee-store-returns | accept_offer | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/accept_offer` | — |
| linkfox-shopee-store-returns | cancel_dispute | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/cancel_dispute` | — |
| linkfox-shopee-store-returns | confirm | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/confirm` | — |
| linkfox-shopee-store-returns | convert_image | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/convert_image` | — |
| linkfox-shopee-store-returns | dispute | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/dispute` | — |
| linkfox-shopee-store-returns | get_available_solutions | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_available_solutions` | — |
| linkfox-shopee-store-returns | get_return_detail | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_return_detail` | — |
| linkfox-shopee-store-returns | get_return_dispute_reason | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_return_dispute_reason` | — |
| linkfox-shopee-store-returns | get_return_list | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_return_list` | — |
| linkfox-shopee-store-returns | get_reverse_tracking_info | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_reverse_tracking_info` | — |
| linkfox-shopee-store-returns | get_shipping_carrier | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/get_shipping_carrier` | — |
| linkfox-shopee-store-returns | offer | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/offer` | — |
| linkfox-shopee-store-returns | query_proof | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> GET `api/v2/returns/query_proof` | — |
| linkfox-shopee-store-returns | upload_proof | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/upload_proof` | — |
| linkfox-shopee-store-returns | upload_shipping_proof | references/linkfox-shopee-store-returns.md | `shopee/developerProxy` -> POST `api/v2/returns/upload_shipping_proof` | — |
| linkfox-shopee-store-sbs | get_bound_whs_info | references/linkfox-shopee-store-sbs.md | `shopee/developerProxy` -> GET `api/v2/sbs/get_bound_whs_info` | — |
| linkfox-shopee-store-sbs | get_current_inventory | references/linkfox-shopee-store-sbs.md | `shopee/developerProxy` -> GET `api/v2/sbs/get_current_inventory` | — |
| linkfox-shopee-store-sbs | get_expiry_report | references/linkfox-shopee-store-sbs.md | `shopee/developerProxy` -> GET `api/v2/sbs/get_expiry_report` | — |
| linkfox-shopee-store-sbs | get_stock_aging | references/linkfox-shopee-store-sbs.md | `shopee/developerProxy` -> GET `api/v2/sbs/get_stock_aging` | — |
| linkfox-shopee-store-sbs | get_stock_movement | references/linkfox-shopee-store-sbs.md | `shopee/developerProxy` -> GET `api/v2/sbs/get_stock_movement` | — |
| linkfox-shopee-store-shop | get_authorised_reseller_brand | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_authorised_reseller_brand` | — |
| linkfox-shopee-store-shop | get_br_shop_onboarding_info | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_br_shop_onboarding_info` | — |
| linkfox-shopee-store-shop | get_profile | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_profile` | — |
| linkfox-shopee-store-shop | get_shop_holiday_mode | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_shop_holiday_mode` | — |
| linkfox-shopee-store-shop | get_shop_info | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_shop_info` | — |
| linkfox-shopee-store-shop | get_shop_notification | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_shop_notification` | — |
| linkfox-shopee-store-shop | get_warehouse_detail | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> GET `api/v2/shop/get_warehouse_detail` | — |
| linkfox-shopee-store-shop | set_shop_holiday_mode | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> POST `api/v2/shop/set_shop_holiday_mode` | — |
| linkfox-shopee-store-shop | update_profile | references/linkfox-shopee-store-shop.md | `shopee/developerProxy` -> POST `api/v2/shop/update_profile` | — |
| linkfox-shopee-store-shop-category | add_item_list | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> POST `api/v2/shop_category/add_item_list` | — |
| linkfox-shopee-store-shop-category | add_shop_category | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> POST `api/v2/shop_category/add_shop_category` | — |
| linkfox-shopee-store-shop-category | delete_item_list | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> POST `api/v2/shop_category/delete_item_list` | — |
| linkfox-shopee-store-shop-category | delete_shop_category | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> POST `api/v2/shop_category/delete_shop_category` | — |
| linkfox-shopee-store-shop-category | get_item_list | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> GET `api/v2/shop_category/get_item_list` | — |
| linkfox-shopee-store-shop-category | get_shop_category_list | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> GET `api/v2/shop_category/get_shop_category_list` | — |
| linkfox-shopee-store-shop-category | update_shop_category | references/linkfox-shopee-store-shop-category.md | `shopee/developerProxy` -> POST `api/v2/shop_category/update_shop_category` | — |
| linkfox-shopee-store-shop-flash-sale | add_shop_flash_sale_items | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/add_shop_flash_sale_items` | — |
| linkfox-shopee-store-shop-flash-sale | create_shop_flash_sale | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/create_shop_flash_sale` | — |
| linkfox-shopee-store-shop-flash-sale | delete_shop_flash_sale | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/delete_shop_flash_sale` | — |
| linkfox-shopee-store-shop-flash-sale | delete_shop_flash_sale_items | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/delete_shop_flash_sale_items` | — |
| linkfox-shopee-store-shop-flash-sale | get_item_criteria | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> GET `api/v2/shop_flash_sale/get_item_criteria` | — |
| linkfox-shopee-store-shop-flash-sale | get_shop_flash_sale | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> GET `api/v2/shop_flash_sale/get_shop_flash_sale` | — |
| linkfox-shopee-store-shop-flash-sale | get_shop_flash_sale_items | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> GET `api/v2/shop_flash_sale/get_shop_flash_sale_items` | — |
| linkfox-shopee-store-shop-flash-sale | get_shop_flash_sale_list | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> GET `api/v2/shop_flash_sale/get_shop_flash_sale_list` | — |
| linkfox-shopee-store-shop-flash-sale | get_time_slot_id | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> GET `api/v2/shop_flash_sale/get_time_slot_id` | — |
| linkfox-shopee-store-shop-flash-sale | update_shop_flash_sale | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/update_shop_flash_sale` | — |
| linkfox-shopee-store-shop-flash-sale | update_shop_flash_sale_items | references/linkfox-shopee-store-shop-flash-sale.md | `shopee/developerProxy` -> POST `api/v2/shop_flash_sale/update_shop_flash_sale_items` | — |
| linkfox-shopee-store-top-picks | add_top_picks | references/linkfox-shopee-store-top-picks.md | `shopee/developerProxy` -> POST `api/v2/top_picks/add_top_picks` | — |
| linkfox-shopee-store-top-picks | delete_top_picks | references/linkfox-shopee-store-top-picks.md | `shopee/developerProxy` -> POST `api/v2/top_picks/delete_top_picks` | — |
| linkfox-shopee-store-top-picks | get_top_picks_list | references/linkfox-shopee-store-top-picks.md | `shopee/developerProxy` -> GET `api/v2/top_picks/get_top_picks_list` | — |
| linkfox-shopee-store-top-picks | update_top_picks | references/linkfox-shopee-store-top-picks.md | `shopee/developerProxy` -> POST `api/v2/top_picks/update_top_picks` | — |
| linkfox-shopee-store-video | delete_video | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> POST `api/v2/video/delete_video` | — |
| linkfox-shopee-store-video | edit_video_info | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> POST `api/v2/video/edit_video_info` | — |
| linkfox-shopee-store-video | get_cover_list | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_cover_list` | — |
| linkfox-shopee-store-video | get_metric_trend | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_metric_trend` | — |
| linkfox-shopee-store-video | get_overview_performance | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_overview_performance` | — |
| linkfox-shopee-store-video | get_prodcut_performance_list | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_prodcut_performance_list` | — |
| linkfox-shopee-store-video | get_user_demographics | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_user_demographics` | — |
| linkfox-shopee-store-video | get_video_detail | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_detail` | — |
| linkfox-shopee-store-video | get_video_detail_audience_distribution | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_detail_audience_distribution` | — |
| linkfox-shopee-store-video | get_video_detail_metric_trend | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_detail_metric_trend` | — |
| linkfox-shopee-store-video | get_video_detail_performance | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_detail_performance` | — |
| linkfox-shopee-store-video | get_video_detail_product_performance | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_detail_product_performance` | — |
| linkfox-shopee-store-video | get_video_list | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_list` | — |
| linkfox-shopee-store-video | get_video_performance_list | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> GET `api/v2/video/get_video_performance_list` | — |
| linkfox-shopee-store-video | post_video | references/linkfox-shopee-store-video.md | `shopee/developerProxy` -> POST `api/v2/video/post_video` | — |
| linkfox-shopee-store-voucher | add_voucher | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> POST `api/v2/voucher/add_voucher` | — |
| linkfox-shopee-store-voucher | delete_voucher | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> POST `api/v2/voucher/delete_voucher` | — |
| linkfox-shopee-store-voucher | end_voucher | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> POST `api/v2/voucher/end_voucher` | — |
| linkfox-shopee-store-voucher | get_voucher | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> GET `api/v2/voucher/get_voucher` | — |
| linkfox-shopee-store-voucher | get_voucher_list | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> GET `api/v2/voucher/get_voucher_list` | — |
| linkfox-shopee-store-voucher | update_voucher | references/linkfox-shopee-store-voucher.md | `shopee/developerProxy` -> POST `api/v2/voucher/update_voucher` | — |
## MCP 调用方式

MCP server 固定为 `LinkFox`，地址为 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，唯一工具为 `proxy_call`。

允许的 `toolName` allowlist：

- `shopee/authorizeUrl`
- `shopee/authorizedStores`
- `shopee/storeTokens`
- `shopee/developerProxy`

调用结构：

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/shop/get_shop_info",
    "method": "GET",
    "shopId": "67890"
  }
}
```

`toolName` 必须精确匹配并区分大小写；`arguments` 是原网关请求对象，不额外包裹 `body`、`params`、`data` 或第二层 `arguments`。共享 developerProxy 的 `path`、`method`、`queryString`、`body` 继续作为业务路由字段放在 `arguments` 中。完整请求参数和响应字段见路由表对应 reference。

WorkBuddy 自动注入 Authorization。禁止在 MCP 配置、文档示例或 `arguments` 中加入 `headers`、API Key、token、JWT、手机号或其他凭证。禁止使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 缺失时禁止静默 HTTP fallback。

同一任务内相同 `toolName + arguments` 不得重复调用。收费调用失败、空结果或返回不理想时不得自动重试。先检查 MCP 连接、schema、`isError`；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 和 `errmsg`/`msg`。MCP/代理错误与下游业务错误必须分层报告。

## 使用示例

授权：

```json
{"toolName":"shopee/authorizeUrl","arguments":{"shopName":"我的虾皮店铺","region":"cn","appType":"erp"}}
```

业务读取：

```json
{"toolName":"shopee/developerProxy","arguments":{"path":"api/v2/shop/get_shop_info","method":"GET","shopId":"67890"}}
```

写操作必须先展示目标店铺、operation 和关键参数，取得用户明确确认后再调用；批量、上传、异步和轮询流程必须遵守对应 reference 的状态机与幂等约束。

## 展示规则

1. **确认目标**：展示店铺名称/ID、appType、站点/区域、请求 operation 和查询时间范围；同店 ERP 与 AD 记录分开呈现。
2. **客观呈现**：将响应中的状态、计数、金额、ID、时间、分页和错误字段原样结构化展示；不要把 Shopee 返回的状态自行改写成成功。
3. **来源标注**：每组结果标注对应子能力、Shopee operation、上游 path 和数据时间；跨模块汇总时保留各模块边界。
4. **写入结果**：对创建/更新/删除/结束/发货/退款/广告投放等操作，明确区分“请求已发送”“平台已接受”“异步处理中”“完成”与“失败”，并展示任务 ID、活动 ID、包裹号或错误码。
5. **敏感信息**：遮蔽 API Key、access token、refresh token、授权 state 中的敏感值；不回显完整鉴权 Header。
6. **不可用字段**：空值、缺失值、0/-1 等仅在 reference 明确表示无数据时标为 N/A；不要把占位值当作实际业务值。
7. **分页与异步**：显示当前页/总数/游标；批量或异步接口展示批次结果和轮询状态，不能只报告提交成功。
8. **上传与媒体**：展示媒体 ID、URL、分片/任务状态和失败分片；不把临时上传 URL 当作永久资源。
9. **错误协同**：根据 errcode、HTTP 状态和 errmsg 给出对应修正建议。常见网关错误包括 1002 参数或未登录、1003 代理/网络异常、1004 缺少目标授权、1005 token 失效或 path 未白名单；不要对同一失败请求盲目重试。
10. **成本提示**：多次查询、批量、报表、广告或深分页可能消耗积分；在继续执行前说明可能产生的额外消耗。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失：停止业务调用，配置上述 MCP server 后重启或重载 WorkBuddy；不得安装、热加载或 HTTP 回退。
- MCP 连接返回 401：视为 WorkBuddy 自动授权链路异常，提示重新登录、重载连接或联系 WorkBuddy 管理员；不得要求用户填写 Authorization。
- 代理成功但下游 JSON 为 401：视为自动授权或下游认证失败；不得把 Key 放进 `arguments`。
- 下游 JSON 为 402 或积分不足：停止调用并引导用户访问 `https://agent.linkfox.com/`；不得自动选套餐、下单、支付或轮询。
- 403 与其他业务错误按对应 reference 处理，不归类为 401/402。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
