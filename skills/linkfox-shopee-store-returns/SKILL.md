---
name: linkfox-shopee-store-returns
description: 管理已授权 Shopee（虾皮）店铺的退货退款，支持退货列表与详情、确认退货、提出或接受解决方案、发起或取消争议、凭证处理、退货承运商及逆向物流查询。适用于卖家查看和处理自己店铺的退货退款；不适用于店铺授权、普通订单查询或取消、正向物流发货和商品刊登管理。
---
# Shopee 店铺退货退款管理

## 适用范围

### 适用

查看和处理已授权 Shopee 店铺的退货、退款与争议，并核对相关凭证和逆向物流。
用户给出退货单号，或希望查询店铺退货退款情况时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看一下店铺最近的退货退款 | 退货列表与单条详情。 |
| 确认这笔退货，或给买家提出处理方案 | 查询可用方案，再按用户要求处理。 |
| 对这笔退货发起争议，或取消争议 | 争议原因查询与争议处理。 |
| 上传或查看退货凭证 | 图片转换、凭证上传和查询。 |
| 查退回包裹的物流和运单凭证 | 退货承运商、运单凭证和逆向轨迹。 |

### 边界

店铺授权使用 `linkfox-shopee-store-auth`；普通订单查询和取消使用 `linkfox-shopee-store-orders`；正向物流发货使用 `linkfox-shopee-store-logistics`；商品刊登管理使用 `linkfox-shopee-store-product`。

## 接口清单

共 15 个 Returns 操作及 1 个店铺授权状态辅助接口。共享认证与充值引导不计入业务接口。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询退货退款列表（`get_return_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_return_list` | [references/apis/get-return-list.md](references/apis/get-return-list.md) | `scripts/get_return_list.py` | 查询退货退款列表。 |
| 查询退货退款详情（`get_return_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_return_detail` | [references/apis/get-return-detail.md](references/apis/get-return-detail.md) | `scripts/get_return_detail.py` | 查询退货退款详情。 |
| 确认退货（`confirm`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/confirm` | [references/apis/confirm.md](references/apis/confirm.md) | `scripts/confirm.py` | 确认退货。 |
| 发起退货争议（`dispute`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/dispute` | [references/apis/dispute.md](references/apis/dispute.md) | `scripts/dispute.py` | 发起退货争议。 |
| 查询可用解决方案（`get_available_solutions`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_available_solutions` | [references/apis/get-available-solutions.md](references/apis/get-available-solutions.md) | `scripts/get_available_solutions.py` | 查询可用解决方案。 |
| 提出解决方案（`offer`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/offer` | [references/apis/offer.md](references/apis/offer.md) | `scripts/offer.py` | 提出解决方案。 |
| 接受解决方案（`accept_offer`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/accept_offer` | [references/apis/accept-offer.md](references/apis/accept-offer.md) | `scripts/accept_offer.py` | 接受解决方案。 |
| 转换凭证图片（`convert_image`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/convert_image` | [references/apis/convert-image.md](references/apis/convert-image.md) | `scripts/convert_image.py` | 转换凭证图片。 |
| 上传退货凭证（`upload_proof`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/upload_proof` | [references/apis/upload-proof.md](references/apis/upload-proof.md) | `scripts/upload_proof.py` | 上传退货凭证。 |
| 查询退货凭证（`query_proof`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/query_proof` | [references/apis/query-proof.md](references/apis/query-proof.md) | `scripts/query_proof.py` | 查询退货凭证。 |
| 查询争议原因（`get_return_dispute_reason`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_return_dispute_reason` | [references/apis/get-return-dispute-reason.md](references/apis/get-return-dispute-reason.md) | `scripts/get_return_dispute_reason.py` | 查询争议原因。 |
| 取消退货争议（`cancel_dispute`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/cancel_dispute` | [references/apis/cancel-dispute.md](references/apis/cancel-dispute.md) | `scripts/cancel_dispute.py` | 取消退货争议。 |
| 查询退货承运商（`get_shipping_carrier`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_shipping_carrier` | [references/apis/get-shipping-carrier.md](references/apis/get-shipping-carrier.md) | `scripts/get_shipping_carrier.py` | 查询退货承运商。 |
| 上传退货运单凭证（`upload_shipping_proof`） | POST `/shopee/developerProxy` → POST path：`api/v2/returns/upload_shipping_proof` | [references/apis/upload-shipping-proof.md](references/apis/upload-shipping-proof.md) | `scripts/upload_shipping_proof.py` | 上传退货运单凭证。 |
| 查询逆向物流轨迹（`get_reverse_tracking_info`） | POST `/shopee/developerProxy` → GET path：`api/v2/returns/get_reverse_tracking_info` | [references/apis/get-reverse-tracking-info.md](references/apis/get-reverse-tracking-info.md) | `scripts/get_reverse_tracking_info.py` | 查询逆向物流轨迹。 |
| 查询店铺授权状态（辅助） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_returns_common.py`（`resolve_store_tokens`） | 返回授权状态；Returns 主流程不额外调用。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；检测结果为缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测和兼容调用约定见 `references/api.md`。
确认用户指定的店铺、退货退款事项及处理范围；所需信息见相应接口文档。

## 退货退款处理流程

1. 用户已提供退货单号时直接读取目标退货详情；需要发现或选择退货事项时，先查询列表，再读取目标详情。
2. 处理退货前查询可用解决方案；按用户要求确认退货、提出或接受方案，需要争议处理时查询原因并发起或取消争议。
3. 按任务需要转换图片、上传或查询凭证；涉及退回包裹时，按需查询承运商、上传运单凭证或查看逆向物流。
4. 按接口文档依次判断网关响应、Shopee 上游状态和业务内容，再向用户说明结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次；业务封装始终禁用响应缓存，每次执行都会请求接口。失败或空结果时，不得自动更换条件、翻页或连续试探；后续查询按用户任务范围执行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-returns-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分退货与普通订单**：本技能处理退货、退款和争议；普通订单及正向发货按适用边界转交。
- **选店链路**：通过已授权店铺转发，由服务端解析令牌，再经紫鸟 `shopee-proxy` 转到 Shopee；授权状态辅助查询不返回原始令牌。实际调用约定见 `references/api.md`。
- **核对处理范围**：确认、方案、争议和上传凭证会影响目标退货事项，按用户已明确的范围执行。
- **清晰展示结果**：注明店铺和退货单号，用表格呈现实际返回的退货状态、方案、凭证或物流节点；区分网关请求完成和上游业务处理结果，不补造缺失内容。
- **说明返回范围**：列表展示本次返回范围和可用分页线索；空结果或失败按接口文档解释，后续调用遵守调用约束。
- **使用现有入口**：独立操作脚本与 `scripts/returns_api.py` 通用入口使用同一业务封装；缓存、参数映射及保存位置的实际运行约定见 `references/api.md`。

## 使用示例

### 查看店铺退货及详情

用户：列出最近的退货，并查看其中一笔的详细情况。

确认店铺，先查询列表，再按选定退货单号查看详情，展示实际状态与返回范围。

### 确认退货或处理争议

用户：查看这笔退货的可处理方案，按我指定的方案处理。

读取详情和可用方案，核对用户指定的处理内容后提交；需要争议时按任务查询争议原因并处理，解释上游返回结果。

### 查看凭证和逆向物流

用户：查这笔退货的凭证与退回包裹轨迹。

查询凭证和逆向物流；用户要求补充材料时，再根据已有材料准备相应上传内容。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
