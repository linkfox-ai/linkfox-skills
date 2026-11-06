---
name: linkfox-temu-manage-product-global
description: 管理 Temu 全球区（非美国、欧洲）店铺商品，支持商品与 SKU 查询、详情、全量或局部编辑、删除、库存、上下架、预售、发布状态、规格、属性关系、类目预检、合规资料及视频封面，并获取加签资源的下载结果。适用于已授权店铺的商品维护；美国和欧洲商品管理、首次发品、价格、促销、广告、订单及履约使用对应技能。
---

# Temu 全球站商品管理

## 适用范围

### 适用

维护已授权 Temu 全球区店铺的商品、SKU、库存和商品资料，核对提交后的状态。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 看全球区店铺商品、SKU 或当前库存 | 商品和 SKU 列表、详情、库存查询。 |
| 改标题、图片、属性或完整商品资料 | 局部编辑或全量编辑，保留请求层级。 |
| 加库存、上下架、开关预售、删除商品 | 核对目标商品和 SKU 后执行用户指定操作。 |
| 看商品是否发布、补合规资料 | 发布状态、合规待办和资质编辑。 |
| 查属性、兼容车型或视频封面 | 属性推荐、层级模板、关系值、已选关系及视频封面。 |

### 边界

美国、欧洲商品管理分别使用 `linkfox-temu-manage-product-us`、`linkfox-temu-manage-product-eu`。首次发品使用 `linkfox-temu-add-product-us`，价格与供货价使用 `linkfox-temu-price-global`；促销、广告、订单、履约和取消使用对应业务技能。电商合规专门流程使用 `linkfox-temu-compliance-global`，本技能保留商品管理中的合规待办与资料编辑。跨域调用的站点要求见 `references/api.md`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 类目预检（`bg.local.goods.category.check`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.category.check` | `references/apis/bg-local-goods-category-check.md` | `scripts/global_manage_category_check.py` | 全球站类目预检。 |
| 合规编辑（`bg.local.goods.compliance.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.compliance.edit` | `references/apis/bg-local-goods-compliance-edit.md` | `scripts/global_manage_compliance_edit.py` | 全球站合规编辑。 |
| 合规列表（`bg.local.compliance.goods.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.compliance.goods.list.query` | `references/apis/bg-local-compliance-goods-list-query.md` | `scripts/global_manage_compliance_list_query.py` | 全球站合规列表。 |
| 商品详情（`bg.local.goods.detail.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.detail.query` | `references/apis/bg-local-goods-detail-query.md` | `scripts/global_manage_detail_query.py` | 全球站商品详情。 |
| 删除商品（`temu.local.goods.delete`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.delete` | `references/apis/temu-local-goods-delete.md` | `scripts/global_manage_goods_delete.py` | 全球站删除商品。 |
| 商品列表搜索（`temu.local.goods.list.retrieve`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.list.retrieve` | `references/apis/temu-local-goods-list-retrieve.md` | `scripts/global_manage_goods_list_retrieve.py` | 全球站商品列表搜索。 |
| 全量编辑（`bg.local.goods.update`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.update` | `references/apis/bg-local-goods-update.md` | `scripts/global_manage_goods_update.py` | 全球站全量编辑。 |
| 商品列表（`bg.local.goods.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.list.query` | `references/apis/bg-local-goods-list-query.md` | `scripts/global_manage_list_query.py` | 全球站商品列表。 |
| 商品外部编码（`bg.local.goods.out.sn.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.out.sn.set` | `references/apis/bg-local-goods-out-sn-set.md` | `scripts/global_manage_out_sn_set.py` | 全球站商品外部编码。 |
| 部分编辑（`bg.local.goods.partial.update`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.partial.update` | `references/apis/bg-local-goods-partial-update.md` | `scripts/global_manage_partial_update.py` | 全球站部分编辑。 |
| 预售状态（`temu.local.goods.pre.sale.status.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.pre.sale.status.edit` | `references/apis/temu-local-goods-pre-sale-status-edit.md` | `scripts/global_manage_pre_sale_status_edit.py` | 全球站预售状态。 |
| 商品属性获取（`bg.local.goods.property.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.get` | `references/apis/bg-local-goods-property-get.md` | `scripts/global_manage_property_get.py` | 全球站商品属性获取。 |
| 属性关联库（`bg.local.goods.property.relations`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations` | `references/apis/bg-local-goods-property-relations.md` | `scripts/global_manage_property_relations.py` | 全球站属性关联库。 |
| 层级模板（`bg.local.goods.property.relations.level.template`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations.level.template` | `references/apis/bg-local-goods-property-relations-level-template.md` | `scripts/global_manage_property_relations_level_template.py` | 全球站层级模板。 |
| 依赖属性模板（`bg.local.goods.property.relations.template`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations.template` | `references/apis/bg-local-goods-property-relations-template.md` | `scripts/global_manage_property_relations_template.py` | 全球站依赖属性模板。 |
| 发布状态（`bg.local.goods.publish.status.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.publish.status.get` | `references/apis/bg-local-goods-publish-status-get.md` | `scripts/global_manage_publish_status_get.py` | 全球站发布状态。 |
| 上下架（`bg.local.goods.sale.status.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sale.status.set` | `references/apis/bg-local-goods-sale-status-set.md` | `scripts/global_manage_sale_status_set.py` | 全球站上下架。 |
| SKU列表（`bg.local.goods.sku.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sku.list.query` | `references/apis/bg-local-goods-sku-list-query.md` | `scripts/global_manage_sku_list_query.py` | 全球站SKU列表。 |
| SKU列表搜索（`temu.local.sku.list.retrieve`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.sku.list.retrieve` | `references/apis/temu-local-sku-list-retrieve.md` | `scripts/global_manage_sku_list_retrieve.py` | 全球站SKU列表搜索。 |
| SKU外部编码（`bg.local.goods.sku.out.sn.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sku.out.sn.set` | `references/apis/bg-local-goods-sku-out-sn-set.md` | `scripts/global_manage_sku_out_sn_set.py` | 全球站SKU外部编码。 |
| SKU库存查询（`temu.local.goods.sku.stock.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.sku.stock.query` | `references/apis/temu-local-goods-sku-stock-query.md` | `scripts/global_manage_sku_stock_query.py` | 全球站SKU库存查询。 |
| 规格多语言（`temu.local.goods.spec.info.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.spec.info.get` | `references/apis/temu-local-goods-spec-info-get.md` | `scripts/global_manage_spec_info_get.py` | 全球站规格多语言。 |
| 库存编辑（`bg.local.goods.stock.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.stock.edit` | `references/apis/bg-local-goods-stock-edit.md` | `scripts/global_manage_stock_edit.py` | 全球站库存编辑。 |
| 视频封面（`bg.local.goods.videocoverimage.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.videocoverimage.get` | `references/apis/bg-local-goods-videocoverimage-get.md` | `scripts/global_manage_videocoverimage_get.py` | 全球站视频封面。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md#接口加签文件下载` | `scripts/temu_global_file_download.py` / `scripts/temu_file_download.py` | 获取 Temu 加签资源的下载结果。 |


通用入口 `scripts/temu_global_proxy.py` 与 `scripts/temu_proxy.py` 复用已有转发接口；`scripts/check_linkfox_token.py` 通过同端点最小探测，不增加业务操作。官方目录和文档编号见 `references/partner-global-catalog.md`。

## 前置条件

先确定目标店铺、全球区域、商品与 SKU，以及用户希望读取或修改的内容。准备 LinkFox 用户密钥与 Temu 店铺令牌；Temu 令牌需在卖家后台手动授权复制，可使用本地 store 保存，见 `references/access-token.md` 与 `references/authorization-flow.md`。两套令牌的用途不同。

## 商品管理流程

1. 确认店铺和区域，按任务选择商品或 SKU 列表，取得目标商品标识。
2. 读取商品详情；编辑前核对线上版本与审核中版本，按需查询规格、类目或属性关系。
3. 只改指定内容时使用局部编辑；全量编辑先读取详情并准备完整商品和 SKU 数据。
4. 按用户任务修改库存、上下架、预售或删除；逐条解释商品和 SKU 结果，结果不明确时先查询现状。
5. 需要确认发布结果时查询发布状态；合规任务先查待补项，再提交用户提供的资料。车型属性按层级模板、关系值、已选关系、编辑写回的顺序处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次；业务脚本始终关闭响应缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续查询时先核对任务范围与失败原因。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-manage-product-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、响应中可用的常见计数字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分区域和令牌用途**：全球区与美国、欧洲的同名操作不能直接互换；商品库存令牌与订单发货令牌分别授权、分别保存。
- **解释商品结构**：详情返回和编辑请求的层级不同，按接口文档重新组装；区分整品与单 SKU 的影响。
- **说明更新影响**：全量更新要求完整资料，局部更新只提交指定字段；提交接受、审核通过和最终可销售是不同状态。
- **清晰展示数据**：注明店铺、区域与返回范围，用表格展示商品、SKU、状态、库存和逐条操作结果。分页模型、枚举和字段限制见各接口定义。
- **保留错误上下文**：分别解释网关错误和 Temu 业务结果；未展开的字段不推测补造。批量操作单独列出成功、失败及冲突项。
- **响应缓存**：本技能业务脚本始终关闭响应缓存，不复用读取或写入结果。具体兼容参数、输出路径和 CLI 约定见 `references/api.md#运行约定`。

## 使用示例

### 查看商品并核对发布状态

用户：找出全球区店铺里这个商品，看看当前线上资料和发布状态。

检索列表定位商品，读取线上详情，再按任务查询发布状态，说明结果和本次范围。

### 修改标题或完整资料

用户：把这个商品标题改成我提供的新标题。

核对店铺与商品，按局部编辑文档准备标题修改，说明提交结果；只有用户要求全量更新时才准备完整资料。

### 调整库存与上下架

用户：给指定 SKU 增加库存，然后下架我指定的另一个 SKU。

核对各操作目标，分别处理库存和上下架，展示每个 SKU 的结果；结果不明时先查询当前状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
