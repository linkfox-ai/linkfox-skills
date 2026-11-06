---
name: linkfox-shopee-store-voucher
description: 管理已授权 Shopee（虾皮）店铺的优惠券 Voucher，支持创建、列表查询、详情查询、更新、提前结束和删除。适用于店铺券、满减券、折扣码和已有 Voucher 活动管理；不适用于店铺授权、限时折扣、套装优惠、加购优惠、店铺秒杀或商品刊登维护。
---
# Shopee 店铺优惠券 Voucher

## 适用范围

### 适用

管理已授权 Shopee 店铺的 Voucher 活动。用户希望创建店铺券、查看活动及详情，或更新、结束、删除指定优惠券时使用，无需明确提及 Voucher。

**场景速查**

| 用户表达 | 操作场景 |
|---|---|
| 给这个店铺创建优惠券 | 根据用户提供的活动配置创建店铺券。 |
| 看店铺有哪些券，查这个券的详情 | 查询列表或指定优惠券。 |
| 修改优惠券设置 | 更新指定优惠券配置。 |
| 提前结束或删除这个券 | 核对目标活动后执行对应操作。 |

### 边界

店铺授权使用 `linkfox-shopee-store-auth`；限时折扣使用 `linkfox-shopee-store-discount`；套装优惠使用 `linkfox-shopee-store-bundle-deal`；加购优惠使用 `linkfox-shopee-store-add-on-deal`；店铺秒杀使用 `linkfox-shopee-store-shop-flash-sale`；商品刊登使用 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建优惠券（`add_voucher`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/add_voucher`；上游 POST | [references/apis/add-voucher.md](references/apis/add-voucher.md) | `scripts/add_voucher.py` | 创建店铺券，准备完整优惠券配置。 |
| 删除优惠券（`delete_voucher`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/delete_voucher`；上游 POST | [references/apis/delete-voucher.md](references/apis/delete-voucher.md) | `scripts/delete_voucher.py` | 删除指定店铺优惠券。 |
| 提前结束优惠券（`end_voucher`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/end_voucher`；上游 POST | [references/apis/end-voucher.md](references/apis/end-voucher.md) | `scripts/end_voucher.py` | 提前结束指定优惠券活动。 |
| 查询优惠券详情（`get_voucher`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/get_voucher`；上游 GET | [references/apis/get-voucher.md](references/apis/get-voucher.md) | `scripts/get_voucher.py` | 按 voucher_id 查看优惠券详情。 |
| 查询优惠券列表（`get_voucher_list`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/get_voucher_list`；上游 GET | [references/apis/get-voucher-list.md](references/apis/get-voucher-list.md) | `scripts/get_voucher_list.py` | 查看优惠券列表，按上游支持的条件分页或筛选状态。 |
| 更新优惠券（`update_voucher`） | POST `/shopee/developerProxy` → path：`api/v2/voucher/update_voucher`；上游 POST | [references/apis/update-voucher.md](references/apis/update-voucher.md) | `scripts/update_voucher.py` | 更新优惠券配置。 |
| 查询选店授权状态（辅助接口） | POST `/shopee/storeTokens` | [references/api.md](references/api.md) | `scripts/_shopee_voucher_common.py` 中 `resolve_store_tokens` | 查询授权状态，不返回原始令牌；优惠券主流程不主动调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖。核对用户指定的店铺与优惠券活动，按对应接口文档准备操作信息。依赖检测和兼容约定见 `references/api.md`。

## 优惠券管理流程

1. 确定目标店铺和用户要求的操作，完成依赖检查与选店。
2. 创建活动时，使用 `add_voucher.py` 提交用户提供的完整优惠券配置。
3. 使用 `get_voucher_list.py` 查看活动列表，按需通过 `get_voucher.py` 核对指定活动详情。
4. 根据用户要求，使用 `update_voucher.py` 更新，或用 `end_voucher.py` 提前结束；需要删除时使用 `delete_voucher.py`。
5. 先核对网关及上游状态，再解释优惠券业务结果。保留完整响应，结果不确定时先核对，避免重复创建或重复修改。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合避免重复调用；脚本不读取或写入响应缓存。失败或空结果时，不得自动改变查询条件或连续翻页试探；后续查询按用户任务范围进行，结果不确定的写入先核对状态，避免重复操作。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-voucher-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 个 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 个 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数与用量字段（如 `total`、`costToken`）、网关状态和错误消息，以及最大列表字段的长度和前 3 条样本。
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

- **运行约定**：本技能的无响应缓存约定、认证兼容和脚本选项见 [运行约定](references/api.md#脚本运行约定)。
- **辨明活动类型**：Voucher 是店铺优惠券，与限时折扣、套装优惠、加购优惠和店铺秒杀分属不同模块。
- **清晰展示数据**：标明目标店铺、优惠券及操作类型，用表格展示实际返回的活动配置、状态与操作结果；不补造缺失字段。
- **区分创建、更新、结束和删除**：这些操作会改变店铺活动，按用户已明确的操作范围执行；接口返回与最终业务结果的区别见对应接口文档。
- **保留查询范围**：列表有后续页时说明本次返回范围，是否继续查询按用户任务范围和调用约束处理。
- **区分业务结果与技术错误**：保留原始网关和 Shopee 错误，不能仅凭解析出响应对象就宣称操作成功。空列表按实际返回说明。

## 使用示例

### 创建并管理优惠券

用户：按我给的配置创建店铺券，之后查看活动并调整设置。

确认店铺与活动配置，创建后查看列表或详情，再根据用户指定的修改内容更新；若用户要求结束活动，则执行提前结束并说明结果。

### 查询或删除指定优惠券

用户：查看这个店铺券的详情，按我的要求删除它。

核对店铺和目标优惠券，查询详情后执行已授权的删除操作，保留响应并解释实际状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
