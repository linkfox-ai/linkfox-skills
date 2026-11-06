---
name: linkfox-shopee-store-account-health
description: 查询已授权 Shopee（虾皮）店铺的账户健康、店铺绩效与指标来源明细，查看当前季度扣分和处罚历史，定位问题商品刊登及逾期未发货订单。适用于账户健康诊断、违规追踪和履约问题排查；不适用于店铺授权、订单处理、商品刊登维护或店铺基础资料查询。
---
# Shopee 店铺账户健康

## 适用范围

### 适用

查看已授权 Shopee 店铺的账户健康和处罚数据。用户希望了解店铺绩效、追踪异常指标来源或定位受影响订单与商品时使用，无需明确提及 Account Health。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看店铺健康情况，哪些指标没达标 | 绩效总览及异常指标来源。 |
| 这季度为什么扣分，有什么处罚 | 当前季度扣分与处罚记录。 |
| 哪些商品刊登有违规或需要改进 | 问题商品刊登与原因。 |
| 哪些订单已经逾期未发货 | 逾期订单及紧急程度。 |

### 边界

店铺授权使用 `linkfox-shopee-store-auth`，订单处理使用 `linkfox-shopee-store-orders`，商品刊登维护使用 `linkfox-shopee-store-product`，店铺基础信息使用 `linkfox-shopee-store-shop`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 店铺绩效总览（`get_shop_performance`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_shop_performance` | [references/apis/get-shop-performance.md](references/apis/get-shop-performance.md) | `scripts/get_shop_performance.py` | 查询履约、商品刊登、客服等账户健康指标。 |
| 指标来源明细（`get_metric_source_detail`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_metric_source_detail` | [references/apis/get-metric-source-detail.md](references/apis/get-metric-source-detail.md) | `scripts/get_metric_source_detail.py` | 按绩效指标下钻受影响的订单或商品刊登。 |
| 扣分历史（`get_penalty_point_history`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_penalty_point_history` | [references/apis/get-penalty-point-history.md](references/apis/get-penalty-point-history.md) | `scripts/get_penalty_point_history.py` | 查询当前季度扣分记录。 |
| 处罚历史（`get_punishment_history`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_punishment_history` | [references/apis/get-punishment-history.md](references/apis/get-punishment-history.md) | `scripts/get_punishment_history.py` | 查询当前季度进行中或已结束的处罚。 |
| 问题商品刊登（`get_listings_with_issues`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_listings_with_issues` | [references/apis/get-listings-with-issues.md](references/apis/get-listings-with-issues.md) | `scripts/get_listings_with_issues.py` | 定位需要改进的商品刊登。 |
| 逾期订单（`get_late_orders`） | POST `/shopee/developerProxy` -> GET path：`api/v2/account_health/get_late_orders` | [references/apis/get-late-orders.md](references/apis/get-late-orders.md) | `scripts/get_late_orders.py` | 查询逾期未发货订单。 |
| 店铺授权状态兼容查询（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口店铺授权状态兼容查询storetokens) | `scripts/_shopee_account_health_common.py` 的 `resolve_store_tokens()` | 共享辅助函数可查询授权状态；账户健康主流程由代理解析令牌，不额外调用此接口。 |

## 前置条件

**先完成店铺授权并确定查询目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能中另行实现授权流程。依赖检测约定见 `references/api.md`。各操作所需参数见接口清单中的文档。

## 查询流程

1. 通过授权技能确定目标店铺，按用户问题选择查询操作，并读取对应接口文档。
2. 健康概况：先查店铺绩效，对失败指标按返回的指标标识查询来源明细，再按需查逾期订单或问题商品刊登。
3. 逾期订单：查询目标店铺后，按返回的逾期天数优先展示更紧急的订单。
4. 扣分与处罚：查询当前季度扣分记录，再按用户需要查询进行中或已结束的处罚。分页、筛选与必填条件见各接口文档。
5. 展示本次取得的数据、问题线索与查询范围；后续查询遵守成本约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：算力规则见下方“算力消耗预估”。同一会话、同一参数组合默认只调用一次，业务脚本不读取或写入响应缓存；重复查看优先读取已保存文件，需要最新状态时再查询。失败或空结果时，不得自动变更条件、翻页或连续试探；需要扩大查询时，先说明已有结果与待查范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-account-health-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`）、最大列表字段的长度和前 3 条样本；同时展示嵌套网关错误码、消息、上游状态及返回中存在的 `costToken`、`costTime`。
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

- **理解账户健康**：Account Health 包含履约、商品刊登、客服等绩效维度；从总览定位异常，再按需下钻，避免无差别调用全部操作。
- **清晰展示数据**：注明目标店铺和本次查询范围，用表格展示绩效、扣分、处罚、问题商品和逾期订单；字段缺失时如实说明，不补造值。
- **展示紧急程度**：优先展示逾期更久的订单、未达标指标和进行中的处罚；查询结果用于排查，订单或商品的后续处理转交对应技能。
- **区分返回层级**：网关响应、Shopee 上游状态和业务内容分别判断，具体规则见接口文档。无记录不能直接认定店铺完全健康。
- **缓存与复用**：本技能业务封装始终关闭响应缓存；同参数数据优先从已保存文件读取，避免重复请求。CLI 与保存约定见 `references/api.md`。
- **官方资料**：账户健康模块索引为 [v2.account_health.get_shop_performance](https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1)，各接口文档提供对应官方链接。

## 使用示例

### 查看健康概况并定位异常

用户：看看这个店铺哪里不达标。

确定店铺后查询绩效总览，展示失败指标；按用户需要查询指标来源与关联订单或商品问题。

### 查询逾期订单

用户：找出店铺逾期未发货的订单。

确认店铺与查询范围，取得订单后按逾期天数展示紧急程度，说明本页返回范围。

### 查询扣分与处罚

用户：这季度有哪些扣分和还在执行的处罚？

查询当前季度扣分，再查进行中的处罚，分别展示违规来源、扣分变化和处罚起止信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
