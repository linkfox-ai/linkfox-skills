---
name: linkfox-temu-promotion-us
description: 管理 Temu 美国站促销活动，支持活动与候选商品查询、报名商品、查询异步操作结果、查看已报名商品、调整活动价和数量、停用活动商品、增加活动 SKU 及加签资源下载。适用于美国站已授权店铺的秒杀、大促和清仓活动运营；不适用于广告投放、普通商品维护、日常定价、订单或售后管理，未定义的独立优惠券操作也不在范围内。
---

# Temu 美国站电商促销

## 适用范围

### 适用

管理已授权 Temu 美国站店铺的促销活动，从查询活动和候选商品，到报名、核验异步结果及维护活动商品。Partner 后台可能将该菜单显示为 Promotion 或 Marketing。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 查一下美国站有哪些可参加的大促或秒杀 | 查询活动及报名状态。 |
| 哪些商品能报名，推荐活动价是多少 | 查询候选商品、推荐价与推荐数量。 |
| 把这些商品报入指定活动 | 核对目标活动、商品、SKU、价格与数量后报名。 |
| 上次提交的报名或更新处理完了吗 | 用草稿线索查询异步操作结果。 |
| 看已报名商品的活动价与剩余名额 | 查询已报名商品。 |
| 调整活动价、增加活动名额、停用商品或加 SKU | 按用户指定的变更维护活动商品。 |
| 下载 Temu 的加签资源 | 使用已授权店铺下载指定资源。 |

### 边界

广告投放转交 linkfox-temu-ads-us，普通商品维护转交 linkfox-temu-manage-product-us，发品转交 linkfox-temu-add-product-us，日常价格转交 linkfox-temu-price-us，订单与售后分别转交 linkfox-temu-order-us、linkfox-temu-returns-refunds-us。欧洲站、全球站促销使用对应站点技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|------|------|----------|----------|------|
| 活动候选商品查询（`bg.promotion.activity.candidate.goods.query`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.candidate.goods.query` | `references/apis/bg-promotion-activity-candidate-goods-query.md` | `scripts/us_promotion_activity_candidate_goods_query.py` | 活动候选商品查询。 |
| 活动商品报名（`bg.promotion.activity.goods.enroll`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.goods.enroll` | `references/apis/bg-promotion-activity-goods-enroll.md` | `scripts/us_promotion_activity_goods_enroll.py` | 活动商品报名。 |
| 活动商品操作结果查询（`bg.promotion.activity.goods.operation.query`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.goods.operation.query` | `references/apis/bg-promotion-activity-goods-operation-query.md` | `scripts/us_promotion_activity_goods_operation_query.py` | 活动商品操作结果查询。 |
| 活动已报名商品查询（`bg.promotion.activity.goods.query`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.goods.query` | `references/apis/bg-promotion-activity-goods-query.md` | `scripts/us_promotion_activity_goods_query.py` | 活动已报名商品查询。 |
| 活动商品更新（`bg.promotion.activity.goods.update`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.goods.update` | `references/apis/bg-promotion-activity-goods-update.md` | `scripts/us_promotion_activity_goods_update.py` | 活动商品更新。 |
| 促销活动查询（`bg.promotion.activity.query`） | POST `/temu/proxy` → US path：`/openapi/router`；Body type：`bg.promotion.activity.query` | `references/apis/bg-promotion-activity-query.md` | `scripts/us_promotion_activity_query.py` | 促销活动查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_us_file_download.py`、`scripts/temu_file_download.py` | 下载指定加签资源。 |

通用入口 `scripts/temu_us_proxy.py` 与 `scripts/temu_proxy.py` 复用代理端点；前者使用美国站默认值，后者支持多站点参数。Partner 菜单和接口文档索引见 [references/partner-us-catalog.md](references/partner-us-catalog.md)。

## 前置条件

准备 LinkFox 密钥与目标 Temu 店铺的授权令牌，明确店铺、站点和本次活动运营范围。Temu 令牌由用户在卖家后台手动授权并复制；本技能保留本地保存、列出、读取及授权步骤脚本，见 [references/access-token.md](references/access-token.md) 与 [references/authorization-flow.md](references/authorization-flow.md)。参数默认值、认证兼容及 CLI 约定见 [references/api.md](references/api.md)。

## 促销操作流程

1. 明确目标店铺与用户范围，查询可参加或已参加的活动。
2. 取得目标活动后，查询候选商品、是否可报名以及推荐活动价和数量。
3. 按用户指定范围准备报名；提交后保存草稿线索。
4. 查询草稿对应的异步报名或更新结果；按任务需要继续核验，避免无限轮询。
5. 查询已报名商品，展示实际活动价、活动数量及剩余名额。
6. 需要改价、改量、停用或加 SKU 时，按用户指定的变更提交更新，再查询异步结果。

只执行任务需要的步骤；单项查询不要求先跑完整流程。上述操作的完整入参、条件限制和结果解释见各接口文档。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，优先复用已保存的响应；业务封装不读取或写入 API 响应缓存。失败或空结果时，不得自动扩大查询范围或连续试探；后续查询与异步轮询按用户任务需要进行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-promotion-us-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 序列化响应的 UTF-8 字节数不超过 8000：保存后，将完整 JSON 打印到标准输出。
- 序列化响应的 UTF-8 字节数超过 8000：保存后，标准输出仅展示摘要，包括顶层字段、顶层实际返回的常见指标（如 `total`、`costToken`），以及最大非空列表字段的长度和前 3 条样本。
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

- **响应缓存**：本技能业务封装不缓存 API 响应；调用器选项与输出规则见 references/api.md。
- **区分两套认证**：LinkFox 密钥用于网关，Temu 店铺令牌用于店铺业务；不得相互替代。授权应用、子账号、过期、多站点与 IP 白名单要求见授权参考。
- **清晰展示结果**：先注明店铺和活动，再用表格列出候选、已报名商品、SKU 活动价和数量，标明本次返回范围及后续页是否可查。
- **区分提交与完成**：保留草稿线索、操作状态和失败原因；异步请求已提交不能视为报名或更新完成。
- **按实际数据说明金额与时间**：保留响应原始金额单位、币种和时间含义；金额缩放、时区及状态枚举须有明确信息才能解释，不得自行推定，时间展示转换时标注时区。
- **核对变更影响**：报名、更新活动价或数量、停用商品及新增 SKU 都会改变店铺活动数据；按用户已明确的目标与范围执行，避免扩大变更或因结果不确定而重复提交。
- **解释空结果与错误**：保留已获得的数据，依据接口参考说明原因；额外查询与轮询遵守成本约束。

## 使用示例

### 查询候选商品

用户：看看这场美国站大促可以报哪些商品，推荐什么活动价。

确认目标店铺与活动，查询候选商品，用表格展示是否可报名、推荐价格及数量。

### 报名并核验结果

用户：按这些价格和数量报名指定活动。

核对活动、商品和 SKU，按指定范围提交报名，保存草稿线索，查询异步结果并说明处理状态。

### 更新活动商品

用户：增加这个商品的活动名额，并确认更新结果。

读取已有活动商品，按接口参考核对可更新条件后提交，查询草稿处理状态及已报名商品数据。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
