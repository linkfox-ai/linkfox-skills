---
name: linkfox-shopee-store-public
description: 处理 Shopee（虾皮）Public 公共能力，查询 Partner 下已授权店铺、商户和开放平台 IP 段，并支持授权码交换 token、刷新 token 及 resend code 换取 token。适用于 Partner 管理、底层 OAuth 令牌处理和 IP 白名单准备；日常用户授权、店铺商品订单物流操作及 Push 回调配置不属于本技能范围。
---
# Shopee Public 公共模块

## 适用范围

### 适用

处理 Shopee Partner 级公共信息与底层 OAuth 令牌需求。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查询 Partner 下授权了哪些店铺或商户 | 已授权店铺、商户列表。 |
| 用已有授权码换 token，或刷新 token | 底层 OAuth 令牌操作。 |
| 通过 resend code 获取 token | 补发授权码对应的令牌操作。 |
| 配置 Shopee IP 白名单 | 查询开放平台 IP 段。 |

### 边界

日常授权、已授权店铺与授权状态查询优先使用 `linkfox-shopee-store-auth`；店铺订单、商品、物流等使用对应业务技能；Push 回调配置使用 `linkfox-shopee-store-push`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询 Partner 下已授权店铺（`get_shops_by_partner`） | POST `/shopee/developerProxy` -> path：`api/v2/public/get_shops_by_partner`（上游 GET） | [references/apis/get-shops-by-partner.md](references/apis/get-shops-by-partner.md) | `scripts/get_shops_by_partner.py` | 查询 Partner 下已授权店铺。 |
| 查询 Partner 下已授权商户（`get_merchants_by_partner`） | POST `/shopee/developerProxy` -> path：`api/v2/public/get_merchants_by_partner`（上游 GET） | [references/apis/get-merchants-by-partner.md](references/apis/get-merchants-by-partner.md) | `scripts/get_merchants_by_partner.py` | 查询 Partner 下已授权商户。 |
| 使用授权码交换 token（`get_access_token`） | POST `/shopee/developerProxy` -> path：`api/v2/public/get_access_token`（上游 POST） | [references/apis/get-access-token.md](references/apis/get-access-token.md) | `scripts/get_access_token.py` | 使用授权码交换 token。 |
| 刷新 access token（`refresh_access_token`） | POST `/shopee/developerProxy` -> path：`api/v2/public/refresh_access_token`（上游 POST） | [references/apis/refresh-access-token.md](references/apis/refresh-access-token.md) | `scripts/refresh_access_token.py` | 刷新 access token。 |
| 使用 resend code 获取 token（`get_token_by_resend_code`） | POST `/shopee/developerProxy` -> path：`api/v2/public/get_token_by_resend_code`（上游 POST） | [references/apis/get-token-by-resend-code.md](references/apis/get-token-by-resend-code.md) | `scripts/get_token_by_resend_code.py` | 使用 resend code 获取 token。 |
| 查询 Shopee 开放平台 IP 段（`get_shopee_ip_ranges`） | POST `/shopee/developerProxy` -> path：`api/v2/public/get_shopee_ip_ranges`（上游 GET） | [references/apis/get-shopee-ip-ranges.md](references/apis/get-shopee-ip-ranges.md) | `scripts/get_shopee_ip_ranges.py` | 查询 Shopee 开放平台 IP 段。 |
| 查询店铺授权状态（兼容辅助调用） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_public_common.py` 的 `resolve_store_tokens` | 返回授权状态，不返回原始 token；Public 流程不会自动调用。 |

六个 Public 操作也可通过 `scripts/public_api.py` 统一选择。模块与兼容辅助调用总览见 [references/api.md](references/api.md)。

## 前置条件

先运行 `python scripts/check_auth_dependency.py` 检查 `linkfox-shopee-store-auth`；缺失时先安装该依赖，不在本技能另行实现授权。
确定 Partner 需求和已授权的网关操作目标；令牌操作需准备用户已有的完整业务资料。依赖检测与参数要求见各接口文档。

## 操作流程

1. 检查授权技能依赖，确定用户要查询 Partner 店铺、商户、IP 段，还是处理底层 OAuth token。
2. 阅读对应接口文档及 [脚本运行约定](references/api.md#脚本运行约定)，核对目标与资料，选择独立脚本或通用入口；日常授权需求转交授权技能。
3. 在用户任务范围内执行一次请求，保留完整响应，再按网关、转发和 Shopee 业务层分别解释结果。
4. 先查看摘要；需要明细时从保存的 JSON 提取。失败或空结果后，遵守调用约束，不自动连续试探。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；脚本不读取或保存响应缓存，优先复用已保存的完整响应。失败或空结果时，不自动翻页、重试或更换参数；先解释已有结果与失败原因，按用户任务范围确定是否继续。算力规则见下文“算力消耗预估”。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-public-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- UTF-8 JSON 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- UTF-8 JSON 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、存在时的标量状态及计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分公共能力与网关目标**：Public 包含 Partner 和 OAuth 级操作，网关仍须定位已授权的操作目标，具体约定见接口文档。
- **区分响应层次**：网关请求完成、上游转发成功和 OAuth 业务成功分别判断；不因有响应就认定已取得 token。
- **清晰展示数据**：店铺和商户列表用表格展示可用标识及授权信息；IP 段按原值展示，说明用于白名单准备。
- **处理 token 结果**：确认目标并说明令牌操作结果；不把本技能当作完整用户授权流程，也不附带用户未要求的店铺业务操作。
- **保留原始数据**：字段以实际响应为准，不补造列表、令牌或实际响应中不存在的字段。

## 使用示例

### 查询 Partner 店铺或商户

用户：看看这个 Partner 下有哪些已授权店铺。

核对已授权的网关目标，调用店铺列表脚本；需要商户列表时选择商户脚本，展示本次实际返回范围。

### 处理底层 token

用户：用我提供的完整 OAuth 请求资料刷新 token。

核对目标和资料后调用刷新脚本，分别检查转发与业务结果，说明是否成功获取令牌。

### 准备 IP 白名单

用户：查询 Shopee 开放平台 IP 段。

调用 IP 段脚本，展示实际返回内容，供用户配置白名单。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
