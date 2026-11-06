---
name: linkfox-shopee-store-top-picks
description: 管理已授权 Shopee（虾皮）店铺的精选商品 Top Picks 集合，支持查看、创建、更新和删除。适用于店铺精选、热门推荐集合及 top_picks_id 对应集合的维护；不适用于店铺授权、商品刊登、店铺分类或折扣、优惠券等促销活动。
---
# Shopee 精选商品 Top Picks

## 适用范围

### 适用

查看或维护已授权 Shopee 店铺的 Top Picks 集合；用户提到店铺精选、热门推荐或精选集合管理时使用。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看店铺现在有哪些精选集合 | 查看现有集合及本次返回范围。 |
| 把这些商品创建为店铺精选 | 创建用户指定的集合。 |
| 调整这个精选集合里的商品 | 更新指定集合。 |
| 删除这个精选集合 | 删除用户指定的集合。 |

### 边界

店铺授权与选店使用 `linkfox-shopee-store-auth`；商品刊登使用 `linkfox-shopee-store-product`；店铺分类使用 `linkfox-shopee-store-shop-category`；Discount、Voucher、Flash Sale、Follow Prize 等促销使用对应技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 获取精选集合列表（`get_top_picks_list`） | POST `/shopee/developerProxy` -> path：`api/v2/top_picks/get_top_picks_list`；上游 `GET` | [references/apis/get-top-picks-list.md](references/apis/get-top-picks-list.md) | `scripts/get_top_picks_list.py` | 获取精选集合列表。 |
| 创建精选集合（`add_top_picks`） | POST `/shopee/developerProxy` -> path：`api/v2/top_picks/add_top_picks`；上游 `POST` | [references/apis/add-top-picks.md](references/apis/add-top-picks.md) | `scripts/add_top_picks.py` | 创建精选集合。 |
| 更新精选集合（`update_top_picks`） | POST `/shopee/developerProxy` -> path：`api/v2/top_picks/update_top_picks`；上游 `POST` | [references/apis/update-top-picks.md](references/apis/update-top-picks.md) | `scripts/update_top_picks.py` | 更新精选集合。 |
| 删除精选集合（`delete_top_picks`） | POST `/shopee/developerProxy` -> path：`api/v2/top_picks/delete_top_picks`；上游 `POST` | [references/apis/delete-top-picks.md](references/apis/delete-top-picks.md) | `scripts/delete_top_picks.py` | 删除精选集合。 |
| 查询店铺授权状态（兼容辅助操作） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_top_picks_common.py` 的 `resolve_store_tokens` | 返回授权状态，正常精选操作不额外查询。 |

通用入口为 `scripts/top_picks_api.py`，根据用户需要选择操作；接口总览及 Feedback 见 [references/api.md](references/api.md)。

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖，缺失时先安装依赖。确认目标店铺和待维护集合，具体依赖、认证兼容和运行约定见 [references/api.md](references/api.md)。

## 精选集合管理流程

1. 检查授权技能依赖，确认用户指定的店铺和集合管理目标。
2. 使用 `get_top_picks_list.py` 查看现有集合，核对待创建、更新或删除的目标。
3. 根据用户明确的范围，使用 `add_top_picks.py` 创建，或使用 `update_top_picks.py` / `delete_top_picks.py` 维护指定集合。
4. 展示集合信息或操作结果，区分网关转发结果与 Shopee 业务结果；后续读取按用户任务范围执行。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；写入后核查集合或用户要求刷新时，可按任务范围再次读取。业务脚本强制关闭响应缓存，不复用也不保存响应缓存。失败或空结果时，不得自动换参数、翻页或连续试探；需要继续查询时，按用户任务范围执行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-top-picks-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层计数或用量字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **理解业务对象**：Top Picks 是店铺精选商品集合，与商品刊登、店铺分类和促销活动分别管理。
- **保留操作范围**：创建、更新和删除会改变店铺精选集合；核对店铺、目标集合和用户指定内容后执行，不附带其他集合变更。
- **清晰展示数据**：注明店铺，用表格展示实际返回的集合和商品信息；未返回的字段不推测补齐。
- **解释执行结果**：请求完成、转发成功和精选集合操作成功需要分层判断，具体规则见对应接口文档。
- **说明返回范围**：展示本次取得的集合范围；空结果不自动认定系统错误，也不自动翻页试探。
- **业务运行约定**：公共调用器能力与本技能业务封装的实际运行方式见 [运行约定](references/api.md#运行约定)。

## 使用示例

### 查看店铺精选集合

用户：看看这家店铺现在的精选集合。

确定店铺，检查依赖并读取现有集合，展示实际返回的集合信息及本次范围。

### 创建、更新或删除精选集合

用户：把这些商品整理成精选集合，或调整、删除指定集合。

先查看现有集合，核对用户指定的目标和内容，再执行相应操作，并说明网关及 Shopee 返回的结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
