---
name: linkfox-temu-ads-eu
description: 管理 Temu 欧洲站搜索推荐广告，支持可投商品检查、ROAS 预测、创建广告、查询详情、修改投放状态和预算、查询店铺广告报表与操作日志，并获取加签资源。适用于已授权 EU 店铺的广告投放维护与效果分析；不适用于商品管理、促销活动、定价、订单、售后或其他站点的广告管理。
---
# Temu 欧洲站电商广告

## 适用范围

### 适用

查看或维护已授权 Temu 欧洲站店铺的搜索推荐广告，核对可投商品、评估目标 ROAS，查看投放效果和操作历史。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这些商品能不能投广告 | 可投商品检查：展示不可投原因。 |
| 先看预测，再为这些商品创建广告 | ROAS 预测与广告创建：按用户指定目标准备投放。 |
| 查看广告预算、状态和投放效果 | 广告详情：展示当前设置与可用指标。 |
| 暂停、开启、删除广告或调整预算、ROAS | 广告修改：核对目标商品和变更内容。 |
| 查询店铺广告报表或某商品的变更记录 | 效果分析与日志追溯：标明时间范围。 |
| 获取广告流程中返回的加签文件 | 加签资源获取：保留下载结果。 |

### 边界

商品管理、促销活动、发品、价格、订单和售后分别使用 `linkfox-temu-manage-product-eu`、`linkfox-temu-promotion-eu`、`linkfox-temu-add-product-eu`、`linkfox-temu-price-eu`、`linkfox-temu-order-eu`、`linkfox-temu-returns-refunds-eu`；美国站或全球站广告使用对应站点技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建广告（`temu.searchrec.ad.create`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.create` | `references/apis/temu-searchrec-ad-create.md` | `scripts/eu_ads_searchrec_ad_create.py` | 创建广告。 |
| 广告详情查询（`temu.searchrec.ad.detail.query`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.detail.query` | `references/apis/temu-searchrec-ad-detail-query.md` | `scripts/eu_ads_searchrec_ad_detail_query.py` | 广告详情查询。 |
| 广告可创建商品查询（`temu.searchrec.ad.goods.create.query`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.goods.create.query` | `references/apis/temu-searchrec-ad-goods-create-query.md` | `scripts/eu_ads_searchrec_ad_goods_create_query.py` | 广告可创建商品查询。 |
| 广告操作日志查询（`temu.searchrec.ad.log.query`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.log.query` | `references/apis/temu-searchrec-ad-log-query.md` | `scripts/eu_ads_searchrec_ad_log_query.py` | 广告操作日志查询。 |
| 修改广告（`temu.searchrec.ad.modify`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.modify` | `references/apis/temu-searchrec-ad-modify.md` | `scripts/eu_ads_searchrec_ad_modify.py` | 修改广告。 |
| 店铺广告报表查询（`temu.searchrec.ad.reports.mall.query`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.reports.mall.query` | `references/apis/temu-searchrec-ad-reports-mall-query.md` | `scripts/eu_ads_searchrec_ad_reports_mall_query.py` | 店铺广告报表查询。 |
| 广告 ROAS 预测（`temu.searchrec.ad.roas.pred`） | POST `/temu/proxy` → path：`/openapi/router`；Body `type=temu.searchrec.ad.roas.pred` | `references/apis/temu-searchrec-ad-roas-pred.md` | `scripts/eu_ads_searchrec_ad_roas_pred.py` | 广告 ROAS 预测。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_eu_file_download.py` | 获取 Temu 加签资源；通用入口为 `scripts/temu_file_download.py`。 |

## 前置条件

**先确定店铺和授权用途**：准备 LinkFox 用户密钥及 Temu 店铺授权。Temu 没有 LinkFox 侧自动 OAuth，需在卖家后台手动复制店铺令牌；可直接使用或保存到本地店铺存储。授权步骤与本地辅助脚本见 [references/access-token.md](references/access-token.md)，流程与店铺类型对照见 [references/authorization-flow.md](references/authorization-flow.md)。

确认目标 EU 店铺、商品和用户要求的操作范围；参数、默认值、兼容入口与运行约定见 [references/api.md](references/api.md)，各广告操作的完整字段见上方接口文档。

## 广告执行流程

1. 先检查目标商品是否可创建广告，展示不可投原因。
2. 按需查询 ROAS 预测，结合用户指定的投放目标准备创建内容。
3. 在用户已明确的范围内创建广告，逐商品核对创建结果。
4. 查询广告详情，查看状态、预算、ROAS 和效果摘要。
5. 根据用户要求暂停、开启、删除或修改预算与 ROAS。
6. 按用户指定时间范围查询店铺广告汇总和明细；需要追溯变更时查询商品操作日志。

单项查询只执行所需步骤；这些步骤不要求每次全部调用。加签资源按需获取。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务封装始终禁用响应缓存。失败或空结果时，先核对参数、店铺授权和返回的错误，不自动连续试探；写入结果不明时先查详情，避免重复创建或修改广告。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-ads-eu-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分两套令牌**：LinkFox 用户密钥用于网关认证，Temu 店铺令牌用于业务授权。主账号授权、多站点独立授权、有效期和 IP 白名单要求见授权说明。
- **清晰展示结果**：先注明店铺和站点，再用表格展示商品、广告状态、预算、目标 ROAS、效果指标及失败原因；缺失信息按实际返回说明，不补造值。
- **区分预测与实绩**：ROAS 预测用于创建前参考，广告详情与报表用于回看当前设置和效果；不把预测当成收益承诺。
- **保留指标口径**：汇总、广告归因及净额指标分别展示，标明报表时间范围。预算、金额和 ROAS 的单位或倍率以实际响应及 Partner 文档为准，不擅自换算。
- **核对写入目标**：创建、删除、开关投放和修改预算或 ROAS 均影响店铺广告；按用户已明确的商品与变更范围执行，逐项解释成功或失败，不以外层请求完成代替商品变更成功。
- **本地辅助能力**：支持授权引导、店铺令牌保存与脱敏列表、通用代理及多站点兼容入口；具体 CLI 和参数约定集中在接口参考。
- **维护接入目录**：后续明确要求接入新 Ads 操作时，以完整 Partner 请求与响应表为依据，补齐独立接口文档、业务脚本和接口清单，并同步 [Partner 目录](references/partner-eu-catalog.md) 与 [文档索引](references/apis/README.md)。不将尚未接入的广告计划、广告组或创意能力当作现有能力。

## 使用示例

### 创建广告

用户：先看看这些商品能否投广告和预测 ROAS，再按我提供的预算创建。

确认店铺与商品，检查可投资格和预测，按用户指定的预算与目标准备创建，展示逐商品结果。

### 调整广告

用户：把指定商品的广告暂停，或调整为我提供的新预算。

核对目标与变更内容，执行对应修改，说明成功商品与失败原因；结果不确定时先查详情。

### 查看效果和历史

用户：查看这段时间店铺广告效果，并追溯这个商品的广告变更。

按时间范围查询报表与日志，区分汇总、明细和归因口径，展示可用结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
