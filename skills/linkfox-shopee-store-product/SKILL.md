---
name: linkfox-shopee-store-product
description: 管理已授权 Shopee（虾皮）店铺的商品，支持类目、属性、品牌、商品查询与创建更新、SKU规格、价格库存、上下架、置顶、评论回复，以及组合商品、SSP标准品、直营店、Outlet、尺码表、车辆兼容和内容诊断。适用于店铺刊登准备与商品日常维护；不适用于跨店选品研究、店铺授权、订单物流、支付、广告投放或媒体上传。
---
# Shopee 店铺商品管理

## 适用范围

### 适用

查看和维护卖家自己已授权的 Shopee 店铺商品，准备刊登资料并解释操作结果。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这个商品应该选什么类目、填写哪些属性 | 上架准备：类目、属性和品牌。 |
| 查看店铺商品及SKU资料 | 商品查询：列表、基础与扩展信息及规格。 |
| 上架新品，修改库存或价格 | 商品维护：创建、更新、价格库存与上下架。 |
| 置顶商品，查看和回复评论 | 运营维护：推广与买家评论。 |
| 查组合商品、SSP、尺码表或内容问题 | 扩展维护：按目标选择对应操作。 |

### 边界

店铺授权依赖 `linkfox-shopee-store-auth`；跨店选品研究使用 `linkfox-youying-shopee-product-search`。订单、物流、退款、广告、结算、店铺信息、促销及媒体上传使用各自技能，具体分流见 [业务边界](references/boundaries.md)。

## 接口清单

除 Feedback 外共 58 项：57 个 Product 转发操作及 1 个店铺授权状态兼容操作。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建商品（`add_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/add_item`；上游 POST | `references/apis/add-item.md` | `scripts/add_item.py` | 创建商品。 |
| 创建Kit组合商品（`add_kit_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/add_kit_item`；上游 POST | `references/apis/add-kit-item.md` | `scripts/add_kit_item.py` | 创建Kit组合商品。 |
| 添加SKU（`add_model`） | POST `/shopee/developerProxy` -> path：`api/v2/product/add_model`；上游 POST | `references/apis/add-model.md` | `scripts/add_model.py` | 添加SKU。 |
| 置顶推广商品（`boost_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/boost_item`；上游 POST | `references/apis/boost-item.md` | `scripts/boost_item.py` | 置顶推广商品。 |
| 根据标题或图片推荐类目（`category_recommend`） | POST `/shopee/developerProxy` -> path：`api/v2/product/category_recommend`；上游 POST | `references/apis/category-recommend.md` | `scripts/category_recommend.py` | 根据标题或图片推荐类目。 |
| 永久删除商品（`delete_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/delete_item`；上游 POST | `references/apis/delete-item.md` | `scripts/delete_item.py` | 永久删除商品。 |
| 删除SKU（`delete_model`） | POST `/shopee/developerProxy` -> path：`api/v2/product/delete_model`；上游 POST | `references/apis/delete-model.md` | `scripts/delete_model.py` | 删除SKU。 |
| 生成组合商品图片（`generate_kit_image`） | POST `/shopee/developerProxy` -> path：`api/v2/product/generate_kit_image`；上游 POST | `references/apis/generate-kit-image.md` | `scripts/generate_kit_image.py` | 生成组合商品图片。 |
| 根据父商品获取联盟商品（`get_aitem_by_pitem_id`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_aitem_by_pitem_id`；上游 GET | `references/apis/get-aitem-by-pitem-id.md` | `scripts/get_aitem_by_pitem_id.py` | 根据父商品获取联盟商品。 |
| 获取车辆兼容列表（`get_all_vehicle_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_all_vehicle_list`；上游 GET | `references/apis/get-all-vehicle-list.md` | `scripts/get_all_vehicle_list.py` | 获取车辆兼容列表。 |
| 获取类目属性树（`get_attribute_tree`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_attribute_tree`；上游 GET | `references/apis/get-attribute-tree.md` | `scripts/get_attribute_tree.py` | 获取类目属性树。 |
| 获取已置顶商品（`get_boosted_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_boosted_list`；上游 GET | `references/apis/get-boosted-list.md` | `scripts/get_boosted_list.py` | 获取已置顶商品。 |
| 获取品牌列表（`get_brand_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_brand_list`；上游 GET | `references/apis/get-brand-list.md` | `scripts/get_brand_list.py` | 获取品牌列表。 |
| 获取类目树（`get_category`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_category`；上游 GET | `references/apis/get-category.md` | `scripts/get_category.py` | 获取类目树。 |
| 获取商品评论（`get_comment`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_comment`；上游 GET | `references/apis/get-comment.md` | `scripts/get_comment.py` | 获取商品评论。 |
| 获取直营店商品列表（`get_direct_item_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_direct_item_list`；上游 GET | `references/apis/get-direct-item-list.md` | `scripts/get_direct_item_list.py` | 获取直营店商品列表。 |
| 获取直营店建议价格（`get_direct_shop_recommended_price`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_direct_shop_recommended_price`；上游 POST | `references/apis/get-direct-shop-recommended-price.md` | `scripts/get_direct_shop_recommended_price.py` | 获取直营店建议价格。 |
| 获取商品基础信息（`get_item_base_info`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_base_info`；上游 GET | `references/apis/get-item-base-info.md` | `scripts/get_item_base_info.py` | 获取商品基础信息。 |
| 获取商品内容诊断结果（`get_item_content_diagnosis_result`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_content_diagnosis_result`；上游 GET | `references/apis/get-item-content-diagnosis-result.md` | `scripts/get_item_content_diagnosis_result.py` | 获取商品内容诊断结果。 |
| 获取商品扩展信息（`get_item_extra_info`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_extra_info`；上游 GET | `references/apis/get-item-extra-info.md` | `scripts/get_item_extra_info.py` | 获取商品扩展信息。 |
| 获取店铺刊登限制（`get_item_limit`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_limit`；上游 GET | `references/apis/get-item-limit.md` | `scripts/get_item_limit.py` | 获取店铺刊登限制。 |
| 获取商品列表（`get_item_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_list`；上游 GET | `references/apis/get-item-list.md` | `scripts/get_item_list.py` | 获取商品列表。 |
| 按内容诊断状态获取商品列表（`get_item_list_by_content_diagnosis`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_list_by_content_diagnosis`；上游 GET | `references/apis/get-item-list-by-content-diagnosis.md` | `scripts/get_item_list_by_content_diagnosis.py` | 按内容诊断状态获取商品列表。 |
| 获取商品促销信息（`get_item_promotion`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_promotion`；上游 GET | `references/apis/get-item-promotion.md` | `scripts/get_item_promotion.py` | 获取商品促销信息。 |
| 获取商品违规信息（`get_item_violation_info`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_item_violation_info`；上游 GET | `references/apis/get-item-violation-info.md` | `scripts/get_item_violation_info.py` | 获取商品违规信息。 |
| 获取Kit组合商品详情（`get_kit_item_info`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_kit_item_info`；上游 GET | `references/apis/get-kit-item-info.md` | `scripts/get_kit_item_info.py` | 获取Kit组合商品详情。 |
| 获取组合商品限制（`get_kit_item_limit`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_kit_item_limit`；上游 GET | `references/apis/get-kit-item-limit.md` | `scripts/get_kit_item_limit.py` | 获取组合商品限制。 |
| 获取主店商品列表（`get_main_item_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_main_item_list`；上游 GET | `references/apis/get-main-item-list.md` | `scripts/get_main_item_list.py` | 获取主店商品列表。 |
| 根据Outlet商品获取Mart商品（`get_mart_item_by_outlet_item_id`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_mart_item_by_outlet_item_id`；上游 GET | `references/apis/get-mart-item-by-outlet-item-id.md` | `scripts/get_mart_item_by_outlet_item_id.py` | 根据Outlet商品获取Mart商品。 |
| 获取Mart与Outlet商品映射（`get_mart_item_mapping_by_id`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_mart_item_mapping_by_id`；上游 GET | `references/apis/get-mart-item-mapping-by-id.md` | `scripts/get_mart_item_mapping_by_id.py` | 获取Mart与Outlet商品映射。 |
| 获取商品SKU列表（`get_model_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_model_list`；上游 GET | `references/apis/get-model-list.md` | `scripts/get_model_list.py` | 获取商品SKU列表。 |
| 获取商品认证规则（`get_product_certification_rule`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_product_certification_rule`；上游 GET | `references/apis/get-product-certification-rule.md` | `scripts/get_product_certification_rule.py` | 获取商品认证规则。 |
| 推荐刊登属性值（`get_recommend_attribute`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_recommend_attribute`；上游 POST | `references/apis/get-recommend-attribute.md` | `scripts/get_recommend_attribute.py` | 推荐刊登属性值。 |
| 获取尺码表详情（`get_size_chart_detail`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_size_chart_detail`；上游 GET | `references/apis/get-size-chart-detail.md` | `scripts/get_size_chart_detail.py` | 获取尺码表详情。 |
| 获取类目尺码表列表（`get_size_chart_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_size_chart_list`；上游 GET | `references/apis/get-size-chart-list.md` | `scripts/get_size_chart_list.py` | 获取类目尺码表列表。 |
| 获取SSP标准品详情（`get_ssp_info`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_ssp_info`；上游 GET | `references/apis/get-ssp-info.md` | `scripts/get_ssp_info.py` | 获取SSP标准品详情。 |
| 搜索SSP标准品（`get_ssp_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_ssp_list`；上游 GET | `references/apis/get-ssp-list.md` | `scripts/get_ssp_list.py` | 搜索SSP标准品。 |
| 获取标准规格选项（`get_variations`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_variations`；上游 GET | `references/apis/get-variations.md` | `scripts/get_variations.py` | 获取标准规格选项。 |
| 根据兼容详情获取车辆（`get_vehicle_list_by_compatibility_detail`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_vehicle_list_by_compatibility_detail`；上游 GET | `references/apis/get-vehicle-list-by-compatibility-detail.md` | `scripts/get_vehicle_list_by_compatibility_detail.py` | 根据兼容详情获取车辆。 |
| 推荐商品重量（`get_weight_recommendation`） | POST `/shopee/developerProxy` -> path：`api/v2/product/get_weight_recommendation`；上游 POST | `references/apis/get-weight-recommendation.md` | `scripts/get_weight_recommendation.py` | 推荐商品重量。 |
| 初始化商品规格（`init_tier_variation`） | POST `/shopee/developerProxy` -> path：`api/v2/product/init_tier_variation`；上游 POST | `references/apis/init-tier-variation.md` | `scripts/init_tier_variation.py` | 初始化商品规格。 |
| 关联商品与SSP（`link_ssp`） | POST `/shopee/developerProxy` -> path：`api/v2/product/link_ssp`；上游 POST | `references/apis/link-ssp.md` | `scripts/link_ssp.py` | 关联商品与SSP。 |
| 发布商品到Outlet店铺（`publish_item_to_outlet_shop`） | POST `/shopee/developerProxy` -> path：`api/v2/product/publish_item_to_outlet_shop`；上游 POST | `references/apis/publish-item-to-outlet-shop.md` | `scripts/publish_item_to_outlet_shop.py` | 发布商品到Outlet店铺。 |
| 注册品牌（`register_brand`） | POST `/shopee/developerProxy` -> path：`api/v2/product/register_brand`；上游 POST | `references/apis/register-brand.md` | `scripts/register_brand.py` | 注册品牌。 |
| 回复买家评论（`reply_comment`） | POST `/shopee/developerProxy` -> path：`api/v2/product/reply_comment`；上游 POST | `references/apis/reply-comment.md` | `scripts/reply_comment.py` | 回复买家评论。 |
| 搜索属性值（`search_attribute_value_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/search_attribute_value_list`；上游 POST | `references/apis/search-attribute-value-list.md` | `scripts/search_attribute_value_list.py` | 搜索属性值。 |
| 搜索店内商品（`search_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/search_item`；上游 GET | `references/apis/search-item.md` | `scripts/search_item.py` | 搜索店内商品。 |
| 搜索未打包SKU（`search_unpackaged_model_list`） | POST `/shopee/developerProxy` -> path：`api/v2/product/search_unpackaged_model_list`；上游 POST | `references/apis/search-unpackaged-model-list.md` | `scripts/search_unpackaged_model_list.py` | 搜索未打包SKU。 |
| 解除商品与SSP关联（`unlink_ssp`） | POST `/shopee/developerProxy` -> path：`api/v2/product/unlink_ssp`；上游 POST | `references/apis/unlink-ssp.md` | `scripts/unlink_ssp.py` | 解除商品与SSP关联。 |
| 批量上架或下架商品（`unlist_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/unlist_item`；上游 POST | `references/apis/unlist-item.md` | `scripts/unlist_item.py` | 批量上架或下架商品。 |
| 更新商品（`update_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_item`；上游 POST | `references/apis/update-item.md` | `scripts/update_item.py` | 更新商品。 |
| 更新Kit组合商品（`update_kit_item`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_kit_item`；上游 POST | `references/apis/update-kit-item.md` | `scripts/update_kit_item.py` | 更新Kit组合商品。 |
| 更新SKU（`update_model`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_model`；上游 POST | `references/apis/update-model.md` | `scripts/update_model.py` | 更新SKU。 |
| 更新商品价格（`update_price`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_price`；上游 POST | `references/apis/update-price.md` | `scripts/update_price.py` | 更新商品价格。 |
| 更新SIP跨境商品价格（`update_sip_item_price`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_sip_item_price`；上游 POST | `references/apis/update-sip-item-price.md` | `scripts/update_sip_item_price.py` | 更新SIP跨境商品价格。 |
| 更新商品库存（`update_stock`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_stock`；上游 POST | `references/apis/update-stock.md` | `scripts/update_stock.py` | 更新商品库存。 |
| 更新商品规格结构（`update_tier_variation`） | POST `/shopee/developerProxy` -> path：`api/v2/product/update_tier_variation`；上游 POST | `references/apis/update-tier-variation.md` | `scripts/update_tier_variation.py` | 更新商品规格结构。 |
| 查询店铺授权状态（兼容函数 `resolve_store_tokens`） | POST `/shopee/storeTokens` | `references/api.md` | `scripts/_shopee_product_common.py` | 兼容函数，商品入口不自动调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内实现授权或令牌签发逻辑。依赖检测及兼容调用约定见 `references/api.md`。

## 商品管理流程

1. 确认目标店铺及用户要求查询或维护的商品范围，完成授权依赖检查。
2. 上架准备：获取类目树，再查类目属性要求，按用户资料准备完整商品信息并创建商品。
3. 日常维护：先查商品列表与基础信息，再对指定商品修改价格、库存或上下架；需要SKU维护时先查规格和SKU，再初始化、添加、更新或删除。
4. 按任务选择置顶、评论、组合商品、SSP、直营店、Mart/Outlet、尺码表、违规、车辆兼容或内容诊断操作。
5. 先判断网关结果，再判断上游状态并读取解析结果；保存完整响应，展示返回范围及本次变更结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；商品入口始终关闭响应缓存，落盘文件用于保存结果。失败或空结果时，不得自动更换检索条件、翻页或连续试探；按用户任务范围决定后续查询或重试。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-product-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见标量字段（如 `total`、`costToken`，以实际返回为准）、最大列表字段的长度和前 3 条样本。
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

- **店铺与商品概念**：商品是店铺刊登，model 是商品下的SKU，tier variation 是规格结构；SSP 是 Shopee Standard Product。Kit组合商品与促销套装属于不同业务。
- **转发链路**：由 developerProxy 按选定店铺解析令牌，经 shopee-proxy 转发到 Shopee；商品入口不额外获取令牌。
- **清晰展示数据**：注明店铺、商品和SKU，用表格展示实际返回的商品信息、价格库存、评论、诊断及维护结果；缺失字段不补造。
- **遵循用户操作范围**：创建、更新、删除、上下架、置顶、品牌注册、SSP关联和评论回复会改变店铺数据或对外展示内容，按用户明确的目标执行并说明返回结果。
- **响应缓存**：公共调用器支持缓存，本技能业务入口始终关闭响应缓存；运行与成本约束的适用说明见 `references/api.md`。
- **处理结果与错误**：区分网关传输完成、Shopee上游成功和业务执行结果；按接口定义解释错误、空结果及分页，不自动连续试探。

## 使用示例

### 查类目并上架

用户：根据这些商品资料准备新品上架。

确认店铺，先查类目与必填属性，再准备完整商品资料，执行创建并展示结果。

### 查商品并改库存

用户：查看店铺商品，把指定商品库存改为我给出的数量。

查询商品列表与基础信息，核对目标商品和SKU后更新库存，说明响应结果。

### 上下架与推广

用户：下架这批指定商品，或置顶指定商品。

核对目标店铺、商品和操作范围，按对应操作执行，解释返回的成功或失败项。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
