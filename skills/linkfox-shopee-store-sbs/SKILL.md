---
name: linkfox-shopee-store-sbs
description: 查询已授权 Shopee（虾皮）店铺的 SBS 绑定仓库、当前库存、库龄、效期报表和库存变动，用于仓储概况、库存积压与临期分析。用户希望查看 SBS 仓储库存数据时使用，无需明确提及 SBS；不适用于店铺授权、物流发货、头程绑定、商品刊登或 FBS 巴西仓储。
---
# Shopee SBS 仓储服务

## 适用范围

### 适用

查看已授权 Shopee 店铺的 SBS 仓储及库存数据，根据需要查询仓库概况与库存分析报表。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看店铺绑定了哪些 SBS 仓库 | 绑定仓库查询。 |
| 查现在的仓库库存 | 当前库存查询。 |
| 哪些库存积压时间长 | 库龄报表。 |
| 查库存效期或临期情况 | 效期报表。 |
| 看库存增减记录 | 库存变动查询。 |

### 边界

店铺授权与选店使用 `linkfox-shopee-store-auth`；物流发货与运单使用 `linkfox-shopee-store-logistics`；头程绑定使用 `linkfox-shopee-store-first-mile`；商品刊登使用 `linkfox-shopee-store-product`；FBS 巴西仓储使用 `linkfox-shopee-store-fbs`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 绑定仓库（`get_bound_whs_info`） | POST `/shopee/developerProxy` -> GET path：`api/v2/sbs/get_bound_whs_info` | [references/apis/get-bound-whs-info.md](references/apis/get-bound-whs-info.md) | `scripts/get_bound_whs_info.py` | 查询 SBS 绑定仓库。 |
| 当前库存（`get_current_inventory`） | POST `/shopee/developerProxy` -> GET path：`api/v2/sbs/get_current_inventory` | [references/apis/get-current-inventory.md](references/apis/get-current-inventory.md) | `scripts/get_current_inventory.py` | 查询 SBS 当前库存。 |
| 效期报表（`get_expiry_report`） | POST `/shopee/developerProxy` -> GET path：`api/v2/sbs/get_expiry_report` | [references/apis/get-expiry-report.md](references/apis/get-expiry-report.md) | `scripts/get_expiry_report.py` | 查询 SBS 效期报表。 |
| 库龄报表（`get_stock_aging`） | POST `/shopee/developerProxy` -> GET path：`api/v2/sbs/get_stock_aging` | [references/apis/get-stock-aging.md](references/apis/get-stock-aging.md) | `scripts/get_stock_aging.py` | 查询 SBS 库龄报表。 |
| 库存变动（`get_stock_movement`） | POST `/shopee/developerProxy` -> GET path：`api/v2/sbs/get_stock_movement` | [references/apis/get-stock-movement.md](references/apis/get-stock-movement.md) | `scripts/get_stock_movement.py` | 查询 SBS 库存变动。 |
| 授权状态辅助查询（`storeTokens`） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_sbs_common.py` 的 `resolve_store_tokens` | 查询后台授权状态，不返回原始令牌；正常 SBS 查询不预先调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内重新实现授权。确认目标店铺或商户与用户希望查看的仓储数据，依赖检查及运行约定见 `references/api.md`。

## 查询流程

1. 确认已授权的目标店铺，以及需要查看的 SBS 仓储数据。
2. 查看仓储概况时，先查询绑定仓库，再查询当前库存。
3. 做库存分析时，按用户需求查询库龄、效期和库存变动；无需执行全部报表。
4. 展示本次返回的数据及可用分析维度，遇到空结果或错误时按接口文档解释，继续查询遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存的响应；脚本不读取或保存响应缓存。失败或空结果时，不得自动更换店铺、翻页或连续试探；需要继续查询时，先说明原因和查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-sbs-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、顶层存在的常见计数（如 `total`、`costToken`），以及非空最大列表字段的长度和前 3 条样本。
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

- **区分仓储体系**：SBS 与 FBS 巴西仓储分别处理，不混用数据。
- **注明数据来源**：展示目标店铺、仓库及实际返回的库存、库龄、效期或变动信息；缺失字段不补造。
- **区分返回层次**：网关响应、Shopee 转发结果和解析后的业务数据分别判断，具体规则见 [references/api.md](references/api.md) 及对应接口文档。
- **按需读取落盘数据**：优先读取摘要，再从完整 JSON 提取所需字段，避免一次载入所有报表。

## 使用示例

### 查看 SBS 仓储概况

用户：看看这个店铺的 SBS 仓库和库存。

确认店铺，依次查询绑定仓库和当前库存，注明仓库归属并展示本次可用库存数据。

### 分析库存积压与临期

用户：分析这家店的库龄和库存效期。

确认店铺，按需获取库龄和效期报表；需要解释库存变化时，在用户任务范围内补充变动记录。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
