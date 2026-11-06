---
name: linkfox-shopee-store-global-product
description: 管理已授权 Shopee 跨境商户的全球商品，支持类目、属性、品牌、全球 SKU、规格、价格、库存、同步字段、尺码表和本地调价维护，并将全球商品发布到各站点店铺及查询发布结果。适用于跨境全球商品管理和多站点发布；不适用于单店本地商品、店铺授权、订单管理或图片视频上传。
---
# Shopee 全球商品与跨站点发布

## 适用范围

### 适用

管理已授权 Shopee 跨境商户的全球商品及站点发布。
用户希望查询或维护全球商品、全球 SKU，或将商品发布到目标站点店铺时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查全球商品的类目、属性和品牌 | 上架准备：读取类目与属性要求。 |
| 创建或修改全球商品和 SKU | 商品维护：管理商品资料、规格和 SKU。 |
| 修改全球价格、库存或同步设置 | 销售维护：更新指定商品及其站点同步信息。 |
| 把全球商品发布到几个站点 | 跨站点发布：检查资格、提交任务并查询结果。 |
| 看尺码表或本地调价比例 | 辅助维护：读取或更新相关配置。 |

### 边界

店铺授权交给 `linkfox-shopee-store-auth`；本地单店商品交给 `linkfox-shopee-store-product`。
商户信息、订单和店铺信息分别使用 `linkfox-shopee-store-merchant`、`linkfox-shopee-store-orders`、`linkfox-shopee-store-shop`；图片与视频上传使用 MediaSpace 模块。

## 接口清单

共 34 个全球商品操作及 1 个令牌辅助操作，不含 Feedback。网关请求均为 POST；下表单独标注上游方法。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建全球商品（`add_global_item`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/add_global_item`；上游 POST | [references/apis/add-global-item.md](references/apis/add-global-item.md) | `scripts/add_global_item.py` | 根据商品资料创建全球商品。 |
| 新增全球 SKU（`add_global_model`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/add_global_model`；上游 POST | [references/apis/add-global-model.md](references/apis/add-global-model.md) | `scripts/add_global_model.py` | 新增全球 SKU。 |
| 推荐类目（`category_recommend`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/category_recommend`；上游 POST | [references/apis/category-recommend.md](references/apis/category-recommend.md) | `scripts/category_recommend.py` | 推荐类目。 |
| 创建发布任务（`create_publish_task`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/create_publish_task`；上游 POST | [references/apis/create-publish-task.md](references/apis/create-publish-task.md) | `scripts/create_publish_task.py` | 创建发布任务。 |
| 删除全球商品（`delete_global_item`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/delete_global_item`；上游 POST | [references/apis/delete-global-item.md](references/apis/delete-global-item.md) | `scripts/delete_global_item.py` | 删除全球商品。 |
| 删除全球 SKU（`delete_global_model`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/delete_global_model`；上游 POST | [references/apis/delete-global-model.md](references/apis/delete-global-model.md) | `scripts/delete_global_model.py` | 删除全球 SKU。 |
| 获取属性树（`get_attribute_tree`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_attribute_tree`；上游 GET | [references/apis/get-attribute-tree.md](references/apis/get-attribute-tree.md) | `scripts/get_attribute_tree.py` | 查询全球商品上架所需属性。 |
| 获取品牌列表（`get_brand_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_brand_list`；上游 GET | [references/apis/get-brand-list.md](references/apis/get-brand-list.md) | `scripts/get_brand_list.py` | 查询目标类目可用品牌。 |
| 获取全球类目（`get_category`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_category`；上游 GET | [references/apis/get-category.md](references/apis/get-category.md) | `scripts/get_category.py` | 获取全球商品类目树。 |
| 映射全球商品编号（`get_global_item_id`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_global_item_id`；上游 GET | [references/apis/get-global-item-id.md](references/apis/get-global-item-id.md) | `scripts/get_global_item_id.py` | 映射全球商品编号。 |
| 获取全球商品详情（`get_global_item_info`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_global_item_info`；上游 GET | [references/apis/get-global-item-info.md](references/apis/get-global-item-info.md) | `scripts/get_global_item_info.py` | 读取指定全球商品详情。 |
| 获取全球商品限制（`get_global_item_limit`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_global_item_limit`；上游 GET | [references/apis/get-global-item-limit.md](references/apis/get-global-item-limit.md) | `scripts/get_global_item_limit.py` | 获取全球商品限制。 |
| 获取全球商品列表（`get_global_item_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_global_item_list`；上游 GET | [references/apis/get-global-item-list.md](references/apis/get-global-item-list.md) | `scripts/get_global_item_list.py` | 按条件查询全球商品列表。 |
| 获取全球 SKU 列表（`get_global_model_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_global_model_list`；上游 GET | [references/apis/get-global-model-list.md](references/apis/get-global-model-list.md) | `scripts/get_global_model_list.py` | 获取全球 SKU 列表。 |
| 获取本地调价比例（`get_local_adjustment_rate`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_local_adjustment_rate`；上游 GET | [references/apis/get-local-adjustment-rate.md](references/apis/get-local-adjustment-rate.md) | `scripts/get_local_adjustment_rate.py` | 获取本地调价比例。 |
| 获取发布任务结果（`get_publish_task_result`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_publish_task_result`；上游 GET | [references/apis/get-publish-task-result.md](references/apis/get-publish-task-result.md) | `scripts/get_publish_task_result.py` | 获取发布任务结果。 |
| 获取可发布店铺（`get_publishable_shop`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_publishable_shop`；上游 GET | [references/apis/get-publishable-shop.md](references/apis/get-publishable-shop.md) | `scripts/get_publishable_shop.py` | 获取可发布店铺。 |
| 获取已发布列表（`get_published_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_published_list`；上游 GET | [references/apis/get-published-list.md](references/apis/get-published-list.md) | `scripts/get_published_list.py` | 获取已发布列表。 |
| 推荐属性（`get_recommend_attribute`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_recommend_attribute`；上游 POST | [references/apis/get-recommend-attribute.md](references/apis/get-recommend-attribute.md) | `scripts/get_recommend_attribute.py` | 推荐属性。 |
| 获取店铺发布资格（`get_shop_publishable_status`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_shop_publishable_status`；上游 GET | [references/apis/get-shop-publishable-status.md](references/apis/get-shop-publishable-status.md) | `scripts/get_shop_publishable_status.py` | 获取店铺发布资格。 |
| 获取尺码表详情（`get_size_chart_detail`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_size_chart_detail`；上游 GET | [references/apis/get-size-chart-detail.md](references/apis/get-size-chart-detail.md) | `scripts/get_size_chart_detail.py` | 获取尺码表详情。 |
| 获取尺码表列表（`get_size_chart_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_size_chart_list`；上游 GET | [references/apis/get-size-chart-list.md](references/apis/get-size-chart-list.md) | `scripts/get_size_chart_list.py` | 获取尺码表列表。 |
| 获取标准规格（`get_variations`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/get_variations`；上游 GET | [references/apis/get-variations.md](references/apis/get-variations.md) | `scripts/get_variations.py` | 获取标准规格。 |
| 初始化规格（`init_tier_variation`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/init_tier_variation`；上游 POST | [references/apis/init-tier-variation.md](references/apis/init-tier-variation.md) | `scripts/init_tier_variation.py` | 初始化规格。 |
| 搜索全球属性值（`search_global_attribute_value_list`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/search_global_attribute_value_list`；上游 POST | [references/apis/search-global-attribute-value-list.md](references/apis/search-global-attribute-value-list.md) | `scripts/search_global_attribute_value_list.py` | 搜索全球属性值。 |
| 设置同步字段（`set_sync_field`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/set_sync_field`；上游 POST | [references/apis/set-sync-field.md](references/apis/set-sync-field.md) | `scripts/set_sync_field.py` | 设置同步字段。 |
| 检查尺码表支持（`support_size_chart`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/support_size_chart`；上游 POST | [references/apis/support-size-chart.md](references/apis/support-size-chart.md) | `scripts/support_size_chart.py` | 检查尺码表支持。 |
| 更新全球商品（`update_global_item`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_global_item`；上游 POST | [references/apis/update-global-item.md](references/apis/update-global-item.md) | `scripts/update_global_item.py` | 修改指定全球商品资料。 |
| 更新全球 SKU（`update_global_model`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_global_model`；上游 POST | [references/apis/update-global-model.md](references/apis/update-global-model.md) | `scripts/update_global_model.py` | 更新全球 SKU。 |
| 更新本地调价比例（`update_local_adjustment_rate`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_local_adjustment_rate`；上游 POST | [references/apis/update-local-adjustment-rate.md](references/apis/update-local-adjustment-rate.md) | `scripts/update_local_adjustment_rate.py` | 更新本地调价比例。 |
| 更新价格（`update_price`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_price`；上游 POST | [references/apis/update-price.md](references/apis/update-price.md) | `scripts/update_price.py` | 维护全球商品价格。 |
| 更新尺码表（`update_size_chart`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_size_chart`；上游 POST | [references/apis/update-size-chart.md](references/apis/update-size-chart.md) | `scripts/update_size_chart.py` | 更新尺码表。 |
| 更新库存（`update_stock`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_stock`；上游 POST | [references/apis/update-stock.md](references/apis/update-stock.md) | `scripts/update_stock.py` | 维护全球商品库存。 |
| 更新规格（`update_tier_variation`） | POST `/shopee/developerProxy` -> path：`api/v2/global_product/update_tier_variation`；上游 POST | [references/apis/update-tier-variation.md](references/apis/update-tier-variation.md) | `scripts/update_tier_variation.py` | 更新规格。 |
| 获取已授权令牌（`storeTokens`，辅助） | POST `/shopee/storeTokens` | [references/api.md](references/api.md) | `scripts/store_tokens.py`；`_shopee_global_product_common.resolve_store_tokens` | 提供已授权令牌辅助查询；常规全球商品调用由服务端解析令牌，不额外取令牌。 |

## 前置条件

**先完成授权并确定目标**：依赖 `linkfox-shopee-store-auth` 确定已授权的商户或店铺标识。GlobalProduct 通常使用 `merchantId`；涉及站点发布或映射时，再按操作需要提供 `shopId`。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。检测约定与请求要求见 [references/api.md](references/api.md)。

## 业务流程

1. 检查授权依赖，按本次操作确定商户或店铺标识及操作范围。
2. 创建并发布：依次查询类目与属性，准备完整商品资料，创建全球商品，再提交站点发布任务、查询任务结果。
3. 查询并维护：先查全球商品列表，再读取目标商品详情，根据用户要求更新库存、价格或商品资料。
4. 维护全球 SKU：按需初始化规格、查询 SKU，再新增、修改或删除指定 SKU。
5. 只对用户指定范围继续发布结果查询和分页；失败或空结果按调用约束处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。业务脚本不启用响应缓存，重复运行会重新请求接口。失败或空结果时，不得自动更换参数、翻页或连续试探；需要继续查询时，先向用户说明原因及查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-global-product-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分全球商品与本地商品**：GlobalProduct 管跨境全球商品及各站点发布；Product 管单店 listing。
- **理解转发链路**：由 developerProxy 选定商户或店铺，服务端注入令牌，经紫鸟 shopee-proxy 转发到 Shopee；常规操作不额外获取令牌。
- **清晰展示结果**：注明商户、目标店铺和操作名称，用表格展示可用商品、SKU、库存、价格及发布状态；缺失字段按缺失说明。
- **区分提交与完成**：发布任务创建成功不等于站点发布完成；结合发布任务结果说明状态。响应判断和数据解析顺序见接口文档。
- **保留已取得的数据**：发生错误时保留完整响应与已经取得的结果，按响应原因说明下一步。
- **使用适当入口**：独立脚本处理对应操作；`scripts/global_product_api.py` 提供全部全球商品操作的通用入口。参数、CLI、无缓存行为及兼容规则见接口文档。

## 使用示例

### 创建全球商品并发布到目标站点

用户：用这份商品资料创建全球商品，发布到我指定的站点店铺。

确定商户和目标店铺，查询类目与属性，创建商品后提交发布任务，再查询并说明各目标站点的发布结果。

### 查询全球商品并维护库存

用户：查出这个全球商品及其 SKU，把库存改成我提供的数量。

先查询商品与 SKU，核对用户指定的更新范围，提交库存变更并解释响应。

### 查看发布状态或尺码表

用户：看这个任务是否发布成功，并核对商品的尺码表。

读取任务结果及所需尺码信息，展示实际返回的状态与内容。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
