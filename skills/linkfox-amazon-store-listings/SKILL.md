---
name: linkfox-amazon-store-listings
description: 管理亚马逊卖家自己的商品刊登，支持单条查询、列表搜索、创建、全量更新、局部修改和删除，检查商品的刊登限制，并查询商品类型及上架属性要求。适用于店铺商品信息维护、销售资格核对和上架准备；不适用于全站商品目录研究、竞品前台数据查询或批量文件提交。
---
# Amazon 店铺刊登与商品类型管理

## 适用范围

### 适用

管理已授权亚马逊卖家店铺的商品刊登及上架要求。
用户希望查看或维护自己店铺的刊登、确认商品能否销售、确定商品类型和所需属性时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 看这个卖家 SKU 的刊登信息和问题 | 单条查询：展示商品资料与可用刊登数据。 |
| 找出店铺里不可购买或有问题的商品 | 列表检索：展示符合条件的刊登及分页情况。 |
| 修改这个商品的标题或其他属性 | 局部修改：根据商品类型要求准备修改内容。 |
| 新建商品，或完整更新现有刊登 | 刊登维护：准备完整属性并解释提交结果。 |
| 删除这个站点的刊登 | 刊登删除：核对目标店铺、商品和站点。 |
| 这个 ASIN 在我的店铺能不能卖 | 资格检查：展示刊登限制及处理线索。 |
| 查这个商品应选哪种类型、上架需要哪些字段 | 上架准备：查询商品类型与属性定义。 |

### 边界

本技能用于卖家自己的刊登管理。全站目录查询使用 `linkfox-amazon-store-catalog`，批量文件提交使用 `linkfox-amazon-store-feeds`；前台竞品研究不属于本技能范围。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 获取单条刊登（`getListingsItem`） | GET `/spApi/developerProxy` -> path：`listings/2021-08-01/items/{sellerId}/{sku}` | `scripts/get_listings_item.py` | 读取卖家单条刊登的商品资料、问题、报价及库存等可用数据。 |
| 搜索刊登列表（`searchListingsItems`） | GET `/spApi/developerProxy` -> path：`listings/2021-08-01/items/{sellerId}` | `scripts/search_listings_items.py` | 按商品标识、关系、时间或状态检索店铺刊登列表。 |
| 部分更新刊登（`patchListingsItem`） | PATCH `/spApi/developerProxy` -> path：`listings/2021-08-01/items/{sellerId}/{sku}` | `scripts/patch_listings_item.py` | 提交指定属性的局部修改。 |
| 创建或全量更新刊登（`putListingsItem`） | PUT `/spApi/developerProxy` -> path：`listings/2021-08-01/items/{sellerId}/{sku}` | `scripts/put_listings_item.py` | 创建刊登或提交完整商品属性进行全量更新。 |
| 删除刊登（`deleteListingsItem`） | DELETE `/spApi/developerProxy` -> path：`listings/2021-08-01/items/{sellerId}/{sku}` | `scripts/delete_listings_item.py` | 删除目标店铺与站点的刊登。 |
| 查询刊登限制（`getListingsRestrictions`） | GET `/spApi/developerProxy` -> path：`listings/2021-08-01/restrictions` | `scripts/get_listings_restrictions.py` | 检查目录商品在目标店铺与站点的销售资格和限制。 |
| 搜索商品类型（`searchDefinitionsProductTypes`） | GET `/spApi/developerProxy` -> path：`definitions/2020-09-01/productTypes` | `scripts/search_definitions_product_types.py` | 按关键词或商品名称查找可用商品类型。 |
| 获取商品类型定义（`getDefinitionsProductType`） | GET `/spApi/developerProxy` -> path：`definitions/2020-09-01/productTypes/{productType}` | `scripts/get_definitions_product_type.py` | 读取商品类型定义及刊登属性要求。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；检测结果为缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测约定见 `references/api.md`。
确认目标店铺、站点及待查或待维护商品；准备上架或属性修改时，按需查看商品类型定义。各接口所需信息见 `references/api.md`。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具会消耗算力。同一会话、同一参数组合默认只调用一次，脚本提供 24 小时本地缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明额外消耗。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-listings-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、响应头的`X-Cost-Credit`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗

不消耗算力。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

用户会因算力消耗而支付费用。需要高频调用或用户对消耗量预期不足时，提醒用户，并由用户决定是否继续。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **清晰展示数据**：注明店铺和站点，用表格展示可用商品资料、刊登问题、销售状态和操作结果。
- **区分读取与写入**：创建、全量更新、局部修改和删除均会改变店铺刊登；根据用户已明确的操作范围准备请求，说明全量更新与局部修改的影响。
- **解释提交结果**：区分请求完成、提交被接受和商品最终可销售；具体状态判断见 `references/api.md`。
- **说明分页情况**：展示本次返回范围和后续页是否可查，按用户任务范围继续查询。
- **处理空结果和错误**：按 `references/api.md` 解释原因与店铺保护措施，保留已取得的数据。

## 使用示例

### 查看单条刊登或搜索店铺商品

用户：查看这个 SKU 的刊登问题，再找出店铺里同类问题商品。

确认店铺和站点，先读取指定刊登，再根据用户要求检索列表，展示问题及返回范围。

### 修改刊登属性

用户：把这个商品的标题修改为我提供的新标题。

确认目标刊登，按需查询商品类型要求，准备局部修改并提交，说明返回的状态与问题。

### 创建或全量更新刊登

用户：按这些商品资料创建新刊登。

确认目标店铺与站点，确定商品类型和完整属性要求，再根据用户资料准备提交；说明接口接受状态与可用校验问题。

### 查询销售资格和上架要求

用户：这个 ASIN 能否在我的店铺销售，上架需要哪些属性？

查询刊登限制及所需商品类型定义，展示资格信息与属性要求，不附带用户未要求的商品变更。

### 删除指定刊登

用户：删除这个站点的指定 SKU 刊登。

核对用户指定的店铺、站点和刊登，执行删除并说明返回状态；结果不确定时按接口参考处理。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
