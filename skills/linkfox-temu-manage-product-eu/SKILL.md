---
name: linkfox-temu-manage-product-eu
description: 管理 Temu 欧洲站已授权店铺的商品，支持商品与 SKU 查询、部分和全量编辑、删除、库存、上下架、预售、类目预检、属性及车型关联、合规信息、外部编码、视频封面和加签文件下载。适用于 Temu EU 商品维护、库存调整和合规补充；不适用于新品发布、价格调整、促销、广告或订单履约，也不用于美国站或全球站商品管理。
---

# Temu 欧洲站商品管理

## 适用范围

### 适用

维护 Temu 欧洲站已授权店铺的商品与 SKU，覆盖 Partner EU 的 Product > Manage Products。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看店铺商品、SKU 和发布状态 | 列表、详情、SKU、库存与发布状态查询。 |
| 修改商品标题、图片或完整资料 | 部分编辑或全量更新。 |
| 调整库存、上下架或开启预售 | 按商品或 SKU 维护库存与销售状态。 |
| 补合规材料、设置外部编码 | 合规待办查询、资料编辑和商品或 SKU 编码维护。 |
| 查类目是否放错、属性或兼容车型 | 类目预检、属性推荐与关系模板查询。 |
| 获取视频封面、下载加签文件 | 读取视频封面和下载加签资源。 |

### 边界

新品发布使用 `linkfox-temu-add-product-eu`，价格、促销、广告分别使用 `linkfox-temu-price-eu`、`linkfox-temu-promotion-eu`、`linkfox-temu-ads-eu`。订单、税务、自发货和取消订单分别转交对应 EU 技能。美国站与全球站商品管理分别使用 `linkfox-temu-manage-product-us`、`linkfox-temu-manage-product-global`；其他尚无 EU 专用技能的域可使用支持该域的对应 US 技能并指定欧洲站，须先核对其支持范围。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 合规商品列表（`bg.local.compliance.goods.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.compliance.goods.list.query` | [bg-local-compliance-goods-list-query.md](references/apis/bg-local-compliance-goods-list-query.md) | `scripts/eu_manage_compliance_list_query.py` | 合规商品列表。 |
| 类目预检（`bg.local.goods.category.check`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.category.check` | [bg-local-goods-category-check.md](references/apis/bg-local-goods-category-check.md) | `scripts/eu_manage_category_check.py` | 类目预检。 |
| 合规编辑（`bg.local.goods.compliance.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.compliance.edit` | [bg-local-goods-compliance-edit.md](references/apis/bg-local-goods-compliance-edit.md) | `scripts/eu_manage_compliance_edit.py` | 合规编辑。 |
| 商品详情（`bg.local.goods.detail.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.detail.query` | [bg-local-goods-detail-query.md](references/apis/bg-local-goods-detail-query.md) | `scripts/eu_manage_detail_query.py` | 商品详情。 |
| 商品列表（`bg.local.goods.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.list.query` | [bg-local-goods-list-query.md](references/apis/bg-local-goods-list-query.md) | `scripts/eu_manage_list_query.py` | 商品列表。 |
| 商品外部编码（Contribution SKU）（`bg.local.goods.out.sn.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.out.sn.set` | [bg-local-goods-out-sn-set.md](references/apis/bg-local-goods-out-sn-set.md) | `scripts/eu_manage_out_sn_set.py` | 商品外部编码（Contribution SKU）。 |
| 部分字段编辑（`bg.local.goods.partial.update`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.partial.update` | [bg-local-goods-partial-update.md](references/apis/bg-local-goods-partial-update.md) | `scripts/eu_manage_partial_update.py` | 部分字段编辑。 |
| 商品属性获取（`bg.local.goods.property.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.get` | [bg-local-goods-property-get.md](references/apis/bg-local-goods-property-get.md) | `scripts/eu_manage_property_get.py` | 商品属性获取。 |
| 车型库层级模板（`bg.local.goods.property.relations.level.template`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations.level.template` | [bg-local-goods-property-relations-level-template.md](references/apis/bg-local-goods-property-relations-level-template.md) | `scripts/eu_manage_property_relations_level_template.py` | 车型库层级模板。 |
| 关系属性值查询（`bg.local.goods.property.relations.template`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations.template` | [bg-local-goods-property-relations-template.md](references/apis/bg-local-goods-property-relations-template.md) | `scripts/eu_manage_property_relations_template.py` | 关系属性值查询。 |
| 商品属性关联数据查询（`bg.local.goods.property.relations`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.property.relations` | [bg-local-goods-property-relations.md](references/apis/bg-local-goods-property-relations.md) | `scripts/eu_manage_property_relations.py` | 商品属性关联数据查询。 |
| 批量查发布状态（`bg.local.goods.publish.status.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.publish.status.get` | [bg-local-goods-publish-status-get.md](references/apis/bg-local-goods-publish-status-get.md) | `scripts/eu_manage_publish_status_get.py` | 批量查发布状态。 |
| 商品上下架（`bg.local.goods.sale.status.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sale.status.set` | [bg-local-goods-sale-status-set.md](references/apis/bg-local-goods-sale-status-set.md) | `scripts/eu_manage_sale_status_set.py` | 商品上下架。 |
| SKU 列表 / 变体（`bg.local.goods.sku.list.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sku.list.query` | [bg-local-goods-sku-list-query.md](references/apis/bg-local-goods-sku-list-query.md) | `scripts/eu_manage_sku_list_query.py` | SKU 列表 / 变体。 |
| SKU 外部编码（Contribution SKU）（`bg.local.goods.sku.out.sn.set`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.sku.out.sn.set` | [bg-local-goods-sku-out-sn-set.md](references/apis/bg-local-goods-sku-out-sn-set.md) | `scripts/eu_manage_sku_out_sn_set.py` | SKU 外部编码（Contribution SKU）。 |
| 库存编辑（`bg.local.goods.stock.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.stock.edit` | [bg-local-goods-stock-edit.md](references/apis/bg-local-goods-stock-edit.md) | `scripts/eu_manage_stock_edit.py` | 库存编辑。 |
| 全量编辑（`bg.local.goods.update`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.update` | [bg-local-goods-update.md](references/apis/bg-local-goods-update.md) | `scripts/eu_manage_goods_update.py` | 全量编辑。 |
| 视频封面（`bg.local.goods.videocoverimage.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`bg.local.goods.videocoverimage.get` | [bg-local-goods-videocoverimage-get.md](references/apis/bg-local-goods-videocoverimage-get.md) | `scripts/eu_manage_videocoverimage_get.py` | 视频封面。 |
| 删除商品（`temu.local.goods.delete`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.delete` | [temu-local-goods-delete.md](references/apis/temu-local-goods-delete.md) | `scripts/eu_manage_goods_delete.py` | 删除商品。 |
| 商品列表搜索（Retrieve）（`temu.local.goods.list.retrieve`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.list.retrieve` | [temu-local-goods-list-retrieve.md](references/apis/temu-local-goods-list-retrieve.md) | `scripts/eu_manage_goods_list_retrieve.py` | 商品列表搜索（Retrieve）。 |
| 预售状态编辑（`temu.local.goods.pre.sale.status.edit`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.pre.sale.status.edit` | [temu-local-goods-pre-sale-status-edit.md](references/apis/temu-local-goods-pre-sale-status-edit.md) | `scripts/eu_manage_pre_sale_status_edit.py` | 预售状态编辑。 |
| SKU 库存查询（`temu.local.goods.sku.stock.query`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.sku.stock.query` | [temu-local-goods-sku-stock-query.md](references/apis/temu-local-goods-sku-stock-query.md) | `scripts/eu_manage_sku_stock_query.py` | SKU 库存查询。 |
| 规格信息查询（`temu.local.goods.spec.info.get`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.goods.spec.info.get` | [temu-local-goods-spec-info-get.md](references/apis/temu-local-goods-spec-info-get.md) | `scripts/eu_manage_spec_info_get.py` | 规格信息查询。 |
| SKU 列表搜索（Retrieve）（`temu.local.sku.list.retrieve`） | POST `/temu/proxy` → path：`/openapi/router`，type：`temu.local.sku.list.retrieve` | [temu-local-sku-list-retrieve.md](references/apis/temu-local-sku-list-retrieve.md) | `scripts/eu_manage_sku_list_retrieve.py` | SKU 列表搜索（Retrieve）。 |
| 加签文件下载 | POST `/temu/fileDownload` → path：`/temu/fileDownload` | [api.md](references/api.md#接口加签文件下载) | `scripts/temu_eu_file_download.py` | 下载 Temu 加签资源文件。 |

通用兼容入口为 `scripts/temu_eu_proxy.py` 和 `scripts/temu_proxy.py`；通用文件下载入口为 `scripts/temu_file_download.py`。它们复用上列操作，不另计接口。官方目录、菜单编号和文档来源见 [references/partner-eu-catalog.md](references/partner-eu-catalog.md)。

## 前置条件

先确定目标店铺、欧洲站及待查或待维护的商品。LinkFox 用户密钥与 Temu 店铺令牌分开配置；Temu 没有 LinkFox 侧自动 OAuth，须在卖家后台手动授权并复制令牌。授权应用、主账号要求、令牌有效期、多站点授权和 IP 白名单见 [references/access-token.md](references/access-token.md) 与 [references/authorization-flow.md](references/authorization-flow.md)。

可运行 `scripts/temu_token_guide.py` 查看后台步骤；用 `scripts/save_temu_access_token.py`、`scripts/list_temu_access_tokens.py`、`scripts/get_temu_access_token.py` 保存、列出和读取本地令牌。`scripts/check_linkfox_token.py` 用于最小网关探测，探测不是业务操作成功的证明。所需参数和 CLI 约定见接口参考。

## 商品管理流程

1. 目标商品未知时，用商品列表查询或游标检索定位 `goodsId`；已知商品或 SKU 时直接选择所需接口，商品资料编辑按需读取详情。
2. 编辑前区分线上在售版本与审核中的最新版本；按需获取属性、规格、类目预检或车型关系模板。
3. 只改指定内容时使用部分编辑；全量编辑先取得完整详情，整理为编辑请求所需结构后再提交。
4. 按用户任务范围维护库存、上下架或预售；需要合规补充时先查待办，再准备相应材料。删除前核对用户指定的店铺和商品。
5. 展示网关、Temu 请求和逐项操作结果。需要核验时使用已有查询能力，结果不确定时保留错误，不自动重复写入。

车型关联按“层级模板 → 关系属性值 → 商品已关联数据 → 编辑写回”执行；先由类目确定关系库及层级，再按用户选择级联取值，最后对照商品当前关联整理更新。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，并复用已保存结果。所有业务查询和写入均关闭响应缓存。失败或空结果时，不得自动变更参数、翻页或连续试探；先核对已保存响应与任务范围，再决定后续请求，结果不确定时不得自动重复写入。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-manage-product-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **清晰展示数据**：注明店铺和站点，用表格呈现商品、SKU、库存、销售及合规状态；区分商品外部编码与 SKU 外部编码，展示本次范围和可用分页信息。
- **区分读取和写入**：编辑、删除、库存、上下架、预售、合规和编码维护会修改店铺数据，按用户已明确的目标执行。全量编辑与部分编辑的影响不同，详情响应也不能直接作为编辑载荷。
- **区分概念**：页码检索与游标检索、商品属性推荐与发品类目模板、车型层级与属性值、视频标识与规格属性值均有区别。具体字段、类型与限制见相应接口文档。
- **解释结果**：区分请求正常、资料提交成功、审核状态和最终可售；批量操作逐条报告成功、失败及冲突，不把空结果视作系统错误。未展开的官方响应以实际数据为准，不补造字段。
- **响应缓存**：本技能业务封装对所有查询和写入固定传入 `--no-cache`，不读取或写入响应缓存；公共调用器可能创建空缓存目录。同一会话复用已保存结果；后续请求遵守调用约束。

## 使用示例

### 查询商品后修改标题

用户：找到这个商品，把标题改成我提供的新标题。

确定店铺和商品，先查询详情，再按部分编辑结构只提交所需改动，展示返回状态。

### 调整库存和上下架

用户：把指定 SKU 的库存设为目标数量并下架。

核对商品与 SKU，采用目标库存更新，再按用户指定范围下架，分别展示每项结果。

### 补充合规与车型信息

用户：查出需要补合规的商品，并补齐我提供的材料。

先查询待办，按实际要求准备材料；涉及车型时先读取层级、属性值及商品已关联内容，再整理修改。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
