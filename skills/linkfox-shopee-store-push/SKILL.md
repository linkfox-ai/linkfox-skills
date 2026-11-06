---
name: linkfox-shopee-store-push
description: 管理 Shopee（虾皮）应用的 Push 推送配置，支持设置及读取回调配置、获取丢失推送消息并确认消费。适用于推送回调维护、webhook 配置核对和丢失消息补推管理；不适用于店铺授权、公共 OAuth 或订单与商品业务管理。
---
# Shopee Push 推送机制

## 适用范围

### 适用

管理已授权 Shopee 应用的 Push 配置与补推消息。用户希望维护回调地址、核对推送设置、拉取丢失消息并确认已处理消息时使用，无需明确提及 Push。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 配置 Shopee 推送回调或 webhook | 设置推送配置，再读取配置核对。 |
| 查看当前应用的推送设置 | 查询现有回调与推送配置。 |
| 拉取丢失的推送消息 | 读取补推消息，展示本次返回范围。 |
| 这些补推消息已处理完成 | 确认对应消息已消费。 |

### 边界

用户侧授权使用 `linkfox-shopee-store-auth`，公共 OAuth / Partner 查询使用 `linkfox-shopee-store-public`；订单、商品等操作使用对应业务技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 设置推送配置（`set_app_push_config`） | POST `/shopee/developerProxy` → method：`POST`，path：`api/v2/push/set_app_push_config` | `references/apis/set-app-push-config.md` | `scripts/set_app_push_config.py` | 配置回调地址及推送设置；提交完整请求体。 |
| 获取推送配置（`get_app_push_config`） | POST `/shopee/developerProxy` → method：`GET`，path：`api/v2/push/get_app_push_config` | `references/apis/get-app-push-config.md` | `scripts/get_app_push_config.py` | 读取当前应用的推送配置。 |
| 获取丢失推送消息（`get_lost_push_message`） | POST `/shopee/developerProxy` → method：`GET`，path：`api/v2/push/get_lost_push_message` | `references/apis/get-lost-push-message.md` | `scripts/get_lost_push_message.py` | 读取丢失消息，用于补推处理。 |
| 确认消费丢失推送消息（`confirm_consumed_lost_push_message`） | POST `/shopee/developerProxy` → method：`POST`，path：`api/v2/push/confirm_consumed_lost_push_message` | `references/apis/confirm-consumed-lost-push-message.md` | `scripts/confirm_consumed_lost_push_message.py` | 确认已经处理的补推消息；提交完整请求体。 |
| 店铺令牌兼容查询（`storeTokens`） | POST `/shopee/storeTokens` | `references/api.md` | `scripts/_shopee_push_common.py` 的 `resolve_store_tokens` | 提供令牌兼容查询函数；4 个业务入口不自动调用。 |

## 前置条件

**先完成授权并确定操作目标**：依赖 `linkfox-shopee-store-auth`。运行 `python scripts/check_auth_dependency.py` 检查安装状态，缺失时先安装依赖；授权流程由授权技能负责，本技能不实现授权逻辑。依赖退出码、目标标识和兼容约定见 `references/api.md`。

## 业务流程

1. 确定应用及目标店铺或商户，完成依赖检查与授权；按需读取当前推送配置。
2. 配置回调时，根据用户给定的完整配置设置，再读取配置核对结果。
3. 补推丢失消息时，先拉取消息，处理完成后再确认对应消息已消费；不得将“已拉取”解释为“已消费”。
4. 展示配置核对或补推处理结果；结果不确定时保留响应，按接口参考处理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；本技能不读取或保存响应缓存。失败或空结果时，不得自动修改参数、翻页或连续试探；写入或消费确认结果不确定时，保留响应并核对状态，不自动重发。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-push-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 序列化后的响应不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 序列化后的响应超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层计数字段（如 `total`、`costToken`），以及最大非空列表字段的长度和前 3 条样本。
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

- **区分应用和店铺**：Push 配置与补推通常属于 Partner/App 级；展示时说明应用与授权上下文。
- **清晰展示结果**：注明应用及授权上下文，分别展示当前配置、丢失消息和消费确认结果；仅引用实际返回内容。
- **区分配置写入与消息确认**：根据用户明确的操作范围准备完整配置或消费确认内容，避免错误覆盖配置或确认尚未处理的消息。
- **解释业务状态**：区分 LinkFox 网关响应、Shopee 上游响应和消息实际处理结果；不把网关正常响应直接当成操作成功。
- **兼容入口**：4 个独立业务脚本和通用入口 `scripts/push_api.py` 均保留；CLI、请求体与查询参数映射、无缓存约定见 `references/api.md` 及各接口定义。
- **官方参考**：[Shopee Push 模块](https://open.shopee.com/documents/v2/v2.push.set_app_push_config?module=105&type=1)。上游请求字段以官方定义及用户提供内容为准，响应字段以实际返回为准，不补造参数或响应。

## 使用示例

### 配置并核对回调

用户：将这个应用的推送回调改成我提供的配置。

核对应用及授权上下文，准备完整配置，执行设置后重新读取并展示核对结果。

### 补推并确认消费

用户：拉取丢失消息，处理完成后确认这些消息已消费。

先拉取并展示消息；实际处理完成后，只确认已完成处理的消息，展示确认结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
