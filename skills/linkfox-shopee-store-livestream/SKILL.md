---
name: linkfox-shopee-store-livestream
description: 管理已授权 Shopee（虾皮）店铺的直播场次、直播商品、展示商品、商品集、评论互动和直播指标，支持直播图片上传、创建与更新场次、开播与结束、评论与禁言。适用于 Shopee Livestream 直播准备、直播中运营和直播数据查看；不适用于店铺授权、短视频发布、通用媒体上传或商品刊登管理。
---
# Shopee 店铺直播管理

## 适用范围

### 适用

管理已授权 Shopee 店铺的 Livestream 直播。用户希望创建或维护直播、调整直播商品、进行评论互动或查看场次表现时使用，无需明确提及 Livestream。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 准备封面、创建直播并开播 | 直播准备：上传图片、创建场次、添加商品并开始直播。 |
| 调整这场直播的商品或商品集 | 商品管理：添加、移除、更新、展示商品或应用商品集。 |
| 看最新评论，回复或管理评论 | 直播互动：评论读取、发表评论、禁言或解除禁言。 |
| 看这场直播和商品的表现 | 数据查看：场次详情、场次指标和商品指标。 |
| 修改或结束这场直播 | 场次维护：更新直播场次或结束直播。 |

### 边界

店铺授权由 `linkfox-shopee-store-auth` 完成；店铺短视频使用 `linkfox-shopee-store-video`，通用 Media / MediaSpace 上传使用对应媒体技能，商品刊登使用 `linkfox-shopee-store-product`。

## 接口清单

25 个直播转发操作，另提供 1 个兼容令牌查询操作；通用入口只分派这 25 个直播操作。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 上传直播图片（`upload_image`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/upload_image` | [references/apis/upload-image.md](./references/apis/upload-image.md) | `scripts/upload_image.py` | 上传直播图片。 |
| 创建直播场次（`create_session`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/create_session` | [references/apis/create-session.md](./references/apis/create-session.md) | `scripts/create_session.py` | 创建直播场次。 |
| 更新直播场次（`update_session`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/update_session` | [references/apis/update-session.md](./references/apis/update-session.md) | `scripts/update_session.py` | 更新直播场次。 |
| 开始直播（`start_session`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/start_session` | [references/apis/start-session.md](./references/apis/start-session.md) | `scripts/start_session.py` | 开始直播。 |
| 结束直播（`end_session`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/end_session` | [references/apis/end-session.md](./references/apis/end-session.md) | `scripts/end_session.py` | 结束直播。 |
| 获取场次详情（`get_session_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_session_detail` | [references/apis/get-session-detail.md](./references/apis/get-session-detail.md) | `scripts/get_session_detail.py` | 获取场次详情。 |
| 添加直播商品（`add_item_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/add_item_list` | [references/apis/add-item-list.md](./references/apis/add-item-list.md) | `scripts/add_item_list.py` | 添加直播商品。 |
| 删除直播商品（`delete_item_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/delete_item_list` | [references/apis/delete-item-list.md](./references/apis/delete-item-list.md) | `scripts/delete_item_list.py` | 删除直播商品。 |
| 更新直播商品列表（`update_item_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/update_item_list` | [references/apis/update-item-list.md](./references/apis/update-item-list.md) | `scripts/update_item_list.py` | 更新直播商品列表。 |
| 获取商品数量（`get_item_count`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_item_count` | [references/apis/get-item-count.md](./references/apis/get-item-count.md) | `scripts/get_item_count.py` | 获取商品数量。 |
| 获取商品列表（`get_item_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_item_list` | [references/apis/get-item-list.md](./references/apis/get-item-list.md) | `scripts/get_item_list.py` | 获取商品列表。 |
| 更新展示商品（`update_show_item`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/update_show_item` | [references/apis/update-show-item.md](./references/apis/update-show-item.md) | `scripts/update_show_item.py` | 更新展示商品。 |
| 删除展示商品（`delete_show_item`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/delete_show_item` | [references/apis/delete-show-item.md](./references/apis/delete-show-item.md) | `scripts/delete_show_item.py` | 删除展示商品。 |
| 获取展示商品（`get_show_item`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_show_item` | [references/apis/get-show-item.md](./references/apis/get-show-item.md) | `scripts/get_show_item.py` | 获取展示商品。 |
| 获取点赞商品列表（`get_like_item_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_like_item_list` | [references/apis/get-like-item-list.md](./references/apis/get-like-item-list.md) | `scripts/get_like_item_list.py` | 获取点赞商品列表。 |
| 获取最近展示商品（`get_recent_item_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_recent_item_list` | [references/apis/get-recent-item-list.md](./references/apis/get-recent-item-list.md) | `scripts/get_recent_item_list.py` | 获取最近展示商品。 |
| 获取商品集列表（`get_item_set_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_item_set_list` | [references/apis/get-item-set-list.md](./references/apis/get-item-set-list.md) | `scripts/get_item_set_list.py` | 获取商品集列表。 |
| 获取商品集商品列表（`get_item_set_item_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_item_set_item_list` | [references/apis/get-item-set-item-list.md](./references/apis/get-item-set-item-list.md) | `scripts/get_item_set_item_list.py` | 获取商品集商品列表。 |
| 应用商品集（`apply_item_set`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/apply_item_set` | [references/apis/apply-item-set.md](./references/apis/apply-item-set.md) | `scripts/apply_item_set.py` | 应用商品集。 |
| 获取场次指标（`get_session_metric`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_session_metric` | [references/apis/get-session-metric.md](./references/apis/get-session-metric.md) | `scripts/get_session_metric.py` | 获取场次指标。 |
| 获取场次商品指标（`get_session_item_metric`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_session_item_metric` | [references/apis/get-session-item-metric.md](./references/apis/get-session-item-metric.md) | `scripts/get_session_item_metric.py` | 获取场次商品指标。 |
| 获取最新评论（`get_latest_comment_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/livestream/get_latest_comment_list` | [references/apis/get-latest-comment-list.md](./references/apis/get-latest-comment-list.md) | `scripts/get_latest_comment_list.py` | 获取最新评论。 |
| 发表评论（`post_comment`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/post_comment` | [references/apis/post-comment.md](./references/apis/post-comment.md) | `scripts/post_comment.py` | 发表评论。 |
| 禁言用户（`ban_user_comment`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/ban_user_comment` | [references/apis/ban-user-comment.md](./references/apis/ban-user-comment.md) | `scripts/ban_user_comment.py` | 禁言用户。 |
| 解除用户禁言（`unban_user_comment`） | POST `/shopee/developerProxy` → POST path：`api/v2/livestream/unban_user_comment` | [references/apis/unban-user-comment.md](./references/apis/unban-user-comment.md) | `scripts/unban_user_comment.py` | 解除用户禁言。 |
| 获取店铺令牌（`storeTokens`，兼容辅助操作） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](./references/apis/store-tokens.md) | `scripts/_shopee_livestream_common.py::resolve_store_tokens` | 供 Python 内部兼容调用；直播 CLI 不自动调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查安装依赖；缺失时先安装依赖，再由授权技能完成选店与授权，不在本技能内另行实现授权流程。检测约定和认证兼容见 [references/api.md](./references/api.md)。
根据用户任务确定直播场次、商品、商品集或互动对象，按需读取清单中对应文档。

## 直播操作流程

1. 确认已授权店铺和用户要求的直播操作范围。
2. 创建并开播时，依次上传直播封面或素材、创建场次、添加直播商品、开始直播；后续步骤使用前一步实际返回的信息。
3. 直播中按用户需要切换展示商品、读取最新评论或发表评论、查看场次指标；需要时维护商品集、更新或结束场次。
4. 按接口参考判断响应，再展示本次取得的数据和已完成的操作；失败或结果不确定时停止依赖该结果的后续步骤。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。脚本不读取或保存响应缓存。失败或空结果时，不得自动修改参数或翻页连续试探；需要继续调用时，先向用户说明目的和范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-livestream-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应体顶层实际存在的常见计数（如 `total`）、最大列表字段的长度和前 3 条样本。
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

- **明确直播对象**：Livestream 场次、直播商品、当前展示商品和商品集是不同对象，展示时注明目标店铺、场次和本次操作。
- **清晰展示结果**：用表格展示实际返回的商品、评论或指标；保留缺失与空结果，不推断未返回的数据。
- **区分读取与修改**：创建、更新、开播、结束、商品维护、发表评论与禁言均可能改变直播状态，按用户已授权的业务范围执行。
- **结合两层结果解释**：区分 LinkFox 网关结果、Shopee 上游返回和脚本解析结果；具体判定、参数限制与输出字段见对应接口文档。
- **保留完整数据**：先读摘要，再按需从落盘 JSON 提取字段；兼容令牌查询的持久化内容经过脱敏，内存返回值供兼容调用使用。
- **缓存适用性**：业务封装始终禁用响应缓存；公共调用器可能创建空 `.cache` 目录，具体运行约定见 [references/api.md](./references/api.md#脚本运行约定)。

## 使用示例

### 创建并开播

用户：用这张封面和这些商品创建直播并开播。

确认店铺与资料，依次上传封面、创建场次、添加指定商品并开始直播，每步核对实际返回结果。

### 直播中管理与查看数据

用户：切换展示商品，查看最新评论和本场直播表现。

确认目标场次，按用户要求切换展示商品并读取评论和场次指标，分别展示操作结果和数据。

### 评论互动

用户：在这场直播发表这条评论。

核对店铺、场次和用户提供的评论内容，提交后按实际响应说明结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
