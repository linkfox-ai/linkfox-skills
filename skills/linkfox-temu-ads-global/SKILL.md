---
name: linkfox-temu-ads-global
description: 管理 Temu 全球站店铺的搜索推荐广告，支持可投商品检查、ROAS 预测、创建和修改广告、广告详情、店铺广告报表与操作日志，并辅助获取加签文件。适用于全球站广告投放、预算与目标回报维护、效果查看及变更排查；不适用于商品管理、促销活动、价格、订单、退货退款或美国站与欧洲站专用广告操作。
---
# Temu 全球站电商广告

## 适用范围

### 适用

管理已授权 Temu 全球站店铺的搜索推荐广告，查看投放资格、预测、效果及变更记录。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 这些商品能不能投广告 | 检查可创建广告资格及不可投原因。 |
| 创建前看一下 ROAS 预测 | 查看商品预测结果，为用户设定目标提供数据。 |
| 给这些商品创建广告 | 核对目标商品与投放方案后创建。 |
| 暂停、开启或删除广告，调整预算或目标 ROAS | 按用户指定范围修改并逐项展示结果。 |
| 查看投放状态、店铺效果或是谁改过广告 | 查询详情、店铺报表或操作日志。 |

### 边界

商品管理、促销、价格、订单、退货退款分别使用 `linkfox-temu-manage-product-global`、`linkfox-temu-promotion-global`、`linkfox-temu-price-global`、`linkfox-temu-order-global`、`linkfox-temu-returns-refunds-global`；发品使用 `linkfox-temu-add-product-us`。美国站或欧洲站专用广告操作使用对应站点技能。本技能覆盖当前七类广告能力。

## 接口清单

| 接口 | 端点与转发操作 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建广告 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.create` | `references/apis/temu-searchrec-ad-create.md` | `scripts/global_ads_searchrec_ad_create.py` | 创建广告。 |
| 广告详情查询 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.detail.query` | `references/apis/temu-searchrec-ad-detail-query.md` | `scripts/global_ads_searchrec_ad_detail_query.py` | 广告详情查询。 |
| 广告可创建商品查询 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.goods.create.query` | `references/apis/temu-searchrec-ad-goods-create-query.md` | `scripts/global_ads_searchrec_ad_goods_create_query.py` | 广告可创建商品查询。 |
| 广告操作日志查询 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.log.query` | `references/apis/temu-searchrec-ad-log-query.md` | `scripts/global_ads_searchrec_ad_log_query.py` | 广告操作日志查询。 |
| 修改广告 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.modify` | `references/apis/temu-searchrec-ad-modify.md` | `scripts/global_ads_searchrec_ad_modify.py` | 修改广告。 |
| 店铺广告报表查询 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.reports.mall.query` | `references/apis/temu-searchrec-ad-reports-mall-query.md` | `scripts/global_ads_searchrec_ad_reports_mall_query.py` | 店铺广告报表查询。 |
| 广告 ROAS 预测 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=temu.searchrec.ad.roas.pred` | `references/apis/temu-searchrec-ad-roas-pred.md` | `scripts/global_ads_searchrec_ad_roas_pred.py` | 广告 ROAS 预测。 |
| 通用转发 | POST `/temu/proxy` → path：`/temu/proxy`，Body `type=<用户指定的广告操作>` | `references/api.md` | `scripts/temu_global_proxy.py`、`scripts/temu_proxy.py` | 支持任意 type 转发。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_global_file_download.py`、`scripts/temu_file_download.py` | 获取加签文件。 |

## 前置条件

**先确定店铺并完成授权**：准备 LinkFox 用户密钥与 Temu 店铺令牌。Temu 令牌由卖家后台手动复制，本技能提供授权引导及本地保存、读取、列表脚本；见 [授权说明](references/access-token.md) 与 [授权流程](references/authorization-flow.md)。核对用户指定的店铺、区域和待操作商品；网关认证、默认值及 CLI 细节见 [接口说明](references/api.md)。

## 广告执行流程

1. 确认目标店铺与任务；需要授权时先查看后台引导，复制令牌后可保存到本地。
2. 创建广告时按需查询商品投放资格或 ROAS 预测，依据用户提供的投放方案创建广告；已有足够信息时可直接创建。
3. 创建后按需查询广告详情，检查现有投放也使用详情查询；用户要求删除、暂停、开启或调整预算、ROAS 时执行对应修改。
4. 查看店铺效果使用广告报表；排查商品广告变更使用操作日志。按需选择这些步骤，不因示例流程自动执行全部操作。
5. 展示已取得的数据和逐商品结果，保留完整响应；失败或空结果不自动试探性追加调用。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，业务脚本不读写响应缓存，优先复用已保存的响应。失败或空结果时，不得自动改参数、翻页或连续试探；需要继续调用时，先说明原因和范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-ads-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应中存在的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分广告与促销**：本技能处理 Partner Global 的 Ads / 搜索推荐广告；完整菜单及资料来源见 [Partner 目录](references/partner-global-catalog.md)。
- **按范围变更**：创建、删除、暂停、开启及调整预算或目标 ROAS 会改变店铺投放，按用户已明确的目标执行；不能把预测值当作收益承诺。
- **清晰展示结果**：注明店铺和站点，用表格展示商品、预算、ROAS、投放状态、不可投原因和成功或失败结果；效果展示注明统计区间及数据口径，数值按接口原义解释，不猜测未定义的单位或枚举。
- **区分提交与业务结果**：结合网关及 Temu 业务结果解释成功、部分失败和错误原因，详见各接口文档。
- **响应读取**：先看摘要，需要具体指标时从完整 JSON 按需提取；Token 不放进面向用户的报表。
- **缓存与令牌存储**：业务脚本不读写响应缓存，具体调用方式见 [脚本运行约定](references/api.md#脚本运行约定)。本地 Token 存储用于授权复用，与响应缓存不同。

## 使用示例

### 创建广告

用户：检查这些商品能否投放，参考预测后按我提供的预算创建广告。

确认店铺及商品，检查可投原因与预测结果，按用户明确的方案创建，展示成功、已有广告和失败商品。

### 修改广告与排查效果

用户：暂停这个商品的广告，再查看最近的效果和变更记录。

核对目标投放并暂停，查询用户要求区间内的店铺报表及该商品的日志，解释修改结果和指标口径。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
