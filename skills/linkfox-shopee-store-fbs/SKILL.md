---
name: linkfox-shopee-store-fbs
description: 查询已授权 Shopee 巴西店铺的 FBS 仓储状态，支持店铺入驻状态、店铺封禁状态、SKU 封禁状态和发票错误排查。适用于巴西 FBS 入驻核对、仓储阻断诊断和发票问题定位；不适用于店铺授权、SBS 通用仓储库存、物流发货或商品刊登维护。
---
# Shopee FBS 巴西仓储状态查询

## 适用范围

### 适用

查看已授权 Shopee 巴西店铺的 FBS 入驻、封禁及发票状态。用户未明确说“FBS”，但希望核对上述巴西仓储状态时也适用。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 看一下巴西店铺是否入驻 FBS | 查询店铺入驻状态。 |
| 排查店铺或 SKU 为什么被 FBS 阻断 | 按任务范围查询店铺及 SKU 封禁状态。 |
| 看看巴西 FBS 发票有什么错误 | 查询店铺发票错误。 |

### 边界

店铺授权与选店使用 `linkfox-shopee-store-auth`；SBS 通用仓储使用 `linkfox-shopee-store-sbs`；物流发货使用 `linkfox-shopee-store-logistics`；商品刊登使用 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询巴西 FBS 店铺入驻状态（`query_br_shop_enrollment_status`） | POST `/shopee/developerProxy` -> GET path：`api/v2/fbs/query_br_shop_enrollment_status` | [references/apis/query-br-shop-enrollment-status.md](references/apis/query-br-shop-enrollment-status.md) | `scripts/query_br_shop_enrollment_status.py` | 查询巴西 FBS 店铺入驻状态。 |
| 查询巴西 FBS 店铺发票错误（`query_br_shop_invoice_error`） | POST `/shopee/developerProxy` -> GET path：`api/v2/fbs/query_br_shop_invoice_error` | [references/apis/query-br-shop-invoice-error.md](references/apis/query-br-shop-invoice-error.md) | `scripts/query_br_shop_invoice_error.py` | 查询巴西 FBS 店铺发票错误。 |
| 查询巴西 FBS 店铺封禁状态（`query_br_shop_block_status`） | POST `/shopee/developerProxy` -> GET path：`api/v2/fbs/query_br_shop_block_status` | [references/apis/query-br-shop-block-status.md](references/apis/query-br-shop-block-status.md) | `scripts/query_br_shop_block_status.py` | 查询巴西 FBS 店铺封禁状态。 |
| 查询巴西 FBS SKU 封禁状态（`query_br_sku_block_status`） | POST `/shopee/developerProxy` -> GET path：`api/v2/fbs/query_br_sku_block_status` | [references/apis/query-br-sku-block-status.md](references/apis/query-br-sku-block-status.md) | `scripts/query_br_sku_block_status.py` | 查询巴西 FBS SKU 封禁状态。 |
| 店铺授权状态查询兼容（`storeTokens`） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口店铺授权状态查询兼容storetokens) | `scripts/_shopee_fbs_common.py::resolve_store_tokens`（函数，无 CLI） | 返回授权状态，供兼容调用方使用，常规 FBS 查询不调用。 |

## 前置条件

**先完成店铺授权并确定目标**：依赖 `linkfox-shopee-store-auth` 选店。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测约定和接口索引见 [references/api.md](references/api.md)。

## 查询流程

1. 确定用户要核对的巴西店铺和 FBS 问题，先完成依赖检测与选店。
2. 查询整体店铺状态时，按用户任务范围依次查看入驻状态、店铺封禁和 SKU 封禁；仅问其中一项时查询对应操作。
3. 排查发票问题时查询店铺发票错误，结合已取得的状态解释问题。
4. 按接口参考判断网关、上游与业务响应，展示已有数据和未能确认的部分；失败或空结果时遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。脚本不读写响应缓存，同参数再次执行会再次请求。失败或空结果时，不得自动更换条件或翻页连续试探；需要继续查询时，先向用户说明查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-fbs-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **核对范围**：本技能的 FBS 查询面向巴西 BR；FBS 与 SBS 的仓储能力需区分。
- **清晰展示数据**：注明目标店铺、查询项目和返回状态，用表格呈现入驻、封禁或发票错误信息，未返回的业务状态不作推断。
- **区分响应层级**：网关请求完成、Shopee 上游响应正常和业务状态允许使用 FBS 是不同结论，判断方式见各接口文档。
- **保留原始信息**：结合脚本保存的完整响应排查；上游业务字段以实际响应为准，不假设固定 schema，不补造字段或枚举。
- **使用兼容入口**：`scripts/fbs_api.py` 可通过操作名选择同一组查询；所有专用入口与通用入口均保存完整处理结果。参数与运行约定见接口文档。
- **核对运行约定**：缓存及兼容调用行为见 [references/api.md](references/api.md#运行与兼容约定)。

## 使用示例

### 查看巴西 FBS 店铺状态

用户：帮我查一下这个巴西店铺的 FBS 入驻和封禁情况。

确认店铺后，依次查询入驻、店铺封禁及用户需要的 SKU 封禁，汇总实际返回信息。

### 排查发票问题

用户：这个巴西店铺的 FBS 发票报错了，查一下原因。

确认店铺后查询发票错误，展示返回原因及未确认信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
