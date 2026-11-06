---
name: linkfox-temu-manage-product-us
description: 管理 Temu 美国站已授权店铺的商品，支持商品与 SKU 查询、局部和全量编辑、删除、库存、上下架、预售、类目预检、属性与车型关系、合规资料、外部编码、视频封面及加签资源下载。适用于美国站商品维护与库存管理；不适用于新商品发布、价格或供货价管理、促销、广告、订单、履约和取消订单，也不用于欧洲站或全球站商品管理。
---

# Temu 美国站商品管理

## 适用范围

### 适用

维护 Temu 美国站已授权店铺的商品资料、可售状态、库存与合规信息，查看商品、SKU、属性、车型关联及视频封面。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查看店铺商品、SKU 或发布状态 | 按任务选商品或 SKU 检索、详情及发布状态查询。 |
| 修改标题、图片、属性或完整资料 | 区分局部修改和全量更新，先读取当前商品。 |
| 增减库存、设定目标库存或开关预售 | 核对商品和 SKU，使用相应库存操作。 |
| 上下架或删除指定商品 | 核对目标店铺及商品，按用户明确范围执行。 |
| 补充合规文件、外部编码或车型关系 | 按需查询待办、属性或车型库后提交维护。 |
| 获取视频封面或加签资源 | 查询视频封面或读取加签下载结果。 |

### 边界

新商品发布使用 `linkfox-temu-add-product-us`；价格/供货价使用 `linkfox-temu-price-us`；促销使用 `linkfox-temu-promotion-us`；广告使用 `linkfox-temu-ads-us`；订单使用 `linkfox-temu-order-us`；履约使用 `linkfox-temu-fulfillment-us`；买家或卖家取消订单使用 `linkfox-temu-cancel-order-us`。欧洲站与全球站商品管理分别使用 `linkfox-temu-manage-product-eu` 和 `linkfox-temu-manage-product-global`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 商品列表（`bg.local.goods.list.query`） | POST `/temu/proxy` → type：`bg.local.goods.list.query`（无独立 path） | `references/apis/bg-local-goods-list-query.md` | `scripts/us_manage_list_query.py` | 商品列表。 |
| 商品列表搜索（Retrieve）（`temu.local.goods.list.retrieve`） | POST `/temu/proxy` → type：`temu.local.goods.list.retrieve`（无独立 path） | `references/apis/temu-local-goods-list-retrieve.md` | `scripts/us_manage_goods_list_retrieve.py` | 商品列表搜索（Retrieve）。 |
| 商品详情（`bg.local.goods.detail.query`） | POST `/temu/proxy` → type：`bg.local.goods.detail.query`（无独立 path） | `references/apis/bg-local-goods-detail-query.md` | `scripts/us_manage_detail_query.py` | 商品详情。 |
| SKU 列表 / Variants（`bg.local.goods.sku.list.query`） | POST `/temu/proxy` → type：`bg.local.goods.sku.list.query`（无独立 path） | `references/apis/bg-local-goods-sku-list-query.md` | `scripts/us_manage_sku_list_query.py` | SKU 列表 / Variants。 |
| SKU 列表搜索（Retrieve）（`temu.local.sku.list.retrieve`） | POST `/temu/proxy` → type：`temu.local.sku.list.retrieve`（无独立 path） | `references/apis/temu-local-sku-list-retrieve.md` | `scripts/us_manage_sku_list_retrieve.py` | SKU 列表搜索（Retrieve）。 |
| 批量查发布状态（`bg.local.goods.publish.status.get`） | POST `/temu/proxy` → type：`bg.local.goods.publish.status.get`（无独立 path） | `references/apis/bg-local-goods-publish-status-get.md` | `scripts/us_manage_publish_status_get.py` | 批量查发布状态。 |
| SKU 库存查询（`temu.local.goods.sku.stock.query`） | POST `/temu/proxy` → type：`temu.local.goods.sku.stock.query`（无独立 path） | `references/apis/temu-local-goods-sku-stock-query.md` | `scripts/us_manage_sku_stock_query.py` | SKU 库存查询。 |
| 库存编辑（`bg.local.goods.stock.edit`） | POST `/temu/proxy` → type：`bg.local.goods.stock.edit`（无独立 path） | `references/apis/bg-local-goods-stock-edit.md` | `scripts/us_manage_stock_edit.py` | 库存编辑。 |
| 部分字段编辑（`bg.local.goods.partial.update`） | POST `/temu/proxy` → type：`bg.local.goods.partial.update`（无独立 path） | `references/apis/bg-local-goods-partial-update.md` | `scripts/us_manage_partial_update.py` | 部分字段编辑。 |
| 全量编辑（`bg.local.goods.update`） | POST `/temu/proxy` → type：`bg.local.goods.update`（无独立 path） | `references/apis/bg-local-goods-update.md` | `scripts/us_manage_goods_update.py` | 全量编辑。 |
| 删除商品（`temu.local.goods.delete`） | POST `/temu/proxy` → type：`temu.local.goods.delete`（无独立 path） | `references/apis/temu-local-goods-delete.md` | `scripts/us_manage_goods_delete.py` | 删除商品。 |
| 规格信息查询（`temu.local.goods.spec.info.get`） | POST `/temu/proxy` → type：`temu.local.goods.spec.info.get`（无独立 path） | `references/apis/temu-local-goods-spec-info-get.md` | `scripts/us_manage_spec_info_get.py` | 规格信息查询。 |
| 类目预检（`bg.local.goods.category.check`） | POST `/temu/proxy` → type：`bg.local.goods.category.check`（无独立 path） | `references/apis/bg-local-goods-category-check.md` | `scripts/us_manage_category_check.py` | 类目预检。 |
| 商品属性获取（`bg.local.goods.property.get`） | POST `/temu/proxy` → type：`bg.local.goods.property.get`（无独立 path） | `references/apis/bg-local-goods-property-get.md` | `scripts/us_manage_property_get.py` | 商品属性获取。 |
| 商品属性关联数据查询（`bg.local.goods.property.relations`） | POST `/temu/proxy` → type：`bg.local.goods.property.relations`（无独立 path） | `references/apis/bg-local-goods-property-relations.md` | `scripts/us_manage_property_relations.py` | 商品属性关联数据查询。 |
| 车型库层级模板（`bg.local.goods.property.relations.level.template`） | POST `/temu/proxy` → type：`bg.local.goods.property.relations.level.template`（无独立 path） | `references/apis/bg-local-goods-property-relations-level-template.md` | `scripts/us_manage_property_relations_level_template.py` | 车型库层级模板。 |
| 关系属性值查询（`bg.local.goods.property.relations.template`） | POST `/temu/proxy` → type：`bg.local.goods.property.relations.template`（无独立 path） | `references/apis/bg-local-goods-property-relations-template.md` | `scripts/us_manage_property_relations_template.py` | 关系属性值查询。 |
| 商品外部编码（Contribution SKU）（`bg.local.goods.out.sn.set`） | POST `/temu/proxy` → type：`bg.local.goods.out.sn.set`（无独立 path） | `references/apis/bg-local-goods-out-sn-set.md` | `scripts/us_manage_out_sn_set.py` | 商品外部编码（Contribution SKU）。 |
| SKU 外部编码（Contribution SKU）（`bg.local.goods.sku.out.sn.set`） | POST `/temu/proxy` → type：`bg.local.goods.sku.out.sn.set`（无独立 path） | `references/apis/bg-local-goods-sku-out-sn-set.md` | `scripts/us_manage_sku_out_sn_set.py` | SKU 外部编码（Contribution SKU）。 |
| 合规商品列表（`bg.local.compliance.goods.list.query`） | POST `/temu/proxy` → type：`bg.local.compliance.goods.list.query`（无独立 path） | `references/apis/bg-local-compliance-goods-list-query.md` | `scripts/us_manage_compliance_list_query.py` | 合规商品列表。 |
| 合规编辑（`bg.local.goods.compliance.edit`） | POST `/temu/proxy` → type：`bg.local.goods.compliance.edit`（无独立 path） | `references/apis/bg-local-goods-compliance-edit.md` | `scripts/us_manage_compliance_edit.py` | 合规编辑。 |
| 商品上下架（`bg.local.goods.sale.status.set`） | POST `/temu/proxy` → type：`bg.local.goods.sale.status.set`（无独立 path） | `references/apis/bg-local-goods-sale-status-set.md` | `scripts/us_manage_sale_status_set.py` | 商品上下架。 |
| 预售状态编辑（`temu.local.goods.pre.sale.status.edit`） | POST `/temu/proxy` → type：`temu.local.goods.pre.sale.status.edit`（无独立 path） | `references/apis/temu-local-goods-pre-sale-status-edit.md` | `scripts/us_manage_pre_sale_status_edit.py` | 预售状态编辑。 |
| 视频封面（`bg.local.goods.videocoverimage.get`） | POST `/temu/proxy` → type：`bg.local.goods.videocoverimage.get`（无独立 path） | `references/apis/bg-local-goods-videocoverimage-get.md` | `scripts/us_manage_videocoverimage_get.py` | 视频封面。 |
| 加签文件下载（fileDownload） | POST `/temu/fileDownload`（无转发 path） | `references/api.md` | `scripts/temu_us_file_download.py` | 读取加签资源下载结果。 |

## 前置条件

先确定已授权店铺及目标商品。LinkFox 用户身份与 Temu 店铺身份分别准备；Temu 授权须由用户在卖家后台取得，步骤及本地令牌工具见 [授权说明](references/access-token.md) 与 [授权流程](references/authorization-flow.md)。网关兼容与脚本运行约定（包括缓存和落盘）见 `references/api.md`，Partner 菜单和官方文档目录见 `references/partner-us-catalog.md`。

## 商品管理流程

1. 确定用户需要查询还是变更，并核对美国站目标店铺、商品及 SKU。
2. 先检索商品列表以定位商品，再按需读取详情、SKU、库存或发布状态，保留编辑前的数据。
3. 根据需求选择局部编辑或全量更新；涉及属性、车型或合规时，先取得相应属性、车型库或待办信息，再按对应文档组装。车型维护依次使用 `bg.local.goods.property.relations.level.template` 取得层级定义、`bg.local.goods.property.relations.template` 逐层查询选项、`bg.local.goods.property.relations` 核对已保存关联，最后通过局部或全量编辑写回；字段与级联条件见各接口文档。
4. 库存、预售、上下架、外部编码和删除按用户明确的范围执行；结果不确定时先查现状，不连续重放写入。
5. 展示每个商品或 SKU 的操作结果及失败项，区分请求完成、单项修改成功和商品最终生效；具体判断见对应接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；本技能业务脚本始终禁用响应缓存，重复执行会再次请求网关。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明追加查询的范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-manage-product-us-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、响应中的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **核对身份**：LinkFox Key 与 Temu accessToken 用途不同；店铺令牌来源、站点、托管类型和用途应一致。授权应用、IP 白名单、有效期与多站点要求见授权说明。
- **保留业务结构差异**：详情读取与编辑请求的组织方式不同；按所选接口文档准备请求，不能将详情原样作为全量编辑数据。
- **选择适当维护方式**：局部更新只改用户指定内容；全量更新准备完整商品资料。库存增量和设定目标库存的影响不同，操作前核对用户意图。
- **说明版本和分页**：区分审核中资料与在售快照，区分页码与游标检索；展示已返回范围和是否还有后续结果。
- **清晰展示数据**：注明店铺、站点、商品及 SKU，用表格展示可用标题、状态、库存、币种与操作结果；不补造响应未提供的字段。
- **按项解释结果**：批量维护展示成功、失败与编码冲突项；合规待办和视频封面缺失按实际数据说明，不把顶层请求完成直接当作全部完成。

## 使用示例

### 查商品并修改标题

用户：找到这个店铺的指定商品，把标题改为我提供的新标题。

定位目标商品并读取详情，按局部编辑文档准备标题变更，执行后展示返回状态与问题。

### 调整库存与预售

用户：把这些 SKU 库存增加指定数量，并查看预售情况。

核对商品和 SKU，读取库存，按用户指定的方式调整，逐项展示结果；查看预售与修改预售分别按任务需要处理。

### 补充合规或维护车型

用户：查看商品缺哪些合规资料，并按我给的文件补齐；另查这个汽车配件的车型关联。

读取合规待办和商品信息，按实际类目要求组织补充资料；车型关联按层级模板、候选属性值、已保存关联的顺序核对，再执行用户要求的变更。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
