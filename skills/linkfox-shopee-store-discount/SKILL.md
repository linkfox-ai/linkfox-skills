---
name: linkfox-shopee-store-discount
description: 管理已授权 Shopee（虾皮）店铺的折扣促销活动，支持活动创建、列表与详情查询、修改、提前结束、删除、参与商品维护和 SIP 跨境折扣设置。适用于店铺限时打折、Discount 促销与既有折扣管理；不适用于店铺授权、其他促销模块或商品刊登维护。
---
# Shopee 店铺折扣促销管理

## 适用范围

### 适用

管理用户已授权 Shopee 店铺的 Discount 活动、活动商品及 SIP 跨境折扣。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 为这些商品创建限时折扣 | 创建活动，再添加参与商品并核对活动状态。 |
| 看看店铺正在进行的折扣 | 查询活动列表和指定活动详情。 |
| 修改活动或商品折扣 | 更新活动设置或参与商品。 |
| 提前结束或删除这个折扣 | 核对目标活动并执行对应操作。 |
| 查看或设置 SIP 折扣 | 查询、设置或删除 SIP 跨境折扣。 |

### 边界

店铺授权与选店使用 `linkfox-shopee-store-auth`；商品刊登使用 `linkfox-shopee-store-product`。
Bundle Deal、Voucher、Add-On Deal、Shop Flash Sale、Follow Prize 分别使用 `linkfox-shopee-store-bundle-deal`、`linkfox-shopee-store-voucher`、`linkfox-shopee-store-add-on-deal`、`linkfox-shopee-store-shop-flash-sale`、`linkfox-shopee-store-follow-prize`。

## 接口清单

12 个 Discount 业务操作及 1 个授权状态辅助操作；公共账号引导不计入业务接口清单。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建折扣活动（`add_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/add_discount` | [references/apis/add-discount.md](references/apis/add-discount.md) | `scripts/add_discount.py` | 创建折扣活动。 |
| 添加折扣商品（`add_discount_item`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/add_discount_item` | [references/apis/add-discount-item.md](references/apis/add-discount-item.md) | `scripts/add_discount_item.py` | 添加折扣商品。 |
| 删除折扣活动（`delete_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/delete_discount` | [references/apis/delete-discount.md](references/apis/delete-discount.md) | `scripts/delete_discount.py` | 删除折扣活动。 |
| 移除折扣商品（`delete_discount_item`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/delete_discount_item` | [references/apis/delete-discount-item.md](references/apis/delete-discount-item.md) | `scripts/delete_discount_item.py` | 移除折扣商品。 |
| 查询折扣详情（`get_discount`） | POST `/shopee/developerProxy` → GET path：`api/v2/discount/get_discount` | [references/apis/get-discount.md](references/apis/get-discount.md) | `scripts/get_discount.py` | 查询折扣详情。 |
| 查询折扣活动列表（`get_discount_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/discount/get_discount_list` | [references/apis/get-discount-list.md](references/apis/get-discount-list.md) | `scripts/get_discount_list.py` | 查询折扣活动列表。 |
| 更新折扣活动（`update_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/update_discount` | [references/apis/update-discount.md](references/apis/update-discount.md) | `scripts/update_discount.py` | 更新折扣活动。 |
| 更新折扣商品（`update_discount_item`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/update_discount_item` | [references/apis/update-discount-item.md](references/apis/update-discount-item.md) | `scripts/update_discount_item.py` | 更新折扣商品。 |
| 提前结束折扣活动（`end_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/end_discount` | [references/apis/end-discount.md](references/apis/end-discount.md) | `scripts/end_discount.py` | 提前结束折扣活动。 |
| 查询 SIP 跨境折扣（`get_sip_discounts`） | POST `/shopee/developerProxy` → GET path：`api/v2/discount/get_sip_discounts` | [references/apis/get-sip-discounts.md](references/apis/get-sip-discounts.md) | `scripts/get_sip_discounts.py` | 查询 SIP 跨境折扣。 |
| 设置 SIP 跨境折扣（`set_sip_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/set_sip_discount` | [references/apis/set-sip-discount.md](references/apis/set-sip-discount.md) | `scripts/set_sip_discount.py` | 设置 SIP 跨境折扣。 |
| 删除 SIP 跨境折扣（`delete_sip_discount`） | POST `/shopee/developerProxy` → POST path：`api/v2/discount/delete_sip_discount` | [references/apis/delete-sip-discount.md](references/apis/delete-sip-discount.md) | `scripts/delete_sip_discount.py` | 删除 SIP 跨境折扣。 |
| 查询授权状态（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口查询授权状态storetokens) | `scripts/_shopee_discount_common.py` 的 `resolve_store_tokens` | 查询已绑定授权信息和状态的辅助函数；折扣流程不自动调用。 |

通用入口为 `scripts/discount_api.py`，可选择上述 12 个 Discount 操作。公共规则和授权状态辅助操作见 [references/api.md](references/api.md)。

## 前置条件

**先完成授权并确定店铺**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，检测约定见 `references/api.md`。
确认用户要查询或维护的活动与商品，按操作对应的接口文档准备业务信息。

## 折扣管理流程

1. 明确目标店铺和任务，检查认证技能依赖，选取对应操作。
2. 创建活动时，先用 `add_discount.py` 提交完整活动资料（名称、时间、折扣类型等），再用 `add_discount_item.py` 添加参与商品，最后按任务需要用 `get_discount_list.py` 核对活动状态。
3. 管理现有活动时，用 `get_discount.py` 查询详情，按用户要求用 `update_discount.py` 或 `update_discount_item.py` 修改；需提前结束时使用 `end_discount.py`。
4. 删除活动、移除商品及维护 SIP 折扣时，核对目标后使用各自操作，展示实际返回结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；脚本始终禁用响应缓存，不读取或写入响应缓存数据，公共调用器可能建立空缓存目录。失败或空结果时，不自动修改条件、翻页或连续试探；后续查询按用户任务范围执行，写入结果不确定时先核对状态。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-discount-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层计数字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **明确活动和商品的区别**：活动创建、修改、结束和删除与参与商品维护是不同操作，不根据相近名称替换。
- **区分常规折扣与 SIP**：SIP 为跨境折扣场景，仅按用户任务选择对应操作。
- **清晰展示结果**：标明店铺、活动及操作，用表格列出实际返回的活动或商品信息；保留原始响应供核对，不补造缺失字段。
- **解释提交状态**：分别核对网关状态、Shopee 上游状态及业务错误；判断与错误处理见接口文档。
- **按任务范围维护店铺**：写入前核对用户已明确的目标和内容。结果不确定时保留响应，先查状态，不自动重复写入。
- **说明分页范围**：列表结果仅代表本次返回范围，不将一页数据称为全部活动。
- **脚本运行约定**：依赖检测、认证兼容和响应缓存行为见 `references/api.md`。

## 使用示例

### 创建限时折扣

用户：为我指定的商品创建这段时间的折扣活动。

核对店铺、活动资料和商品，创建活动后添加商品，再按需要查询活动状态，展示各步骤结果。

### 修改或结束现有活动

用户：查看这个折扣活动，并按我提供的内容修改；另一场活动提前结束。

读取对应活动详情，核对不同目标后分别执行修改或结束，说明每个操作结果。

### 查询 SIP 折扣

用户：看看店铺的 SIP 跨境折扣。

查询 SIP 折扣并展示实际数据；需要设置或删除时按用户要求维护。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
