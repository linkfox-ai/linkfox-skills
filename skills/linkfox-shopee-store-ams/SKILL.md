---
name: linkfox-shopee-store-ams
description: 管理已授权 Shopee（虾皮）店铺的联盟营销 AMS，支持开放推广和定向达人活动、推广商品和达人维护、佣金率建议、店铺与商品及达人效果、转化与结算验证报告。适用于达人带货、联盟推广设置和效果核对；不适用于店铺授权、站内 CPC 广告、商品刊登、店铺视频或订单管理。
---
# Shopee 联盟营销 AMS

## 适用范围

### 适用

管理已授权 Shopee 店铺的 AMS（Affiliate Marketing Solutions）联盟推广。
用户希望维护开放推广、为指定达人创建定向推广、查看建议佣金或核对推广效果时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看哪些商品已加入或可以加入联盟推广 | 开放推广商品查询与维护。 |
| 开启新品自动加入，调整商品佣金 | 开放推广设置维护。 |
| 为这些达人创建定向活动 | 达人筛选与定向推广维护。 |
| 查询推荐达人或达人推广表现 | 推荐、已管理达人与达人效果。 |
| 看联盟推广带来的销量和转化 | 店铺、商品、内容、活动效果与转化报告。 |
| 核对联盟结算数据 | 结算验证列表和报告。 |

### 边界

店铺授权交由 `linkfox-shopee-store-auth`；站内 CPC 广告使用 `linkfox-shopee-store-ads`（module=117）。商品刊登、店铺视频和订单分别使用 `linkfox-shopee-store-product`、`linkfox-shopee-store-video`、`linkfox-shopee-store-orders`。

## 接口清单

包含 36 个 AMS 转发操作和共享脚本提供的 1 个令牌兼容操作；Feedback 不计入。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 将全部合格商品加入开放推广（`add_all_products_to_open_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/add_all_products_to_open_campaign` | [references/apis/add-all-products-to-open-campaign.md](references/apis/add-all-products-to-open-campaign.md) | `scripts/add_all_products_to_open_campaign.py` | 将全部合格商品加入开放推广。 |
| 批量添加开放推广商品（`batch_add_products_to_open_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/batch_add_products_to_open_campaign` | [references/apis/batch-add-products-to-open-campaign.md](references/apis/batch-add-products-to-open-campaign.md) | `scripts/batch_add_products_to_open_campaign.py` | 批量添加开放推广商品。 |
| 批量编辑开放推广商品设置（`batch_edit_products_open_campaign_setting`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/batch_edit_products_open_campaign_setting` | [references/apis/batch-edit-products-open-campaign-setting.md](references/apis/batch-edit-products-open-campaign-setting.md) | `scripts/batch_edit_products_open_campaign_setting.py` | 批量编辑开放推广商品设置。 |
| 批量查询商品建议佣金率（`batch_get_products_suggested_rate`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/batch_get_products_suggested_rate` | [references/apis/batch-get-products-suggested-rate.md](references/apis/batch-get-products-suggested-rate.md) | `scripts/batch_get_products_suggested_rate.py` | 批量查询商品建议佣金率。 |
| 批量移除开放推广商品（`batch_remove_products_open_campaign_setting`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/batch_remove_products_open_campaign_setting` | [references/apis/batch-remove-products-open-campaign-setting.md](references/apis/batch-remove-products-open-campaign-setting.md) | `scripts/batch_remove_products_open_campaign_setting.py` | 批量移除开放推广商品。 |
| 创建定向推广活动（`create_new_targeted_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/create_new_targeted_campaign` | [references/apis/create-new-targeted-campaign.md](references/apis/create-new-targeted-campaign.md) | `scripts/create_new_targeted_campaign.py` | 创建定向推广活动。 |
| 编辑定向推广达人列表（`edit_affiliate_list_of_targeted_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/edit_affiliate_list_of_targeted_campaign` | [references/apis/edit-affiliate-list-of-targeted-campaign.md](references/apis/edit-affiliate-list-of-targeted-campaign.md) | `scripts/edit_affiliate_list_of_targeted_campaign.py` | 编辑定向推广达人列表。 |
| 编辑全部开放推广商品设置（`edit_all_products_open_campaign_setting`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/edit_all_products_open_campaign_setting` | [references/apis/edit-all-products-open-campaign-setting.md](references/apis/edit-all-products-open-campaign-setting.md) | `scripts/edit_all_products_open_campaign_setting.py` | 编辑全部开放推广商品设置。 |
| 编辑定向推广商品列表（`edit_product_list_of_targeted_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/edit_product_list_of_targeted_campaign` | [references/apis/edit-product-list-of-targeted-campaign.md](references/apis/edit-product-list-of-targeted-campaign.md) | `scripts/edit_product_list_of_targeted_campaign.py` | 编辑定向推广商品列表。 |
| 查询达人效果（`get_affiliate_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_affiliate_performance` | [references/apis/get-affiliate-performance.md](references/apis/get-affiliate-performance.md) | `scripts/get_affiliate_performance.py` | 查询达人效果。 |
| 查询新品自动加入开关（`get_auto_add_new_product_toggle_status`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_auto_add_new_product_toggle_status` | [references/apis/get-auto-add-new-product-toggle-status.md](references/apis/get-auto-add-new-product-toggle-status.md) | `scripts/get_auto_add_new_product_toggle_status.py` | 查询新品自动加入开关。 |
| 查询活动关键指标（`get_campaign_key_metrics_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_campaign_key_metrics_performance` | [references/apis/get-campaign-key-metrics-performance.md](references/apis/get-campaign-key-metrics-performance.md) | `scripts/get_campaign_key_metrics_performance.py` | 查询活动关键指标。 |
| 查询内容效果（`get_content_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_content_performance` | [references/apis/get-content-performance.md](references/apis/get-content-performance.md) | `scripts/get_content_performance.py` | 查询内容效果。 |
| 查询转化报告（`get_conversion_report`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_conversion_report` | [references/apis/get-conversion-report.md](references/apis/get-conversion-report.md) | `scripts/get_conversion_report.py` | 查询转化报告。 |
| 查询已管理达人（`get_managed_affiliate_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_managed_affiliate_list` | [references/apis/get-managed-affiliate-list.md](references/apis/get-managed-affiliate-list.md) | `scripts/get_managed_affiliate_list.py` | 查询已管理达人。 |
| 查询已加入开放推广的商品（`get_open_campaign_added_product`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_open_campaign_added_product` | [references/apis/get-open-campaign-added-product.md](references/apis/get-open-campaign-added-product.md) | `scripts/get_open_campaign_added_product.py` | 查询已加入开放推广的商品。 |
| 查询开放推广批量任务结果（`get_open_campaign_batch_task_result`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_open_campaign_batch_task_result` | [references/apis/get-open-campaign-batch-task-result.md](references/apis/get-open-campaign-batch-task-result.md) | `scripts/get_open_campaign_batch_task_result.py` | 查询开放推广批量任务结果。 |
| 查询未加入开放推广的商品（`get_open_campaign_not_added_product`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_open_campaign_not_added_product` | [references/apis/get-open-campaign-not-added-product.md](references/apis/get-open-campaign-not-added-product.md) | `scripts/get_open_campaign_not_added_product.py` | 查询未加入开放推广的商品。 |
| 查询开放推广效果（`get_open_campaign_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_open_campaign_performance` | [references/apis/get-open-campaign-performance.md](references/apis/get-open-campaign-performance.md) | `scripts/get_open_campaign_performance.py` | 查询开放推广效果。 |
| 查询商品优化建议（`get_optimization_suggestion_product`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_optimization_suggestion_product` | [references/apis/get-optimization-suggestion-product.md](references/apis/get-optimization-suggestion-product.md) | `scripts/get_optimization_suggestion_product.py` | 查询商品优化建议。 |
| 查询效果数据更新时间（`get_performance_data_update_time`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_performance_data_update_time` | [references/apis/get-performance-data-update-time.md](references/apis/get-performance-data-update-time.md) | `scripts/get_performance_data_update_time.py` | 查询效果数据更新时间。 |
| 查询商品效果（`get_product_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_product_performance` | [references/apis/get-product-performance.md](references/apis/get-product-performance.md) | `scripts/get_product_performance.py` | 查询商品效果。 |
| 查询推荐达人（`get_recommended_affiliate_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_recommended_affiliate_list` | [references/apis/get-recommended-affiliate-list.md](references/apis/get-recommended-affiliate-list.md) | `scripts/get_recommended_affiliate_list.py` | 查询推荐达人。 |
| 查询店铺效果（`get_shop_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_shop_performance` | [references/apis/get-shop-performance.md](references/apis/get-shop-performance.md) | `scripts/get_shop_performance.py` | 查询店铺效果。 |
| 查询店铺建议佣金率（`get_shop_suggested_rate`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_shop_suggested_rate` | [references/apis/get-shop-suggested-rate.md](references/apis/get-shop-suggested-rate.md) | `scripts/get_shop_suggested_rate.py` | 查询店铺建议佣金率。 |
| 查询定向推广可添加商品（`get_targeted_campaign_addable_product_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_targeted_campaign_addable_product_list` | [references/apis/get-targeted-campaign-addable-product-list.md](references/apis/get-targeted-campaign-addable-product-list.md) | `scripts/get_targeted_campaign_addable_product_list.py` | 查询定向推广可添加商品。 |
| 查询定向推广活动列表（`get_targeted_campaign_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_targeted_campaign_list` | [references/apis/get-targeted-campaign-list.md](references/apis/get-targeted-campaign-list.md) | `scripts/get_targeted_campaign_list.py` | 查询定向推广活动列表。 |
| 查询定向推广效果（`get_targeted_campaign_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_targeted_campaign_performance` | [references/apis/get-targeted-campaign-performance.md](references/apis/get-targeted-campaign-performance.md) | `scripts/get_targeted_campaign_performance.py` | 查询定向推广效果。 |
| 查询定向推广设置（`get_targeted_campaign_settings`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_targeted_campaign_settings` | [references/apis/get-targeted-campaign-settings.md](references/apis/get-targeted-campaign-settings.md) | `scripts/get_targeted_campaign_settings.py` | 查询定向推广设置。 |
| 查询结算验证列表（`get_validation_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_validation_list` | [references/apis/get-validation-list.md](references/apis/get-validation-list.md) | `scripts/get_validation_list.py` | 查询结算验证列表。 |
| 查询结算验证报告（`get_validation_report`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/get_validation_report` | [references/apis/get-validation-report.md](references/apis/get-validation-report.md) | `scripts/get_validation_report.py` | 查询结算验证报告。 |
| 筛选查询达人列表（`query_affiliate_list`） | POST `/shopee/developerProxy` -> GET path：`api/v2/ams/query_affiliate_list` | [references/apis/query-affiliate-list.md](references/apis/query-affiliate-list.md) | `scripts/query_affiliate_list.py` | 筛选查询达人列表。 |
| 移除全部开放推广商品（`remove_all_products_open_campaign_setting`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/remove_all_products_open_campaign_setting` | [references/apis/remove-all-products-open-campaign-setting.md](references/apis/remove-all-products-open-campaign-setting.md) | `scripts/remove_all_products_open_campaign_setting.py` | 移除全部开放推广商品。 |
| 终止定向推广活动（`terminate_targeted_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/terminate_targeted_campaign` | [references/apis/terminate-targeted-campaign.md](references/apis/terminate-targeted-campaign.md) | `scripts/terminate_targeted_campaign.py` | 终止定向推广活动。 |
| 更新新品自动加入设置（`update_auto_add_new_product_setting`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/update_auto_add_new_product_setting` | [references/apis/update-auto-add-new-product-setting.md](references/apis/update-auto-add-new-product-setting.md) | `scripts/update_auto_add_new_product_setting.py` | 更新新品自动加入设置。 |
| 更新定向推广基本信息（`update_basic_info_of_targeted_campaign`） | POST `/shopee/developerProxy` -> POST path：`api/v2/ams/update_basic_info_of_targeted_campaign` | [references/apis/update-basic-info-of-targeted-campaign.md](references/apis/update-basic-info-of-targeted-campaign.md) | `scripts/update_basic_info_of_targeted_campaign.py` | 更新定向推广基本信息。 |
| 兼容查询店铺令牌（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口兼容查询店铺令牌storetokens) | `scripts/_shopee_ams_common.py`（`resolve_store_tokens`） | 提供令牌查询辅助调用；AMS 入口不自动取令牌。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店和授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装，不在本技能内另行实现授权或令牌逻辑。依赖检测与认证兼容约定见 `references/api.md`。
确认目标店铺、推广类型及待查询或维护的商品、达人和活动；按接口清单读取对应文档。

## 操作流程

1. 检查授权技能依赖，确认用户目标店铺和本次推广任务，按接口清单选择操作。
2. 管理开放推广商品时，先查已加入商品，再查未加入商品；用户要求添加时，准备并提交批量添加。其他开放推广设置按用户任务选择维护操作。
3. 创建定向达人活动时，先查推荐达人，结合用户目标准备完整活动内容，创建后按任务范围查询活动效果。
4. 查询佣金建议、店铺或商品或达人效果、转化和结算验证报告时，使用对应读取操作；保留返回结果并说明覆盖范围。
5. 先检查网关和上游状态，再读取解析结果；结果不确定时保留原始错误和已有数据，具体判断见 `references/api.md` 及各接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存响应。本技能始终禁用响应缓存，`--no-cache` 为兼容选项。失败或空结果时，不得自动修改参数或翻页连续试探；需要继续查询时，说明已有结果及继续查询的范围；写入结果不确定时先核对实际状态，不自动重复提交。算力规则见下方“算力消耗预估”。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-ams-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如返回结果中的 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分推广类型**：Open Campaign 为开放推广，所有达人可参与；Targeted Campaign 为定向推广，面向指定达人。
- **区分佣金与效果**：店铺及商品建议佣金率用于设置参考，效果报表用于核对已经发生的推广表现，不能将两者混为同一结果。
- **清晰展示数据**：注明店铺、推广类型、统计区间和数据更新时间，用表格展示响应中实际存在的商品、达人、佣金、活动及效果字段，不补造缺失指标。
- **按用户范围维护**：商品加入或移除、佣金及自动加入设置、定向活动创建和终止均可能改变推广状态；按用户已明确的目标准备操作并解释返回结果。
- **解释异步结果**：区分提交成功、批量任务完成和实际生效，按需查询任务结果；不得将网关正常响应直接表述为推广已生效。
- **理解转发链路**：`developerProxy` 根据选定店铺由服务端注入令牌，经紫鸟 `shopee-proxy` 转发至 Shopee；具体参数放置和脚本兼容约定见接口文档。
- **按需查阅参考**：通用入口为 `scripts/ams_api.py`；每个操作脚本保留 module=127 的官方文档链接，接口清单提供对应参数文档。

## 使用示例

### 管理开放推广商品

用户：查看当前联盟推广商品，把我选定的商品加入推广。

确认店铺，查询已加入和未加入商品，按用户选定范围准备批量添加内容，提交后说明结果及可查询的批量任务状态。

### 创建定向达人活动

用户：为这些达人和商品创建定向推广，再查看活动表现。

核对店铺和达人目标，按需查看推荐达人，准备完整活动内容，创建后按用户指定范围查询效果。

### 核对推广效果与佣金建议

用户：看店铺联盟推广转化，再查询这些商品的建议佣金率。

分别取得效果、转化和佣金建议，标明统计范围与各指标用途，展示实际返回的数据。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
