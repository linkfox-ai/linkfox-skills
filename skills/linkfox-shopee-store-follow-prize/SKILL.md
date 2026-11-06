---
name: linkfox-shopee-store-follow-prize
description: 管理已授权 Shopee（虾皮）店铺的关注有礼 Follow Prize 活动，支持创建、列表查询、详情查询、更新、提前结束和删除。适用于关注送券、粉丝福利活动的查询与维护；店铺授权、其他促销活动和商品刊登维护使用对应技能。
---
# Shopee 关注有礼 Follow Prize

## 适用范围

### 适用

管理已授权 Shopee 店铺的关注有礼活动。用户希望查询或维护 Follow Prize、关注送券或粉丝福利时使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 为店铺创建关注送券活动 | 创建关注有礼活动。 |
| 看看当前关注有礼活动 | 查询列表及可用活动状态。 |
| 查看这个活动的详情 | 查询指定活动。 |
| 调整、提前结束或删除指定活动 | 按用户要求维护活动。 |

### 边界

店铺授权使用 `linkfox-shopee-store-auth`；限时折扣、组合优惠、优惠券和店铺秒杀使用对应促销技能，其中 Discount、Voucher、Shop Flash Sale 分别为 `linkfox-shopee-store-discount`、`linkfox-shopee-store-voucher`、`linkfox-shopee-store-shop-flash-sale`。商品刊登使用 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建关注有礼活动（`add_follow_prize`） | POST `/shopee/developerProxy` -> 上游 POST，path：`api/v2/follow_prize/add_follow_prize` | [references/apis/add-follow-prize.md](./references/apis/add-follow-prize.md) | `scripts/add_follow_prize.py` | 创建关注有礼活动。 |
| 删除关注有礼活动（`delete_follow_prize`） | POST `/shopee/developerProxy` -> 上游 POST，path：`api/v2/follow_prize/delete_follow_prize` | [references/apis/delete-follow-prize.md](./references/apis/delete-follow-prize.md) | `scripts/delete_follow_prize.py` | 删除关注有礼活动。 |
| 提前结束关注有礼活动（`end_follow_prize`） | POST `/shopee/developerProxy` -> 上游 POST，path：`api/v2/follow_prize/end_follow_prize` | [references/apis/end-follow-prize.md](./references/apis/end-follow-prize.md) | `scripts/end_follow_prize.py` | 提前结束关注有礼活动。 |
| 更新关注有礼活动（`update_follow_prize`） | POST `/shopee/developerProxy` -> 上游 POST，path：`api/v2/follow_prize/update_follow_prize` | [references/apis/update-follow-prize.md](./references/apis/update-follow-prize.md) | `scripts/update_follow_prize.py` | 更新关注有礼活动。 |
| 查询关注有礼详情（`get_follow_prize_detail`） | POST `/shopee/developerProxy` -> 上游 GET，path：`api/v2/follow_prize/get_follow_prize_detail` | [references/apis/get-follow-prize-detail.md](./references/apis/get-follow-prize-detail.md) | `scripts/get_follow_prize_detail.py` | 查询关注有礼详情。 |
| 查询关注有礼列表（`get_follow_prize_list`） | POST `/shopee/developerProxy` -> 上游 GET，path：`api/v2/follow_prize/get_follow_prize_list` | [references/apis/get-follow-prize-list.md](./references/apis/get-follow-prize-list.md) | `scripts/get_follow_prize_list.py` | 查询关注有礼列表。 |
| 查询店铺授权状态（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](./references/api.md) | `scripts/_shopee_follow_prize_common.py` 的 `resolve_store_tokens` | 辅助函数；活动操作由服务端解析令牌，不自动追加此调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖。确定用户指定的店铺与活动，所需信息、依赖检测约定及各接口定义见 `references/api.md` 和接口清单。

## 活动管理流程

1. 完成依赖检查和选店，按用户目标选择创建、查询或维护操作。
2. 创建活动时准备完整活动资料，使用 `scripts/add_follow_prize.py` 提交。
3. 按任务需要使用 `scripts/get_follow_prize_list.py` 查看活动列表，或用详情脚本核对指定活动。
4. 用户要求调整或结束活动时，使用 `scripts/update_follow_prize.py` 或 `scripts/end_follow_prize.py`；删除使用 `scripts/delete_follow_prize.py`，展示返回结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务封装始终禁用响应缓存。失败或空结果时，不得自动更换条件、翻页或连续试探；需要继续查询时，先向用户说明原因与查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-follow-prize-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应顶层实际存在的计数或用量字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **授权与活动分工**：依赖技能负责授权和选店，本技能负责关注有礼活动；辅助授权状态查询不等于完成店铺授权。
- **清晰展示结果**：注明目标店铺、活动及执行操作，使用响应中实际提供的活动信息和状态，不补造活动字段。
- **解释操作结果**：区分 LinkFox 请求状态、Shopee 上游状态和活动业务结果；状态判断见各接口文档。
- **缓存约定**：业务封装始终禁用响应缓存；具体运行约定见 [references/api.md](./references/api.md#脚本运行约定)。
- **输出约定**：完整响应先落盘，较大结果先读摘要，再从文件按需提取。通用入口为 `scripts/follow_prize_api.py`，用法见接口文档。
- **维护活动范围**：创建、更新、提前结束和删除均改变店铺活动，依据用户已经指定的店铺、活动和操作范围执行。

## 使用示例

### 创建并查看关注有礼活动

用户：按我提供的活动资料创建关注送券活动，并查看创建后的列表。

确定目标店铺，准备完整活动资料并创建，再按用户要求查询列表并展示结果。

### 查询和维护指定活动

用户：查看这个活动的详情，并按我提供的新设置调整。

核对目标店铺与活动，读取详情，依据用户资料更新，说明接口返回的状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
