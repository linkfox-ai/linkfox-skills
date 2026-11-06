---
name: linkfox-shopee-store-shop-category
description: 管理已授权 Shopee（虾皮）店铺的自定义分类，支持创建、查看、更新和删除分类，以及向分类添加商品、查询分类商品和移除关联。适用于 Shop Category 维护与分类商品整理；不适用于店铺授权、商品刊登管理、精选 Top Picks 或店铺基础信息查询。
---
# Shopee 店铺分类管理

## 适用范围

### 适用

管理已授权 Shopee 店铺的自定义分类及分类内商品关联。
用户希望整理店铺分类、调整分类设置或维护分类商品时使用，无需明确提及 Shop Category。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 新建一个店铺分类 | 创建分类，再按用户要求添加商品。 |
| 看看店铺有哪些分类、里面有哪些商品 | 查询分类列表与指定分类商品。 |
| 调整分类设置或删除分类 | 核对目标分类后执行指定变更。 |
| 把这些商品加入或移出分类 | 维护商品与分类之间的关联。 |

### 边界

店铺授权转交 `linkfox-shopee-store-auth`；商品刊登管理使用 `linkfox-shopee-store-product`；精选 Top Picks 使用 `linkfox-shopee-store-top-picks`；店铺基础信息使用 `linkfox-shopee-store-shop`。

## 接口清单

分类模块包含 7 个转发操作；公共脚本另提供 1 个授权状态查询辅助接口，共 8 个业务接口（不计公共认证引导与 Feedback）。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建店铺分类（`add_shop_category`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_category/add_shop_category` | [references/apis/add-shop-category.md](references/apis/add-shop-category.md) | `scripts/add_shop_category.py` | 创建店铺分类。 |
| 查看店铺分类列表（`get_shop_category_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_category/get_shop_category_list` | [references/apis/get-shop-category-list.md](references/apis/get-shop-category-list.md) | `scripts/get_shop_category_list.py` | 查看店铺分类列表。 |
| 删除店铺分类（`delete_shop_category`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_category/delete_shop_category` | [references/apis/delete-shop-category.md](references/apis/delete-shop-category.md) | `scripts/delete_shop_category.py` | 删除店铺分类。 |
| 更新店铺分类设置（`update_shop_category`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_category/update_shop_category` | [references/apis/update-shop-category.md](references/apis/update-shop-category.md) | `scripts/update_shop_category.py` | 更新店铺分类设置。 |
| 向分类添加商品（`add_item_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_category/add_item_list` | [references/apis/add-item-list.md](references/apis/add-item-list.md) | `scripts/add_item_list.py` | 向分类添加商品。 |
| 查看分类内商品（`get_item_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_category/get_item_list` | [references/apis/get-item-list.md](references/apis/get-item-list.md) | `scripts/get_item_list.py` | 查看分类内商品。 |
| 从分类移除商品（`delete_item_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_category/delete_item_list` | [references/apis/delete-item-list.md](references/apis/delete-item-list.md) | `scripts/delete_item_list.py` | 从分类移除商品。 |
| 查询店铺授权状态（辅助兼容） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_shop_category_common.py::resolve_store_tokens` | 授权状态查询辅助函数；分类流程不自动调用。 |

通用入口为 `scripts/shop_category_api.py`，操作选择约定见 [接口总览](references/api.md)。

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖。确认目标店铺、分类和需整理的商品，参数和依赖退出约定见 `references/api.md`。

## 店铺分类管理流程

1. 检查授权技能依赖，并核对用户指定的店铺与分类维护范围。
2. 新建分类时先创建分类，再按用户要求添加商品；查看现状时读取分类列表及指定分类的商品。
3. 更新、删除分类或移除商品关联时，按用户明确的目标执行对应操作。
4. 展示分类和商品关联结果；按接口文档区分网关返回、上游响应与业务完成情况。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，业务脚本不读取或保存响应缓存。失败或空结果时，不得自动修改参数、翻页或连续试探；需要继续查询时，先向用户说明原因和查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-shop-category-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体按 UTF-8 编码不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体按 UTF-8 编码超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、已返回的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分分类与刊登**：Shop Category 是店铺自定义分类；移除分类商品关联与删除商品刊登是不同操作。
- **清晰展示数据**：注明店铺，用表格展示返回的分类、商品标识和操作结果；未返回的字段不补造。
- **保留完整响应**：先看摘要，需要字段时再从保存文件提取。具体解析键和状态判断见接口文档。
- **响应缓存**：业务脚本不读取或保存响应缓存，细节见 `references/api.md` 的运行约定。
- **授权与令牌**：由授权技能选店，分类操作交由网关解析令牌。授权状态查询辅助函数只返回授权信息，分类流程不自动调用。

## 使用示例

### 创建分类并添加商品

用户：建一个新品分类，把我指定的商品放进去。

核对店铺及用户提供的分类资料，创建分类后使用返回的分类标识添加指定商品，展示两步操作结果。

### 查看分类商品

用户：看看这个店铺有哪些分类，再查看指定分类的商品。

读取分类列表，再按用户指定范围查询分类商品，展示已返回的数据与查询范围。

### 调整或移除分类关联

用户：把这些商品从指定分类移出。

核对店铺、分类及商品清单，执行移除关联并解释返回结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
