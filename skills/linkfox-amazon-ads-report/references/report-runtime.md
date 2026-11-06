# Amazon Ads 报告运行规则

## 默认构参规则

以下为 Agent 未收到定制要求时的业务选择；脚本本身仍默认 `timeUnit=SUMMARY`，必须由 Agent 显式传入按下表确定的值。

| 条件 | 默认规则 |
|------|---------|
| `timeUnit` | 日期跨度 ≤ 7 天 → `DAILY`；> 7 天 → `SUMMARY` |
| `columns` 身份维度 | `DAILY` 时必含 `date`；`SUMMARY` 时必含 `startDate` + `endDate`；再追加该报告的主键字段（参考 frontmatter 中 groupBy 对应的主键，如 campaignId+campaignName / advertisedAsin+advertisedSku / searchTerm / keyword 等） |
| `columns` 基础指标 | `impressions` / `clicks` / `cost`（以该报告 Base metrics 存在的为准） |
| `columns` 归因指标 | **仅当用户提到"销售/转化/ROI/ACOS"等意图时追加**：优先取该报告支持的 `sales7d` / `purchases7d` / `acosClicks7d` / `roasClicks7d`；不提供这些列时，按规格选择实际销售/转化列，例如 SB / SD 的 `sales` / `purchases`、`sbPurchasedProduct` 的 `sales14d` / `orders14d`、`sdPurchasedProduct` 的 `salesBrandHalo` / `conversionsBrandHalo`。只取该报告存在的列，并说明对应归因口径。 |
| `filters` | 不加（全量返回） |
| `groupBy` | 取 frontmatter `groupBy` 数组的第一个值（即 Configuration 表里 Amazon 官方推荐的主维度） |

所有字段仅从对应报告的基础指标或适用分组附加指标中选择，不能凭归因窗口后缀推导出不存在的列。归因后缀 `_1d` / `_7d` / `_14d` / `_30d` 表示相应归因窗口；实际列名也可能直接以 `1d` / `7d` / `14d` / `30d` 结尾，保持规格中的原值。

## 日期与数据限制

- 日期包含起止当天。最大跨度以逐类型 frontmatter 的 `dateRange.maxSpanDays` 为准：多数 31 天；`sbPurchasedProduct` 为 731 天；GrossAndInvalids 系列为 365 天；Prompt 扩展为 90 天。
- 回溯窗口以 `dateRange.dataRetentionDays` 为准，SP 多为 95 天、SB 多为 60 天、SD 多为 65 天、GrossAndInvalids 为 365 天；如 `spSearchTerm` 为 65 天，以具体文件为准。
- 数据通常延迟约 12 小时，建议截止昨日。`endDate >= 今天` 时脚本只在 stderr 警告，不阻断提交。日期超限应先按报告规格分段，按用户所需日期范围安排请求，再本地合并。
- 搜索词、预览期、分组专有指标与筛选限制详见各报告类型文档，调用前按需阅读。

## 脚本运行与恢复

- CLI：`python scripts/get_report.py '<JSON 参数>' [--inline] [--no-cache]`。参数及默认值见 [api.md](api.md)。不传 `reportId` 时执行创建→轮询→下载→解压；传入非空 `reportId` 时只需 `profileId`、`region`、`reportId`，直接恢复轮询。
- 默认每 30 秒查询一次，最多 15 次，等待窗口约 7.5 分钟；报告常需 2–10 分钟。等待约 5 分钟时输出一次进度提示。脚本不自动延长等待或重新创建。
- 上游 HTTP 425 且内容为 `The Request is a duplicate of : <uuid>` 时，脚本自动解析已有任务并转为轮询；无法解析则报错，不继续试探。
- 状态 `PENDING` / `PROCESSING`（兼容 `IN_QUEUE` / `IN_PROGRESS`）继续等待；`COMPLETED`（兼容 `SUCCESS`）须有下载地址；`FAILED`（兼容 `FAILURE` / `CANCELLED`）输出 `failureReason` 并退出 1。
- 等待耗尽时输出并保存 `status=STILL_PROCESSING`、任务 ID、`lastStatus`、`pollAttempts`、`elapsedSeconds` 和 `resumeHint.params`，退出 2。询问用户继续等还是稍后恢复；同一 `reportId` 配 `maxAttempts=60` 约 30 分钟、`120` 约 1 小时，不重复创建。
- 成功后下载 Amazon 预签名素材（源 URL 通常约 1 小时有效），探测 gzip 魔数解压成 JSON；非 gzip 保留原文件，解压失败警告后保留原下载文件。CSV / XLSX 等可用格式以类型文档为准，不强行解析为 JSON。
- 默认开启本机单文件 HTTP 服务，绑定 `127.0.0.1`，端口由系统分配，持续 300 秒；开启时生存期至少 10 秒。只有 `/` 与 `/download` 可访问，其他路径返回 404，文件消失返回 410。服务结束后关闭，链接随即失效。用户需要立即退出可设 `serveExtractedFileHttp=false`。
- 网关地址依次使用 `LINKFOX_TOOL_GATEWAY`、`AMAZON_ADS_BASE_URL`、正式网关兜底。API key 支持 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`；请求传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。
- 业务调用使用profileId，由服务端选择并管理授权凭证。
- `check_auth_dependency.py` 支持环境变量、仓库相邻目录、Claude/Cursor/LinkFox/OpenClaw/Hermes 安装路径探测及 `--json`。成功返回 0 并输出 `DEPENDENCY_OK:`，缺失返回 42 并输出 `DEPENDENCY_MISSING:`；`skipDepCheck` 只跳过本地安装检查，不绕过账号授权。
- 报告请求不使用响应缓存。业务封装通过公共 `call_api.run` 发起请求且始终加 `--no-cache`；公共调用器可能创建空缓存目录，但不读取或写入响应缓存，不叠加业务缓存。轮询原始响应、成功、失败和未完成结果均按会话落盘。
- 请求前探测当前工作目录可写性；网关响应、最终结果和下载文件固定保存在 `<cwd>/linkfox/<日期>/<session>/data/`，不可写时在请求前报错，不回退到用户目录或系统临时目录。`tempDirectory` 表示位于会话数据内的下载工作目录。

## 账号保护与重试

同一广告账号/profile 连续收到 Amazon Ads API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大广告账号风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查 profileId、region、实体/报告 ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 广告账号/profile 全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该广告账号调用，检查 Ads 授权、应用权限、profile 归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属 profile/区域、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 广告账号/profile+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该广告账号/profile 全部 Ads API。
- 保留已有 `reportId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明广告账号保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊广告账号安全，检测到 Amazon Ads API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。
