---
name: linkfox-temu-add-product-us
description: 管理 Temu 美国站商品发布与维护，支持推荐 V2 发品、类目属性和规格查询、图片上传、商品列表与详情、商品编辑和迁移、类目映射、SKU 库存及供货价查询，并支持加签文件下载。适用于 Partner US 商品上架准备、创建与维护；不适用于订单、发货和物流履约。
---

# Temu 美国站商品发布与维护

## 适用范围

### 适用

管理已授权 Temu 美国站店铺的商品，覆盖 Partner US Product 菜单的 19 个商品操作，以及加签文件下载。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 在美国站发布这个新品 | 获取类目属性和规格、上传图片，再提交推荐 V2 发品。 |
| 看店铺商品列表或这个货品的详情 | 查询商品资料并说明本次返回范围。 |
| 修改商品属性、敏感属性或产地 | 按目标货品准备对应编辑操作。 |
| 把同主体全托管商品搬到半托管 | 核对目标店铺与迁移资料。 |
| 查库存、调整 SKU 库存、查供货价 | 读取或维护目标商品库存并查询价格。 |
| 根据商品名找类目、查品牌或规格 | 准备上架所需的类目与规格资料。 |

### 边界

订单、发货和物流转交 `linkfox-temu-order-us` 或对应履约技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 |
|------|------|----------|----------|
| 商品列表查询（`temu.goods.list.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.list.get` | `references/product-query-apis.md` | `scripts/us_goods_list.py` |
| 商品详情查询（`temu.goods.detail.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.detail.get` | `references/product-query-apis.md` | `scripts/us_goods_detail.py` |
| 更新商品（`temu.goods.update`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.update` | `references/product-edit-apis.md` | `scripts/us_goods_update.py` |
| 编辑商品属性（`temu.goods.edit.property`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.edit.property` | `references/product-edit-apis.md` | `scripts/us_goods_edit_property.py` |
| 编辑敏感品属性（`temu.goods.edit.sensitive.attr`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.edit.sensitive.attr` | `references/product-edit-apis.md` | `scripts/us_goods_edit_sensitive.py` |
| 半托管货品迁移（`temu.goods.migrate`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.migrate` | `references/product-edit-apis.md` | `scripts/us_goods_migrate.py` |
| 发布商品 V2（`temu.local.goods.v2.add`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.local.goods.v2.add` | `references/product-publish-apis.md` | `scripts/us_goods_add.py` |
| 商品图片上传 V2（`temu.local.goods.image.v2.upload`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.local.goods.image.v2.upload` | `references/product-publish-apis.md` | `scripts/us_goods_image_upload.py` |
| 发布商品（半托管/跨境）（`temu.goods.add`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.add` | `references/product-publish-apis.md` | `scripts/us_goods_add_legacy.py` |
| 获取类目属性模板（`temu.local.product.attributes.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.local.product.attributes.get` | `references/category-spec-apis.md` | `scripts/us_goods_attrs.py` |
| 获取商品规格（`temu.local.product.variation.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.local.product.variation.get` | `references/category-spec-apis.md` | `scripts/us_goods_variation.py` |
| 商品类目树（`bg.goods.cats.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.goods.cats.get` | `references/category-spec-apis.md` | `scripts/us_goods_cats.py` |
| 类目属性模板（跨境 type）（`bg.goods.attrs.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.goods.attrs.get` | `references/category-spec-apis.md` | `scripts/us_goods_attrs_bg.py` |
| 父规格列表（`bg.glo.goods.parentspec.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.glo.goods.parentspec.get` | `references/category-spec-apis.md` | `scripts/us_goods_parent_spec.py` |
| 可绑定品牌（`bg.glo.goods.brand.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.glo.goods.brand.get` | `references/category-spec-apis.md` | `scripts/us_goods_brand.py` |
| 商品类目映射（`bg.goods.category.mapping`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.goods.category.mapping` | `references/category-spec-apis.md` | `scripts/us_goods_category_mapping.py` |
| 虚拟库存查询（`bg.btg.goods.stock.quantity.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.btg.goods.stock.quantity.get` | `references/stock-price-apis.md` | `scripts/us_goods_stock_get.py` |
| 虚拟库存更新（`bg.btg.goods.stock.quantity.update`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.btg.goods.stock.quantity.update` | `references/stock-price-apis.md` | `scripts/us_goods_stock_update.py` |
| 供货价列表（`temu.goods.price.list.get`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.goods.price.list.get` | `references/stock-price-apis.md` | `scripts/us_goods_price_list.py` |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_us_file_download.py`、`scripts/temu_file_download.py` |

通用代理 `scripts/temu_us_proxy.py` 与 `scripts/temu_proxy.py` 复用商品端点，按请求体选择操作，不额外计为商品接口。Partner 文档分区编号见 [接口目录](references/partner-us-catalog.md)。

## 前置条件

先确认目标店铺与业务用途。LinkFox 用户密钥与 Temu 店铺令牌是两套认证；Temu accessToken 需在卖家后台手动获取，无自动 OAuth。授权步骤与本地令牌工具见 [access-token.md](references/access-token.md) 和 [authorization-flow.md](references/authorization-flow.md)。

## 商品操作流程

1. 确认店铺、站点和目标商品；缺少店铺令牌时，使用 `scripts/temu_token_guide.py` 展示对应后台授权步骤，用户复制令牌后可用本地保存脚本登记。
2. 发品先确定叶子类目，再依次获取属性模板、获取规格、上传图片、提交推荐 V2 商品。以属性模板的必填要求准备资料，沿用返回的属性和规格标识。
3. 查询、编辑、迁移或库存操作按用户指定范围选择接口。需要已有商品资料时先读取；同主体迁移须核对来源与目标。
4. 结合网关与 Temu 业务结果说明实际完成情况；保留完整响应，错误或空结果后的进一步调用遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：业务脚本不读写响应缓存，每次调用均会发起请求；同一会话、同一参数组合默认只调用一次。失败或空结果时，不得自动更换关键词、翻页或连续试探；需要继续查询时，先说明原因与范围。写入结果不确定时，先查询当前商品或库存，避免直接重复提交。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-add-product-us-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`，以响应体实际字段为准）、最大列表字段的长度和前 3 条样本。
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

- **区分授权用途**：商品/库存、订单/发货、全托管与本土店令牌对应不同后台应用，按授权参考选择；不要将授权指南推荐站点直接替换成当前美国站任务的目标站点。
- **业务脚本约定**：业务封装的认证、默认值、参数归一化、CLI 与无缓存约定见 [运行约定](references/api.md#运行约定)。业务脚本调用时强制关闭响应缓存，重复写入不会因缓存而被跳过。
- **清晰展示结果**：注明店铺、站点及操作范围；表格展示商品、SKU、库存或价格等实际返回值。发布、编辑、迁移与库存写入根据用户明确范围执行，不将请求完成直接描述为业务成功。
- **保留响应原文**：嵌套业务内容解析失败时保留原文并说明，字段不完整时不补造。接口参数与已知字段以 references 为准，类目动态字段以实际模板和 Partner 文档为准。
- **按需读取数据**：先读落盘摘要，具体字段从 JSON 文件提取；加签文件下载返回网关结果，不声称已将文件下载到本地。

## 使用示例

### 推荐 V2 发品

用户：根据这些资料在美国站上架新品。

确定目标店铺与类目，依次获取属性模板和规格、上传图片，再提交完整商品资料并解释结果。

### 查询并维护库存

用户：查看这个 SKC 的库存，并按我给出的调整表更新。

读取现有库存，核对 SKU 和仓库，按用户指定方式准备调整并提交，展示更新结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
