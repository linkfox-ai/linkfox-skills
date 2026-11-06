---
name: linkfox-temu-promotion-global
description: 管理 Temu 全球站的促销活动，支持活动查询、候选商品与已报名商品查询、商品报名、报名或更新结果查询、活动商品改价、增量、下架和添加 SKU，并支持促销相关加签文件下载。适用于已授权店铺的活动选品、报名和活动维护；不适用于广告投放、常规商品库存管理、供货价定价、订单或售后处理。
---
# Temu 全球站电商促销

## 适用范围

### 适用

管理已授权 Temu 全球站店铺的促销活动及活动商品。用户希望了解可参加活动、挑选可报名商品、提交报名或维护活动商品时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 有哪些秒杀、大促或清仓活动可以参加 | 查询活动与报名情况。 |
| 这个活动有哪些可报名商品、推荐活动价是多少 | 查看候选商品与推荐数量和价格。 |
| 把指定商品报到这个活动 | 按用户给定的商品、SKU、数量和价格报名。 |
| 刚才的报名或更新成功了吗 | 查询异步操作结果。 |
| 查看活动中的商品，增加活动数量或修改活动价 | 查询已报名商品并按指定动作维护。 |
| 下载促销相关的加签文件 | 请求加签资源。 |

### 边界

广告投放使用对应 Temu Ads 技能；常规商品管理、供货价定价、发品、订单和售后分别转交 `linkfox-temu-manage-product-global`、`linkfox-temu-price-global`、`linkfox-temu-add-product-us`、`linkfox-temu-order-global`、`linkfox-temu-returns-refunds-global`。当前已定义能力以接口清单为准，不将优惠券或活动创建理解为已实现操作。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 促销活动查询（`bg.promotion.activity.query`） | POST `/temu/proxy` → type：`bg.promotion.activity.query`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-query.md](references/apis/bg-promotion-activity-query.md) | `scripts/global_promotion_activity_query.py` | 促销活动查询。 |
| 活动候选商品查询（`bg.promotion.activity.candidate.goods.query`） | POST `/temu/proxy` → type：`bg.promotion.activity.candidate.goods.query`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-candidate-goods-query.md](references/apis/bg-promotion-activity-candidate-goods-query.md) | `scripts/global_promotion_activity_candidate_goods_query.py` | 活动候选商品查询。 |
| 活动已报名商品查询（`bg.promotion.activity.goods.query`） | POST `/temu/proxy` → type：`bg.promotion.activity.goods.query`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-goods-query.md](references/apis/bg-promotion-activity-goods-query.md) | `scripts/global_promotion_activity_goods_query.py` | 活动已报名商品查询。 |
| 活动商品报名（`bg.promotion.activity.goods.enroll`） | POST `/temu/proxy` → type：`bg.promotion.activity.goods.enroll`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-goods-enroll.md](references/apis/bg-promotion-activity-goods-enroll.md) | `scripts/global_promotion_activity_goods_enroll.py` | 活动商品报名。 |
| 活动商品操作结果查询（`bg.promotion.activity.goods.operation.query`） | POST `/temu/proxy` → type：`bg.promotion.activity.goods.operation.query`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-goods-operation-query.md](references/apis/bg-promotion-activity-goods-operation-query.md) | `scripts/global_promotion_activity_goods_operation_query.py` | 活动商品操作结果查询。 |
| 活动商品更新（`bg.promotion.activity.goods.update`） | POST `/temu/proxy` → type：`bg.promotion.activity.goods.update`（上游 path：`/openapi/router`） | [references/apis/bg-promotion-activity-goods-update.md](references/apis/bg-promotion-activity-goods-update.md) | `scripts/global_promotion_activity_goods_update.py` | 活动商品更新。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md#接口加签文件下载) | `scripts/temu_global_file_download.py` / `scripts/temu_file_download.py` | 请求 Temu 加签资源。 |

通用入口 `scripts/temu_global_proxy.py` 与多站点兼容入口 `scripts/temu_proxy.py` 复用上述转发端点，不增加独立促销操作。认证探测 `scripts/check_linkfox_token.py` 同样复用代理；本地令牌和授权辅助脚本见 [授权说明](references/access-token.md)。

## 前置条件

先确定目标店铺、站点与用户需要的促销动作。LinkFox 用户密钥与 Temu 店铺令牌是两套凭据；Temu 没有 LinkFox 侧自动 OAuth，需在卖家后台手动授权并复制令牌，或读取已保存的店铺令牌。按需阅读 [授权说明](references/access-token.md) 和 [授权流程](references/authorization-flow.md)。具体鉴权兼容、默认参数与 CLI 约定见 [接口参考](references/api.md#运行约定)。

## 促销执行流程

1. 查询可参加或已参加的活动，确定目标活动。
2. 查询候选商品，结合是否允许报名、推荐数量与推荐价选择商品。
3. 按用户指定范围提交商品报名，保存报名草稿标识。
4. 用草稿标识查询报名或更新结果；需要轮询时遵守调用约束，尚在处理中不得重复报名或更新。
5. 查询已报名商品，核对活动价、活动数量与剩余数量。
6. 按用户指定动作修改活动价、增加活动数量、下架活动商品或添加 SKU，再查询操作结果。

接口参数、枚举与使用限制见各接口文档；用户只要求查询时，完成所需查询即可。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：普通查询在同一会话、同一参数组合下默认只调用一次；业务脚本不读取或保存响应缓存，优先复用已落盘结果。异步操作结果确需轮询时，可在已说明的查询范围内重复查询同一 `draftIdList`，不得重复提交报名或更新。失败或空结果时，不得自动更换筛选条件、翻页或连续试探；需要继续查询时，先向用户说明查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-promotion-global-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应体中存在的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **分清活动与常规商品信息**：活动数量独立于商品库存，活动供货价与常规定价分开解读。
- **区分提交与最终结果**：报名或更新返回草稿标识不代表已最终完成；展示实际返回的操作状态和失败原因，未定义的状态枚举不自行补充。
- **清晰展示数据**：注明店铺和站点，先展示活动名称、类型、状态和时间，再展示商品、SKU、推荐或实际活动价、数量和报名资格。时间按接口秒级时间戳解释；币种和价格单位未给出时如实说明，不自行换算。
- **保留响应层次**：网关结果和 Temu 业务结果分别解释，具体成功判断、空结果和错误处理见 [接口参考](references/api.md)。
- **按需读取与展示**：保留原始响应文件；先看摘要，必要时按字段读取。列表展示本次返回范围，不因空结果自动翻页或改筛选条件。
- **保留扩展约定**：后续确有新增 Partner 业务文档时，再补齐独立接口文档与业务入口，并同步 [Partner 目录](references/partner-global-catalog.md)、[接口索引](references/apis/README.md) 和接口清单；不将待补的菜单编号当作已知值。

## 使用示例

### 查询可报名活动和候选商品

用户：看看全球站有哪些正在进行的秒杀活动，再看选定活动能报哪些商品。

先查询目标活动，再按用户选择查看候选商品，展示报名资格和推荐价量。

### 报名并查询处理结果

用户：按这些 SKU、活动价和数量报名到指定活动。

核对店铺和用户提供的报名内容，提交后保存草稿标识，查询并说明实际处理状态。

### 维护已报名商品

用户：增加这个商品的活动数量，再查更新结果。

先读取当前活动商品信息，按接口限制准备增加数量的请求，再提交并查询草稿处理结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
