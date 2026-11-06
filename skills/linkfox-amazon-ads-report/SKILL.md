---
name: linkfox-amazon-ads-report
description: 获取亚马逊 Amazon Ads 的 Sponsored Products（SP）、Sponsored Brands（SB）和 Sponsored Display（SD）广告报告，完成创建、等待生成、下载和解压，支持继续等待已有报告。适用于广告活动、广告组、搜索词、定向、投放商品、购买商品、流量异常和 Prompt 扩展效果查询。不适用于 ST、DSP、Brand Analytics、Retail Analytics、Attribution 报告、报告删除修改、定时任务或广告实体管理。
---

# Amazon Ads 报告获取

## 适用范围

### 适用

获取已授权广告账号的 SP / SB / SD 报告，或恢复尚在生成的报告。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看上周的广告花费 | 广告活动报告。 |
| 哪个投放商品卖得好 | 投放商品或购买商品报告，按广告类型选择。 |
| 买家搜什么词找到广告 | 搜索词报告。 |
| 看关键词、定向或广告组表现 | 定向或广告组报告。 |
| 检查异常流量或 Prompt 广告效果 | 流量异常或 Prompt 扩展报告。 |
| 上次报告还没好，继续等 | 复用已有任务，继续等待并下载。 |

### 边界

授权与账号选择依赖 `linkfox-amazon-ads-auth`；广告实体元数据与维护使用 `linkfox-amazon-ads-manager`。ST / DSP、Brand Analytics / Retail Analytics / Attribution、报告删除修改和定时任务不在本技能范围。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建广告报告 | POST `/amazonAds/developerProxy` -> 上游 POST，path：`reporting/reports` | [references/api.md](references/api.md#接口创建广告报告)、[报告类型目录](references/report-types/index.md)及其中逐类型文档 | `scripts/get_report.py` | 创建后自动等待、下载和解压。 |
| 查询广告报告 | POST `/amazonAds/developerProxy` -> 上游 GET，path：`reporting/reports/{reportId}` | [references/api.md](references/api.md#接口查询广告报告)、[运行规则](references/report-runtime.md) | `scripts/get_report.py` | 查询状态；支持已有任务恢复。 |

## 前置条件

**先完成授权并确定账号与站点**：依赖 `linkfox-amazon-ads-auth`。运行 `python scripts/check_auth_dependency.py` 做本地依赖检查；缺失时先安装，不在本技能中另行实现授权或取 token。依赖检测约定见 [接口定义](references/api.md)。账号解析按下方执行流程进行。

## 报告获取流程

1. 调用认证技能的 `authorized_stores.py` 获取已授权账号与站点，按用户站点映射的 `countryCode` 匹配。仅一个候选时静默选用，不向用户播报内部编号；多个候选时用 `accountName` 澄清，例如“美国站授权了 A 和 B，这次用哪个？”；无候选时引导授权。严禁让用户直接提供内部账号编号，严禁在歧义下取第一项或默认账号。
2. 按用户意图确定报告类型；用户指定类型时只取该类型。先读 [报告类型目录](references/report-types/index.md)，再读对应类型文档的 frontmatter、配置与基础指标表。
3. 询问用户希望按日还是汇总、是否增加归因/视频/新客指标、是否筛选。用户说“默认/随便”时跳过询问。按用户要求或 [默认构参规则](references/report-runtime.md#默认构参规则) 准备参数，显式传入脚本所需业务字段。
4. 调用 `scripts/get_report.py`，由脚本完成创建、等待、下载与解压。已有任务直接恢复等待；同参数创建命中上游去重时复用原任务，不重复创建。
5. 完成后展示本地报告路径与临时访问链接。等待窗口耗尽时说明“报告仍在 Amazon 侧生成”，询问是否继续等，并用返回的续跑参数继续同一任务；失败时按接口定义解释原因和保护措施。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话避免重复创建相同参数的报告；已有任务使用 `reportId` 继续轮询。报告请求不使用响应缓存，轮询获取最新状态。失败或空结果时，不得自动更换报告类型、列或日期范围连续试探；需要调整时，先说明原因和请求范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-report-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、响应头的`X-Cost-Credit`）、最大列表字段的长度和前 3 条样本。
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

- **报告规格与执行器分工**：支持范围以报告类型目录现有文档为准。字段、分组、筛选及日期规格由 Agent 查表，脚本负责异步执行，不代替业务选择。SP 广告组或广告位分析使用活动报告对应分组；SD 也在现有覆盖范围内。
- **展示下载结果**：完整展示 `downloadPath` 和实际返回的 `extractedFileHttpUrl`，提醒链接仅能在运行脚本的机器访问且有时效。未返回链接时只展示本地路径，不编造链接。解压文件链接与 Amazon 源压缩包链接用途不同。
- **区分未完成与失败**：等待耗尽不是报告失败。保留原任务，向用户提供继续等待约 30 分钟、约 1 小时或稍后恢复的选择；续跑方式见 [运行规则](references/report-runtime.md)。成功空数据或全零可能表示账号当期没有投放，不自动重试或判为错误。
- **处理错误与保护**：如实呈现非成功响应和生成失败原因，不盲目重试或换报告类型。参数限制、日期分段、错误码、冷却阈值和恢复边界见 [接口定义](references/api.md)及 [账号保护规则](references/report-runtime.md#账号保护与重试)。
- **输出与读取**：完整网关响应和最终结果按会话保存；下载文件也存放于当前工作目录的会话数据目录。优先按摘要提取数据，不将大报告整份载入上下文。

## 使用示例

### 查看一周 SP 广告活动花费

用户：帮我看美国站上周广告花费，其他按默认。

先确认已授权账号，读取 SP 活动报告规格，按默认规则选择日期维度、活动标识和基础指标，拉取并展示下载结果。

### 查看搜索词与转化

用户：看上个月的搜索词、销售和 ACOS，只看关键词匹配。

确认广告类型与账号，读取对应搜索词报告，选用该报告支持的归因列与筛选条件；按日期上限安排请求并本地合并，不补造缺失字段。

### 继续等待已有报告

用户：上次还没生成好，现在继续等半小时。

使用上次保存的任务和续跑参数继续轮询，不重新创建。若仍未完成，展示当前状态并保留恢复信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
