---
name: linkfox-temu-promotion-eu
description: 管理 Temu 欧洲站已授权店铺的促销活动，支持活动与候选商品查询、商品报名、异步操作结果查询、已报名商品查询，以及活动供货价、活动数量、停用和新增 SKU 的维护，并支持相关加签资源下载。适用于欧洲站促销选品、活动报名和活动商品维护；不适用于广告投放、普通商品管理、供货价维护、订单售后或尚未接入的活动创建与优惠券管理。
---

# Temu 欧洲站电商促销

## 适用范围

### 适用

管理已授权 Temu 欧洲站店铺的促销活动与活动商品。
用户希望查看可参加或已参加的活动、核对候选商品与推荐活动价、报名或调整活动商品时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看欧洲站有哪些活动可以参加 | 查询促销活动与参与情况。 |
| 这个活动有哪些候选商品，建议报什么价格 | 查询候选商品、报名资格和推荐活动供货价。 |
| 把指定商品报名到这个活动 | 按用户指定的商品、SKU、价格和数量报名，随后核对操作结果。 |
| 刚才报名或更新处理好了吗 | 查询异步操作结果与失败原因。 |
| 查看已报名商品，调整活动价或数量 | 查询活动商品后执行指定维护操作。 |
| 下载活动关联的加签文件 | 获取已有的 Temu 加签资源。 |

### 边界

广告投放使用 `linkfox-temu-ads-eu`；普通商品列表、编辑、库存和上下架使用 `linkfox-temu-manage-product-eu`；发品使用 `linkfox-temu-add-product-eu`；日常供货价与定价单使用 `linkfox-temu-price-eu`；订单使用 `linkfox-temu-order-eu`，退货退款使用 `linkfox-temu-returns-refunds-eu`。
美国站或全球站促销分别使用 `linkfox-temu-promotion-us`、`linkfox-temu-promotion-global`。当前已接入的六个促销操作不包含活动创建与优惠券管理。

## 接口清单

| 接口 | 端点与转发操作 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 促销活动查询 | POST `/temu/proxy` → `type=bg.promotion.activity.query` | `references/apis/bg-promotion-activity-query.md` | `scripts/eu_promotion_activity_query.py` | 促销活动查询。 |
| 活动候选商品查询 | POST `/temu/proxy` → `type=bg.promotion.activity.candidate.goods.query` | `references/apis/bg-promotion-activity-candidate-goods-query.md` | `scripts/eu_promotion_activity_candidate_goods_query.py` | 活动候选商品查询。 |
| 活动已报名商品查询 | POST `/temu/proxy` → `type=bg.promotion.activity.goods.query` | `references/apis/bg-promotion-activity-goods-query.md` | `scripts/eu_promotion_activity_goods_query.py` | 活动已报名商品查询。 |
| 活动商品报名 | POST `/temu/proxy` → `type=bg.promotion.activity.goods.enroll` | `references/apis/bg-promotion-activity-goods-enroll.md` | `scripts/eu_promotion_activity_goods_enroll.py` | 活动商品报名。 |
| 活动商品操作结果查询 | POST `/temu/proxy` → `type=bg.promotion.activity.goods.operation.query` | `references/apis/bg-promotion-activity-goods-operation-query.md` | `scripts/eu_promotion_activity_goods_operation_query.py` | 活动商品操作结果查询。 |
| 活动商品更新 | POST `/temu/proxy` → `type=bg.promotion.activity.goods.update` | `references/apis/bg-promotion-activity-goods-update.md` | `scripts/eu_promotion_activity_goods_update.py` | 活动商品更新。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_eu_file_download.py` | 获取 Temu 加签资源。 |

网关以请求体中的 `type` 选择上游操作，没有单独的促销 URL path；上游统一路由为 `/openapi/router`。Token 校验复用 `/temu/proxy` 的探测请求，不另计业务接口。完整目录与 Partner 文档定位见 [references/partner-eu-catalog.md](references/partner-eu-catalog.md)。

## 前置条件

准备 LinkFox 接口密钥及目标店铺的 Temu 授权。两套令牌用途不同；Temu 令牌需在卖家后台手动复制，支持直接使用或先保存到本地后按店铺读取。
后台授权步骤、本地保存、列出与读取令牌见 [references/access-token.md](references/access-token.md)，授权决策见 [references/authorization-flow.md](references/authorization-flow.md)。调用前核对目标店铺、区域及用途；参数默认值与认证兼容规则见 [references/api.md](references/api.md)。

## 促销执行流程

1. 查询可参加或已参加的活动，确定目标活动。
2. 查询候选商品，核对报名资格、推荐活动价与推荐活动数量。
3. 根据用户明确指定的商品、SKU、活动供货价和数量报名，保存返回的草稿标识。
4. 查询报名或更新的操作结果；仍在处理时说明当前状态，后续查询遵守调用约束，不连续自动轮询或重复提交。
5. 查询已报名商品，核对活动价、活动数量与剩余名额。
6. 需要维护时，按用户要求调整活动供货价、增加活动数量、停用活动商品或增加 SKU，再查询操作结果。详细条件见对应接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，脚本不读取或写入响应缓存。失败或空结果时，不得自动更换活动、翻页或修改参数连续试探；需要继续查询时，先说明当前结果与下一步查询范围。算力规则见“算力消耗预估”。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-promotion-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应体顶层的常见计数（如 `total`、`costToken`，如有）、最大列表字段的长度和前 3 条样本。
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

- **区分活动与日常经营**：活动供货价、活动名额和活动停用属于促销域，不等同于普通供货价、商品库存或商品上下架。
- **清晰展示数据**：先标明店铺和区域，再用表格展示活动名称、状态、起止时间及参与情况；商品表展示报名资格、推荐价或实际活动价、数量、SKU 和失败原因。时间注明时区，金额单位和币种未明确时保留原值，不自行换算。
- **解释异步结果**：提交完成与报名或更新成功是不同阶段；保留草稿标识与原始状态，未知状态值不自行命名为成功。
- **按返回范围说明结果**：区分候选商品与已报名商品、总记录数与本次页内记录；空结果不自动换活动、翻页或重试。
- **授权和 CLI**：通用代理、欧洲站代理、下载、Token 校验和本地授权辅助脚本均可使用；完整选项、默认值、缓存与本地存储行为见 `references/api.md` 的运行约定。
- **维护接入资料**：Partner 后台菜单可能显示为 Marketing/Promotion；菜单名称不代表未接入操作已可用。新增操作必须取得完整 Partner 请求与响应表，按 `references/partner-eu-catalog.md` 的接入约定维护，不能推测字段。

## 使用示例

### 查询活动与候选商品

用户：看看欧洲站这个活动可以报哪些商品。

确认店铺和目标活动，查询候选商品，展示资格、推荐活动价与数量；需要先找活动时先执行活动查询。

### 报名并核对结果

用户：按这些商品、SKU、活动价和数量报名。

核对用户提供的信息与活动资格，提交报名并保存草稿标识，再查询操作结果，说明是否仍在处理及可用失败原因。

### 维护已报名商品

用户：把指定活动商品的活动供货价改为我给出的价格。

确认活动与商品，按对应维护操作提交用户指定修改，随后核对操作结果与已报名商品信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
