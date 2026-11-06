# 视频编辑运行与交付约定

## 运行前置

从可写任务工作目录启动，执行前确认 `<cwd>/linkfox/` 可创建及写入；不可写立即停止。输出必须留在 cwd 时，取消本次调用的 ACPX_WORKSPACES 设置。业务入口会在请求前检查该变量首路径是否等于 cwd，防止公共模板回退到 home 或临时目录；不修改公共模板本身。Windows 使用 `PYTHONUTF8=1` 或 `python -X utf8`，保证控制台与保存 JSON 均为 UTF-8。

凭证仅来自 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关 LINKFOX_TOOL_GATEWAY 默认 https://tool-gateway.linkfox.com。缺失凭证、401 或计费错误按 [onboarding.md](onboarding.md) 处理，403 不属于充值问题。登录令牌、验证码、密钥不写入任务数据、缓存或源文件；认证引导使用本技能的 scripts/onboarding.py。

## 完整任务 CLI

`python <skill-root>/scripts/run_task.py '<JSON 参数>'`；业务参数置于 params，外层只允许 requestId/chatId/messageId/title/params。params 必须是非空对象；requestId 可选，提供时原样转发，缺失时不自动生成。提供 requestId 时，每个新任务使用新的唯一值，核查同一操作保留该值；已接受任务通过 taskId 恢复查询，不自动重复提交。

| 参数 / 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| parameters | JSON object / `-` | 无 | 位置参数；`-` 从 stdin 读取。完整流程媒体字段允许本地路径或外部 URL，提交前转换成 viewUrl。 |
| --params-file | path | 无 | UTF-8 参数文件，与 parameters 互斥。 |
| --task-id | string | 无 | 恢复已有任务，只查询，不上传或创建；不能混入创建参数（含参数文件）。 |
| --member-id | string | 无 | 查询时可选 memberId；可用于恢复。 |
| --timeout | float | 视频 1200 秒，图像分支 600 秒 | 必须大于 0，总等待时间。 |
| --poll-interval | float | 10 秒 | CLI 接受非负值；视频按接口要求使用至少 10 秒。通用图像分支在初值至少 5 时逐步减至 5 秒。 |
| --initial-delay | float | 新视频 120 秒，恢复 0 秒，图像分支 10 秒 | 非负，实际首次等待不超过总超时。 |

完整流程自动复用当前 SESSION_ID；未设置时生成 aigc- 前缀会话标识。上传完成才创建一次，保存 taskId 后无缓存查询。超时保存最后响应及 taskId，使用 --task-id 恢复。查询错误、FAILED 或未知状态停止，不自动探测其他模型或创建更多收费任务。

## 低层入口与缓存

`python <skill-root>/scripts/video_editing_async.py '<JSON 参数>' [--inline] [--no-cache]` 用于已上传素材的显式创建；`query_task.py` 与 `upload_by_base64.py` 保留相同参数形式。

业务封装通过 call_api.run 完成网关调用，始终传 --no-cache 禁用公共调用器的第二层缓存。业务适配层提供唯一一层 24 小时缓存：以排序后的原请求 JSON 做 SHA-256，截取前 16 位，保存在 `<cwd>/linkfox/.cache/linkfox-aigc-video-edit/linkfox-aigc-video-edit-<摘要>.json`；兼容缓存的裸响应 JSON 和 `_cache.hit` 标志。创建和显式 Base64 上传默认复用本地缓存，--no-cache 绕过读写；query_task.py 总是绕过缓存，upload_file.py 同样绕过。缓存可能包含失败响应，不因命中而忽略业务错误；缓存过期不代表允许自动重建任务。

非对象、损坏或 `_cache` 结构异常的缓存不复用。缓存命中时响应附加的脚本字段如下；它们不是网关业务字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| _cache | object | 本地缓存命中信息。 |
| _cache.hit | boolean | 为 true 表示复用本地缓存，仍须检查响应错误。 |

XML ToolErrorResponse 转成 errcode/errmsg，费用响应头覆盖正文同名值。公共调用器负责请求、认证、超时与响应落盘，业务适配层只补响应兼容、本地缓存、HTTP 状态及 cwd 检查；没有另一套 LinkFox HTTP transport。非 LinkFox 素材下载保留必要 HTTP。

## 结果保存与下载恢复

JSON 保存至 `<cwd>/linkfox/<日期>/<session>/data/linkfox-aigc-video-edit-<接口标识>-<timestamp>.json`，并更新会话元信息；微秒文件名避免同秒轮询覆盖。小响应完整打印，大响应仅摘要，--inline 强制完整打印。工作流捕获入口的 `Saved full response: <路径> (<长度> bytes)` 后读取该响应。

SUCCESS 时下载每个有效结果到 `<session>/media/`，保留资源 id/type，兼容响应若实际包含单项 status/errorCode/errorMsg 也保留；不推断未返回字段。下载器验证 HTTP(S) 与重定向，分块保存临时文件，非空后改为最终文件名；根据实际扩展名、响应中的 format 或 Content-Type 决定扩展名，未知为 .bin。

资产清单写到 data，包含以下字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string / null | 查询任务编号。 |
| status | string / null | 查询任务状态。 |
| costToken / costCredit | integer / string / null | 查询实际费用，不被创建阶段费用覆盖。 |
| items | array<object> | 资源记录，保留实际返回标识与兼容字段。 |
| items[].id / items[].type | string / null | 资源标识及类型。 |
| items[].status / items[].errorCode / items[].errorMsg | 实际返回类型 | 仅兼容响应实际存在时保留，当前接口不承诺返回。 |
| items[].localPath | string | 成功下载的本地绝对路径。 |
| items[].downloadError | string | 下载失败说明；失败不重建任务。 |
| mediaPaths | array<string> | 成功保存的本地媒体绝对路径。 |

输出 `Saved media manifest: <清单路径>`；有媒体时输出 `Saved full response: ["<绝对路径>", ...]` 供展示，不向用户复述原协议行。成功但无文件时保留查询 JSON 路径，不把 JSON 当作生成媒体。

下载失败使用 `python <skill-root>/scripts/download_results.py <终态查询JSON>`，只接受通过响应错误判断且 status=SUCCESS 的查询对象，不调用 LinkFox 接口或生成新任务。
