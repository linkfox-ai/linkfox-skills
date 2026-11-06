---
name: linkfox-temu-ads-us
description: 管理 Temu 美国站店铺广告，支持可投商品核验、ROAS 预测、广告创建、详情查询、暂停与开启、预算与 ROAS 调整、删除、店铺广告报表、操作日志和加签文件下载。适用于已授权店铺的广告投放维护和效果分析；不适用于商品管理、促销活动、订单处理或尚未接入的广告组与创意管理。
---
# Temu 美国站广告管理

## 适用范围

### 适用

用户希望管理自己 Temu 美国站店铺的广告、检查商品可投资格、查看投放效果或追查变更历史时使用，无需明确提及 Partner 或接口名称。

**场景速查**

| 用户表达 | 操作场景 |
|----------|----------|
| 这些商品能不能投广告，ROAS 怎么设 | 核验可投资格，按需查询 ROAS 预测。 |
| 按我给的预算和目标创建广告 | 准备商品广告并展示逐商品创建结果。 |
| 看广告状态，暂停、开启或调整预算 | 查询广告详情，按用户授权范围修改。 |
| 删除指定商品广告 | 核对店铺与商品，提交指定删除操作。 |
| 看美国站店铺广告效果或操作历史 | 查看报表、汇总指标和操作日志。 |
| 获取广告相关的加签文件 | 转发加签资源下载请求。 |

### 边界

商品管理、促销、发品、价格、订单和退货分别使用 `linkfox-temu-manage-product-us`、`linkfox-temu-promotion-us`、`linkfox-temu-add-product-us`、`linkfox-temu-price-us`、`linkfox-temu-order-us`、`linkfox-temu-returns-refunds-us`。欧洲站和全球站广告使用对应站点技能。本技能只覆盖清单中的已接入能力，不承诺尚未定义的广告组或创意管理。

## 接口清单

| 接口 | 端点与转发操作 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建广告 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.create` | `references/apis/temu-searchrec-ad-create.md` | `scripts/us_ads_searchrec_ad_create.py` | 美国站广告操作。 |
| 广告详情查询 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.detail.query` | `references/apis/temu-searchrec-ad-detail-query.md` | `scripts/us_ads_searchrec_ad_detail_query.py` | 美国站广告操作。 |
| 广告可创建商品查询 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.goods.create.query` | `references/apis/temu-searchrec-ad-goods-create-query.md` | `scripts/us_ads_searchrec_ad_goods_create_query.py` | 美国站广告操作。 |
| 广告操作日志查询 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.log.query` | `references/apis/temu-searchrec-ad-log-query.md` | `scripts/us_ads_searchrec_ad_log_query.py` | 美国站广告操作。 |
| 修改广告 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.modify` | `references/apis/temu-searchrec-ad-modify.md` | `scripts/us_ads_searchrec_ad_modify.py` | 美国站广告操作。 |
| 店铺广告报表查询 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.reports.mall.query` | `references/apis/temu-searchrec-ad-reports-mall-query.md` | `scripts/us_ads_searchrec_ad_reports_mall_query.py` | 美国站广告操作。 |
| 广告 ROAS 预测 | POST `/temu/proxy`；转发操作（Body `type`）：`temu.searchrec.ad.roas.pred` | `references/apis/temu-searchrec-ad-roas-pred.md` | `scripts/us_ads_searchrec_ad_roas_pred.py` | 美国站广告操作。 |
| 加签文件下载 | POST `/temu/fileDownload`（无上游 path 字段） | `references/api.md#接口加签文件下载` | `scripts/temu_us_file_download.py`；`scripts/temu_file_download.py` | 转发加签资源下载请求。 |

通用入口 `scripts/temu_us_proxy.py` 与 `scripts/temu_proxy.py` 复用 `/temu/proxy`；7 项广告操作用 Body type 区分，无独立的上游 path 参数。Partner 菜单编号、文档链接及索引见 `references/partner-us-catalog.md`、`references/apis/README.md`。

## 前置条件

确定美国站店铺、待操作商品及任务范围。LinkFox 用户密钥与 Temu 店铺 accessToken 是两套认证；Temu 令牌须在卖家后台手动授权并复制，无自动 OAuth。需要帮助时读 `references/access-token.md` 与 `references/authorization-flow.md`，可使用本地授权指引及保存、列出、读取令牌脚本。

## 广告执行流程

1. 核对目标店铺、商品、授权用途和用户要求；按需完成后台授权及本地令牌选择。
2. 创建任务可先查询商品可创建广告的资格，并按需查询 ROAS 预测。
3. 按用户提供的预算和目标创建广告；区分已创建、成功及失败商品。
4. 按需查看广告详情与投放状态；按用户任务暂停、开启、调整预算或 ROAS，或删除广告。
5. 按指定时间范围获取店铺报表，展示汇总和明细；排查变更时查询商品操作日志。

按任务选择必要步骤，仅读取效果时无需创建或修改广告。各操作所需字段、时间与类型约定见对应接口定义。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：算力规则见“算力消耗预估”。同一会话、同一参数组合默认只调用一次；本技能不提供响应缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续检索时，先向用户说明查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-ads-us-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **认证分工**：LinkFox 用于网关身份，Temu 用于店铺授权；失败时按对应层解释，保留已有结果。
- **调用与授权**：脚本的 CLI、认证兼容、输出及缓存约定见 `references/api.md#运行约定`。
- **明确操作影响**：创建、修改和删除会改变广告投放，按用户已明确的店铺、商品及操作范围执行；ROAS 预测仅为预测，不等于效果保证。
- **展示投放结果**：注明店铺、站点与查询区间，用表格展示商品、预算、ROAS、广告状态、汇总及明细；分别报告批量成功与失败原因，不自行推断单位、枚举或缺失数据。
- **区分指标口径**：区分总量、广告归因、净总量与净广告归因；指标可能包在 val 中，按真实响应解释。
- **解释多层响应**：先核对 LinkFox 外层及网关状态，再解释 Temu 业务结果；详细判断见 `references/api.md` 与各操作文档。

## 使用示例

### 创建商品广告

用户：检查这些商品是否可以投广告，再按我给的预算和 ROAS 创建。

核对店铺和商品，查询资格与需要的预测，准备创建请求，分别展示成功、已创建及失败商品。

### 调整广告与追查变更

用户：暂停指定商品的广告，并看看最近是谁改过预算。

核对商品后执行指定暂停，查询用户时间范围内的操作日志，展示修改结果及真实返回的变更信息。

### 查看广告效果

用户：看昨天美国站店铺的广告汇总和商品表现。

确定店铺当地日期范围，读取报表，区分各指标口径；需要单商品状态时再读详情。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
