---
name: linkfox-shopee-store-shop-flash-sale
description: 管理已授权 Shopee（虾皮）店铺的 Shop Flash Sale 秒杀活动，支持查询可用时段和商品参与条件、创建活动、查看活动与商品、添加或更新秒杀商品、更新和删除活动以及移除商品。适用于店铺限时秒杀筹备、活动状态核对和活动维护；不适用于店铺授权、限时折扣、优惠券或商品刊登管理。
---
# Shopee 店铺秒杀 Shop Flash Sale

## 适用范围

### 适用

管理已授权 Shopee 店铺的秒杀活动及活动内商品。用户提到店铺秒杀、Shop Flash Sale、限时秒杀或需要维护 Flash Sale 活动时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查一下可用秒杀时段和商品报名条件 | 活动筹备：读取时段与参与条件。 |
| 在这个时段创建店铺秒杀并加商品 | 活动创建：创建活动后添加商品并核对状态。 |
| 看店铺秒杀列表、详情和参加商品 | 状态查询：展示活动及活动内商品。 |
| 修改活动设置或秒杀商品 | 活动维护：按用户范围更新活动或商品。 |
| 删除活动或移除指定商品 | 活动清理：核对对象后执行指定删除。 |

### 边界

店铺授权与选店使用 `linkfox-shopee-store-auth`；限时折扣使用 `linkfox-shopee-store-discount`，优惠券使用 `linkfox-shopee-store-voucher`，商品刊登使用 `linkfox-shopee-store-product`。Bundle Deal、Follow Prize 等其他促销交给对应促销技能。

## 接口清单

共 11 个秒杀业务操作和 1 个兼容辅助操作；下表区分网关外层 POST 与 Shopee 上游方法。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 获取秒杀时段（`get_time_slot_id`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_flash_sale/get_time_slot_id` | [references/apis/get-time-slot-id.md](references/apis/get-time-slot-id.md) | `scripts/get_time_slot_id.py` | 获取可用秒杀时段编号。 |
| 创建秒杀活动（`create_shop_flash_sale`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/create_shop_flash_sale` | [references/apis/create-shop-flash-sale.md](references/apis/create-shop-flash-sale.md) | `scripts/create_shop_flash_sale.py` | 创建店铺秒杀活动；传入完整请求体。 |
| 查询商品参与条件（`get_item_criteria`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_flash_sale/get_item_criteria` | [references/apis/get-item-criteria.md](references/apis/get-item-criteria.md) | `scripts/get_item_criteria.py` | 查询商品参与秒杀的条件。 |
| 添加秒杀商品（`add_shop_flash_sale_items`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/add_shop_flash_sale_items` | [references/apis/add-shop-flash-sale-items.md](references/apis/add-shop-flash-sale-items.md) | `scripts/add_shop_flash_sale_items.py` | 添加秒杀商品。 |
| 查询秒杀活动列表（`get_shop_flash_sale_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_flash_sale/get_shop_flash_sale_list` | [references/apis/get-shop-flash-sale-list.md](references/apis/get-shop-flash-sale-list.md) | `scripts/get_shop_flash_sale_list.py` | 查询秒杀活动列表；分页与状态筛选。 |
| 查询秒杀活动详情（`get_shop_flash_sale`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_flash_sale/get_shop_flash_sale` | [references/apis/get-shop-flash-sale.md](references/apis/get-shop-flash-sale.md) | `scripts/get_shop_flash_sale.py` | 按 flash_sale_id 查询活动详情。 |
| 查询秒杀商品（`get_shop_flash_sale_items`） | POST `/shopee/developerProxy` → GET path：`api/v2/shop_flash_sale/get_shop_flash_sale_items` | [references/apis/get-shop-flash-sale-items.md](references/apis/get-shop-flash-sale-items.md) | `scripts/get_shop_flash_sale_items.py` | 查询活动内商品。 |
| 更新秒杀活动（`update_shop_flash_sale`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/update_shop_flash_sale` | [references/apis/update-shop-flash-sale.md](references/apis/update-shop-flash-sale.md) | `scripts/update_shop_flash_sale.py` | 更新秒杀活动设置。 |
| 更新秒杀商品（`update_shop_flash_sale_items`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/update_shop_flash_sale_items` | [references/apis/update-shop-flash-sale-items.md](references/apis/update-shop-flash-sale-items.md) | `scripts/update_shop_flash_sale_items.py` | 更新秒杀商品设置。 |
| 删除秒杀活动（`delete_shop_flash_sale`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/delete_shop_flash_sale` | [references/apis/delete-shop-flash-sale.md](references/apis/delete-shop-flash-sale.md) | `scripts/delete_shop_flash_sale.py` | 删除秒杀活动。 |
| 移除秒杀商品（`delete_shop_flash_sale_items`） | POST `/shopee/developerProxy` → POST path：`api/v2/shop_flash_sale/delete_shop_flash_sale_items` | [references/apis/delete-shop-flash-sale-items.md](references/apis/delete-shop-flash-sale-items.md) | `scripts/delete_shop_flash_sale_items.py` | 移除秒杀商品。 |
| 查询店铺授权状态（`storeTokens`，兼容辅助操作） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口查询店铺授权状态storetokens) | `scripts/_shopee_shop_flash_sale_common.py` 中的 `resolve_store_tokens()` | 辅助函数入口；秒杀 CLI 不自动调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测及兼容约定见 [references/api.md](references/api.md)。

## 执行流程

1. 确认用户指定的店铺和活动任务，完成授权依赖检查。
2. 创建活动时，先用 `scripts/get_time_slot_id.py` 查询可用时段；需要核对商品资格时，用 `scripts/get_item_criteria.py` 查询参与条件。
3. 根据用户选定的时段与活动资料，用 `scripts/create_shop_flash_sale.py` 创建活动，再用 `scripts/add_shop_flash_sale_items.py` 添加指定商品。
4. 用 `scripts/get_shop_flash_sale_list.py` 核对活动状态；按任务需要读取活动详情和活动内商品。
5. 维护现有活动时，按用户范围选择更新活动、更新商品、移除商品或删除活动，说明实际返回结果。具体请求要求见对应接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；本技能脚本不读取或写入响应缓存。失败或空结果时，不得自动更换查询条件、翻页或连续试探；需要继续查询时，按用户任务范围执行，不自动重放写操作。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-shop-flash-sale-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分活动与商品**：Shop Flash Sale 是店铺秒杀活动；时段、活动和活动内商品分别管理，更新或删除活动与更新或移除商品是不同操作。
- **清晰展示数据**：注明店铺、活动、所选时段和实际返回状态；按需用表格展示活动及商品数据，不补造缺失信息。
- **按用户范围维护店铺**：创建、更新、添加、删除均会改变店铺数据；核对用户指定对象及操作内容，保留已获得的数据和错误线索。
- **解释返回结果**：区分 LinkFox 请求完成、Shopee 上游响应和活动业务结果；状态判断及解析约定见 [references/api.md](references/api.md)。
- **运行细节**：通用入口、认证兼容、数据保存与缓存约定见 [references/api.md](references/api.md#脚本运行约定)。

## 使用示例

### 创建店铺秒杀

用户：查可用时段，在我选的时段创建秒杀并加入这些商品。

确认店铺，查询时段并按需查看参与条件；取得用户选择和业务资料后创建活动、添加指定商品，再查询活动列表核对结果。

### 查询现有活动

用户：查看这家店铺的秒杀活动，以及指定活动的商品。

按用户要求查询列表、活动详情和活动内商品，说明本次返回范围和可用状态信息。

### 更新或删除活动和商品

用户：修改这个活动的设置，移除我指定的商品。

核对店铺、活动与商品，分别选择活动更新和商品移除操作；按实际响应解释结果，不将代理转发完成直接当作业务成功。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
