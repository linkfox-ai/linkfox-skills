---
name: linkfox-amazon-ads-sp-insights-report
description: 获取亚马逊 Sponsored Products（SP）的 Audience 受众细分表现和 Search Term Impression Share/Rank 搜索词展示份额及排名报告，自动完成账号映射、异步等待、多分片 CSV 下载和保存。适用于用户明确要求 SP 受众、搜索词展示份额或份额排名的场景；不适用于普通 SP 搜索词表现报告、常规广告报告、广告实体管理及 SB、SD、DSP 报告。
---
# Amazon Ads SP 洞察报告获取

## 适用范围

### 适用

获取已授权广告账号的两类 Sponsored Products 专项报告。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看 SP 各受众细分的表现 | Audience：按账号、广告活动或广告组查看受众数据。 |
| 看搜索词的展示份额和排名 | Search Term Impression Share/Rank：查看搜索词份额及份额排名。 |
| 上次洞察报告还没生成，继续取 | 续跑已有报告，复用原任务。 |

### 边界

普通 SP 搜索词曝光、点击、花费、销售、转化报告，以及常规 SP/SB/SD 报告，使用 `linkfox-amazon-ads-report`（普通 SP 搜索词对应 `spSearchTerm`）；广告活动、广告组、关键词、投放和预算管理使用 `linkfox-amazon-ads-manager`。授权与令牌刷新使用 `linkfox-amazon-ads-auth`。Sponsored Television、DSP、Brand Analytics、Retail Analytics 不在本技能范围。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询 advertiser accounts | POST `/amazonAds/developerProxy` → path：`adsApi/v1/query/advertiserAccounts`，method：`POST` | [references/api.md](references/api.md#接口查询-advertiser-accounts) | `scripts/reporting_v1_workflow.py`（由两个入口调用） | 按授权 profile 映射唯一广告账号。 |
| 创建洞察报告 | POST `/amazonAds/developerProxy` → path：`adsApi/v1/create/reports`，method：`POST` | [references/api.md](references/api.md#接口创建洞察报告)、[Audience](references/sp-audience-reporting-v1.md)、[Search Impression Share](references/sp-search-impression-share-v1.md) | `scripts/get_sp_audience_report.py` / `scripts/get_sp_search_impression_share.py` | 固定兼容字段，创建指定类型报告。 |
| 查询洞察报告状态 | POST `/amazonAds/developerProxy` → path：`adsApi/v1/retrieve/reports`，method：`POST` | [references/api.md](references/api.md#接口查询洞察报告状态) | `scripts/reporting_v1_workflow.py`（由两个入口调用） | 轮询任务，完成后下载全部分片。 |

## 前置条件

依赖 `linkfox-amazon-ads-auth` 完成授权与账号选择；运行 `python scripts/check_auth_dependency.py` 检查安装情况。入口启动时自动检查，缺失时按 [接口参考](references/api.md) 处理，不另行实现授权或令牌获取。

## 报告获取流程

1. **确定类型**：受众表现使用 `scripts/get_sp_audience_report.py`；展示份额及排名使用 `scripts/get_sp_search_impression_share.py`。一次只运行用户要求的一个入口。
2. **读取参考**：按报告类型读取 [Audience](references/sp-audience-reporting-v1.md) 或 [Search Impression Share](references/sp-search-impression-share-v1.md)，核对字段、限制及展示重点。
3. **解析账号**：先用授权技能的 `authorized_stores.py` 获取账号与站点列表，按用户站点匹配 `countryCode`。一个候选时静默使用；多个候选必须用 `accountName` 让用户确认，禁止默认第一个；没有候选时说明未授权并引导授权。不得要求用户提供或向用户播报数字 profile 标识。
4. **确定日期与粒度**：创建报告前取得用户日期，缺失时先询问，不猜测。默认粒度及全部参数约定见对应报告参考。
5. **说明等待并运行**：告知 Amazon 通常约需 2–10 分钟，随后运行所选入口，由共享工作流完成映射、创建、轮询及下载。不要手工拆成三次业务调用，也不要直接运行共享模块。
6. **解释结果**：报告完成后展示类型、日期、行数、预览及全部分片路径；合法空报告按接口参考解释。
7. **继续未完成报告**：等待窗口结束表示任务仍在生成，先向用户确认是否继续，再使用返回的续跑参数和原入口继续原任务，禁止重复创建。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一报告类型和同一参数组合默认只调用一次，成功结果缓存 24 小时。失败、未完成或空报告不得自动换日期、切换账号或连续试探；继续未完成任务时按续跑参数处理。

### 输出策略

- 始终保存完整响应，目标路径为 `<根>/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-sp-insights-report-<timestamp>.json`。`<根>` 优先取 `ACPX_WORKSPACES` 第一个路径下的 `linkfox/`，其次取 `<cwd>/linkfox/`；两处均不可写则请求前报错，不回退到家目录或系统临时目录。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，未设置时自动生成。完整 CSV 分片保存于同一会话的 `data/`。
- 响应体的 UTF-8 编码不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体的 UTF-8 编码超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、存在的常见计数及状态（如 `total`、`costToken`、`success`）、最大列表字段的长度和前 3 条样本。
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

- **理解报告**：只覆盖 Reporting API v1 的 SP Audience 与搜索词展示份额/排名；不能用常规 v3 数据替代或伪造。Reporting API v1 为 open beta，不承诺账号开放范围、字段及限流长期稳定。
- **区分账号标识**：profile 用于服务端选择授权，advertiser account 为报告目标，通常由脚本自动映射；用户多账号选择规则不得跳过。
- **固定报告组合**：两个入口共享工作流，字段由脚本按参考构造，不让 Agent 自由组合维度或过滤；具体限制见报告参考。
- **呈现报告**：Audience 优先展示受众名称、类型、来源、国家、曝光、点击、花费、购买、销售额、ROAS，并保留币种；搜索词报告突出搜索词、展示份额及份额排名。注明日期与粒度，说明当天数据可能不完整。
- **保护输出**：完整报告从所有 CSV 分片按需读取，优先看摘要和预览；禁止展示完整 Token、内部授权记录或 Amazon 预签名下载链接。
- **尊重结果**：失败时如实说明错误，不盲目换日期、账号或参数重建；空结果、续跑、缓存及网关账号保护措施见 [接口参考](references/api.md)。客观呈现，除非用户要求，不主动延伸商业决策建议。
- **本地输出**：报告入口优先在工作区落盘，并提供成功结果缓存；与通用调用器的衔接说明、目录优先级及 CLI 约定见接口参考。

## 使用示例

### 获取 SP Audience 报告

用户：查看美国站上周各受众细分的表现。

确认唯一广告账号与日期范围，读取 Audience 参考，运行受众报告入口；展示受众指标、币种和所有 CSV 分片路径。

### 获取搜索词展示份额及排名

用户：查看日本站上周搜索词的展示份额和排名。

确认账号与日期，运行搜索词展示份额入口，突出搜索词、份额与排名；不得用普通搜索词表现报告替代。

### 恢复已有任务

用户：继续获取上次还在生成的洞察报告。

确认继续后，按原报告类型使用返回的续跑参数，复用同一任务并绕过缓存。脚本调用示例见 [脚本用法](references/script-usage.md#入口调用示例)。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
